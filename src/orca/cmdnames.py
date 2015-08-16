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
SHOW_FIND_GUI = _("Opens the Find dialog.")

# Translators: the Orca "Find" dialog allows a user to search for text in a
# window and then move focus to that text. For example, they may want to find
# the "OK" button. This string is used for finding the next occurrence of a
# string.
FIND_NEXT = _("Searches for the next instance of a string.")

# Translators: the Orca "Find" dialog allows a user to search for text in a
# window and then move focus to that text. For example, they may want to find
# the "OK" button. This string is used for finding the previous occurrence of a
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

# Translators: the speech volume is how high or low in gain/volume the
# speech synthesis engine will generate speech.
INCREASE_SPEECH_VOLUME = _("Increases the speech volume.")

# Translators: the speech volume is how high or low in gain/volume the
# speech synthesis engine will generate speech.
DECREASE_SPEECH_VOLUME = _("Decreases the speech volume.")

# Translators: Orca allows the user to turn speech synthesis on or off.
#  We call it 'silencing'.
TOGGLE_SPEECH = _("Toggles the silencing of speech.")

# Translators: Orca's verbosity levels control how much (or how little)
# Orca will speak when presenting objects as the user navigates within
# applications and reads content. The levels can be toggled via command.
# This string describes that command.
TOGGLE_SPEECH_VERBOSITY = _("Toggles speech verbosity level.")

# Translators: this string is associated with the keyboard shortcut to quit
# Orca.
QUIT_ORCA = _("Quits the screen reader")

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

# Translators: Orca has a command to review previous chat room messages in
# speech and braille. This string to be translated is associated with the
# keyboard commands used to review those previous messages.
CHAT_PREVIOUS_MESSAGE = _("Speak and braille a previous chat room message.")

# Translators: In chat applications, it is often possible to see that a "buddy"
# is typing currently (e.g. via a keyboard icon or status text). Some users like
# to have this typing status announced by Orca; others find that announcement
# unpleasant. Therefore, it is a setting in Orca. This string to be translated
# is associated with the command to toggle typing status presentation on or off.
CHAT_TOGGLE_BUDDY_TYPING = \
    _("Toggle whether we announce when our buddies are typing.")

# Translators: Orca has a command to review previous chat room messages in
# speech and braille. Some users prefer to have this message history combined
# (e.g. the last ten messages which came in, no matter what room they came
# from). Other users prefer to have specific room history (e.g. the last ten
# messages from #a11y). Therefore, this is a setting in Orca. This string to be
# translated is associated with the command to toggle specific room history on
# or off.
CHAT_TOGGLE_MESSAGE_HISTORIES = \
    _("Toggle whether we provide chat room specific message " \
      "histories.")

# Translators: In chat applications, Orca automatically presents incoming
# messages in speech and braille. If a user is in multiple conversations or
# channels at the same time, it can be confusing to know what room or channel
# a given message came from just from hearing/reading it. For this reason, Orca
# has an option to present the name of the room first ("#a11y <joanie> hello!"
# instead of "<joanie> hello!"). This string to be translated is associated with
# the command to toggle room name presentation on or off.
CHAT_TOGGLE_ROOM_NAME_PREFIX = \
    _("Toggle whether we prefix chat room messages with " \
      "the name of the chat room.")

# Translators: this is a command for a button on a refreshable braille display
# (an external hardware device used by people who are blind). When pressing the
# button, the display scrolls to the left.
BRAILLE_LINE_LEFT = _("Line Left")

# Translators: this is a command for a button on a refreshable braille display
# (an external hardware device used by people who are blind). When pressing the
# button, the display scrolls to the right.
BRAILLE_LINE_RIGHT = _("Line Right")

# Translators: this is a command for a button on a refreshable braille display
# (an external hardware device used by people who are blind). When pressing the
# button, the display scrolls up.
BRAILLE_LINE_UP = _("Line Up")

# Translators: this is a command for a button on a refreshable braille display
# (an external hardware device used by people who are blind). When pressing the
# button, the display scrolls down.
BRAILLE_LINE_DOWN = _("Line Down")

