# Orca
#
# Copyright 2004-2007 Sun Microsystems Inc.
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

"""The default Script for presenting information to the user using
both speech and Braille.  This is based primarily on the de-facto
standard implementation of the AT-SPI, which is the GAIL support
for GTK."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2007 Sun Microsystems Inc."
__license__   = "LGPL"

try:
    # This can fail due to gtk not being available.  We want to
    # be able to recover from that if possible.  The main driver
    # for this is to allow "orca --text-setup" to work even if
    # the desktop is not running.
    #
    import gtk
except:
    pass

import locale
import math
import time

import pyatspi
import braille
import chnames
import debug
import find
import flat_review
import input_event
import keybindings
import mag
import orca
import orca_prefs
import orca_state
import phonnames
import pronunciation_dict
import punctuation_settings
import rolenames
import script
import settings
import speech
import speechserver
import string

from orca_i18n import _         # for gettext support
from orca_i18n import ngettext  # for ngettext support
from orca_i18n import Q_        # to provide qualified translatable strings

########################################################################
#                                                                      #
# The Default script class.                                            #
#                                                                      #
########################################################################

class Script(script.Script):

    EMBEDDED_OBJECT_CHARACTER = u'\ufffc'
    NO_BREAK_SPACE_CHARACTER  = u'\u00a0'

    def __init__(self, app):
        """Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """
        script.Script.__init__(self, app)

        self.flatReviewContext  = None
        self.windowActivateTime = None
        self.lastReviewCurrentEvent = None

        # Used to determine whether the used double clicked on the
        # "where am I" key.
        #
        self.lastWhereAmIEvent = None

        # Unicode currency symbols (populated by the
        # getUnicodeCurrencySymbols() routine).
        #
        self._unicodeCurrencySymbols = []

        # Used by the drawOutline routine.
        #
        self._display = None
        self._visibleRectangle = None

        # Used by the visualAppearanceChanged routine for updating whether
        # progress bars are spoken.
        #
        self.lastProgressBarTime = {}
        self.lastProgressBarValue = {}

    def setupInputEventHandlers(self):
        """Defines InputEventHandler fields for this script that can be
        called by the key and braille bindings."""

        self.inputEventHandlers["leftClickReviewItemHandler"] = \
            input_event.InputEventHandler(
                Script.leftClickReviewItem,
                # Translators: the 'flat review' feature of Orca
                # allows the blind user to explore the text in a
                # window in a 2D fashion.  That is, Orca treats all
                # the text from all objects in a window (e.g.,
                # buttons, labels, etc.) as a sequence of words in a
                # sequence of lines.  The flat review feature allows
                # the user to explore this text by the {previous,next}
                # {line,word,character}.  A left click means to generate
                # a left mouse button click on the current item.
                #
                _("Performs left click on current flat review item."))

        self.inputEventHandlers["rightClickReviewItemHandler"] = \
             input_event.InputEventHandler(
                Script.rightClickReviewItem,
                # Translators: the 'flat review' feature of Orca
                # allows the blind user to explore the text in a
                # window in a 2D fashion.  That is, Orca treats all
                # the text from all objects in a window (e.g.,
                # buttons, labels, etc.) as a sequence of words in a
                # sequence of lines.  The flat review feature allows
                # the user to explore this text by the {previous,next}
                # {line,word,character}.  A right click means to generate
                # a right mouse button click on the current item.
                #
                _("Performs right click on current flat review item."))

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

        self.inputEventHandlers["whereAmIHandler"] = \
            input_event.InputEventHandler(
                Script.getWhereAmIInfo,
                # Translators: the "Where am I" feature of Orca allows
                # a user to press a key and then have information
                # about their current context spoken and brailled to
                # them.  For example, the information may include the
                # name of the current pushbutton with focus as well as
                # its mnemonic.
                #
                _("Performs the where am I operation."))

        self.inputEventHandlers["getTitleOrStatusHandler"] = \
            input_event.InputEventHandler(
                Script.getTitleOrStatus,
                # Translators: Orca has a command that will speak
                # a window's title if pressed once.  If pressed
                # two times quickly the contents of the status bar
                # will be spoken instead.
                #
                _("Speaks the title bar or status bar."))

        self.inputEventHandlers["findHandler"] = \
            input_event.InputEventHandler(
                orca._showFindGUI,
                # Translators: the Orca "Find" dialog allows a user to
                # search for text in a window and then move focus to
                # that text.  For example, they may want to find the
                # "OK" button.
                #
                _("Opens the Orca Find dialog."))

        self.inputEventHandlers["findNextHandler"] = \
            input_event.InputEventHandler(
                Script.findNext,
                # Translators: the Orca "Find" dialog allows a user to
                # search for text in a window and then move focus to
                # that text.  For example, they may want to find the
                # "OK" button.  This string is used for finding the
                # next occurence of a string.
                #
                _("Searches for the next instance of a string."))

        self.inputEventHandlers["findPreviousHandler"] = \
            input_event.InputEventHandler(
                Script.findPrevious,
                # Translators: the Orca "Find" dialog allows a user to
                # search for text in a window and then move focus to
                # that text.  For example, they may want to find the
                # "OK" button.  This string is used for finding the
                # previous occurence of a string.
                #
                _("Searches for the previous instance of a string."))

        self.inputEventHandlers["showZonesHandler"] = \
            input_event.InputEventHandler(
                Script.showZones,
                "Paints and prints the visible zones in the active window.")

        self.inputEventHandlers["toggleFlatReviewModeHandler"] = \
            input_event.InputEventHandler(
                Script.toggleFlatReviewMode,
                # Translators: the 'flat review' feature of Orca
                # allows the blind user to explore the text in a
                # window in a 2D fashion.  That is, Orca treats all
                # the text from all objects in a window (e.g.,
                # buttons, labels, etc.) as a sequence of words in a
                # sequence of lines.  The flat review feature allows
                # the user to explore this text by the {previous,next}
                # {line,word,character}.
                #
                _("Enters and exits flat review mode."))

        self.inputEventHandlers["reviewPreviousLineHandler"] = \
            input_event.InputEventHandler(
                Script.reviewPreviousLine,
                # Translators: the 'flat review' feature of Orca
                # allows the blind user to explore the text in a
                # window in a 2D fashion.  That is, Orca treats all
                # the text from all objects in a window (e.g.,
                # buttons, labels, etc.) as a sequence of words in a
                # sequence of lines.  The flat review feature allows
                # the user to explore this text by the {previous,next}
                # {line,word,character}.
                #
                _("Moves flat review to the beginning of the previous line."))

        self.inputEventHandlers["reviewHomeHandler"] = \
            input_event.InputEventHandler(
                Script.reviewHome,
                # Translators: the 'flat review' feature of Orca
                # allows the blind user to explore the text in a
                # window in a 2D fashion.  That is, Orca treats all
                # the text from all objects in a window (e.g.,
                # buttons, labels, etc.) as a sequence of words in a
                # sequence of lines.  The flat review feature allows
                # the user to explore this text by the {previous,next}
                # {line,word,character}.  The home position is the
                # beginning of the content in the window.
                #
                _("Moves flat review to the home position."))

        self.inputEventHandlers["reviewCurrentLineHandler"] = \
            input_event.InputEventHandler(
                Script.reviewCurrentLine,
                # Translators: the 'flat review' feature of Orca
                # allows the blind user to explore the text in a
                # window in a 2D fashion.  That is, Orca treats all
                # the text from all objects in a window (e.g.,
                # buttons, labels, etc.) as a sequence of words in a
                # sequence of lines.  The flat review feature allows
                # the user to explore this text by the {previous,next}
                # {line,word,character}.
                #
                _("Speaks the current flat review line."))

        self.inputEventHandlers["reviewNextLineHandler"] = \
            input_event.InputEventHandler(
                Script.reviewNextLine,
                # Translators: the 'flat review' feature of Orca
                # allows the blind user to explore the text in a
                # window in a 2D fashion.  That is, Orca treats all
                # the text from all objects in a window (e.g.,
                # buttons, labels, etc.) as a sequence of words in a
                # sequence of lines.  The flat review feature allows
                # the user to explore this text by the {previous,next}
                # {line,word,character}.
                #
                _("Moves flat review to the beginning of the next line."))

        self.inputEventHandlers["reviewEndHandler"] = \
            input_event.InputEventHandler(
                Script.reviewEnd,
                # Translators: the 'flat review' feature of Orca
                # allows the blind user to explore the text in a
                # window in a 2D fashion.  That is, Orca treats all
                # the text from all objects in a window (e.g.,
                # buttons, labels, etc.) as a sequence of words in a
                # sequence of lines.  The flat review feature allows
                # the user to explore this text by the {previous,next}
                # {line,word,character}.  The end position is the last
                # bit of information in the window.
                #
                _("Moves flat review to the end position."))

        self.inputEventHandlers["reviewPreviousItemHandler"] = \
            input_event.InputEventHandler(
                Script.reviewPreviousItem,
                # Translators: the 'flat review' feature of Orca
                # allows the blind user to explore the text in a
                # window in a 2D fashion.  That is, Orca treats all
                # the text from all objects in a window (e.g.,
                # buttons, labels, etc.) as a sequence of words in a
                # sequence of lines.  The flat review feature allows
                # the user to explore this text by the {previous,next}
                # {line,word,character}.  Previous will go backwards
                # in the window until you reach the top (i.e., it will
                # wrap across lines if necessary).
                #
                _("Moves flat review to the previous item or word."))

        self.inputEventHandlers["reviewAboveHandler"] = \
            input_event.InputEventHandler(
                Script.reviewAbove,
                # Translators: the 'flat review' feature of Orca
                # allows the blind user to explore the text in a
                # window in a 2D fashion.  That is, Orca treats all
                # the text from all objects in a window (e.g.,
                # buttons, labels, etc.) as a sequence of words in a
                # sequence of lines.  The flat review feature allows
                # the user to explore this text by the {previous,next}
                # {line,word,character}.  Above in this case means
                # geographically above, as if you drew a vertical line
                # in the window.
                #
                _("Moves flat review to the word above the current word."))

        self.inputEventHandlers["reviewCurrentItemHandler"] = \
            input_event.InputEventHandler(
                Script.reviewCurrentItem,
                # Translators: the 'flat review' feature of Orca
                # allows the blind user to explore the text in a
                # window in a 2D fashion.  That is, Orca treats all
                # the text from all objects in a window (e.g.,
                # buttons, labels, etc.) as a sequence of words in a
                # sequence of lines.  The flat review feature allows
                # the user to explore this text by the {previous,next}
                # {line,word,character}.  The 'speaks' means it will
                # speak the word.  The 'spells' means it will spell
                # out a word letter by letter.
                #
                _("Speaks or spells the current flat review item or word."))

        self.inputEventHandlers["reviewCurrentAccessibleHandler"] = \
            input_event.InputEventHandler(
                Script.reviewCurrentAccessible,
                # Translators: the 'flat review' feature of Orca
                # allows the blind user to explore the text in a
                # window in a 2D fashion.  That is, Orca treats all
                # the text from all objects in a window (e.g.,
                # buttons, labels, etc.) as a sequence of words in a
                # sequence of lines.  The flat review feature allows
                # the user to explore this text by the {previous,next}
                # {line,word,character}.  The flat review object is
                # typically something like a pushbutton, a label, or
                # some other GUI widget.  The 'speaks' means it will
                # speak the text associated with the object.
                #
                _("Speaks the current flat review object."))

        self.inputEventHandlers["reviewNextItemHandler"] = \
            input_event.InputEventHandler(
                Script.reviewNextItem,
                # Translators: the 'flat review' feature of Orca
                # allows the blind user to explore the text in a
                # window in a 2D fashion.  That is, Orca treats all
                # the text from all objects in a window (e.g.,
                # buttons, labels, etc.) as a sequence of words in a
                # sequence of lines.  The flat review feature allows
                # the user to explore this text by the {previous,next}
                # {line,word,character}.  Next will go forwards
                # in the window until you reach the end (i.e., it will
                # wrap across lines if necessary).
                #
                _("Moves flat review to the next item or word."))

        self.inputEventHandlers["reviewBelowHandler"] = \
            input_event.InputEventHandler(
                Script.reviewBelow,
                # Translators: the 'flat review' feature of Orca
                # allows the blind user to explore the text in a
                # window in a 2D fashion.  That is, Orca treats all
                # the text from all objects in a window (e.g.,
                # buttons, labels, etc.) as a sequence of words in a
                # sequence of lines.  The flat review feature allows
                # the user to explore this text by the {previous,next}
                # {line,word,character}.  Below in this case means
                # geographically below, as if you drew a vertical line
                # downward on the screen.
                #
                _("Moves flat review to the word below the current word."))

        self.inputEventHandlers["reviewPreviousCharacterHandler"] = \
            input_event.InputEventHandler(
                Script.reviewPreviousCharacter,
                # Translators: the 'flat review' feature of Orca
                # allows the blind user to explore the text in a
                # window in a 2D fashion.  That is, Orca treats all
                # the text from all objects in a window (e.g.,
                # buttons, labels, etc.) as a sequence of words in a
                # sequence of lines.  The flat review feature allows
                # the user to explore this text by the {previous,next}
                # {line,word,character}.  Previous will go backwards
                # in the window until you reach the top (i.e., it will
                # wrap across lines if necessary).
                #
                _("Moves flat review to the previous character."))

        self.inputEventHandlers["reviewEndOfLineHandler"] = \
            input_event.InputEventHandler(
                Script.reviewEndOfLine,
                # Translators: the 'flat review' feature of Orca
                # allows the blind user to explore the text in a
                # window in a 2D fashion.  That is, Orca treats all
                # the text from all objects in a window (e.g.,
                # buttons, labels, etc.) as a sequence of words in a
                # sequence of lines.  The flat review feature allows
                # the user to explore this text by the {previous,next}
                # {line,word,character}.
                #
                _("Moves flat review to the end of the line."))

        self.inputEventHandlers["reviewCurrentCharacterHandler"] = \
            input_event.InputEventHandler(
                Script.reviewCurrentCharacter,
                # Translators: the 'flat review' feature of Orca
                # allows the blind user to explore the text in a
                # window in a 2D fashion.  That is, Orca treats all
                # the text from all objects in a window (e.g.,
                # buttons, labels, etc.) as a sequence of words in a
                # sequence of lines.  The flat review feature allows
                # the user to explore this text by the {previous,next}
                # {line,word,character}.  Previous will go backwards
                # in the window until you reach the top (i.e., it will
                # wrap across lines if necessary).  The 'speaks' in
                # this case will be the spoken language form of the
                # character currently being reviewed.
                #
                _("Speaks the current flat review character."))

        self.inputEventHandlers["reviewNextCharacterHandler"] = \
            input_event.InputEventHandler(
                Script.reviewNextCharacter,
                # Translators: the 'flat review' feature of Orca
                # allows the blind user to explore the text in a
                # window in a 2D fashion.  That is, Orca treats all
                # the text from all objects in a window (e.g.,
                # buttons, labels, etc.) as a sequence of words in a
                # sequence of lines.  The flat review feature allows
                # the user to explore this text by the {previous,next}
                # {line,word,character}.  Next will go forwards
                # in the window until you reach the end (i.e., it will
                # wrap across lines if necessary).
                #
                _("Moves flat review to the next character."))

        self.inputEventHandlers["toggleTableCellReadModeHandler"] = \
            input_event.InputEventHandler(
                Script.toggleTableCellReadMode,
                # Translators: when users are navigating a table, they
                # sometimes want the entire row of a table read, or
                # they just want the current cell to be presented to them.
                #
                _("Toggles whether to read just the current table cell " \
                  "or the whole row."))

        self.inputEventHandlers["readCharAttributesHandler"] = \
            input_event.InputEventHandler(
                Script.readCharAttributes,
                # Translators: the attributes being presented are the
                # text attributes, such as bold, italic, font name,
                # font size, etc.
                #
                _("Reads the attributes associated with the current text " \
                  "character."))

        self.inputEventHandlers["reportScriptInfoHandler"] = \
            input_event.InputEventHandler(
                Script.reportScriptInfo,
                "Reports information on current script.")

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

        self.inputEventHandlers["reviewBottomLeftHandler"] = \
            input_event.InputEventHandler(
                Script.reviewBottomLeft,
                # Translators: the 'flat review' feature of Orca
                # allows the blind user to explore the text in a
                # window in a 2D fashion.  That is, Orca treats all
                # the text from all objects in a window (e.g.,
                # buttons, labels, etc.) as a sequence of words in a
                # sequence of lines.  The flat review feature allows
                # the user to explore this text by the {previous,next}
                # {line,word,character}.  The bottom left is the bottom
                # left of the window currently being reviewed.
                #
                _("Moves flat review to the bottom left."))

        self.inputEventHandlers["goBrailleHomeHandler"] = \
            input_event.InputEventHandler(
                Script.goBrailleHome,
                # Translators: the 'flat review' feature of Orca
                # allows the blind user to explore the text in a
                # window in a 2D fashion.  That is, Orca treats all
                # the text from all objects in a window (e.g.,
                # buttons, labels, etc.) as a sequence of words in a
                # sequence of lines.  The flat review feature allows
                # the user to explore this text by the {previous,next}
                # {line,word,character}.  Flat review is modal, and
                # the user can be exploring the window without changing
                # which object in the window which has focus.  The
                # feature used here will return the flat review to the
                # object with focus.
                #
                _("Returns to object with keyboard focus."))

        self.inputEventHandlers["enterLearnModeHandler"] = \
            input_event.InputEventHandler(
                Script.enterLearnMode,
                # Translators: Orca has a "Learn Mode" that will allow
                # the user to type any key on the keyboard and hear what
                # the effects of that key would be.  The effects might
                # be what Orca would do if it had a handler for the
                # particular key combination, or they might just be to
                # echo the name of the key if Orca doesn't have a handler.
                #
                _("Enters learn mode.  Press escape to exit learn mode."))

        self.inputEventHandlers["exitLearnModeHandler"] = \
            input_event.InputEventHandler(
                Script.exitLearnMode,
                # Translators: Orca has a "Learn Mode" that will allow
                # the user to type any key on the keyboard and hear what
                # the effects of that key would be.  The effects might
                # be what Orca would do if it had a handler for the
                # particular key combination, or they might just be to
                # echo the name of the key if Orca doesn't have a handler.
                #
                _("Exits learn mode."))

        self.inputEventHandlers["decreaseSpeechRateHandler"] = \
            input_event.InputEventHandler(
                speech.decreaseSpeechRate,
                # Translators: the speech rate is how fast the speech
                # synthesis engine will generate speech.
                #
                _("Decreases the speech rate."))

        self.inputEventHandlers["increaseSpeechRateHandler"] = \
            input_event.InputEventHandler(
                speech.increaseSpeechRate,
                # Translators: the speech rate is how fast the speech
                # synthesis engine will generate speech.
                #
                _("Increases the speech rate."))

        self.inputEventHandlers["decreaseSpeechPitchHandler"] = \
            input_event.InputEventHandler(
                speech.decreaseSpeechPitch,
                # Translators: the speech pitch is how high or low in
                # pitch/frequency the speech synthesis engine will
                # generate speech.
                #
                _("Decreases the speech pitch."))

        self.inputEventHandlers["increaseSpeechPitchHandler"] = \
            input_event.InputEventHandler(
                speech.increaseSpeechPitch,
                # Translators: the speech pitch is how high or low in
                # pitch/frequency the speech synthesis engine will
                # generate speech.
                #
                _("Increases the speech pitch."))

        self.inputEventHandlers["shutdownHandler"] = \
            input_event.InputEventHandler(
                orca.quitOrca,
                _("Quits Orca"))

        self.inputEventHandlers["preferencesSettingsHandler"] = \
            input_event.InputEventHandler(
                orca.showPreferencesGUI,
                # Translators: the preferences configuration dialog is
                # the dialog that allows users to set their preferences
                # for Orca.
                #
                _("Displays the preferences configuration dialog."))

        self.inputEventHandlers["appPreferencesSettingsHandler"] = \
            input_event.InputEventHandler(
                orca._showAppPreferencesGUI,
                # Translators: the application preferences configuration
                # dialog is the dialog that allows users to set their
                # preferences for a specific application within Orca.
                #
                _("Displays the application preferences configuration dialog."))

        self.inputEventHandlers["toggleSilenceSpeechHandler"] = \
            input_event.InputEventHandler(
                orca._toggleSilenceSpeech,
                # Translators: Orca allows the user to turn speech synthesis
                # on or off.  We call it 'silencing'.
                #
                _("Toggles the silencing of speech."))

        self.inputEventHandlers["listAppsHandler"] = \
            input_event.InputEventHandler(
                Script.printAppsHandler,
                "Prints a debug listing of all known applications to the " \
                "console where Orca is running.")

        self.inputEventHandlers["cycleDebugLevelHandler"] = \
            input_event.InputEventHandler(
                orca.cycleDebugLevel,
                "Cycles the debug level at run time.")

        self.inputEventHandlers["printActiveAppHandler"] = \
            input_event.InputEventHandler(
                Script.printActiveAppHandler,
                "Prints debug information about the currently active " \
                "application to the console where Orca is running.")

        self.inputEventHandlers["printAncestryHandler"] = \
            input_event.InputEventHandler(
                Script.printAncestryHandler,
                "Prints debug information about the ancestry of the object " \
                "with focus.")

        self.inputEventHandlers["printHierarchyHandler"] = \
            input_event.InputEventHandler(
                Script.printHierarchyHandler,
                "Prints debug information about the application with focus.")

        self.inputEventHandlers["printMemoryUsageHandler"] = \
            input_event.InputEventHandler(
                Script.printMemoryUsageHandler,
                "Prints memory usage information.")
                        
        self.inputEventHandlers["bookmarkCurrentWhereAmI"] = \
            input_event.InputEventHandler(
                Script.bookmarkCurrentWhereAmI,
                # Translators: this command announces information regarding
                # the relationship of the given bookmark to the current 
                # position
                #
                _("Bookmark where am I with respect to current position."))    
                
        self.inputEventHandlers["goToBookmark"] = \
            input_event.InputEventHandler(
                Script.goToBookmark,
                # Translators: this command moves the current position to the
                # location stored at the bookmark.
                #
                _("Go to bookmark."))
                
        self.inputEventHandlers["addBookmark"] = \
            input_event.InputEventHandler(
                Script.addBookmark,
                # Translators: this event handler binds an in-page accessible 
                # object location to the given input key command.
                #
                _("Add bookmark."))
                
        self.inputEventHandlers["saveBookmarks"] = \
            input_event.InputEventHandler(
                Script.saveBookmarks,
                # Translators: this event handler saves all bookmarks for the 
                # current application to disk.
                #
                _("Save bookmarks."))
                
        self.inputEventHandlers["goToNextBookmark"] = \
            input_event.InputEventHandler(
                Script.goToNextBookmark,
                # Translators: this event handler cycles through the registered
                # bookmarks and takes the user to the next bookmark location.
                #
                _("Go to next bookmark location."))
                
        self.inputEventHandlers["goToPrevBookmark"] = \
            input_event.InputEventHandler(
                Script.goToPrevBookmark,
                # Translators: this event handler cycles through the 
                # registered bookmarks and takes the user to the previous 
                # bookmark location.
                #
                _("Go to previous bookmark location."))

    def getInputEventHandlerKey(self, inputEventHandler):
        """Returns the name of the key that contains an inputEventHadler
        passed as argument
        """

        for keyName, handler in self.inputEventHandlers.iteritems():
            if handler == inputEventHandler:
                return keyName

        return None

    def getListeners(self):
        """Sets up the AT-SPI event listeners for this script.
        """
        listeners = script.Script.getListeners(self)
        listeners["focus:"]                                 = \
            self.onFocus
        #listeners["keyboard:modifiers"]                     = \
        #    self.noOp
        listeners["mouse:button"]                           = \
            self.onMouseButton
        listeners["object:property-change:accessible-name"] = \
            self.onNameChanged
        listeners["object:text-caret-moved"]                = \
            self.onCaretMoved
        listeners["object:text-changed:delete"]             = \
            self.onTextDeleted
        listeners["object:text-changed:insert"]             = \
            self.onTextInserted
        listeners["object:text-selection-changed"]          = \
            self.noOp
        listeners["object:active-descendant-changed"]       = \
            self.onActiveDescendantChanged
        listeners["object:children-changed"]               = \
            self.noOp
        listeners["object:link-selected"]                   = \
            self.onLinkSelected
        listeners["object:state-changed:"]                  = \
            self.onStateChanged
        listeners["object:selection-changed"]               = \
            self.onSelectionChanged
        listeners["object:property-change:accessible-value"] = \
            self.onValueChanged
        listeners["object:property-change"]                 = \
            self.noOp
        listeners["object:value-changed:"]                  = \
            self.onValueChanged
        listeners["object:visible-changed"]                 = \
            self.noOp
        listeners["window:activate"]                        = \
            self.onWindowActivated
        listeners["window:create"]                          = \
            self.noOp
        listeners["window:deactivate"]                      = \
            self.onWindowDeactivated
        listeners["window:destroy"]                         = \
            self.noOp
        listeners["window:maximize"]                        = \
            self.noOp
        listeners["window:minimize"]                        = \
            self.noOp
        listeners["window:rename"]                          = \
            self.noOp
        listeners["window:restore"]                         = \
            self.noOp
        listeners["window:switch"]                          = \
            self.noOp
        listeners["window:titlelize"]                       = \
            self.noOp

        return listeners

    def __getDesktopBindings(self):
        """Returns an instance of keybindings.KeyBindings that use the
        numeric keypad for focus tracking and flat review.
        """

        orcaModMask      = 1 << settings.MODIFIER_ORCA
        orcaShiftModMask = (1 << settings.MODIFIER_ORCA |
                            1 << pyatspi.MODIFIER_SHIFT)
        keyBindings = keybindings.KeyBindings()

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Divide",
                0,
                0,
                self.inputEventHandlers["leftClickReviewItemHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Multiply",
                0,
                0,
                self.inputEventHandlers["rightClickReviewItemHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Subtract",
                0,
                0,
                self.inputEventHandlers["toggleFlatReviewModeHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Add",
                0,
                0,
                self.inputEventHandlers["sayAllHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Enter",
                orcaModMask,
                0,
                self.inputEventHandlers["whereAmIHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Enter",
                orcaModMask,
                orcaModMask,
                self.inputEventHandlers["getTitleOrStatusHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Delete",
                orcaModMask,
                0,
                self.inputEventHandlers["findHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Delete",
                orcaShiftModMask,
                orcaModMask,
                self.inputEventHandlers["findNextHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Delete",
                orcaShiftModMask,
                orcaShiftModMask,
                self.inputEventHandlers["findPreviousHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_7",
                orcaModMask,
                0,
                self.inputEventHandlers["reviewPreviousLineHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Home",
                orcaModMask,
                0,
                self.inputEventHandlers["reviewPreviousLineHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_7",
                orcaModMask,
                orcaModMask,
                self.inputEventHandlers["reviewHomeHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Home",
                orcaModMask,
                orcaModMask,
                self.inputEventHandlers["reviewHomeHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_8",
                0,
                0,
                self.inputEventHandlers["reviewCurrentLineHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Up",
                0,
                0,
                self.inputEventHandlers["reviewCurrentLineHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_9",
                orcaModMask,
                0,
                self.inputEventHandlers["reviewNextLineHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Page_Up",
                orcaModMask,
                0,
                self.inputEventHandlers["reviewNextLineHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_9",
                orcaModMask,
                orcaModMask,
                self.inputEventHandlers["reviewEndHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Page_Up",
                orcaModMask,
                orcaModMask,
                self.inputEventHandlers["reviewEndHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_4",
                orcaModMask,
                0,
                self.inputEventHandlers["reviewPreviousItemHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Left",
                orcaModMask,
                0,
                self.inputEventHandlers["reviewPreviousItemHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_4",
                orcaModMask,
                orcaModMask,
                self.inputEventHandlers["reviewAboveHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Left",
                orcaModMask,
                orcaModMask,
                self.inputEventHandlers["reviewAboveHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_5",
                orcaModMask,
                0,
                self.inputEventHandlers["reviewCurrentItemHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Begin",
                orcaModMask,
                0,
                self.inputEventHandlers["reviewCurrentItemHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_5",
                orcaModMask,
                orcaModMask,
                self.inputEventHandlers["reviewCurrentAccessibleHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Begin",
                orcaModMask,
                orcaModMask,
                self.inputEventHandlers["reviewCurrentAccessibleHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_6",
                orcaModMask,
                0,
                self.inputEventHandlers["reviewNextItemHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Right",
                orcaModMask,
                0,
                self.inputEventHandlers["reviewNextItemHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_6",
                orcaModMask,
                orcaModMask,
                self.inputEventHandlers["reviewBelowHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Right",
                orcaModMask,
                orcaModMask,
                self.inputEventHandlers["reviewBelowHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_1",
                orcaModMask,
                0,
                self.inputEventHandlers["reviewPreviousCharacterHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_End",
                orcaModMask,
                0,
                self.inputEventHandlers["reviewPreviousCharacterHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_1",
                orcaModMask,
                orcaModMask,
                self.inputEventHandlers["reviewEndOfLineHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_End",
                orcaModMask,
                orcaModMask,
                self.inputEventHandlers["reviewEndOfLineHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_2",
                0,
                0,
                self.inputEventHandlers["reviewCurrentCharacterHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Down",
                0,
                0,
                self.inputEventHandlers["reviewCurrentCharacterHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_3",
                0,
                0,
                self.inputEventHandlers["reviewNextCharacterHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Page_Down",
                0,
                0,
                self.inputEventHandlers["reviewNextCharacterHandler"]))

        return keyBindings

    def __getLaptopBindings(self):
        """Returns an instance of keybindings.KeyBindings that use the
        the main keyboard keys for focus tracking and flat review.
        """

        orcaModMask        = 1 << settings.MODIFIER_ORCA
        orcaControlModMask = (1 << settings.MODIFIER_ORCA |
                              1 << pyatspi.MODIFIER_CONTROL)
        keyBindings = keybindings.KeyBindings()

        keyBindings.add(
            keybindings.KeyBinding(
                "7",
                orcaModMask,
                orcaModMask,
                self.inputEventHandlers["leftClickReviewItemHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "8",
                orcaModMask,
                orcaModMask,
                self.inputEventHandlers["rightClickReviewItemHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "p",
                orcaModMask,
                orcaModMask,
                self.inputEventHandlers["toggleFlatReviewModeHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "semicolon",
                orcaModMask,
                orcaModMask,
                self.inputEventHandlers["sayAllHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "Return",
                orcaModMask,
                orcaModMask,
                self.inputEventHandlers["whereAmIHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "slash",
                orcaModMask,
                orcaModMask,
                self.inputEventHandlers["getTitleOrStatusHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "bracketleft",
                orcaModMask,
                orcaModMask,
                self.inputEventHandlers["findHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "bracketright",
                orcaControlModMask,
                orcaModMask,
                self.inputEventHandlers["findNextHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "bracketright",
                orcaControlModMask,
                orcaControlModMask,
                self.inputEventHandlers["findPreviousHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "u",
                orcaControlModMask,
                orcaModMask,
                self.inputEventHandlers["reviewPreviousLineHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "u",
                orcaControlModMask,
                orcaControlModMask,
                self.inputEventHandlers["reviewHomeHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "i",
                orcaModMask,
                orcaModMask,
                self.inputEventHandlers["reviewCurrentLineHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "o",
                orcaControlModMask,
                orcaModMask,
                self.inputEventHandlers["reviewNextLineHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "o",
                orcaControlModMask,
                orcaControlModMask,
                self.inputEventHandlers["reviewEndHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "j",
                orcaControlModMask,
                orcaModMask,
                self.inputEventHandlers["reviewPreviousItemHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "j",
                orcaControlModMask,
                orcaControlModMask,
                self.inputEventHandlers["reviewAboveHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "k",
                orcaControlModMask,
                orcaModMask,
                self.inputEventHandlers["reviewCurrentItemHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "k",
                orcaControlModMask,
                orcaControlModMask,
                self.inputEventHandlers["reviewCurrentAccessibleHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "l",
                orcaControlModMask,
                orcaModMask,
                self.inputEventHandlers["reviewNextItemHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "l",
                orcaControlModMask,
                orcaControlModMask,
                self.inputEventHandlers["reviewBelowHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "m",
                orcaControlModMask,
                orcaModMask,
                self.inputEventHandlers["reviewPreviousCharacterHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "m",
                orcaControlModMask,
                orcaControlModMask,
                self.inputEventHandlers["reviewEndOfLineHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "comma",
                orcaModMask,
                orcaModMask,
                self.inputEventHandlers["reviewCurrentCharacterHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "period",
                orcaModMask,
                orcaModMask,
                self.inputEventHandlers["reviewNextCharacterHandler"]))

        return keyBindings

    def getKeyBindings(self):
        """Defines the key bindings for this script.

        Returns an instance of keybindings.KeyBindings.
        """

        orcaModMask           = 1 << settings.MODIFIER_ORCA
        orcaShiftModMask      = (1 << settings.MODIFIER_ORCA |
                                 1 << pyatspi.MODIFIER_SHIFT)
        orcaControlModMask    = (1 << settings.MODIFIER_ORCA |
                                 1 << pyatspi.MODIFIER_CONTROL)
        orcaAltModMask        = (1 << settings.MODIFIER_ORCA |
                                 1 << pyatspi.MODIFIER_ALT)
        orcaShiftAltModMask   = (1 << settings.MODIFIER_ORCA |
                                 1 << pyatspi.MODIFIER_ALT |
                                 1 << pyatspi.MODIFIER_SHIFT)
        orcaControlAltModMask = (1 << settings.MODIFIER_ORCA |
                                 1 << pyatspi.MODIFIER_CONTROL |
                                 1 << pyatspi.MODIFIER_ALT)
        shiftAltModMask       = (1 << pyatspi.MODIFIER_SHIFT |
                                 1 << pyatspi.MODIFIER_ALT)
        keyBindings = script.Script.getKeyBindings(self)

        if settings.keyboardLayout == settings.GENERAL_KEYBOARD_LAYOUT_DESKTOP:
            for keyBinding in self.__getDesktopBindings().keyBindings:
                keyBindings.add(keyBinding)
        else:
            for keyBinding in self.__getLaptopBindings().keyBindings:
                keyBindings.add(keyBinding)

        keyBindings.add(
            keybindings.KeyBinding(
                "Num_Lock",
                orcaModMask,
                orcaModMask,
                self.inputEventHandlers["showZonesHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "F11",
                orcaModMask,
                orcaModMask,
                self.inputEventHandlers["toggleTableCellReadModeHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "SunF36",
                orcaModMask,
                orcaModMask,
                self.inputEventHandlers["toggleTableCellReadModeHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "f",
                orcaModMask,
                orcaModMask,
                self.inputEventHandlers["readCharAttributesHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "h",
                orcaModMask,
                orcaModMask,
                self.inputEventHandlers["enterLearnModeHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "q",
                orcaModMask,
                orcaModMask,
                self.inputEventHandlers["shutdownHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "space",
                orcaControlModMask,
                orcaModMask,
                self.inputEventHandlers["preferencesSettingsHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "space",
                orcaControlModMask,
                orcaControlModMask,
                self.inputEventHandlers["appPreferencesSettingsHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "s",
                orcaModMask,
                orcaModMask,
                self.inputEventHandlers["toggleSilenceSpeechHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "End",
                orcaControlAltModMask,
                orcaControlAltModMask,
                self.inputEventHandlers["listAppsHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "Home",
                orcaControlAltModMask,
                orcaControlAltModMask,
                self.inputEventHandlers["reportScriptInfoHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "Page_Up",
                orcaControlAltModMask,
                orcaControlAltModMask,
                self.inputEventHandlers["printAncestryHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "Page_Down",
                orcaControlAltModMask,
                orcaControlAltModMask,
                self.inputEventHandlers["printHierarchyHandler"]))

        #####################################################################
        #                                                                   #
        #  Bookmark key bindings                                            #
        #                                                                   #
        #####################################################################   
        # key binding to save bookmark information to disk 
        keyBindings.add(
            keybindings.KeyBinding(
                "b",
                orcaShiftAltModMask,
                orcaAltModMask,
                self.inputEventHandlers["saveBookmarks"])) 
        # key binding to move to the previous bookmark         
        keyBindings.add(
            keybindings.KeyBinding(
                "b",
                orcaShiftAltModMask,
                orcaShiftModMask,
                self.inputEventHandlers["goToPrevBookmark"])) 
        # key binding to move to the next bookmark             
        keyBindings.add(
            keybindings.KeyBinding(
                "b",
                orcaShiftAltModMask,
                orcaModMask,
                self.inputEventHandlers["goToNextBookmark"]))    
                
        # key bindings for '1' through '6' for relevant commands            
        for key in xrange(1, 7):  
            # 'Add bookmark' key bindings
            keyBindings.add(
                keybindings.KeyBinding(
                    str(key),
                    orcaShiftAltModMask,
                    orcaAltModMask,
                    self.inputEventHandlers["addBookmark"]))
                    
            # 'Go to bookmark' key bindings
            keyBindings.add(
                keybindings.KeyBinding(
                    str(key),
                    orcaShiftAltModMask,
                    orcaModMask,
                    self.inputEventHandlers["goToBookmark"]))
                    
            # key binding for WhereAmI information with respect to root acc 
            keyBindings.add(
                keybindings.KeyBinding(
                    str(key),
                    orcaShiftAltModMask,
                    shiftAltModMask,
                    self.inputEventHandlers["bookmarkCurrentWhereAmI"]))

        #####################################################################
        #                                                                   #
        #  Unbound handlers                                                 #
        #                                                                   #
        #####################################################################

        keyBindings.add(
            keybindings.KeyBinding(
                None,
                0,
                0,
                self.inputEventHandlers["reportScriptInfoHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                None,
                0,
                0,
                self.inputEventHandlers["cycleDebugLevelHandler"]))

        if settings.debugMemoryUsage:
            keyBindings.add(
                keybindings.KeyBinding(
                    None,
                    0,
                    0,
                    self.inputEventHandlers["printMemoryUsageHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                None,
                0,
                0,
                self.inputEventHandlers["decreaseSpeechRateHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                None,
                0,
                0,
                self.inputEventHandlers["increaseSpeechRateHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                None,
                0,
                0,
                self.inputEventHandlers["decreaseSpeechPitchHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                None,
                0,
                0,
                self.inputEventHandlers["increaseSpeechPitchHandler"]))

        keyBindings = settings.overrideKeyBindings(self, keyBindings)

        return keyBindings

    def getBrailleBindings(self):
        """Defines the braille bindings for this script.

        Returns a dictionary where the keys are BrlTTY commands and the
        values are InputEventHandler instances.
        """
        brailleBindings = script.Script.getBrailleBindings(self)
        brailleBindings[braille.CMD_FWINLT]   = \
            self.inputEventHandlers["panBrailleLeftHandler"]
        brailleBindings[braille.CMD_FWINRT]   = \
            self.inputEventHandlers["panBrailleRightHandler"]
        brailleBindings[braille.CMD_LNUP]     = \
            self.inputEventHandlers["reviewAboveHandler"]
        brailleBindings[braille.CMD_LNDN]     = \
            self.inputEventHandlers["reviewBelowHandler"]
        brailleBindings[braille.CMD_TOP_LEFT] = \
            self.inputEventHandlers["reviewHomeHandler"]
        brailleBindings[braille.CMD_BOT_LEFT] = \
            self.inputEventHandlers["reviewBottomLeftHandler"]
        brailleBindings[braille.CMD_HOME]     = \
            self.inputEventHandlers["goBrailleHomeHandler"]

        return brailleBindings

    def processKeyboardEvent(self, keyboardEvent):
        """Processes the given keyboard event. It uses the super
        class equivalent to do most of the work. The only thing done here
        is to detect when the user is trying to get out of learn mode.

        Arguments:
        - keyboardEvent: an instance of input_event.KeyboardEvent
        """

        if (keyboardEvent.type == pyatspi.KEY_PRESSED_EVENT) and \
           (keyboardEvent.event_string == "Escape"):
            settings.learnModeEnabled = False

        return script.Script.processKeyboardEvent(self, keyboardEvent)

    def __sayAllProgressCallback(self, context, progressType):
        # [[[TODO: WDW - this needs work.  Need to be able to manage
        # the monitoring of progress and couple that with both updating
        # the visual progress of what is being spoken as well as
        # positioning the cursor when speech has stopped.]]]
        #
        text = context.obj.queryText()
        if progressType == speechserver.SayAllContext.PROGRESS:
            #print "PROGRESS", context.utterance, context.currentOffset
            #obj = context.obj
            #[x, y, width, height] = obj.text.getCharacterExtents(
            #    context.currentOffset, 0)
            #print context.currentOffset, x, y, width, height
            #self.drawOutline(x, y, width, height)
            pass
        elif progressType == speechserver.SayAllContext.INTERRUPTED:
            #print "INTERRUPTED", context.utterance, context.currentOffset
            text.setCaretOffset(context.currentOffset)
        elif progressType == speechserver.SayAllContext.COMPLETED:
            #print "COMPLETED", context.utterance, context.currentOffset
            orca.setLocusOfFocus(None, context.obj, False)
            text.setCaretOffset(context.currentOffset)

    def sayAll(self, inputEvent):
        try:
            orca_state.locusOfFocus.queryText()
        except NotImplementedError:
            speech.speakUtterances(
                self.speechGenerator.getSpeech(orca_state.locusOfFocus, False))
        except AttributeError:
            pass
        else:
            speech.sayAll(self.textLines(orca_state.locusOfFocus),
                          self.__sayAllProgressCallback)

        return True

    def isTextArea(self, obj):
        """Returns True if obj is a GUI component that is for entering text.

        Arguments:
        - obj: an accessible
        """
        return obj and \
            obj.getRole() in (pyatspi.ROLE_TEXT, pyatspi.ROLE_PARAGRAPH)

    def getText(self, obj, startOffset, endOffset):
        """Returns the substring of the given object's text specialization.

        Arguments:
        - obj: an accessible supporting the accessible text specialization
        - startOffset: the starting character position
        - endOffset: the ending character position
        """
        return obj.queryText().getText(startOffset, endOffset)

    def sayPhrase(self, obj, startOffset, endOffset):
        """Speaks the text of an Accessible object between the start and
        end offsets, unless the phrase is empty in which case it's ignored.

        Arguments:
        - obj: an Accessible object that implements the AccessibleText
               interface
        - startOffset: the start text offset.
        - endOffset: the end text offset.
        """

        # Swap values if in wrong order (StarOffice is fussy about that).
        #
        if ((startOffset > endOffset) and (endOffset != -1)) or \
           (startOffset == -1):
            temp = endOffset
            endOffset = startOffset
            startOffset = temp

        phrase = self.getText(obj, startOffset, endOffset)

        if len(phrase):
            if phrase.isupper():
                voice = self.voices[settings.UPPERCASE_VOICE]
            else:
                voice = self.voices[settings.DEFAULT_VOICE]

            phrase = self.adjustForRepeats(phrase)
            speech.speak(phrase, voice)
            self.speakTextSelectionState(obj, startOffset, endOffset)

    def sayLine(self, obj):
        """Speaks the line of an AccessibleText object that contains the
        caret, unless the line is empty in which case it's ignored.

        Arguments:
        - obj: an Accessible object that implements the AccessibleText
               interface
        """

        # Get the AccessibleText interface of the provided object
        #
        [line, caretOffset, startOffset] = self.getTextLineAtCaret(obj)
        debug.println(debug.LEVEL_FINEST, \
            "sayLine: line=<%s>, len=%d, start=%d, " % \
            (line, len(line), startOffset))
        debug.println(debug.LEVEL_FINEST, \
            "caret=%d, speakBlankLines=%s" % \
            (caretOffset, settings.speakBlankLines))

        if len(line):
            if line.isupper():
                voice = self.voices[settings.UPPERCASE_VOICE]
            else:
                voice = self.voices[settings.DEFAULT_VOICE]

            if settings.enableSpeechIndentation:
                self.speakTextIndentation(obj, line)
            line = self.adjustForRepeats(line)
            speech.speak(line, voice)
            self.speakTextSelectionState(obj, startOffset, caretOffset)

        else:
            # Speak blank line if appropriate. It's necessary to
            # test whether the first character is a newline, because
            # StarOffice blank lines are empty, and so StarOffice.py
            # handles speaking blank lines.
            text = obj.queryText()
            char = text.getTextAtOffset(caretOffset,
                pyatspi.TEXT_BOUNDARY_CHAR)
            debug.println(debug.LEVEL_FINEST,
                "sayLine: character=<%s>, start=%d, end=%d" % \
                (char[0], char[1], char[2]))

            if char[0] == "\n" and startOffset == caretOffset \
                   and settings.speakBlankLines:
                # Translators: "blank" is a short word to mean the
                # user has navigated to an empty line.
                #
                speech.speak(_("blank"))

    def sayWord(self, obj):
        """Speaks the word at the caret.  [[[TODO: WDW - what if there is no
        word at the caret?]]]

        Arguments:
        - obj: an Accessible object that implements the AccessibleText
               interface
        """

        text = obj.queryText()
        offset = text.caretOffset
        lastKey = orca_state.lastNonModifierKeyEvent.event_string
        lastWord = orca_state.lastWord

        [word, startOffset, endOffset] = \
            text.getTextAtOffset(offset,
                                 pyatspi.TEXT_BOUNDARY_WORD_START)

        # Speak a newline if a control-right-arrow or control-left-arrow
        # was used to cross a line boundary. Handling is different for
        # the two keys since control-right-arrow places the cursor after
        # the last character in a word, but control-left-arrow places
        # the cursor at the beginning of a word.
        #
        if lastKey == "Right" and len(lastWord) > 0:
            lastChar = lastWord[len(lastWord) - 1]
            if lastChar == "\n" and lastWord != word:
                voice = self.voices[settings.DEFAULT_VOICE]
                speech.speak(chnames.getCharacterName("\n"), voice, False)

        if lastKey == "Left" and len(word) > 0:
            lastChar = word[len(word) - 1]
            if lastChar == "\n" and lastWord != word:
                voice = self.voices[settings.DEFAULT_VOICE]
                speech.speak(chnames.getCharacterName("\n"), voice, False)

        if self.getLinkIndex(obj, offset) >= 0:
            voice = self.voices[settings.HYPERLINK_VOICE]
        elif word.isupper():
            voice = self.voices[settings.UPPERCASE_VOICE]
        else:
            voice = self.voices[settings.DEFAULT_VOICE]

        word = self.adjustForRepeats(word)
        orca_state.lastWord = word
        speech.speak(word, voice)
        self.speakTextSelectionState(obj, startOffset, endOffset)

    def speakTextIndentation(self, obj, line):
        """Speaks a summary of the number of spaces and/or tabs at the
        beginning of the given line.

        Arguments:
        - obj: the text object.
        - line: the string to check for spaces and tabs.
        """

        # For the purpose of speaking the text indentation, replace
        # occurances of UTF-8 '\302\240' (non breaking space) with
        # spaces.
        #
        line = line.replace("\302\240",  " ")
        line = line.decode("UTF-8")

        spaceCount = 0
        tabCount = 0
        for offset in range(0, len(line)):
            if line[offset] == ' ':
                spaceCount += 1
            elif line[offset] == '\t':
                tabCount += 1
            else:
                break

        utterance = ""
        if spaceCount:
            # Translators: this is the number of space characters on a line
            # of text.
            #
            utterance += ngettext("%d space",
                                  "%d spaces",
                                  spaceCount) % spaceCount + " "
        if tabCount:
            # Translators: this is the number of tab characters on a line
            # of text.
            #
            utterance += ngettext("%d tab",
                                  "%d tabs",
                                  tabCount) % tabCount + " "
        if len(utterance):
            speech.speak(utterance)

    def echoPreviousWord(self, obj):
        """Speaks the word prior to the caret, as long as there is
        a word prior to the caret and there is no intervening word
        delimiter between the caret and the end of the word.

        The entry condition for this method is that the character
        prior to the current caret position is a word delimiter,
        and it's what caused this method to be called in the first
        place.

        Arguments:
        - obj: an Accessible object that implements the AccessibleText
               interface.
        """

        try:
            text = obj.queryText()
        except NotImplementedError:
            return

        offset = text.caretOffset - 1
        if (offset < 0):
            return

        [char, startOffset, endOffset] = \
            text.getTextAtOffset( \
                offset,
                pyatspi.TEXT_BOUNDARY_CHAR)
        if not self.isWordDelimiter(char):
            return

        # OK - we seem to be cool so far.  So...starting with what
        # should be the last character in the word (caretOffset - 2),
        # work our way to the beginning of the word, stopping when
        # we hit another word delimiter.
        #
        wordEndOffset = text.caretOffset - 2
        wordStartOffset = wordEndOffset

        while wordStartOffset >= 0:
            [char, startOffset, endOffset] = \
                text.getTextAtOffset( \
                    wordStartOffset,
                    pyatspi.TEXT_BOUNDARY_CHAR)
            if self.isWordDelimiter(char):
                break
            else:
                wordStartOffset -= 1

        # If we came across a word delimiter before hitting any
        # text, we really don't have a previous word.
        #
        # Otherwise, get the word.  Remember we stopped when we
        # hit a word delimiter, so the word really starts at
        # wordStartOffset + 1.  getText also does not include
        # the character at wordEndOffset, so we need to adjust
        # for that, too.
        #
        if wordStartOffset == wordEndOffset:
            return
        else:
            word = self.getText(obj, wordStartOffset + 1, wordEndOffset + 1)

        if self.getLinkIndex(obj, wordStartOffset + 1) >= 0:
            voice = self.voices[settings.HYPERLINK_VOICE]
        elif word.isupper():
            voice = self.voices[settings.UPPERCASE_VOICE]
        else:
            voice = self.voices[settings.DEFAULT_VOICE]

        word = self.adjustForRepeats(word)
        speech.speak(word, voice)

    def sayCharacter(self, obj):
        """Speak the character under the caret.  [[[TODO: WDW - isn't the
        caret between characters?]]]

        Arguments:
        - obj: an Accessible object that implements the AccessibleText
               interface
        """

        text = obj.queryText()
        offset = text.caretOffset

        # If we have selected text and the last event was a move to the
        # right, then speak the character to the left of where the text
        # caret is (i.e. the selected character).
        #
        mods = orca_state.lastInputEvent.modifiers
        shiftMask = 1 << pyatspi.MODIFIER_SHIFT
        if (mods & shiftMask) \
            and orca_state.lastNonModifierKeyEvent.event_string == "Right":
            startOffset = offset-1
            endOffset = offset
        else:
            startOffset = offset
            endOffset = offset+1
        if endOffset > text.characterCount:
            character = "\n"
        else:
            character = self.getText(obj, startOffset, endOffset)
        if self.getLinkIndex(obj, offset) >= 0:
            voice = self.voices[settings.HYPERLINK_VOICE]
        elif character.decode("UTF-8").isupper():
            voice = self.voices[settings.UPPERCASE_VOICE]
        else:
            voice = self.voices[settings.DEFAULT_VOICE]

        prevChar = self.getText(obj, startOffset-1, endOffset-1)

        debug.println(debug.LEVEL_FINEST, \
            "sayCharacter: prev=<%s>, char=<%s>, startOffset=%d, " % \
            (prevChar, character, startOffset))
        debug.println(debug.LEVEL_FINEST, \
            "caretOffset=%d, endOffset=%d, speakBlankLines=%s" % \
            (offset, endOffset, settings.speakBlankLines))

        # Handle speaking newlines when the right-arrow key is pressed.
        if orca_state.lastNonModifierKeyEvent.event_string == "Right":
            if prevChar == "\n":
                # The cursor is at the beginning of a line.
                # Speak a newline.
                speech.speak(chnames.getCharacterName("\n"), voice, False)

        # Handle speaking newlines when the left-arrow key is pressed.
        elif orca_state.lastNonModifierKeyEvent.event_string == "Left":
            if character == "\n":
                # The cursor is at the end of a line.
                # Speak a newline.
                speech.speak(chnames.getCharacterName("\n"), voice, False)

        if character == "\n":
            if prevChar == "\n":
                # This is a blank line. Announce it if the user requested
                # that blank lines be spoken.
                if settings.speakBlankLines:
                    # Translators: "blank" is a short word to mean the
                    # user has navigated to an empty line.
                    #
                    speech.speak(_("blank"), voice, False)
        else:
            speech.speak(chnames.getCharacterName(character), voice, False)

        self.speakTextSelectionState(obj, startOffset, endOffset)

    def presentTooltip(self, obj):
        """
        Speaks the tooltip for the current object of interest.
        """

        # The tooltip is generally the accessible description. If
        # the description is not set, present the text that is
        # spoken when the object receives keyboard focus.
        #
        text = ""
        if obj.description:
            text = obj.description
        else:
            # Reuse the "where am I" algorithm.
            text = self.whereAmI._getObjLabelAndName(obj)

        debug.println(debug.LEVEL_FINEST, "presentTooltip: text='%s'" % text)
        if text != "":
            braille.displayMessage(text)
            speech.speak(text)

    def doWhereAmI(self, inputEvent, statusOrTitle):
        """Peforms the whereAmI operation.

        Arguments:
        - inputEvent:     The original inputEvent
        - titleOrStatus:  If true, the user is interested in the window's
                          title or status bar.
        """

        obj = orca_state.locusOfFocus
        self.updateBraille(obj)

        clickCount = self.getClickCount(self.lastWhereAmIEvent, inputEvent)
        doubleClick = clickCount == 2
        self.lastWhereAmIEvent = inputEvent

        return self.whereAmI.whereAmI(obj, doubleClick, statusOrTitle)

    def getWhereAmIInfo(self, inputEvent):
        """Speaks information about the current object of interest."""

        self.doWhereAmI(inputEvent, False)

    def getTitleOrStatus(self, inputEvent):
        """Speaks the window title for a single click; speaks the contents
        of the status bar for a double click.
        """

        self.doWhereAmI(inputEvent, True)

    def findCommonAncestor(self, a, b):
        """Finds the common ancestor between Accessible a and Accessible b.

        Arguments:
        - a: Accessible
        - b: Accessible
        """

        debug.println(debug.LEVEL_FINEST,
                      "default.findCommonAncestor...")

        if (not a) or (not b):
            return None

        if a == b:
            return a

        aParents = [a]
        try:
            parent = a.parent
            while parent and (parent.parent != parent):
                aParents.append(parent)
                parent = parent.parent
            aParents.reverse()
        except:
            debug.printException(debug.LEVEL_FINEST)

        bParents = [b]
        try:
            parent = b.parent
            while parent and (parent.parent != parent):
                bParents.append(parent)
                parent = parent.parent
            bParents.reverse()
        except:
            debug.printException(debug.LEVEL_FINEST)

        commonAncestor = None

        maxSearch = min(len(aParents), len(bParents))
        i = 0
        while i < maxSearch:
            if self.isSameObject(aParents[i], bParents[i]):
                commonAncestor = aParents[i]
                i += 1
            else:
                break

        debug.println(debug.LEVEL_FINEST,
                      "...default.findCommonAncestor")

        return commonAncestor

    def handleProgressBarUpdate(self, event, obj):
        """Determine whether this progress bar event should be spoken or not.
        It should be spoken if:
        1/ settings.enableProgressBarUpdates is True.
        2/ The application with the progress bar has focus.
        3/ The time of this event exceeds the
           settings.progressBarUpdateInterval value.  This value
           indicates the time (in seconds) between potential spoken
           progress bar updates.
        4/ The new value of the progress bar (converted to an integer),
           is different from the last one or equals 100 (i.e complete).

        Arguments:
        - event: if not None, the Event that caused this to happen
        - obj:  the Accessible progress bar object.
        """

        if settings.enableProgressBarUpdates:
            if orca_state.locusOfFocus and \
               orca_state.locusOfFocus.getApplication() == obj.getApplication():
                currentTime = time.time()

                # If this progress bar is not already known, create initial
                # values for it.
                #
                if not self.lastProgressBarTime.has_key(obj):
                    self.lastProgressBarTime[obj] = 0.0
                if not self.lastProgressBarValue.has_key(obj):
                    self.lastProgressBarValue[obj] = None

                lastProgressBarTime = self.lastProgressBarTime[obj]
                lastProgressBarValue = self.lastProgressBarValue[obj]
                value = obj.queryValue()
                percentValue = int((value.currentValue / \
                    (value.maximumValue - value.minimumValue)) * 100.0)

                if (currentTime - lastProgressBarTime) > \
                       settings.progressBarUpdateInterval \
                   or percentValue == 100:
                    if lastProgressBarValue != percentValue:
                        utterances = []

                        # There may be cases when more than one progress
                        # bar is updating at the same time in a window.
                        # If this is the case, then speak the index of this
                        # progress bar in the dictionary of known progress
                        # bars, as well as the value.
                        #
                        if len(self.lastProgressBarTime) > 1:
                            index = 0
                            for key in self.lastProgressBarTime.keys():
                                if key == obj:
                                    # Translators: this is an index value
                                    # so that we can tell which progress bar
                                    # we are referring to.
                                    #
                                    label = _("Progress bar %d.") % (index + 1)
                                    utterances.append(label)
                                else:
                                    index += 1

                        # Translators: this is the percentage value of a
                        # progress bar.
                        #
                        percentage = _("%d percent.") % percentValue + " "

                        utterances.append(percentage)
                        speech.speakUtterances(utterances)

                        self.lastProgressBarTime[obj] = currentTime
                        self.lastProgressBarValue[obj] = percentValue

    def locusOfFocusChanged(self, event, oldLocusOfFocus, newLocusOfFocus):
        """Called when the visual object with focus changes.

        Arguments:
        - event: if not None, the Event that caused the change
        - oldLocusOfFocus: Accessible that is the old locus of focus
        - newLocusOfFocus: Accessible that is the new locus of focus
        """

        try:
            if self.findCommandRun:
                # Then the Orca Find dialog has just given up focus
                # to the original window.  We don't want to speak
                # the window title, current line, etc.
                return
        except:
            pass

        if newLocusOfFocus:
            mag.magnifyAccessible(event, newLocusOfFocus)

        # We always automatically go back to focus tracking mode when
        # the focus changes.
        #
        if self.flatReviewContext:
            self.toggleFlatReviewMode()

        # [[[TODO: WDW - HACK because parents that manage their descendants
        # can give us a different object each time we ask for the same
        # exact child.  So...we do a check here to see if the old object
        # and new object have the same index in the parent and if they
        # have the same name.  If so, then they are likely to be the same
        # object.  The reason we check for the name here is a small sanity
        # check.  This whole algorithm could fail because one might be
        # deleting/adding identical elements from/to a list or table, thus
        # the objects really could be different even though they seem the
        # same.  Logged as bug 319675.]]]
        #
        if self.isSameObject(oldLocusOfFocus, newLocusOfFocus):
            return

        # Well...now that we got that behind us, let's do what we're supposed
        # to do.
        #
        if oldLocusOfFocus:
            oldParent = oldLocusOfFocus.parent
        else:
            oldParent = None

        if newLocusOfFocus:
            newParent = newLocusOfFocus.parent
        else:
            newParent = None

        # Clear the point of reference.
        # If the point of reference is a cell, we want to keep the 
        # table-related points of reference.
        if oldParent is not None and oldParent == newParent and \
              newParent.getRole() == pyatspi.ROLE_TABLE:
            for key in self.pointOfReference.keys():
                if key not in ('lastRow', 'lastColumn'):
                    del self.pointOfReference[key]
        else:
            self.pointOfReference = {}

        if newLocusOfFocus:
            self.updateBraille(newLocusOfFocus)

            utterances = []

            # Now figure out how of the container context changed and
            # speech just what is different.
            #
            commonAncestor = self.findCommonAncestor(oldLocusOfFocus,
                                                     newLocusOfFocus)
            if commonAncestor:
                context = self.speechGenerator.getSpeechContext( \
                                           newLocusOfFocus, commonAncestor)
                utterances.append(" ".join(context))

            # Now, we'll treat table row and column headers as context
            # as well.  This requires special handling because we're
            # making headers seem hierarchical in the context, but they
            # are not hierarchical in the containment hierarchicy.
            # We also only want to speak the one that changed.  If both
            # changed, first speak the row header, then the column header.
            #
            # We also keep track of tree level depth and only announce
            # that if it changes.
            #
            oldNodeLevel = -1
            newNodeLevel = -1
            if newLocusOfFocus.getRole() == pyatspi.ROLE_TABLE_CELL:
                try:
                    table = oldParent.queryTable()
                except:
                    table = None
                if table and \
                      oldLocusOfFocus.getRole() == pyatspi.ROLE_TABLE_CELL:
                    oldRow = table.getRowAtIndex( \
                                           oldLocusOfFocus.getIndexInParent())
                    oldCol = table.getColumnAtIndex( \
                                           oldLocusOfFocus.getIndexInParent())
                else:
                    oldRow = -1
                    oldCol = -1

                try:
                    table = newParent.queryTable()
                except:
                    pass
                else:
                    newRow = table.getRowAtIndex( \
                                  newLocusOfFocus.getIndexInParent())
                    newCol = table.getColumnAtIndex( \
                                  newLocusOfFocus.getIndexInParent())

                    if (newRow != oldRow) or (oldParent != newParent):
                        desc = table.getRowDescription(newRow)
                        if desc and len(desc):
                            text = desc
                            if settings.speechVerbosityLevel \
                                   == settings.VERBOSITY_LEVEL_VERBOSE:
                                text += " " \
                                        + rolenames.rolenames[\
                                        pyatspi.ROLE_ROW_HEADER].speech
                            utterances.append(text)
                    if (newCol != oldCol) or (oldParent != newParent):
                        # Don't speak Thunderbird column headers, since
                        # it's not possible to navigate across a row.
                        topName = self.getTopLevelName(newLocusOfFocus)
                        if not topName.endswith(" - Thunderbird"):
                            desc = table.getColumnDescription(newCol)
                            if desc and len(desc):
                                text = desc
                                if settings.speechVerbosityLevel \
                                       == settings.VERBOSITY_LEVEL_VERBOSE:
                                    text += " " \
                                            + rolenames.rolenames[\
                                            pyatspi.ROLE_COLUMN_HEADER].speech
                                utterances.append(text)

            oldNodeLevel = self.getNodeLevel(oldLocusOfFocus)
            newNodeLevel = self.getNodeLevel(newLocusOfFocus)

            # We'll also treat radio button groups as though they are
            # in a context, with the label for the group being the
            # name of the context.
            #
            if newLocusOfFocus.getRole() == pyatspi.ROLE_RADIO_BUTTON:
                radioGroupLabel = None
                inSameGroup = False
                relations = newLocusOfFocus.getRelationSet()
                for relation in relations:
                    if (not radioGroupLabel) \
                        and (relation.getRelationType() \
                             == pyatspi.RELATION_LABELLED_BY):
                        radioGroupLabel = relation.getTarget(0)
                    if (not inSameGroup) \
                        and (relation.getRelationType() \
                             == pyatspi.RELATION_MEMBER_OF):
                        for i in range(0, relation.getNTargets()):
                            target = relation.getTarget(i)
                            if target == oldLocusOfFocus:
                                inSameGroup = True
                                break

                # We'll only announce the radio button group when we
                # switch groups.
                #
                if (not inSameGroup) and radioGroupLabel:
                    utterances.append(self.getDisplayedText(radioGroupLabel))

            # Check to see if we are in the Pronunciation Dictionary in the 
            # Orca Preferences dialog. If so, then we do not want to use the 
            # pronunciation dictionary to replace the actual words in the 
            # first column of this table.
            #
            rolesList = [pyatspi.ROLE_TABLE_CELL, \
                         pyatspi.ROLE_TABLE, \
                         pyatspi.ROLE_SCROLL_PANE, \
                         pyatspi.ROLE_PANEL, \
                         pyatspi.ROLE_PANEL]
            if self.isDesiredFocusedItem(newLocusOfFocus, rolesList) and \
               newLocusOfFocus.getApplication().name == "orca":
                orca_state.usePronunciationDictionary = False
            else:
                orca_state.usePronunciationDictionary = True

            # Get the text for the object itself.
            #
            utterances.extend(
                self.speechGenerator.getSpeech(newLocusOfFocus, False))

            # Now speak the new tree node level if it has changed.
            #
            if (oldNodeLevel != newNodeLevel) \
               and (newNodeLevel >= 0):
                # Translators: this represents the depth of a node in a tree
                # view (i.e., how many ancestors a node has).
                #
                utterances.append(_("tree level %d") % (newNodeLevel + 1))

            # We might be automatically speaking the unbound labels
            # in a dialog box as the result of the dialog box suddenly
            # appearing.  If so, don't interrupt this because of a
            # focus event that occurs when something like the "OK"
            # button gets focus shortly after the window appears.
            #
            shouldNotInterrupt = (event and event.type.startswith("focus:")) \
                and self.windowActivateTime \
                and ((time.time() - self.windowActivateTime) < 1.0)

            if newLocusOfFocus.getRole() == pyatspi.ROLE_LINK:
                voice = self.voices[settings.HYPERLINK_VOICE]
            else:
                voice = self.voices[settings.DEFAULT_VOICE]

            speech.speakUtterances(utterances, voice, not shouldNotInterrupt)

            # If this is a table cell, save the current row and column
            # information in the table cell's table, so that we can use
            # it the next time.
            #
            if newLocusOfFocus.getRole() == pyatspi.ROLE_TABLE_CELL:
                try:
                    table = newParent.queryTable()
                except:
                    pass
                else:
                    column = table.getColumnAtIndex( \
                                    newLocusOfFocus.getIndexInParent())
                    self.pointOfReference['lastColumn'] = column
                    row = table.getRowAtIndex( \
                                    newLocusOfFocus.getIndexInParent())
                    self.pointOfReference['lastRow'] = row
        else:
            orca_state.noFocusTimeStamp = time.time()

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

        # Check if this event is for a progress bar.
        #
        if obj.getRole() == pyatspi.ROLE_PROGRESS_BAR:
            self.handleProgressBarUpdate(event, obj)

        if self.flatReviewContext:
            if self.isSameObject(
                obj,
                self.flatReviewContext.getCurrentAccessible()):
                self.updateBrailleReview()
            return

        # We care if panels are suddenly showing.  The reason for this
        # is that some applications, such as Evolution, will bring up
        # a wizard dialog that uses "Forward" and "Backward" buttons
        # that change the contents of the dialog.  We only discover
        # this through showing events. [[[TODO: WDW - perhaps what we
        # really want is to speak unbound labels that are suddenly
        # showing?  event.detail == 1 means object is showing.]]]
        #
        # [[[TODO: WDW - I added the 'False' condition to prevent this
        # condition from ever working.  I wanted to keep the code around,
        # though, just in case we want to reuse it somewhere else.  The
        # bug that spurred all of this on is:
        #
        #    http://bugzilla.gnome.org/show_bug.cgi?id=338687
        #
        # The main problem is that the profile editor in gnome-terminal
        # ended up being very verbose and speaking lots of things it
        # should not have been speaking.]]]
        #
        if False and (obj.getRole() == pyatspi.ROLE_PANEL) \
               and (event.detail1 == 1) \
               and self.isInActiveApp(obj):

            # It's only showing if its parent is showing. [[[TODO: WDW -
            # HACK we stop at the application level because applications
            # never seem to have their showing state set.]]]
            #
            reallyShowing = True
            parent = obj.parent
            while reallyShowing \
                      and parent \
                      and (parent != parent.parent) \
                      and (parent.getRole() != pyatspi.ROLE_APPLICATION):
                debug.println(debug.LEVEL_FINEST,
                              "default.visualAppearanceChanged - " \
                              + "checking parent")
                reallyShowing = parent.getState().contains( \
                                                  pyatspi.STATE_SHOWING)
                parent = parent.parent

            # Find all the unrelated labels in the dialog and speak them.
            #
            if reallyShowing:
                utterances = []
                labels = self.findUnrelatedLabels(obj)
                for label in labels:
                    utterances.append(label.name)

                speech.speakUtterances(utterances)

                return

        # If this object is CONTROLLED_BY the object that currently
        # has focus, speak/braille this object.
        #
        relations = obj.getRelationSet()
        for relation in relations:
            if relation.getRelationType() \
                   == pyatspi.RELATION_CONTROLLED_BY:
                target = relation.getTarget(0)
                if target == orca_state.locusOfFocus:
                    self.updateBraille(target)
                    speech.speakUtterances(
                        self.speechGenerator.getSpeech(target, True))
                    return

        # If this object is a label, and if it has a LABEL_FOR relation
        # to the focused object, then we should speak/braille the
        # focused object, as if it had just got focus.
        #
        if obj.getRole() == pyatspi.ROLE_LABEL:
            for relation in relations:
                if relation.getRelationType() \
                       == pyatspi.RELATION_LABEL_FOR:
                    target = relation.getTarget(0)
                    if target == orca_state.locusOfFocus:
                        self.updateBraille(target)
                        speech.speakUtterances(
                            self.speechGenerator.getSpeech(target, True))
                        return

        if obj != orca_state.locusOfFocus:
            return

        if event:
            debug.println(debug.LEVEL_FINE,
                          "VISUAL CHANGE: '%s' '%s' (event='%s')" \
                          % (obj.name, obj.getRole(), event.type))
        else:
            debug.println(debug.LEVEL_FINE,
                          "VISUAL CHANGE: '%s' '%s' (event=None)" \
                          % (obj.name, obj.getRole()))

        mag.magnifyAccessible(event, obj)
        self.updateBraille(obj)
        speech.speakUtterances(self.speechGenerator.getSpeech(obj, True))

    def updateBraille(self, obj, extraRegion=None):
        """Updates the braille display to show the give object.

        Arguments:
        - obj: the Accessible
        - extra: extra Region to add to the end
        """

        if not obj:
            return

        braille.clear()

        line = braille.Line()
        braille.addLine(line)

        # For multiline text areas, we only show the context if we
        # are on the very first line.  Otherwise, we show only the
        # line.
        #
        try:
            text = obj.queryText()
        except NotImplementedError:
            text = None
        if text and self.isTextArea(obj):
            [lineString, startOffset, endOffset] = text.getTextAtOffset(
                text.caretOffset,
                pyatspi.TEXT_BOUNDARY_LINE_START)
            if startOffset == 0:
                line.addRegions(self.brailleGenerator.getBrailleContext(obj))
        else:
            line.addRegions(self.brailleGenerator.getBrailleContext(obj))

        result = self.brailleGenerator.getBrailleRegions(obj)
        line.addRegions(result[0])

        if extraRegion:
            line.addRegion(extraRegion)

        if extraRegion:
            braille.setFocus(extraRegion)
        else:
            braille.setFocus(result[1])

        braille.refresh(True)

    ########################################################################
    #                                                                      #
    # AT-SPI OBJECT EVENT HANDLERS                                         #
    #                                                                      #
    ########################################################################

    def onFocus(self, event):
        """Called whenever an object gets focus.

        Arguments:
        - event: the Event
        """

        # [[[TODO: WDW - HACK to deal with quirky GTK+ menu behavior.
        # The problem is that when moving to submenus in a menu, the
        # menu gets focus first and then the submenu gets focus all
        # with a single keystroke.  So...focus in menus really means
        # that the object has focus *and* it is selected.  Now, this
        # assumes the selected state will be set before focus is given,
        # which appears to be the case from empirical analysis of the
        # event stream.  But of course, all menu items and menus in
        # the complete menu path will have their selected state set,
        # so, we really only care about the leaf menu or menu item
        # that it selected.]]]
        #
        role = event.source.getRole()
        if role in (pyatspi.ROLE_MENU, 
                    pyatspi.ROLE_MENU_ITEM,
                    pyatspi.ROLE_CHECK_MENU_ITEM,
                    pyatspi.ROLE_RADIO_MENU_ITEM):
            try:
                if event.source.querySelection().nSelectedChildren > 0:
                    return
            except:
                pass

        # [[[TODO: WDW - HACK to deal with the fact that active cells
        # may or may not get focus.  Their parents, however, do tend to
        # get focus, but when the parent gets focus, it really means
        # that the selected child in it has focus.  Of course, this all
        # breaks when more than one child is selected.  Then, we really
        # need to depend upon the model where focus really works.]]]
        #
        newFocus = event.source

        if role in (pyatspi.ROLE_LAYERED_PANE, 
                    pyatspi.ROLE_TABLE,
                    pyatspi.ROLE_TREE_TABLE,
                    pyatspi.ROLE_TREE):
            if event.source.childCount:
                # Well...we'll first see if there is a selection.  If there
                # is, we'll use it.
                #
                try:
                    selection = event.source.querySelection()
                except NotImplementedError:
                    selection = None
                if selection and selection.nSelectedChildren > 0:
                    newFocus = selection.getSelectedChild(0)

                # Otherwise, we might have tucked away some information
                # for this thing in the onActiveDescendantChanged method.
                #
                elif self.pointOfReference.has_key("activeDescendantInfo"):
                    [parent, index] = \
                        self.pointOfReference['activeDescendantInfo']
                    newFocus = parent[index]

        orca.setLocusOfFocus(event, newFocus)

    def onNameChanged(self, event):
        """Called whenever a property on an object changes.

        Arguments:
        - event: the Event
        """

        # [[[TODO: WDW - HACK because gnome-terminal issues a name changed
        # event for the edit preferences dialog even though the name really
        # didn't change.  I'm guessing this is going to be a vagary in all
        # of GTK+.]]]
        #
        if event.source and (event.source.getRole() == pyatspi.ROLE_DIALOG) \
           and (event.source == orca_state.locusOfFocus):
            return

        # We do this because we can get name change events even if the
        # name doesn't change.  [[[TODO: WDW - I'm hesitant to rip the
        # above TODO out, though, because it's been in here for so long.]]]
        #
        if self.pointOfReference.get('oldName', None) == event.source.name:
            return

        self.pointOfReference['oldName'] = event.source.name
        orca.visualAppearanceChanged(event, event.source)

    def _presentTextAtNewCaretPosition(self, event):

        text = event.source.queryText()

        if event.source:
            mag.magnifyAccessible(event, event.source)

        # Update the Braille display - if we can just reposition
        # the cursor, then go for it.
        #
        brailleNeedsRepainting = True
        line = braille.getShowingLine()
        for region in line.regions:
            if isinstance(region, braille.Text) \
               and (region.accessible == event.source):
                if region.repositionCursor():
                    braille.refresh(True)
                    brailleNeedsRepainting = False
                break

        if brailleNeedsRepainting:
            self.updateBraille(event.source)

        if not orca_state.lastInputEvent:
            return

        if isinstance(orca_state.lastInputEvent, input_event.MouseButtonEvent):
            if not orca_state.lastInputEvent.pressed:
                self.sayLine(event.source)
            return

        # Guess why the caret moved and say something appropriate.
        # [[[TODO: WDW - this motion assumes traditional GUI
        # navigation gestures.  In an editor such as vi, line up and
        # down is done via other actions such as "i" or "j".  We may
        # need to think about this a little harder.]]]
        #
        if not isinstance(orca_state.lastInputEvent,
                          input_event.KeyboardEvent):
            return

        keyString = orca_state.lastNonModifierKeyEvent.event_string
        mods = orca_state.lastInputEvent.modifiers
        isControlKey = mods & (1 << pyatspi.MODIFIER_CONTROL)
        isShiftKey = mods & (1 << pyatspi.MODIFIER_SHIFT)
        hasLastPos = self.pointOfReference.has_key("lastCursorPosition")

        if (keyString == "Up") or (keyString == "Down"):
            # If the user has typed Shift-Up or Shift-Down, then we want
            # to speak the text that has just been selected or unselected,
            # otherwise we speak the new line where the text cursor is
            # currently positioned.
            #
            if hasLastPos and isShiftKey and not isControlKey:
                self.sayPhrase(event.source, 
                               self.pointOfReference["lastCursorPosition"],
                               text.caretOffset)
            else:
                self.sayLine(event.source)

        elif (keyString == "Left") or (keyString == "Right"):
            # If the user has typed Control-Shift-Up or Control-Shift-Dowm,
            # then we want to speak the text that has just been selected
            # or unselected, otherwise if the user has typed Control-Left
            # or Control-Right, we speak the current word otherwise we speak
            # the character at the text cursor position.
            #
            if hasLastPos and isShiftKey and isControlKey:
                self.sayPhrase(event.source, 
                               self.pointOfReference["lastCursorPosition"],
                               text.caretOffset)
            elif isControlKey:
                self.sayWord(event.source)
            else:
                self.sayCharacter(event.source)

        elif keyString == "Page_Up":
            # If the user has typed Control-Shift-Page_Up, then we want
            # to speak the text that has just been selected or unselected,
            # otherwise if the user has typed Control-Page_Up, then we
            # speak the character to the right of the current text cursor
            # position otherwise we speak the current line.
            #
            if hasLastPos and isShiftKey and isControlKey:
                self.sayPhrase(event.source, 
                               self.pointOfReference["lastCursorPosition"],
                               text.caretOffset)
            elif isControlKey:
                self.sayCharacter(event.source)
            else:
                self.sayLine(event.source)

        elif keyString == "Page_Down":
            # If the user has typed Control-Shift-Page_Down, then we want
            # to speak the text that has just been selected or unselected,
            # otherwise if the user has just typed Page_Down, then we speak
            # the current line.
            #
            if hasLastPos and isShiftKey and isControlKey:
                self.sayPhrase(event.source, 
                               self.pointOfReference["lastCursorPosition"],
                               text.caretOffset)
            else:
                self.sayLine(event.source)

        elif (keyString == "Home") or (keyString == "End"):
            # If the user has typed Shift-Home or Shift-End, then we want
            # to speak the text that has just been selected or unselected,
            # otherwise if the user has typed Control-Home or Control-End,
            # then we speak the current line otherwise we speak the character
            # to the right of the current text cursor position.
            #
            if hasLastPos and isShiftKey and not isControlKey:
                self.sayPhrase(event.source, 
                               self.pointOfReference["lastCursorPosition"],
                               text.caretOffset)
            elif isControlKey:
                self.sayLine(event.source)
            else:
                self.sayCharacter(event.source)

        elif (keyString == "A") and isControlKey:
            # The user has typed Control-A. Check to see if the entire
            # document has been selected, and if so, let the user know.
            #
            charCount = text.characterCount
            for i in range(0, text.getNSelections()):
                [startSelOffset, endSelOffset] = text.getSelection(i)
                if text.caretOffset == 0 and \
                   startSelOffset == 0 and endSelOffset == charCount:
                    # Translators: this means the user has selected
                    # all the text in a document (e.g., Ctrl+a in gedit).
                    #
                    speech.speak(_("entire document selected"))

    def onCaretMoved(self, event):
        """Called whenever the caret moves.

        Arguments:
        - event: the Event
        """

        # We don't always get focus: events for text areas, so if we
        # see caret moved events for a focused text area, we silently
        # set them to be the locus of focus.
        #
        if event and event.source and \
           (event.source != orca_state.locusOfFocus) and \
            event.source.getState().contains(pyatspi.STATE_FOCUSED):
            orca.setLocusOfFocus(event, event.source, False)

        # Ignore caret movements from non-focused objects, unless the
        # currently focused object is the parent of the object which
        # has the caret.
        #
        if (event.source != orca_state.locusOfFocus) \
            and (event.source.parent != orca_state.locusOfFocus):
            return

        # We always automatically go back to focus tracking mode when
        # the caret moves in the focused object.
        #
        if self.flatReviewContext:
            self.toggleFlatReviewMode()

        self._presentTextAtNewCaretPosition(event)

    def onTextDeleted(self, event):
        """Called whenever text is deleted from an object.

        Arguments:
        - event: the Event
        """

        # We don't always get focus: events for text areas, so if we
        # see deleted text events for a focused text area, we silently
        # set them to be the locus of focus..
        #
        if event and event.source and \
           (event.source != orca_state.locusOfFocus) and \
            event.source.getState().contains(pyatspi.STATE_FOCUSED):
            orca.setLocusOfFocus(event, event.source, False)

        # Ignore text deletions from non-focused objects, unless the
        # currently focused object is the parent of the object from which
        # text was deleted
        #
        if (event.source != orca_state.locusOfFocus) \
            and (event.source.parent != orca_state.locusOfFocus):
            return

        # We'll also ignore sliders because we get their output via
        # their values changing.
        #
        if event.source.getRole() == pyatspi.ROLE_SLIDER:
            return

        # [[[NOTE: WDW - if we handle events synchronously, we'll
        # be looking at the text object *before* the text was
        # actually removed from the object.  If we handle events
        # asynchronously, we'll be looking at the text object
        # *after* the text was removed.  The importance of knowing
        # this is that the output will differ depending upon how
        # orca.settings.asyncMode has been set.  For example, the
        # regression tests run in synchronous mode, so the output
        # they see will not be the same as what the user normally
        # experiences.]]]

        self.updateBraille(event.source)

        # The any_data member of the event object has the deleted text in
        # it - If the last key pressed was a backspace or delete key,
        # speak the deleted text.  [[[TODO: WDW - again, need to think
        # about the ramifications of this when it comes to editors such
        # as vi or emacs.
        #
        if (not orca_state.lastInputEvent) \
            or \
            (not isinstance(orca_state.lastInputEvent,
                            input_event.KeyboardEvent)):
            return

        keyString = orca_state.lastNonModifierKeyEvent.event_string
        controlPressed = orca_state.lastInputEvent.modifiers \
                         & (1 << pyatspi.MODIFIER_CONTROL)
        text = event.source.queryText()
        if keyString == "BackSpace":
            # Speak the character that has just been deleted.
            #
            character = event.any_data

        elif (keyString == "Delete") \
             or (keyString == "D" and controlPressed):
            # Speak the character to the right of the caret after
            # the current right character has been deleted.
            #
            offset = text.caretOffset
            [character, startOffset, endOffset] = \
                text.getTextAtOffset(
                    offset,
                    pyatspi.TEXT_BOUNDARY_CHAR)

        else:
            return

        if self.getLinkIndex(event.source, text.caretOffset) >= 0:
            voice = self.voices[settings.HYPERLINK_VOICE]
        elif character.isupper():
            voice = self.voices[settings.UPPERCASE_VOICE]
        else:
            voice = self.voices[settings.DEFAULT_VOICE]

        # We won't interrupt what else might be being spoken
        # right now because it is typically something else
        # related to this event.
        #
        speech.speak(character, voice, False)

    def onTextInserted(self, event):
        """Called whenever text is inserted into an object.

        Arguments:
        - event: the Event
        """

        # We don't always get focus: events for text areas, so if we
        # see inserted text events for a focused text area, we silently
        # set them to be the locus of focus..
        #
        if event and event.source and \
           (event.source != orca_state.locusOfFocus) and \
            event.source.getState().contains(pyatspi.STATE_FOCUSED):
            orca.setLocusOfFocus(event, event.source, False)

        # Ignore text insertions from non-focused objects, unless the
        # currently focused object is the parent of the object from which
        # text was inserted.
        #
        if (event.source != orca_state.locusOfFocus) \
            and (event.source.parent != orca_state.locusOfFocus):
            return

        # We'll also ignore sliders because we get their output via
        # their values changing.
        #
        if event.source.getRole() == pyatspi.ROLE_SLIDER:
            return

        self.updateBraille(event.source)

        text = event.any_data

        # If this is a spin button, then speak the text and return.
        #
        if event.source.getRole() == pyatspi.ROLE_SPIN_BUTTON:
            speech.speak(text)
            return

        # If the last input event was a keyboard event, check to see if
        # the text for this event matches what the user typed. If it does,
        # then don't speak it.
        #
        # Note that the text widgets sometimes compress their events,
        # thus we might get a longer string from a single text inserted
        # event, while we also get individual keyboard events for the
        # characters used to type the string.  This is ugly.  We attempt
        # to handle it here by only echoing text if we think it was the
        # result of a command (e.g., a paste operation).
        #
        # Note that we have to special case the space character as it
        # comes across as "space" in the keyboard event and " " in the
        # text event.
        #
        speakThis = False
        if isinstance(orca_state.lastInputEvent, input_event.KeyboardEvent):
            keyString = orca_state.lastNonModifierKeyEvent.event_string
            wasAutoComplete = (event.source.getRole() == pyatspi.ROLE_TEXT and \
                               event.source.queryText().getNSelections())
            wasCommand = orca_state.lastInputEvent.modifiers \
                         & (1 << pyatspi.MODIFIER_CONTROL \
                            | 1 << pyatspi.MODIFIER_ALT \
                            | 1 << pyatspi.MODIFIER_META \
                            | 1 << pyatspi.MODIFIER_META2 \
                            | 1 << pyatspi.MODIFIER_META3)
            if (text == " " and keyString == "space") \
                or (text == keyString):
                pass
            elif wasCommand or wasAutoComplete:
                speakThis = True
            elif (event.source.getRole() == pyatspi.ROLE_PASSWORD_TEXT) and \
                 settings.enableKeyEcho and settings.enablePrintableKeys:
                # Echoing "star" is preferable to echoing the descriptive
                # name of the bullet that has appeared (e.g. "black circle")
                #
                text = "*"
                speakThis = True

        elif isinstance(orca_state.lastInputEvent, \
                        input_event.MouseButtonEvent) and \
             orca_state.lastInputEvent.button == "2":
            speakThis = True

        if speakThis:
            if text.isupper():
                speech.speak(text, self.voices[settings.UPPERCASE_VOICE])
            else:
                speech.speak(text)

        if settings.enableEchoByWord \
           and self.isWordDelimiter(text.decode("UTF-8")[-1:]):
            self.echoPreviousWord(event.source)

    def onActiveDescendantChanged(self, event):
        """Called when an object who manages its own descendants detects a
        change in one of its children.

        Arguments:
        - event: the Event
        """

        if not event.source.getState().contains(pyatspi.STATE_FOCUSED):
            return

        # There can be cases when the object that fires an
        # active-descendant-changed event has no children. In this case,
        # use the object that fired the event, otherwise, use the child.
        #
        child = event.any_data
        if child:
            orca.setLocusOfFocus(event, child)
        else:
            orca.setLocusOfFocus(event, event.source)

        # We'll tuck away the activeDescendant information for future
        # reference since the AT-SPI gives us little help in finding
        # this.
        #
        if orca_state.locusOfFocus \
           and (orca_state.locusOfFocus != event.source):
            self.pointOfReference['activeDescendantInfo'] = \
                [orca_state.locusOfFocus.parent,
                 orca_state.locusOfFocus.getIndexInParent()]

    def onLinkSelected(self, event):
        """Called when a hyperlink is selected in a text area.

        Arguments:
        - event: the Event
        """

        # [[[TODO: WDW - HACK one might think we could expect an
        # application to keep its name, but it appears as though
        # yelp has an identity problem and likes to start calling
        # itself "yelp," but then changes its name to "Mozilla"
        # on Fedora Core 4 after the user selects a link.  So, we'll
        # just assume that link-selected events always come from the
        # application with focus.]]]
        #
        #if orca_state.locusOfFocus \
        #   and (orca_state.locusOfFocus.app == event.source.app):
        #    orca.setLocusOfFocus(event, event.source)
        orca.setLocusOfFocus(event, event.source)

    def onStateChanged(self, event):
        """Called whenever an object's state changes.

        Arguments:
        - event: the Event
        """

        # Do we care?
        #
        if event.type.startswith("object:state-changed:active"):
            if self.findCommandRun:
                self.findCommandRun = False
                self.find()
                return

        if event.type.startswith("object:state-changed:focused"):
            iconified = False
            try:
                window = self.getTopLevel(event.source)
                iconified = window.getState().contains(pyatspi.STATE_ICONIFIED)
            except:
                debug.println(debug.LEVEL_FINEST,
                        "onStateChanged: could not get frame of focused item")
            if not iconified:
                if event.detail1:
                    self.onFocus(event)
                # We don't set locus of focus of None here because it
                # wreaks havoc on the code that determines the context
                # when you tab from widget to widget.  For example,
                # tabbing between panels in the gtk-demo buttons demo.
                #
                #else:
                #    orca.setLocusOfFocus(event, None)
                return

        # Handle tooltip popups.
        #
        if event.source.getRole() == pyatspi.ROLE_TOOL_TIP:
            obj = event.source

            if event.type.startswith("object:state-changed:showing"):
                if event.detail1 == 1:
                    self.presentTooltip(obj)
                elif orca_state.locusOfFocus \
                    and isinstance(orca_state.lastInputEvent,
                                   input_event.KeyboardEvent) \
                    and (orca_state.lastNonModifierKeyEvent.event_string \
                                                                  == "F1"):
                    self.updateBraille(orca_state.locusOfFocus)
                    speech.speakUtterances(self.speechGenerator.getSpeech(
                        orca_state.locusOfFocus,
                        False))

            return

        if state_change_notifiers.has_key(event.source.getRole()):
            notifiers = state_change_notifiers[event.source.getRole()]
            found = False
            for state in notifiers:
                if state and event.type.endswith(state):
                    found = True
                    break
            if found:
                orca.visualAppearanceChanged(event, event.source)

        # [[[TODO: WDW - HACK we'll handle this in the visual appearance
        # changed handler.]]]
        #
        # The object with focus might become insensitive, so we need to
        # flag that.  This typically occurs in wizard dialogs such as
        # the account setup assistant in Evolution.
        #
        #if event.type.endswith("sensitive") \
        #   and (event.detail1 == 0) \
        #   and event.source == orca_state.locusOfFocus:
        #    print "FOO INSENSITIVE"
        #    #orca.setLocusOfFocus(event, None)

    def onSelectionChanged(self, event):
        """Called when an object's selection changes.

        Arguments:
        - event: the Event
        """

        if not event or not event.source:
            return

        # Avoid doing this with objects that manage their descendants
        # because they'll issue a descendant changed event.
        #
        if event.source.getState().contains(pyatspi.STATE_MANAGES_DESCENDANTS):
            return

        if event.source.getRole() == pyatspi.ROLE_COMBO_BOX:
            orca.visualAppearanceChanged(event, event.source)

        # We treat selected children as the locus of focus. When the
        # selection changed we want to update the locus of focus. If
        # there is no selection, we default the locus of focus to the
        # containing object.
        #
        elif (event.source != orca_state.locusOfFocus) and \
            event.source.getState().contains(pyatspi.STATE_FOCUSED):
            newFocus = event.source
            if event.source.childCount:
                selection = event.source.querySelection()
                if selection.nSelectedChildren > 0:
                    newFocus = selection.getSelectedChild(0)

            orca.setLocusOfFocus(event, newFocus)

    def onValueChanged(self, event):
        """Called whenever an object's value changes.  Currently, the
        value changes for non-focused objects are ignored.

        Arguments:
        - event: the Event
        """

        # We'll let caret moved and text inserted events be used to
        # manage spin buttons, since they basically are text areas.
        #
        if event.source.getRole() == pyatspi.ROLE_SPIN_BUTTON:
            return

        # We'll also try to ignore those objects that keep telling
        # us their value changed even though it hasn't.
        #
        value = event.source.queryValue()
        if self.pointOfReference.has_key("oldValue") \
           and (value.currentValue == self.pointOfReference["oldValue"]):
            return

        orca.visualAppearanceChanged(event, event.source)
        if event.source.getState().contains(pyatspi.STATE_FOCUSED):
            self.pointOfReference["oldValue"] = value.currentValue

    def onWindowActivated(self, event):
        """Called whenever a toplevel window is activated.

        Arguments:
        - event: the Event
        """

        self.windowActivateTime = time.time()
        orca.setLocusOfFocus(event, event.source)

        # We keep track of the active window to handle situations where
        # we get window activated and window deactivated events out of
        # order (see onWindowDeactivated).
        #
        # For example, events can be:
        #
        #    window:activate   (w1)
        #    window:activate   (w2)
        #    window:deactivate (w1)
        #
        # as well as:
        #
        #    window:activate   (w1)
        #    window:deactivate (w1)
        #    window:activate   (w2)
        #
        orca_state.activeWindow = event.source

    def onWindowDeactivated(self, event):
        """Called whenever a toplevel window is deactivated.

        Arguments:
        - event: the Event
        """

        # If we receive a "window:deactivate" event for the object that
        # currently has focus, then stop the current speech output.
        # This is very useful for terminating long speech output from
        # commands running in gnome-terminal.
        #
        if orca_state.locusOfFocus and \
          (orca_state.locusOfFocus.getApplication() == \
             event.source.getApplication()):
            speech.stop()

        # Because window activated and deactivated events may be
        # received in any order when switching from one application to
        # another, locusOfFocus and activeWindow, we really only change
        # the locusOfFocus and activeWindow when we are dealing with
        # an event from the current activeWindow.
        #
        if event.source == orca_state.activeWindow:
            orca.setLocusOfFocus(event, None)
            orca_state.activeWindow = None

    def onMouseButton(self, event):
        """Called whenever the user presses or releases a mouse button.

        Arguments:
        - event: the Event
        """

        # If we've received a mouse button released event, then check if
        # there are and text selections for the locus of focus and speak
        # them.
        #
        state = event.type[-1]
        if state == "r":
            obj = orca_state.locusOfFocus
            try:
                text = obj.queryText()
            except:
                pass
            else:
                [textContents, startOffset, endOffset] = \
                    self.whereAmI._getTextSelections(obj, True)
                if textContents:
                    utterances = []
                    utterances.append(textContents)

                    # Translators: when the user selects (highlights) text in
                    # a document, Orca lets them know this.
                    #
                    # ONLY TRANSLATE THE PART AFTER THE PIPE CHARACTER |
                    #
                    utterances.append(Q_("text|selected"))
                    speech.speakUtterances(utterances)
                self.updateBraille(orca_state.locusOfFocus)

    def noOp(self, event):
        """Just here to capture events.

        Arguments:
        - event: the Event
        """
        pass

    ########################################################################
    #                                                                      #
    # Utilities                                                            #
    #                                                                      #
    ########################################################################

    def isLayoutOnly(self, obj):
        """Returns True if the given object is a table and is for layout
        purposes only."""

        layoutOnly = False

        if obj:
            attributes = obj.getAttributes()
        else:
            attributes = None

        if obj and (obj.getRole() == pyatspi.ROLE_TABLE) and attributes:
            for attribute in attributes:
                if attribute == "layout-guess:true":
                    layoutOnly = True
                    break
        elif obj and (obj.getRole() == pyatspi.ROLE_PANEL):
            text = self.getDisplayedText(obj)
            label = self.getDisplayedLabel(obj)
            if not ((label and len(label)) or (text and len(text))):
                layoutOnly = True

        if layoutOnly:
            debug.println(debug.LEVEL_FINEST,
                          "Object deemed to be for layout purposes only: %s" \
                          % obj)

        return layoutOnly

    def toggleTableCellReadMode(self, inputEvent=None):
        """Toggles an indicator for whether we should just read the current
        table cell or read the whole row."""

        settings.readTableCellRow = not settings.readTableCellRow
        if settings.readTableCellRow:
            # Translators: when users are navigating a table, they
            # sometimes want the entire row of a table read, or
            # they just want the current cell to be presented to them.
            #
            line = _("Speak row")
        else:
            # Translators: when users are navigating a table, they
            # sometimes want the entire row of a table read, or
            # they just want the current cell to be presented to them.
            #
            line = _("Speak cell")

        speech.speak(line)

        return True

    def textAttrsToDictionary(self, tokenString):
        """Converts a string of text attribute tokens of the form
        <key>:<value>; into a dictionary of keys and values.
        Text before the colon is the key and text afterwards is the
        value. If there is a final semi-colon, then it's ignored.

        Arguments:
        - tokenString: the string of tokens containing <key>:<value>; pairs.

        Returns a list containing two items:
        A list of the keys in the order they were extracted from the
        text attribute string and a dictionary of key/value items.
        """

        keyList = []
        dictionary = {}
        allTokens = tokenString.split(";")
        for token in allTokens:
            item = token.split(":")
            if len(item) == 2:
                key = item[0].strip()
                attribute = item[1].strip()
                keyList.append(key)
                dictionary[key] = attribute

        return [keyList, dictionary]

    def outputCharAttributes(self, keys, attributes):
        """Speak each of the text attributes given dictionary.

        Arguments:
        - attributes: a dictionary of text attributes to speak.
        """

        for key in keys:
            if attributes.has_key(key):
                attribute = attributes[key]
                if attribute:
                    # If it's the 'weight' attribute and greater than 400, just
                    # speak it as bold, otherwise speak the weight.
                    #
                    if key == "weight" and int(attribute) > 400:
                        # Translators: bold as in the font sense.
                        #
                        line = _("bold")
                    elif key == "left-margin" or key == "right-margin":
                        # We need to test if we are getting a margin value
                        # that includes unit information (OOo now provides
                        # this). If not, then we will assume it's pixels.
                        #
                        numericPoint = locale.localeconv()["decimal_point"]
                        lastChar = attribute[len(attribute) - 1]
                        if lastChar == numericPoint or \
                           lastChar in string.digits:
                            # Translators: these represent the number of pixels
                            # for the left or right margins in a document.  We
                            # are hesitant to interpret the values -- they are
                            # given to us in some unknown form by the 
                            # application, so we leave things in plural form 
                            # here.
                            #
                            line = ngettext("%s %s pixel",
                                            "%s %s pixels",
                                            int(attribute)) % (key, attribute)
                        else:
                            line = key + " " + attribute
                    else:
                        line = key + " " + attribute
                    speech.speak(line)

    def readCharAttributes(self, inputEvent=None):
        """Reads the attributes associated with the current text character.
        Calls outCharAttributes to speak a list of attributes. By default,
        a certain set of attributes will be spoken. If this is not desired,
        then individual application scripts should override this method to
        only speak the subset required.
        """

        try:
            text = orca_state.locusOfFocus.queryText()
        except:
            pass
        else:
            caretOffset = text.caretOffset

            # Creates dictionaries of the default attributes, plus the set
            # of attributes specific to the character at the caret offset.
            # Combine these two dictionaries and then extract just the
            # entries we are interested in.
            #
            defAttributes = text.getDefaultAttributes()
            debug.println(debug.LEVEL_FINEST, \
                "readCharAttributes: default text attributes: %s" % \
                defAttributes)
            [defUser, defDict] = self.textAttrsToDictionary(defAttributes)
            allAttributes = defDict

            charAttributes = text.getAttributes(caretOffset)
            if charAttributes[0]:
                [charList, charDict] = \
                    self.textAttrsToDictionary(charAttributes[0])

                # It looks like some applications like Evolution and Star
                # Office don't implement getDefaultAttributes(). In that
                # case, the best we can do is use the specific text
                # attributes for this character returned by getAttributes().
                #
                if allAttributes:
                    for key in charDict.keys():
                        allAttributes[key] = charDict[key]
                else:
                    allAttributes = charDict

            # Get a dictionary of text attributes that the user cares about.
            #
            [userAttrList, userAttrDict] = \
                self.textAttrsToDictionary(settings.enabledSpokenTextAttributes)

            # Create a dictionary of just the items we are interested in.
            # Always include size and family-name. For the others, if the
            # value is the default, then ignore it.
            #
            attributes = {}
            for key in userAttrList:
                if allAttributes.has_key(key):
                    textAttr = allAttributes.get(key)
                    userAttr = userAttrDict.get(key)
                    if textAttr != userAttr or len(userAttr) == 0:
                        attributes[key] = textAttr

            self.outputCharAttributes(userAttrList, attributes)

        return True

    def reportScriptInfo(self, inputEvent=None):
        """Output useful information on the current script via speech
        and braille.  This information will be helpful to script writers.
        """

        infoString = "SCRIPT INFO: Script name='%s'" % self.name
        app = orca_state.locusOfFocus.getApplication()
        if orca_state.locusOfFocus and app:
            infoString += " Application name='%s'" \
                          % app.name

            try:
                infoString += " Toolkit name='%s'" \
                              % app.toolkitName
            except:
                infoString += " Toolkit unknown"

            try:
                infoString += " Version='%s'" \
                              % app.version
            except:
                infoString += " Version unknown"

            debug.println(debug.LEVEL_INFO, infoString)
            speech.speak(infoString)
            braille.displayMessage(infoString)

        return True

    def enterLearnMode(self, inputEvent=None):
        """Turns learn mode on.  The user must press the escape key to exit
        learn mode.

        Returns True to indicate the input event has been consumed.
        """

        if settings.learnModeEnabled:
            return True

        self.exitLearnModeKeyBinding = keybindings.KeyBinding(
            "Escape",
            0,
            0,
            self.inputEventHandlers["exitLearnModeHandler"])
        self.keyBindings.add(self.exitLearnModeKeyBinding)

        speech.speak(
            # Translators: Orca has a "Learn Mode" that will allow
            # the user to type any key on the keyboard and hear what
            # the effects of that key would be.  The effects might
            # be what Orca would do if it had a handler for the
            # particular key combination, or they might just be to
            # echo the name of the key if Orca doesn't have a handler.
            # This text here is what is spoken to the user.
            #
            _("Entering learn mode.  Press any key to hear its function.  " \
              "To exit learn mode, press the escape key."))

        # Translators: Orca has a "Learn Mode" that will allow
        # the user to type any key on the keyboard and hear what
        # the effects of that key would be.  The effects might
        # be what Orca would do if it had a handler for the
        # particular key combination, or they might just be to
        # echo the name of the key if Orca doesn't have a handler.
        # This text here is what is to be presented on the braille
        # display.
        #
        braille.displayMessage(_("Learn mode.  Press escape to exit."))
        settings.learnModeEnabled = True
        return True

    def exitLearnMode(self, inputEvent=None):
        """Turns learn mode off.

        Returns True to indicate the input event has been consumed.
        """

        self.keyBindings.remove(self.exitLearnModeKeyBinding)

        # Translators: Orca has a "Learn Mode" that will allow
        # the user to type any key on the keyboard and hear what
        # the effects of that key would be.  The effects might
        # be what Orca would do if it had a handler for the
        # particular key combination, or they might just be to
        # echo the name of the key if Orca doesn't have a handler.
        # Exiting learn mode puts the user back in normal operating
        # mode.
        #
        message = _("Exiting learn mode.")
        speech.speak(message)
        braille.displayMessage(message)
        return True

    def pursueForFlatReview(self, obj):
        """Determines if we should look any further at the object
        for flat review."""
        return obj.getState().contains(pyatspi.STATE_SHOWING)

    def getFlatReviewContext(self):
        """Returns the flat review context, creating one if necessary."""

        if not self.flatReviewContext:
            self.flatReviewContext = self.flatReviewContextClass(self)
            self.justEnteredFlatReviewMode = True

            # Remember where the cursor currently was
            # when the user was in focus tracking mode.  We'll try to
            # keep the position the same as we move to characters above
            # and below us.
            #
            self.targetCursorCell = braille.cursorCell

        return self.flatReviewContext

    def toggleFlatReviewMode(self, inputEvent=None):
        """Toggles between flat review mode and focus tracking mode."""

        if self.flatReviewContext:
            self.drawOutline(-1, 0, 0, 0)
            self.flatReviewContext = None
            self.updateBraille(orca_state.locusOfFocus)
        else:
            context = self.getFlatReviewContext()
            [wordString, x, y, width, height] = \
                     context.getCurrent(flat_review.Context.WORD)
            self.drawOutline(x, y, width, height)
            self._reviewCurrentItem(inputEvent, self.targetCursorCell)

        return True

    def updateBrailleReview(self, targetCursorCell=0):
        """Obtains the braille regions for the current flat review line
        and displays them on the braille display.  If the targetCursorCell
        is non-0, then an attempt will be made to postion the review cursor
        at that cell.  Otherwise, we will pan in display-sized increments
        to show the review cursor."""

        context = self.getFlatReviewContext()

        [regions, regionWithFocus] = context.getCurrentBrailleRegions()
        if not regions:
            regions = []
            regionWithFocus = None

        line = braille.Line()
        line.addRegions(regions)
        braille.setLines([line])
        braille.setFocus(regionWithFocus, False)
        if regionWithFocus:
            braille.panToOffset(regionWithFocus.brailleOffset \
                                + regionWithFocus.cursorOffset)

        if self.justEnteredFlatReviewMode:
            braille.refresh(True, self.targetCursorCell)
            self.justEnteredFlatReviewMode = False
        else:
            braille.refresh(True, targetCursorCell)

    def _setFlatReviewContextToBeginningOfBrailleDisplay(self):
        """Sets the character of interest to be the first character showing
        at the beginning of the braille display."""

        context = self.getFlatReviewContext()
        [regions, regionWithFocus] = context.getCurrentBrailleRegions()
        for region in regions:
            if ((region.brailleOffset + len(region.string.decode("UTF-8"))) \
                   > braille._viewport[0]) \
                and (isinstance(region, braille.ReviewText) \
                     or isinstance(region, braille.ReviewComponent)):
                position = max(region.brailleOffset, braille._viewport[0])
                offset = position - region.brailleOffset
                self.targetCursorCell = region.brailleOffset \
                                        - braille._viewport[0]
                [word, charOffset] = region.zone.getWordAtOffset(offset)
                if word:
                    self.flatReviewContext.setCurrent(
                        word.zone.line.index,
                        word.zone.index,
                        word.index,
                        charOffset)
                else:
                    self.flatReviewContext.setCurrent(
                        region.zone.line.index,
                        region.zone.index,
                        0, # word index
                        0) # character index
                break

    def panBrailleLeft(self, inputEvent=None, panAmount=0):
        """Pans the braille display to the left.  If panAmount is non-zero,
        the display is panned by that many cells.  If it is 0, the display
        is panned one full display width.  In flat review mode, panning
        beyond the beginning will take you to the end of the previous line.

        In focus tracking mode, the cursor stays at its logical position.
        In flat review mode, the review cursor moves to character
        associated with cell 0."""

        if self.flatReviewContext:
            if braille.beginningIsShowing:
                self.flatReviewContext.goBegin(flat_review.Context.LINE)
                self.reviewPreviousCharacter(inputEvent)
            else:
                braille.panLeft(panAmount)

            # This will update our target cursor cell
            #
            self._setFlatReviewContextToBeginningOfBrailleDisplay()

            [charString, x, y, width, height] = \
                self.flatReviewContext.getCurrent(flat_review.Context.CHAR)
            self.drawOutline(x, y, width, height)

            self.targetCursorCell = 1
            self.updateBrailleReview(self.targetCursorCell)
        elif braille.beginningIsShowing and orca_state.locusOfFocus \
             and self.isTextArea(orca_state.locusOfFocus):
            # If we're at the beginning of a line of a multiline text
            # area, then force it's caret to the end of the previous
            # line.  The assumption here is that we're currently
            # viewing the line that has the caret -- which is a pretty
            # good assumption for focus tacking mode.  When we set the
            # caret position, we will get a caret event, which will
            # then update the braille.
            #
            text = orca_state.locusOfFocus.queryText()
            [lineString, startOffset, endOffset] = text.getTextAtOffset(
                text.caretOffset,
                pyatspi.TEXT_BOUNDARY_LINE_START)
            if startOffset > 0:
                text.setCaretOffset(startOffset - 1)
        else:
            braille.panLeft(panAmount)
            braille.refresh(False)

        return True

    def panBrailleLeftOneChar(self, inputEvent=None):
        """Nudges the braille display one character to the left.

        In focus tracking mode, the cursor stays at its logical position.
        In flat review mode, the review cursor moves to character
        associated with cell 0."""

        self.panBrailleLeft(inputEvent, 1)

    def panBrailleRight(self, inputEvent=None, panAmount=0):
        """Pans the braille display to the right.  If panAmount is non-zero,
        the display is panned by that many cells.  If it is 0, the display
        is panned one full display width.  In flat review mode, panning
        beyond the end will take you to the begininng of the next line.

        In focus tracking mode, the cursor stays at its logical position.
        In flat review mode, the review cursor moves to character
        associated with cell 0."""

        if self.flatReviewContext:
            if braille.endIsShowing:
                self.flatReviewContext.goEnd(flat_review.Context.LINE)
                self.reviewNextCharacter(inputEvent)
            else:
                braille.panRight(panAmount)

            # This will update our target cursor cell
            #
            self._setFlatReviewContextToBeginningOfBrailleDisplay()

            [charString, x, y, width, height] = \
                self.flatReviewContext.getCurrent(flat_review.Context.CHAR)

            self.drawOutline(x, y, width, height)

            self.targetCursorCell = 1
            self.updateBrailleReview(self.targetCursorCell)
        elif braille.endIsShowing and orca_state.locusOfFocus \
             and self.isTextArea(orca_state.locusOfFocus):
            # If we're at the end of a line of a multiline text area, then
            # force it's caret to the beginning of the next line.  The
            # assumption here is that we're currently viewing the line that
            # has the caret -- which is a pretty good assumption for focus
            # tacking mode.  When we set the caret position, we will get a
            # caret event, which will then update the braille.
            #
            text = orca_state.locusOfFocus.queryText()
            [lineString, startOffset, endOffset] = text.getTextAtOffset(
                text.caretOffset,
                pyatspi.TEXT_BOUNDARY_LINE_START)
            if endOffset < text.characterCount:
                text.setCaretOffset(endOffset)
        else:
            braille.panRight(panAmount)
            braille.refresh(False)

        return True

    def panBrailleRightOneChar(self, inputEvent=None):
        """Nudges the braille display one character to the right.

        In focus tracking mode, the cursor stays at its logical position.
        In flat review mode, the review cursor moves to character
        associated with cell 0."""

        self.panBrailleRight(inputEvent, 1)

    def goBrailleHome(self, inputEvent=None):
        """Returns to the component with focus."""

        if self.flatReviewContext:
            return self.toggleFlatReviewMode(inputEvent)
        else:
            return braille.returnToRegionWithFocus(inputEvent)

    def leftClickReviewItem(self, inputEvent=None):
        """Performs a left mouse button click on the current item."""

        self.getFlatReviewContext().clickCurrent(1)
        return True

    def rightClickReviewItem(self, inputEvent=None):
        """Performs a right mouse button click on the current item."""

        self.getFlatReviewContext().clickCurrent(3)
        return True

    def reviewCurrentLine(self, inputEvent):
        """Presents the current flat review line via braille and speech."""

        clickCount = self.getClickCount(self.lastReviewCurrentEvent,
                                           inputEvent)
        self._reviewCurrentLine(inputEvent, clickCount)
        self.lastReviewCurrentEvent = inputEvent

        return True

    def _reviewCurrentLine(self, inputEvent, clickCount=1):
        """Presents the current flat review line via braille and speech.

        Arguments:
        - inputEvent - the current input event.
        - clickCount - number of times the user has "clicked" the current key.
        """

        context = self.getFlatReviewContext()

        [lineString, x, y, width, height] = \
                 context.getCurrent(flat_review.Context.LINE)
        self.drawOutline(x, y, width, height)

        # Don't announce anything from speech if the user used
        # the Braille display as an input device.
        #
        if not isinstance(inputEvent, input_event.BrailleEvent):
            if (not lineString) \
               or (not len(lineString)) \
               or (lineString == "\n"):
                # Translators: "blank" is a short word to mean the
                # user has navigated to an empty line.
                #
                speech.speak(_("blank"))
            elif lineString.isspace():
                # Translators: "white space" is a short phrase to mean the
                # user has navigated to a line with only whitespace on it.
                #
                speech.speak(_("white space"))
            elif lineString.isupper() and (clickCount < 2 or clickCount > 3):
                speech.speak(lineString, self.voices[settings.UPPERCASE_VOICE])
            elif clickCount == 2:
                self.spellCurrentItem(lineString)
            elif clickCount == 3:
                self.phoneticSpellCurrentItem(lineString)
            else:
                lineString = self.adjustForRepeats(lineString)
                speech.speak(lineString)

        self.updateBrailleReview()

        return True

    def reviewPreviousLine(self, inputEvent):
        """Moves the flat review context to the beginning of the
        previous line."""

        context = self.getFlatReviewContext()

        moved = context.goPrevious(flat_review.Context.LINE,
                                   flat_review.Context.WRAP_LINE)

        if moved:
            self._reviewCurrentLine(inputEvent)
            self.targetCursorCell = braille.cursorCell

        return True

    def reviewHome(self, inputEvent):
        """Moves the flat review context to the top left of the current
        window."""

        context = self.getFlatReviewContext()

        context.goBegin()

        self._reviewCurrentLine(inputEvent)
        self.targetCursorCell = braille.cursorCell

        return True

    def reviewNextLine(self, inputEvent):
        """Moves the flat review context to the beginning of the
        next line.  Places the flat review cursor at the beginning
        of the line."""

        context = self.getFlatReviewContext()

        moved = context.goNext(flat_review.Context.LINE,
                               flat_review.Context.WRAP_LINE)

        if moved:
            self._reviewCurrentLine(inputEvent)
            self.targetCursorCell = braille.cursorCell

        return True

    def reviewBottomLeft(self, inputEvent):
        """Moves the flat review context to the beginning of the
        last line in the window.  Places the flat review cursor at
        the beginning of the line."""

        context = self.getFlatReviewContext()

        context.goEnd(flat_review.Context.WINDOW)
        context.goBegin(flat_review.Context.LINE)
        self._reviewCurrentLine(inputEvent)
        self.targetCursorCell = braille.cursorCell

        return True

    def reviewEnd(self, inputEvent):
        """Moves the flat review context to the end of the
        last line in the window.  Places the flat review cursor
        at the end of the line."""

        context = self.getFlatReviewContext()
        context.goEnd()

        self._reviewCurrentLine(inputEvent)
        self.targetCursorCell = braille.cursorCell

        return True

    def reviewCurrentItem(self, inputEvent, targetCursorCell=0):
        """Speak/Braille the current item to the user. A "double-click"
        of this key will cause the word to be spelt. A "triple-click"
        will cause the word to be phonetically spelt.
        """

        clickCount = self.getClickCount(self.lastReviewCurrentEvent,
                                           inputEvent)
        self._reviewCurrentItem(inputEvent, targetCursorCell, clickCount)
        self.lastReviewCurrentEvent = inputEvent

        return True

    def spellCurrentItem(self, itemString):
        """Spell the current flat review word or line.

        Arguments:
        - itemString: the string to spell.
        """

        for (charIndex, character) in enumerate(itemString.decode("UTF-8")):
            if character.isupper():
                speech.speak(character.encode("UTF-8"),
                             self.voices[settings.UPPERCASE_VOICE])
            else:
                speech.speak(character.encode("UTF-8"))

    def _reviewCurrentItem(self, inputEvent, targetCursorCell=0,
                           clickCount=1):
        """Presents the current item to the user.

        Arguments:
        - inputEvent - the current input event.
        - targetCursorCell - if non-zero, the target braille cursor cell.
        - clickCount - number of times the user has "clicked" the current key.
        """

        context = self.getFlatReviewContext()
        [wordString, x, y, width, height] = \
                 context.getCurrent(flat_review.Context.WORD)
        self.drawOutline(x, y, width, height)

        # Don't announce anything from speech if the user used
        # the Braille display as an input device.
        #
        if not isinstance(inputEvent, input_event.BrailleEvent):
            if (not wordString) \
               or (not len(wordString)) \
               or (wordString == "\n"):
                # Translators: "blank" is a short word to mean the
                # user has navigated to an empty line.
                #
                speech.speak(_("blank"))
            else:
                [lineString, x, y, width, height] = \
                         context.getCurrent(flat_review.Context.LINE)
                if lineString == "\n":
                    # Translators: "blank" is a short word to mean the
                    # user has navigated to an empty line.
                    #
                    speech.speak(_("blank"))
                elif wordString.isspace():
                    # Translators: "white space" is a short phrase to mean the
                    # user has navigated to a line with only whitespace on it.
                    #
                    speech.speak(_("white space"))
                elif wordString.isupper() \
                     and (clickCount < 2 or clickCount > 3):
                    speech.speak(wordString,
                                 self.voices[settings.UPPERCASE_VOICE])
                elif clickCount == 2:
                    self.spellCurrentItem(wordString)
                elif clickCount == 3:
                    self.phoneticSpellCurrentItem(wordString)
                else:
                    wordString = self.adjustForRepeats(wordString)
                    speech.speak(wordString)

        self.updateBrailleReview(targetCursorCell)

        return True

    def reviewCurrentAccessible(self, inputEvent):
        context = self.getFlatReviewContext()
        [zoneString, x, y, width, height] = \
                 context.getCurrent(flat_review.Context.ZONE)
        self.drawOutline(x, y, width, height)

        # Don't announce anything from speech if the user used
        # the Braille display as an input device.
        #
        if not isinstance(inputEvent, input_event.BrailleEvent):
            speech.speakUtterances(
                self.speechGenerator.getSpeech(
                    context.getCurrentAccessible(), False))

        return True

    def reviewPreviousItem(self, inputEvent):
        """Moves the flat review context to the previous item.  Places
        the flat review cursor at the beginning of the item."""

        context = self.getFlatReviewContext()

        moved = context.goPrevious(flat_review.Context.WORD,
                                   flat_review.Context.WRAP_LINE)

        if moved:
            self._reviewCurrentItem(inputEvent)
            self.targetCursorCell = braille.cursorCell

        return True

    def reviewNextItem(self, inputEvent):
        """Moves the flat review context to the next item.  Places
        the flat review cursor at the beginning of the item."""

        context = self.getFlatReviewContext()

        moved = context.goNext(flat_review.Context.WORD,
                               flat_review.Context.WRAP_LINE)

        if moved:
            self._reviewCurrentItem(inputEvent)
            self.targetCursorCell = braille.cursorCell

        return True

    def reviewCurrentCharacter(self, inputEvent):
        """Presents the current flat review character via braille and speech.
        """

        clickCount = self.getClickCount(self.lastReviewCurrentEvent,
                                           inputEvent)
        self._reviewCurrentCharacter(inputEvent, clickCount)
        self.lastReviewCurrentEvent = inputEvent

        return True

    def _reviewCurrentCharacter(self, inputEvent, clickCount=1):
        """Presents the current flat review character via braille and speech.

        Arguments:
        - inputEvent - the current input event.
        - clickCount - number of times the user has "clicked" the current key.
        """

        context = self.getFlatReviewContext()

        [charString, x, y, width, height] = \
                 context.getCurrent(flat_review.Context.CHAR)
        self.drawOutline(x, y, width, height)

        # Don't announce anything from speech if the user used
        # the Braille display as an input device.
        #
        if not isinstance(inputEvent, input_event.BrailleEvent):
            if (not charString) or (not len(charString)):
                # Translators: "blank" is a short word to mean the
                # user has navigated to an empty line.
                #
                speech.speak(_("blank"))
            else:
                [lineString, x, y, width, height] = \
                         context.getCurrent(flat_review.Context.LINE)
                if lineString == "\n":
                    # Translators: "blank" is a short word to mean the
                    # user has navigated to an empty line.
                    #
                    speech.speak(_("blank"))
                elif clickCount == 2:
                    self.spellCurrentItem(charString)
                elif clickCount == 3:
                    self.phoneticSpellCurrentItem(charString)
                elif charString.isupper():
                    speech.speak(charString,
                                 self.voices[settings.UPPERCASE_VOICE])
                else:
                    speech.speak(charString)

        self.updateBrailleReview()

        return True

    def reviewPreviousCharacter(self, inputEvent):
        """Moves the flat review context to the previous character.  Places
        the flat review cursor at character."""

        context = self.getFlatReviewContext()

        moved = context.goPrevious(flat_review.Context.CHAR,
                                   flat_review.Context.WRAP_LINE)

        if moved:
            self._reviewCurrentCharacter(inputEvent)
            self.targetCursorCell = braille.cursorCell

        return True

    def reviewEndOfLine(self, inputEvent):
        """Moves the flat review context to the end of the line.  Places
        the flat review cursor at the end of the line."""

        context = self.getFlatReviewContext()
        context.goEnd(flat_review.Context.LINE)

        self.reviewCurrentCharacter(inputEvent)
        self.targetCursorCell = braille.cursorCell

        return True

    def reviewNextCharacter(self, inputEvent):
        """Moves the flat review context to the next character.  Places
        the flat review cursor at character."""

        context = self.getFlatReviewContext()

        moved = context.goNext(flat_review.Context.CHAR,
                               flat_review.Context.WRAP_LINE)

        if moved:
            self._reviewCurrentCharacter(inputEvent)
            self.targetCursorCell = braille.cursorCell

        return True

    def reviewAbove(self, inputEvent):
        """Moves the flat review context to the character most directly
        above the current flat review cursor.  Places the flat review
        cursor at character."""

        context = self.getFlatReviewContext()

        moved = context.goAbove(flat_review.Context.CHAR,
                                flat_review.Context.WRAP_LINE)

        if moved:
            self._reviewCurrentItem(inputEvent, self.targetCursorCell)

        return True

    def reviewBelow(self, inputEvent):
        """Moves the flat review context to the character most directly
        below the current flat review cursor.  Places the flat review
        cursor at character."""

        context = self.getFlatReviewContext()

        moved = context.goBelow(flat_review.Context.CHAR,
                                flat_review.Context.WRAP_LINE)

        if moved:
            self._reviewCurrentItem(inputEvent, self.targetCursorCell)

        return True

    def showZones(self, inputEvent):
        """Debug routine to paint rectangles around the discrete
        interesting (e.g., text)  zones in the active window for
        this application.
        """

        flatReviewContext = self.getFlatReviewContext()
        lines = flatReviewContext.lines
        for line in lines:
            lineString = ""
            for zone in line.zones:
                lineString += " '%s' [%s]" % \
                          (zone.string, zone.accessible.getRoleName())
                self.drawOutline(zone.x, zone.y, zone.width, zone.height,
                                 False)
            debug.println(debug.LEVEL_OFF, lineString)
        self.flatReviewContext = None

    def find(self, query=None):
        """Searches for the specified query.  If no query is specified,
        it searches for the query specified in the Orca Find dialog.

        Arguments:
        - query: The search query to find.
        """

        if not query:
            query = find.getLastQuery()
        if query:
            context = self.getFlatReviewContext()
            location = query.findQuery(context, self.justEnteredFlatReviewMode)
            if not location:
                # Translators: the Orca "Find" dialog allows a user to
                # search for text in a window and then move focus to
                # that text.  For example, they may want to find the
                # "OK" button.  This message lets them know a string
                # they were searching for was not found.
                #
                message = _("string not found")
                braille.displayMessage(message)
                speech.speak(message)
            else:
                context.setCurrent(location.lineIndex, location.zoneIndex, \
                                   location.wordIndex, location.charIndex)
                self.reviewCurrentItem(None)
                self.targetCursorCell = braille.cursorCell

    def findNext(self, inputEvent):
        """Searches forward for the next instance of the string
        searched for via the Orca Find dialog.  Other than direction
        and the starting point, the search options initially specified
        (case sensitivity, window wrap, and full/partial match) are
        preserved.
        """

        lastQuery = find.getLastQuery()
        if lastQuery:
            lastQuery.searchBackwards = False
            lastQuery.startAtTop = False
            self.find(lastQuery)
        else:
            orca._showFindGUI()

    def findPrevious(self, inputEvent):
        """Searches backwards for the next instance of the string
        searched for via the Orca Find dialog.  Other than direction
        and the starting point, the search options initially specified
        (case sensitivity, window wrap, and full/or partial match) are
        preserved.
        """

        lastQuery = find.getLastQuery()
        if lastQuery:
            lastQuery.searchBackwards = True
            lastQuery.startAtTop = False
            self.find(lastQuery)
        else:
            orca._showFindGUI()
            
    def goToBookmark(self, inputEvent): 
        """ Go to the bookmark indexed by inputEvent.hw_code.  Delegates to 
        Bookmark.goToBookmark """
        bookmarks = self.getBookmarks()
        bookmarks.goToBookmark(inputEvent)
    
    def addBookmark(self, inputEvent): 
        """ Add an in-page accessible object bookmark for this key.
        Delegates to Bookmark.addBookmark """
        bookmarks = self.getBookmarks()
        bookmarks.addBookmark(inputEvent)
    
    def bookmarkCurrentWhereAmI(self, inputEvent):
        """ Report "Where am I" information for this bookmark relative to the 
        current pointer location.  Delegates to 
        Bookmark.bookmarkCurrentWhereAmI""" 
        bookmarks = self.getBookmarks()
        bookmarks.bookmarkCurrentWhereAmI(inputEvent)
    
    def saveBookmarks(self, inputEvent): 
        """ Save the bookmarks for this script. Delegates to 
        Bookmark.saveBookmarks """
        bookmarks = self.getBookmarks()
        bookmarks.saveBookmarks(inputEvent)
    
    def goToNextBookmark(self, inputEvent): 
        """ Go to the next bookmark location.  If no bookmark has yet to be
        selected, the first bookmark will be used.  Delegates to 
        Bookmark.goToNextBookmark """
        bookmarks = self.getBookmarks()
        bookmarks.goToNextBookmark(inputEvent)
    
    def goToPrevBookmark(self, inputEvent):
        """ Go to the previous bookmark location.  If no bookmark has yet to 
        be selected, the first bookmark will be used.  Delegates to 
        Bookmark.goToPrevBookmark """ 
        bookmarks = self.getBookmarks()
        bookmarks.goToPrevBookmark(inputEvent)
           
########################################################################
#                                                                      #
# DEBUG support.                                                       #
#                                                                      #
########################################################################

    def _isInterestingObj(self, obj):
        import inspect

        interesting = False

        if getattr(obj, "__class__", None):
            name = obj.__class__.__name__
            if name not in ["function",
                            "type",
                            "list",
                            "dict",
                            "tuple",
                            "wrapper_descriptor",
                            "module",
                            "method_descriptor",
                            "member_descriptor",
                            "instancemethod",
                            "builtin_function_or_method",
                            "frame",
                            "classmethod",
                            "classmethod_descriptor",
                            "_Environ",
                            "MemoryError",
                            "_Printer",
                            "_Helper",
                            "getset_descriptor",
                            "weakref",
                            "property",
                            "cell",
                            "staticmethod",
                            "EventListener",
                            "KeystrokeListener",
                            "KeyBinding",
                            "InputEventHandler",
                            "Rolename"]:
                try:
                    filename = inspect.getabsfile(obj.__class__)
                    if filename.index("orca"):
                        interesting = True
                except:
                    pass

        return interesting

    def _detectCycle(self, obj, visitedObjs, indent=""):
        """Attempts to discover a cycle in object references."""

        # [[[TODO: WDW - not sure this really works.]]]

        import gc
        visitedObjs.append(obj)
        for referent in gc.get_referents(obj):
            try:
                if visitedObjs.index(referent):
                    if self._isInterestingObj(referent):
                        print indent, "CYCLE!!!!", `referent`
                    break
            except:
                pass
            self._detectCycle(referent, visitedObjs, " " + indent)
        visitedObjs.remove(obj)

    def _printObjInfo(self, indent, obj):
        """Prints information about an object, if we care about it."""
        if self._isInterestingObj(obj):
            print indent, obj.__class__.__name__, `obj`

    def printMemoryUsageHandler(self, inputEvent):
        """Prints memory usage information."""
        print 'TODO: print something useful for memory debugging'

    def printAppsHandler(self, inputEvent=None):
        """Prints a list of all applications to stdout."""
        self.printApps()
        return True

    def printActiveAppHandler(self, inputEvent=None):
        """Prints the currently active application."""
        self.printActiveApp()
        return True

    def printAncestryHandler(self, inputEvent=None):
        """Prints the ancestry for the current locusOfFocus"""
        self.printAncestry(orca_state.locusOfFocus)
        return True

    def printHierarchyHandler(self, inputEvent=None):
        """Prints the application for the current locusOfFocus"""
        if orca_state.locusOfFocus:
            self.printHierarchy(orca_state.locusOfFocus.getApplication(),
                                orca_state.locusOfFocus)
        return True

# Routines that were previously in util.py, but that have now been moved
# here so that they can be customized in application scripts if so desired.
#

    def isSameObject(self, obj1, obj2):
        if (obj1 == obj2):
            return True
        elif (not obj1) or (not obj2):
            return False

        try:
            if (obj1.name != obj2.name) or (obj1.getRole() != obj2.getRole()):
                return False
            else:
                # Gecko sometimes creates multiple accessibles to represent
                # the same object.  If the two objects have the same name
                # and the same role, check the extents.  If those also match
                # then the two objects are for all intents and purposes the
                # same object.
                #
                extents1 = \
                    obj1.queryComponent().getExtents(pyatspi.DESKTOP_COORDS)
                extents2 = \
                    obj2.queryComponent().getExtents(pyatspi.DESKTOP_COORDS)
                if (extents1.x == extents2.x) and \
                   (extents1.y == extents2.y) and \
                   (extents1.width == extents2.width) and \
                   (extents1.height == extents2.height):
                    return True

            # When we're looking at children of objects that manage
            # their descendants, we will often get different objects
            # that point to the same logical child.  We want to be able
            # to determine if two objects are in fact pointing to the
            # same child.
            # If we cannot do so easily (i.e., object equivalence), we examine
            # the hierarchy and the object index at each level.
            #
            parent1 = obj1
            parent2 = obj2
            while (parent1 and parent2 and \
                    parent1.getState().contains( \
                        pyatspi.STATE_TRANSIENT) and \
                    parent2.getState().contains(pyatspi.STATE_TRANSIENT)):
                if parent1.getIndexInParent() != parent2.getIndexInParent():
                    return False
                parent1 = parent1.parent
                parent2 = parent2.parent
            if parent1 and parent2 and parent1 == parent2:
                return True
        except:
            pass

        # In java applications, TRANSIENT state is missing for tree items
        # (fix for bug #352250)
        #
        try:
            parent1 = obj1
            parent2 = obj2
            while parent1 and parent2 and \
                    parent1.getRole() == pyatspi.ROLE_LABEL and \
                    parent2.getRole() == pyatspi.ROLE_LABEL:
                if parent1.getIndexInParent() != parent2.getIndexInParent():
                    return False
                parent1 = parent1.parent
                parent2 = parent2.parent
            if parent1 and parent2 and parent1 == parent2:
                return True
        except:
            pass

        return False

    def appendString(self, text, newText, delimiter=" "):
        """Appends the newText to the given text with the delimiter in between
        and returns the new string.  Edge cases, such as no initial text or
        no newText, are handled gracefully."""

        if (not newText) or (len(newText) == 0):
            return text
        elif text and len(text):
            return text + delimiter + newText
        else:
            return newText

    def __hasLabelForRelation(self, label):
        """Check if label has a LABEL_FOR relation

        Arguments:
        - label: the label in question

        Returns TRUE if label has a LABEL_FOR relation.
        """
        if (not label) or (label.getRole() != pyatspi.ROLE_LABEL):
            return False

        relations = label.getRelationSet()

        for relation in relations:
            if relation.getRelationType() \
                   == pyatspi.RELATION_LABEL_FOR:
                return True

        return False

    def __isLabeling(self, label, obj):
        """Check if label is connected via  LABEL_FOR relation with object

        Arguments:
        - obj: the object in question
        - labeled: the label in question

        Returns TRUE if label has a relation LABEL_FOR for object.
        """

        if (not obj) \
           or (not label) \
           or (label.getRole() != pyatspi.ROLE_LABEL):
            return False

        relations = label.getRelationSet()
        if not relations:
            return False

        for relation in relations:
            if relation.getRelationType() \
                   == pyatspi.RELATION_LABEL_FOR:

                for i in range(0, relation.getNTargets()):
                    target = relation.getTarget(i)
                    if target == obj:
                        return True

        return False

    def getUnicodeCurrencySymbols(self):
        """Return a list of the unicode currency symbols, populating the list
        if this is the first time that this routine has been called.

        Returns a list of unicode currency symbols.
        """

        if not self._unicodeCurrencySymbols:
            self._unicodeCurrencySymbols = [ \
                u'\u0024',     # dollar sign
                u'\u00A2',     # cent sign
                u'\u00A3',     # pound sign
                u'\u00A4',     # currency sign
                u'\u00A5',     # yen sign
                u'\u0192',     # latin small letter f with hook
                u'\u060B',     # afghani sign
                u'\u09F2',     # bengali rupee mark
                u'\u09F3',     # bengali rupee sign
                u'\u0AF1',     # gujarati rupee sign
                u'\u0BF9',     # tamil rupee sign
                u'\u0E3F',     # thai currency symbol baht
                u'\u17DB',     # khmer currency symbol riel
                u'\u2133',     # script capital m
                u'\u5143',     # cjk unified ideograph-5143
                u'\u5186',     # cjk unified ideograph-5186
                u'\u5706',     # cjk unified ideograph-5706
                u'\u5713',     # cjk unified ideograph-5713
                u'\uFDFC',     # rial sign
            ]

            # Add 20A0 (EURO-CURRENCY SIGN) to 20B5 (CEDI SIGN)
            #
            for ordChar in range(ord(u'\u20A0'), ord(u'\u20B5') + 1):
                self._unicodeCurrencySymbols.append(unichr(ordChar))

        return self._unicodeCurrencySymbols

    def findDisplayedLabel(self, obj):
        """Return a list of the objects that are labelling this object.

        Argument:
        - obj: the object in question

        Returns a list of the objects that are labelling this object.
        """

        # For some reason, some objects are labelled by the same thing
        # more than once.  Go figure, but we need to check for this.
        #
        label = []
        relations = obj.getRelationSet()
        allTargets = []

        for relation in relations:
            if relation.getRelationType() \
                   == pyatspi.RELATION_LABELLED_BY:

                # The object can be labelled by more than one thing, so we just
                # get all the labels (from unique objects) and append them
                # together.  An example of such objects live in the "Basic"
                # page of the gnome-accessibility-keyboard-properties app.
                # The "Delay" and "Speed" objects are labelled both by
                # their names and units.
                #
                for i in range(0, relation.getNTargets()):
                    target = relation.getTarget(i)
                    if not target in allTargets:
                        allTargets.append(target)
                        label.append(target)

        # [[[TODO: HACK - we've discovered oddness in hierarchies such as
        # the gedit Edit->Preferences dialog.  In this dialog, we have
        # labeled groupings of objects.  The grouping is done via a FILLER
        # with two children - one child is the overall label, and the
        # other is the container for the grouped objects.  When we detect
        # this, we add the label to the overall context.
        #
        # We are also looking for objects which have a PANEL or a FILLER as
        # parent, and its parent has more children. Through these children,
        # a potential label with LABEL_FOR relation may exists. We want to
        # present this label.
        # This case can be seen in FileChooserDemo application, in Open dialog
        # window, the line with "Look In" label, a combobox and some
        # presentation buttons.
        #
        # Finally, we are searching the hierarchy of embedded components for
        # children that are labels.]]]
        #
        if not len(label):
            potentialLabels = []
            useLabel = False
            if (obj.getRole() == pyatspi.ROLE_EMBEDDED):
                candidate = obj
                while candidate.childCount:
                    candidate = candidate[0]
                # The parent of this object may contain labels
                # or it may contain filler that contains labels.
                #
                candidate = candidate.parent
                for child in candidate:
                    if child.getRole() == pyatspi.ROLE_FILLER:
                        candidate = child
                        break
                # If there are labels in this embedded component,
                # they should be here.
                #
                for child in candidate:
                    if child.getRole() == pyatspi.ROLE_LABEL:
                        useLabel = True
                        potentialLabels.append(child)
            elif ((obj.getRole() == pyatspi.ROLE_FILLER) \
                    or (obj.getRole() == pyatspi.ROLE_PANEL)) \
                and (obj.childCount == 2):
                child0, child1 = obj
                child0_role = child0.getRole()
                child1_role = child1.getRole()
                if child0_role == pyatspi.ROLE_LABEL \
                    and not self.__hasLabelForRelation(child0) \
                    and child1_role in [pyatspi.ROLE_FILLER, \
                                             pyatspi.ROLE_PANEL]:
                    useLabel = True
                    potentialLabels.append(child0)
                elif child1_role == pyatspi.ROLE_LABEL \
                    and not self.__hasLabelForRelation(child1) \
                    and child0_role in [pyatspi.ROLE_FILLER, \
                                             pyatspi.ROLE_PANEL]:
                    useLabel = True
                    potentialLabels.append(child1)
            else:
                parent = obj.parent
                if parent and \
                    ((parent.getRole() == pyatspi.ROLE_FILLER) \
                            or (parent.getRole() == pyatspi.ROLE_PANEL)):
                    for potentialLabel in parent:
                        try:
                            useLabel = self.__isLabeling(potentialLabel, obj)
                            if useLabel:
                                potentialLabels.append(potentialLabel)
                                break
                        except:
                            pass

            if useLabel and len(potentialLabels):
                label = potentialLabels

        return label

    def getDisplayedLabel(self, obj):
        """If there is an object labelling the given object, return the
        text being displayed for the object labelling this object.
        Otherwise, return None.

        Argument:
        - obj: the object in question

        Returns the string of the object labelling this object, or None
        if there is nothing of interest here.
        """

        labelString = None
        labels = self.findDisplayedLabel(obj)
        for label in labels:
            labelString = self.appendString(labelString, 
                                            self.getDisplayedText(label))

        return labelString

    def __getDisplayedTextInComboBox(self, combo):

        """Returns the text being displayed in a combo box.  If nothing is
        displayed, then None is returned.

        Arguments:
        - combo: the combo box

        Returns the text in the combo box or an empty string if nothing is
        displayed.
        """

        displayedText = None

        # Find the text displayed in the combo box.  This is either:
        #
        # 1) The last text object that's a child of the combo box
        # 2) The selected child of the combo box.
        # 3) The contents of the text of the combo box itself when
        #    treated as a text object.
        #
        # Preference is given to #1, if it exists.
        #
        # If the label of the combo box is the same as the utterance for
        # the child object, then this utterance is only displayed once.
        #
        # [[[TODO: WDW - Combo boxes are complex beasts.  This algorithm
        # needs serious work.  Logged as bugzilla bug 319745.]]]
        #
        textObj = None
        for child in combo:
            if child and child.getRole() == pyatspi.ROLE_TEXT:
                textObj = child

        if textObj:
            [displayedText, caretOffset, startOffset] = \
                self.getTextLineAtCaret(textObj)
            #print "TEXTOBJ", displayedText
        else:
            try:
                comboSelection = combo.querySelection()
                selectedItem = comboSelection.getSelectedChild(0)
            except:
                selectedItem = None

            if selectedItem:
                displayedText = self.getDisplayedText(selectedItem)
                #print "SELECTEDITEM", displayedText
            elif combo.name and len(combo.name):
                # We give preference to the name over the text because
                # the text for combo boxes seems to never change in
                # some cases.  The main one where we see this is in
                # the gaim "Join Chat" window.
                #
                displayedText = combo.name
                #print "NAME", displayedText
            else:
                [displayedText, caretOffset, startOffset] = \
                    self.getTextLineAtCaret(combo)
                # Set to None instead of empty string.
                displayedText = displayedText or None
                #print "TEXT", displayedText

        return displayedText

    def getDisplayedText(self, obj):
        """Returns the text being displayed for an object.

        Arguments:
        - obj: the object

        Returns the text being displayed for an object or None if there isn't
        any text being shown.
        """

        displayedText = None

        role = obj.getRole()
        if role == pyatspi.ROLE_COMBO_BOX:
            return self.__getDisplayedTextInComboBox(obj)

        # The accessible text of an object is used to represent what is
        # drawn on the screen.
        #
        try:
            text = obj.queryText()
        except NotImplementedError:
            pass
        else:
            displayedText = text.getText(0, -1)

            # [[[WDW - HACK to account for things such as Gecko that want
            # to use the EMBEDDED_OBJECT_CHARACTER on a label to hold the
            # object that has the real accessible text for the label.  We
            # detect this by the specfic case where the text for the
            # current object is a single EMBEDDED_OBJECT_CHARACTER.  In
            # this case, we look to the child for the real text.]]]
            #
            unicodeText = displayedText.decode("UTF-8")
            if unicodeText \
               and (len(unicodeText) == 1) \
               and (unicodeText[0] == self.EMBEDDED_OBJECT_CHARACTER) \
               and obj.childCount > 0:
                try:
                    displayedText = self.getDisplayedText(obj[0])
                except:
                    debug.printException(debug.LEVEL_WARNING)
            elif unicodeText:
                # [[[TODO: HACK - Welll.....we'll just plain ignore any
                # text with EMBEDDED_OBJECT_CHARACTERs here.  We still need a
                # general case to handle this stuff and expand objects
                # with EMBEDDED_OBJECT_CHARACTERs.]]]
                #
                for i in range(0, len(unicodeText)):
                    if unicodeText[i] == self.EMBEDDED_OBJECT_CHARACTER:
                        displayedText = None
                        break

        if not displayedText:
            displayedText = obj.name

        # [[[WDW - HACK because push buttons can have labels as their
        # children.  An example of this is the Font: button on the General
        # tab in the Editing Profile dialog in gnome-terminal.
        #
        if not displayedText and role == pyatspi.ROLE_PUSH_BUTTON:
            for child in obj:
                if child.getRole() == pyatspi.ROLE_LABEL:
                    childText = self.getDisplayedText(child)
                    if childText and len(childText):
                        displayedText = self.appendString(displayedText,
                                                          childText)

        return displayedText

    def getTextForValue(self, obj):
        """Returns the text to be displayed for the object's current value.

        Arguments:
        - obj: the Accessible object that may or may not have a value.

        Returns a string representing the value.
        """

        try:
            value = obj.queryValue()
        except NotImplementedError:
            return ""

        # OK, this craziness is all about trying to figure out the most
        # meaningful formatting string for the floating point values.
        # The number of places to the right of the decimal point should
        # be set by the minimumIncrement, but the minimumIncrement isn't
        # always set.  So...we'll default the minimumIncrement to 1/100
        # of the range.  But, if max == min, then we'll just go for showing
        # them off to two meaningful digits.
        #
        try:
            minimumIncrement = value.minimumIncrement
        except:
            minimumIncrement = 0.0

        if minimumIncrement == 0.0:
            minimumIncrement = (value.maximumValue - value.minimumValue) \
                               / 100.0

        try:
            decimalPlaces = max(0, -math.log10(minimumIncrement))
        except:
            try:
                decimalPlaces = max(0, -math.log10(value.minimumValue))
            except:
                try:
                    decimalPlaces = max(0, -math.log10(value.maximumValue))
                except:
                    decimalPlaces = 0

        formatter = "%%.%df" % decimalPlaces
        valueString = formatter % value.currentValue
        #minString   = formatter % value.minimumValue
        #maxString   = formatter % value.maximumValue

        # [[[TODO: WDW - probably want to do this as a percentage at some
        # point?  Logged as bugzilla bug 319743.]]]
        #
        return valueString

    def findFocusedObject(self, root):
        """Returns the accessible that has focus under or including the
        given root.

        TODO: This will currently traverse all children, whether they are
        visible or not and/or whether they are children of parents that
        manage their descendants.  At some point, this method should be
        optimized to take such things into account.

        Arguments:
        - root: the root object where to start searching

        Returns the object with the FOCUSED state or None if no object with
        the FOCUSED state can be found.
        """

        if root.getState().contains(pyatspi.STATE_FOCUSED):
            return root

        for child in root:
            try:
                candidate = self.findFocusedObject(child)
                if candidate:
                    return candidate
            except:
                pass

        return None

    def getRealActiveDescendant(self, obj):
        """Given an object that should be a child of an object that
        manages its descendants, return the child that is the real
        active descendant carrying useful information.

        Arguments:
        - obj: an object that should be a child of an object that
        manages its descendants.
        """

        # If obj is a table cell and all of it's children are table cells
        # (probably cell renderers), then return the first child which has
        # a non zero length text string. If no such object is found, just
        # fall through and use the default approach below. See bug #376791
        # for more details.
        #
        if obj.getRole() == pyatspi.ROLE_TABLE_CELL and obj.childCount:
            nonTableCellFound = False
            for child in obj:
                if child.getRole() != pyatspi.ROLE_TABLE_CELL:
                    nonTableCellFound = True
            if not nonTableCellFound:
                for child in obj:
                    try:
                        text = child.queryText()
                    except NotImplementedError:
                        continue
                    else:
                        if text.getText(0, -1):
                            return child

        # [[[TODO: WDW - this is an odd hacky thing I've somewhat drawn
        # from Gnopernicus.  The notion here is that we get an active
        # descendant changed event, but that object tends to have children
        # itself and we need to decide what to do.  Well...the idea here
        # is that the last child (Gnopernicus chooses child(1)), tends to
        # be the child with information.  The previous children tend to
        # be non-text or just there for spacing or something.  You will
        # see this in the various table demos of gtk-demo and you will
        # also see this in the Contact Source Selector in Evolution.
        #
        # Just note that this is most likely not a really good solution
        # for the general case.  That needs more thought.  But, this
        # comment is here to remind us this is being done in poor taste
        # and we need to eventually clean up our act.]]]
        #
        if obj and obj.childCount:
            return obj[-1]
        else:
            return obj

    def getClickCount(self, lastInputEvent, inputEvent):
        """Return the count of the number of clicks a user has made to one
        of the keys on the keyboard.

        Arguments:
        - lastInputEvent: the last input event.
        - inputEvent: the current input event.
        """

        if not isinstance(inputEvent, input_event.KeyboardEvent):
            orca_state.clickCount = 0
            return orca_state.clickCount

        if not isinstance(lastInputEvent, input_event.KeyboardEvent):
            orca_state.clickCount = 1
            return orca_state.clickCount

        if (lastInputEvent.hw_code != inputEvent.hw_code) or \
           (lastInputEvent.modifiers != inputEvent.modifiers):
            orca_state.clickCount = 1
            return orca_state.clickCount

        if (inputEvent.time - lastInputEvent.time) < \
                settings.doubleClickTimeout:
            orca_state.clickCount += 1
        else:
            orca_state.clickCount = 1
        return orca_state.clickCount

    def isDesiredFocusedItem(self, obj, rolesList):
        """Called to determine if the given object and it's hierarchy of
           parent objects, each have the desired roles.

        Arguments:
        - obj: the accessible object to check.
        - rolesList: the list of desired roles for the components and the
          hierarchy of its parents.

        Returns True if all roles match.
        """
        current = obj
        for role in rolesList:
            if current is None:
                return False

            if isinstance(role, str):
                current_role = current.getRoleName()
            else:
                current_role = current.getRole()

            if current_role != role:
                return False
            current = current.parent

        return True

    def speakMisspeltWord(self, allTokens, badWord):
        """Called by various spell checking routine to speak the misspelt word,
           plus the context that it is being used in.

        Arguments:
        - allTokens: a list of all the words.
        - badWord: the misspelt word.
        """

        # Create an utterance to speak consisting of the misspelt
        # word plus the context where it is used (upto five words
        # to either side of it).
        #
        for i in range(0, len(allTokens)):
            if allTokens[i].startswith(badWord):
                minIndex = i - 5
                if minIndex < 0:
                    minIndex = 0
                maxIndex = i + 5
                if maxIndex > (len(allTokens) - 1):
                    maxIndex = len(allTokens) - 1

                # Translators: Orca will provide more compelling output of
                # the spell checking dialog in some applications.  The first
                # thing it does is let them know what the misspelled word
                # is.
                #
                utterances = [_("Misspelled word: %s") % badWord]

                # Translators: Orca will provide more compelling output of
                # the spell checking dialog in some applications.  The second
                # thing it does is give the phrase containing the misspelled
                # word in the document.  This is known as the context.
                #
                contextPhrase = " ".join(allTokens[minIndex:maxIndex+1])
                utterances.append(_("Context is %s") % contextPhrase)

                # Turn the list of utterances into a string.
                text = " ".join(utterances)
                speech.speak(text)

    def textLines(self, obj):
        """Creates a generator that can be used to iterate over each line
        of a text object, starting at the caret offset.

        Arguments:
        - obj: an Accessible that has a text specialization

        Returns an iterator that produces elements of the form:
        [SayAllContext, acss], where SayAllContext has the text to be
        spoken and acss is an ACSS instance for speaking the text.
        """

        try:
            text = obj.queryText()
        except:
            return

        length = text.characterCount
        offset = text.caretOffset

        # Determine the correct "say all by" mode to use.
        #
        if settings.sayAllStyle == settings.SAYALL_STYLE_SENTENCE:
            mode = pyatspi.TEXT_BOUNDARY_SENTENCE_END
        elif settings.sayAllStyle == settings.SAYALL_STYLE_LINE:
            mode = pyatspi.TEXT_BOUNDARY_LINE_START
        else:
            mode = pyatspi.TEXT_BOUNDARY_LINE_START

        # Get the next line of text to read
        #
        done = False
        while not done:
            lastEndOffset = -1
            while offset < length:
                [lineString, startOffset, endOffset] = text.getTextAtOffset(
                    offset, mode)

                # Some applications that don't support sentence boundaries
                # will provide the line boundary results instead; others
                # will return nothing.
                #
                if not lineString:
                    mode = pyatspi.TEXT_BOUNDARY_LINE_START
                    [lineString, startOffset, endOffset] = \
                        text.getTextAtOffset(offset, mode)

                # [[[WDW - HACK: well...gnome-terminal sometimes wants to
                # give us outrageous values back from getTextAtOffset
                # (see http://bugzilla.gnome.org/show_bug.cgi?id=343133),
                # so we try to handle it.]]]
                #
                if startOffset < 0:
                    break

                # [[[WDW - HACK: this is here because getTextAtOffset
                # tends not to be implemented consistently across toolkits.
                # Sometimes it behaves properly (i.e., giving us an endOffset
                # that is the beginning of the next line), sometimes it
                # doesn't (e.g., giving us an endOffset that is the end of
                # the current line).  So...we hack.  The whole 'max' deal
                # is to account for lines that might be a brazillion lines
                # long.]]]
                #
                if endOffset == lastEndOffset:
                    offset = max(offset + 1, lastEndOffset + 1)
                    lastEndOffset = endOffset
                    continue

                lastEndOffset = endOffset
                offset = endOffset

                lineString = self.adjustForRepeats(lineString)
                if lineString.isupper():
                    voice = settings.voices[settings.UPPERCASE_VOICE]
                else:
                    voice = settings.voices[settings.DEFAULT_VOICE]

                yield [speechserver.SayAllContext(obj, lineString,
                                                  startOffset, endOffset),
                       voice]

            moreLines = False
            relations = obj.getRelationSet()
            for relation in relations:
                if relation.getRelationType()  \
                       == pyatspi.RELATION_FLOWS_TO:
                    obj = relation.getTarget(0)

                    try:
                        text = obj.queryText()
                    except NotImplementedError:
                        return

                    length = text.characterCount
                    offset = 0
                    moreLines = True
                    break
            if not moreLines:
                done = True

    def _addRepeatSegment(self, segment, line, respectPunctuation=True):
        """Add in the latest line segment, adjusting for repeat characters
        and punctuation.

        Arguments:
        - segment: the segment of repeated characters.
        - line: the current built-up line to characters to speak.
        - respectPunctuation: if False, ignore punctuation level.

        Returns: the current built-up line plus the new segment, after
        adjusting for repeat character counts and punctuation.
        """

        style = settings.verbalizePunctuationStyle
        isPunctChar = True
        try:
            level, action = punctuation_settings.getPunctuationInfo(segment[0])
        except:
            isPunctChar = False
        count = len(segment)
        if (count >= settings.repeatCharacterLimit) \
           and (not segment[0] in string.whitespace):
            if (not respectPunctuation) \
               or (isPunctChar and (style <= level)):
                repeatChar = chnames.getCharacterName(segment[0])
                # Translators: Orca will tell you how many characters
                # are repeated on a line of text.  For example: "22
                # space characters".  The %d is the number and the %s
                # is the spoken word for the character.
                #
                line += " " + ngettext("%d %s character",
                                       "%d %s characters",
                                       count) % (count, repeatChar)
            else:
                line += segment
        else:
            line += segment

        return line

    def adjustForRepeats(self, line):
        """Adjust line to include repeat character counts.
        As some people will want this and others might not,
        there is a setting in settings.py that determines
        whether this functionality is enabled.

        repeatCharacterLimit = <n>

        If <n> is 0, then there would be no repeat characters.
        Otherwise <n> would be the number of same characters (or more)
        in a row that cause the repeat character count output.
        If the value is set to 1, 2 or 3 then it's treated as if it was
        zero. In other words, no repeat character count is given.

        Arguments:
        - line: the string to adjust for repeat character counts.

        Returns: a new line adjusted for repeat character counts (if enabled).
        """

        line = line.decode("UTF-8")

        if (len(line) < 4) or (settings.repeatCharacterLimit < 4):
            return line.encode("UTF-8")

        newLine = u''
        segment = lastChar = line[0]

        multipleChars = False
        for i in range(1, len(line)):
            if line[i] == lastChar:
                segment += line[i]
            else:
                multipleChars = True
                newLine = self._addRepeatSegment(segment, newLine)
                segment = line[i]

            lastChar = line[i]

        newLine = self._addRepeatSegment(segment, newLine, multipleChars)

        # Pylint is confused and flags this with the following error:
        #
        # E1103:5188:Script.adjustForRepeats: Instance of 'True' has
        # no 'encode' member (but some types could not be inferred)
        #
        # We know newLine is a unicode string, so we'll just tell pylint
        # that we know what we are doing.
        #
        # pylint: disable-msg=E1103

        return newLine.encode("UTF-8")

    def _getPronunciationForSegment(self, segment):
        """Adjust the word segment to potentially replace it with what 
        those words actually sound like. Two pronunciation dictionaries
        are checked. First the application specific one (which might be
        empty), then the default (global) one.

        Arguments: 
        - segment: the string to adjust for words in the pronunciation
          dictionaries.

        Returns: a new word segment adjusted for words found in the 
        pronunciation dictionaries, or the original word segment if there
        was no dictionary entry.
        """

        newSegment = pronunciation_dict.getPronunciation(segment,
                                     self.app_pronunciation_dict)
        if newSegment == segment:
            newSegment = pronunciation_dict.getPronunciation(segment)

        return newSegment

    def adjustForPronunciation(self, line):
        """Adjust the line to replace words in the pronunciation dictionary,
        with what those words actually sound like.

        Arguments:
        - line: the string to adjust for words in the pronunciation dictionary.

        Returns: a new line adjusted for words found in the pronunciation
        dictionary.
        """

        line = line.decode("UTF-8")
        newLine = segment = u''

        for i in range(0, len(line)):
            if self.isWordDelimiter(line[i]):
                if len(segment) != 0:
                    newLine = newLine + \
                              self._getPronunciationForSegment(segment)
                newLine = newLine + line[i]
                segment = u''
            else:
                segment += line[i]

        if len(segment) != 0:
            newLine = newLine + self._getPronunciationForSegment(segment)

        return newLine.encode("UTF-8")

    def getLinkIndex(self, obj, characterIndex):
        """A brute force method to see if an offset is a link.  This
        is provided because not all Accessible Hypertext implementations
        properly support the getLinkIndex method.  Returns an index of
        0 or greater of the characterIndex is on a hyperlink.

        Arguments:
        -obj: the Accessible object with the Accessible Hypertext specialization
        -characterIndex: the text position to check
        """

        if not obj:
            return -1

        try:
            obj.queryText()
        except NotImplementedError:
            return -1

        try:
            hypertext = obj.queryHypertext()
        except NotImplementedError:
            return -1

        for i in xrange(hypertext.getNLinks()):
            link = hypertext.getLink(i)
            if (characterIndex >= link.startIndex) \
               and (characterIndex <= link.endIndex):
                return i

        return -1

    def isWordDelimiter(self, character):
        """Returns True if the given character is a word delimiter.

        Arguments:
        - character: the character in question

        Returns True if the given character is a word delimiter.
        """

        if not isinstance(character, unicode):
            character = character.decode("UTF-8")

        return (character in string.whitespace) \
               or (character in '!*+,-./:;<=>?@[\]^_{|}') \
               or (character == self.NO_BREAK_SPACE_CHARACTER)

    def getFrame(self, obj):
        """Returns the frame containing this object, or None if this object
        is not inside a frame.

        Arguments:
        - obj: the Accessible object
        """

        debug.println(debug.LEVEL_FINEST,
                      "Finding frame for source.name="
                      + obj.name or "None")

        while obj \
              and (obj != obj.parent) \
              and (obj.getRole() != pyatspi.ROLE_FRAME):
            obj = obj.parent
            if obj:
                debug.println(debug.LEVEL_FINEST, "--> obj.name="
                          + obj.name or "None")

        if obj and (obj.getRole() == pyatspi.ROLE_FRAME):
            pass
        else:
            obj = None

        return obj

    def getTopLevel(self, obj):
        """Returns the top-level object (frame, dialog ...) containing this
        object, or None if this object is not inside a top-level object.

        Arguments:
        - obj: the Accessible object
        """

        debug.println(debug.LEVEL_FINEST,
                      "Finding top-level object for source.name="
                      + obj.name or "None")

        while obj \
              and obj.parent \
              and (obj != obj.parent) \
              and (obj.parent.getRole() != pyatspi.ROLE_APPLICATION):
            obj = obj.parent
            debug.println(debug.LEVEL_FINEST, "--> obj.name="
                          + obj.name or "None")

        if obj and obj.parent and \
           (obj.parent.getRole() == pyatspi.ROLE_APPLICATION):
            pass
        else:
            obj = None

        return obj

    def getTopLevelName(self, obj):
        """ Returns the name of the top-level object. See getTopLevel.
        """
        top = self.getTopLevel(obj)
        if (not top) or (not top.name):
            return ""
        else:
            return top.name

    def getTextLineAtCaret(self, obj):
        """Gets the line of text where the caret is.

        Argument:
        - obj: an Accessible object that implements the AccessibleText
               interface

        Returns the [string, caretOffset, startOffset] for the line of text
        where the caret is.
        """

        # Get the the AccessibleText interrface
        #
        try:
            text = obj.queryText()
        except NotImplementedError:
            return ["", 0, 0]

        # The caret might be positioned at the very end of the text area.
        # In these cases, calling text.getTextAtOffset on an offset that's
        # not positioned to a character can yield unexpected results.  In
        # particular, we'll see the Gecko toolkit return a start and end
        # offset of (0, 0), and we'll see other implementations, such as
        # gedit, return reasonable results (i.e., gedit will give us the
        # last line).
        #
        # In order to accommodate the differing behavior of different
        # AT-SPI implementations, we'll make sure we give getTextAtOffset
        # the offset of an actual character.  Then, we'll do a little check
        # to see if that character is a newline - if it is, we'll treat it
        # as the line.
        #
        if text.caretOffset == text.characterCount:
            caretOffset = max(0, text.caretOffset - 1)
            character = text.getText(caretOffset,
                                     caretOffset + 1).decode("UTF-8")
        else:
            caretOffset = text.caretOffset
            character = None

        if (text.caretOffset == text.characterCount) \
            and (character == "\n"):
            content = ""
            startOffset = caretOffset
        else:
            # Get the line containing the caret.  [[[TODO: HACK WDW - If
            # there's only 1 character in the string, well, we get it.  We
            # do this because Gecko's implementation of getTextAtOffset
            # is broken if there is just one character in the string.]]]
            #
            if (text.characterCount == 1):
                lineString = text.getText(caretOffset, caretOffset + 1)
                startOffset = caretOffset
            else:
                [lineString, startOffset, endOffset] = text.getTextAtOffset(
                    caretOffset, pyatspi.TEXT_BOUNDARY_LINE_START)

            # Sometimes we get the trailing line-feed-- remove it
            #
            content = lineString.decode("UTF-8")
            if content[-1:] == "\n":
                content = content[:-1]

        return [content.encode("UTF-8"), text.caretOffset, startOffset]

    def getNodeLevel(self, obj):
        """Determines the node level of this object if it is in a tree
        relation, with 0 being the top level node.  If this object is
        not in a tree relation, then -1 will be returned.

        Arguments:
        -obj: the Accessible object
        """

        if not obj:
            return -1

        nodes = []
        node = obj
        done = False
        while not done:
            relations = node.getRelationSet()
            node = None
            for relation in relations:
                if relation.getRelationType() \
                       == pyatspi.RELATION_NODE_CHILD_OF:
                    node = relation.getTarget(0)
                    break

            # We want to avoid situations where something gives us an
            # infinite cycle of nodes.  Bon Echo has been seen to do
            # this (see bug 351847).
            #
            if (len(nodes) > 100) or nodes.count(node):
                debug.println(debug.LEVEL_WARNING,
                              "Script.getNodeLevel detected a cycle!!!")
                done = True
            elif node:
                nodes.append(node)
                debug.println(debug.LEVEL_FINEST,
                              "Script.getNodeLevel %d" % len(nodes))
            else:
                done = True

        return len(nodes) - 1

    def getChildNodes(self, obj):
        """Gets all of the children that have RELATION_NODE_CHILD_OF pointing
        to this expanded table cell.

        Arguments:
        -obj: the Accessible Object

        Returns: a list of all the child nodes
        """

        try:
            table = obj.parent.queryTable()
        except:
            return []
        else:
            if not obj.getState().contains(pyatspi.STATE_EXPANDED):
                return []

        nodes = []        
        row = table.getRowAtIndex(obj.getIndexInParent())
        col = table.getColumnAtIndex(obj.getIndexInParent())
        nodeLevel = self.getNodeLevel(obj)
        done = False

        # Candidates will be in the rows beneath the current row.
        # Only check in the current column and stop checking as
        # soon as the node level of a candidate is equal or less
        # than our current level.
        #
        for i in range(row+1, table.nRows):
            cell = table.getAccessibleAt(i, col)
            relations = cell.getRelationSet()
            for relation in relations:
                if relation.getRelationType() \
                       == pyatspi.RELATION_NODE_CHILD_OF:
                    nodeOf = relation.getTarget(0)
                    if self.isSameObject(obj, nodeOf):
                        nodes.append(cell)
                    else:
                        currentLevel = self.getNodeLevel(nodeOf)
                        if currentLevel <= nodeLevel:
                            done = True
                    break
            if done:
                break

        return nodes

    def getAcceleratorAndShortcut(self, obj):
        """Gets the accelerator string (and possibly shortcut) for the given
        object.

        Arguments:
        - obj: the Accessible object

        A list containing the accelerator and shortcut for the given object,
        where the first element is the accelerator and the second element is
        the shortcut.
        """

        try:
            action = obj.queryAction()
        except NotImplementedError:
            return ["", ""]

        # [[[TODO: WDW - assumes the first keybinding is all that we care about.
        # Logged as bugzilla bug 319741.]]]
        #
        bindingStrings = action.getKeyBinding(0).split(';')

        # [[[TODO: WDW - assumes menu items have three bindings.  Logged as
        # bugzilla bug 319741.]]]
        #
        if len(bindingStrings) == 3:
            #mnemonic       = bindingStrings[0]
            fullShortcut   = bindingStrings[1]
            accelerator    = bindingStrings[2]
        elif len(bindingStrings) > 0:
            fullShortcut   = bindingStrings[0]
            try:
                accelerator = bindingStrings[1]
            except:
                accelerator = ""
        else:
            fullShortcut   = ""
            accelerator    = ""

        fullShortcut = fullShortcut.replace("<","")
        fullShortcut = fullShortcut.replace(">"," ")
        fullShortcut = fullShortcut.replace(":"," ")

        # If the accelerator string includes a Space, make sure we speak it.
        #
        if accelerator.endswith(" "):
            # Translators: this is the spoken word for the space character
            #
            accelerator += _("space")
        accelerator  = accelerator.replace("<","")
        accelerator  = accelerator.replace(">"," ")

        return [accelerator, fullShortcut]

    def getKnownApplications(self):
        """Retrieves the list of currently running apps for the desktop
        as a list of Accessible objects.
        """

        debug.println(debug.LEVEL_FINEST,
                      "Script.getKnownApplications...")

        apps = filter(lambda x: x is not None,
                      pyatspi.Registry.getDesktop(0))

        debug.println(debug.LEVEL_FINEST,
                      "...Script.getKnownApplications")

        return apps

    def getObjects(self, root, onlyShowing=True):
        """Returns a list of all objects under the given root.  Objects
        are returned in no particular order - this function does a simple
        tree traversal, ignoring the children of objects which report the
        MANAGES_DESCENDANTS state.

        Arguments:
        - root:        the Accessible object to traverse
        - onlyShowing: examine only those objects that are SHOWING

        Returns: a list of all objects under the specified object
        """

        # The list of object we'll return
        #
        objlist = []

        # Start at the first child of the given object
        #
        if root.childCount <= 0:
            return objlist

        for i, child in enumerate(root):
            debug.println(debug.LEVEL_FINEST,
                          "Script.getObjects looking at child %d" % i)
            if child \
               and ((not onlyShowing) or (onlyShowing and \
                    (child.getState().contains(pyatspi.STATE_SHOWING)))):
                objlist.append(child)
                if (child.getState().contains( \
                    pyatspi.STATE_MANAGES_DESCENDANTS) == 0) \
                    and (child.childCount > 0):
                    objlist.extend(self.getObjects(child, onlyShowing))

        return objlist

    def findByRole(self, root, role, onlyShowing=True):
        """Returns a list of all objects of a specific role beneath the
        given root.  [[[TODO: MM - This is very inefficient - this should
        do it's own traversal and not add objects to the list that aren't
        of the specified role.  Instead it uses the traversal from
        getObjects and then deletes objects from the list that aren't of
        the specified role.  Logged as bugzilla bug 319740.]]]

        Arguments:
        - root the Accessible object to traverse
        - role the string describing the Accessible role of the object
        - onlyShowing: examine only those objects that are SHOWING

        Returns a list of descendants of the root that are of the given role.
        """

        objlist = []
        allobjs = self.getObjects(root, onlyShowing)
        for o in allobjs:
            if o.getRole() == role:
                objlist.append(o)
        return objlist

    def findUnrelatedLabels(self, root):
        """Returns a list containing all the unrelated (i.e., have no
        relations to anything and are not a fundamental element of a
        more atomic component like a combo box) labels under the given
        root.  Note that the labels must also be showing on the display.

        Arguments:
        - root the Accessible object to traverse

        Returns a list of unrelated labels under the given root.
        """

        # Find all the labels in the dialog
        #
        allLabels = self.findByRole(root, pyatspi.ROLE_LABEL)

        # add the names of only those labels which are not associated with
        # other objects (i.e., empty relation sets).
        #
        # [[[WDW - HACK: In addition, do not grab free labels whose
        # parents are push buttons because push buttons can have labels as
        # children.]]]
        #
        # [[[WDW - HACK: panels with labelled borders will have a child
        # label that does not have its relation set.  So...we check to see
        # if the panel's name is the same as the label's name.  If so, we
        # ignore the label.]]]
        #
        unrelatedLabels = []

        for label in allLabels:
            relations = label.getRelationSet()
            if len(relations) == 0:
                parent = label.parent
                if parent and (parent.getRole() == pyatspi.ROLE_PUSH_BUTTON):
                    pass
                elif parent and (parent.getRole() == pyatspi.ROLE_PANEL) \
                   and (parent.name == label.name):
                    pass
                elif label.getState().contains(pyatspi.STATE_SHOWING):
                    unrelatedLabels.append(label)

        # Now sort the labels based on their geographic position, top to
        # bottom, left to right.  This is a very inefficient sort, but the
        # assumption here is that there will not be a lot of labels to
        # worry about.
        #
        sortedLabels = []
        for label in unrelatedLabels:
            label_extents = \
                label.queryComponent().getExtents(pyatspi.DESKTOP_COORDS)
            index = 0
            for sortedLabel in sortedLabels:
                sorted_extents = \
                    sortedLabel.queryComponent().getExtents(
                  pyatspi.DESKTOP_COORDS)
                if (label_extents.y > sorted_extents.y) \
                   or ((label_extents.y == sorted_extents.y) \
                       and (label_extents.x > sorted_extents.x)):
                    index += 1
                else:
                    break
            sortedLabels.insert(index, label)

        return sortedLabels

    def phoneticSpellCurrentItem(self, itemString):
        """Phonetically spell the current flat review word or line.

        Arguments:
        - itemString: the string to phonetically spell.
        """

        for (charIndex, character) in enumerate(itemString.decode("UTF-8")):
            if character.isupper():
                voice = settings.voices[settings.UPPERCASE_VOICE]
                character = character.lower()
            else:
                voice =  settings.voices[settings.DEFAULT_VOICE]
            phoneticString = phonnames.getPhoneticName(character)
            speech.speak(phoneticString, voice)

    def printAncestry(self, child):
        """Prints a hierarchical view of a child's ancestry."""

        if not child:
            return

        ancestorList = [child]
        parent = child.parent
        while parent and (parent.parent != parent):
            ancestorList.insert(0, parent)
            parent = parent.parent

        indent = ""
        for ancestor in ancestorList:
            print indent + "+-", debug.getAccessibleDetails(ancestor)
            indent += "  "

    def printHierarchy(self, root, ooi, indent="",
                       onlyShowing=True, omitManaged=True):
        """Prints the accessible hierarchy of all children

        Arguments:
        -indent:      Indentation string
        -root:        Accessible where to start
        -ooi:         Accessible object of interest
        -onlyShowing: If True, only show children painted on the screen
        -omitManaged: If True, omit children that are managed descendants
        """

        if not root:
            return

        if root == ooi:
            print indent + "(*)", debug.getAccessibleDetails(root)
        else:
            print indent + "+-", debug.getAccessibleDetails(root)

        rootManagesDescendants = root.getState().contains( \
                                      pyatspi.STATE_MANAGES_DESCENDANTS)

        for child in root:
            if child == root:
                print indent + "  " + "WARNING CHILD == PARENT!!!"
            elif not child:
                print indent + "  " + "WARNING CHILD IS NONE!!!"
            elif child.parent != root:
                print indent + "  " + "WARNING CHILD.PARENT != PARENT!!!"
            else:
                paint = (not onlyShowing) or (onlyShowing and \
                         child.getState().contains(pyatspi.STATE_SHOWING))
                paint = paint \
                        and ((not omitManaged) \
                             or (omitManaged and not rootManagesDescendants))

                if paint:
                    self.printHierarchy(child,
                                        ooi,
                                        indent + "  ",
                                        onlyShowing,
                                        omitManaged)

    def printApps(self):
        """Prints a list of all applications to stdout."""

        level = debug.LEVEL_OFF

        apps = self.getKnownApplications()
        debug.println(level, "There are %d Accessible applications" % len(apps))
        for app in apps:
            debug.printDetails(level, "  App: ", app, False)
            for child in app:
                debug.printDetails(level, "    Window: ", child, False)
                if child.parent != app:
                    debug.println(level,
                                  "      WARNING: child's parent is not app!!!")

        return True

    def printActiveApp(self):
        """Prints the active application."""

        level = debug.LEVEL_OFF

        window = self.findActiveWindow()
        if not window:
            debug.println(level, "Active application: None")
        else:
            app = window.getApplication()
            if not app:
                debug.println(level, "Active application: None")
            else:
                debug.println(level, "Active application: %s" % app.name)

    def isInActiveApp(self, obj):
        """Returns True if the given object is from the same application that
        currently has keyboard focus.

        Arguments:
        - obj: an Accessible object
        """

        if not obj:
            return False
        else:
            return orca_state.locusOfFocus \
                   and (orca_state.locusOfFocus.getApplication() \
                          == obj.getApplication())

    def findActiveWindow(self):
        """Traverses the list of known apps looking for one who has an
        immediate child (i.e., a window) whose state includes the active state.

        Returns the Python Accessible of the window that's active or None if
        no windows are active.
        """

        window = None
        apps = self.getKnownApplications()
        for app in apps:
            for child in app:
                try:
                    state = child.getState()
                    if state.contains(pyatspi.STATE_ACTIVE):
                        window = child
                        break
                except:
                    debug.printException(debug.LEVEL_FINEST)

        return window

    def getAncestor(self, obj, ancestorRoles, stopRoles):
        """Returns the object of the specified roles which contains the
        given object, or None if the given object is not contained within
        an object the specified roles.

        Arguments:
        - obj: the Accessible object
        - ancestorRoles: the list of roles to look for
        - stopRoles: the list of roles to stop the search at
        """

        if not obj:
            return None

        if not isinstance(ancestorRoles, [].__class__):
            ancestorRoles = [ancestorRoles]

        if not isinstance(stopRoles, [].__class__):
            stopRoles = [stopRoles]

        ancestor = None

        obj = obj.parent
        while obj and (obj != obj.parent):
            if obj.getRole() in ancestorRoles:
                ancestor = obj
                break
            elif obj.getRole() in stopRoles:
                break
            else:
                obj = obj.parent

        return ancestor

    def saveOldAppSettings(self):
        """Save a copy of all the existing application specific settings
        (as specified by the settings.userCustomizableSettings dictionary)."""

        return orca_prefs.readPreferences()

    def restoreOldAppSettings(self, prefsDict):
        """Restore a copy of all the previous saved application settings.

        Arguments:
        - prefsDict: the dictionary containing the old application settings.
        """

        for key in settings.userCustomizableSettings:
            if prefsDict.has_key(key):
                setattr(settings, key, prefsDict[key])

    ########################################################################
    #                                                                      #
    # METHODS FOR DRAWING RECTANGLES AROUND OBJECTS ON THE SCREEN          #
    #                                                                      #
    ########################################################################

    def drawOutline(self, x, y, width, height, erasePrevious=True):
        """Draws a rectangular outline around the accessible, erasing the
        last drawn rectangle in the process."""

        if not self._display:
            try:
                self._display = gtk.gdk.display_get_default()
            except:
                debug.printException(debug.LEVEL_FINEST)
                self._display = gtk.gdk.display(":0")

            if not self._display:
                debug.println(debug.LEVEL_SEVERE,
                              "Script.drawOutline could not open display.")
                return

        screen = self._display.get_default_screen()
        root_window = screen.get_root_window()
        graphics_context = root_window.new_gc()
        graphics_context.set_subwindow(gtk.gdk.INCLUDE_INFERIORS)
        graphics_context.set_function(gtk.gdk.INVERT)
        graphics_context.set_line_attributes(3,                  # width
                                             gtk.gdk.LINE_SOLID, # style
                                             gtk.gdk.CAP_BUTT,   # end style
                                             gtk.gdk.JOIN_MITER) # join style

        # Erase the old rectangle.
        #
        if self._visibleRectangle and erasePrevious:
            self.drawOutline(self._visibleRectangle[0],
                             self._visibleRectangle[1],
                             self._visibleRectangle[2],
                             self._visibleRectangle[3],
                             False)
            self._visibleRectangle = None

        # We'll use an invalid x value to indicate nothing should be
        # drawn.
        #
        if x < 0:
            self._visibleRectangle = None
            return

        # The +1 and -2 stuff here is an attempt to stay within the
        # bounding box of the object.
        #
        root_window.draw_rectangle(graphics_context,
                                   False, # Fill
                                   x + 1,
                                   y + 1,
                                   max(1, width - 2),
                                   max(1, height - 2))

        self._visibleRectangle = [x, y, width, height]

    def outlineAccessible(self, accessible, erasePrevious=True):
        """Draws a rectangular outline around the accessible, erasing the
        last drawn rectangle in the process."""

        try:
            component = accessible.queryComponent()
        except AttributeError:
            self.drawOutline(-1, 0, 0, 0, erasePrevious)
        except NotImplementedError:
            pass
        else:
            visibleRectangle = \
                component.getExtents(pyatspi.DESKTOP_COORDS)
            self.drawOutline(visibleRectangle.x, visibleRectangle.y,
                             visibleRectangle.width, visibleRectangle.height,
                             erasePrevious)

    def isTextSelected(self, obj, startOffset, endOffset):
        """Returns an indication of whether the text is selected by
        comparing the text offset with the various selected regions of
        text for this accessible object.

        Arguments:
        - obj: the Accessible object.
        - startOffset: text start offset.
        - endOffset: text end offset.

        Returns an indication of whether the text is selected.
        """

        try:
            text = obj.queryText()
        except:
            return False

        for i in xrange(text.getNSelections()):
            [startSelOffset, endSelOffset] = text.getSelection(i)
            if (startOffset >= startSelOffset) \
               and (endOffset <= endSelOffset):
                return True

        return False

    def speakTextSelectionState(self, obj, startOffset, endOffset):
        """Speak "selected" if the text was just selected, "unselected" if
        it was just unselected.

        Arguments:
        - obj: the Accessible object.
        - startOffset: text start offset.
        - endOffset: text end offset.
        """

        try:
            text = obj.queryText()
        except:
            return

        # Handle special cases.
        #
        # Shift-Page-Down:    speak "page selected from cursor position".
        # Shift-Page-Up:      speak "page selected to cursor position".
        #
        # Control-Shift-Down: speak "line selected down from cursor position".
        # Control-Shift-Up:   speak "line selected up from cursor position".
        #
        # Control-Shift-Home: speak "document selected to cursor position".
        # Control-Shift-End:  speak "document selected from cursor position".
        #
        if isinstance(orca_state.lastInputEvent, input_event.KeyboardEvent):
            eventStr = orca_state.lastNonModifierKeyEvent.event_string
            mods = orca_state.lastInputEvent.modifiers
        else:
            eventStr = None
            mods = 0

        isControlKey = mods & (1 << pyatspi.MODIFIER_CONTROL)
        isShiftKey = mods & (1 << pyatspi.MODIFIER_SHIFT)

        specialCaseFound = False
        if (eventStr == "Page_Down") and isShiftKey and not isControlKey:
            specialCaseFound = True
            # Translators: when the user selects (highlights) text in
            # a document, Orca will speak information about what they
            # have selected.
            #
            line = _("page selected from cursor position")

        elif (eventStr == "Page_Up") and isShiftKey and not isControlKey:
            specialCaseFound = True
            # Translators: when the user selects (highlights) text in
            # a document, Orca will speak information about what they
            # have selected.
            #
            line = _("page selected to cursor position")

        elif (eventStr == "Down") and isShiftKey and isControlKey:
            specialCaseFound = True
            # Translators: when the user selects (highlights) text in
            # a document, Orca will speak information about what they
            # have selected.
            #
            line = _("line selected down from cursor position")

        elif (eventStr == "Up") and isShiftKey and isControlKey:
            specialCaseFound = True
            # Translators: when the user selects (highlights) text in
            # a document, Orca will speak information about what they
            # have selected.
            #
            line = _("line selected up from cursor position")

        elif (eventStr == "Home") and isShiftKey and isControlKey:
            specialCaseFound = True
            # Translators: when the user selects (highlights) text in
            # a document, Orca will speak information about what they
            # have selected.
            #
            line = _("document selected to cursor position")

        elif (eventStr == "End") and isShiftKey and isControlKey:
            specialCaseFound = True
            # Translators: when the user selects (highlights) text in
            # a document, Orca will speak information about what they
            # have selected.
            #
            line = _("document selected from cursor position")

        if specialCaseFound:
            speech.speak(line, None, False)
            return

        try:
            # If we are selecting by word, then there possibly will be
            # whitespace characters on either end of the text. We adjust
            # the startOffset and endOffset to exclude them.
            #
            try:
                tmpStr = text.getText(startOffset, 
                                      endOffset).decode("UTF-8")
            except:
                tmpStr = u''
            n = len(tmpStr)

            # Don't strip whitespace if string length is one (might be a
            # space).
            #
            if n > 1:
                while endOffset > startOffset:
                    if self.isWordDelimiter(tmpStr[n-1]):
                        n -= 1
                        endOffset -= 1
                    else:
                        break
                n = 0
                while startOffset < endOffset:
                    if self.isWordDelimiter(tmpStr[n]):
                        n += 1
                        startOffset += 1
                    else:
                        break
        except:
            debug.printException(debug.LEVEL_FINEST)

        if self.isTextSelected(obj, startOffset, endOffset):
            # Translators: when the user selects (highlights) text in
            # a document, Orca lets them know this.
            #
            # ONLY TRANSLATE THE PART AFTER THE PIPE CHARACTER |
            #
            speech.speak(Q_("text|selected"), None, False)
        else:
            if self.pointOfReference.has_key("lastSelections"):
                for i in xrange(len(self.pointOfReference["lastSelections"])):
                    startSelOffset = \
                        self.pointOfReference["lastSelections"][0][0]
                    endSelOffset = \
                        self.pointOfReference["lastSelections"][0][1]
                    if (startOffset >= startSelOffset) \
                        and (endOffset <= endSelOffset):
                        # Translators: when the user unselects
                        # (unhighlights) text in a document, Orca lets
                        # them know this.
                        #
                        # ONLY TRANSLATE THE PART AFTER THE PIPE CHARACTER |
                        #
                        speech.speak(Q_("text|unselected"), None, False)
                        break

        # Save away the current text cursor position and list of text
        # selections for next time.
        #
        self.pointOfReference["lastCursorPosition"] = text.caretOffset
        self.pointOfReference["lastSelections"] = []
        for i in xrange(text.getNSelections()):
            self.pointOfReference["lastSelections"].append(
              text.getSelection(i))

    def getURI(self, obj):
        """Return the URI for a given link object.

        Arguments:
        - obj: the Accessible object.
        """
        return obj.queryHyperlink().getURI(0)

    def getDocumentFrame(self):
        """Dummy method used as a reminder to refactor whereamI for links,
        possibly subclassing whereamI for the Gecko script.
        """
        return None
    
    def systemBeep(self):
        """Rings the system bell.  This is really a hack.  Ideally, we want
        a method that will present an earcon (any sound designated representing
        an error, event etc)
        """
        print "\a"

# Dictionary that defines the state changes we care about for various
# objects.  The key represents the role and the value represents a list
# of states that we care about.
#
state_change_notifiers = {}

state_change_notifiers[pyatspi.ROLE_CHECK_MENU_ITEM] = ("checked", None)
state_change_notifiers[pyatspi.ROLE_CHECK_BOX]       = ("checked", None)
state_change_notifiers[pyatspi.ROLE_PANEL]           = ("showing", None)
state_change_notifiers[pyatspi.ROLE_LABEL]           = ("showing", None)
state_change_notifiers[pyatspi.ROLE_TOGGLE_BUTTON]   = ("checked", None)
state_change_notifiers[pyatspi.ROLE_TABLE_CELL]      = ("checked", "expanded",
                                                        None)
state_change_notifiers[pyatspi.ROLE_LIST_ITEM]       = ("expanded", None)
