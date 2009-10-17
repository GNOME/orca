# Orca
#
# Copyright 2004-2009 Sun Microsystems Inc.
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

"""The default Script for presenting information to the user using
both speech and Braille.  This is based primarily on the de-facto
standard implementation of the AT-SPI, which is the GAIL support
for GTK."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2004-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import locale
import math
import re
import sys
import time

import pyatspi
import braille
import chnames
import debug
import eventsynthesizer
import find
import flat_review
import input_event
import keybindings
import mag
import outline
import orca
import orca_prefs
import orca_state
import phonnames
import pronunciation_dict
import punctuation_settings
import script
import settings
import speech
import speechserver
import mouse_review
import text_attribute_names

from orca_i18n import _         # for gettext support
from orca_i18n import ngettext  # for ngettext support
from orca_i18n import C_        # to provide qualified translatable strings

########################################################################
#                                                                      #
# The Default script class.                                            #
#                                                                      #
########################################################################

class Script(script.Script):

    EMBEDDED_OBJECT_CHARACTER = u'\ufffc'
    NO_BREAK_SPACE_CHARACTER  = u'\u00a0'
    WORDS_RE = re.compile("(\W+)", re.UNICODE)
    DISPLAYED_LABEL = 'displayedLabel'
    DISPLAYED_TEXT = 'displayedText'
    KEY_BINDING = 'keyBinding'
    NESTING_LEVEL = 'nestingLevel'
    NODE_LEVEL = 'nodeLevel'
    REAL_ACTIVE_DESCENDANT = 'realActiveDescendant'

    def __init__(self, app):
        """Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """
        script.Script.__init__(self, app)

        self.flatReviewContext  = None
        self.windowActivateTime = None
        self.lastReviewCurrentEvent = None
        self.exitLearnModeKeyBinding = None
        self.targetCursorCell = None

        self.justEnteredFlatReviewMode = False

        self.digits = '0123456789'
        self.whitespace = ' \t\n\r\v\f'

        # Used to determine whether the used double clicked on the
        # "where am I" key.
        #
        self.lastWhereAmIEvent = None

        # Used to determine whether the used double clicked on the
        # "say all" key.
        #
        self.lastSayAllEvent = None

        # Unicode currency symbols (populated by the
        # getUnicodeCurrencySymbols() routine).
        #
        self._unicodeCurrencySymbols = []

        # Used by the visualAppearanceChanged routine for updating whether
        # progress bars are spoken.
        #
        self.lastProgressBarTime = {}
        self.lastProgressBarValue = {}

        self.lastSelectedMenu = None

        # A dictionary of non-standardly-named text attributes and their
        # Atk equivalents.
        #
        self.attributeNamesDict = {}

        # Keep track of the last time we issued a mouse routing command
        # so that we can guess if a change resulted from our moving the
        # pointer.
        #
        self.lastMouseRoutingTime = None

        # The last location of the mouse, which we might want if routing
        # the pointer elsewhere.
        #
        self.oldMouseCoordinates = [0, 0]

    def setupInputEventHandlers(self):
        """Defines InputEventHandler fields for this script that can be
        called by the key and braille bindings."""

        self.inputEventHandlers["routePointerToItemHandler"] = \
            input_event.InputEventHandler(
                Script.routePointerToItem,
                # Translators: this command will move the mouse pointer
                # to the current item without clicking on it.
                #
                _("Routes the pointer to the current item."))

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

        self.inputEventHandlers["whereAmIBasicHandler"] = \
            input_event.InputEventHandler(
                Script.whereAmIBasic,
                # Translators: the "Where am I" feature of Orca allows
                # a user to press a key and then have information
                # about their current context spoken and brailled to
                # them.  For example, the information may include the
                # name of the current pushbutton with focus as well as
                # its mnemonic.
                #
                _("Performs the basic where am I operation."))

        self.inputEventHandlers["whereAmIDetailedHandler"] = \
            input_event.InputEventHandler(
                Script.whereAmIDetailed,
                # Translators: the "Where am I" feature of Orca allows
                # a user to press a key and then have information
                # about their current context spoken and brailled to
                # them.  For example, the information may include the
                # name of the current pushbutton with focus as well as
                # its mnemonic.
                #
                _("Performs the detailed where am I operation."))

        # [[[WDW - I'd prefer to call this presentTitleHandler, but
        # we're keeping it at getTitleHandler for backwards
        # compatibility for people who have customized their key
        # bindings.]]]
        #
        self.inputEventHandlers["getTitleHandler"] = \
            input_event.InputEventHandler(
                Script.presentTitle,
                # Translators: This command will cause the window's
                # title to be spoken.
                #
                _("Speaks the title bar."))

        # [[[WDW - I'd prefer to call this presentStatusBarHandler,
        # but we're keeping it at getStatusBarHandler for backwards
        # compatibility for people who have customized their key
        # bindings.]]]
        #
        self.inputEventHandlers["getStatusBarHandler"] = \
            input_event.InputEventHandler(
                Script.presentStatusBar,
                # Translators: This command will cause the window's
                # status bar contents to be spoken.
                #
                _("Speaks the status bar."))

        self.inputEventHandlers["findHandler"] = \
            input_event.InputEventHandler(
                orca.showFindGUI,
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
                # Translators: this is a debug message that Orca users
                # will not normally see. It describes a debug routine that
                # paints rectangles around the interesting (e.g., text)
                # zones in the active window for the application that
                # currently has focus.
                #
                _("Paints and prints the visible zones in the active window."))

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
                # {line,word,character}.  This particular command will
                # cause Orca to speak the current line.
                #
                _("Speaks the current flat review line."))

        self.inputEventHandlers["reviewSpellCurrentLineHandler"] = \
            input_event.InputEventHandler(
                Script.reviewSpellCurrentLine,
                # Translators: the 'flat review' feature of Orca
                # allows the blind user to explore the text in a
                # window in a 2D fashion.  That is, Orca treats all
                # the text from all objects in a window (e.g.,
                # buttons, labels, etc.) as a sequence of words in a
                # sequence of lines.  The flat review feature allows
                # the user to explore this text by the {previous,next}
                # {line,word,character}. This particular command will
                # cause Orca to spell the current line.
                #
                _("Spells the current flat review line."))

        self.inputEventHandlers["reviewPhoneticCurrentLineHandler"] = \
            input_event.InputEventHandler(
                Script.reviewPhoneticCurrentLine,
                # Translators: the 'flat review' feature of Orca
                # allows the blind user to explore the text in a
                # window in a 2D fashion.  That is, Orca treats all
                # the text from all objects in a window (e.g.,
                # buttons, labels, etc.) as a sequence of words in a
                # sequence of lines.  The flat review feature allows
                # the user to explore this text by the {previous,next}
                # {line,word,character}. This particular command will
                # cause Orca to "phonetically spell" the current line,
                # saying "Alpha" for "a", "Bravo" for "b" and so on.
                #
                _("Phonetically spells the current flat review line."))

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
                # {line,word,character}.  This command will speak the
                # current word or item.
                #
                _("Speaks the current flat review item or word."))

        self.inputEventHandlers["reviewSpellCurrentItemHandler"] = \
            input_event.InputEventHandler(
                Script.reviewSpellCurrentItem,
                # Translators: the 'flat review' feature of Orca
                # allows the blind user to explore the text in a
                # window in a 2D fashion.  That is, Orca treats all
                # the text from all objects in a window (e.g.,
                # buttons, labels, etc.) as a sequence of words in a
                # sequence of lines.  The flat review feature allows
                # the user to explore this text by the {previous,next}
                # {line,word,character}.  This command will spell out
                # the current word or item letter by letter.
                #
                _("Spells the current flat review item or word."))

        self.inputEventHandlers["reviewPhoneticCurrentItemHandler"] = \
            input_event.InputEventHandler(
                Script.reviewPhoneticCurrentItem,
                # Translators: the 'flat review' feature of Orca
                # allows the blind user to explore the text in a
                # window in a 2D fashion.  That is, Orca treats all
                # the text from all objects in a window (e.g.,
                # buttons, labels, etc.) as a sequence of words in a
                # sequence of lines.  The flat review feature allows
                # the user to explore this text by the {previous,next}
                # {line,word,character}.  This command will spell out
                # the current word or item phonetically, saying "Alpha"
                # for "a", "Bravo" for "b" and so on.
                #
                _("Phonetically spells the current flat review item or word."))

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

        self.inputEventHandlers["reviewSpellCurrentCharacterHandler"] = \
            input_event.InputEventHandler(
                Script.reviewSpellCurrentCharacter,
                # Translators: the 'flat review' feature of Orca
                # allows the blind user to explore the text in a
                # window in a 2D fashion.  That is, Orca treats all
                # the text from all objects in a window (e.g.,
                # buttons, labels, etc.) as a sequence of words in a
                # sequence of lines.  The flat review feature allows
                # the user to explore this text by the {previous,next}
                # {line,word,character}.  Previous will go backwards
                # in the window until you reach the top (i.e., it will
                # wrap across lines if necessary).  This command will
                # cause Orca to speak a phonetic representation of the
                # character currently being reviewed, saying "Alpha"
                # for "a", "Bravo" for "b" and so on.
                #
                _("Phonetically speaks the current flat review character."))

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
                # Translators: this is a debug message that Orca users
                # will not normally see. It describes a debug routine
                # that outputs useful information on the current script
                #  via speech and braille. This information will be
                # helpful to script writers.
                #
                _("Reports information on current script."))

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

        self.inputEventHandlers["contractedBrailleHandler"] = \
            input_event.InputEventHandler(
                Script.setContractedBraille,
                # Translators: braille can be displayed in many ways.
                # Contracted braille provides a more efficient means
                # to represent text, especially long documents.  The
                # feature used here is an option to toggle between
                # contracted and uncontracted.
                #
                _("Turns contracted braille on and off."))

        self.inputEventHandlers["processRoutingKeyHandler"] = \
            input_event.InputEventHandler(
                Script.processRoutingKey,
                # Translators: hardware braille displays often have
                # buttons near each braille cell.  These are called
                # cursor routing keys and are a way for a user to
                # tell the machine they are interested in a particular
                # character on the display.
                #
                _("Processes a cursor routing key."))

        self.inputEventHandlers["processBrailleCutBeginHandler"] = \
            input_event.InputEventHandler(
                Script.processBrailleCutBegin,
                # Translators: this is used to indicate the start point
                # of a text selection.
                #
                _("Marks the beginning of a text selection."))

        self.inputEventHandlers["processBrailleCutLineHandler"] = \
            input_event.InputEventHandler(
                Script.processBrailleCutLine,
                # Translators: this is used to indicate the end point
                # of a text selection.
                #
                _("Marks the end of a text selection."))

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
                orca.showAppPreferencesGUI,
                # Translators: the application preferences configuration
                # dialog is the dialog that allows users to set their
                # preferences for a specific application within Orca.
                #
                _("Displays the application preferences configuration dialog."))

        self.inputEventHandlers["toggleSilenceSpeechHandler"] = \
            input_event.InputEventHandler(
                orca.toggleSilenceSpeech,
                # Translators: Orca allows the user to turn speech synthesis
                # on or off.  We call it 'silencing'.
                #
                _("Toggles the silencing of speech."))

        self.inputEventHandlers["listAppsHandler"] = \
            input_event.InputEventHandler(
                Script.printAppsHandler,
                # Translators: this is a debug message that Orca users
                # will not normally see. It describes a debug routine
                # that prints a list of all known applications currently
                # running on the desktop, to stdout.
                #
                _("Prints a debug listing of all known applications to the " \
                "console where Orca is running."))

        self.inputEventHandlers["cycleDebugLevelHandler"] = \
            input_event.InputEventHandler(
                orca.cycleDebugLevel,
                # Translators: this is a debug message that Orca users
                # will not normally see. It describes a debug routine
                # that allows the user to adjust the level of debug
                # information that Orca generates at run time.
                #
                _("Cycles the debug level at run time."))

        self.inputEventHandlers["printAncestryHandler"] = \
            input_event.InputEventHandler(
                Script.printAncestryHandler,
                # Translators: this is a debug message that Orca users
                # will not normally see. It describes a debug routine
                # that will take the component in the currently running
                # application that has focus, and print debug information
                # to the console giving its component ancestry (i.e. all
                # the components that are its descendants in the component
                # tree).
                #
                _("Prints debug information about the ancestry of the object " \
                "with focus."))

        self.inputEventHandlers["printHierarchyHandler"] = \
            input_event.InputEventHandler(
                Script.printHierarchyHandler,
                # Translators: this is a debug message that Orca users
                # will not normally see. It describes a debug routine
                # that will take the currently running application, and
                # print debug information to the console giving its
                # component hierarchy (i.e. all the components and all
                # their descendants in the component tree).
                #
                _("Prints debug information about the application with focus."))

        self.inputEventHandlers["printMemoryUsageHandler"] = \
            input_event.InputEventHandler(
                Script.printMemoryUsageHandler,
                # Translators: this is a debug message that Orca users
                # will not normally see. It describes a debug routine
                # that will print Orca memory usage information.
                #
                _("Prints memory usage information."))

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

        self.inputEventHandlers["toggleColorEnhancementsHandler"] = \
            input_event.InputEventHandler(
                mag.toggleColorEnhancements,
                # Translators: "color enhancements" are changes users can
                # make to the appearance of the screen to make things easier
                # to see, such as inverting the colors or applying a tint.
                # This command toggles these enhancements on/off.
                #
                _("Toggles color enhancements."))

        self.inputEventHandlers["toggleMouseEnhancementsHandler"] = \
            input_event.InputEventHandler(
                mag.toggleMouseEnhancements,
                # Translators: "mouse enhancements" are changes users can
                # make to the appearance of the mouse pointer to make it
                # easier to see, such as increasing its size, changing its
                # color, and surrounding it with crosshairs.  This command
                # toggles these enhancements on/off.
                #
                _("Toggles mouse enhancements."))

        self.inputEventHandlers["increaseMagnificationHandler"] = \
            input_event.InputEventHandler(
                mag.increaseMagnification,
                # Translators: this command increases the magnification
                # level.
                #
                _("Increases the magnification level."))

        self.inputEventHandlers["decreaseMagnificationHandler"] = \
            input_event.InputEventHandler(
                mag.decreaseMagnification,
                # Translators: this command decreases the magnification
                # level.
                #
                _("Decreases the magnification level."))

        self.inputEventHandlers["toggleMagnifierHandler"] = \
            input_event.InputEventHandler(
                mag.toggleMagnifier,
                # Translators: Orca allows the user to turn the magnifier
                # on or off. This command not only toggles magnification,
                # but also all of the color and pointer customizations
                # made through the magnifier.
                #
                _("Toggles the magnifier."))

        self.inputEventHandlers["cycleZoomerTypeHandler"] = \
            input_event.InputEventHandler(
                mag.cycleZoomerType,
                # Translators: the user can choose between several different
                # types of magnification, including full screen and split
                # screen.  The "position" here refers to location of the
                # magnifier.
                #
                _("Cycles to the next magnifier position."))

        self.inputEventHandlers["toggleMouseReviewHandler"] = \
            input_event.InputEventHandler(
                mouse_review.toggle,
                # Translators: Orca allows the item under the pointer to
                # be spoken. This toggles the feature.
                #
                _("Toggle mouse review mode."))

        self.inputEventHandlers["bypassNextCommandHandler"] = \
            input_event.InputEventHandler(
                Script.bypassNextCommand,
                # Translators: Orca normally intercepts all keyboard
                # commands and only passes them along to the current
                # application when they are not Orca commands.  This
                # command causes the next command issued to be passed
                # along to the current application, bypassing Orca's
                # interception of it.
                #
                _("Passes the next command on to the current application."))

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
        listeners["object:active-descendant-changed"]       = \
            self.onActiveDescendantChanged
        listeners["object:link-selected"]                   = \
            self.onLinkSelected
        listeners["object:state-changed:active"]            = \
            self.onStateChanged
        listeners["object:state-changed:focused"]           = \
            self.onStateChanged
        listeners["object:state-changed:showing"]           = \
            self.onStateChanged
        listeners["object:state-changed:checked"]           = \
            self.onStateChanged
        listeners["object:state-changed:pressed"]           = \
            self.onStateChanged
        listeners["object:state-changed:indeterminate"]     = \
            self.onStateChanged
        listeners["object:state-changed:expanded"]          = \
            self.onStateChanged
        listeners["object:state-changed:selected"]          = \
            self.onStateChanged
        listeners["object:text-attributes-changed"]         = \
            self.onTextAttributesChanged
        listeners["object:text-selection-changed"]          = \
            self.onTextSelectionChanged
        listeners["object:selection-changed"]               = \
            self.onSelectionChanged
        listeners["object:property-change:accessible-value"] = \
            self.onValueChanged
        listeners["object:value-changed"]                   = \
            self.onValueChanged
        listeners["window:activate"]                        = \
            self.onWindowActivated
        listeners["window:deactivate"]                      = \
            self.onWindowDeactivated
        listeners["window:create"]                          = \
            self.noOp

        return listeners

    def __getDesktopBindings(self):
        """Returns an instance of keybindings.KeyBindings that use the
        numeric keypad for focus tracking and flat review.
        """

        keyBindings = keybindings.KeyBindings()

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Divide",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["routePointerToItemHandler"]))

        # We want the user to be able to combine modifiers with the
        # mouse click (e.g. to Shift+Click and select), therefore we
        # do not "care" about the modifiers -- unless it's the Orca
        # modifier.
        #
        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Divide",
                settings.ORCA_MODIFIER_MASK,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["leftClickReviewItemHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Multiply",
                settings.ORCA_MODIFIER_MASK,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["rightClickReviewItemHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Subtract",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["toggleFlatReviewModeHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Add",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["sayAllHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Enter",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["whereAmIBasicHandler"],
                1))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Enter",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["whereAmIDetailedHandler"],
                2))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Enter",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["getTitleHandler"],
                1))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Enter",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["getStatusBarHandler"],
                2))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Delete",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["findHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Delete",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["findNextHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Delete",
                settings.defaultModifierMask,
                settings.ORCA_SHIFT_MODIFIER_MASK,
                self.inputEventHandlers["findPreviousHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_7",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["reviewPreviousLineHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Home",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["reviewPreviousLineHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_7",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["reviewHomeHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Home",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["reviewHomeHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_8",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["reviewCurrentLineHandler"],
                1))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_8",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["reviewSpellCurrentLineHandler"],
                2))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_8",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["reviewPhoneticCurrentLineHandler"],
                3))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Up",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["reviewCurrentLineHandler"],
                1))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Up",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["reviewSpellCurrentLineHandler"],
                2))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Up",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["reviewPhoneticCurrentLineHandler"],
                3))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_9",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["reviewNextLineHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Page_Up",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["reviewNextLineHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_9",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["reviewEndHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Page_Up",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["reviewEndHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_4",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["reviewPreviousItemHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Left",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["reviewPreviousItemHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_4",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["reviewAboveHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Left",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["reviewAboveHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_5",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["reviewCurrentItemHandler"],
                1))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_5",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["reviewSpellCurrentItemHandler"],
                2))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_5",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["reviewPhoneticCurrentItemHandler"],
                3))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Begin",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["reviewCurrentItemHandler"],
                1))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Begin",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["reviewSpellCurrentItemHandler"],
                2))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Begin",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["reviewPhoneticCurrentItemHandler"],
                3))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_5",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["reviewCurrentAccessibleHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Begin",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["reviewCurrentAccessibleHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_6",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["reviewNextItemHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Right",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["reviewNextItemHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_6",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["reviewBelowHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Right",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["reviewBelowHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_1",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["reviewPreviousCharacterHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_End",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["reviewPreviousCharacterHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_1",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["reviewEndOfLineHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_End",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["reviewEndOfLineHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_2",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["reviewCurrentCharacterHandler"],
                1))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_2",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["reviewSpellCurrentCharacterHandler"],
                2))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Down",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["reviewCurrentCharacterHandler"],
                1))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Down",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["reviewSpellCurrentCharacterHandler"],
                2))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_3",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["reviewNextCharacterHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "KP_Page_Down",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["reviewNextCharacterHandler"]))

        return keyBindings

    def __getLaptopBindings(self):
        """Returns an instance of keybindings.KeyBindings that use the
        the main keyboard keys for focus tracking and flat review.
        """

        keyBindings = keybindings.KeyBindings()

        keyBindings.add(
            keybindings.KeyBinding(
                "9",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["routePointerToItemHandler"]))

        # We want the user to be able to combine modifiers with the
        # mouse click (e.g. to Shift+Click and select), therefore we
        # do not "care" about the modifiers (other than the Orca
        # modifier).
        #
        keyBindings.add(
            keybindings.KeyBinding(
                "7",
                settings.ORCA_MODIFIER_MASK,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["leftClickReviewItemHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "8",
                settings.ORCA_MODIFIER_MASK,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["rightClickReviewItemHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "p",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["toggleFlatReviewModeHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "semicolon",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["sayAllHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "Return",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["whereAmIBasicHandler"],
                1))

        keyBindings.add(
            keybindings.KeyBinding(
                "Return",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["whereAmIDetailedHandler"],
                2))

        keyBindings.add(
            keybindings.KeyBinding(
                "slash",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["getTitleHandler"],
                1))

        keyBindings.add(
            keybindings.KeyBinding(
                "slash",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["getStatusBarHandler"],
                2))

        keyBindings.add(
            keybindings.KeyBinding(
                "bracketleft",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["findHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "bracketright",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["findNextHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "bracketright",
                settings.defaultModifierMask,
                settings.ORCA_CTRL_MODIFIER_MASK,
                self.inputEventHandlers["findPreviousHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "u",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["reviewPreviousLineHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "u",
                settings.defaultModifierMask,
                settings.ORCA_CTRL_MODIFIER_MASK,
                self.inputEventHandlers["reviewHomeHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "i",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["reviewCurrentLineHandler"],
                1))

        keyBindings.add(
            keybindings.KeyBinding(
                "i",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["reviewSpellCurrentLineHandler"],
                2))

        keyBindings.add(
            keybindings.KeyBinding(
                "i",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["reviewPhoneticCurrentLineHandler"],
                3))

        keyBindings.add(
            keybindings.KeyBinding(
                "o",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["reviewNextLineHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "o",
                settings.defaultModifierMask,
                settings.ORCA_CTRL_MODIFIER_MASK,
                self.inputEventHandlers["reviewEndHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "j",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["reviewPreviousItemHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "j",
                settings.defaultModifierMask,
                settings.ORCA_CTRL_MODIFIER_MASK,
                self.inputEventHandlers["reviewAboveHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "k",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["reviewCurrentItemHandler"],
                1))

        keyBindings.add(
            keybindings.KeyBinding(
                "k",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["reviewSpellCurrentItemHandler"],
                2))

        keyBindings.add(
            keybindings.KeyBinding(
                "k",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["reviewPhoneticCurrentItemHandler"],
                3))

        keyBindings.add(
            keybindings.KeyBinding(
                "k",
                settings.defaultModifierMask,
                settings.ORCA_CTRL_MODIFIER_MASK,
                self.inputEventHandlers["reviewCurrentAccessibleHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "l",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["reviewNextItemHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "l",
                settings.defaultModifierMask,
                settings.ORCA_CTRL_MODIFIER_MASK,
                self.inputEventHandlers["reviewBelowHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "m",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["reviewPreviousCharacterHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "m",
                settings.defaultModifierMask,
                settings.ORCA_CTRL_MODIFIER_MASK,
                self.inputEventHandlers["reviewEndOfLineHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "comma",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["reviewCurrentCharacterHandler"],
                1))

        keyBindings.add(
            keybindings.KeyBinding(
                "comma",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["reviewSpellCurrentCharacterHandler"],
                2))

        keyBindings.add(
            keybindings.KeyBinding(
                "period",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["reviewNextCharacterHandler"]))

        return keyBindings

    def getKeyBindings(self):
        """Defines the key bindings for this script.

        Returns an instance of keybindings.KeyBindings.
        """

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
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["showZonesHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "F11",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["toggleTableCellReadModeHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "SunF36",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["toggleTableCellReadModeHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "f",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["readCharAttributesHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "h",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["enterLearnModeHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "q",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["shutdownHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "space",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["preferencesSettingsHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "space",
                settings.defaultModifierMask,
                settings.ORCA_CTRL_MODIFIER_MASK,
                self.inputEventHandlers["appPreferencesSettingsHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "s",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["toggleSilenceSpeechHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "End",
                settings.defaultModifierMask,
                settings.ORCA_CTRL_ALT_MODIFIER_MASK,
                self.inputEventHandlers["listAppsHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "Home",
                settings.defaultModifierMask,
                settings.ORCA_CTRL_ALT_MODIFIER_MASK,
                self.inputEventHandlers["reportScriptInfoHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "Page_Up",
                settings.defaultModifierMask,
                settings.ORCA_CTRL_ALT_MODIFIER_MASK,
                self.inputEventHandlers["printAncestryHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "Page_Down",
                settings.defaultModifierMask,
                settings.ORCA_CTRL_ALT_MODIFIER_MASK,
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
                settings.defaultModifierMask,
                settings.ORCA_ALT_MODIFIER_MASK,
                self.inputEventHandlers["saveBookmarks"]))
        # key binding to move to the previous bookmark
        keyBindings.add(
            keybindings.KeyBinding(
                "b",
                settings.defaultModifierMask,
                settings.ORCA_SHIFT_MODIFIER_MASK,
                self.inputEventHandlers["goToPrevBookmark"]))
        # key binding to move to the next bookmark
        keyBindings.add(
            keybindings.KeyBinding(
                "b",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["goToNextBookmark"]))

        # key bindings for '1' through '6' for relevant commands
        for key in xrange(1, 7):
            # 'Add bookmark' key bindings
            keyBindings.add(
                keybindings.KeyBinding(
                    str(key),
                    settings.defaultModifierMask,
                    settings.ORCA_ALT_MODIFIER_MASK,
                    self.inputEventHandlers["addBookmark"]))

            # 'Go to bookmark' key bindings
            keyBindings.add(
                keybindings.KeyBinding(
                    str(key),
                    settings.defaultModifierMask,
                    settings.ORCA_MODIFIER_MASK,
                    self.inputEventHandlers["goToBookmark"]))

            # key binding for WhereAmI information with respect to root acc
            keyBindings.add(
                keybindings.KeyBinding(
                    str(key),
                    settings.defaultModifierMask,
                    settings.SHIFT_ALT_MODIFIER_MASK,
                    self.inputEventHandlers["bookmarkCurrentWhereAmI"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "BackSpace",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["bypassNextCommandHandler"]))

        #####################################################################
        #                                                                   #
        #  Unbound handlers                                                 #
        #                                                                   #
        #####################################################################

        keyBindings.add(
            keybindings.KeyBinding(
                "",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["cycleDebugLevelHandler"]))

        if settings.debugMemoryUsage:
            keyBindings.add(
                keybindings.KeyBinding(
                    "",
                    settings.defaultModifierMask,
                    settings.NO_MODIFIER_MASK,
                    self.inputEventHandlers["printMemoryUsageHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["decreaseSpeechRateHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["increaseSpeechRateHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["decreaseSpeechPitchHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["increaseSpeechPitchHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["toggleColorEnhancementsHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["toggleMouseEnhancementsHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["increaseMagnificationHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["decreaseMagnificationHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["toggleMagnifierHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["cycleZoomerTypeHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["panBrailleLeftHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["panBrailleRightHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "",
                settings.defaultModifierMask,
                settings.NO_MODIFIER_MASK,
                self.inputEventHandlers["toggleMouseReviewHandler"]))

        try:
            keyBindings = settings.overrideKeyBindings(self, keyBindings)
        except:
            debug.println(debug.LEVEL_WARNING,
                          "WARNING: problem overriding keybindings:")
            debug.printException(debug.LEVEL_WARNING)

        return keyBindings

    def getBrailleBindings(self):
        """Defines the braille bindings for this script.

        Returns a dictionary where the keys are BrlTTY commands and the
        values are InputEventHandler instances.
        """
        brailleBindings = script.Script.getBrailleBindings(self)
        try:
            brailleBindings[braille.brlapi.KEY_CMD_FWINLT]   = \
                self.inputEventHandlers["panBrailleLeftHandler"]
            brailleBindings[braille.brlapi.KEY_CMD_FWINRT]   = \
                self.inputEventHandlers["panBrailleRightHandler"]
            brailleBindings[braille.brlapi.KEY_CMD_LNUP]     = \
                self.inputEventHandlers["reviewAboveHandler"]
            brailleBindings[braille.brlapi.KEY_CMD_LNDN]     = \
                self.inputEventHandlers["reviewBelowHandler"]
            brailleBindings[braille.brlapi.KEY_CMD_FREEZE]   = \
                self.inputEventHandlers["toggleFlatReviewModeHandler"]
            brailleBindings[braille.brlapi.KEY_CMD_TOP_LEFT] = \
                self.inputEventHandlers["reviewHomeHandler"]
            brailleBindings[braille.brlapi.KEY_CMD_BOT_LEFT] = \
                self.inputEventHandlers["reviewBottomLeftHandler"]
            brailleBindings[braille.brlapi.KEY_CMD_HOME]     = \
                self.inputEventHandlers["goBrailleHomeHandler"]
            brailleBindings[braille.brlapi.KEY_CMD_SIXDOTS]   = \
                self.inputEventHandlers["contractedBrailleHandler"]
            brailleBindings[braille.brlapi.KEY_CMD_ROUTE]   = \
                self.inputEventHandlers["processRoutingKeyHandler"]
            brailleBindings[braille.brlapi.KEY_CMD_CUTBEGIN] = \
                self.inputEventHandlers["processBrailleCutBeginHandler"]
            brailleBindings[braille.brlapi.KEY_CMD_CUTLINE] = \
                self.inputEventHandlers["processBrailleCutLineHandler"]
        except:
            debug.println(debug.LEVEL_CONFIGURATION,
                          "WARNING: braille bindings unavailable:")
            debug.printException(debug.LEVEL_CONFIGURATION)
        return brailleBindings

    def processKeyboardEvent(self, keyboardEvent):
        """Processes the given keyboard event. It uses the super
        class equivalent to do most of the work. The only thing done here
        is to detect when the user is trying to get out of learn mode.

        Arguments:
        - keyboardEvent: an instance of input_event.KeyboardEvent
        """

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
            return
        elif progressType == speechserver.SayAllContext.INTERRUPTED:
            #print "INTERRUPTED", context.utterance, context.currentOffset
            text.setCaretOffset(context.currentOffset)
        elif progressType == speechserver.SayAllContext.COMPLETED:
            #print "COMPLETED", context.utterance, context.currentOffset
            orca.setLocusOfFocus(
                None, context.obj, notifyPresentationManager=False)
            text.setCaretOffset(context.currentOffset)

        # If there is a selection, clear it. See bug #489504 for more details.
        #
        if text.getNSelections():
            text.setSelection(0, context.currentOffset, context.currentOffset)

    def sayAll(self, inputEvent):
        clickCount = self.getClickCount()
        doubleClick = clickCount == 2
        self.lastSayAllEvent = inputEvent

        if doubleClick:
            # Try to "say all" for the current dialog/window by flat
            # reviewing everything. See bug #354462 for more details.
            #
            context = self.getFlatReviewContext()

            utterances = []
            context.goBegin()
            while True:
                [wordString, x, y, width, height] = \
                         context.getCurrent(flat_review.Context.ZONE)

                utterances.append(wordString)

                moved = context.goNext(flat_review.Context.ZONE,
                                       flat_review.Context.WRAP_LINE)

                if not moved:
                    break

            speech.speak(utterances)

        elif self.isTextArea(orca_state.locusOfFocus):
            try:
                orca_state.locusOfFocus.queryText()
            except NotImplementedError:
                utterances = self.speechGenerator.generateSpeech(
                    orca_state.locusOfFocus)
                utterances.extend(self.tutorialGenerator.getTutorial(
                           orca_state.locusOfFocus, False))
                speech.speak(utterances)
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
            obj.getRole() in (pyatspi.ROLE_TEXT,
                              pyatspi.ROLE_PARAGRAPH,
                              pyatspi.ROLE_TERMINAL)

    def isReadOnlyTextArea(self, obj):
        """Returns True if obj is a text entry area that is read only."""
        state = obj.getState()
        readOnly = self.isTextArea(obj) \
                   and state.contains(pyatspi.STATE_FOCUSABLE) \
                   and not state.contains(pyatspi.STATE_EDITABLE)
        debug.println(debug.LEVEL_ALL,
                      "default.py:isReadOnlyTextArea=%s for %s" \
                      % (readOnly, debug.getAccessibleDetails(obj)))
        return readOnly

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

        phrase = self.getText(obj, startOffset, endOffset)

        if len(phrase) and phrase != "\n":
            if phrase.decode("UTF-8").isupper():
                voice = self.voices[settings.UPPERCASE_VOICE]
            else:
                voice = self.voices[settings.DEFAULT_VOICE]

            phrase = self.adjustForRepeats(phrase)
            speech.speak(phrase, voice)
        else:
            # Speak blank line if appropriate.
            #
            self.sayCharacter(obj)

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

        if len(line) and line != "\n":
            if line.decode("UTF-8").isupper():
                voice = self.voices[settings.UPPERCASE_VOICE]
            else:
                voice = self.voices[settings.DEFAULT_VOICE]

            if settings.enableSpeechIndentation:
                self.speakTextIndentation(obj, line)
            line = self.adjustForLinks(obj, line, startOffset)
            line = self.adjustForRepeats(line)
            speech.speak(line, voice)
        else:
            # Speak blank line if appropriate.
            #
            self.sayCharacter(obj)

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
                speech.speakCharacter("\n", voice)

        if lastKey == "Left" and len(word) > 0:
            lastChar = word[len(word) - 1]
            if lastChar == "\n" and lastWord != word:
                voice = self.voices[settings.DEFAULT_VOICE]
                speech.speakCharacter("\n", voice)

        if self.getLinkIndex(obj, offset) >= 0:
            voice = self.voices[settings.HYPERLINK_VOICE]
        elif word.decode("UTF-8").isupper():
            voice = self.voices[settings.UPPERCASE_VOICE]
        else:
            voice = self.voices[settings.DEFAULT_VOICE]

        self.speakMisspelledIndicator(obj, startOffset)

        word = self.adjustForRepeats(word)
        orca_state.lastWord = word
        speech.speak(word, voice)

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
        utterance = ""
        offset = 0
        while True:
            while (offset < len(line)) and line[offset] == ' ':
                spaceCount += 1
                offset += 1
            if spaceCount:
                # Translators: this is the number of space characters on a line
                # of text.
                #
                utterance += ngettext("%d space",
                                      "%d spaces",
                                      spaceCount) % spaceCount + " "

            while (offset < len(line)) and line[offset] == '\t':
                tabCount += 1
                offset += 1
            if tabCount:
                # Translators: this is the number of tab characters on a line
                # of text.
                #
                utterance += ngettext("%d tab",
                                      "%d tabs",
                                      tabCount) % tabCount + " "

            if not (spaceCount  or tabCount):
                break
            spaceCount  = tabCount = 0

        if len(utterance):
            speech.speak(utterance)

    def echoPreviousSentence(self, obj):
        """Speaks the sentence prior to the caret, as long as there is
        a sentence prior to the caret and there is no intervening sentence
        delimiter between the caret and the end of the sentence.

        The entry condition for this method is that the character
        prior to the current caret position is a sentence delimiter,
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
        previousOffset = text.caretOffset - 2
        if (offset < 0 or previousOffset < 0):
            return

        [currentChar, startOffset, endOffset] = \
            text.getTextAtOffset(offset, pyatspi.TEXT_BOUNDARY_CHAR)
        [previousChar, startOffset, endOffset] = \
            text.getTextAtOffset(previousOffset, pyatspi.TEXT_BOUNDARY_CHAR)
        if not self.isSentenceDelimiter(currentChar, previousChar):
            return

        # OK - we seem to be cool so far.  So...starting with what
        # should be the last character in the sentence (caretOffset - 2),
        # work our way to the beginning of the sentence, stopping when
        # we hit another sentence delimiter.
        #
        sentenceEndOffset = text.caretOffset - 2
        sentenceStartOffset = sentenceEndOffset

        while sentenceStartOffset >= 0:
            [currentChar, startOffset, endOffset] = \
                text.getTextAtOffset(sentenceStartOffset,
                                     pyatspi.TEXT_BOUNDARY_CHAR)
            [previousChar, startOffset, endOffset] = \
                text.getTextAtOffset(sentenceStartOffset-1,
                                     pyatspi.TEXT_BOUNDARY_CHAR)
            if self.isSentenceDelimiter(currentChar, previousChar):
                break
            else:
                sentenceStartOffset -= 1

        # If we came across a sentence delimiter before hitting any
        # text, we really don't have a previous sentence.
        #
        # Otherwise, get the sentence.  Remember we stopped when we
        # hit a sentence delimiter, so the sentence really starts at
        # sentenceStartOffset + 1.  getText also does not include
        # the character at sentenceEndOffset, so we need to adjust
        # for that, too.
        #
        if sentenceStartOffset == sentenceEndOffset:
            return
        else:
            sentence = self.getText(obj, sentenceStartOffset + 1,
                                         sentenceEndOffset + 1)

        if self.getLinkIndex(obj, sentenceStartOffset + 1) >= 0:
            voice = self.voices[settings.HYPERLINK_VOICE]
        elif sentence.decode("UTF-8").isupper():
            voice = self.voices[settings.UPPERCASE_VOICE]
        else:
            voice = self.voices[settings.DEFAULT_VOICE]

        sentence = self.adjustForRepeats(sentence)
        speech.speak(sentence, voice)

    def echoPreviousWord(self, obj, offset=None):
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
        - offset: if not None, the offset within the text to use as the
                  end of the word.
        """

        try:
            text = obj.queryText()
        except NotImplementedError:
            return

        if not offset:
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
        wordEndOffset = offset - 1
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
        elif word.decode("UTF-8").isupper():
            voice = self.voices[settings.UPPERCASE_VOICE]
        else:
            voice = self.voices[settings.DEFAULT_VOICE]

        word = self.adjustForRepeats(word)
        speech.speak(word, voice)

    def sayCharacter(self, obj):
        """Speak the character at the caret.

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
        try:
            mods = orca_state.lastInputEvent.modifiers
            eventString = orca_state.lastInputEvent.event_string
        except:
            mods = 0
            eventString = ""

        if (mods & settings.SHIFT_MODIFIER_MASK) \
           and eventString in ["Right", "Down"]:
            offset -= 1

        character, startOffset, endOffset = \
            text.getTextAtOffset(offset, pyatspi.TEXT_BOUNDARY_CHAR)
        if not character:
            character = "\n"

        if self.getLinkIndex(obj, offset) >= 0:
            voice = self.voices[settings.HYPERLINK_VOICE]
        elif character.decode("UTF-8").isupper():
            voice = self.voices[settings.UPPERCASE_VOICE]
        else:
            voice = self.voices[settings.DEFAULT_VOICE]

        debug.println(debug.LEVEL_FINEST, \
            "sayCharacter: char=<%s>, startOffset=%d, " % \
            (character, startOffset))
        debug.println(debug.LEVEL_FINEST, \
            "caretOffset=%d, endOffset=%d, speakBlankLines=%s" % \
            (offset, endOffset, settings.speakBlankLines))

        if character == "\n":
            line = text.getTextAtOffset(max(0, offset),
                                        pyatspi.TEXT_BOUNDARY_LINE_START)
            if not line[0] or line[0] == "\n":
                # This is a blank line. Announce it if the user requested
                # that blank lines be spoken.
                if settings.speakBlankLines:
                    # Translators: "blank" is a short word to mean the
                    # user has navigated to an empty line.
                    #
                    speech.speak(_("blank"), voice, False)
                return

        self.speakMisspelledIndicator(obj, offset)
        speech.speakCharacter(character, voice)

    def isFunctionalDialog(self, obj):
        """Returns true if the window is a functioning as a dialog.
        This method should be subclassed by application scripts as needed.
        """

        return False

    def getUnfocusedAlertAndDialogCount(self, obj):
        """If the current application has one or more alert or dialog
        windows and the currently focused window is not an alert or a dialog,
        return a count of the number of alert and dialog windows, otherwise
        return a count of zero.

        Arguments:
        - obj: the Accessible object

        Returns the alert and dialog count.
        """

        alertAndDialogCount = 0
        app = obj.getApplication()
        window = self.getTopLevel(obj)
        if window and window.getRole() != pyatspi.ROLE_ALERT and \
           window.getRole() != pyatspi.ROLE_DIALOG and \
           not self.isFunctionalDialog(window):
            for child in app:
                if child.getRole() == pyatspi.ROLE_ALERT or \
                   child.getRole() == pyatspi.ROLE_DIALOG or \
                   self.isFunctionalDialog(child):
                    alertAndDialogCount += 1

        return alertAndDialogCount

    def presentToolTip(self, obj):
        """
        Speaks the tooltip for the current object of interest.
        """

        # The tooltip is generally the accessible description. If
        # the description is not set, present the text that is
        # spoken when the object receives keyboard focus.
        #
        text = ""
        if obj.description:
            speechResult = brailleResult = obj.description
        else:
            # [[[TODO: WDW to JD: I see what you mean about making the
            # _getLabelAndName method a public method.  We might consider
            # doing that when we get to the braille refactor where we
            # will probably make an uber generator class/module that the
            # speech and braille generator classes can subclass.  For
            # now, I've kind of hacked at the speech result.  The idea
            # is that the speech result might return an audio cue and
            # voice specification.  Of course, if it does that, then
            # the speechResult[0] assumption will fail. :-(]]]
            #
            speechResult = self.whereAmI.getWhereAmI(obj, True)
            brailleResult = speechResult[0]
        debug.println(debug.LEVEL_FINEST,
                      "presentToolTip: text='%s'" % speechResult)
        if speechResult:
            speech.speak(speechResult)
        if brailleResult:
            braille.displayMessage(brailleResult)

    def doWhereAmI(self, inputEvent, basicOnly):
        """Peforms the whereAmI operation.

        Arguments:
        - inputEvent:     The original inputEvent
        """

        obj = orca_state.locusOfFocus
        self.updateBraille(obj)

        return self.whereAmI.whereAmI(obj, basicOnly)

    def whereAmIBasic(self, inputEvent):
        """Speaks basic information about the current object of interest.
        """

        self.doWhereAmI(inputEvent, True)

    def whereAmIDetailed(self, inputEvent):
        """Speaks detailed/custom information about the current object of
        interest.
        """

        self.doWhereAmI(inputEvent, False)

    def presentTitle(self, inputEvent):
        """Speaks and brailles the title of the window with focus.
        """

        obj = orca_state.locusOfFocus
        self.updateBraille(obj)
        speech.speak(self.speechGenerator.generateTitle(obj))

    def presentStatusBar(self, inputEvent):
        """Speaks and brailles the contents of the status bar and/or default
        button of the window with focus.
        """

        obj = orca_state.locusOfFocus
        self.updateBraille(obj)

        frame, dialog = self.findFrameAndDialog(obj)
        if frame:
            # In windows with lots of objects (Thunderbird, Firefox, etc.)
            # If we wait until we've checked for both the status bar and
            # a default button, there may be a noticable delay. Therefore,
            # speak the status bar info immediately and then go looking
            # for a default button.
            #
            speech.speak(self.speechGenerator.generateStatusBar(frame))
        window = dialog or frame
        if window:
            speech.speak(self.speechGenerator.generateDefaultButton(window))

    def findStatusBar(self, obj):
        """Returns the status bar in the window which contains obj.
        """

        # There are some objects which are not worth descending.
        #
        skipRoles = [pyatspi.ROLE_TREE,
                     pyatspi.ROLE_TREE_TABLE,
                     pyatspi.ROLE_TABLE]

        if obj.getState().contains(pyatspi.STATE_MANAGES_DESCENDANTS) \
           or obj.getRole() in skipRoles:
            return

        statusBar = None
        # The status bar is likely near the bottom of the window.
        #
        for i in range(obj.childCount - 1, -1, -1):
            if obj[i].getRole() == pyatspi.ROLE_STATUS_BAR:
                statusBar = obj[i]
            elif not obj[i] in skipRoles:
                statusBar = self.findStatusBar(obj[i])

            if statusBar:
                break

        return statusBar

    def findDefaultButton(self, obj):
        """Returns the default button in dialog, obj.
        """

        # There are some objects which are not worth descending.
        #
        skipRoles = [pyatspi.ROLE_TREE,
                     pyatspi.ROLE_TREE_TABLE,
                     pyatspi.ROLE_TABLE]

        if obj.getState().contains(pyatspi.STATE_MANAGES_DESCENDANTS) \
           or obj.getRole() in skipRoles:
            return

        defaultButton = None
        # The default button is likely near the bottom of the window.
        #
        for i in range(obj.childCount - 1, -1, -1):
            if obj[i].getRole() == pyatspi.ROLE_PUSH_BUTTON \
                and obj[i].getState().contains(pyatspi.STATE_IS_DEFAULT):
                defaultButton = obj[i]
            elif not obj[i].getRole() in skipRoles:
                defaultButton = self.findDefaultButton(obj[i])

            if defaultButton:
                break

        return defaultButton

    def findFrameAndDialog(self, obj):
        """Returns the frame and (possibly) the dialog containing
        the object.
        """

        results = [None, None]

        parent = obj.parent
        while parent and (parent.parent != parent):
            if parent.getRole() == pyatspi.ROLE_FRAME:
                results[0] = parent
            if parent.getRole() in [pyatspi.ROLE_DIALOG,
                                    pyatspi.ROLE_FILE_CHOOSER]:
                results[1] = parent
            parent = parent.parent

        return results

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
        2/ settings.progressBarVerbosity matches the current location of the
           progress bar.
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
            makeAnnouncment = False
            if settings.progressBarVerbosity == settings.PROGRESS_BAR_ALL:
                makeAnnouncement = True
            elif settings.progressBarVerbosity == settings.PROGRESS_BAR_WINDOW:
                makeAnnouncement = self.isSameObject( \
                    self.getTopLevel(obj), self.findActiveWindow())
            elif orca_state.locusOfFocus:
                makeAnnouncement = self.isSameObject( \
                    obj.getApplication(),
                    orca_state.locusOfFocus.getApplication())

            if makeAnnouncement:
                currentTime = time.time()

                # Check for defunct progress bars. Get rid of them if they
                # are all defunct. Also find out which progress bar was
                # the most recently updated.
                #
                defunctBars = 0
                mostRecentUpdate = [obj, 0]
                for key, value in self.lastProgressBarTime.items():
                    if value > mostRecentUpdate[1]:
                        mostRecentUpdate = [key, value]
                    try:
                        isDefunct = \
                            key.getState().contains(pyatspi.STATE_DEFUNCT)
                    except:
                        isDefunct = True
                    if isDefunct:
                        defunctBars += 1

                if defunctBars == len(self.lastProgressBarTime):
                    self.lastProgressBarTime = {}
                    self.lastProgressBarValue = {}

                # If this progress bar is not already known, create initial
                # values for it.
                #
                if obj not in self.lastProgressBarTime:
                    self.lastProgressBarTime[obj] = 0.0
                if obj not in self.lastProgressBarValue:
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
                        # bars, as well as the value. But only speak the
                        # index if this progress bar was not the most
                        # recently updated to prevent chattiness.
                        #
                        if len(self.lastProgressBarTime) > 1:
                            index = 0
                            for key in self.lastProgressBarTime.keys():
                                if key == obj and key != mostRecentUpdate[0]:
                                    # Translators: this is an index value
                                    # so that we can tell which progress bar
                                    # we are referring to.
                                    #
                                    label = _("Progress bar %d.") % (index + 1)
                                    utterances.append(label)
                                else:
                                    index += 1

                        utterances.extend(self.speechGenerator.generateSpeech(
                            obj, alreadyFocused=True))

                        speech.speak(utterances)

                        self.lastProgressBarTime[obj] = currentTime
                        self.lastProgressBarValue[obj] = percentValue

    def locusOfFocusChanged(self, event, oldLocusOfFocus, newLocusOfFocus):
        """Called when the visual object with focus changes.

        Arguments:
        - event: if not None, the Event that caused the change
        - oldLocusOfFocus: Accessible that is the old locus of focus
        - newLocusOfFocus: Accessible that is the new locus of focus
        """

        if newLocusOfFocus \
           and newLocusOfFocus.getState().contains(pyatspi.STATE_DEFUNCT):
            return

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
        #
        if oldParent is not None and oldParent == newParent and \
              newParent.getRole() in [pyatspi.ROLE_TABLE,
                                      pyatspi.ROLE_TREE_TABLE]:
            for key in self.pointOfReference.keys():
                if key not in ('lastRow', 'lastColumn'):
                    del self.pointOfReference[key]
        else:
            self.pointOfReference = {}

        if newLocusOfFocus:
            self.updateBraille(newLocusOfFocus)

            # Check to see if we are in the Pronunciation Dictionary in the
            # Orca Preferences dialog. If so, then we do not want to use the
            # pronunciation dictionary to replace the actual words in the
            # first column of this table.
            #
            # [[[TODO: WDW - this should be pushed into an
            # adjustForPronunciation method in a script for orca.]]]
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

            # We might be automatically speaking the unbound labels
            # in a dialog box as the result of the dialog box suddenly
            # appearing.  If so, don't interrupt this because of a
            # focus event that occurs when something like the "OK"
            # button gets focus shortly after the window appears.
            #
            shouldNotInterrupt = (event and event.type.startswith("focus:")) \
                and self.windowActivateTime \
                and ((time.time() - self.windowActivateTime) < 1.0)

            # [[[TODO: WDW - this should move to the generator.]]]
            #
            if newLocusOfFocus.getRole() == pyatspi.ROLE_LINK:
                voice = self.voices[settings.HYPERLINK_VOICE]
            else:
                voice = self.voices[settings.DEFAULT_VOICE]

            utterances = self.speechGenerator.generateSpeech(
                newLocusOfFocus,
                priorObj=oldLocusOfFocus)
            speech.speak(utterances, voice, not shouldNotInterrupt)

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
                    index = self.getCellIndex(newLocusOfFocus)
                    column = table.getColumnAtIndex(index)
                    self.pointOfReference['lastColumn'] = column
                    row = table.getRowAtIndex(index)
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

                speech.speak(utterances)

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
                    utterances = self.speechGenerator.generateSpeech(
                        target, alreadyFocused=True)
                    utterances.extend(self.tutorialGenerator.getTutorial(
                               target, True))
                    speech.speak(utterances)
                    return

        # If this object is a label, and if it has a LABEL_FOR relation
        # to the focused object, then we should speak/braille the
        # focused object, as if it had just got focus.
        #
        if obj.getRole() == pyatspi.ROLE_LABEL \
           and obj.getState().contains(pyatspi.STATE_SHOWING):
            for relation in relations:
                if relation.getRelationType() \
                       == pyatspi.RELATION_LABEL_FOR:
                    target = relation.getTarget(0)
                    if target == orca_state.locusOfFocus:
                        self.updateBraille(target)
                        utterances = self.speechGenerator.generateSpeech(
                            target, alreadyFocused=True)
                        utterances.extend(self.tutorialGenerator.getTutorial(
                                          target, True))
                        speech.speak(utterances)
                        return

        if not self.isSameObject(obj, orca_state.locusOfFocus):
            return

        # Radio buttons normally change their state when you arrow to them,
        # so we handle the announcement of their state changes in the focus
        # handling code.  However, we do need to handle radio buttons where
        # the user needs to press the space key so select them.  We see this
        # in the disk selection area of the OpenSolaris gui-install application
        # for example.
        #
        if obj.getRole() == pyatspi.ROLE_RADIO_BUTTON:
            if orca_state.lastNonModifierKeyEvent \
               and orca_state.lastNonModifierKeyEvent.event_string \
                   in [" ", "space"]:
                pass
            else:
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
        utterances = self.speechGenerator.generateSpeech(
                         obj, alreadyFocused=True)
        utterances.extend(self.tutorialGenerator.getTutorial(obj, True))
        speech.speak(utterances)

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

        result = self.brailleGenerator.generateBraille(obj)
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
                # We might have tucked away some information for this
                # thing in the onActiveDescendantChanged method.
                #
                if "activeDescendantInfo" in self.pointOfReference:
                    [parent, index] = \
                        self.pointOfReference['activeDescendantInfo']
                    newFocus = parent[index]

                else:
                    # Well...we'll first see if there is a selection.  If there
                    # is, we'll use it.
                    #
                    try:
                        selection = event.source.querySelection()
                    except NotImplementedError:
                        selection = None
                    if selection and selection.nSelectedChildren > 0:
                        newFocus = selection.getSelectedChild(0)

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

    def _speakContiguousSelection(self, obj, relationship):
        """Check if the contiguous object has a selection. If it does, then
        speak it. If the user pressed Shift-Down, then look for an object
        with a RELATION_FLOWS_FROM relationship. If they pressed Shift-Up,
        then look for a RELATION_FLOWS_TO relationship.

        Arguments:
        - the current text object
        - the flows relationship (RELATION_FLOWS_FROM or RELATION_FLOWS_TO).

        Returns an indication of whether anything was spoken.
        """

        lastPos = self.pointOfReference.get("lastCursorPosition")

        # Reasons to NOT speak contiguous selections:
        #
        # 1. The new cursor position is in the same object as the old
        #    cursor position. (The change in selection is all within
        #    the current object.)
        # 2. If we are selecting up line by line from the beginning of
        #    the line and have just crossed into a new object, the change
        #    in selection is the previous line (which has just become
        #    selected).  Nothing has changed on the line we came from.
        #
        if self.isSameObject(lastPos[0], obj) \
           or relationship == pyatspi.RELATION_FLOWS_TO and lastPos[1] == 0:
            return False

        selSpoken = False
        current = obj
        for relation in current.getRelationSet():
            if relation.getRelationType() == relationship:
                obj = relation.getTarget(0)
                objText = obj.queryText()

                # When selecting down across paragraph boundaries, what
                # we've (un)selected on (what is now) the previous line
                # is from wherever the cursor used to be to the end of
                # the line.
                #
                if relationship == pyatspi.RELATION_FLOWS_FROM:
                    start, end = lastPos[1], objText.characterCount

                # When selecting up across paragraph boundaries, what
                # we've (un)selected on (what is now) the next line is
                # from the beginning of the line to wherever the cursor
                # used to be.
                #
                else:
                    start, end = 0, lastPos[1]

                if objText.getNSelections() > 0:
                    [textContents, startOffset, endOffset] = \
                        self.getSelectedText(obj)

                    # Now that we have the full selection, adjust based
                    # on the relation type. (see above comment)
                    #
                    startOffset = start or startOffset
                    endOffset = end or endOffset
                    self.sayPhrase(obj, startOffset, endOffset)
                    selSpoken = True
                else:
                    # We don't have selections in this object. But we're
                    # here, which means that something is selected in a
                    # neighboring object and the text in this object must
                    # have just become unselected and needs to be spoken.
                    #
                    self.sayPhrase(obj, start, end)
                    selSpoken = True

        return selSpoken

    def _presentTextAtNewCaretPosition(self, event, otherObj=None):
        """Updates braille, magnification, and outputs speech for the
        event.source or the otherObj."""

        obj = otherObj or event.source
        text = obj.queryText()

        if obj:
            mag.magnifyAccessible(event, obj)

        # Update the Braille display - if we can just reposition
        # the cursor, then go for it.
        #
        brailleNeedsRepainting = True
        line = braille.getShowingLine()
        for region in line.regions:
            if isinstance(region, braille.Text) \
               and (region.accessible == obj):
                if region.repositionCursor():
                    braille.refresh(True)
                    brailleNeedsRepainting = False
                break

        if brailleNeedsRepainting:
            self.updateBraille(obj)

        if not orca_state.lastInputEvent:
            return

        if isinstance(orca_state.lastInputEvent, input_event.MouseButtonEvent):
            if not orca_state.lastInputEvent.pressed:
                self.sayLine(obj)
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
        isControlKey = mods & settings.CTRL_MODIFIER_MASK
        isShiftKey = mods & settings.SHIFT_MODIFIER_MASK
        lastPos = self.pointOfReference.get("lastCursorPosition")
        hasLastPos = (lastPos != None)

        if (keyString == "Up") or (keyString == "Down"):
            # If the user has typed Shift-Up or Shift-Down, then we want
            # to speak the text that has just been selected or unselected,
            # otherwise we speak the new line where the text cursor is
            # currently positioned.
            #
            if hasLastPos and isShiftKey and not isControlKey:
                if keyString == "Up":
                    # If we have just crossed a paragraph boundary with
                    # Shift+Up, what we've selected in this object starts
                    # with the current offset and goes to the end of the
                    # paragraph.
                    #
                    if not self.isSameObject(lastPos[0], obj):
                        [startOffset, endOffset] = \
                            text.caretOffset, text.characterCount
                    else:
                        [startOffset, endOffset] \
                                             = self.getOffsetsForPhrase(obj)
                    self.sayPhrase(obj, startOffset, endOffset)
                    selSpoken = self._speakContiguousSelection(obj,
                                                   pyatspi.RELATION_FLOWS_TO)
                else:
                    selSpoken = self._speakContiguousSelection(obj,
                                                 pyatspi.RELATION_FLOWS_FROM)

                    # If we have just crossed a paragraph boundary with
                    # Shift+Down, what we've selected in this object starts
                    # with the beginning of the paragraph and goes to the
                    # current offset.
                    #
                    if not self.isSameObject(lastPos[0], obj):
                        [startOffset, endOffset] = 0, text.caretOffset
                    else:
                        [startOffset, endOffset] \
                                             = self.getOffsetsForPhrase(obj)

                    if startOffset != endOffset:
                        self.sayPhrase(obj, startOffset, endOffset)

            else:
                [startOffset, endOffset] = self.getOffsetsForLine(obj)
                self.sayLine(obj)

        elif (keyString == "Left") or (keyString == "Right"):
            # If the user has typed Control-Shift-Up or Control-Shift-Dowm,
            # then we want to speak the text that has just been selected
            # or unselected, otherwise if the user has typed Control-Left
            # or Control-Right, we speak the current word otherwise we speak
            # the character at the text cursor position.
            #
            inNewObj = hasLastPos and not self.isSameObject(lastPos[0], obj)

            if hasLastPos and not inNewObj and isShiftKey and isControlKey:
                [startOffset, endOffset] = self.getOffsetsForPhrase(obj)
                self.sayPhrase(obj, startOffset, endOffset)
            elif isControlKey and not isShiftKey:
                [startOffset, endOffset] = self.getOffsetsForWord(obj)
                if startOffset == endOffset:
                    self.sayCharacter(obj)
                else:
                    self.sayWord(obj)
            else:
                [startOffset, endOffset] = self.getOffsetsForChar(obj)
                self.sayCharacter(obj)

        elif keyString == "Page_Up":
            # If the user has typed Control-Shift-Page_Up, then we want
            # to speak the text that has just been selected or unselected,
            # otherwise if the user has typed Control-Page_Up, then we
            # speak the character to the right of the current text cursor
            # position otherwise we speak the current line.
            #
            if hasLastPos and isShiftKey and isControlKey:
                [startOffset, endOffset] = self.getOffsetsForPhrase(obj)
                self.sayPhrase(obj, startOffset, endOffset)
            elif isControlKey:
                [startOffset, endOffset] = self.getOffsetsForChar(obj)
                self.sayCharacter(obj)
            else:
                [startOffset, endOffset] = self.getOffsetsForLine(obj)
                self.sayLine(obj)

        elif keyString == "Page_Down":
            # If the user has typed Control-Shift-Page_Down, then we want
            # to speak the text that has just been selected or unselected,
            # otherwise if the user has just typed Page_Down, then we speak
            # the current line.
            #
            if hasLastPos and isShiftKey and isControlKey:
                [startOffset, endOffset] = self.getOffsetsForPhrase(obj)
                self.sayPhrase(obj, startOffset, endOffset)
            else:
                [startOffset, endOffset] = self.getOffsetsForLine(obj)
                self.sayLine(obj)

        elif (keyString == "Home") or (keyString == "End"):
            # If the user has typed Shift-Home or Shift-End, then we want
            # to speak the text that has just been selected or unselected,
            # otherwise if the user has typed Control-Home or Control-End,
            # then we speak the current line otherwise we speak the character
            # to the right of the current text cursor position.
            #
            if hasLastPos and isShiftKey and not isControlKey:
                [startOffset, endOffset] = self.getOffsetsForPhrase(obj)
                self.sayPhrase(obj, startOffset, endOffset)
            elif isControlKey:
                [startOffset, endOffset] = self.getOffsetsForLine(obj)
                self.sayLine(obj)
            else:
                [startOffset, endOffset] = self.getOffsetsForChar(obj)
                self.sayCharacter(obj)

        else:
            startOffset = text.caretOffset
            endOffset = text.caretOffset

        self._saveLastCursorPosition(obj, text.caretOffset)
        self._saveSpokenTextRange(startOffset, endOffset)

    def onCaretMoved(self, event):
        """Called whenever the caret moves.

        Arguments:
        - event: the Event
        """

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
                         & settings.CTRL_MODIFIER_MASK
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
        elif character.decode("UTF-8").isupper():
            voice = self.voices[settings.UPPERCASE_VOICE]
        else:
            voice = self.voices[settings.DEFAULT_VOICE]

        # We won't interrupt what else might be being spoken
        # right now because it is typically something else
        # related to this event.
        #
        if len(character.decode('utf-8')) == 1:
            speech.speakCharacter(character, voice)
        else:
            speech.speak(character, voice, False)

    def willEchoCharacter(self, event):
        """Given a keyboard event containing an alphanumeric key,
        determine if the script is likely to echo it as a character.
        """

        # The check here in English is something like this: "If this
        # character echo is enabled, then character echo is likely to
        # happen if the locus of focus is a focusable editable text
        # area or terminal and neither of the Ctrl, Alt, or Orca
        # modifiers are pressed.  If that's the case, then character
        # echo will kick in for us."
        #
        return  settings.enableEchoByCharacter \
                and orca_state.locusOfFocus \
                and (self.isTextArea(orca_state.locusOfFocus)\
                     or orca_state.locusOfFocus.getRole() \
                        == pyatspi.ROLE_ENTRY) \
                and (orca_state.locusOfFocus.getRole() \
                     == pyatspi.ROLE_TERMINAL \
                     or (not self.isReadOnlyTextArea(orca_state.locusOfFocus) \
                         and (orca_state.locusOfFocus.getState().contains( \
                                  pyatspi.STATE_FOCUSABLE)))) \
                and not (event.modifiers & settings.ORCA_CTRL_MODIFIER_MASK)

    def onTextInserted(self, event):
        """Called whenever text is inserted into an object.

        Arguments:
        - event: the Event
        """

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
            # We are using getTextLineAtCaret here instead of the "text"
            # variable, because of a problem with selected text in spin
            # buttons. See bug #520395 for more details.
            #
            [spinValue, caretOffset, startOffset] = \
                self.getTextLineAtCaret(event.source)
            speech.speak(spinValue)
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
                         & settings.COMMAND_MODIFIER_MASK
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

        # We might need to echo this if it is a single character.
        #
        speakThis = speakThis \
                    or (settings.enableEchoByCharacter \
                        and text \
                        and event.source.getRole() \
                            != pyatspi.ROLE_PASSWORD_TEXT \
                        and len(text.decode("UTF-8")) == 1)

        if speakThis:
            if text.decode("UTF-8").isupper():
                speech.speak(text, self.voices[settings.UPPERCASE_VOICE])
            else:
                speech.speak(text)

        try:
            text = event.source.queryText()
        except NotImplementedError:
            return

        # Pylint is confused and flags this and similar lines, with the
        # following error:
        #
        # E1103:3673:Script.onTextInserted: Instance of 'str' has no
        #'caretOffset' member (but some types could not be inferred)
        #
        # But it does, so we'll just tell pylint that we know what we
        # are doing.
        #
        # pylint: disable-msg=E1103

        offset = min(event.detail1, text.caretOffset - 1)
        previousOffset = offset - 1
        if (offset < 0 or previousOffset < 0):
            return

        [currentChar, startOffset, endOffset] = \
            text.getTextAtOffset(offset, pyatspi.TEXT_BOUNDARY_CHAR)
        [previousChar, startOffset, endOffset] = \
            text.getTextAtOffset(previousOffset, pyatspi.TEXT_BOUNDARY_CHAR)

        if settings.enableEchoBySentence and \
           self.isSentenceDelimiter(currentChar, previousChar):
            self.echoPreviousSentence(event.source)

        elif settings.enableEchoByWord and self.isWordDelimiter(currentChar):
            self.echoPreviousWord(event.source)

    def stopSpeechOnActiveDescendantChanged(self, event):
        """Whether or not speech should be stopped prior to setting the
        locusOfFocus in onActiveDescendantChanged.

        Arguments:
        - event: the Event

        Returns True if speech should be stopped; False otherwise.
        """

        return True

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
            if self.stopSpeechOnActiveDescendantChanged(event):
                speech.stop()
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

        if event.type.startswith("object:state-changed:selected") \
           and orca_state.locusOfFocus:
            # If this selection state change is for the object which
            # currently has the locus of focus, and the last keyboard
            # event was Space, or we are a focused table cell and we
            # arrowed Down or Up and are now selected, then let the
            # user know the selection state.
            # See bugs #486908 and #519564 for more details.
            #
            if isinstance(orca_state.lastInputEvent,
                          input_event.KeyboardEvent):
                if orca_state.lastNonModifierKeyEvent:
                    keyString = orca_state.lastNonModifierKeyEvent.event_string
                else:
                    keyString = None
                mods = orca_state.lastInputEvent.modifiers
                isControlKey = mods & settings.CTRL_MODIFIER_MASK
                state = orca_state.locusOfFocus.getState()
                announceState = False

                if state.contains(pyatspi.STATE_FOCUSED) and \
                   self.isSameObject(event.source, orca_state.locusOfFocus):

                    if keyString == "space":
                        if isControlKey:
                            announceState = True
                        else:
                            # Weed out a bogus situation. If we are already
                            # selected and the user presses "space" again,
                            # we don't want to speak the intermediate
                            # "unselected" state.
                            #
                            eventState = event.source.getState()
                            selected = eventState.contains(\
                                           pyatspi.STATE_SELECTED)
                            announceState = (selected and event.detail1)

                    if (keyString == "Down" or keyString == "Up") \
                       and event.source.getRole() == pyatspi.ROLE_TABLE_CELL \
                       and state.contains(pyatspi.STATE_SELECTED):
                        announceState = True

                if announceState:
                    if event.detail1:
                        # Translators: this object is now selected.
                        # Let the user know this.
                        #
                        #
                        speech.speak(C_("text", "selected"), None, False)
                    else:
                        # Translators: this object is now unselected.
                        # Let the user know this.
                        #
                        #
                        speech.speak(C_("text", "unselected"), None, False)
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
                    self.presentToolTip(obj)
                elif orca_state.locusOfFocus \
                    and isinstance(orca_state.lastInputEvent,
                                   input_event.KeyboardEvent) \
                    and (orca_state.lastNonModifierKeyEvent.event_string \
                         == "F1"):
                    self.updateBraille(orca_state.locusOfFocus)
                    utterances = self.speechGenerator.generateSpeech(
                        orca_state.locusOfFocus)
                    utterances.extend(self.tutorialGenerator.getTutorial(
                                      orca_state.locusOfFocus, False))
                    speech.speak(utterances)
            return

        if event.source.getRole() in state_change_notifiers:
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

    def getOffsetsForPhrase(self, obj):
        """Return the start and end offset for the given phrase

        Arguments:
        - obj: the Accessible object
        """

        text = obj.queryText()
        lastPos = self.pointOfReference.get("lastCursorPosition")
        startOffset = lastPos[1]
        endOffset = text.caretOffset

        # Swap values if in wrong order (StarOffice is fussy about that).
        #
        if ((startOffset > endOffset) and (endOffset != -1)) or \
           (startOffset == -1):
            temp = endOffset
            endOffset = startOffset
            startOffset = temp
        return [startOffset, endOffset]

    def getOffsetsForLine(self, obj):
        """Return the start and end offset for the given line

        Arguments:
        - obj: the Accessible object
        """

        [line, endOffset, startOffset] = self.getTextLineAtCaret(obj)
        return [startOffset, endOffset]

    def getOffsetsForWord(self, obj):
        """Return the start and end offset for the given word

        Arguments:
        - obj: the Accessible object
        """

        text = obj.queryText()
        offset = text.caretOffset
        [word, startOffset, endOffset] = text.getTextAtOffset(offset,
                                           pyatspi.TEXT_BOUNDARY_WORD_START)
        return [startOffset, endOffset]

    def getOffsetsForChar(self, obj):
        """Return the start and end offset for the given character

        Arguments:
        - obj: the Accessible object
        """

        text = obj.queryText()
        offset = text.caretOffset

        mods = orca_state.lastInputEvent.modifiers
        if (mods & settings.SHIFT_MODIFIER_MASK) \
            and orca_state.lastNonModifierKeyEvent.event_string == "Right":
            startOffset = offset-1
            endOffset = offset
        else:
            startOffset = offset
            endOffset = offset+1

        return [startOffset, endOffset]

    def onTextAttributesChanged(self, event):
        """Called when an object's text attributes change. Right now this
        method is only to handle the presentation of spelling errors on
        the fly. Also note that right now, the Gecko toolkit is the only
        one to present this information to us.

        Arguments:
        - event: the Event
        """

        if settings.speechVerbosityLevel == settings.VERBOSITY_LEVEL_VERBOSE \
           and self.isSameObject(event.source, orca_state.locusOfFocus):
            try:
                text = event.source.queryText()
            except:
                return

            # If the misspelled word indicator has just appeared, it's
            # because the user typed a word boundary or navigated out
            # of the word. We don't want to have to store a full set of
            # each object's text attributes to compare, therefore, we'll
            # check the previous word (most likely case) and the next
            # word with respect to the current position.
            #
            prevWordAndOffsets = \
                text.getTextAtOffset(text.caretOffset - 1,
                                     pyatspi.TEXT_BOUNDARY_WORD_START)
            nextWordAndOffsets = \
                text.getTextAtOffset(text.caretOffset + 1,
                                     pyatspi.TEXT_BOUNDARY_WORD_START)

            if self.isWordMisspelled(event.source, prevWordAndOffsets[1] ) \
               or self.isWordMisspelled(event.source, nextWordAndOffsets[1]):
                # Translators: this is to inform the user of the presence
                # of the red squiggly line which indicates that a given
                # word is not spelled correctly.
                #
                speech.speak(_("misspelled"))

    def onTextSelectionChanged(self, event):
        """Called when an object's text selection changes.

        Arguments:
        - event: the Event
        """

        obj = event.source
        spokenRange = self.pointOfReference.get("spokenTextRange") or [0, 0]
        startOffset, endOffset = spokenRange

        if not obj.getState().contains(pyatspi.STATE_FOCUSED):
            # We're selecting across paragraph (or other text object)
            # boundaries. If we're here, the selection has changed in
            # an object which does not have the caret. We need to try
            # to sort this out.
            #
            lastPos = self.pointOfReference.get("lastCursorPosition")
            if not lastPos:
                # We have no point of reference. Bail.
                #
                return
            elif endOffset - startOffset > 1:
                # We're coming at the line from below. And didn't just
                # land on a blank/empty line. We have other methods for
                # dealing with this situation.
                #
                return
            else:
                # If we do a select all in a document in which each
                # paragraph is a separate accessible object, we'll
                # get an event for each of those objects. We don't
                # want to repeat "(un)selected". See bug #583811.
                #
                diff = lastPos[0].getIndexInParent() - obj.getIndexInParent()
                if abs(diff) > 1:
                    # We can skip this one because we'll do the
                    # announcement based on another one.
                    #
                    return
                elif startOffset > 0 and startOffset == endOffset:
                    try:
                        text = lastPos[0].queryText()
                    except:
                        pass
                    else:
                        if startOffset == text.characterCount:
                            return

            # We must be approaching from the top, left, or right. Or
            # from below but we've found a blank line. Our stored point
            # of reference tells us our caret location. Figure out how
            # we got here by looking at our position with respect to
            # the event under consideration.
            #
            relationType = None
            for relation in lastPos[0].getRelationSet():
                if relation.getRelationType() in [pyatspi.RELATION_FLOWS_FROM,
                                                  pyatspi.RELATION_FLOWS_TO] \
                   and self.isSameObject(obj, relation.getTarget(0)):
                    relationType = relation.getRelationType()
                    break

            # If there's a completely blank line in between our previous
            # and current locations, where we came from will lack any
            # offically-selectable characters. As a result, we won't
            # indicate when a blank line has been selected. Under these
            # conditions, we'll try to backtrack further.
            #
            endOffset = 0
            while obj and not endOffset:
                try:
                    endOffset = obj.queryText().characterCount
                    startOffset = max(0, endOffset - 1)
                except:
                    pass

                if not endOffset:
                    for relation in obj.getRelationSet():
                        if relation.getRelationType() == relationType:
                            obj = relation.getTarget(0)
                            break
                    else:
                        break

        self.speakTextSelectionState(obj, startOffset, endOffset)

    def onSelectionChanged(self, event):
        """Called when an object's selection changes.

        Arguments:
        - event: the Event
        """

        if not event or not event.source:
            return

        # Save the event source, if it is a menu or combo box. It will be
        # useful for optimizing getComponentAtDesktopCoords in the case
        # that the  pointer is hovering over a menu item. The alternative is
        # to traverse the application's tree looking for potential moused-over
        # menu items.
        if event.source.getRole() in (pyatspi.ROLE_COMBO_BOX,
                                           pyatspi.ROLE_MENU):
            self.lastSelectedMenu = event.source

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
        if "oldValue" in self.pointOfReference \
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

            # Clear the braille display just in case we are about to give
            # focus to an inaccessible application. See bug #519901 for
            # more details.
            #
            braille.clear()

            # Hide the flat review window and reset it so that it will be
            # recreated.
            #
            if self.flatReviewContext:
                self.drawOutline(-1, 0, 0, 0)
                self.flatReviewContext = None
                self.updateBraille(orca_state.locusOfFocus)

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
                    self.getAllSelectedText(obj)
                if textContents:
                    utterances = []
                    utterances.append(textContents)

                    # Translators: when the user selects (highlights) text in
                    # a document, Orca lets them know this.
                    #
                    utterances.append(C_("text", "selected"))
                    speech.speak(utterances)
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

    def getAtkNameForAttribute(self, attribName):
        """Converts the given attribute name into the Atk equivalent. This
        is necessary because an application or toolkit (e.g. Gecko) might
        invent entirely new names for the same attributes.

        Arguments:
        - attribName: The name of the text attribute

        Returns the Atk equivalent name if found or attribName otherwise.
        """

        return self.attributeNamesDict.get(attribName, attribName)

    def getAppNameForAttribute(self, attribName):
        """Converts the given Atk attribute name into the application's
        equivalent. This is necessary because an application or toolkit
        (e.g. Gecko) might invent entirely new names for the same text
        attributes.

        Arguments:
        - attribName: The name of the text attribute

        Returns the application's equivalent name if found or attribName
        otherwise.
        """

        for key, value in self.attributeNamesDict.items():
            if value == attribName:
                return key

        return attribName

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
            localizedKey = text_attribute_names.getTextAttributeName(key)
            if key in attributes:
                line = ""
                attribute = attributes[key]
                localizedValue = \
                    text_attribute_names.getTextAttributeName(attribute)
                if attribute:
                    key = self.getAtkNameForAttribute(key)
                    # If it's the 'weight' attribute and greater than 400, just
                    # speak it as bold, otherwise speak the weight.
                    #
                    if key == "weight" \
                       and (attribute == "bold" or int(attribute) > 400):
                        # Translators: bold as in the font sense.
                        #
                        line = _("bold")
                    elif key in ["left-margin", "right-margin"]:
                        # We need to test if we are getting a margin value
                        # that includes unit information (OOo now provides
                        # this). If not, then we will assume it's pixels.
                        #
                        numericPoint = locale.localeconv()["decimal_point"]
                        lastChar = attribute[len(attribute) - 1]
                        if lastChar == numericPoint or \
                           lastChar in self.digits:
                            # Translators: these represent the number of pixels
                            # for the left or right margins in a document.  We
                            # are hesitant to interpret the values -- they are
                            # given to us in some unknown form by the
                            # application, so we leave things in plural form
                            # here.
                            #
                            line = ngettext("%(key)s %(value)s pixel",
                                            "%(key)s %(value)s pixels",
                                            int(attribute)) \
                                   % {"key" : localizedKey,
                                      "value": localizedValue}
                    elif key in ["indent", "size"]:
                        # In Gecko, we seem to get these values as a number
                        # immediately followed by "px". But we'll hedge our
                        # bet.
                        #
                        value = attribute.split("px")
                        if len(value) > 1:
                            line = ngettext("%(key)s %(value)s pixel",
                                            "%(key)s %(value)s pixels",
                                            float(value[0])) \
                                   % {"key" : localizedKey,
                                      "value" : value[0]}
                    elif key == "family-name":
                        # In Gecko, we get a huge list and we just want the
                        # first one.  See:
                        # http://www.w3.org/TR/CSS2/fonts.html#font-family-prop
                        #
                        localizedValue = \
                            attribute.split(",")[0].strip().strip('"')

                    line = line or (localizedKey + " " + localizedValue)
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
                if key in allAttributes:
                    textAttr = allAttributes.get(key)
                    userAttr = userAttrDict.get(key)
                    if textAttr != userAttr or len(userAttr) == 0:
                        attributes[key] = textAttr

            self.outputCharAttributes(userAttrList, attributes)

            # If this is a hypertext link, then let the user know:
            #
            if self.getLinkIndex(orca_state.locusOfFocus, caretOffset) >= 0:
                # Translators: this indicates that this piece of
                # text is a hypertext link.
                #
                speech.speak(_("link"))

        return True

    def hasTextSelections(self, obj):
        """Return an indication of whether this object has selected text.
        Note that it's possible that this object has no selection, but is part
        of a selected text area. Because of this, we need to check the
        objects on either side to see if they are none zero length and
        have text selections.

        Arguments:
        - obj: the text object to start checking for selected text.

        Returns: an indication of whether this object has selected text,
        or adjacent text objects have selected text.
        """

        currentSelected = False
        otherSelected = False
        text = obj.queryText()
        nSelections = text.getNSelections()
        if nSelections:
            currentSelected = True
        else:
            otherSelected = False
            text = obj.queryText()
            displayedText = text.getText(0, self.getTextEndOffset(text))
            if (text.caretOffset == 0) or len(displayedText) == 0:
                current = obj
                morePossibleSelections = True
                while morePossibleSelections:
                    morePossibleSelections = False
                    for relation in current.getRelationSet():
                        if relation.getRelationType() == \
                               pyatspi.RELATION_FLOWS_FROM:
                            prevObj = relation.getTarget(0)
                            prevObjText = prevObj.queryText()
                            if prevObjText.getNSelections() > 0:
                                otherSelected = True
                            else:
                                displayedText = prevObjText.getText(0,
                                    self.getTextEndOffset(prevObjText))
                                if len(displayedText) == 0:
                                    current = prevObj
                                    morePossibleSelections = True
                            break

                current = obj
                morePossibleSelections = True
                while morePossibleSelections:
                    morePossibleSelections = False
                    for relation in current.getRelationSet():
                        if relation.getRelationType() == \
                               pyatspi.RELATION_FLOWS_TO:
                            nextObj = relation.getTarget(0)
                            nextObjText = nextObj.queryText()
                            if nextObjText.getNSelections() > 0:
                                otherSelected = True
                            else:
                                displayedText = nextObjText.getText(0,
                                    self.getTextEndOffset(nextObjText))
                                if len(displayedText) == 0:
                                    current = nextObj
                                    morePossibleSelections = True
                            break

        return [currentSelected, otherSelected]

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

            debug.println(debug.LEVEL_OFF, infoString)
            print infoString
            speech.speak(infoString)
            braille.displayMessage(infoString)

        return True

    def bypassNextCommand(self, inputEvent=None):
        """Causes the next keyboard command to be ignored by Orca
        and passed along to the current application.

        Returns True to indicate the input event has been consumed.
        """

        # Translators: Orca normally intercepts all keyboard
        # commands and only passes them along to the current
        # application when they are not Orca commands.  This
        # command causes the next command issued to be passed
        # along to the current application, bypassing Orca's
        # interception of it.
        #
        speech.speak(_("Bypass mode enabled."))
        orca_state.bypassNextCommand = True
        return True

    def enterLearnMode(self, inputEvent=None):
        """Turns learn mode on.  The user must press the escape key to exit
        learn mode.

        Returns True to indicate the input event has been consumed.
        """

        if settings.learnModeEnabled:
            return True

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

    def pursueForFlatReview(self, obj):
        """Determines if we should look any further at the object
        for flat review."""

        try:
            state = obj.getState()
        except:
            debug.printException(debug.LEVEL_WARNING)
            return False
        else:
            return state.contains(pyatspi.STATE_SHOWING)

    def getShowingDescendants(self, parent):
        """Given a parent that manages its descendants, return a list of
        Accessible children that are actually showing.  This algorithm
        was inspired a little by the srw_elements_from_accessible logic
        in Gnopernicus, and makes the assumption that the children of
        an object that manages its descendants are arranged in a row
        and column format.

        Arguments:
        - parent: The accessible which manages its descendants

        Returns a list of Accessible descendants which are showing.
        """

        if not parent:
            return []

        if not parent.getState().contains(pyatspi.STATE_MANAGES_DESCENDANTS) \
           or parent.childCount <= 50:
            return []

        try:
            icomponent = parent.queryComponent()
        except NotImplementedError:
            return []

        descendants = []

        parentExtents = icomponent.getExtents(0)

        # [[[TODO: WDW - HACK related to GAIL bug where table column
        # headers seem to be ignored:
        # http://bugzilla.gnome.org/show_bug.cgi?id=325809.  The
        # problem is that this causes getAccessibleAtPoint to return
        # the cell effectively below the real cell at a given point,
        # making a mess of everything.  So...we just manually add in
        # showing headers for now.  The remainder of the logic below
        # accidentally accounts for this offset, yet it should also
        # work when bug 325809 is fixed.]]]
        #
        try:
            table = parent.queryTable()
        except NotImplementedError:
            table = None

        if table:
            for i in range(0, table.nColumns):
                header = table.getColumnHeader(i)
                if header:
                    extents = header.queryComponent().getExtents(0)
                    stateset = header.getState()
                    if stateset.contains(pyatspi.STATE_SHOWING) \
                       and (extents.x >= 0) and (extents.y >= 0) \
                       and (extents.width > 0) and (extents.height > 0) \
                       and self.visible(extents.x, extents.y,
                                        extents.width, extents.height,
                                        parentExtents.x, parentExtents.y,
                                        parentExtents.width,
                                        parentExtents.height):
                        descendants.append(header)

        # This algorithm goes left to right, top to bottom while attempting
        # to do *some* optimization over queries.  It could definitely be
        # improved. The gridSize is a minimal chunk to jump around in the
        # table.
        #
        gridSize = 7
        currentY = parentExtents.y
        while currentY < (parentExtents.y + parentExtents.height):
            currentX = parentExtents.x
            minHeight = sys.maxint
            while currentX < (parentExtents.x + parentExtents.width):
                child = \
                    icomponent.getAccessibleAtPoint(currentX, currentY + 1, 0)
                if child:
                    extents = child.queryComponent().getExtents(0)
                    if extents.x >= 0 and extents.y >= 0:
                        newX = extents.x + extents.width
                        minHeight = min(minHeight, extents.height)
                        if not descendants.count(child):
                            descendants.append(child)
                    else:
                        newX = currentX + gridSize
                else:
                    newX = currentX + gridSize
                if newX <= currentX:
                    currentX += gridSize
                else:
                    currentX = newX
            if minHeight == sys.maxint:
                minHeight = gridSize
            currentY += minHeight

        return descendants

    def visible(self,
                ax, ay, awidth, aheight,
                bx, by, bwidth, bheight):
        """Returns true if any portion of region 'a' is in region 'b'
        """
        highestBottom = min(ay + aheight, by + bheight)
        lowestTop = max(ay, by)

        leftMostRightEdge = min(ax + awidth, bx + bwidth)
        rightMostLeftEdge = max(ax, bx)

        visible = False

        if (lowestTop <= highestBottom) \
           and (rightMostLeftEdge <= leftMostRightEdge):
            visible = True
        elif (aheight == 0):
            if (awidth == 0):
                visible = (lowestTop == highestBottom) \
                          and (leftMostRightEdge == rightMostLeftEdge)
            else:
                visible = leftMostRightEdge <= rightMostLeftEdge
        elif (awidth == 0):
            visible = (lowestTop <= highestBottom)

        return visible

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
            if inputEvent:
                # Translators: the 'flat review' feature of Orca
                # allows the blind user to explore the text in a
                # window in a 2D fashion.  That is, Orca treats all
                # the text from all objects in a window (e.g.,
                # buttons, labels, etc.) as a sequence of words in a
                # sequence of lines.  The flat review feature allows
                # the user to explore this text by the {previous,next}
                # {line,word,character}.  This message lets the user know
                # they have left the flat review feature.
                #
                if settings.speechVerbosityLevel \
                   != settings.VERBOSITY_LEVEL_BRIEF:
                    speech.speak(_("Leaving flat review."))
            self.drawOutline(-1, 0, 0, 0)
            self.flatReviewContext = None
            self.updateBraille(orca_state.locusOfFocus)
        else:
            if inputEvent:
                # Translators: the 'flat review' feature of Orca
                # allows the blind user to explore the text in a
                # window in a 2D fashion.  That is, Orca treats all
                # the text from all objects in a window (e.g.,
                # buttons, labels, etc.) as a sequence of words in a
                # sequence of lines.  The flat review feature allows
                # the user to explore this text by the {previous,next}
                # {line,word,character}.  This message lets the user know
                # they have entered the flat review feature.
                #
                if settings.speechVerbosityLevel \
                   != settings.VERBOSITY_LEVEL_BRIEF:
                    speech.speak(_("Entering flat review."))
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
                   > braille.viewport[0]) \
                and (isinstance(region, braille.ReviewText) \
                     or isinstance(region, braille.ReviewComponent)):
                position = max(region.brailleOffset, braille.viewport[0])
                offset = position - region.brailleOffset
                self.targetCursorCell = region.brailleOffset \
                                        - braille.viewport[0]
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
            movedCaret = False
            if startOffset > 0:
                movedCaret = text.setCaretOffset(startOffset - 1)

            # If we didn't move the caret and we're in a terminal, we
            # jump into flat review to review the text.  See
            # http://bugzilla.gnome.org/show_bug.cgi?id=482294.
            #
            if (not movedCaret) \
               and (orca_state.locusOfFocus.getRole() \
                    == pyatspi.ROLE_TERMINAL):
                context = self.getFlatReviewContext()
                context.goBegin(flat_review.Context.LINE)
                self.reviewPreviousCharacter(inputEvent)
        else:
            braille.panLeft(panAmount)
            # We might be panning through a flashed message.
            #
            braille.resetFlashTimer()
            braille.refresh(False, stopFlash=False)

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
            # We might be panning through a flashed message.
            #
            braille.resetFlashTimer()
            braille.refresh(False, stopFlash=False)

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

    def setContractedBraille(self, inputEvent=None):
        """Toggles contracted braille."""

        braille.setContractedBraille(inputEvent)
        return True

    def processRoutingKey(self, inputEvent=None):
        """Processes a cursor routing key."""

        braille.processRoutingKey(inputEvent)
        return True

    def processBrailleCutBegin(self, inputEvent=None):
        """Clears the selection and moves the caret offset in the currently
        active text area.
        """

        obj, caretOffset = braille.getCaretContext(inputEvent)

        if caretOffset >= 0:
            self.clearTextSelection(obj)
            self.setCaretOffset(obj, caretOffset)

        return True

    def processBrailleCutLine(self, inputEvent=None):
        """Extends the text selection in the currently active text
        area and also copies the selected text to the system clipboard."""

        obj, caretOffset = braille.getCaretContext(inputEvent)

        if caretOffset >= 0:
            self.adjustTextSelection(obj, caretOffset)
            texti = obj.queryText()
            startOffset, endOffset = texti.getSelection(0)
            import gtk
            clipboard = gtk.clipboard_get()
            clipboard.set_text(texti.getText(startOffset, endOffset))

        return True

    def getAbsoluteMouseCoordinates(self):
        """Gets the absolute position of the mouse pointer."""

        import gtk
        rootWindow = gtk.Window().get_screen().get_root_window()
        x, y, modifiers = rootWindow.get_pointer()

        return x, y

    def routePointerToItem(self, inputEvent=None):
        """Moves the mouse pointer to the current item."""

        # Store the original location for scripts which want to restore
        # it later.
        #
        self.oldMouseCoordinates = self.getAbsoluteMouseCoordinates()
        self.lastMouseRoutingTime = time.time()
        if self.flatReviewContext:
            self.flatReviewContext.routeToCurrent()
        else:
            try:
                eventsynthesizer.routeToCharacter(orca_state.locusOfFocus)
            except:
                try:
                    eventsynthesizer.routeToObject(orca_state.locusOfFocus)
                except:
                    # Translators: Orca has a command that allows the user
                    # to move the mouse pointer to the current object. If
                    # for some reason Orca cannot identify the current
                    # location, it will speak this message.
                    #
                    speech.speak(_("Could not find current location."))

        return True

    def leftClickReviewItem(self, inputEvent=None):
        """Performs a left mouse button click on the current item."""

        if self.flatReviewContext:
            self.flatReviewContext.clickCurrent(1)
        else:
            try:
                eventsynthesizer.clickCharacter(orca_state.locusOfFocus, 1)
            except:
                try:
                    eventsynthesizer.clickObject(orca_state.locusOfFocus, 1)
                except:
                    # Translators: Orca has a command that allows the user
                    # to move the mouse pointer to the current object. If
                    # for some reason Orca cannot identify the current
                    # location, it will speak this message.
                    #
                    speech.speak(_("Could not find current location."))
        return True

    def rightClickReviewItem(self, inputEvent=None):
        """Performs a right mouse button click on the current item."""

        if self.flatReviewContext:
            self.flatReviewContext.clickCurrent(3)
        else:
            try:
                eventsynthesizer.clickCharacter(orca_state.locusOfFocus, 3)
            except:
                try:
                    eventsynthesizer.clickObject(orca_state.locusOfFocus, 3)
                except:
                    # Translators: Orca has a command that allows the user
                    # to move the mouse pointer to the current object. If
                    # for some reason Orca cannot identify the current
                    # location, it will speak this message.
                    #
                    speech.speak(_("Could not find current location."))
        return True

    def reviewCurrentLine(self, inputEvent):
        """Brailles and speaks the current flat review line."""

        self._reviewCurrentLine(inputEvent, 1)
        self.lastReviewCurrentEvent = inputEvent

        return True

    def reviewSpellCurrentLine(self, inputEvent):
        """Brailles and spells the current flat review line."""

        self._reviewCurrentLine(inputEvent, 2)
        self.lastReviewCurrentEvent = inputEvent

        return True

    def reviewPhoneticCurrentLine(self, inputEvent):
        """Brailles and phonetically spells the current flat review line."""

        self._reviewCurrentLine(inputEvent, 3)
        self.lastReviewCurrentEvent = inputEvent

        return True

    def _reviewCurrentLine(self, inputEvent, speechType=1):
        """Presents the current flat review line via braille and speech.

        Arguments:
        - inputEvent - the current input event.
        - speechType - the desired presentation: speak (1), spell (2), or
                       phonetic (3)
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
            elif lineString.decode("UTF-8").isupper() \
                 and (speechType < 2 or speechType > 3):
                speech.speak(lineString, self.voices[settings.UPPERCASE_VOICE])
            elif speechType == 2:
                self.spellCurrentItem(lineString)
            elif speechType == 3:
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
        """Brailles and speaks the current item to the user."""

        self._reviewCurrentItem(inputEvent, targetCursorCell, 1)
        self.lastReviewCurrentEvent = inputEvent

        return True

    def reviewSpellCurrentItem(self, inputEvent, targetCursorCell=0):
        """Brailles and spells the current item to the user."""

        self._reviewCurrentItem(inputEvent, targetCursorCell, 2)
        self.lastReviewCurrentEvent = inputEvent

        return True

    def reviewPhoneticCurrentItem(self, inputEvent, targetCursorCell=0):
        """Brailles and phonetically spells the current item to the user."""

        self._reviewCurrentItem(inputEvent, targetCursorCell, 3)
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
                           speechType=1):
        """Presents the current item to the user.

        Arguments:
        - inputEvent - the current input event.
        - targetCursorCell - if non-zero, the target braille cursor cell.
        - speechType - the desired presentation: speak (1), spell (2), or
                       phonetic (3).
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
                elif wordString.decode("UTF-8").isupper() and speechType == 1:
                    speech.speak(wordString,
                                 self.voices[settings.UPPERCASE_VOICE])
                elif speechType == 2:
                    self.spellCurrentItem(wordString)
                elif speechType == 3:
                    self.phoneticSpellCurrentItem(wordString)
                elif speechType == 1:
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
            utterances = self.speechGenerator.generateSpeech(
                    context.getCurrentAccessible())
            utterances.extend(self.tutorialGenerator.getTutorial(
                    context.getCurrentAccessible(), False))
            speech.speak(utterances)
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
        """Brailles and speaks the current flat review character."""

        self._reviewCurrentCharacter(inputEvent, 1)
        self.lastReviewCurrentEvent = inputEvent

        return True

    def reviewSpellCurrentCharacter(self, inputEvent):
        """Brailles and 'spells' (phonetically) the current flat review
        character.
        """

        self._reviewCurrentCharacter(inputEvent, 2)
        self.lastReviewCurrentEvent = inputEvent

        return True

    def _reviewCurrentCharacter(self, inputEvent, speechType=1):
        """Presents the current flat review character via braille and speech.

        Arguments:
        - inputEvent - the current input event.
        - speechType - the desired presentation: speak (1) or phonetic (2)
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
                elif speechType == 2:
                    self.phoneticSpellCurrentItem(charString)
                elif charString.decode("UTF-8").isupper():
                    speech.speakCharacter(charString,
                                          self.voices[settings.UPPERCASE_VOICE])
                else:
                    speech.speakCharacter(charString)

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
            orca.showFindGUI()

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
            orca.showFindGUI()

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

    def printMemoryUsageHandler(self, inputEvent):
        """Prints memory usage information."""
        print 'TODO: print something useful for memory debugging'

    def printAppsHandler(self, inputEvent=None):
        """Prints a list of all applications to stdout."""
        self.printApps()
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
                return self.getRealActiveDescendant(obj1).name == \
                       self.getRealActiveDescendant(obj2).name
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

        try:
            return self.generatorCache[self.DISPLAYED_LABEL][obj]
        except:
            if not self.generatorCache.has_key(self.DISPLAYED_LABEL):
                self.generatorCache[self.DISPLAYED_LABEL] = {}
            labelString = None

        labels = self.findDisplayedLabel(obj)
        for label in labels:
            labelString = self.appendString(labelString,
                                            self.getDisplayedText(label))

        self.generatorCache[self.DISPLAYED_LABEL][obj] = labelString
        return self.generatorCache[self.DISPLAYED_LABEL][obj]

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

        try:
            return self.generatorCache[self.DISPLAYED_TEXT][obj]
        except:
            if not self.generatorCache.has_key(self.DISPLAYED_TEXT):
                self.generatorCache[self.DISPLAYED_TEXT] = {}
            displayedText = None

        role = obj.getRole()
        if role == pyatspi.ROLE_COMBO_BOX:
            displayedText = self.__getDisplayedTextInComboBox(obj)
            self.generatorCache[self.DISPLAYED_TEXT][obj] = displayedText
            return self.generatorCache[self.DISPLAYED_TEXT][obj]

        # The accessible text of an object is used to represent what is
        # drawn on the screen.
        #
        try:
            text = obj.queryText()
        except NotImplementedError:
            pass
        else:
            displayedText = text.getText(0, self.getTextEndOffset(text))

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

        self.generatorCache[self.DISPLAYED_TEXT][obj] = displayedText
        return self.generatorCache[self.DISPLAYED_TEXT][obj]

    def getTextForValue(self, obj):
        """Returns the text to be displayed for the object's current value.

        Arguments:
        - obj: the Accessible object that may or may not have a value.

        Returns a string representing the value.
        """

        # Use ARIA "valuetext" attribute if present.  See
        # http://bugzilla.gnome.org/show_bug.cgi?id=552965
        #
        attributes = obj.getAttributes()
        for attribute in attributes:
            if attribute.startswith("valuetext"):
                return attribute[10:]

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

        try:
            return self.generatorCache[self.REAL_ACTIVE_DESCENDANT][obj]
        except:
            if not self.generatorCache.has_key(self.REAL_ACTIVE_DESCENDANT):
                self.generatorCache[self.REAL_ACTIVE_DESCENDANT] = {}
            realActiveDescendant = None

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
                        if text.getText(0, self.getTextEndOffset(text)):
                            realActiveDescendant = child

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
        if not realActiveDescendant and obj and obj.childCount:
            realActiveDescendant = obj[-1]

        self.generatorCache[self.REAL_ACTIVE_DESCENDANT][obj] = \
            realActiveDescendant or obj
        return self.generatorCache[self.REAL_ACTIVE_DESCENDANT][obj]

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

            if not isinstance(role, list):
                role = [role]

            if isinstance(role[0], str):
                current_role = current.getRoleName()
            else:
                current_role = current.getRole()

            if not current_role in role:
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
                if lineString.decode("UTF-8").isupper():
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
           and (not segment[0] in self.whitespace):
            if (not respectPunctuation) \
               or (isPunctChar and (style <= level)):
                repeatChar = chnames.getCharacterName(segment[0])
                # Translators: Orca will tell you how many characters
                # are repeated on a line of text.  For example: "22
                # space characters".  The %d is the number and the %s
                # is the spoken word for the character.
                #
                line += " " \
                     + ngettext("%(count)d %(repeatChar)s character",
                                "%(count)d %(repeatChar)s characters",
                                count) \
                       % {"count" : count, "repeatChar": repeatChar}
            else:
                line += segment
        else:
            line += segment

        return line

    def adjustForLinks(self, obj, line, startOffset):
        """Adjust line to include the word "link" after any hypertext links.

        Arguments:
        - obj: the accessible object that this line came from.
        - line: the string to adjust for links.
        - startOffset: the caret offset at the start of the line.

        Returns: a new line adjusted to add the speaking of "link" after
        text which is also a link.
        """

        line = line.decode("UTF-8")
        endOffset = startOffset + len(line)

        try:
            hyperText = obj.queryHypertext()
            nLinks = hyperText.getNLinks()
        except:
            nLinks = 0

        adjustedLine = list(line)
        for n in range(nLinks, 0, -1):
            link = hyperText.getLink(n - 1)

            # We only care about links in the string, line:
            #
            if startOffset < link.endIndex < endOffset:
                index = link.endIndex - startOffset
            elif startOffset <= link.startIndex < endOffset:
                index = len(line) - 1
            else:
                continue

            # Translators: this indicates that this piece of
            # text is a hypertext link.
            #
            linkString = " " + _("link")

            # If the link was not followed by a whitespace or punctuation
            # character, then add in a space to make it more presentable.
            #
            nextChar = adjustedLine[index]
            if not (nextChar in self.whitespace \
                    or punctuation_settings.getPunctuationInfo(nextChar)):
                linkString += " "
            adjustedLine[index:index] = linkString

        return "".join(adjustedLine).encode("UTF-8")

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

    def expandEOCs(self, obj, startOffset=0, endOffset=-1):
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
        try:
            text = obj.queryText()
        except:
            text = None

        if text and text.characterCount:
            string = text.getText(startOffset, endOffset)
            unicodeText = string.decode("UTF-8")
            if unicodeText \
                and self.EMBEDDED_OBJECT_CHARACTER in unicodeText:
                # If we're not getting the full text of this object, but
                # rather a substring, we need to figure out the offset of
                # the first child within this substring.
                #
                childOffset = 0
                for child in obj:
                    if self.getCharacterOffsetInParent(child) >= startOffset:
                        break
                    childOffset += 1

                toBuild = list(unicodeText)
                count = toBuild.count(self.EMBEDDED_OBJECT_CHARACTER)
                for i in xrange(count):
                    index = toBuild.index(self.EMBEDDED_OBJECT_CHARACTER)
                    child = obj[i + childOffset]
                    childText = self.expandEOCs(child)
                    if not childText:
                        childText = ""
                    toBuild[index] = childText.decode("UTF-8")
                string = "".join(toBuild)

        return string

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

        newLine = ""
        words = self.WORDS_RE.split(line.decode("UTF-8"))
        for word in words:
            if word.isalnum():
                word = self._getPronunciationForSegment(word)
            newLine += word

        if line != newLine:
            debug.println(debug.LEVEL_FINEST,
                          "adjustForPronunciation: \n  From '%s'\n  To   '%s'" \
                          % (line, newLine))
            return newLine.encode("UTF-8")
        else:
            return line

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

    def getCellIndex(self, obj):
        """Returns the index of the cell which should be used with the
        table interface.  This is necessary because in some apps we
        cannot count on getIndexInParent() returning the index we need.

        Arguments:
        -obj: the table cell whose index we need.
        """
        return obj.getIndexInParent()

    def isSentenceDelimiter(self, currentChar, previousChar):
        """Returns True if we are positioned at the end of a sentence.
        This is determined by checking if the current character is a
        white space character and the previous character is one of the
        normal end-of-sentence punctuation characters.

        Arguments:
        - currentChar:  the current character
        - previousChar: the previous character

        Returns True if the given character is a sentence delimiter.
        """

        if not isinstance(currentChar, unicode):
            currentChar = currentChar.decode("UTF-8")

        if not isinstance(previousChar, unicode):
            previousChar = previousChar.decode("UTF-8")

        if currentChar == '\r' or currentChar == '\n':
            return True

        return (currentChar in self.whitespace and previousChar in '!.?:;')

    def isWordDelimiter(self, character):
        """Returns True if the given character is a word delimiter.

        Arguments:
        - character: the character in question

        Returns True if the given character is a word delimiter.
        """

        if not isinstance(character, unicode):
            character = character.decode("UTF-8")

        return (character in self.whitespace) \
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

    def getTextEndOffset(self, textInterface):
        """Returns the offset which should be used as the end offset.
        By default, this is -1. However, this value triggers an assertion
        in certain apps. See bug 598797.

        Argument:
        - textInterface: the accessible text interface for which the end
          offset is desired.

        """

        return -1

    def getTextLineAtCaret(self, obj, offset=None):
        """Gets the line of text where the caret is.

        Argument:
        - obj: an Accessible object that implements the AccessibleText
          interface
        - offset: an optional caret offset to use. (Not used here at the
          moment, but needed in the Gecko script)

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

    def getNestingLevel(self, obj):
        """Determines the nesting level of this object in a list.  If this
        object is not in a list relation, then 0 will be returned.

        Arguments:
        -obj: the Accessible object
        """

        if not obj:
            return 0

        try:
            return self.generatorCache[self.NESTING_LEVEL][obj]
        except:
            if not self.generatorCache.has_key(self.NESTING_LEVEL):
                self.generatorCache[self.NESTING_LEVEL] = {}

        nestingLevel = 0
        parent = obj.parent
        while parent.parent.getRole() == pyatspi.ROLE_LIST:
            nestingLevel += 1
            parent = parent.parent

        self.generatorCache[self.NESTING_LEVEL][obj] = nestingLevel
        return self.generatorCache[self.NESTING_LEVEL][obj]

    def getNodeLevel(self, obj):
        """Determines the node level of this object if it is in a tree
        relation, with 0 being the top level node.  If this object is
        not in a tree relation, then -1 will be returned.

        Arguments:
        -obj: the Accessible object
        """

        if not obj:
            return -1

        try:
            return self.generatorCache[self.NODE_LEVEL][obj]
        except:
            if not self.generatorCache.has_key(self.NODE_LEVEL):
                self.generatorCache[self.NODE_LEVEL] = {}

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

        self.generatorCache[self.NODE_LEVEL][obj] = len(nodes) - 1
        return self.generatorCache[self.NODE_LEVEL][obj]

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
        index = self.getCellIndex(obj)
        row = table.getRowAtIndex(index)
        col = table.getColumnAtIndex(index)
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

    def getKeyBinding(self, obj):
        """Gets the mnemonic, accelerator string and possibly shortcut
        for the given object.  These are based upon the first accessible
        action for the object.

        Arguments:
        - obj: the Accessible object

        Returns: list containing strings: [mnemonic, shortcut, accelerator]
        """

        try:
            return self.generatorCache[self.KEY_BINDING][obj]
        except:
            if not self.generatorCache.has_key(self.KEY_BINDING):
                self.generatorCache[self.KEY_BINDING] = {}

        try:
            action = obj.queryAction()
        except NotImplementedError:
            self.generatorCache[self.KEY_BINDING][obj] = ["", "", ""]
            return self.generatorCache[self.KEY_BINDING][obj]

        # Action is a string in the format, where the mnemonic and/or
        # accelerator can be missing.
        #
        # <mnemonic>;<full-path>;<accelerator>
        #
        # The keybindings in <full-path> should be separated by ":"
        #
        bindingStrings = action.getKeyBinding(0).decode("UTF-8").split(';')

        if len(bindingStrings) == 3:
            mnemonic       = bindingStrings[0]
            fullShortcut   = bindingStrings[1]
            accelerator    = bindingStrings[2]
        elif len(bindingStrings) > 0:
            mnemonic       = ""
            fullShortcut   = bindingStrings[0]
            try:
                accelerator = bindingStrings[1]
            except:
                accelerator = ""
        else:
            mnemonic       = ""
            fullShortcut   = ""
            accelerator    = ""

        fullShortcut = fullShortcut.replace("<","")
        fullShortcut = fullShortcut.replace(">"," ")
        fullShortcut = fullShortcut.replace(":"," ").strip()

        # If the accelerator or mnemonic strings includes a Space,
        # make sure we speak it.
        #
        if mnemonic.endswith(" "):
            # Translators: this is the spoken word for the space character
            #
            mnemonic += _("space")
        mnemonic = mnemonic.replace("<","")
        mnemonic = mnemonic.replace(">"," ").strip()

        if accelerator.endswith(" "):
            # Translators: this is the spoken word for the space character
            #
            accelerator += _("space")
        accelerator = accelerator.replace("<","")
        accelerator = accelerator.replace(">"," ").strip()

        debug.println(debug.LEVEL_FINEST, "default.getKeyBinding: " \
                      + repr([mnemonic, fullShortcut, accelerator]))

        self.generatorCache[self.KEY_BINDING][obj] = \
            [mnemonic, fullShortcut, accelerator]
        return self.generatorCache[self.KEY_BINDING][obj]

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
            line = indent + "+- " + debug.getAccessibleDetails(ancestor)
            debug.println(debug.LEVEL_OFF, line)
            print line
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
            line = indent + "(*) " + debug.getAccessibleDetails(root)
        else:
            line = indent + "+- " + debug.getAccessibleDetails(root)

        debug.println(debug.LEVEL_OFF, line)
        print line

        rootManagesDescendants = root.getState().contains( \
                                      pyatspi.STATE_MANAGES_DESCENDANTS)

        for child in root:
            if child == root:
                line = indent + "  " + "WARNING CHILD == PARENT!!!"
                debug.println(debug.LEVEL_OFF, line)
                print line
            elif not child:
                line = indent + "  " + "WARNING CHILD IS NONE!!!"
                debug.println(debug.LEVEL_OFF, line)
                print line
            elif child.parent != root:
                line = indent + "  " + "WARNING CHILD.PARENT != PARENT!!!"
                debug.println(debug.LEVEL_OFF, line)
                print line
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

        apps = self.getKnownApplications()
        line = "There are %d Accessible applications" % len(apps)
        debug.println(debug.LEVEL_OFF, line)
        print line
        for app in apps:
            line = debug.getAccessibleDetails(app, "  App: ", False)
            debug.println(debug.LEVEL_OFF, line)
            print line
            for child in app:
                line = debug.getAccessibleDetails(child, "    Window: ", False)
                debug.println(debug.LEVEL_OFF, line)
                print line
                if child.parent != app:
                    debug.println(debug.LEVEL_OFF,
                                  "      WARNING: child's parent is not app!!!")

        return True

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
            if key in prefsDict:
                setattr(settings, key, prefsDict[key])

    ########################################################################
    #                                                                      #
    # METHODS FOR DRAWING RECTANGLES AROUND OBJECTS ON THE SCREEN          #
    #                                                                      #
    ########################################################################

    def drawOutline(self, x, y, width, height):
        """Draws an outline around the accessible, erasing the
        last drawn outline in the process."""

        if (x == -1) and (y == 0) and (width == 0) and (height == 0):
            outline.erase()
        else:
            outline.draw(x, y, width, height)

    def outlineAccessible(self, accessible):
        """Draws a rectangular outline around the accessible, erasing the
        last drawn rectangle in the process."""

        try:
            component = accessible.queryComponent()
        except AttributeError:
            self.drawOutline(-1, 0, 0, 0)
        except NotImplementedError:
            pass
        else:
            visibleRectangle = \
                component.getExtents(pyatspi.DESKTOP_COORDS)
            self.drawOutline(visibleRectangle.x, visibleRectangle.y,
                             visibleRectangle.width, visibleRectangle.height)

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

        # If start offset and end offset are the same, just return False.
        # This is possible if there was no text spoken in onCaretMoved.
        #
        if startOffset == endOffset:
            return False

        try:
            text = obj.queryText()
        except:
            return False

        for i in xrange(text.getNSelections()):
            [startSelOffset, endSelOffset] = text.getSelection(i)
            if (startOffset >= startSelOffset) and (endOffset <= endSelOffset):
                return True

        return False

    def _saveSpokenTextRange(self, startOffset, endOffset):
        """Save away the start and end offset of the range of text that
        was spoken. It will be used by speakTextSelectionState, to try
        to determine if the text was selected or unselected.

        Arguments:
        - startOffset: the start of the spoken text range.
        - endOffset: the end of the spoken text range.
        """

        self.pointOfReference["spokenTextRange"] = [startOffset, endOffset]

    def _saveLastCursorPosition(self, obj, caretOffset):
        """Save away the current text cursor position for next time.

        Arguments:
        - obj: the current accessible
        - caretOffset: the cursor position within this object
        """

        self.pointOfReference["lastCursorPosition"] = [obj, caretOffset]

    def _saveLastTextSelections(self, text):
        """Save away the list of text selections for next time.

        Arguments:
        - text: the text object.
        """

        self.pointOfReference["lastSelections"] = []
        for i in xrange(text.getNSelections()):
            self.pointOfReference["lastSelections"].append(
              text.getSelection(i))

    def _getCtrlShiftSelectionsStrings(self):
        return [
            # Translators: when the user selects (highlights) text in
            # a document, Orca will speak information about what they
            # have selected.
            #
            _("paragraph selected down from cursor position"),
            _("paragraph unselected down from cursor position"),
            _("paragraph selected up from cursor position"),
            _("paragraph unselected up from cursor position"),
        ]

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
        # Control-Shift-Page_Down:
        #          speak "line selected to end from previous cursor position".
        # Control-Shift-Page_Up:
        #        speak "line selected from start to previous cursor position".
        #
        # Shift-Page_Down:    speak "page <state> from cursor position".
        # Shift-Page_Up:      speak "page <state> to cursor position".
        #
        # Control-Shift-Down: speak "line <state> down from cursor position".
        # Control-Shift-Up:   speak "line <state> up from cursor position".
        #
        # Control-Shift-Home: speak "document <state> to cursor position".
        # Control-Shift-End:  speak "document <state> from cursor position".
        #
        # Control-a:          speak "entire document selected".
        #
        # where <state> is either "selected" or "unselected" depending
        # upon whether there are any text selections.
        #
        if isinstance(orca_state.lastInputEvent, input_event.KeyboardEvent):
            eventStr = orca_state.lastNonModifierKeyEvent.event_string
            mods = orca_state.lastInputEvent.modifiers
        else:
            eventStr = None
            mods = 0

        isControlKey = mods & settings.CTRL_MODIFIER_MASK
        isShiftKey = mods & settings.SHIFT_MODIFIER_MASK
        selectedText = (text.getNSelections() != 0)

        specialCaseFound = False
        if (eventStr == "Page_Down") and isShiftKey and isControlKey:
            specialCaseFound = True
            # Translators: when the user selects (highlights) text in
            # a document, Orca will speak information about what they
            # have selected.
            #
            line = _("line selected to end from previous cursor position")

        elif (eventStr == "Page_Up") and isShiftKey and isControlKey:
            specialCaseFound = True
            # Translators: when the user selects (highlights) text in
            # a document, Orca will speak information about what they
            # have selected.
            #
            line = _("line selected from start to previous cursor position")

        elif (eventStr == "Page_Down") and isShiftKey and not isControlKey:
            specialCaseFound = True
            if selectedText:
                # Translators: when the user selects (highlights) text in
                # a document, Orca will speak information about what they
                # have selected.
                #
                line = _("page selected from cursor position")
            else:
                # Translators: when the user unselects text in a document,
                # Orca will speak information about what they have unselected.
                #
                line = _("page unselected from cursor position")

        elif (eventStr == "Page_Up") and isShiftKey and not isControlKey:
            specialCaseFound = True
            if selectedText:
                # Translators: when the user selects (highlights) text in
                # a document, Orca will speak information about what they
                # have selected.
                #
                line = _("page selected to cursor position")
            else:
                # Translators: when the user unselects text in a document,
                # Orca will speak information about what they have unselected.
                #
                line = _("page unselected to cursor position")

        elif (eventStr == "Down") and isShiftKey and isControlKey:
            specialCaseFound = True
            strings = self._getCtrlShiftSelectionsStrings()
            if selectedText:
                line = strings[0]
            else:
                line = strings[1]

        elif (eventStr == "Up") and isShiftKey and isControlKey:
            specialCaseFound = True
            strings = self._getCtrlShiftSelectionsStrings()
            if selectedText:
                line = strings[2]
            else:
                line = strings[3]

        elif (eventStr == "Home") and isShiftKey and isControlKey:
            specialCaseFound = True
            if selectedText:
                # Translators: when the user selects (highlights) text in
                # a document, Orca will speak information about what they
                # have selected.
                #
                line = _("document selected to cursor position")
            else:
                # Translators: when the user unselects text in a document,
                # Orca will speak information about what they have unselected.
                #
                line = _("document unselected to cursor position")

        elif (eventStr == "End") and isShiftKey and isControlKey:
            specialCaseFound = True
            if selectedText:
                # Translators: when the user selects (highlights) text in
                # a document, Orca will speak information about what they
                # have selected.
                #
                line = _("document selected from cursor position")
            else:
                # Translators: when the user unselects text in a document,
                # Orca will speak information about what they have unselected.
                #
                line = _("document unselected from cursor position")

        elif (eventStr == "A") and isControlKey:
            # The user has typed Control-A. Check to see if the entire
            # document has been selected, and if so, let the user know.
            #
            charCount = text.characterCount
            for i in range(0, text.getNSelections()):
                [startOffset, endOffset] = text.getSelection(i)
                if text.caretOffset == 0 and \
                   startOffset == 0 and endOffset == charCount:
                    specialCaseFound = True
                    self.updateBraille(obj)

                    # Translators: this means the user has selected
                    # all the text in a document (e.g., Ctrl+a in gedit).
                    #
                    line = _("entire document selected")

        if specialCaseFound:
            speech.speak(line, None, False)
            return
        elif startOffset == endOffset:
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
            speech.speak(C_("text", "selected"), None, False)
        elif len(text.getText(startOffset, endOffset)):
            # Translators: when the user unselects
            # (unhighlights) text in a document, Orca lets
            # them know this.
            #
            speech.speak(C_("text", "unselected"), None, False)

        self._saveLastTextSelections(text)

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

    def clearTextSelection(self, obj):
        """Clears the text selection if the object supports it."""
        try:
            texti = obj.queryText()
        except:
            return

        for i in range(0, texti.getNSelections()):
            texti.removeSelection(0)

    def adjustTextSelection(self, obj, offset):
        """Adjusts the end point of a text selection"""
        try:
            texti = obj.queryText()
        except:
            return

        if not texti.getNSelections():
            caretOffset = texti.caretOffset
            startOffset = min(offset, caretOffset)
            endOffset = max(offset, caretOffset)
            texti.addSelection(startOffset, endOffset)
        else:
            startOffset, endOffset = texti.getSelection(0)
            if offset < startOffset:
                startOffset = offset
            else:
                endOffset = offset
            texti.setSelection(0, startOffset, endOffset)

    def setCaretOffset(self, obj, offset):
        """Set the caret offset on a given accessible. Similar to
        Accessible.setCaretOffset()

        Arguments:
        - obj: Given accessible object.
        - offset: Offset to hich to set the caret.
        """
        try:
            texti = obj.queryText()
        except:
            return None

        texti.setCaretOffset(offset)

    def attributeStringToDictionary(self, dict_string):
        """Creates a Python dict from a typical attributes list returned from
        different AT-SPI methods.

        Arguments:
        - dict_string: A list of colon seperated key/value pairs seperated by
        semicolons.
        Returns a Python dict of the given attributes.
        """
        try:
            return dict(
                map(lambda pair: pair.strip().split(':'),
                    dict_string.strip('; ').split(';')))
        except ValueError:
            return {}

    def _getPopupItemAtDesktopCoords(self, x, y):
        """Since pop-up items often don't contain nested components, we need
        a way to efficiently determine if the cursor is over a menu item.

        Arguments:
        - x: X coordinate.
        - y: Y coordinate.

        Returns a menu item the mouse is over, or None.
        """
        suspect_children = []
        if self.lastSelectedMenu:
            try:
                si = self.lastSelectedMenu.querySelection()
            except NotImplementedError:
                return None

            if si.nSelectedChildren > 0:
                suspect_children = [si.getSelectedChild(0)]
            else:
                suspect_children = self.lastSelectedMenu
            for child in suspect_children:
                try:
                    ci = child.queryComponent()
                except NotImplementedError:
                    continue

                if ci.contains(x, y, pyatspi.DESKTOP_COORDS) \
                   and ci.getLayer() == pyatspi.LAYER_POPUP:
                    return child

    def getComponentAtDesktopCoords(self, parent, x, y):
        """Get the descendant component at the given desktop coordinates.

        Arguments:

        - parent: The parent component we are searching below.
        - x: X coordinate.
        - y: Y coordinate.

        Returns end-node that contains the given coordinates, or None.
        """
        acc = self._getPopupItemAtDesktopCoords(x, y)
        if acc:
            return acc

        container = parent
        while True:
            if container.getRole() == pyatspi.ROLE_PAGE_TAB_LIST:
                try:
                    si = container.querySelection()
                    container = si.getSelectedChild(0)[0]
                except NotImplementedError:
                    pass
            try:
                ci = container.queryComponent()
            except:
                return None
            else:
                inner_container = container
            container =  ci.getAccessibleAtPoint(x, y, pyatspi.DESKTOP_COORDS)
            if not container or container.queryComponent() == ci:
                # The gecko bridge simply has getAccessibleAtPoint return
                # itself if there are no further children.
                # TODO: Put in Gecko.py
                break
        if inner_container == parent:
            return None
        else:
            return inner_container

    # pylint: disable-msg=W0142

    def getSelectedText(self, obj):
        """Get the text selection for the given object.

        Arguments:
        - obj: the text object to extract the selected text from.

        Returns: the selected text contents plus the start and end
        offsets within the text.
        """

        textContents = ""
        textObj = obj.queryText()
        nSelections = textObj.getNSelections()
        for i in range(0, nSelections):
            [startOffset, endOffset] = textObj.getSelection(i)

            debug.println(debug.LEVEL_FINEST,
                "getSelectedText: selection start=%d, end=%d" % \
                (startOffset, endOffset))

            selectedText = textObj.getText(startOffset, endOffset)
            debug.println(debug.LEVEL_FINEST,
                "getSelectedText: selected text=<%s>" % selectedText)

            if i > 0:
                textContents += " "
            textContents += selectedText

        return [textContents, startOffset, endOffset]

    def getAllSelectedText(self, obj):
        """Get all the text applicable text selections for the given object.
        including any previous or next text objects that also have
        selected text and add in their text contents.

        Arguments:
        - obj: the text object to start extracting the selected text from.

        Returns: all the selected text contents plus the start and end
        offsets within the text for the given object.
        """

        textContents = ""
        startOffset = 0
        endOffset = 0
        text = obj.queryText()
        if text.getNSelections() > 0:
            [textContents, startOffset, endOffset] = \
                self.getSelectedText(obj)

        current = obj
        morePossibleSelections = True
        while morePossibleSelections:
            morePossibleSelections = False
            for relation in current.getRelationSet():
                if relation.getRelationType() \
                   == pyatspi.RELATION_FLOWS_FROM:
                    prevObj = relation.getTarget(0)
                    prevObjText = prevObj.queryText()
                    if prevObjText.getNSelections() > 0:
                        [newTextContents, start, end] = \
                            self.getSelectedText(prevObj)
                        textContents = newTextContents + " " + textContents
                        current = prevObj
                        morePossibleSelections = True
                    else:
                        displayedText = prevObjText.getText(0,
                            self.getTextEndOffset(prevObjText))
                        if len(displayedText) == 0:
                            current = prevObj
                            morePossibleSelections = True
                    break

        current = obj
        morePossibleSelections = True
        while morePossibleSelections:
            morePossibleSelections = False
            for relation in current.getRelationSet():
                if relation.getRelationType() \
                   == pyatspi.RELATION_FLOWS_TO:
                    nextObj = relation.getTarget(0)
                    nextObjText = nextObj.queryText()
                    if nextObjText.getNSelections() > 0:
                        [newTextContents, start, end] = \
                            self.getSelectedText(nextObj)
                        textContents += " " + newTextContents
                        current = nextObj
                        morePossibleSelections = True
                    else:
                        displayedText = nextObjText.getText(0,
                            self.getTextEndOffset(nextObjText))
                        if len(displayedText) == 0:
                            current = nextObj
                            morePossibleSelections = True
                    break

        return [textContents, startOffset, endOffset]

    def getAllTextSelections(self, acc):
        """Get a list of text selections in the given accessible object,
        equivelent to getNSelections()*texti.getSelection()

        Arguments:
        - acc: An accessible.

        Returns list of start and end offsets for multiple selections, or an
        empty list if nothing is selected or if the accessible does not support
        the text interface.
        """
        rv = []
        try:
            texti = acc.queryText()
        except:
            return rv

        for i in xrange(texti.getNSelections()):
            rv.append(texti.getSelection(i))

        return rv

    def speakWordUnderMouse(self, acc):
        """Determine if the speak-word-under-mouse capability applies to
        the given accessible.

        Arguments:
        - acc: Accessible to test.

        Returns True if this accessible should provide the single word.
        """
        return acc and acc.getState().contains(pyatspi.STATE_EDITABLE)

    def speakMisspelledIndicator(self, obj, offset):
        """Speaks an announcement indicating that a given word is misspelled.

        Arguments:
        - obj: An accessible which implements the accessible text interface.
        - offset: Offset in the accessible's text for which to retrieve the
          attributes.
        """

        if settings.speechVerbosityLevel == settings.VERBOSITY_LEVEL_VERBOSE:
            try:
                text = obj.queryText()
            except:
                return
            # If we're on whitespace, we cannot be on a misspelled word.
            #
            charAndOffsets = \
                text.getTextAtOffset(offset, pyatspi.TEXT_BOUNDARY_CHAR)
            if not charAndOffsets[0].strip() \
               or self.isWordDelimiter(charAndOffsets[0]):
                orca_state.lastWordCheckedForSpelling = charAndOffsets[0]
                return

            wordAndOffsets = \
                text.getTextAtOffset(offset, pyatspi.TEXT_BOUNDARY_WORD_START)
            if self.isWordMisspelled(obj, offset) \
               and wordAndOffsets[0] != orca_state.lastWordCheckedForSpelling:
                # Translators: this is to inform the user of the presence
                # of the red squiggly line which indicates that a given
                # word is not spelled correctly.
                #
                speech.speak(_("misspelled"))
            # Store this word so that we do not continue to present the
            # presence of the red squiggly as the user arrows amongst
            # the characters.
            #
            orca_state.lastWordCheckedForSpelling = wordAndOffsets[0]

    def isWordMisspelled(self, obj, offset):
        """Identifies if the current word is flagged as misspelled by the
        application.

        Arguments:
        - obj: An accessible which implements the accessible text interface.
        - offset: Offset in the accessible's text for which to retrieve the
          attributes.

        Returns True if the word is flagged as misspelled.
        """

        # Right now, the Gecko toolkit is the only one to expose this
        # information to us. As other appliations and toolkits do so,
        # the scripts for those applications/toolkits can override this
        # method and, theoretically, the presentation of misspelled words
        # should JustWork(tm).
        #
        return False

    def getTextAttributes(self, acc, offset, get_defaults=False):
        """Get the text attributes run for a given offset in a given accessible

        Arguments:
        - acc: An accessible.
        - offset: Offset in the accessible's text for which to retrieve the
        attributes.
        - get_defaults: Get the default attributes as well as the unique ones.
        Default is True

        Returns a dictionary of attributes, a start offset where the attributes
        begin, and an end offset. Returns ({}, 0, 0) if the accessible does not
        supprt the text attribute.
        """
        rv = {}
        try:
            texti = acc.queryText()
        except:
            return rv, 0, 0

        if get_defaults:
            rv.update(self.attributeStringToDictionary(
                texti.getDefaultAttributes()))

        attrib_str, start, end = texti.getAttributes(offset)

        rv.update(self.attributeStringToDictionary(attrib_str))

        return rv, start, end

    def getWordAtCoords(self, acc, x, y):
        """Get the word at the given coords in the accessible.

        Arguments:
        - acc: Accessible that supports the Text interface.
        - x: X coordinate.
        - y: Y coordinate.

        Returns a tuple containing the word, start offset, and end offset.
        """
        try:
            ti = acc.queryText()
        except NotImplementedError:
            return '', 0, 0

        text_contents = ti.getText(0, self.getTextEndOffset(ti))
        line_offsets = []
        start_offset = 0
        while True:
            try:
                end_offset = text_contents.index('\n', start_offset)
            except ValueError:
                line_offsets.append((start_offset, len(text_contents)))
                break
            line_offsets.append((start_offset, end_offset))
            start_offset = end_offset + 1
        for start, end in line_offsets:
            bx, by, bw, bh = \
                ti.getRangeExtents(start, end, pyatspi.DESKTOP_COORDS)
            bb = mouse_review.BoundingBox(bx, by, bw, bh)
            if bb.isInBox(x, y):
                start_offset = 0
                word_offsets = []
                while True:
                    try:
                        end_offset = \
                            text_contents[start:end].index(' ', start_offset)
                    except ValueError:
                        word_offsets.append((start_offset,
                                             len(text_contents[start:end])))
                        break
                    word_offsets.append((start_offset, end_offset))
                    start_offset = end_offset + 1
                for a, b in word_offsets:
                    bx, by, bw, bh = \
                        ti.getRangeExtents(start+a, start+b,
                                           pyatspi.DESKTOP_COORDS)
                    bb = mouse_review.BoundingBox(bx, by, bw, bh)
                    if bb.isInBox(x, y):
                        return text_contents[start+a:start+b], start+a, start+b
        return '', 0, 0

# Dictionary that defines the state changes we care about for various
# objects.  The key represents the role and the value represents a list
# of states that we care about.
#
state_change_notifiers = {}

state_change_notifiers[pyatspi.ROLE_CHECK_MENU_ITEM] = ("checked", None)
state_change_notifiers[pyatspi.ROLE_CHECK_BOX]       = ("checked",
                                                        "indeterminate",
                                                        None)
state_change_notifiers[pyatspi.ROLE_PANEL]           = ("showing", None)
state_change_notifiers[pyatspi.ROLE_LABEL]           = ("showing", None)
state_change_notifiers[pyatspi.ROLE_RADIO_BUTTON]    = ("checked", None)
state_change_notifiers[pyatspi.ROLE_TOGGLE_BUTTON]   = ("checked",
                                                        "pressed",
                                                        None)
state_change_notifiers[pyatspi.ROLE_TABLE_CELL]      = ("checked",
                                                        "expanded",
                                                        None)
state_change_notifiers[pyatspi.ROLE_LIST_ITEM]       = ("expanded", None)
state_change_notifiers[pyatspi.ROLE_LABEL]           = ("expanded", None)