# Translators: this is a command for a button on a refreshable braille display
# (an external hardware device used by people who are blind). When pressing the
# button, it instructs the braille display to freeze.
BRAILLE_FREEZE = _("Freeze")

# Translators: this is a command for a button on a refreshable braille display
# (an external hardware device used by people who are blind). When pressing the
# button, the display scrolls to the top left of the window.
BRAILLE_TOP_LEFT = _("Top Left")

# Translators: this is a command for a button on a refreshable braille display
# (an external hardware device used by people who are blind). When pressing the
# button, the display scrolls to the bottom left of the window.
BRAILLE_BOTTOM_LEFT = _("Bottom Left")

# Translators: this is a command for a button on a refreshable braille display
# (an external hardware device used by people who are blind). When pressing the
# button, the display scrolls to position containing the cursor.
BRAILLE_HOME = _("Cursor Position")

# Translators: this is a command for a button on a refreshable braille display
# (an external hardware device used by people who are blind). When pressing the
# button, the display toggles between six-dot braille and eight-dot braille.
BRAILLE_SIX_DOTS  = _("Six Dots")

# Translators: this is a command for a button on a refreshable braille display
# (an external hardware device used by people who are blind). This command
# represents a whole set of buttons known as cursor routing keys and are a way
# for a user to move the application's caret to the position indicated on the
# display.
BRAILLE_ROUTE_CURSOR = _("Cursor Routing")

# Translators: this is a command for a button on a refreshable braille display
# (an external hardware device used by people who are blind). This command
# represents the start of a selection operation. It is called "Cut Begin" to map
# to what BrlTTY users are used to: in character cell mode operation on virtual
# consoles, the act of copying text is erroneously called a "cut" operation.
BRAILLE_CUT_BEGIN = _("Cut Begin")

# Translators: this is a command for a button on a refreshable braille display
# (an external hardware device used by people who are blind). This command
# represents marking the endpoint of a selection. It is called "Cut Line" to map
# to what BrlTTY users are used to: in character cell mode operation on virtual
# consoles, the act of copying text is erroneously called a "cut" operation.
BRAILLE_CUT_LINE = _("Cut Line")

# Translators: this is a command which causes Orca to present the last received
# notification message.
NOTIFICATION_MESSAGES_LAST = _("Present last notification message.")

# Translators: this is a command which causes Orca to present a list of all the
# notification messages received.
NOTIFICATION_MESSAGES_LIST = _("Present notification messages list")

# Translators: this is a command which causes Orca to present the previous
# notification message.
NOTIFICATION_MESSAGES_PREVIOUS = _("Present previous notification message.")

# Translators: this is a command related to navigating within a document.
CARET_NAVIGATION_NEXT_CHAR = _("Goes to next character.")

# Translators: this is a command related to navigating within a document.
CARET_NAVIGATION_PREV_CHAR = _("Goes to previous character.")

# Translators: this is a command related to navigating within a document.
CARET_NAVIGATION_NEXT_WORD = _("Goes to next word.")

# Translators: this is a command related to navigating within a document.
CARET_NAVIGATION_PREV_WORD = _("Goes to previous word.")

# Translators: this is a command related to navigating within a document.
CARET_NAVIGATION_NEXT_LINE = _("Goes to next line.")

# Translators: this is a command related to navigating within a document.
CARET_NAVIGATION_PREV_LINE = _("Goes to previous line.")

# Translators: this is a command related to navigating within a document.
CARET_NAVIGATION_FILE_START = _("Goes to the top of the file.")

# Translators: this is a command related to navigating within a document.
CARET_NAVIGATION_FILE_END = _("Goes to the bottom of the file.")

# Translators: this is a command related to navigating within a document.
CARET_NAVIGATION_LINE_START = _("Goes to the beginning of the line.")

# Translators: this is a command related to navigating within a document.
CARET_NAVIGATION_LINE_END = _("Goes to the end of the line.")

# Translators: this is a command related to navigating within a document.
CARET_NAVIGATION_NEXT_OBJECT = _("Goes to the next object.")

