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

"""Messages which Orca presents in speech and/or braille. These
have been put in their own module so that we can present them in
the correct language when users change the synthesizer language
on the fly without having to reload a bunch of modules."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2004-2009 Sun Microsystems Inc." \
                "Copyright (c) 2010-2013 The Orca Team"
__license__   = "LGPL"

from .orca_i18n import _, C_, ngettext
from .orca_platform import version

# Translators: This is presented when the user has navigated to an empty line.
BLANK = _("blank")

# Translators: This refers to font weight.
BOLD = _("bold")

# Translators: Orca normally intercepts all keyboard commands and only passes
# them along to the current application when they are not Orca commands. This
# command causes the next command issued to be passed along to the current
# application, bypassing Orca's interception of it.
BYPASS_MODE_ENABLED = _("Bypass mode enabled.")

# Translators: Orca uses Speech Dispatcher to present content to users via
# text-to-speech. Speech Dispatcher has a feature to control how capital
# letters are presented: Do nothing at all, say the word 'capital' prior to
# presenting a capital letter, or play a tone which Speech Dispatcher refers
# to as a sound 'icon'. This string to be translated refers to the brief/
# non-verbose output presented in response to the use of an Orca command which
# makes it possible for users to quickly cycle amongst these alternatives
# without having to get into a GUI.
CAPITALIZATION_ICON_BRIEF = C_("capitalization style", "icon")

# Translators: Orca uses Speech Dispatcher to present content to users via
# text-to-speech. Speech Dispatcher has a feature to control how capital
# letters are presented: Do nothing at all, say the word 'capital' prior to
# presenting a capital letter, or play a tone which Speech Dispatcher refers
# to as a sound 'icon'. This string to be translated refers to the full/verbose
# output presented in response to the use of an Orca command which makes it
# possible for users to quickly cycle amongst these alternatives without having
# to get into a GUI.
CAPITALIZATION_ICON_FULL = _("Capitalization style set to icon.")

# Translators: Orca uses Speech Dispatcher to present content to users via
# text-to-speech. Speech Dispatcher has a feature to control how capital
# letters are presented: Do nothing at all, say the word 'capital' prior to
# presenting a capital letter, or play a tone which Speech Dispatcher refers
# to as a sound 'icon'. This string to be translated refers to the brief/
# non-verbose output presented in response to the use of an Orca command which
# makes it possible for users to quickly cycle amongst these alternatives
# without having to get into a GUI.
CAPITALIZATION_NONE_BRIEF = C_("capitalization style", "none")

# Translators: Orca uses Speech Dispatcher to present content to users via
# text-to-speech. Speech Dispatcher has a feature to control how capital
# letters are presented: Do nothing at all, say the word 'capital' prior to
# presenting a capital letter, or play a tone which Speech Dispatcher refers
# to as a sound 'icon'. This string to be translated refers to the full/verbose
# output presented in response to the use of an Orca command which makes it
# possible for users to quickly cycle amongst these alternatives without having
# to get into a GUI.
CAPITALIZATION_NONE_FULL = _("Capitalization style set to none.")

# Translators: Orca uses Speech Dispatcher to present content to users via
# text-to-speech. Speech Dispatcher has a feature to control how capital
# letters are presented: Do nothing at all, say the word 'capital' prior to
# presenting a capital letter, or play a tone which Speech Dispatcher refers
# to as a sound 'icon'. This string to be translated refers to the brief/
# non-verbose output presented in response to the use of an Orca command which
# makes it possible for users to quickly cycle amongst these alternatives
# without having to get into a GUI.
CAPITALIZATION_SPELL_BRIEF = C_("capitalization style", "spell")

# Translators: Orca uses Speech Dispatcher to present content to users via
# text-to-speech. Speech Dispatcher has a feature to control how capital
# letters are presented: Do nothing at all, say the word 'capital' prior to
# presenting a capital letter, or play a tone which Speech Dispatcher refers
# to as a sound 'icon'. This string to be translated refers to the full/verbose
# output presented in response to the use of an Orca command which makes it
# possible for users to quickly cycle amongst these alternatives without having
# to get into a GUI.
CAPITALIZATION_SPELL_FULL = _("Capitalization style set to spell.")

# Translators: this is the name of a cell in a spreadsheet.
CELL = _("Cell %s")

# Translators: when the user selects (highlights) or unselects text in a
# document, Orca will speak information about what they have selected or
# unselected. This message is presented when the user selects the entire
# document by pressing Ctrl+A.
DOCUMENT_SELECTED_ALL = _("entire document selected")

# Translators: when the user selects (highlights) or unselects text in a
# document, Orca will speak information about what they have selected or
# unselected. This message is presented when the user selects from the
# current location to the end of the document by pressing Ctrl+Shift+End.
DOCUMENT_SELECTED_DOWN = _("document selected from cursor position")

# Translators: when the user selects (highlights) or unselects text in a
# document, Orca will speak information about what they have selected or
# unselected. This message is presented when the user unselects previously
# selected text by pressing Ctrl+Shift+End.
DOCUMENT_UNSELECTED_DOWN = _("document unselected from cursor position")

# Translators: when the user selects (highlights) or unselects text in a
# document, Orca will speak information about what they have selected or
# unselected. This message is presented when the user selects from the
# current location to the start of the document by pressing Ctrl+Shift+Home.
DOCUMENT_SELECTED_UP = _("document selected to cursor position")

# Translators: when the user selects (highlights) or unselects text in a
# document, Orca will speak information about what they have selected or
# unselected. This message is presented when the user unselects previously
# selected text by pressing Ctrl+Shift+Home.
DOCUMENT_UNSELECTED_UP = _("document unselected to cursor position")

# Translators: Orca allows you to dynamically define which row of a spreadsheet
# or table should be treated as containing column headers. This message is
# presented when the user sets the row to a particular row number.
DYNAMIC_COLUMN_HEADER_SET = _("Dynamic column header set for row %d")

# Translators: Orca allows you to dynamically define which row of a spreadsheet
# or table should be treated as containing column headers. This message is
# presented when the user unsets the row so it is no longer treated as if it
# contained column headers.
DYNAMIC_COLUMN_HEADER_CLEARED = _("Dynamic column header cleared.")

# Translators: Orca allows you to dynamically define which column of a
# spreadsheet or table should be treated as containing column headers. This
# message is presented when the user sets the column to a particular column
# number.
DYNAMIC_ROW_HEADER_SET = _("Dynamic row header set for column %s")

# Translators: Orca allows you to dynamically define which column of a
# spreadsheet or table should be treated as containing column headers. This
# message is presented when the user unsets the column so it is no longer
# treated as if it contained row headers.
DYNAMIC_ROW_HEADER_CLEARED = _("Dynamic row header cleared.")

# Translators: this is used to announce that the current input line in a
# spreadsheet is blank/empty.
EMPTY = _("empty")

# Translators: the 'flat review' feature of Orca allows the blind user to
# explore the text in a window in a 2D fashion.  That is, Orca treats all
# the text from all objects in a window (e.g., buttons, labels, etc.) as a
# sequence of words in a sequence of lines.  This message is presented to
# let the user know that he/she successfully appended the contents under
# flat review onto the existing contents of the clipboard.
FLAT_REVIEW_APPENDED = _("Appended contents to clipboard.")

# Translators: the 'flat review' feature of Orca allows the blind user to
# explore the text in a window in a 2D fashion.  That is, Orca treats all
# the text from all objects in a window (e.g., buttons, labels, etc.) as a
# sequence of words in a sequence of lines.  This message is presented to
# let the user know that he/she successfully copied the contents under flat
# review to the clipboard.
FLAT_REVIEW_COPIED = _("Copied contents to clipboard.")

# Translators: the 'flat review' feature of Orca allows the blind user to
# explore the text in a window in a 2D fashion.  That is, Orca treats all
# the text from all objects in a window (e.g., buttons, labels, etc.) as a
# sequence of words in a sequence of lines.  This message is presented to
# let the user know that he/she attempted to use a flat review command when
# not using flat review.
FLAT_REVIEW_NOT_IN = _("Not using flat review.")

# Translators: the 'flat review' feature of Orca allows the blind user to
# explore the text in a window in a 2D fashion.  That is, Orca treats all
# the text from all objects in a window (e.g., buttons, labels, etc.) as a
# sequence of words in a sequence of lines.  This message is presented to
# let the user know he/she just entered flat review.
FLAT_REVIEW_START = _("Entering flat review.")

# Translators: the 'flat review' feature of Orca allows the blind user to
# explore the text in a window in a 2D fashion.  That is, Orca treats all
# the text from all objects in a window (e.g., buttons, labels, etc.) as a
# sequence of words in a sequence of lines.  This message is presented to
# let the user know he/she just entered flat review.
FLAT_REVIEW_STOP = _("Leaving flat review.")

# Translators: this means a particular cell in a spreadsheet has a formula
# (e.g., "=sum(a1:d1)")
HAS_FORMULA = _("has formula")

# Translators: Orca has an "echo" setting which allows the user to configure
# what is spoken in response to a key press. Given a user who typed "Hello
# world.":
# - key echo: "H e l l o space w o r l d period"
# - word echo: "Hello" spoken when the space is pressed;
#   "world" spoken when the period is pressed.
# - sentence echo: "Hello world" spoken when the period
#   is pressed.
# A user can choose to have no echo, one type of echo, or multiple types of
# echo and can cycle through the various levels quickly via a command. The
# following string is a brief message which will be presented to the user who
# is cycling amongst the various echo options.
KEY_ECHO_KEY_BRIEF = C_("key echo", "key")

# Translators: Orca has an "echo" setting which allows the user to configure
# what is spoken in response to a key press. Given a user who typed "Hello
# world.":
# - key echo: "H e l l o space w o r l d period"
# - word echo: "Hello" spoken when the space is pressed;
#   "world" spoken when the period is pressed.
# - sentence echo: "Hello world" spoken when the period
#   is pressed.
# A user can choose to have no echo, one type of echo, or multiple types of
# echo and can cycle through the various levels quickly via a command.
KEY_ECHO_KEY_FULL = _("Key echo set to key.")

# Translators: Orca has an "echo" setting which allows the user to configure
# what is spoken in response to a key press. Given a user who typed "Hello
# world.":
# - key echo: "H e l l o space w o r l d period"
# - word echo: "Hello" spoken when the space is pressed;
#   "world" spoken when the period is pressed.
# - sentence echo: "Hello world" spoken when the period
#   is pressed.
# A user can choose to have no echo, one type of echo, or multiple types of
# echo and can cycle through the various levels quickly via a command. The
# following string is a brief message which will be presented to the user who
# is cycling amongst the various echo options.
KEY_ECHO_NONE_BRIEF = C_("key echo", "None")

# Translators: Orca has an "echo" setting which allows the user to configure
# what is spoken in response to a key press. Given a user who typed "Hello
# world.":
# - key echo: "H e l l o space w o r l d period"
# - word echo: "Hello" spoken when the space is pressed;
#   "world" spoken when the period is pressed.
# - sentence echo: "Hello world" spoken when the period
#   is pressed.
# A user can choose to have no echo, one type of echo, or multiple types of
# echo and can cycle through the various levels quickly via a command.
KEY_ECHO_NONE_FULL = _("Key echo set to None.")

# Translators: Orca has an "echo" setting which allows the user to configure
# what is spoken in response to a key press. Given a user who typed "Hello
# world.":
# - key echo: "H e l l o space w o r l d period"
# - word echo: "Hello" spoken when the space is pressed;
#   "world" spoken when the period is pressed.
# - sentence echo: "Hello world" spoken when the period
#   is pressed.
# A user can choose to have no echo, one type of echo, or multiple types of
# echo and can cycle through the various levels quickly via a command. The
# following string is a brief message which will be presented to the user who
# is cycling amongst the various echo options.
KEY_ECHO_KEY_AND_WORD_BRIEF = C_("key echo", "key and word")

# Translators: Orca has an "echo" setting which allows the user to configure
# what is spoken in response to a key press. Given a user who typed "Hello
# world.":
# - key echo: "H e l l o space w o r l d period"
# - word echo: "Hello" spoken when the space is pressed;
#   "world" spoken when the period is pressed.
# - sentence echo: "Hello world" spoken when the period
#   is pressed.
# A user can choose to have no echo, one type of echo, or multiple types of
# echo and can cycle through the various levels quickly via a command.
KEY_ECHO_KEY_AND_WORD_FULL = _("Key echo set to key and word.")

# Translators: Orca has an "echo" setting which allows the user to configure
# what is spoken in response to a key press. Given a user who typed "Hello
# world.":
# - key echo: "H e l l o space w o r l d period"
# - word echo: "Hello" spoken when the space is pressed;
#   "world" spoken when the period is pressed.
# - sentence echo: "Hello world" spoken when the period
#   is pressed.
# A user can choose to have no echo, one type of echo, or multiple types of
# echo and can cycle through the various levels quickly via a command. The
# following string is a brief message which will be presented to the user who
# is cycling amongst the various echo options.
KEY_ECHO_SENTENCE_BRIEF = C_("key echo", "sentence")

# Translators: Orca has an "echo" setting which allows the user to configure
# what is spoken in response to a key press. Given a user who typed "Hello
# world.":
# - key echo: "H e l l o space w o r l d period"
# - word echo: "Hello" spoken when the space is pressed;
#   "world" spoken when the period is pressed.
# - sentence echo: "Hello world" spoken when the period
#   is pressed.
# A user can choose to have no echo, one type of echo, or multiple types of
# echo and can cycle through the various levels quickly via a command.
KEY_ECHO_SENTENCE_FULL = _("Key echo set to sentence.")

# Translators: Orca has an "echo" setting which allows the user to configure
# what is spoken in response to a key press. Given a user who typed "Hello
# world.":
# - key echo: "H e l l o space w o r l d period"
# - word echo: "Hello" spoken when the space is pressed;
#   "world" spoken when the period is pressed.
# - sentence echo: "Hello world" spoken when the period
#   is pressed.
# A user can choose to have no echo, one type of echo, or multiple types of
# echo and can cycle through the various levels quickly via a command. The
# following string is a brief message which will be presented to the user who
# is cycling amongst the various echo options.
KEY_ECHO_WORD_BRIEF = C_("key echo", "word")

# Translators: Orca has an "echo" setting which allows the user to configure
# what is spoken in response to a key press. Given a user who typed "Hello
# world.":
# - key echo: "H e l l o space w o r l d period"
# - word echo: "Hello" spoken when the space is pressed;
#   "world" spoken when the period is pressed.
# - sentence echo: "Hello world" spoken when the period
#   is pressed.
# A user can choose to have no echo, one type of echo, or multiple types of
# echo and can cycle through the various levels quickly via a command.
KEY_ECHO_WORD_FULL = _("Key echo set to word.")

# Translators: Orca has an "echo" setting which allows the user to configure
# what is spoken in response to a key press. Given a user who typed "Hello
# world.":
# - key echo: "H e l l o space w o r l d period"
# - word echo: "Hello" spoken when the space is pressed;
#   "world" spoken when the period is pressed.
# - sentence echo: "Hello world" spoken when the period
#   is pressed.
# A user can choose to have no echo, one type of echo, or multiple types of
# echo and can cycle through the various levels quickly via a command. The
# following string is a brief message which will be presented to the user who
# is cycling amongst the various echo options.
KEY_ECHO_WORD_AND_SENTENCE_BRIEF = C_("key echo", "word and sentence")

# Translators: Orca has an "echo" setting which allows the user to configure
# what is spoken in response to a key press. Given a user who typed "Hello
# world.":
# - key echo: "H e l l o space w o r l d period"
# - word echo: "Hello" spoken when the space is pressed;
#   "world" spoken when the period is pressed.
# - sentence echo: "Hello world" spoken when the period
#   is pressed.
# A user can choose to have no echo, one type of echo, or multiple types of
# echo and can cycle through the various levels quickly via a command.
KEY_ECHO_WORD_AND_SENTENCE_FULL = _("Key echo set to word and sentence.")

# Translators: This brief message indicates that indentation and
# justification will be spoken.
INDENTATION_JUSTIFICATION_OFF_BRIEF = \
    C_("indentation and justification", "Disabled")

# Translators: This detailed message indicates that indentation and
# justification will not be spoken.
INDENTATION_JUSTIFICATION_OFF_FULL = \
    _("Speaking of indentation and justification disabled.")

# Translators: This brief message indicates that indentation and
# justification will be spoken.
INDENTATION_JUSTIFICATION_ON_BRIEF = \
    C_("indentation and justification", "Enabled")

# Translators: This detailed message indicates that indentation and
# justification will be spoken.
INDENTATION_JUSTIFICATION_ON_FULL = \
    _("Speaking of indentation and justification enabled.")

# Translators: Orca has a "Learn Mode" that will allow the user to type any key
# on the keyboard and hear what the effects of that key would be.  The effects
# might be what Orca would do if it had a handler for the particular key
# combination, or they might just be to echo the name of the key if Orca doesn't
# have a handler. This message is what is presented on the braille display when
# entering Learn Mode.
LEARN_MODE_START_BRAILLE = _("Learn mode.  Press escape to exit.")

# Translators: Orca has a "Learn Mode" that will allow the user to type any key
# on the keyboard and hear what the effects of that key would be.  The effects
# might be what Orca would do if it had a handler for the particular key
# combination, or they might just be to echo the name of the key if Orca doesn't
# have a handler. This message is what is spoken to the user when entering Learn
# Mode.
LEARN_MODE_START_SPEECH = \
    _("Entering learn mode.  Press any key to hear its function.  " \
      "To get a list of Orca shortcuts, press the Orca modifier " \
      "plus H twice quickly. To view the documentation, press F1. " \
      "To exit learn mode, press the escape key.")

# Translators: Orca has a "Learn Mode" that will allow the user to type any key
# on the keyboard and hear what the effects of that key would be.  The effects
# might be what Orca would do if it had a handler for the particular key
# combination, or they might just be to echo the name of the key if Orca doesn't
# have a handler. This message is what is presented in speech and braille when
# exiting Learn Mode.
LEARN_MODE_STOP = _("Exiting learn mode.")

# Translators: when the user selects (highlights) or unselects text in a
# document, Orca will speak information about what they have selected or
# unselected. This message is presented when the user selects from the
# current location to the start of the line by pressing Ctrl+Shift+Page_Up.
LINE_SELECTED_LEFT = _("line selected from start to previous cursor position")

# Translators: when the user selects (highlights) or unselects text in a
# document, Orca will speak information about what they have selected or
# unselected. This message is presented when the user selects from the
# current location to the end of the line by pressing Ctrl+Shift+Page_Down.
LINE_SELECTED_RIGHT = _("line selected to end from previous cursor position")

# Translators: this indicates that this piece of text is a hypertext link.
LINK = _("link")

# Translators: The following string instructs the user how to navigate amongst
# the list of commands presented in 'list shortcuts' mode as well as how to exit
# the list when finished.
LIST_SHORTCUTS_MODE_NAVIGATION = \
    _("Use Up and Down Arrow to navigate the list. Press Escape to exit.")

# Translators: This message is presented when the user is in 'list shortcuts'
# mode. This is the message we present when the user requested a list of
# application-specific shortcuts, but none could be found for that application.
LIST_SHORTCUTS_MODE_NO_RESULTS = _("No Orca shortcuts for %s found.")

# Translators: Orca has a 'List Shortcuts' mode by which a user can navigate
# through a list of the bound commands in Orca. This is the message that is
# presented to the user as confirmation that this mode has been entered.
LIST_SHORTCUTS_MODE_START = _("List shortcuts mode.")

# Translators: Orca has a 'List Shortcuts' mode by which a user can navigate
# through a list of the bound commands in Orca. This is the message that is
# presented to the user as confirmation that this mode has been exited.
LIST_SHORTCUTS_MODE_STOP = _("Exiting list shortcuts mode.")

# Translators: Orca has a 'List Shortcuts' mode by which a user can navigate
# through a list of the bound commands in Orca. Pressing 1 presents the
# commands/shortcuts available for all applications. These are the "default"
# commands/shortcuts. Pressing 2 presents commands/shortcuts Orca provides for
# the application with focus. The following message is presented to the user
# upon entering this  mode.
LIST_SHORTCUTS_MODE_TUTORIAL = \
    _("Press 1 for Orca's default shortcuts. Press 2 for " \
      "Orca's shortcuts for the current application. " \
      "Press escape to exit.")

# Translators: A live region is an area of a web page that is periodically
# updated, e.g. stock ticker. http://www.w3.org/TR/wai-aria/terms#def_liveregion
# Orca has several features to facilitate accessing live regions. This message
# is presented to inform the user that Orca's live region features have been
# turned off.
LIVE_REGIONS_OFF = _("Live region support is off")

# Translators: Orca has a command that allows the user to move the mouse pointer
# to the current object. This is a brief message which will be presented if for
# some reason Orca cannot identify/find the current location.
LOCATION_NOT_FOUND_BRIEF = C_("location", "Not found")

# Translators: Orca has a command that allows the user to move the mouse pointer
# to the current object. This is a detailed message which will be presented if
# for some reason Orca cannot identify/find the current location.
LOCATION_NOT_FOUND_FULL = _("Could not find current location.")

# Translators: This is to inform the user of the presence of the red squiggly
# line which indicates that a given word is not spelled correctly.
MISSPELLED = _("misspelled")

# Translators: Orca tries to provide more compelling output of the spell check
# dialog in some applications. The first thing it does is let the user know
# what the misspelled word is.
MISSPELLED_WORD = _("Misspelled word: %s")

# Translators: Orca tries to provide more compelling output of the spell check
# dialog in some applications. The second thing it does is give the phrase
# containing the misspelled word in the document. This is known as the context.
MISSPELLED_WORD_CONTEXT = _("Context is %s")

# Translators: Orca has a command that presents a list of structural navigation
# objects in a dialog box so that users can navigate more quickly than they
# could with native keyboard navigation. This is a message that will be
# presented to the user when an error (such as the operation timing out) kept us
# from getting these objects.
NAVIGATION_DIALOG_ERROR = _("Error: Could not create list of objects.")

# Translators: This is for navigating document content by moving from anchor to
# anchor. (An anchor is a named spot that one can jump to.) This is a detailed
# message which will be presented to the user if no more anchors can be found.
NO_MORE_ANCHORS = _("No more anchors.")

# Translators: This is for navigating document content by moving from blockquote
# to blockquote. This is a detailed message which will be presented to the user
# if no more blockquotes can be found.
NO_MORE_BLOCKQUOTES = _("No more blockquotes.")

# Translators: This is for navigating document content by moving from button
# to button. This is a detailed message which will be presented to the user
# if no more buttons can be found.
NO_MORE_BUTTONS = _("No more buttons.")

# Translators: This is for navigating document content by moving from check
# box to check box. This is a detailed message which will be presented to the
# user if no more check boxes can be found.
NO_MORE_CHECK_BOXES = _("No more check boxes.")

# Translators: This is for navigating document content by moving from 'large
# object' to 'large object'. A 'large object' is a logical chunk of text,
# such as a paragraph, a list, a table, etc. This is a detailed message which
# will be presented to the user if no more check boxes can be found.
NO_MORE_CHUNKS = _("No more large objects.")

# Translators: This is for navigating document content by moving from combo
# box to combo box. This is a detailed message which will be presented to the
# user if no more combo boxes can be found.
NO_MORE_COMBO_BOXES = _("No more combo boxes.")

# Translators: This is for navigating document content by moving from entry
# to entry. This is a detailed message which will be presented to the user
# if no more entries can be found.
NO_MORE_ENTRIES = _("No more entries.")

# Translators: This is for navigating document content by moving from form
# field to form field. This is a detailed message which will be presented to
# the user if no more form fields can be found.
NO_MORE_FORM_FIELDS = _("No more form fields.")

# Translators: This is for navigating document content by moving from heading
# to heading. This is a detailed message which will be presented to the user
# if no more headings can be found.
NO_MORE_HEADINGS = _("No more headings.")

# Translators: This is for navigating document content by moving from heading
# to heading at a particular level (i.e. only <h1> or only <h2>, etc.). This
# is a detailed message which will be presented to the user if no more headings
# at the desired level can be found.
NO_MORE_HEADINGS_AT_LEVEL = _("No more headings at level %d.")

# Translators: this is for navigating to the previous ARIA role landmark.
# ARIA role landmarks are the W3C defined HTML tag attribute 'role' used to
# identify important part of webpage like banners, main context, search etc.
# This is an indication that one was not found.
NO_LANDMARK_FOUND = _("No landmark found.")

# Translators: This is for navigating document content by moving from link to
# link (regardless of visited state). This is a detailed message which will be
# presented to the user if no more links can be found.
NO_MORE_LINKS = _("No more links.")

# Translators: This is for navigating document content by moving from bulleted/
# numbered list to bulleted/numbered list. This is a detailed message which will
# be presented to the user if no more lists can be found.
NO_MORE_LISTS = _("No more lists.")

# Translators: This is for navigating document content by moving from bulleted/
# numbered list item to bulleted/numbered list item. This is a detailed message
# which will be presented to the user if no more list items can be found.
NO_MORE_LIST_ITEMS = _("No more list items.")

# Translators: This is for navigating document content by moving from live
# region to live region. A live region is an area of a web page that is
# periodically updated, e.g. stock ticker. This is a detailed message which
# will be presented to the user if no more live regions can be found. For
# more info, see http://www.w3.org/TR/wai-aria/terms#def_liveregion
NO_MORE_LIVE_REGIONS = _("No more live regions.")

# Translators: This is for navigating document content by moving from paragraph
# to paragraph. This is a detailed message which will be presented to the user
# if no more paragraphs can be found.
NO_MORE_PARAGRAPHS = _("No more paragraphs.")

# Translators: This is for navigating document content by moving from radio
# button to radio button. This is a detailed message which will be presented to
# the user if no more radio buttons can be found.
NO_MORE_RADIO_BUTTONS = _("No more radio buttons.")

# Translators: This is for navigating document content by moving from separator
# to separator (e.g. <hr> tags). This is a detailed message which will be
# presented to the user if no more separators can be found.
NO_MORE_SEPARATORS = _("No more separators.")

# Translators: This is for navigating document content by moving from table to
# to table. This is a detailed message which will be presented to the user if
# no more tables can be found.
NO_MORE_TABLES = _("No more tables.")

# Translators: This is for navigating document content by moving from unvisited
# link to unvisited link. This is a detailed message which will be presented to
# the user if no more unvisited links can be found.
NO_MORE_UNVISITED_LINKS = _("No more unvisited links.")

# Translators: This is for navigating document content by moving from visited
# link to visited link. This is a detailed message which will be presented to
# the user if no more visited links can be found.
NO_MORE_VISITED_LINKS = _("No more visited links.")

# Translators: when the user selects (highlights) or unselects text in a
# document, Orca will speak information about what they have selected or
# unselected. This message is presented when the user selects from the
# current location to the end of the page by pressing Shift+Page_Down.
PAGE_SELECTED_DOWN = _("page selected from cursor position")

# Translators: when the user selects (highlights) or unselects text in a
# document, Orca will speak information about what they have selected or
# unselected. This message is presented when the user selects from the
# current location to the start of the page by pressing Shift+Page_Up.
PAGE_SELECTED_UP = _("page selected to cursor position")

# Translators: when the user selects (highlights) or unselects text in a
# document, Orca will speak information about what they have selected or
# unselected. This message is presented when the user unselects a previously
# selected page by pressing Shift+Page_Down.
PAGE_UNSELECTED_DOWN = _("page unselected from cursor position")

# Translators: when the user selects (highlights) or unselects text in a
# document, Orca will speak information about what they have selected or
# unselected. This message is presented when the user unselects a previously
# selected page by pressing Shift+Page_Up.
PAGE_UNSELECTED_UP = _("page unselected to cursor position")

# Translators: when the user selects (highlights) or unselects text in a
# document, Orca will speak information about what they have selected or
# unselected. This message is presented when the user selects from the
# current location to the end of the paragraph by pressing Ctrl+Shift+Down.
PARAGRAPH_SELECTED_DOWN = _("paragraph selected down from cursor position")

# Translators: when the user selects (highlights) or unselects text in a
# document, Orca will speak information about what they have selected or
# unselected. This message is presented when the user selects from the
# current location to the start of the paragraph by pressing Ctrl+Shift+UP.
PARAGRAPH_SELECTED_UP = _("paragraph selected up from cursor position")

# Translators: when the user selects (highlights) or unselects text in a
# document, Orca will speak information about what they have selected or
# unselected. This message is presented when the user unselects previously
# selected text from the current location to the end of the paragraph by
# pressing Ctrl+Shift+Down.
PARAGRAPH_UNSELECTED_DOWN = _("paragraph unselected down from cursor position")

# Translators: when the user selects (highlights) or unselects text in a
# document, Orca will speak information about what they have selected or
# unselected. This message is presented when the user unselects previously
# selected text from the current location to the start of the paragraph by
# pressing Ctrl+Shift+UP.
PARAGRAPH_UNSELECTED_UP = _("paragraph unselected up from cursor position")

# Translators: This is a detailed message which will be presented as the user
# cycles amongst his/her saved profiles. A "profile" is a collection of settings
# which apply to a given task, such as a "Spanish" profile which would use
# Spanish text-to-speech and Spanish braille and selected when reading Spanish
# content. The string representing the profile name is created by the user.
PROFILE_CHANGED = _("Profile set to %s.")

# Translators: This is an error message presented when the user attempts to
# cycle among his/her saved profiles, but no profiles can be found. A profile
# is a collection of settings which apply to a given task, such as a "Spanish"
# profile which would use Spanish text-to-speech and Spanish braille and
# selected when reading Spanish content.
PROFILE_NOT_FOUND = _("No profiles found.")

# Translators: this is an index value so that we can present value changes
# regarding a specific progress bar in environments where there are multiple
# progress bars (e.g. in the Firefox downloads dialog).
PROGRESS_BAR_NUMBER = _("Progress bar %d.")

# Translators: This brief message will be presented as the user cycles
# through the different levels of spoken punctuation. The options are:
# All puntuation marks will be spoken, None will be spoken, Most will be
# spoken, or Some will be spoken.
PUNCTUATION_ALL_BRIEF = C_("spoken punctuation", "All")

# Translators: This detailed message will be presented as the user cycles
# through the different levels of spoken punctuation. The options are:
# All puntuation marks will be spoken, None will be spoken, Most will be
# spoken, or Some will be spoken.
PUNCTUATION_ALL_FULL = _("Punctuation level set to all.")

# Translators: This brief message will be presented as the user cycles
# through the different levels of spoken punctuation. The options are:
# All puntuation marks will be spoken, None will be spoken, Most will be
# spoken, or Some will be spoken.
PUNCTUATION_MOST_BRIEF = C_("spoken punctuation", "Most")

# Translators: This detailed message will be presented as the user cycles
# through the different levels of spoken punctuation. The options are:
# All puntuation marks will be spoken, None will be spoken, Most will be
# spoken, or Some will be spoken.
PUNCTUATION_MOST_FULL = _("Punctuation level set to most.")

# Translators: This brief message will be presented as the user cycles
# through the different levels of spoken punctuation. The options are:
# All puntuation marks will be spoken, None will be spoken, Most will be
# spoken, or Some will be spoken.
PUNCTUATION_NONE_BRIEF = C_("spoken punctuation", "None")

# Translators: This detailed message will be presented as the user cycles
# through the different levels of spoken punctuation. The options are:
# All puntuation marks will be spoken, None will be spoken, Most will be
# spoken, or Some will be spoken.
PUNCTUATION_NONE_FULL = _("Punctuation level set to none.")

# Translators: This brief message will be presented as the user cycles
# through the different levels of spoken punctuation. The options are:
# All puntuation marks will be spoken, None will be spoken, Most will be
# spoken, or Some will be spoken.
PUNCTUATION_SOME_BRIEF = C_("spoken punctuation", "Some")

# Translators: This detailed message will be presented as the user cycles
# through the different levels of spoken punctuation. The options are:
# All puntuation marks will be spoken, None will be spoken, Most will be
# spoken, or Some will be spoken.
PUNCTUATION_SOME_FULL = _("Punctuation level set to some.")

# Translators: This message is presented to the user when Orca's preferences
# have been reloaded.
SETTINGS_RELOADED = _("Orca user settings reloaded.")

# Translators: This message is presented to the user when speech synthesis
# has been temporarily turned off.
SPEECH_DISABLED = _("Speech disabled.")

# Translators: This message is presented to the user when speech synthesis
# has been turned back on.
SPEECH_ENABLED = _("Speech enabled.")

# Translators: This string announces speech rate change.
SPEECH_FASTER = _("faster.")

# Translators: This string announces speech rate change.
SPEECH_SLOWER = _("slower.")

# Translators: This string announces speech pitch change.
SPEECH_HIGHER = _("higher.")

# Translators: This string announces speech pitch change.
SPEECH_LOWER  = _("lower.")

# Translators: This message is presented to the user when Orca is launched.
START_ORCA = _("Welcome to Orca.")

# Translators: This message is presented to the user when Orca is quit.
STOP_ORCA = _("Goodbye.")

# Translators: the Orca "Find" dialog allows a user to search for text in a
# window and then move focus to that text.  For example, they may want to find
# the "OK" button.  This message lets them know a string they were searching
# for was not found.
STRING_NOT_FOUND = _("string not found")

# Translators: The structural navigation keys are designed to move the caret
# around document content by object type. H moves you to the next heading,
# Shift H to the previous heading, T to the next table, and so on. Some users
# prefer to turn this off to use Firefox's search when typing feature. This
# message is presented when the user toggles the structural navigation feature
# of Orca. It should be a brief informative message.            
STRUCTURAL_NAVIGATION_KEYS_OFF = _("Structural navigation keys off.")

# Translators: The structural navigation keys are designed to move the caret
# around document content by object type. H moves you to the next heading,
# Shift H to the previous heading, T to the next table, and so on. Some users
# prefer to turn this off to use Firefox's search when typing feature. This
# message is presented when the user toggles the structural navigation feature
# of Orca. It should be a brief informative message.            
STRUCTURAL_NAVIGATION_KEYS_ON = _("Structural navigation keys on.")

# Translators: Orca has a command that allows the user to move to the next
# structural navigation object. In Orca, "structural navigation" refers to
# quickly moving through a document by jumping amongst objects of a given
# type, such as from link to link, or from heading to heading, or from form
# field to form field. This is a brief message which will be presented to the
# user if the desired structural navigation object could not be found.
STRUCTURAL_NAVIGATION_NOT_FOUND = C_("structural navigation", "Not found")

# Translators: When users are navigating a table, they sometimes want the entire
# row of a table read; other times they want just the current cell presented.
# This string is a message presented to the user when this setting is toggled.
TABLE_MODE_CELL = _("Speak cell")

# Translators: When users are navigating a table, they sometimes want the entire
# row of a table read; other times they want just the current cell presented.
# This string is a message presented to the user when this setting is toggled.
TABLE_MODE_ROW = _("Speak row")

# Translators: This is for navigating document content by moving from table cell
# to table cell. If the user gives a table navigation command but is not in a
# table, presents this message.
TABLE_NOT_IN_A = _("Not in a table.")

# Translators: This is a message presented to users when the columns in a table
# have been reordered.
TABLE_REORDERED_COLUMNS = _("Columns reordered")

# Translators: This is a message presented to users when the rows in a table
# have been reordered.
TABLE_REORDERED_ROWS = _("Rows reordered")

# Translators: This is for navigating document content by moving from table cell
# to table cell. This is the message presented when the user attempts to move to
# the cell below the current cell and is already in the last row.
TABLE_COLUMN_BOTTOM = _("Bottom of column.")

# Translators: This is for navigating document content by moving from table cell
# to table cell. This is the message presented when the user attempts to move to
# the cell above the current cell and is already in the first row.
TABLE_COLUMN_TOP = _("Top of column.")

# Translators: This is for navigating document content by moving from table cell
# to table cell. This is the message presented when the user attempts to move to
# the left of the current cell and is already in the first column.
TABLE_ROW_BEGINNING = _("Beginning of row.")

# Translators: This is for navigating document content by moving from table cell
# to table cell. This is the message presented when the user attempts to move to
# the right of the current cell and is already in the last column.
TABLE_ROW_END = _("End of row.")

# Translators: This message is presented to the user to confirm that he/she just
# deleted a table row.
TABLE_ROW_DELETED = _("Row deleted.")

# Translators: This message is presented to the user to confirm that he/she just
# deleted the last row of a table.
TABLE_ROW_DELETED_FROM_END = _("Last row deleted.")

# Translators: This message is presented to the user to confirm that he/she just
# inserted a table row.
TABLE_ROW_INSERTED = _("Row inserted.")

# Translators: This message is presented to the user to confirm that he/she just
# inserted a table row at the end of the table. This typically happens when the
# user presses Tab from within the last cell of the table.
TABLE_ROW_INSERTED_AT_END = _("Row inserted at the end of the table.")

# Translators: when the user selects (highlights) text in a document, Orca lets
# them know.
TEXT_SELECTED = C_("text", "selected")

# Translators: when the user unselects (un-highlights) text in a document, Orca
# lets them know.
TEXT_UNSELECTED = C_("text", "unselected")

# Translators: this is information about a unicode character reported to the
# user.  The value is the unicode number value of this character in hex.
UNICODE = _("Unicode %s")

# Translators: This message presents the Orca version number.
VERSION = _("Orca version %s.") % version

# Translators: This is presented when the user has navigated to a line with only
# whitespace characters (space, tab, etc.) on it.
WHITE_SPACE = _("white space")

# Translators: when the user is attempting to locate a particular object and the
# top of a page or list is reached without that object being found, we "wrap" to
# the bottom and continue looking upwards. We need to inform the user when this
# is taking place.
WRAPPING_TO_BOTTOM = _("Wrapping to bottom.")

# Translators: when the user is attempting to locate a particular object and the
# bottom of a page or list is reached without that object being found, we "wrap"
# to the top and continue looking downwards. We need to inform the user when
# this is taking place.
WRAPPING_TO_TOP = _("Wrapping to top.")
