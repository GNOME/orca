# Orca
#
# Copyright 2004-2009 Sun Microsystems Inc.
# Copyright 2010-2013 The Orca Team
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

"""Command names which Orca presents in speech and/or braille. These
have been put in their own module so that we can present them in
the correct language when users change the synthesizer language
on the fly without having to reload a bunch of modules."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2004-2009 Sun Microsystems Inc." \
                "Copyright (c) 2010-2013 The Orca Team"
__license__   = "LGPL"

from .orca_i18n import _

# Translators: this command will move the mouse pointer to the current item
#  without clicking on it.             
ROUTE_POINTER_TO_ITEM = _("Routes the pointer to the current item.")

# Translators: the 'flat review' feature of Orca allows the blind user to
# explore the text in a window in a 2D fashion.  That is, Orca treats all
# the text from all objects in a window (e.g., buttons, labels, etc.) as a
# sequence of words in a sequence of lines.  The flat review feature allows
# the user to explore this text by the {previous,next} {line,word,character}.
# Left click means to generate a left mouse button click on the current item.
LEFT_CLICK_REVIEW_ITEM = _("Performs left click on current flat review item.")

# Translators: the 'flat review' feature of Orca allows the blind user to
# explore the text in a window in a 2D fashion.  That is, Orca treats all
# the text from all objects in a window (e.g., buttons, labels, etc.) as a
# sequence of words in a sequence of lines.  The flat review feature allows
# the user to explore this text by the {previous,next} {line,word,character}.
# Right click means to generate a right mouse button click on the current item.
RIGHT_CLICK_REVIEW_ITEM = _("Performs right click on current flat review item.")

# Translators: the Orca "SayAll" command allows the user to press a key and have
# the entire document in a window be automatically spoken to the user. If the
# user presses any key during a SayAll operation, the speech will be interrupted
# and the cursor will be positioned at the point where the speech was interrupted.
SAY_ALL = _("Speaks entire document.")

# Translators: the "Where am I" feature of Orca allows a user to press a key and
# then have information about their current context spoken and brailled to them.
# For example, the information may include the name of the current pushbutton
# with focus as well as its mnemonic.
WHERE_AM_I_BASIC = _("Performs the basic where am I operation.")

# Translators: the "Where am I" feature of Orca allows a user to press a key and
# then have information about their current context spoken and brailled to them.
# For example, the information may include the name of the current pushbutton
# with focus as well as its mnemonic.
WHERE_AM_I_DETAILED = _("Performs the detailed where am I operation.")

# Translators: This command will cause the window's status bar contents to be
# spoken.
PRESENT_STATUS_BAR = _("Speaks the status bar.")

# Translators: This command will cause the window's title to be spoken.
PRESENT_TITLE = _("Speaks the title bar.")

# Translators: the Orca "Find" dialog allows a user to search for text in a
# window and then move focus to that text. For example, they may want to find
# the "OK" button.
SHOW_FIND_GUI = _("Opens the Orca Find dialog.")

# Translators: the Orca "Find" dialog allows a user to search for text in a
# window and then move focus to that text. For example, they may want to find
# the "OK" button. This string is used for finding the next occurence of a
# string.
FIND_NEXT = _("Searches for the next instance of a string.")

# Translators: the Orca "Find" dialog allows a user to search for text in a
# window and then move focus to that text. For example, they may want to find
# the "OK" button. This string is used for finding the previous occurence of a
# string.
FIND_PREVIOUS = _("Searches for the previous instance of a string.")

# Translators: the 'flat review' feature of Orca allows the blind user to
# explore the text in a window in a 2D fashion.  That is, Orca treats all
# the text from all objects in a window (e.g., buttons, labels, etc.) as a
# sequence of words in a sequence of lines.  The flat review feature allows
# the user to explore this text by the {previous,next} {line,word,character}.
TOGGLE_FLAT_REVIEW = _("Enters and exits flat review mode.")

# Translators: the 'flat review' feature of Orca allows the blind user to
# explore the text in a window in a 2D fashion.  That is, Orca treats all
# the text from all objects in a window (e.g., buttons, labels, etc.) as a
# sequence of words in a sequence of lines.  The flat review feature allows
# the user to explore this text by the {previous,next} {line,word,character}.
# The home position is the beginning of the content in the window.
REVIEW_HOME = _("Moves flat review to the home position.")

# Translators: the 'flat review' feature of Orca allows the blind user to
# explore the text in a window in a 2D fashion.  That is, Orca treats all
# the text from all objects in a window (e.g., buttons, labels, etc.) as a
# sequence of words in a sequence of lines.  The flat review feature allows
# the user to explore this text by the {previous,next} {line,word,character}.
# The home position is the last bit of information in the window.
REVIEW_END = _("Moves flat review to the end position.")

# Translators: the 'flat review' feature of Orca allows the blind user to
# explore the text in a window in a 2D fashion.  That is, Orca treats all
# the text from all objects in a window (e.g., buttons, labels, etc.) as a
# sequence of words in a sequence of lines.  The flat review feature allows
# the user to explore this text by the {previous,next} {line,word,character}.
REVIEW_PREVIOUS_LINE = \
    _("Moves flat review to the beginning of the previous line.")

# Translators: the 'flat review' feature of Orca allows the blind user to
# explore the text in a window in a 2D fashion.  That is, Orca treats all
# the text from all objects in a window (e.g., buttons, labels, etc.) as a
# sequence of words in a sequence of lines.  The flat review feature allows
# the user to explore this text by the {previous,next} {line,word,character}.
REVIEW_CURRENT_LINE = _("Speaks the current flat review line.")

# Translators: the 'flat review' feature of Orca allows the blind user to
# explore the text in a window in a 2D fashion.  That is, Orca treats all
# the text from all objects in a window (e.g., buttons, labels, etc.) as a
# sequence of words in a sequence of lines.  The flat review feature allows
# the user to explore this text by the {previous,next} {line,word,character}.
# This particular command will cause Orca to spell the current line character
# by character.
REVIEW_SPELL_CURRENT_LINE = _("Spells the current flat review line.")

# Translators: the 'flat review' feature of Orca allows the blind user to
# explore the text in a window in a 2D fashion.  That is, Orca treats all
# the text from all objects in a window (e.g., buttons, labels, etc.) as a
# sequence of words in a sequence of lines.  The flat review feature allows
# the user to explore this text by the {previous,next} {line,word,character}.
# This particular command will cause Orca to spell the current line character
# by character phonetically, saying "Alpha" for "a", "Bravo" for "b" and so on.
REVIEW_PHONETIC_CURRENT_LINE = \
    _("Phonetically spells the current flat review line.")

# Translators: the 'flat review' feature of Orca allows the blind user to
# explore the text in a window in a 2D fashion.  That is, Orca treats all
# the text from all objects in a window (e.g., buttons, labels, etc.) as a
# sequence of words in a sequence of lines.  The flat review feature allows
# the user to explore this text by the {previous,next} {line,word,character}.
REVIEW_NEXT_LINE = _("Moves flat review to the beginning of the next line.")

# Translators: the 'flat review' feature of Orca allows the blind user to
# explore the text in a window in a 2D fashion.  That is, Orca treats all
# the text from all objects in a window (e.g., buttons, labels, etc.) as a
# sequence of words in a sequence of lines.  The flat review feature allows
# the user to explore this text by the {previous,next} {line,word,character}.
# Previous will go backwards in the window until you reach the top (i.e., it
# will wrap across lines if necessary).
REVIEW_PREVIOUS_ITEM = _("Moves flat review to the previous item or word.")

# Translators: the 'flat review' feature of Orca allows the blind user to
# explore the text in a window in a 2D fashion.  That is, Orca treats all
# the text from all objects in a window (e.g., buttons, labels, etc.) as a
# sequence of words in a sequence of lines.  The flat review feature allows
# the user to explore this text by the {previous,next} {line,word,character}.
# This command will speak the current word or item.
REVIEW_CURRENT_ITEM = _("Speaks the current flat review item or word.")

# Translators: the 'flat review' feature of Orca allows the blind user to
# explore the text in a window in a 2D fashion.  That is, Orca treats all
# the text from all objects in a window (e.g., buttons, labels, etc.) as a
# sequence of words in a sequence of lines.  The flat review feature allows
# the user to explore this text by the {previous,next} {line,word,character}.
# This particular command will cause Orca to spell the current word or item
# character by character.
REVIEW_SPELL_CURRENT_ITEM = _("Spells the current flat review item or word.")

# Translators: the 'flat review' feature of Orca allows the blind user to
# explore the text in a window in a 2D fashion.  That is, Orca treats all
# the text from all objects in a window (e.g., buttons, labels, etc.) as a
# sequence of words in a sequence of lines.  The flat review feature allows
# the user to explore this text by the {previous,next} {line,word,character}.
# This particular command will cause Orca to spell the current word or item
# character by character phonetically, saying "Alpha" for "a", "Bravo" for "b"
# and so on.
REVIEW_PHONETIC_CURRENT_ITEM = \
    _("Phonetically spells the current flat review item or word.")

# Translators: the 'flat review' feature of Orca allows the blind user to
# explore the text in a window in a 2D fashion.  That is, Orca treats all
# the text from all objects in a window (e.g., buttons, labels, etc.) as a
# sequence of words in a sequence of lines.  The flat review feature allows
# the user to explore this text by the {previous,next} {line,word,character}.
# Next will go forwards in the window until you reach the end (i.e., it
# will wrap across lines if necessary).
REVIEW_NEXT_ITEM = _("Moves flat review to the next item or word.")

# Translators: the 'flat review' feature of Orca allows the blind user to
# explore the text in a window in a 2D fashion.  That is, Orca treats all
# the text from all objects in a window (e.g., buttons, labels, etc.) as a
# sequence of words in a sequence of lines.  The flat review feature allows
# the user to explore this text by the {previous,next} {line,word,character}.
# Above in this case means geographically above, as if you drew a vertical
# line upward on the screen.
REVIEW_ABOVE = _("Moves flat review to the word above the current word.")

# Translators: the 'flat review' feature of Orca allows the blind user to
# explore the text in a window in a 2D fashion.  That is, Orca treats all
# the text from all objects in a window (e.g., buttons, labels, etc.) as a
# sequence of words in a sequence of lines.  The flat review feature allows
# the user to explore this text by the {previous,next} {line,word,character}.
# With respect to this command, the flat review object is typically something
# like a pushbutton, a label, or some other GUI widget. The 'speaks' means it
# will speak the text associated with the object.
REVIEW_CURRENT_ACCESSIBLE = _("Speaks the current flat review object.")

# Translators: the 'flat review' feature of Orca allows the blind user to
# explore the text in a window in a 2D fashion.  That is, Orca treats all
# the text from all objects in a window (e.g., buttons, labels, etc.) as a
# sequence of words in a sequence of lines.  The flat review feature allows
# the user to explore this text by the {previous,next} {line,word,character}.
# Below in this case means geographically below, as if you drew a vertical
# line downward on the screen.
REVIEW_BELOW = _("Moves flat review to the word below the current word.")

# Translators: the 'flat review' feature of Orca allows the blind user to
# explore the text in a window in a 2D fashion.  That is, Orca treats all
# the text from all objects in a window (e.g., buttons, labels, etc.) as a
# sequence of words in a sequence of lines.  The flat review feature allows
# the user to explore this text by the {previous,next} {line,word,character}.
# Previous will go backwards in the window until you reach the top (i.e., it
# will wrap across lines if necessary).
REVIEW_PREVIOUS_CHARACTER = _("Moves flat review to the previous character.")

# Translators: the 'flat review' feature of Orca allows the blind user to
# explore the text in a window in a 2D fashion.  That is, Orca treats all
# the text from all objects in a window (e.g., buttons, labels, etc.) as a
# sequence of words in a sequence of lines.  The flat review feature allows
# the user to explore this text by the {previous,next} {line,word,character}.
# This command will speak the current character
REVIEW_CURRENT_CHARACTER = _("Speaks the current flat review character.")

# Translators: the 'flat review' feature of Orca allows the blind user to
# explore the text in a window in a 2D fashion.  That is, Orca treats all
# the text from all objects in a window (e.g., buttons, labels, etc.) as a
# sequence of words in a sequence of lines.  The flat review feature allows
# the user to explore this text by the {previous,next} {line,word,character}.
# This particular command will cause Orca to present the character phonetically,
# saying "Alpha" for "a", "Bravo" for "b" and so on.
REVIEW_SPELL_CURRENT_CHARACTER = \
    _("Phonetically speaks the current flat review character.")

# Translators: the 'flat review' feature of Orca allows the blind user to
# explore the text in a window in a 2D fashion.  That is, Orca treats all
# the text from all objects in a window (e.g., buttons, labels, etc.) as a
# sequence of words in a sequence of lines.  The flat review feature allows
# the user to explore this text by the {previous,next} {line,word,character}.
# This particular command will cause Orca to present the character's unicode
# value.
REVIEW_UNICODE_CURRENT_CHARACTER = \
    _("Speaks unicode value of the current flat review character.")

# Translators: the 'flat review' feature of Orca allows the blind user to
# explore the text in a window in a 2D fashion.  That is, Orca treats all
# the text from all objects in a window (e.g., buttons, labels, etc.) as a
# sequence of words in a sequence of lines.  The flat review feature allows
# the user to explore this text by the {previous,next} {line,word,character}.
# Previous will go forwards in the window until you reach the end (i.e., it
# will wrap across lines if necessary).
REVIEW_NEXT_CHARACTER = _("Moves flat review to the next character.")

# Translators: the 'flat review' feature of Orca allows the blind user to
# explore the text in a window in a 2D fashion.  That is, Orca treats all
# the text from all objects in a window (e.g., buttons, labels, etc.) as a
# sequence of words in a sequence of lines.  The flat review feature allows
# the user to explore this text by the {previous,next} {line,word,character}.
# This command will move to and present the end of the line.
REVIEW_END_OF_LINE = _("Moves flat review to the end of the line.")

# Translators: the 'flat review' feature of Orca allows the blind user to
# explore the text in a window in a 2D fashion.  That is, Orca treats all
# the text from all objects in a window (e.g., buttons, labels, etc.) as a
# sequence of words in a sequence of lines.  The flat review feature allows
# the user to explore this text by the {previous,next} {line,word,character}.
# The bottom left is the bottom left of the window currently being reviewed.
REVIEW_BOTTOM_LEFT = _("Moves flat review to the bottom left.")

# Translators: the 'flat review' feature of Orca allows the blind user to
# explore the text in a window in a 2D fashion.  That is, Orca treats all
# the text from all objects in a window (e.g., buttons, labels, etc.) as a
# sequence of words in a sequence of lines.  The flat review feature allows
# the user to explore this text by the {previous,next} {line,word,character}.
# This command lets the user copy the contents currently being reviewed to the
# clipboard.
FLAT_REVIEW_COPY = _("Copies the contents under flat review to the clipboard.")

# Translators: the 'flat review' feature of Orca allows the blind user to
# explore the text in a window in a 2D fashion.  That is, Orca treats all
# the text from all objects in a window (e.g., buttons, labels, etc.) as a
# sequence of words in a sequence of lines.  The flat review feature allows
# the user to explore this text by the {previous,next} {line,word,character}.
# This command lets the user append the contents currently being reviewed to
# the existing contents of the clipboard.
FLAT_REVIEW_APPEND = \
    _("Appends the contents under flat review to the clipboard.")

# Translators: when users are navigating a table, they sometimes want the
# entire row of a table read; other times they just want the current cell
# to be presented to them.
TOGGLE_TABLE_CELL_READ_MODE = \
    _("Toggles whether to read just the current table cell or the whole row.")

# Translators: the attributes being presented are the text attributes, such as
# bold, italic, font name, font size, etc.
READ_CHAR_ATTRIBUTES = \
    _("Reads the attributes associated with the current text character.")

# Translators: a refreshable braille display is an external hardware device that
# presents braille characters to the user. There are a limited number of cells
# on the display (typically 40 cells).  Orca provides the feature to build up a
# longer logical line and allow the user to press buttons on the braille display
# so they can pan left and right over this line.
PAN_BRAILLE_LEFT = _("Pans the braille display to the left.")

# Translators: a refreshable braille display is an external hardware device that
# presents braille characters to the user. There are a limited number of cells
# on the display (typically 40 cells).  Orca provides the feature to build up a
# longer logical line and allow the user to press buttons on the braille display
# so they can pan left and right over this line.
PAN_BRAILLE_RIGHT = _("Pans the braille display to the right.")

# Translators: the 'flat review' feature of Orca allows the blind user to
# explore the text in a window in a 2D fashion.  That is, Orca treats all
# the text from all objects in a window (e.g., buttons, labels, etc.) as a
# sequence of words in a sequence of lines.  The flat review feature allows
# the user to explore this text by the {previous,next} {line,word,character}.
# Flat review is modal, and the user can be exploring the window without
# changing which object in the window which has focus. The feature used here
# will return the flat review to the object with focus.
GO_BRAILLE_HOME = _("Returns to object with keyboard focus.")

# Translators: braille can be displayed in many ways. Contracted braille
# provides a more efficient means to represent text, especially long
# documents. The feature used here is an option to toggle between contracted
# and uncontracted.
SET_CONTRACTED_BRAILLE = _("Turns contracted braille on and off.")

# Translators: hardware braille displays often have buttons near each braille
# cell. These are called cursor routing keys and are a way for a user to tell
# the machine they are interested in a particular character on the display.
PROCESS_ROUTING_KEY = _("Processes a cursor routing key.")

# Translators: this is used to indicate the start point of a text selection.
PROCESS_BRAILLE_CUT_BEGIN = _("Marks the beginning of a text selection.")

# Translators: this is used to indicate the end point of a text selection.
PROCESS_BRAILLE_CUT_LINE = _("Marks the end of a text selection.")

# Translators: Orca has a "Learn Mode" that will allow the user to type any key
# on the keyboard and hear what the effects of that key would be. The effects
# might be what Orca would do if it had a handler for the particular key
# combination, or they might just be to echo the name of the key if Orca doesn't
# have a handler.
ENTER_LEARN_MODE = _("Enters learn mode.  Press escape to exit learn mode.")

# Translators: Orca has a "List Shortcuts" mode that will allow the user to list
# a group of keyboard shortcuts. The Orca default shortcuts can be listed by
# pressing 1, and Orca shortcuts for the application under focus can be listed
# by pressing 2. User can press Up/ Down to navigate and hear the list, change
# to another list by pressing 1/2, and exit the "List Shortcuts" Mode by
# pressing Escape.
ENTER_LIST_SHORTCUTS_MODE = \
    _("Enters list shortcuts mode.  Press escape to exit list shortcuts mode.")

# Translators: the speech rate is how fast the speech synthesis engine will
# generate speech.
DECREASE_SPEECH_RATE = _("Decreases the speech rate.")

# Translators: the speech rate is how fast the speech synthesis engine will
# generate speech.
INCREASE_SPEECH_RATE = _("Increases the speech rate.")

# Translators: the speech pitch is how high or low in pitch/frequency the
# speech synthesis engine will generate speech.
DECREASE_SPEECH_PITCH = _("Decreases the speech pitch.")

# Translators: the speech pitch is how high or low in pitch/frequency the
# speech synthesis engine will generate speech.
INCREASE_SPEECH_PITCH = _("Increases the speech pitch.")

# Translators: Orca allows the user to turn speech synthesis on or off.
#  We call it 'silencing'.
TOGGLE_SPEECH = _("Toggles the silencing of speech.")

# Translators: this string is associated with the keyboard shortcut to quit
# Orca.
QUIT_ORCA = _("Quits Orca")

# Translators: the preferences configuration dialog is the dialog that allows
# users to set their preferences for Orca.
SHOW_PREFERENCES_GUI = _("Displays the preferences configuration dialog.")

# Translators: the preferences configuration dialog is the dialog that allows
# users to set their preferences for a specific application within Orca.
SHOW_APP_PREFERENCES_GUI = \
    _("Displays the application preferences configuration dialog.")

# Translators: Orca allows the user to enable/disable speaking of indentation
# and justification.
TOGGLE_SPOKEN_INDENTATION_AND_JUSTIFICATION = \
    _("Toggles the speaking of indentation and justification.")

# Translators: Orca allows users to cycle through punctuation levels. None,
# some, most, or all, punctuation will be spoken.
CYCLE_PUNCTUATION_LEVEL = _("Cycles to the next speaking of punctuation level.")

# Translators: Orca has a feature whereby users can set up different "profiles,"
# which are collection of settings which apply to a given task, such as a
# "Spanish" profile which would use Spanish text-to-speech and Spanish braille
# and selected when reading Spanish content. This string to be translated refers
# to an Orca command which makes it possible for users to quickly cycle amongst
# their saved profiles without having to get into a GUI.
CYCLE_SETTINGS_PROFILE = _("Cycles to the next settings profile.")

# Translators: Orca uses Speech Dispatcher to present content to users via text-
# to-speech. Speech Dispatcher has a feature to control how capital letters are
# presented: Do nothing at all, say the word 'capital' prior to presenting a
# capital letter, or play a tone which Speech Dispatcher refers to as a sound
# 'icon'. This string to be translated refers to an Orca command which makes it
# possible for users to quickly cycle amongst these alternatives without having
# to get into a GUI.
CYCLE_CAPITALIZATION_STYLE = _("Cycles to the next capitalization style.")

# Translators: Orca has an "echo" setting which allows the user to configure
# what is spoken in response to a key press. Given a user who typed "Hello
# world.":
# - key echo: "H e l l o space w o r l d period"
# - word echo: "Hello" spoken when the space is pressed; "world" spoken when
#   the period is pressed.
# - sentence echo: "Hello world" spoken when the period is pressed.
# A user can choose to have no echo, one type of echo, or multiple types of
# echo. The following string refers to a command that allows the user to quickly
# choose which type of echo is being used.
CYCLE_KEY_ECHO = _("Cycles to the next key echo level.")

# Translators: this is a debug message that Orca users will not normally see. It
# describes a debug routine that allows the user to adjust the level of debug
# information that Orca generates at run time.
CYCLE_DEBUG_LEVEL = _("Cycles the debug level at run time.")

# Translators: this command announces information regarding the relationship of
# the given bookmark to the current position. Note that in this context, the
# "bookmark" is storing the location of an accessible object, typically on a web
# page.
BOOKMARK_CURRENT_WHERE_AM_I = \
    _("Bookmark where am I with respect to current position.")

# Translators: this event handler cycles through the registered bookmarks and
# takes the user to the previous bookmark location. Note that in this context,
# the "bookmark" is storing the location of an accessible object, typically on
# a web page.
BOOKMARK_GO_TO_PREVIOUS = _("Go to previous bookmark location.")

# Translators: this command moves the user to the location stored at the bookmark.
# Note that in this context, the "bookmark" is storing the location of an
# accessible object, typically on a web page.
BOOKMARK_GO_TO = _("Go to bookmark.")

# Translators: this event handler cycles through the registered bookmarks and
# takes the user to the next bookmark location. Note that in this context, the
# "bookmark" is storing the location of an accessible object, typically on a web
# page.
BOOKMARK_GO_TO_NEXT = _("Go to next bookmark location.")

# Translators: this event handler binds an in-page accessible object location to
# the given input key command.
BOOKMARK_ADD = _("Add bookmark.")

# Translators: this event handler saves all bookmarks for the current application
# to disk.
BOOKMARK_SAVE = _("Save bookmarks.")

# Translators: Orca allows the item under the pointer to be spoken. This toggles
# the feature without the need to get into a GUI.
MOUSE_REVIEW_TOGGLE = _("Toggle mouse review mode.")

# Translators: Orca has a command to present the current time in speech and in
# braille.
PRESENT_CURRENT_TIME = _("Present current time.")

# Translators: Orca has a command to present the current date in speech and in
# braille.
PRESENT_CURRENT_DATE = _("Present current date.")

# Translators: Orca normally intercepts all keyboard commands and only passes
# them along to the current application when they are not Orca commands. This
# command causes the next command issued to be passed along to the current
# application, bypassing Orca's interception of it.
BYPASS_NEXT_COMMAND = \
    _("Passes the next command on to the current application.")