# Translators: this is a command related to navigating within a document.
CARET_NAVIGATION_PREV_OBJECT = _("Goes to the previous object.")

# Translators: this is for causing a collapsed combo box which was reached
# by Orca's caret navigation to be expanded.
CARET_NAVIGATION_EXPAND_COMBO_BOX = \
    _("Causes the current combo box to be expanded.")

# Translators: Gecko native caret navigation is where Firefox (or Thunderbird)
# itself controls how the arrow keys move the caret around HTML content. It's
# often broken, so Orca needs to provide its own support. As such, Orca offers
# the user the ability to toggle which application is controlling the caret.
CARET_NAVIGATION_TOGGLE = \
    _("Switches between native and screen-reader caret navigation.")

# Translators: A live region is an area of a web page that is periodically
# updated, e.g. stock ticker. http://www.w3.org/TR/wai-aria/terms#def_liveregion
# The "politeness" level is an indication of when the user wishes to be notified
# about a change to live region content. Examples include: never ("off"), when
# idle ("polite"), and when there is a change ("assertive"). Orca has several
# features to facilitate accessing live regions. This string refers to a command
# to cycle through the different "politeness" levels.
LIVE_REGIONS_ADVANCE_POLITENESS = _("Advance live region politeness setting.")

# Translators: A live region is an area of a web page that is periodically
# updated, e.g. stock ticker. http://www.w3.org/TR/wai-aria/terms#def_liveregion
# The "politeness" level is an indication of when the user wishes to be notified
# about a change to live region content. Examples include: never ("off"), when
# idle ("polite"), and when there is a change ("assertive"). Orca has several
# features to facilitate accessing live regions. This string refers to a command
# to turn off live regions by default.
LIVE_REGIONS_SET_POLITENESS_OFF = \
    _("Set default live region politeness level to off.")

# Translators: A live region is an area of a web page that is periodically
# updated, e.g. stock ticker. http://www.w3.org/TR/wai-aria/terms#def_liveregion
# This string refers to a command for reviewing up to nine stored previous live
# messages.
LIVE_REGIONS_REVIEW = _("Review live region announcement.")

# Translators: A live region is an area of a web page that is periodically
# updated, e.g. stock ticker. http://www.w3.org/TR/wai-aria/terms#def_liveregion
# This string refers to an Orca command which allows the user to toggle whether
# or not Orca pays attention to changes in live regions. Note that turning off
# monitoring of live events is NOT the same as turning the politeness level
# to "off". The user can opt to have no notifications presented (politeness
# level of "off") and still manually review recent updates to live regions via
# Orca commands for doing so -- as long as the monitoring of live regions is
# enabled.
LIVE_REGIONS_MONITOR = _("Monitor live regions.")

# Translators: hovering the mouse over certain objects on a web page causes a
# new object to appear such as a pop-up menu. This command will move the user
# to the object which just appeared as a result of the user hovering the mouse.
# If the user is already in the mouse over object, this command will hide the
# mouse over and return the user to the object he/she was in.
MOUSE_OVER_MOVE = _("Moves focus into and away from the current mouse over.")

# Translators: Orca allows you to dynamically define which row of a spreadsheet
# or table should be treated as containing column headers. This string refers to
# the command to set the row.
DYNAMIC_COLUMN_HEADER_SET = _("Set the row to use as dynamic column headers.")

# Translators: Orca allows you to dynamically define which row of a spreadsheet
# or table should be treated as containing column headers. This string refers to
# the command to unset the row so it is no longer treated as if it contained
# column headers.
DYNAMIC_COLUMN_HEADER_CLEAR = _("Clears the dynamic column headers.")

# Translators: Orca allows you to dynamically define which column of a
# spreadsheet or table should be treated as containing row headers. This
# string refers to the command to set the column.
DYNAMIC_ROW_HEADER_SET = _("Set the column to use as dynamic row headers.")

# Translators: Orca allows you to dynamically define which column of a
# spreadsheet or table should be treated as containing column headers. This
# string refers to the command to unset the column so it is no longer treated
# as if it contained row headers.
DYNAMIC_ROW_HEADER_CLEAR = _("Clears the dynamic row headers")

