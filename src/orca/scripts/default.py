# Orca
#
# Copyright 2004-2009 Sun Microsystems Inc.
# Copyright 2010 Joanmarie Diggs
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

"""The default Script for presenting information to the user using
both speech and Braille.  This is based primarily on the de-facto
standard implementation of the AT-SPI, which is the GAIL support
for GTK."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2004-2009 Sun Microsystems Inc." \
                "Copyright (c) 2010 Joanmarie Diggs"
__license__   = "LGPL"

import locale
import time

import pyatspi
import orca.braille as braille
import orca.debug as debug
import orca.eventsynthesizer as eventsynthesizer
import orca.find as find
import orca.flat_review as flat_review
import orca.input_event as input_event
import orca.keybindings as keybindings
import orca.outline as outline
import orca.orca as orca
import orca.orca_state as orca_state
import orca.phonnames as phonnames
import orca.script as script
import orca.settings as settings
import orca.settings_manager as settings_manager
import orca.speech as speech
import orca.speechserver as speechserver
import orca.mouse_review as mouse_review
import orca.text_attribute_names as text_attribute_names
import orca.notification_messages as notification_messages

from orca.orca_i18n import _
from orca.orca_i18n import ngettext
from orca.orca_i18n import C_

_settingsManager = settings_manager.getManager()

########################################################################
#                                                                      #
# The Default script class.                                            #
#                                                                      #
########################################################################

class Script(script.Script):

    EMBEDDED_OBJECT_CHARACTER = u'\ufffc'
    NO_BREAK_SPACE_CHARACTER  = u'\u00a0'

    # generatorCache
    #
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

        self.inputEventHandlers["reviewUnicodeCurrentCharacterHandler"] = \
            input_event.InputEventHandler(
                Script.reviewUnicodeCurrentCharacter,
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
                # cause Orca to speak information about the current character
                # Like its unicode value and other relevant information
                #
                _("Speaks unicode value of the current flat review character."))


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

        self.inputEventHandlers["enterListShortcutsModeHandler"] = \
            input_event.InputEventHandler(
                Script.enterListShortcutsMode,
                # Translators: Orca has a "List Shortcuts Mode" that will allow
                # the user to list a group of keyboard shortcuts. The Orca
                # default shortcuts can be listed by pressing 1, and Orca
                # shortcuts for the application under focus can be listed by
                # pressing 2. User can press Up/ Down to navigate and hear
                # the list, changeover to another list by pressing 1/2,
                # and exit the "List Shortcuts Mode" by pressing Escape.
                #
                _("Enters list shortcuts mode.  Press escape to exit " \
                  "list shortcuts mode."), False)
                # Do not enable learn mode for this action

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
                Script.toggleSilenceSpeech,
                # Translators: Orca allows the user to turn speech synthesis
                # on or off.  We call it 'silencing'.
                #
                _("Toggles the silencing of speech."))

        self.inputEventHandlers[ \
          "toggleSpeakingIndentationJustificationHandler"] = \
            input_event.InputEventHandler(
                Script.toggleSpeakingIndentationJustification,
                # Translators: Orca allows the user to enable/disable
                # the speaking of indentation and justification.
                #
                _("Toggles the speaking of indentation and justification."))

        self.inputEventHandlers["cycleSpeakingPunctuationLevelHandler"] = \
            input_event.InputEventHandler(
                Script.cycleSpeakingPunctuationLevel,
                # Translators: Orca allows users to cycle through
                # punctuation levels.
                # None, some, most, or all, punctuation will be spoken.
                #
                _("Cycles to the next speaking of punctuation level."))

        self.inputEventHandlers["cycleKeyEchoHandler"] = \
            input_event.InputEventHandler(
                Script.cycleKeyEcho,
                # Translators: Orca has an "echo" setting which allows
                # the user to configure what is spoken in response to a
                # key press. Given a user who typed "Hello world.":
                # - key echo: "H e l l o space w o r l d period"
                # - word echo: "Hello" spoken when the space is pressed;
                #   "world" spoken when the period is pressed.
                # - sentence echo: "Hello world" spoken when the period
                #   is pressed.
                # A user can choose to have no echo, one type of echo, or
                # multiple types of echo.
                # The following string refers to a command that allows the
                # user to quickly choose which type of echo is being used.
                #
                _("Cycles to the next key echo level."))

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
                Script.cycleDebugLevel,
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

        self.inputEventHandlers["toggleMouseReviewHandler"] = \
            input_event.InputEventHandler(
                mouse_review.toggle,
                # Translators: Orca allows the item under the pointer to
                # be spoken. This toggles the feature.
                #
                _("Toggle mouse review mode."))

        self.inputEventHandlers["presentTimeHandler"] = \
            input_event.InputEventHandler(
                Script.presentTime,
                # Translators: Orca can present the current time to the
                # user when the user presses
                # a shortcut key.
                #
                _("Present current time."))

        self.inputEventHandlers["presentDateHandler"] = \
            input_event.InputEventHandler(
                Script.presentDate,
                # Translators: Orca can present the current date to the
                # user when the user presses
                # a shortcut key.
                #
                _("Present current date."))

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

        self.inputEventHandlers.update(notification_messages.inputEventHandlers)

    def getInputEventHandlerKey(self, inputEventHandler):
        """Returns the name of the key that contains an inputEventHadler
        passed as argument
        """

        for keyName, handler in list(self.inputEventHandlers.items()):
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

        import orca.desktop_keyboardmap as desktop_keyboardmap
        keyBindings = keybindings.KeyBindings()
        keyBindings.load(desktop_keyboardmap.keymap, self.inputEventHandlers)
        return keyBindings

    def __getLaptopBindings(self):
        """Returns an instance of keybindings.KeyBindings that use the
        the main keyboard keys for focus tracking and flat review.
        """

        import orca.laptop_keyboardmap as laptop_keyboardmap
        keyBindings = keybindings.KeyBindings()
        keyBindings.load(laptop_keyboardmap.keymap, self.inputEventHandlers)
        return keyBindings

    def getKeyBindings(self):
        """Defines the key bindings for this script.

        Returns an instance of keybindings.KeyBindings.
        """

        keyBindings = script.Script.getKeyBindings(self)

        bindings = self.getDefaultKeyBindings()
        for keyBinding in bindings.keyBindings:
            keyBindings.add(keyBinding)

        bindings = self.getToolkitKeyBindings()
        for keyBinding in bindings.keyBindings:
            keyBindings.add(keyBinding)

        bindings = self.getAppKeyBindings()
        for keyBinding in bindings.keyBindings:
            keyBindings.add(keyBinding)

        return keyBindings

    def getDefaultKeyBindings(self):
        """Returns the default script's keybindings, i.e. without any of
        the toolkit or application specific commands added."""

        keyBindings = keybindings.KeyBindings()

        layout = _settingsManager.getSetting('keyboardLayout')
        if layout == settings.GENERAL_KEYBOARD_LAYOUT_DESKTOP:
            for keyBinding in self.__getDesktopBindings().keyBindings:
                keyBindings.add(keyBinding)
        else:
            for keyBinding in self.__getLaptopBindings().keyBindings:
                keyBindings.add(keyBinding)

        import orca.common_keyboardmap as common_keyboardmap
        keyBindings.load(common_keyboardmap.keymap, self.inputEventHandlers)

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
        if self.utilities.isSameObject(oldLocusOfFocus, newLocusOfFocus):
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
            for key in list(self.pointOfReference.keys()):
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
            # [[[TODO: WDW - this should be pushed into script_utilities'
            # adjustForPronunciation method.]]]
            #
            rolesList = [pyatspi.ROLE_TABLE_CELL, \
                         pyatspi.ROLE_TABLE, \
                         pyatspi.ROLE_SCROLL_PANE, \
                         pyatspi.ROLE_PANEL, \
                         pyatspi.ROLE_PANEL]
            if self.utilities.hasMatchingHierarchy(newLocusOfFocus, rolesList) \
               and newLocusOfFocus.getApplication().name == "orca":
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
            try:
                newRole = newLocusOfFocus.getRole()
            except:
                newRole = None
            if newRole == pyatspi.ROLE_LINK:
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
            if newRole == pyatspi.ROLE_TABLE_CELL:
                try:
                    table = newParent.queryTable()
                except:
                    pass
                else:
                    index = self.utilities.cellIndex(newLocusOfFocus)
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
            if self.utilities.isSameObject(
                obj,
                self.flatReviewContext.getCurrentAccessible()):
                self.updateBrailleReview()
            return

        # If this object is CONTROLLED_BY the object that currently
        # has focus, speak/braille this object.
        #
        try:
            relations = obj.getRelationSet()
        except (LookupError, RuntimeError):
            relations = []
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
                            target, alreadyFocused=False)
                        utterances.extend(self.tutorialGenerator.getTutorial(
                                          target, True))
                        speech.speak(utterances)
                        return

        if obj.getRole() == pyatspi.ROLE_NOTIFICATION \
           and obj.getState().contains(pyatspi.STATE_SHOWING):
            utterances = self.speechGenerator.generateSpeech(obj)
            speech.speak(utterances)
            labels = self.utilities.unrelatedLabels(obj)
            msg = ''.join(map(self.utilities.displayedText, labels))
            self.displayBrailleMessage(msg, flashTime=settings.brailleFlashTime)
            notification_messages.saveMessage(msg)

        if not self.utilities.isSameObject(obj, orca_state.locusOfFocus):
            return

        # Radio buttons normally change their state when you arrow to them,
        # so we handle the announcement of their state changes in the focus
        # handling code.  However, we do need to handle radio buttons where
        # the user needs to press the space key so select them.  We see this
        # in the disk selection area of the OpenSolaris gui-install application
        # for example.
        #
        if obj.getRole() == pyatspi.ROLE_RADIO_BUTTON:
            eventStr, mods = self.utilities.lastKeyAndModifiers()
            if not eventStr in [" ", "space"]:
                return

        if event:
            debug.println(debug.LEVEL_FINE,
                          "VISUAL CHANGE: '%s' '%s' (event='%s')" \
                          % (obj.name, obj.getRole(), event.type))
        else:
            debug.println(debug.LEVEL_FINE,
                          "VISUAL CHANGE: '%s' '%s' (event=None)" \
                          % (obj.name, obj.getRole()))

        self.updateBraille(obj)
        utterances = self.speechGenerator.generateSpeech(
                         obj, alreadyFocused=True)
        utterances.extend(self.tutorialGenerator.getTutorial(obj, True))
        speech.speak(utterances)

    def activate(self):
        """Called when this script is activated."""

        _settingsManager.loadAppSettings(self)
        braille.setupKeyRanges(list(self.brailleBindings.keys()))
        speech.updatePunctuationLevel()

    def updateBraille(self, obj, extraRegion=None):
        """Updates the braille display to show the give object.

        Arguments:
        - obj: the Accessible
        - extra: extra Region to add to the end
        """

        if not obj:
            return

        self.clearBraille()

        line = self.getNewBrailleLine()
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
        self.addBrailleRegionsToLine(result[0], line)

        if extraRegion:
            self.addBrailleRegionToLine(extraRegion, line)

        if extraRegion:
            self.setBrailleFocus(extraRegion)
        else:
            self.setBrailleFocus(result[1])

        self.refreshBraille(True)

    ########################################################################
    #                                                                      #
    # INPUT EVENT HANDLERS (AKA ORCA COMMANDS)                             #
    #                                                                      #
    ########################################################################

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
        self.presentMessage(_("Bypass mode enabled."))
        orca_state.bypassNextCommand = True
        return True

    def enterLearnMode(self, inputEvent=None):
        """Turns learn mode on.  The user must press the escape key to exit
        learn mode.

        Returns True to indicate the input event has been consumed.
        """

        if orca_state.learnModeEnabled:
            return True

        self.speakMessage(
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
        self.displayBrailleMessage(_("Learn mode.  Press escape to exit."))
        orca_state.learnModeEnabled = True
        return True

    def exitLearnMode(self, inputEvent=None):
        """Turns learn mode off.

        Returns True to indicate the input event has been consumed.
        """

        if not orca_state.learnModeEnabled:
            return False

        if isinstance(inputEvent, input_event.KeyboardEvent) \
           and not inputEvent.event_string == 'Escape':
            return False

        # Translators: Orca has a "Learn Mode" that will allow
        # the user to type any key on the keyboard and hear what
        # the effects of that key would be.  The effects might
        # be what Orca would do if it had a handler for the
        # particular key combination, or they might just be to
        # echo the name of the key if Orca doesn't have a handler.
        # Exiting learn mode puts the user back in normal operating
        # mode.
        #
        self.presentMessage(_("Exiting learn mode."))
        orca_state.learnModeEnabled = False

    def enterListShortcutsMode(self, inputEvent):
        """Turns list shortcuts mode on.  The user must press the escape key to
        exit list shortcuts mode. Key bindings for learn mode & list shortcuts
        mode are Orca+H & Orca+H(double click) respectively. So, while enabling
        list shortcuts mode, learn mode is enabled as a side effect. We start by
        disabling it.

        Returns True to indicate the input event has been consumed.
        """
        orca_state.learnModeEnabled = False
        if orca_state.listShortcutsModeEnabled:
            return True

        # Translators: Orca has a 'List Shortcuts' mode by which a user can
        # navigate through a list of the bound commands in Orca. This is the
        # message that is presented to the user as confirmation that this
        # mode has been entered.
        #
        mode = _("List shortcuts mode.")

        # Translators: Orca has a 'List Shortcuts' mode by which a user can
        # navigate through a list of the bound commands in Orca. Pressing 1
        # presents the commands/shortcuts available for all applications.
        # These are the "default" commands/shortcuts. Pressing 2 presents
        # commands/shortcuts Orca provides for the application with focus.
        # The following message is presented to the user upon entering this
        # mode.
        #
        message = _("Press 1 for Orca's default shortcuts. Press 2 for " \
                    "Orca's shortcuts for the current application. " \
                    "Press escape to exit.")

        message = mode + " " + message
        self.speakMessage(message)
        self.displayBrailleMessage(message, -1, -1)
        orca_state.listShortcutsModeEnabled = True
        return True

    def exitListShortcutsMode(self, inputEvent=None):
        """Turns list shortcuts mode off.

        Returns True to indicate the input event has been consumed.
        """

        orca_state.listOfShortcuts = []
        orca_state.typeOfShortcuts = ""
        orca_state.ptrToShortcut = -1
        orca_state.listShortcutsModeEnabled = False

        # Translators: Orca has a "List Shortcuts Mode" that allows the user to
        # list a group of keyboard shortcuts. Pressing 1 makes it possible for
        # the user to navigate amongst a list of global ("default") commands.
        # Pressing 2 allows the user to navigate amongst Orca commands specific
        # to the application with focus. Escape exists this mode. This string
        # is the prompt which will be presented to the user in both speech and
        # braille upon exiting this mode.
        #
        message = _("Exiting list shortcuts mode.")
        self.presentMessage(message)
        return True

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

    def goToBookmark(self, inputEvent):
        """ Go to the bookmark indexed by inputEvent.hw_code.  Delegates to
        Bookmark.goToBookmark """
        bookmarks = self.getBookmarks()
        bookmarks.goToBookmark(inputEvent)

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

    def saveBookmarks(self, inputEvent):
        """ Save the bookmarks for this script. Delegates to
        Bookmark.saveBookmarks """
        bookmarks = self.getBookmarks()
        bookmarks.saveBookmarks(inputEvent)

    def panBrailleLeft(self, inputEvent=None, panAmount=0):
        """Pans the braille display to the left.  If panAmount is non-zero,
        the display is panned by that many cells.  If it is 0, the display
        is panned one full display width.  In flat review mode, panning
        beyond the beginning will take you to the end of the previous line.

        In focus tracking mode, the cursor stays at its logical position.
        In flat review mode, the review cursor moves to character
        associated with cell 0."""

        if self.flatReviewContext:
            if self.isBrailleBeginningShowing():
                self.flatReviewContext.goBegin(flat_review.Context.LINE)
                self.reviewPreviousCharacter(inputEvent)
            else:
                self.panBrailleInDirection(panAmount, panToLeft=True)

            # This will update our target cursor cell
            #
            self._setFlatReviewContextToBeginningOfBrailleDisplay()

            [charString, x, y, width, height] = \
                self.flatReviewContext.getCurrent(flat_review.Context.CHAR)
            self.drawOutline(x, y, width, height)

            self.targetCursorCell = 1
            self.updateBrailleReview(self.targetCursorCell)
        elif self.isBrailleBeginningShowing() and orca_state.locusOfFocus \
             and self.utilities.isTextArea(orca_state.locusOfFocus):

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
            self.panBrailleInDirection(panAmount, panToLeft=True)
            # We might be panning through a flashed message.
            #
            braille.resetFlashTimer()
            self.refreshBraille(False, stopFlash=False)

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
            if self.isBrailleEndShowing():
                self.flatReviewContext.goEnd(flat_review.Context.LINE)
                self.reviewNextCharacter(inputEvent)
            else:
                self.panBrailleInDirection(panAmount, panToLeft=False)

            # This will update our target cursor cell
            #
            self._setFlatReviewContextToBeginningOfBrailleDisplay()

            [charString, x, y, width, height] = \
                self.flatReviewContext.getCurrent(flat_review.Context.CHAR)

            self.drawOutline(x, y, width, height)

            self.targetCursorCell = 1
            self.updateBrailleReview(self.targetCursorCell)
        elif self.isBrailleEndShowing() and orca_state.locusOfFocus \
             and self.utilities.isTextArea(orca_state.locusOfFocus):
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
            self.panBrailleInDirection(panAmount, panToLeft=False)
            # We might be panning through a flashed message.
            #
            braille.resetFlashTimer()
            self.refreshBraille(False, stopFlash=False)

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

        self._setContractedBraille(inputEvent)
        return True

    def processRoutingKey(self, inputEvent=None):
        """Processes a cursor routing key."""

        braille.processRoutingKey(inputEvent)
        return True

    def processBrailleCutBegin(self, inputEvent=None):
        """Clears the selection and moves the caret offset in the currently
        active text area.
        """

        obj, caretOffset = self.getBrailleCaretContext(inputEvent)

        if caretOffset >= 0:
            self.utilities.clearTextSelection(obj)
            self.utilities.setCaretOffset(obj, caretOffset)

        return True

    def processBrailleCutLine(self, inputEvent=None):
        """Extends the text selection in the currently active text
        area and also copies the selected text to the system clipboard."""

        obj, caretOffset = self.getBrailleCaretContext(inputEvent)

        if caretOffset >= 0:
            self.utilities.adjustTextSelection(obj, caretOffset)
            texti = obj.queryText()
            startOffset, endOffset = texti.getSelection(0)
            from gi.repository import Gtk
            clipboard = Gtk.clipboard_get()
            clipboard.set_text(texti.getText(startOffset, endOffset))

        return True

    def routePointerToItem(self, inputEvent=None):
        """Moves the mouse pointer to the current item."""

        # Store the original location for scripts which want to restore
        # it later.
        #
        self.oldMouseCoordinates = self.utilities.absoluteMouseCoordinates()
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
                    # Translators: Orca has a command that allows the user to
                    # move the mouse pointer to the current object. This is a
                    # detailed message which will be presented if for some
                    # reason Orca cannot identify/find the current location.
                    #
                    full = _("Could not find current location.")
                    # Translators: Orca has a command that allows the user to
                    # move the mouse pointer to the current object. This is a
                    # brief message which will be presented if for some reason
                    # Orca cannot identify/find the current location.
                    #
                    brief = C_("location", "Not found")
                    self.presentMessage(full, brief)

        return True

    def presentStatusBar(self, inputEvent):
        """Speaks and brailles the contents of the status bar and/or default
        button of the window with focus.
        """

        obj = orca_state.locusOfFocus
        self.updateBraille(obj)
        voice = self.voices[settings.DEFAULT_VOICE]

        frame, dialog = self.utilities.frameAndDialog(obj)
        if frame:
            # In windows with lots of objects (Thunderbird, Firefox, etc.)
            # If we wait until we've checked for both the status bar and
            # a default button, there may be a noticable delay. Therefore,
            # speak the status bar info immediately and then go looking
            # for a default button.
            #
            msg = self.speechGenerator.generateStatusBar(frame)
            if msg:
                self.presentMessage(msg, voice=voice)

        window = dialog or frame
        if window:
            msg = self.speechGenerator.generateDefaultButton(window)
            if msg:
                self.presentMessage(msg, voice=voice)

    def presentTitle(self, inputEvent):
        """Speaks and brailles the title of the window with focus."""

        title = self.speechGenerator.generateTitle(orca_state.locusOfFocus)
        for (string, voice) in title:
            self.presentMessage(string, voice=voice)

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
            [defUser, defDict] = \
                self.utilities.stringToKeysAndDict(defAttributes)
            allAttributes = defDict

            charAttributes = text.getAttributes(caretOffset)
            if charAttributes[0]:
                [charList, charDict] = \
                    self.utilities.stringToKeysAndDict(charAttributes[0])

                # It looks like some applications like Evolution and Star
                # Office don't implement getDefaultAttributes(). In that
                # case, the best we can do is use the specific text
                # attributes for this character returned by getAttributes().
                #
                if allAttributes:
                    for key in list(charDict.keys()):
                        allAttributes[key] = charDict[key]
                else:
                    allAttributes = charDict

            # Get a dictionary of text attributes that the user cares about.
            #
            [userAttrList, userAttrDict] = self.utilities.stringToKeysAndDict(
                _settingsManager.getSetting('enabledSpokenTextAttributes'))

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
            if self.utilities.linkIndex(
                orca_state.locusOfFocus, caretOffset) >= 0:
                # Translators: this indicates that this piece of
                # text is a hypertext link.
                #
                speech.speak(_("link"))

        return True

    def reportScriptInfo(self, inputEvent=None):
        """Output useful information on the current script via speech
        and braille.  This information will be helpful to script writers.
        """

        return self.utilities.scriptInfo()

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
                    self.speakMessage(_("Could not find current location."))
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
                    # Translators: Orca has a command that allows the user to
                    # move the mouse pointer to the current object. This is a
                    # detailed message which will be presented if for some
                    # reason Orca cannot identify/find the current location.
                    #
                    full = _("Could not find current location.")
                    # Translators: Orca has a command that allows the user to
                    # move the mouse pointer to the current object. This is a
                    # brief message which will be presented if for some reason
                    # Orca cannot identify/find the current location.
                    #
                    brief = C_("location", "Not found")
                    self.presentMessage(full, brief)

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
                    wordString = self.utilities.adjustForRepeats(wordString)
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
            self.targetCursorCell = self.getBrailleCursorCell()

        return True

    def reviewNextItem(self, inputEvent):
        """Moves the flat review context to the next item.  Places
        the flat review cursor at the beginning of the item."""

        context = self.getFlatReviewContext()

        moved = context.goNext(flat_review.Context.WORD,
                               flat_review.Context.WRAP_LINE)

        if moved:
            self._reviewCurrentItem(inputEvent)
            self.targetCursorCell = self.getBrailleCursorCell()

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

    def reviewUnicodeCurrentCharacter(self, inputEvent):
        """Brailles and speaks unicode information about the current flat
        review character.
        """

        self._reviewCurrentCharacter(inputEvent, 3)
        self.lastReviewCurrentEvent = inputEvent

        return True

    def _reviewCurrentCharacter(self, inputEvent, speechType=1):
        """Presents the current flat review character via braille and speech.

        Arguments:
        - inputEvent - the current input event.
        - speechType - the desired presentation:
                       speak (1),
                       phonetic (2)
                       unicode value information (3)
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
                if lineString == "\n" and speechType != 3:
                    # Translators: "blank" is a short word to mean the
                    # user has navigated to an empty line.
                    #
                    speech.speak(_("blank"))
                elif speechType == 3:
                    self.speakUnicodeCharacter(charString)
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
            self.targetCursorCell = self.getBrailleCursorCell()

        return True

    def reviewEndOfLine(self, inputEvent):
        """Moves the flat review context to the end of the line.  Places
        the flat review cursor at the end of the line."""

        context = self.getFlatReviewContext()
        context.goEnd(flat_review.Context.LINE)

        self.reviewCurrentCharacter(inputEvent)
        self.targetCursorCell = self.getBrailleCursorCell()

        return True

    def reviewNextCharacter(self, inputEvent):
        """Moves the flat review context to the next character.  Places
        the flat review cursor at character."""

        context = self.getFlatReviewContext()

        moved = context.goNext(flat_review.Context.CHAR,
                               flat_review.Context.WRAP_LINE)

        if moved:
            self._reviewCurrentCharacter(inputEvent)
            self.targetCursorCell = self.getBrailleCursorCell()

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
                lineString = self.utilities.adjustForRepeats(lineString)
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
            self.targetCursorCell = self.getBrailleCursorCell()

        return True

    def reviewHome(self, inputEvent):
        """Moves the flat review context to the top left of the current
        window."""

        context = self.getFlatReviewContext()

        context.goBegin()

        self._reviewCurrentLine(inputEvent)
        self.targetCursorCell = self.getBrailleCursorCell()

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
            self.targetCursorCell = self.getBrailleCursorCell()

        return True

    def reviewBottomLeft(self, inputEvent):
        """Moves the flat review context to the beginning of the
        last line in the window.  Places the flat review cursor at
        the beginning of the line."""

        context = self.getFlatReviewContext()

        context.goEnd(flat_review.Context.WINDOW)
        context.goBegin(flat_review.Context.LINE)
        self._reviewCurrentLine(inputEvent)
        self.targetCursorCell = self.getBrailleCursorCell()

        return True

    def reviewEnd(self, inputEvent):
        """Moves the flat review context to the end of the
        last line in the window.  Places the flat review cursor
        at the end of the line."""

        context = self.getFlatReviewContext()
        context.goEnd()

        self._reviewCurrentLine(inputEvent)
        self.targetCursorCell = self.getBrailleCursorCell()

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

    def sayAll(self, inputEvent):
        try:
            clickCount = inputEvent.getClickCount()
        except:
            clickCount = 1
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

        elif self.utilities.isTextArea(orca_state.locusOfFocus):
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

    def toggleFlatReviewMode(self, inputEvent=None):
        """Toggles between flat review mode and focus tracking mode."""

        verbosity = _settingsManager.getSetting('speechVerbosityLevel')
        if self.flatReviewContext:
            if inputEvent and verbosity != settings.VERBOSITY_LEVEL_BRIEF:
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
                self.presentMessage(_("Leaving flat review."))
            self.drawOutline(-1, 0, 0, 0)
            self.flatReviewContext = None
            self.updateBraille(orca_state.locusOfFocus)
        else:
            if inputEvent and verbosity != settings.VERBOSITY_LEVEL_BRIEF:
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
                self.presentMessage(_("Entering flat review."))
            context = self.getFlatReviewContext()
            [wordString, x, y, width, height] = \
                     context.getCurrent(flat_review.Context.WORD)
            self.drawOutline(x, y, width, height)
            self._reviewCurrentItem(inputEvent, self.targetCursorCell)

        return True

    def toggleSilenceSpeech(self, inputEvent=None):
        """Toggle the silencing of speech.

        Returns True to indicate the input event has been consumed.
        """
        speech.stop()
        if _settingsManager.getSetting('silenceSpeech'):
            _settingsManager.setSetting('silenceSpeech', False)
            # Translators: this is a spoken prompt letting the user know
            # that speech synthesis has been turned back on.
            #
            self.presentMessage(_("Speech enabled."))
        else:
            # Translators: this is a spoken prompt letting the user know
            # that speech synthesis has been temporarily turned off.
            #
            self.presentMessage(_("Speech disabled."))
            _settingsManager.setSetting('silenceSpeech', True)
        return True

    def toggleSpeakingIndentationJustification(self, inputEvent=None):
        """Toggles the speaking of indentation and justification."""

        value = _settingsManager.getSetting('enableSpeechIndentation')
        _settingsManager.setSetting('enableSpeechIndentation', not value)
        if _settingsManager.getSetting('enableSpeechIndentation'):
            # Translators: This is a detailed message indicating that
            # indentation and justification will be spoken.
            #
            full = _("Speaking of indentation and justification enabled.")
            # Translators: This is a brief message that will be presented
            # to the user who has just enabled/disabled the speaking of
            # indentation and justification information.
            #
            brief = C_("indentation and justification", "Enabled")
        else:
            # Translators: This is a detailed message indicating that
            # indentation and justification will not be spoken.
            #
            full = _("Speaking of indentation and justification disabled.")
            # Translators: This is a brief message that will be presented
            # to the user who has just enabled/disabled the speaking of
            # indentation and justification information.
            #
            brief = C_("indentation and justification", "Disabled")

        self.presentMessage(full, brief)

        return True

    def cycleSpeakingPunctuationLevel(self, inputEvent=None):
        """ Cycle through the punctuation levels for speech. """

        currentLevel = _settingsManager.getSetting('verbalizePunctuationStyle')
        if currentLevel == settings.PUNCTUATION_STYLE_NONE:
            newLevel = settings.PUNCTUATION_STYLE_SOME
            # Translators: This detailed message will be presented as the
            # user cycles through the different levels of spoken punctuation.
            # The options are: All puntuation marks will be spoken, None
            # will be spoken, Most will be spoken, or Some will be spoken.
            #
            full = _("Punctuation level set to some.")
            # Translators: This brief message will be presented as the user
            # cycles through the different levels of spoken punctuation.
            # The options are: All puntuation marks will be spoken, None
            # will be spoken, Most will be spoken, or Some will be spoken.
            #
            brief = C_("spoken punctuation", "Some")
        elif currentLevel == settings.PUNCTUATION_STYLE_SOME:
            newLevel = settings.PUNCTUATION_STYLE_MOST
            # Translators: This detailed message will be presented as the
            # user cycles through the different levels of spoken punctuation.
            # The options are: All puntuation marks will be spoken, None
            # will be spoken, Most will be spoken, or Some will be spoken.
            #
            full = _("Punctuation level set to most.")
            # Translators: This brief message will be presented as the user
            # cycles through the different levels of spoken punctuation.
            # The options are: All puntuation marks will be spoken, None
            # will be spoken, Most will be spoken, or Some will be spoken.
            #
            brief = C_("spoken punctuation", "Most")
        elif currentLevel == settings.PUNCTUATION_STYLE_MOST:
            newLevel = settings.PUNCTUATION_STYLE_ALL
            # Translators: This detailed message will be presented as the
            # user cycles through the different levels of spoken punctuation.
            # The options are: All puntuation marks will be spoken, None
            # will be spoken, Most will be spoken, or Some will be spoken.
            #
            full = _("Punctuation level set to all.")
            # Translators: This brief message will be presented as the user
            # cycles through the different levels of spoken punctuation.
            # The options are: All puntuation marks will be spoken, None
            # will be spoken, Most will be spoken, or Some will be spoken.
            #
            brief = C_("spoken punctuation", "All")
        else:
            # the all case, so cycle to none.
            newLevel = settings.PUNCTUATION_STYLE_NONE
            # Translators: This detailed message will be presented as the
            # user cycles through the different levels of spoken punctuation.
            # The options are: All puntuation marks will be spoken, None
            # will be spoken, Most will be spoken, or Some will be spoken.
            #
            full = _("Punctuation level set to none.")
            # Translators: This brief message will be presented as the user
            # cycles through the different levels of spoken punctuation.
            # The options are: All puntuation marks will be spoken, None
            # will be spoken, Most will be spoken, or Some will be spoken.
            #
            brief = C_("spoken punctuation", "None")

        _settingsManager.setSetting('verbalizePunctuationStyle', newLevel)
        self.presentMessage(full, brief)
        speech.updatePunctuationLevel()
        return True

    def cycleKeyEcho(self, inputEvent=None):
        (newKey, newWord, newSentence) = (False, False, False)
        key = _settingsManager.getSetting('enableKeyEcho')
        word = _settingsManager.getSetting('enableEchoByWord')
        sentence = _settingsManager.getSetting('enableEchoBySentence')

        # check if we are in the none case.
        if (key, word, sentence) == (False, False, False):
            # cycle to key echo
            (newKey, newWord, newSentence) = (True, False, False)
            # Translators: Orca has an "echo" setting which allows
            # the user to configure what is spoken in response to a
            # key press. Given a user who typed "Hello world.":
            # - key echo: "H e l l o space w o r l d period"
            # - word echo: "Hello" spoken when the space is pressed;
            #   "world" spoken when the period is pressed.
            # - sentence echo: "Hello world" spoken when the period
            #   is pressed.
            # A user can choose to have no echo, one type of echo, or
            # multiple types of echo and can cycle through the various
            # levels quickly via a command.
            #
            full = _("Key echo set to key.")
            # Translators: Orca has an "echo" setting which allows
            # the user to configure what is spoken in response to a
            # key press. Given a user who typed "Hello world.":
            # - key echo: "H e l l o space w o r l d period"
            # - word echo: "Hello" spoken when the space is pressed;
            #   "world" spoken when the period is pressed.
            # - sentence echo: "Hello world" spoken when the period
            #   is pressed.
            # A user can choose to have no echo, one type of echo, or
            # multiple types of echo and can cycle through the various
            # levels quickly via a command. The following string is a
            # brief message which will be presented to the user who is
            # cycling amongst the various echo options.
            #
            brief = C_("key echo", "key")

        # The key echo only case
        elif (key, word, sentence) == (True, False, False):
            # cycle to word echo
            (newKey, newWord, newSentence) = (False, True, False)
            # Translators: Orca has an "echo" setting which allows
            # the user to configure what is spoken in response to a
            # key press. Given a user who typed "Hello world.":
            # - key echo: "H e l l o space w o r l d period"
            # - word echo: "Hello" spoken when the space is pressed;
            #   "world" spoken when the period is pressed.
            # - sentence echo: "Hello world" spoken when the period
            #   is pressed.
            # A user can choose to have no echo, one type of echo, or
            # multiple types of echo and can cycle through the various
            # levels quickly via a command.
            #
            full = _("Key echo set to word.")
            # Translators: Orca has an "echo" setting which allows
            # the user to configure what is spoken in response to a
            # key press. Given a user who typed "Hello world.":
            # - key echo: "H e l l o space w o r l d period"
            # - word echo: "Hello" spoken when the space is pressed;
            #   "world" spoken when the period is pressed.
            # - sentence echo: "Hello world" spoken when the period
            #   is pressed.
            # A user can choose to have no echo, one type of echo, or
            # multiple types of echo and can cycle through the various
            # levels quickly via a command. The following string is a
            # brief message which will be presented to the user who is
            # cycling amongst the various echo options.
            #
            brief = C_("key echo", "word")

        # the word only case
        elif (key, word, sentence) == (False, True, False):
            # cycle to sentence echo
            (newKey, newWord, newSentence) = (False, False, True)
            # Translators: Orca has an "echo" setting which allows
            # the user to configure what is spoken in response to a
            # key press. Given a user who typed "Hello world.":
            # - key echo: "H e l l o space w o r l d period"
            # - word echo: "Hello" spoken when the space is pressed;
            #   "world" spoken when the period is pressed.
            # - sentence echo: "Hello world" spoken when the period
            #   is pressed.
            # A user can choose to have no echo, one type of echo, or
            # multiple types of echo and can cycle through the various
            # levels quickly via a command.
            #
            full = _("Key echo set to sentence.")
            # Translators: Orca has an "echo" setting which allows
            # the user to configure what is spoken in response to a
            # key press. Given a user who typed "Hello world.":
            # - key echo: "H e l l o space w o r l d period"
            # - word echo: "Hello" spoken when the space is pressed;
            #   "world" spoken when the period is pressed.
            # - sentence echo: "Hello world" spoken when the period
            #   is pressed.
            # A user can choose to have no echo, one type of echo, or
            # multiple types of echo and can cycle through the various
            # levels quickly via a command. The following string is a
            # brief message which will be presented to the user who is
            # cycling amongst the various echo options.
            #
            brief = C_("key echo", "sentence")

        # the sentence only case
        elif (key, word, sentence) == (False, False, True):
            # cycle to word and key echo
            (newKey, newWord, newSentence) = (True, True, False)
            # Translators: Orca has an "echo" setting which allows
            # the user to configure what is spoken in response to a
            # key press. Given a user who typed "Hello world.":
            # - key echo: "H e l l o space w o r l d period"
            # - word echo: "Hello" spoken when the space is pressed;
            #   "world" spoken when the period is pressed.
            # - sentence echo: "Hello world" spoken when the period
            #   is pressed.
            # A user can choose to have no echo, one type of echo, or
            # multiple types of echo and can cycle through the various
            # levels quickly via a command.
            #
            full = _("Key echo set to key and word.")
            # Translators: Orca has an "echo" setting which allows
            # the user to configure what is spoken in response to a
            # key press. Given a user who typed "Hello world.":
            # - key echo: "H e l l o space w o r l d period"
            # - word echo: "Hello" spoken when the space is pressed;
            #   "world" spoken when the period is pressed.
            # - sentence echo: "Hello world" spoken when the period
            #   is pressed.
            # A user can choose to have no echo, one type of echo, or
            # multiple types of echo and can cycle through the various
            # levels quickly via a command. The following string is a
            # brief message which will be presented to the user who is
            # cycling amongst the various echo options.
            #
            brief = C_("key echo", "key and word")

        # the key and word case
        elif (key, word, sentence) == (True, True, False):
            # cycle to word and sentence echo
            (newKey, newWord, newSentence) = (False, True, True)
            # Translators: Orca has an "echo" setting which allows
            # the user to configure what is spoken in response to a
            # key press. Given a user who typed "Hello world.":
            # - key echo: "H e l l o space w o r l d period"
            # - word echo: "Hello" spoken when the space is pressed;
            #   "world" spoken when the period is pressed.
            # - sentence echo: "Hello world" spoken when the period
            #   is pressed.
            # A user can choose to have no echo, one type of echo, or
            # multiple types of echo and can cycle through the various
            # levels quickly via a command.
            #
            full = _("Key echo set to word and sentence.")
            # Translators: Orca has an "echo" setting which allows
            # the user to configure what is spoken in response to a
            # key press. Given a user who typed "Hello world.":
            # - key echo: "H e l l o space w o r l d period"
            # - word echo: "Hello" spoken when the space is pressed;
            #   "world" spoken when the period is pressed.
            # - sentence echo: "Hello world" spoken when the period
            #   is pressed.
            # A user can choose to have no echo, one type of echo, or
            # multiple types of echo and can cycle through the various
            # levels quickly via a command. The following string is a
            # brief message which will be presented to the user who is
            # cycling amongst the various echo options.
            #
            brief = C_("key echo", "word and sentence")

        # cycle round
        else:
            # cycle to none
            (newKey, newWord, newSentence) = (False, False, False)
            # Translators: Orca has an "echo" setting which allows
            # the user to configure what is spoken in response to a
            # key press. Given a user who typed "Hello world.":
            # - key echo: "H e l l o space w o r l d period"
            # - word echo: "Hello" spoken when the space is pressed;
            #   "world" spoken when the period is pressed.
            # - sentence echo: "Hello world" spoken when the period
            #   is pressed.
            # A user can choose to have no echo, one type of echo, or
            # multiple types of echo and can cycle through the various
            # levels quickly via a command.
            #
            full = _("Key echo set to None.")
            # Translators: Orca has an "echo" setting which allows
            # the user to configure what is spoken in response to a
            # key press. Given a user who typed "Hello world.":
            # - key echo: "H e l l o space w o r l d period"
            # - word echo: "Hello" spoken when the space is pressed;
            #   "world" spoken when the period is pressed.
            # - sentence echo: "Hello world" spoken when the period
            #   is pressed.
            # A user can choose to have no echo, one type of echo, or
            # multiple types of echo and can cycle through the various
            # levels quickly via a command. The following string is a
            # brief message which will be presented to the user who is
            # cycling amongst the various echo options.
            #
            brief = C_("key echo", "None")

        _settingsManager.setSetting('enableKeyEcho', newKey)
        _settingsManager.setSetting('enableEchoByWord', newWord)
        _settingsManager.setSetting('enableEchoBySentence', newSentence)
        self.presentMessage(full, brief)
        return True


    def toggleTableCellReadMode(self, inputEvent=None):
        """Toggles an indicator for whether we should just read the current
        table cell or read the whole row."""

        speakRow = _settingsManager.getSetting('readTableCellRow')
        _settingsManager.setSetting('readTableCellRow', not speakRow)
        if not speakRow:
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

        self.presentMessage(line)

        return True

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

    def printAppsHandler(self, inputEvent=None):
        """Prints a list of all applications to stdout."""

        self.utilities.printApps()
        return True

    def printAncestryHandler(self, inputEvent=None):
        """Prints the ancestry for the current locusOfFocus"""

        self.utilities.printAncestry(orca_state.locusOfFocus)
        return True

    def printHierarchyHandler(self, inputEvent=None):
        """Prints the application for the current locusOfFocus"""

        if orca_state.locusOfFocus:
            self.utilities.printHierarchy(
                orca_state.locusOfFocus.getApplication(),
                orca_state.locusOfFocus)

        return True

    def cycleDebugLevel(self, inputEvent=None):
        levels = [debug.LEVEL_ALL, "all",
                  debug.LEVEL_FINEST, "finest",
                  debug.LEVEL_FINER, "finer",
                  debug.LEVEL_FINE, "fine",
                  debug.LEVEL_CONFIGURATION, "configuration",
                  debug.LEVEL_INFO, "info",
                  debug.LEVEL_WARNING, "warning",
                  debug.LEVEL_SEVERE, "severe",
                  debug.LEVEL_OFF, "off"]

        try:
            levelIndex = levels.index(debug.debugLevel) + 2
        except:
            levelIndex = 0
        else:
            if levelIndex >= len(levels):
                levelIndex = 0

        debug.debugLevel = levels[levelIndex]
        briefMessage = levels[levelIndex + 1]
        fullMessage =  "Debug level %s." % briefMessage
        orca_state.activeScript.presentMessage(fullMessage, briefMessage)

        return True

    ########################################################################
    #                                                                      #
    # AT-SPI OBJECT EVENT HANDLERS                                         #
    #                                                                      #
    ########################################################################

    def noOp(self, event):
        """Just here to capture events.

        Arguments:
        - event: the Event
        """
        pass

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

    def onCaretMoved(self, event):
        """Called whenever the caret moves.

        Arguments:
        - event: the Event
        """

        if not orca_state.locusOfFocus:
            return

        # Should the event source be the locusOfFocus?
        #
        try:
            role = orca_state.locusOfFocus.getRole()
        except (LookupError, RuntimeError):
            role = None
        if role in [pyatspi.ROLE_FRAME, pyatspi.ROLE_DIALOG]:
            frameApp = orca_state.locusOfFocus.getApplication()
            eventApp = event.source.getApplication()
            if frameApp == eventApp \
               and event.source.getState().contains(pyatspi.STATE_FOCUSED):
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

    def onFocus(self, event):
        """Called whenever an object gets focus.

        Arguments:
        - event: the Event
        """

        state = event.source.getState()
        if event.type.startswith("focus:") \
           and state.contains(pyatspi.STATE_FOCUSABLE) \
           and not state.contains(pyatspi.STATE_FOCUSED):
            return

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

    def onMouseButton(self, event):
        """Called whenever the user presses or releases a mouse button.

        Arguments:
        - event: the Event
        """

        mouseEvent = input_event.MouseButtonEvent(event)
        orca_state.lastInputEvent = mouseEvent

        if mouseEvent.pressed:
            speech.stop()
            return

        # If we've received a mouse button released event, then check if
        # there are and text selections for the locus of focus and speak
        # them.
        #
        obj = orca_state.locusOfFocus
        try:
            text = obj.queryText()
        except:
            return

        self.updateBraille(orca_state.locusOfFocus)
        textContents = self.utilities.allSelectedText(obj)[0]
        if not textContents:
            return

        utterances = []
        utterances.append(textContents)

        # Translators: when the user selects (highlights) text in
        # a document, Orca lets them know this.
        #
        utterances.append(C_("text", "selected"))
        speech.speak(utterances)

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
        # We are ignoring name changes in comboboxes that have focus
        # see bgo#617204
        ignoreList = [pyatspi.ROLE_DIALOG, pyatspi.ROLE_COMBO_BOX]
        if event.source and (event.source.getRole() in ignoreList) \
           and (event.source == orca_state.locusOfFocus):
            return

        # We do this because we can get name change events even if the
        # name doesn't change.  [[[TODO: WDW - I'm hesitant to rip the
        # above TODO out, though, because it's been in here for so long.]]]
        #
        try:
            name = event.source.name
        except:
            return
        if self.pointOfReference.get('oldName', None) == name:
            return

        self.pointOfReference['oldName'] = name
        self.visualAppearanceChanged(event, event.source)

    def onSelectionChanged(self, event):
        """Called when an object's selection changes.

        Arguments:
        - event: the Event
        """
        if not event or not event.source:
            return

        # Save the event source, if it is a menu or combo box. It will be
        # useful for optimizing componentAtDesktopCoords in the case that
        # the pointer is hovering over a menu item. The alternative is to
        # traverse the application's tree looking for potential moused-over
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
            self.visualAppearanceChanged(event, event.source)

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
           and not _settingsManager.getSetting('onlySpeakDisplayedText') \
           and orca_state.locusOfFocus:
            # If this selection state change is for the object which
            # currently has the locus of focus, and the last keyboard
            # event was Space, or we are a focused table cell and we
            # arrowed Down or Up and are now selected, then let the
            # user know the selection state.
            # See bugs #486908 and #519564 for more details.
            #
            announceState = False
            keyString, mods = self.utilities.lastKeyAndModifiers()
            state = orca_state.locusOfFocus.getState()
            if state.contains(pyatspi.STATE_FOCUSED) \
               and self.utilities.isSameObject(
                event.source, orca_state.locusOfFocus):

                if keyString == "space":
                    if mods & settings.CTRL_MODIFIER_MASK:
                        announceState = True
                    else:
                        # Weed out a bogus situation. If we are already
                        # selected and the user presses "space" again,
                        # we don't want to speak the intermediate
                        # "unselected" state.
                        #
                        eventState = event.source.getState()
                        selected = eventState.contains(pyatspi.STATE_SELECTED)
                        announceState = (selected and event.detail1)

                elif keyString in ["Down", "Up"] \
                     and event.source.getRole() == pyatspi.ROLE_TABLE_CELL \
                     and state.contains(pyatspi.STATE_SELECTED):
                    announceState = True

            if announceState:
                voice = self.voices.get(settings.SYSTEM_VOICE)
                if event.detail1:
                    # Translators: this object is now selected.
                    # Let the user know this.
                    #
                    #
                    speech.speak(C_("text", "selected"), voice, False)
                else:
                    # Translators: this object is now unselected.
                    # Let the user know this.
                    #
                    #
                    speech.speak(C_("text", "unselected"), voice, False)
                return

        if event.type.startswith("object:state-changed:focused"):
            iconified = False
            try:
                window = self.utilities.topLevelObject(event.source)
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
            if not event.type.startswith("object:state-changed:showing"):
                return

            keyString, mods = self.utilities.lastKeyAndModifiers()
            if keyString != "F1" \
               and not  _settingsManager.getSetting('presentToolTips'):
                return

            if event.detail1 == 1:
                self.presentToolTip(event.source)
                return

            if orca_state.locusOfFocus and keyString == "F1":
                obj = orca_state.locusOfFocus
                self.updateBraille(obj)
                utterances = self.speechGenerator.generateSpeech(obj)
                utterances.extend(
                    self.tutorialGenerator.getTutorial(obj, False))
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
                self.visualAppearanceChanged(event, event.source)

    def onTextAttributesChanged(self, event):
        """Called when an object's text attributes change. Right now this
        method is only to handle the presentation of spelling errors on
        the fly. Also note that right now, the Gecko toolkit is the only
        one to present this information to us.

        Arguments:
        - event: the Event
        """

        verbosity = _settingsManager.getSetting('speechVerbosityLevel')
        if verbosity == settings.VERBOSITY_LEVEL_VERBOSE \
           and self.utilities.isSameObject(
                event.source, orca_state.locusOfFocus):
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

            if self.utilities.isWordMisspelled(
                    event.source, prevWordAndOffsets[1] ) \
               or self.utilities.isWordMisspelled(
                    event.source, nextWordAndOffsets[1]):
                # Translators: this is to inform the user of the presence
                # of the red squiggly line which indicates that a given
                # word is not spelled correctly.
                #
                self.speakMessage(_("misspelled"))

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
        keyString, mods = self.utilities.lastKeyAndModifiers()
        if not keyString:
            return

        text = event.source.queryText()
        if keyString == "BackSpace":
            # Speak the character that has just been deleted.
            #
            character = event.any_data

        elif keyString == "Delete" \
             or (keyString == "D" and mods & settings.CTRL_MODIFIER_MASK):
            # Speak the character to the right of the caret after
            # the current right character has been deleted.
            #
            offset = text.caretOffset
            [character, startOffset, endOffset] = \
                text.getTextAtOffset(offset, pyatspi.TEXT_BOUNDARY_CHAR)

        else:
            return

        if self.utilities.linkIndex(event.source, text.caretOffset) >= 0:
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

        state = event.source.getState()            
        if event.source.getRole() == pyatspi.ROLE_TABLE_CELL \
           and not state.contains(pyatspi.STATE_FOCUSED) \
           and not state.contains(pyatspi.STATE_SELECTED):
            return

        self.updateBraille(event.source)

        if event.source.getRole() == pyatspi.ROLE_SPIN_BUTTON:
            # We cannot use the event.any_data due to a problem with
            # selected text in spin buttons. See bug #520395 for more
            # details.
            #
            [value, caret, start] = self.getTextLineAtCaret(event.source)
            speech.speak(value)
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
        string = event.any_data
        speakThis = False
        wasCommand = False
        try:
            role = event.source.getRole()
        except:
            role = None
        if isinstance(orca_state.lastInputEvent, input_event.MouseButtonEvent):
            speakThis = orca_state.lastInputEvent.button == "2"
        else:
            keyString, mods = self.utilities.lastKeyAndModifiers()
            wasCommand = mods & settings.COMMAND_MODIFIER_MASK
            if not wasCommand and keyString in ["Return", "Tab", "space"] \
               and role == pyatspi.ROLE_TERMINAL:
                wasCommand = True
            try:
                selections = event.source.queryText().getNSelections()
            except:
                selections = 0

            wasAutoComplete = role == pyatspi.ROLE_TEXT and selections
            if (string == " " and keyString == "space") or string == keyString:
                pass
            elif wasCommand or wasAutoComplete:
                speakThis = True
            elif role == pyatspi.ROLE_PASSWORD_TEXT \
                 and _settingsManager.getSetting('enableKeyEcho') \
                 and _settingsManager.getSetting('enablePrintableKeys'):
                # Echoing "star" is preferable to echoing the descriptive
                # name of the bullet that has appeared (e.g. "black circle")
                #
                string = "*"
                speakThis = True

        # Auto-completed, auto-corrected, auto-inserted, etc.
        #
        speakThis = speakThis or self.utilities.isAutoTextEvent(event)

        # We might need to echo this if it is a single character.
        #
        speakThis = speakThis \
                    or (_settingsManager.getSetting('enableEchoByCharacter') \
                        and string \
                        and role != pyatspi.ROLE_PASSWORD_TEXT \
                        and len(string.decode("UTF-8")) == 1)

        if speakThis:
            if string.decode("UTF-8").isupper():
                speech.speak(string, self.voices[settings.UPPERCASE_VOICE])
            else:
                speech.speak(string)

        if wasCommand:
            return

        try:
            text = event.source.queryText()
        except NotImplementedError:
            return

        offset = min(event.detail1, text.caretOffset - 1)
        previousOffset = offset - 1
        if (offset < 0 or previousOffset < 0):
            return

        [currentChar, startOffset, endOffset] = \
            text.getTextAtOffset(offset, pyatspi.TEXT_BOUNDARY_CHAR)
        [previousChar, startOffset, endOffset] = \
            text.getTextAtOffset(previousOffset, pyatspi.TEXT_BOUNDARY_CHAR)

        if _settingsManager.getSetting('enableEchoBySentence') \
           and self.utilities.isSentenceDelimiter(currentChar, previousChar):
            self.echoPreviousSentence(event.source)

        elif _settingsManager.getSetting('enableEchoByWord') \
             and self.utilities.isWordDelimiter(currentChar):
            self.echoPreviousWord(event.source)

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
                   and self.utilities.isSameObject(obj, relation.getTarget(0)):
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

        self.visualAppearanceChanged(event, event.source)
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
            self.clearBraille()

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

        # disable list notification  messages mode
        notification_messages.listNotificationMessagesModeEnabled = False

        # disable learn mode
        orca_state.learnModeEnabled = False

        # disable list shortcuts mode
        orca_state.listShortcutsModeEnabled = False
        orca_state.listOfShortcuts = []
        orca_state.typeOfShortcuts = ""

    ########################################################################
    #                                                                      #
    # Methods for presenting content                                       #
    #                                                                      #
    ########################################################################

    def _presentTextAtNewCaretPosition(self, event, otherObj=None):
        """Updates braille and outputs speech for the event.source or the
        otherObj."""

        obj = otherObj or event.source
        text = obj.queryText()

        # Update the Braille display - if we can just reposition
        # the cursor, then go for it.
        #
        brailleNeedsRepainting = True
        line = braille.getShowingLine()
        for region in line.regions:
            if isinstance(region, braille.Text) \
               and (region.accessible == obj):
                if region.repositionCursor():
                    self.refreshBraille(True)
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
        keyString, mods = self.utilities.lastKeyAndModifiers()
        if not keyString:
            return
        isControlKey = mods & settings.CTRL_MODIFIER_MASK
        isShiftKey = mods & settings.SHIFT_MODIFIER_MASK
        lastPos = self.pointOfReference.get("lastCursorPosition")
        hasLastPos = (lastPos != None)

        if keyString in ["Up", "Down"]:
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
                    if not self.utilities.isSameObject(lastPos[0], obj):
                        [startOffset, endOffset] = \
                            text.caretOffset, text.characterCount
                    else:
                        [startOffset, endOffset] = \
                            self.utilities.offsetsForPhrase(obj)
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
                    if not self.utilities.isSameObject(lastPos[0], obj):
                        [startOffset, endOffset] = 0, text.caretOffset
                    else:
                        [startOffset, endOffset] \
                            = self.utilities.offsetsForPhrase(obj)

                    if startOffset != endOffset:
                        self.sayPhrase(obj, startOffset, endOffset)

            else:
                [startOffset, endOffset] = self.utilities.offsetsForLine(obj)
                self.sayLine(obj)

        elif keyString in ["Left", "Right"]:
            # If the user has typed Control-Shift-Up or Control-Shift-Dowm,
            # then we want to speak the text that has just been selected
            # or unselected, otherwise if the user has typed Control-Left
            # or Control-Right, we speak the current word otherwise we speak
            # the character at the text cursor position.
            #
            inNewObj = hasLastPos \
                       and not self.utilities.isSameObject(lastPos[0], obj)

            if hasLastPos and not inNewObj and isShiftKey and isControlKey:
                [startOffset, endOffset] = self.utilities.offsetsForPhrase(obj)
                self.sayPhrase(obj, startOffset, endOffset)
            elif isControlKey and not isShiftKey:
                [startOffset, endOffset] = self.utilities.offsetsForWord(obj)
                if startOffset == endOffset:
                    self.sayCharacter(obj)
                else:
                    self.sayWord(obj)
            else:
                [startOffset, endOffset] = self.utilities.offsetsForChar(obj)
                self.sayCharacter(obj)

        elif keyString == "Page_Up":
            # If the user has typed Control-Shift-Page_Up, then we want
            # to speak the text that has just been selected or unselected,
            # otherwise if the user has typed Control-Page_Up, then we
            # speak the character to the right of the current text cursor
            # position otherwise we speak the current line.
            #
            if hasLastPos and isShiftKey and isControlKey:
                [startOffset, endOffset] = self.utilities.offsetsForPhrase(obj)
                self.sayPhrase(obj, startOffset, endOffset)
            elif isControlKey:
                [startOffset, endOffset] = self.utilities.offsetsForChar(obj)
                self.sayCharacter(obj)
            else:
                [startOffset, endOffset] = self.utilities.offsetsForLine(obj)
                self.sayLine(obj)

        elif keyString == "Page_Down":
            # If the user has typed Control-Shift-Page_Down, then we want
            # to speak the text that has just been selected or unselected,
            # otherwise if the user has just typed Page_Down, then we speak
            # the current line.
            #
            if hasLastPos and isShiftKey and isControlKey:
                [startOffset, endOffset] = self.utilities.offsetsForPhrase(obj)
                self.sayPhrase(obj, startOffset, endOffset)
            else:
                [startOffset, endOffset] = self.utilities.offsetsForLine(obj)
                self.sayLine(obj)

        elif keyString in ["Home", "End"]:
            # If the user has typed Shift-Home or Shift-End, then we want
            # to speak the text that has just been selected or unselected,
            # otherwise if the user has typed Control-Home or Control-End,
            # then we speak the current line otherwise we speak the character
            # to the right of the current text cursor position.
            #
            if hasLastPos and isShiftKey and not isControlKey:
                [startOffset, endOffset] = self.utilities.offsetsForPhrase(obj)
                self.sayPhrase(obj, startOffset, endOffset)
            elif isControlKey:
                [startOffset, endOffset] = self.utilities.offsetsForLine(obj)
                self.sayLine(obj)
            else:
                [startOffset, endOffset] = self.utilities.offsetsForChar(obj)
                self.sayCharacter(obj)

        else:
            startOffset = text.caretOffset
            endOffset = text.caretOffset

        self._saveLastCursorPosition(obj, text.caretOffset)
        self._saveSpokenTextRange(startOffset, endOffset)

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
            orca.setLocusOfFocus(None, context.obj, notifyScript=False)
            text.setCaretOffset(context.currentOffset)

        # If there is a selection, clear it. See bug #489504 for more details.
        #
        if text.getNSelections():
            text.setSelection(0, context.currentOffset, context.currentOffset)

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
        if self.utilities.isSameObject(lastPos[0], obj) \
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
                        self.utilities.selectedText(obj)

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
        if not self.utilities.isSentenceDelimiter(currentChar, previousChar):
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
            if self.utilities.isSentenceDelimiter(currentChar, previousChar):
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
            sentence = self.utilities.substring(obj, sentenceStartOffset + 1,
                                         sentenceEndOffset + 1)

        if self.utilities.linkIndex(obj, sentenceStartOffset + 1) >= 0:
            voice = self.voices[settings.HYPERLINK_VOICE]
        elif sentence.decode("UTF-8").isupper():
            voice = self.voices[settings.UPPERCASE_VOICE]
        else:
            voice = self.voices[settings.DEFAULT_VOICE]

        sentence = self.utilities.adjustForRepeats(sentence)
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
        if not self.utilities.isWordDelimiter(char):
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
            if self.utilities.isWordDelimiter(char):
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
            word = self.utilities.\
                substring(obj, wordStartOffset + 1, wordEndOffset + 1)

        if self.utilities.linkIndex(obj, wordStartOffset + 1) >= 0:
            voice = self.voices[settings.HYPERLINK_VOICE]
        elif word.decode("UTF-8").isupper():
            voice = self.voices[settings.UPPERCASE_VOICE]
        else:
            voice = self.voices[settings.DEFAULT_VOICE]

        word = self.utilities.adjustForRepeats(word)
        speech.speak(word, voice)

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

        if _settingsManager.getSetting('enableProgressBarUpdates'):
            makeAnnouncement = False
            verbosity = _settingsManager.getSetting('progressBarVerbosity')
            if verbosity == settings.PROGRESS_BAR_ALL:
                makeAnnouncement = True
            elif verbosity == settings.PROGRESS_BAR_WINDOW:
                makeAnnouncement = self.utilities.isSameObject(
                    self.utilities.topLevelObject(obj),
                    self.utilities.activeWindow())
            elif orca_state.locusOfFocus:
                makeAnnouncement = self.utilities.isSameObject( \
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
                for key, value in list(self.lastProgressBarTime.items()):
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
                if value.maximumValue == value.minimumValue:
                    # This is a busy indicator and not a real progress bar.
                    return
                percentValue = int((value.currentValue / \
                    (value.maximumValue - value.minimumValue)) * 100.0)

                if (currentTime - lastProgressBarTime) > \
                      _settingsManager.getSetting('progressBarUpdateInterval') \
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
                            for key in list(self.lastProgressBarTime.keys()):
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
                    self.speakMessage(line)

    def presentToolTip(self, obj):
        """
        Speaks the tooltip for the current object of interest.
        """

        # The tooltip is generally the accessible description. If
        # the description is not set, present the text that is
        # spoken when the object receives keyboard focus.
        #
        speechResult = brailleResult = None
        text = ""
        if obj.description:
            speechResult = brailleResult = obj.description
        else:
            speechResult = self.whereAmI.getWhereAmI(obj, True)
            if speechResult:
                brailleResult = speechResult[0]
        debug.println(debug.LEVEL_FINEST,
                      "presentToolTip: text='%s'" % speechResult)
        if speechResult:
            speech.speak(speechResult)
        if brailleResult:
            self.displayBrailleMessage(brailleResult)

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
        eventString, mods = self.utilities.lastKeyAndModifiers()
        if (mods & settings.SHIFT_MODIFIER_MASK) \
           and eventString in ["Right", "Down"]:
            offset -= 1

        character, startOffset, endOffset = \
            text.getTextAtOffset(offset, pyatspi.TEXT_BOUNDARY_CHAR)
        if not character or character == '\r':
            character = "\n"

        if self.utilities.linkIndex(obj, offset) >= 0:
            voice = self.voices[settings.HYPERLINK_VOICE]
        elif character.decode("UTF-8").isupper():
            voice = self.voices[settings.UPPERCASE_VOICE]
        else:
            voice = self.voices[settings.DEFAULT_VOICE]

        speakBlankLines = _settingsManager.getSetting('speakBlankLines')
        debug.println(debug.LEVEL_FINEST, \
            "sayCharacter: char=<%s>, startOffset=%d, " % \
            (character, startOffset))
        debug.println(debug.LEVEL_FINEST, \
            "caretOffset=%d, endOffset=%d, speakBlankLines=%s" % \
            (offset, endOffset, speakBlankLines))

        if character == "\n":
            line = text.getTextAtOffset(max(0, offset),
                                        pyatspi.TEXT_BOUNDARY_LINE_START)
            if not line[0] or line[0] == "\n":
                # This is a blank line. Announce it if the user requested
                # that blank lines be spoken.
                if speakBlankLines:
                    # Translators: "blank" is a short word to mean the
                    # user has navigated to an empty line.
                    #
                    self.speakMessage(_("blank"), interrupt=False)
                return

        if character in ["\n", "\r\n"]:
            # This is a blank line. Announce it if the user requested
            # that blank lines be spoken.
            if speakBlankLines:
                # Translators: "blank" is a short word to mean the
                # user has navigated to an empty line.
                #
                self.speakMessage(_("blank"), interrupt=False)
            return
        else:
            self.speakMisspelledIndicator(obj, offset)
            speech.speakCharacter(character, voice)

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
            (caretOffset, _settingsManager.getSetting('speakBlankLines')))

        if len(line) and line != "\n":
            if line.decode("UTF-8").isupper():
                voice = self.voices[settings.UPPERCASE_VOICE]
            else:
                voice = self.voices[settings.DEFAULT_VOICE]

            result = \
              self.speechGenerator.generateTextIndentation(obj, line=line)
            if result:
                self.speakMessage(result[0])
            line = self.utilities.adjustForLinks(obj, line, startOffset)
            line = self.utilities.adjustForRepeats(line)
            speech.speak(line, voice)
        else:
            # Speak blank line if appropriate.
            #
            self.sayCharacter(obj)

    def sayPhrase(self, obj, startOffset, endOffset):
        """Speaks the text of an Accessible object between the start and
        end offsets, unless the phrase is empty in which case it's ignored.

        Arguments:
        - obj: an Accessible object that implements the AccessibleText
               interface
        - startOffset: the start text offset.
        - endOffset: the end text offset.
        """

        phrase = self.utilities.substring(obj, startOffset, endOffset)

        if len(phrase) and phrase != "\n":
            if phrase.decode("UTF-8").isupper():
                voice = self.voices[settings.UPPERCASE_VOICE]
            else:
                voice = self.voices[settings.DEFAULT_VOICE]

            phrase = self.utilities.adjustForRepeats(phrase)
            speech.speak(phrase, voice)
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
        lastKey, mods = self.utilities.lastKeyAndModifiers()
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

        if self.utilities.linkIndex(obj, offset) >= 0:
            voice = self.voices[settings.HYPERLINK_VOICE]
        elif word.decode("UTF-8").isupper():
            voice = self.voices[settings.UPPERCASE_VOICE]
        else:
            voice = self.voices[settings.DEFAULT_VOICE]

        self.speakMisspelledIndicator(obj, startOffset)

        word = self.utilities.adjustForRepeats(word)
        orca_state.lastWord = word
        speech.speak(word, voice)

    def stopSpeechOnActiveDescendantChanged(self, event):
        """Whether or not speech should be stopped prior to setting the
        locusOfFocus in onActiveDescendantChanged.

        Arguments:
        - event: the Event

        Returns True if speech should be stopped; False otherwise.
        """

        if not event.any_data:
            return True

        # In an object which manages its descendants, the
        # 'descendants' may really be a single object which changes
        # its name. If the name-change occurs followed by the active
        # descendant changing (to the same object) we won't present
        # the locusOfFocus because it hasn't changed. Thus we need to
        # be sure not to cut of the presentation of the name-change
        # event.

        if orca_state.locusOfFocus == event.any_data:
            oldName = self.pointOfReference.get('oldName', '')
            if not oldName or event.any_data.name == oldName:
                return False

        if event.source == orca_state.locusOfFocus == event.any_data.parent:
            return False

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

        for key, value in list(self.attributeNamesDict.items()):
            if value == attribName:
                return key

        return attribName

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
            self.targetCursorCell = self.getBrailleCursorCell()

        return self.flatReviewContext

    def drawOutline(self, x, y, width, height):
        """Draws an outline around the accessible, erasing the last drawn
        outline in the process."""

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

        line = self.getNewBrailleLine()
        self.addBrailleRegionsToLine(regions, line)
        braille.setLines([line])
        self.setBrailleFocus(regionWithFocus, False)
        if regionWithFocus:
            self.panBrailleToOffset(regionWithFocus.brailleOffset \
                                    + regionWithFocus.cursorOffset)

        if self.justEnteredFlatReviewMode:
            self.refreshBraille(True, self.targetCursorCell)
            self.justEnteredFlatReviewMode = False
        else:
            self.refreshBraille(True, targetCursorCell)

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
                self.presentMessage(message)
            else:
                context.setCurrent(location.lineIndex, location.zoneIndex, \
                                   location.wordIndex, location.charIndex)
                self.reviewCurrentItem(None)
                self.targetCursorCell = self.getBrailleCursorCell()

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
        sayAllStyle = _settingsManager.getSetting('sayAllStyle')
        if sayAllStyle == settings.SAYALL_STYLE_SENTENCE:
            mode = pyatspi.TEXT_BOUNDARY_SENTENCE_END
        elif sayAllStyle == settings.SAYALL_STYLE_LINE:
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

                lineString = self.utilities.adjustForRepeats(lineString)
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
                if caretOffset == -1:
                    caretOffset = text.characterCount
                try:
                    [lineString, startOffset, endOffset] = text.getTextAtOffset(
                        caretOffset, pyatspi.TEXT_BOUNDARY_LINE_START)
                except:
                    return ["", 0, 0]

            # Sometimes we get the trailing line-feed-- remove it
            #
            content = lineString.decode("UTF-8")

            # It is important that these are in order.
            # In some circumstances we might get:
            # word word\r\n
            # so remove \n, and then remove \r.
            # See bgo#619332.
            #
            content = content.rstrip('\n')
            content = content.rstrip('\r')

        return [content.encode("UTF-8"), text.caretOffset, startOffset]

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
        for i in range(text.getNSelections()):
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

        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return

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
        eventStr, mods = self.utilities.lastKeyAndModifiers()
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
                    if self.utilities.isWordDelimiter(tmpStr[n-1]):
                        n -= 1
                        endOffset -= 1
                    else:
                        break
                n = 0
                while startOffset < endOffset:
                    if self.utilities.isWordDelimiter(tmpStr[n]):
                        n += 1
                        startOffset += 1
                    else:
                        break

        except:
            debug.printException(debug.LEVEL_FINEST)

        if not _settingsManager.getSetting('onlySpeakDisplayedText'):
            voice = self.voices.get(settings.SYSTEM_VOICE)
            if self.utilities.isTextSelected(obj, startOffset, endOffset):
                # Translators: when the user selects (highlights) text in
                # a document, Orca lets them know this.
                #
                speech.speak(C_("text", "selected"), voice, False)
            elif len(text.getText(startOffset, endOffset)):
                # Translators: when the user unselects
                # (unhighlights) text in a document, Orca lets
                # them know this.
                #
                speech.speak(C_("text", "unselected"), voice, False)

        self._saveLastTextSelections(text)

    def systemBeep(self):
        """Rings the system bell. This is really a hack. Ideally, we want
        a method that will present an earcon (any sound designated for the
        purpose of representing an error, event etc)
        """

        print("\a")

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

        verbosity = _settingsManager.getSetting('speechVerbosityLevel')
        if verbosity == settings.VERBOSITY_LEVEL_VERBOSE:
            try:
                text = obj.queryText()
            except:
                return
            # If we're on whitespace, we cannot be on a misspelled word.
            #
            charAndOffsets = \
                text.getTextAtOffset(offset, pyatspi.TEXT_BOUNDARY_CHAR)
            if not charAndOffsets[0].strip() \
               or self.utilities.isWordDelimiter(charAndOffsets[0]):
                orca_state.lastWordCheckedForSpelling = charAndOffsets[0]
                return

            wordAndOffsets = \
                text.getTextAtOffset(offset, pyatspi.TEXT_BOUNDARY_WORD_START)
            if self.utilities.isWordMisspelled(obj, offset) \
               and wordAndOffsets[0] != orca_state.lastWordCheckedForSpelling:
                # Translators: this is to inform the user of the presence
                # of the red squiggly line which indicates that a given
                # word is not spelled correctly.
                #
                self.speakMessage(_("misspelled"))
            # Store this word so that we do not continue to present the
            # presence of the red squiggly as the user arrows amongst
            # the characters.
            #
            orca_state.lastWordCheckedForSpelling = wordAndOffsets[0]

    ############################################################################
    #                                                                          #
    # Presentation methods                                                     #
    # (scripts should not call methods in braille.py or speech.py directly)    #
    #                                                                          #
    ############################################################################

    def presentationInterrupt(self):
        """Convenience method to interrupt presentation of whatever is being
        presented at the moment."""

        speech.stop()
        braille.killFlash()

    def presentKeyboardEvent(self, event):
        """Convenience method to present the KeyboardEvent event. Returns True
        if we fully present the event; False otherwise."""

        braille.displayKeyEvent(event)
        orcaModifierPressed = event.isOrcaModifier() and event.isPressedKey()
        if event.isCharacterEchoable() and not orcaModifierPressed:
            return False
        if orca_state.learnModeEnabled:
            if event.isPrintableKey() and event.getClickCount() == 2:
                self.phoneticSpellCurrentItem(event.event_string)
                return True

        speech.speakKeyEvent(event)
        return True

    def presentMessage(self, fullMessage, briefMessage=None, voice=None):
        """Convenience method to speak a message and 'flash' it in braille.

        Arguments:
        - fullMessage: This can be a string or a list. This will be presented
          as the message for users whose flash or message verbosity level is
          verbose.
        - briefMessage: This can be a string or a list. This will be presented
          as the message for users whose flash or message verbosity level is
          brief. Note that providing no briefMessage will result in the full
          message being used for either. Callers wishing to present nothing as
          the briefMessage should set briefMessage to an empty string.
        - voice: The voice to use when speaking this message. By default, the
          "system" voice will be used.
        """

        if not fullMessage:
            return

        if briefMessage is None:
            briefMessage = fullMessage

        if _settingsManager.getSetting('enableSpeech'):
            if _settingsManager.getSetting('messageVerbosityLevel') \
                    == settings.VERBOSITY_LEVEL_BRIEF:
                message = briefMessage
            else:
                message = fullMessage
            if message:
                voice = voice or self.voices.get(settings.SYSTEM_VOICE)
                speech.speak(message, voice)

        if (_settingsManager.getSetting('enableBraille') \
             or _settingsManager.getSetting('enableBrailleMonitor')) \
           and _settingsManager.getSetting('enableFlashMessages'):
            if _settingsManager.getSetting('flashVerbosityLevel') \
                    == settings.VERBOSITY_LEVEL_BRIEF:
                message = briefMessage
            else:
                message = fullMessage
            if not message:
                return

            if isinstance(message[0], list):
                message = message[0]
            if isinstance(message, list):
                message = [i for i in message if isinstance(i, str)]
                message = " ".join(message)

            if _settingsManager.getSetting('flashIsPersistent'):
                duration = -1
            else:
                duration = _settingsManager.getSetting('brailleFlashTime')

            braille.displayMessage(message, flashTime=duration)

    # [[[TODO - JD: Soon I'll add a check to only do the braille
    # presentation if the user has braille or the braille monitor
    # enabled. For now, the easiest way to regression test these
    # changes is to always present braille.]]]

    @staticmethod
    def addBrailleRegionToLine(region, line):
        """Adds the braille region to the line.

        Arguments:
        - region: a braille.Region (e.g. what is returned by the braille
          generator's generateBraille() method.
        - line: a braille.Line
        """

        line.addRegion(region)

    @staticmethod
    def addBrailleRegionsToLine(regions, line):
        """Adds the braille region to the line.

        Arguments:
        - regions: a series of braille.Region instances (a single instance
          being what is returned by the braille generator's generateBraille()
          method.
        - line: a braille.Line
        """

        line.addRegions(regions)

    @staticmethod
    def addToLineAsBrailleRegion(string, line):
        """Creates a Braille Region out of string and adds it to the line.

        Arguments:
        - string: the string to be displayed
        - line: a braille.Line
        """

        line.addRegion(braille.Region(string))

    @staticmethod
    def brailleRegionsFromStrings(strings):
        """Creates a list of braille regions from the list of strings.

        Arguments:
        - strings: a list of strings from which to create the list of
          braille Region instances

        Returns the list of braille Region instances
        """

        brailleRegions = []
        for string in strings:
            brailleRegions.append(braille.Region(string))

        return brailleRegions

    @staticmethod
    def clearBraille():
        """Clears the logical structure, but keeps the Braille display as is
        (until a refresh operation)."""

        braille.clear()

    @staticmethod
    def displayBrailleMessage(message, cursor=-1, flashTime=0):
        """Displays a single line, setting the cursor to the given position,
        ensuring that the cursor is in view.

        Arguments:
        - message: the string to display
        - cursor: the 0-based cursor position, where -1 (default) means no
          cursor
        - flashTime:  if non-0, the number of milliseconds to display the
          regions before reverting back to what was there before. A 0 means
          to not do any flashing.  A negative number means to display the
          message until some other message comes along or the user presses
          a cursor routing key.
        """

        braille.displayMessage(message, cursor, flashTime)

    @staticmethod
    def displayBrailleRegions(regionInfo, flashTime=0):
        """Displays a list of regions on a single line, setting focus to the
        specified region.  The regionInfo parameter is something that is
        typically returned by a call to braille_generator.generateBraille.

        Arguments:
        - regionInfo: a list where the first element is a list of regions
          to display and the second element is the region with focus (must
          be in the list from element 0)
        - flashTime:  if non-0, the number of milliseconds to display the
          regions before reverting back to what was there before. A 0 means
          to not do any flashing. A negative number means to display the
          message until some other message comes along or the user presses
          a cursor routing key.
        """

        braille.displayRegions(regionInfo, flashTime)

    def displayBrailleForObject(self, obj):
        """Convenience method for scripts combining the call to the braille
        generator for the script with the call to displayBrailleRegions.

        Arguments:
        - obj: the accessible object to display in braille
        """

        regions = self.brailleGenerator.generateBraille(obj)
        self.displayBrailleRegions(regions)

    @staticmethod
    def getBrailleCaretContext(event):
        """Gets the accesible and caret offset associated with the given
        event.  The event should have a BrlAPI event that contains an
        argument value that corresponds to a cell on the display.

        Arguments:
        - event: an instance of input_event.BrailleEvent.  event.event is
          the dictionary form of the expanded BrlAPI event.
        """

        return braille.getCaretContext(event)

    @staticmethod
    def getBrailleCursorCell():
        """Returns the value of position of the braille cell which has the
        cursor. A value of 0 means no cell has the cursor."""

        return braille.cursorCell

    @staticmethod
    def getNewBrailleLine(clearBraille=False, addLine=False):
        """Creates a new braille Line.

        Arguments:
        - clearBraille: Whether the display should be cleared.
        - addLine: Whether the line should be added to the logical display
          for painting.

        Returns the new Line.
        """

        if clearBraille:
            braille.clear()
        line = braille.Line()
        if addLine:
            braille.addLine(line)

        return line

    @staticmethod
    def getNewBrailleComponent(accessible, string, cursorOffset=0,
                               indicator='', expandOnCursor=False):
        """Creates a new braille Component.

        Arguments:
        - accessible: the accessible associated with this region
        - string: the string to be displayed
        - cursorOffset: a 0-based index saying where to draw the cursor
          for this Region if it gets focus

        Returns the new Component.
        """

        return braille.Component(accessible, string, cursorOffset,
                                 indicator, expandOnCursor)

    @staticmethod
    def getNewBrailleRegion(string, cursorOffset=0, expandOnCursor=False):
        """Creates a new braille Region.

        Arguments:
        - string: the string to be displayed
        - cursorOffset: a 0-based index saying where to draw the cursor
          for this Region if it gets focus

        Returns the new Region.
        """

        return braille.Region(string, cursorOffset, expandOnCursor)

    @staticmethod
    def getNewBrailleText(accessible, label="", eol="", startOffset=None,
                          endOffset=None):

        """Creates a new braille Text region.

        Arguments:
        - accessible: the accessible associated with this region and which
          implements AtkText
        - label: an optional label to display
        - eol: the endOfLine indicator

        Returns the new Text region.
        """

        return braille.Text(accessible, label, eol, startOffset, endOffset)

    @staticmethod
    def isBrailleBeginningShowing():
        """If True, the beginning of the line is showing on the braille
        display."""

        return braille.beginningIsShowing

    @staticmethod
    def isBrailleEndShowing():
        """If True, the end of the line is showing on the braille display."""

        return braille.endIsShowing

    @staticmethod
    def panBrailleInDirection(panAmount=0, panToLeft=True):
        """Pans the display to the left, limiting the pan to the beginning
        of the line being displayed.

        Arguments:
        - panAmount: the amount to pan.  A value of 0 means the entire
          width of the physical display.
        - panToLeft: if True, pan to the left; otherwise to the right

        Returns True if a pan actually happened.
        """

        if panToLeft:
            return braille.panLeft(panAmount)
        else:
            return braille.panRight(panAmount)

    @staticmethod
    def panBrailleToOffset(offset):
        """Automatically pan left or right to make sure the current offset
        is showing."""

        braille.panToOffset(offset)

    @staticmethod
    def presentItemsInBraille(items):
        """Method to braille a list of items. Scripts should call this
        method rather than handling the creation and displaying of a
        braille line directly.

        Arguments:
        - items: a list of strings to be presented
        """

        line = braille.getShowingLine()
        for item in items:
            line.addRegion(braille.Region(" " + item))

        braille.refresh()

    @staticmethod
    def refreshBraille(panToCursor=True, targetCursorCell=0, getLinkMask=True,
                       stopFlash=True):
        """This is the method scripts should use to refresh braille rather
        than calling self.refreshBraille() directly. The intent is to centralize
        such calls into as few places as possible so that we can easily and
        safely not perform braille-related functions for users who do not
        have braille and/or the braille monitor enabled.

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
          knowing that we will fail and/or it taking an unreasonable
          amount of time (AKA Gecko).
        - stopFlash: if True, kill any flashed message that may be showing.
        """

        braille.refresh(panToCursor, targetCursorCell, getLinkMask, stopFlash)

    @staticmethod
    def setBrailleFocus(region, panToFocus=True, getLinkMask=True):
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

        braille.setFocus(region, panToFocus, getLinkMask)

    @staticmethod
    def _setContractedBraille(event):
        """Turns contracted braille on or off based upon the event.

        Arguments:
        - event: an instance of input_event.BrailleEvent.  event.event is
          the dictionary form of the expanded BrlAPI event.
        """

        braille.setContractedBraille(event)

    ########################################################################
    #                                                                      #
    # Speech methods                                                       #
    # (scripts should not call methods in speech.py directly)              #
    #                                                                      #
    ########################################################################

    def speakMessage(self, string, voice=None, interrupt=True):
        """Method to speak a single string. Scripts should use this
        method rather than calling speech.speak directly.

        - string: The string to be spoken.
        - voice: The voice to use. By default, the "system" voice will
          be used.
        - interrupt: If True, any current speech should be interrupted
          prior to speaking the new text.
        """

        if _settingsManager.getSetting('enableSpeech'):
            voice = voice or self.voices.get(settings.SYSTEM_VOICE)
            speech.speak(string, voice, interrupt)

    @staticmethod
    def presentItemsInSpeech(items):
        """Method to speak a list of items. Scripts should call this
        method rather than handling the creation and speaking of
        utterances directly.

        Arguments:
        - items: a list of strings to be presented
        """

        utterances = []
        for item in items:
            utterances.append(item)

        speech.speak(utterances)

    def speakUnicodeCharacter(self, character):
        """ Speaks some information about an unicode character.
        At the Momment it just anounces the character unicode number but
        this information may be changed in the future

        Arguments:
        - character: the character to speak information of
        """
        # Translators: this is information about a unicode character
        # reported to the user.  The value is the unicode number value
        # of this character in hex.
        #
        speech.speak(_("Unicode %s") % \
                         self.utilities.unicodeValueString(character))

    def presentTime(self, inputEvent):
        """ Presents the current time. """
        timeFormat = _settingsManager.getSetting('presentTimeFormat')
        try:
            timeFormat = timeFormat.encode("UTF-8")
        except UnicodeDecodeError:
            pass

        message = time.strftime(timeFormat, time.localtime())
        self.presentMessage(message)
        return True

    def presentDate(self, inputEvent):
        """ Presents the current date. """
        dateFormat = _settingsManager.getSetting('presentDateFormat')
        try:
            dateFormat = dateFormat.encode("UTF-8")
        except UnicodeDecodeError:
            pass

        message = time.strftime(dateFormat, time.localtime())
        self.presentMessage(message)
        return True

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
state_change_notifiers[pyatspi.ROLE_LABEL]           = ("showing",
                                                        "expanded",
                                                        None)
state_change_notifiers[pyatspi.ROLE_NOTIFICATION]    = ("showing", None)
state_change_notifiers[pyatspi.ROLE_PUSH_BUTTON]     = ("expanded", None)
state_change_notifiers[pyatspi.ROLE_RADIO_BUTTON]    = ("checked", None)
state_change_notifiers[pyatspi.ROLE_TOGGLE_BUTTON]   = ("checked",
                                                        "pressed",
                                                        None)
state_change_notifiers[pyatspi.ROLE_TABLE_CELL]      = ("checked",
                                                        "expanded",
                                                        None)
state_change_notifiers[pyatspi.ROLE_LIST_ITEM]       = ("expanded", None)