# Translators: This string refers to an Orca command. The "input line" refers
# to the place where one enters formulas for a spreadsheet.
PRESENT_INPUT_LINE = _("Presents the contents of the input line.")

# Translators: the structural navigation keys are designed to move the caret
# around the document content by object type. Thus H moves you to the next
# heading, Shift H to the previous heading, T to the next table, and so on.
# This feature needs to be toggle-able so that it does not interfere with normal
# writing functions.
STRUCTURAL_NAVIGATION_TOGGLE = _("Toggles structural navigation keys.")

# Translators: this is for navigating among blockquotes in a document.
BLOCKQUOTE_PREV = _("Goes to previous blockquote.")

# Translators: this is for navigating among blockquotes in a document.
BLOCKQUOTE_NEXT = _("Goes to next blockquote.")

# Translators: this is for navigating among blockquotes in a document.
BLOCKQUOTE_LIST = _("Displays a list of blockquotes.")

# Translators: this is for navigating among buttons in a document.
BUTTON_PREV = _("Goes to previous button.")

# Translators: this is for navigating among buttons in a document.
BUTTON_NEXT = _("Goes to next button.")

# Translators: this is for navigating among buttons in a document.
BUTTON_LIST = _("Displays a list of buttons.")

# Translators: this is for navigating among check boxes in a document.
CHECK_BOX_PREV = _("Goes to previous check box.")

# Translators: this is for navigating among check boxes in a document.
CHECK_BOX_NEXT = _("Goes to next check box.")

# Translators: this is for navigating among check boxes in a document.
CHECK_BOX_LIST = _("Displays a list of check boxes.")

# Translators: this is for navigating among clickable objects in a document.
# A "clickable" is a web element with an "onClick" handler.
CLICKABLE_PREV = _("Goes to previous clickable.")

# Translators: this is for navigating among clickable objects in a document.
# A "clickable" is a web element with an "onClick" handler.
CLICKABLE_NEXT = _("Goes to next clickable.")

# Translators: this is for navigating among clickable objects in a document.
# A "clickable" is a web element with an "onClick" handler.
CLICKABLE_LIST = _("Displays a list of clickables.")

# Translators: this is for navigating among combo boxes in a document.
COMBO_BOX_PREV = _("Goes to previous combo box.")

# Translators: this is for navigating among combo boxes in a document.
COMBO_BOX_NEXT = _("Goes to next combo box.")

# Translators: this is for navigating among combo boxes in a document.
COMBO_BOX_LIST = _("Displays a list of combo boxes.")

# Translators: this is for navigating among entries in a document.
ENTRY_PREV = _("Goes to previous entry.")

# Translators: this is for navigating among entries in a document.
ENTRY_NEXT = _("Goes to next entry.")

# Translators: this is for navigating among entries in a document.
ENTRY_LIST = _("Displays a list of entries.")

# Translators: this is for navigating among form fields in a document.
FORM_FIELD_PREV = _("Goes to previous form field.")

# Translators: this is for navigating among form fields in a document.
FORM_FIELD_NEXT = _("Goes to next form field.")

# Translators: this is for navigating among form fields in a document.
FORM_FIELD_LIST = _("Displays a list of form fields.")

# Translators: this is for navigating among headings (e.g. <h1>) in a document.
HEADING_PREV = _("Goes to previous heading.")

# Translators: this is for navigating among headings (e.g. <h1>) in a document.
HEADING_NEXT = _("Goes to next heading.")

# Translators: this is for navigating among headings (e.g. <h1>) in a document.
HEADING_LIST = _("Displays a list of headings.")

# Translators: this is for navigating among headings (e.g. <h1>) in a document.
# <h1> is a heading at level 1, <h2> is a heading at level 2, etc.
HEADING_AT_LEVEL_PREV = _("Goes to previous heading at level %d.")

# Translators: this is for navigating among headings (e.g. <h1>) in a document.
# <h1> is a heading at level 1, <h2> is a heading at level 2, etc.
HEADING_AT_LEVEL_NEXT = _("Goes to next heading at level %d.")

# Translators: this is for navigating among headings (e.g. <h1>) in a document.
# <h1> is a heading at level 1, <h2> is a heading at level 2, etc.
HEADING_AT_LEVEL_LIST = _("Displays a list of headings at level %d.")

# Translators: this is for navigating among images in a document.
IMAGE_PREV = _("Goes to previous image.")

# Translators: this is for navigating among images in a document.
IMAGE_NEXT = _("Goes to next image.")

# Translators: this is for navigating among images in a document.
IMAGE_LIST = _("Displays a list of images.")

# Translators: this is for navigating among ARIA landmarks in a document. ARIA
# role landmarks are the W3C defined HTML tag attribute 'role' used to identify
# important part of webpage like banners, main context, search etc.
LANDMARK_PREV = _("Goes to previous landmark.")

# Translators: this is for navigating among ARIA landmarks in a document. ARIA
# role landmarks are the W3C defined HTML tag attribute 'role' used to identify
# important part of webpage like banners, main context, search etc.
LANDMARK_NEXT = _("Goes to next landmark.")

# Translators: this is for navigating among ARIA landmarks in a document. ARIA
# role landmarks are the W3C defined HTML tag attribute 'role' used to identify
# important part of webpage like banners, main context, search etc.
LANDMARK_LIST = _("Displays a list of landmarks.")

# Translators: this is for navigating among large objects in a document.
# A 'large object' is a logical chunk of text, such as a paragraph, a list,
# a table, etc.
LARGE_OBJECT_PREV = _("Goes to previous large object.")

# Translators: this is for navigating among large objects in a document.
# A 'large object' is a logical chunk of text, such as a paragraph, a list,
# a table, etc.
LARGE_OBJECT_NEXT = _("Goes to next large object.")

# Translators: this is for navigating among large objects in a document.
# A 'large object' is a logical chunk of text, such as a paragraph, a list,
# a table, etc.
LARGE_OBJECT_LIST = _("Displays a list of large objects.")

# Translators: this is for navigating among links in a document.
LINK_PREV = _("Goes to previous link.")

# Translators: this is for navigating among links in a document.
LINK_NEXT = _("Goes to next link.")

# Translators: this is for navigating among links in a document.
LINK_LIST = _("Displays a list of links.")

# Translators: this is for navigating among lists in a document.
LIST_PREV = _("Goes to previous list.")

# Translators: this is for navigating among lists in a document.
LIST_NEXT = _("Goes to next list.")

# Translators: this is for navigating among lists in a document.
LIST_LIST = _("Displays a list of lists.")

# Translators: this is for navigating among list items in a document.
LIST_ITEM_PREV = _("Goes to previous list item.")

# Translators: this is for navigating among list items in a document.
LIST_ITEM_NEXT = _("Goes to next list item.")

# Translators: this is for navigating among list items in a document.
LIST_ITEM_LIST = _("Displays a list of list items.")

# Translators: this is for navigating among live regions in a document. A live
# region is an area of a web page that is periodically updated, e.g. a stock
# ticker. http://www.w3.org/TR/wai-aria/terms#def_liveregion
LIVE_REGION_PREV = _("Goes to previous live region.")

# Translators: this is for navigating among live regions in a document. A live
# region is an area of a web page that is periodically updated, e.g. a stock
# ticker. http://www.w3.org/TR/wai-aria/terms#def_liveregion
LIVE_REGION_NEXT = _("Goes to next live region.")

# Translators: this is for navigating among live regions in a document. A live
# region is an area of a web page that is periodically updated, e.g. a stock
# ticker. http://www.w3.org/TR/wai-aria/terms#def_liveregion
LIVE_REGION_LAST = _("Goes to the last live region which made an announcement.")

# Translators: this is for navigating among paragraphs in a document.
PARAGRAPH_PREV = _("Goes to previous paragraph.")

# Translators: this is for navigating among paragraphs in a document.
PARAGRAPH_NEXT = _("Goes to next paragraph.")

# Translators: this is for navigating among paragraphs in a document.
PARAGRAPH_LIST = _("Displays a list of paragraphs.")

# Translators: this is for navigating among radio buttons in a document.
RADIO_BUTTON_PREV = _("Goes to previous radio button.")

# Translators: this is for navigating among radio buttons in a document.
RADIO_BUTTON_NEXT = _("Goes to next radio button.")

# Translators: this is for navigating among radio buttons in a document.
RADIO_BUTTON_LIST = _("Displays a list of radio buttons.")

# Translators: this is for navigating among separators (e.g. <hr>) in a
# document.
SEPARATOR_PREV = _("Goes to previous separator.")

# Translators: this is for navigating among separators (e.g. <hr>) in a
# document.
SEPARATOR_NEXT = _("Goes to next separator.")

# Translators: this is for navigating among tables in a document.
TABLE_PREV = _("Goes to previous table.")

# Translators: this is for navigating among tables in a document.
TABLE_NEXT = _("Goes to next table.")

# Translators: this is for navigating among tables in a document.
TABLE_LIST = _("Displays a list of tables.")

# Translators: this is for navigating among table cells in a document.
TABLE_CELL_DOWN = _("Goes down one cell.")

# Translators: this is for navigating among table cells in a document.
TABLE_CELL_FIRST = _("Goes to the first cell in a table.")

# Translators: this is for navigating among table cells in a document.
TABLE_CELL_LAST = _("Goes to the last cell in a table.")

# Translators: this is for navigating among table cells in a document.
TABLE_CELL_LEFT = _("Goes left one cell.")

# Translators: this is for navigating among table cells in a document.
TABLE_CELL_RIGHT = _("Goes right one cell.")

# Translators: this is for navigating among table cells in a document.
TABLE_CELL_UP = _("Goes up one cell.")

# Translators: Orca has a number of commands that override the default
# behavior within an application. For instance, on a web page, "h" moves
# you to the next heading. What should happen when you press an "h" in
# an entry on a web page depends: If you want to resume reading content,
# "h" should move to the next heading; if you want to enter text, "h"
# should not not move you to the next heading. Similarly, if you are
# at the bottom of an entry and press Down arrow, should you leave the
# entry? Again, it depends on if you want to resume reading content or
# if you are editing the text in the entry. Because Orca doesn't know
# what you want to do, it has two modes: In browse mode, Orca treats
# key presses as commands to read the content; in focus mode, Orca treats
# key presses as something that should be handled by the focused widget.
# This string is associated with the Orca command to manually switch
# between these two modes.
TOGGLE_PRESENTATION_MODE = _("Switches between browse mode and focus mode.")

# Translators: (Please see the previous, detailed translator notes about
# Focus mode and Browse mode.) In order to minimize the amount of work Orca
# users need to do to switch between focus mode and browse mode, Orca attempts
# to automatically switch to the mode which is appropriate to the current
# web element. Sometimes, however, this automatic mode switching is not what
# the user wants. A good example being web apps which have their own keyboard
# navigation and use interaction model. As a result, Orca has a command which
# enables setting a "sticky" focus mode which disables all automatic toggling.
# This string is associated with the Orca command to enable sticky focus mode.
SET_FOCUS_MODE_STICKY = _("Enables sticky focus mode.")

# Translators: this is for navigating among unvisited links in a document.
UNVISITED_LINK_PREV = _("Goes to previous unvisited link.")

# Translators: this is for navigating among unvisited links in a document.
UNVISITED_LINK_NEXT = _("Goes to next unvisited link.")

# Translators: this is for navigating among unvisited links in a document.
UNVISITED_LINK_LIST = _("Displays a list of unvisited links.")

# Translators: this is for navigating among visited links in a document.
VISITED_LINK_PREV = _("Goes to previous visited link.")

# Translators: this is for navigating among visited links in a document.
VISITED_LINK_NEXT = _("Goes to next visited link.")

# Translators: this is for navigating among visited links in a document.
VISITED_LINK_LIST = _("Displays a list of visited links.")
