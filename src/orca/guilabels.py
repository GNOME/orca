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

"""Labels for Orca's GUIs. These have been put in their own module so that we
can present them in the correct language when users change the language on the
fly without having to reload a bunch of modules."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2004-2009 Sun Microsystems Inc." \
                "Copyright (c) 2010-2013 The Orca Team"
__license__   = "LGPL"

from .orca_i18n import _, C_

# Translators: Orca has had to implement its own caret navigation model to work
# around issues in Gecko/Firefox. In some versions of Firefox, we must perform
# a focus grab on each object being navigated in order for things to work as
# expected; in other versions of Firefox, we must avoid doing so in order for
# things# to work as expected. We cannot identify with certainty which situation
# the user is in, so we must provide this as an option within Orca.
CARET_NAVIGATION_GRAB_FOCUS = _("_Grab focus on objects when navigating")

# Translators: When the user arrows up and down in HTML content, and Orca is
# controlling the caret, the user might want Orca to always position the
# cursor at the beginning of the line (as opposed to the position directly
# above/below the current cursor position). Different users have different
# preferences. This string is the label for a checkbox which allows users
# to set the line-positioning behavior they want.
CARET_NAVIGATION_START_OF_LINE = \
    _("_Position cursor at start of line when navigating vertically")

# Translators: If this checkbox is checked, then Orca will tell you when one of
# your buddies is typing a message.
CHAT_ANNOUNCE_BUDDY_TYPING = _("Announce when your _buddies are typing")

# Translators: If this checkbox is checked, then Orca will provide the user with
# chat room specific message histories rather than just a single history which
# contains the latest messages from all the chat rooms that they are in.
CHAT_SEPARATE_MESSAGE_HISTORIES = _("Provide chat room specific _message histories")

# Translators: This is the label of a panel holding options for how messages in
# this application's chat rooms should be spoken. The options are: Speak messages
# from all channels (i.e. even if the chat application doesn't have focus); speak
# messages from a channel only if it is the active channel; speak messages from
# any channel, but only if the chat application has focus.
CHAT_SPEAK_MESSAGES_FROM = _("Speak messages from")

# Translators: This is the label of a radio button. If it is selected, Orca will
# speak all new chat messages as they appear irrespective of whether or not the
# chat application currently has focus. This is the default behaviour.
CHAT_SPEAK_MESSAGES_ALL = _("All cha_nnels")

# Translators: This is the label of a radio button. If it is selected, Orca will
# speak all new chat messages as they appear if and only if the chat application
# has focus. The string substituion is for the application name (e.g Pidgin).
CHAT_SPEAK_MESSAGES_ALL_IF_FOCUSED = _("All channels when an_y %s window is active")

# Translators: This is the label of a radio button. If it is selected, Orca will
# only speak new chat messages for the currently active channel, irrespective of
# whether the chat application has focus.
CHAT_SPEAK_MESSAGES_ACTIVE = _("A channel only if its _window is active")

# Translators: If this checkbox is checked, then Orca will speak the name of the
# chat room prior to presenting an incoming message.
CHAT_SPEAK_ROOM_NAME = _("_Speak Chat Room name")

# Translators: This is a label which will appear in the list of available speech
# engines as a special item. It refers to the default engine configured within
# the speech subsystem. Apart from this item, the user will have a chance to
# select a particular speech engine by its real name (Festival, IBMTTS, etc.)
DEFAULT_SYNTHESIZER = _("Default Synthesizer")

# Translators: This is the label for a spinbutton. This option allows the user
# to specify the number of matched characters that must be present before Orca
# speaks the line that contains the results from an application's Find toolbar.
FIND_MINIMUM_MATCH_LENGTH = _("Minimum length of matched text:")

# Translators: This is the label of a panel containing options for what Orca
# presents when the user is in the Find toolbar of an application, e.g. Firefox.
FIND_OPTIONS = _("Find Options")

# Translators: This is the label for a checkbox. This option controls whether
# the line that contains the match from an application's Find toolbar should
# always be spoken, or only spoken if it is a different line than the line
# which contained the last match.
FIND_ONLY_SPEAK_CHANGED_LINES = _("Onl_y speak changed lines during find")

# Translators: This is the label for a checkbox. This option controls whether or
# not Orca will automatically speak the line that contains the match while the
# user is performing a search from the Find toolbar of an application, e.g.
# Firefox.
FIND_SPEAK_RESULTS = _("Speak results during _find")

# Translators: Function is a table column header where the cells in the column
# are a sentence that briefly describes what action Orca will take if and when
# the user invokes that keyboard command.
KB_HEADER_FUNCTION = _("Function")

# Translators: Key Binding is a table column header where the cells in the
# column represent keyboard combinations the user can press to invoke Orca
# commands.
KB_HEADER_KEY_BINDING = _("Key Binding")

# Translators: Orca has a command that presents a list of structural navigation
# objects in a dialog box so that users can navigate more quickly than they
# could with native keyboard navigation. This is the title for a column which
# contains the text of a blockquote.
SN_HEADER_BLOCKQUOTE = C_("structural navigation", "Blockquote")

# Translators: Orca has a command that presents a list of structural navigation
# objects in a dialog box so that users can navigate more quickly than they
# could with native keyboard navigation. This is the title for a column which
# contains the text of a button.
SN_HEADER_BUTTON = C_("structural navigation", "Button")

# Translators: Orca has a command that presents a list of structural navigation
# objects in a dialog box so that users can navigate more quickly than they
# could with native keyboard navigation. This is the title for a column which
# contains the caption of a table.
SN_HEADER_CAPTION = C_("structural navigation", "Caption")

# Translators: Orca has a command that presents a list of structural navigation
# objects in a dialog box so that users can navigate more quickly than they
# could with native keyboard navigation. This is the title for a column which
# contains the label of a check box.
SN_HEADER_CHECK_BOX = C_("structural navigation", "Check Box")

# Translators: Orca has a command that presents a list of structural navigation
# objects in a dialog box so that users can navigate more quickly than they
# could with native keyboard navigation. This is the title for a column which
# contains the selected item in a combo box.
SN_HEADER_COMBO_BOX = C_("structural navigation", "Combo Box")

# Translators: Orca has a command that presents a list of structural navigation
# objects in a dialog box so that users can navigate more quickly than they
# could with native keyboard navigation. This is the title for a column which
# contains the description of an element.
SN_HEADER_DESCRIPTION = C_("structural navigation", "Description")

# Translators: Orca has a command that presents a list of structural navigation
# objects in a dialog box so that users can navigate more quickly than they
# could with native keyboard navigation. This is the title for a column which
# contains the text of a heading.
SN_HEADER_HEADING = C_("structural navigation", "Heading")

# Translators: Orca has a command that presents a list of structural navigation
# objects in a dialog box so that users can navigate more quickly than they
# could with native keyboard navigation. This is the title for a column which
# contains the label of a form field.
SN_HEADER_LABEL = C_("structural navigation", "Label")

# Translators: Orca has a command that presents a list of structural navigation
# objects in a dialog box so that users can navigate more quickly than they
# could with native keyboard navigation. This is the title of a column which
# contains the level of a heading. Level will be a "1" for <h1>, a "2" for <h2>,
# and so on.
SN_HEADER_LEVEL = C_("structural navigation", "Level")

# Translators: Orca has a command that presents a list of structural navigation
# objects in a dialog box so that users can navigate more quickly than they
# could with native keyboard navigation. This is the title for a column which
# contains the text of a link.
SN_HEADER_LINK = C_("structural navigation", "Link")

# Translators: Orca has a command that presents a list of structural navigation
# objects in a dialog box so that users can navigate more quickly than they
# could with native keyboard navigation. This is the title for a column which
# contains the text of a list.
SN_HEADER_LIST = C_("structural navigation", "List")

# Translators: Orca has a command that presents a list of structural navigation
# objects in a dialog box so that users can navigate more quickly than they
# could with native keyboard navigation. This is the title for a column which
# contains the text of a list item.
SN_HEADER_LIST_ITEM = C_("structural navigation", "List Item")

# Translators: Orca has a command that presents a list of structural navigation
# objects in a dialog box so that users can navigate more quickly than they
# could with native keyboard navigation. This is the title for a column which
# contains the text of an object.
SN_HEADER_OBJECT = C_("structural navigation", "Object")

# Translators: Orca has a command that presents a list of structural navigation
# objects in a dialog box so that users can navigate more quickly than they
# could with native keyboard navigation. This is the title for a column which
# contains the text of a paragraph.
SN_HEADER_PARAGRAPH = C_("structural navigation", "Paragraph")

# Translators: Orca has a command that presents a list of structural navigation
# objects in a dialog box so that users can navigate more quickly than they
# could with native keyboard navigation. This is the title for a column which
# contains the label of a radio button.
SN_HEADER_RADIO_BUTTON = C_("structural navigation", "Radio Button")

# Translators: Orca has a command that presents a list of structural navigation
# objects in a dialog box so that users can navigate more quickly than they
# could with native keyboard navigation. This is the title for a column which
# contains the role of a widget. Examples include "heading", "paragraph",
# "table", "combo box", etc.
SN_HEADER_ROLE = C_("structural navigation", "Role")

# Translators: Orca has a command that presents a list of structural navigation
# objects in a dialog box so that users can navigate more quickly than they
# could with native keyboard navigation. This is the title for a column which
# contains the selected item of a form field.
SN_HEADER_SELETED_ITEM = C_("structural navigation", "Selected Item")

# Translators: Orca has a command that presents a list of structural navigation
# objects in a dialog box so that users can navigate more quickly than they
# could with native keyboard navigation. This is the title for a column which
# contains the state of a widget. Examples include "checked"/"not checked",
# "selected"/"not selected", "visited/not visited", etc.
SN_HEADER_STATE = C_("structural navigation", "State")

# Translators: Orca has a command that presents a list of structural navigation
# objects in a dialog box so that users can navigate more quickly than they
# could with native keyboard navigation. This is the title for a column which
# contains the text of an entry.
SN_HEADER_TEXT = C_("structural navigation", "Text")

# Translators: Orca has a command that presents a list of structural navigation
# objects in a dialog box so that users can navigate more quickly than they
# could with native keyboard navigation. This is the title for a column which
# contains the URI of a link.
SN_HEADER_URI = C_("structural navigation", "URI")

# Translators: Orca has a command that presents a list of structural navigation
# objects in a dialog box so that users can navigate more quickly than they
# could with native keyboard navigation. This is the title for a column which
# contains the value of a form field.
SN_HEADER_VALUE = C_("structural navigation", "Value")

# Translators: Orca has a command that presents a list of structural navigation
# objects in a dialog box so that users can navigate more quickly than they
# could with native keyboard navigation. This is the title of such a dialog box.
SN_TITLE_BLOCKQUOTE = C_("structural navigation", "Blockquotes")

# Translators: Orca has a command that presents a list of structural navigation
# objects in a dialog box so that users can navigate more quickly than they
# could with native keyboard navigation. This is the title of such a dialog box.
SN_TITLE_BUTTON = C_("structural navigation", "Buttons")

# Translators: Orca has a command that presents a list of structural navigation
# objects in a dialog box so that users can navigate more quickly than they
# could with native keyboard navigation. This is the title of such a dialog box.
SN_TITLE_CHECK_BOX = C_("structural navigation", "Check Boxes")

# Translators: Orca has a command that presents a list of structural navigation
# objects in a dialog box so that users can navigate more quickly than they
# could with native keyboard navigation. This is the title of such a dialog box.
SN_TITLE_COMBO_BOX = C_("structural navigation", "Combo Boxes")

# Translators: Orca has a command that presents a list of structural navigation
# objects in a dialog box so that users can navigate more quickly than they
# could with native keyboard navigation. This is the title of such a dialog box.
SN_TITLE_ENTRY = C_("structural navigation", "Entries")

# Translators: Orca has a command that presents a list of structural navigation
# objects in a dialog box so that users can navigate more quickly than they
# could with native keyboard navigation. This is the title of such a dialog box.
SN_TITLE_FORM_FIELD = C_("structural navigation", "Form Fields")

# Translators: Orca has a command that presents a list of structural navigation
# objects in a dialog box so that users can navigate more quickly than they
# could with native keyboard navigation. This is the title of such a dialog box.
SN_TITLE_HEADING = C_("structural navigation", "Headings")

# Translators: Orca has a command that presents a list of structural navigation
# objects in a dialog box so that users can navigate more quickly than they
# could with native keyboard navigation. This is the title of such a dialog box.
# Level will be a "1" for <h1>, a "2" for <h2>, and so on.
SN_TITLE_HEADING_AT_LEVEL = C_("structural navigation", "Headings at Level %d")

# Translators: Orca has a command that presents a list of structural navigation
# objects in a dialog box so that users can navigate more quickly than they
# could with native keyboard navigation. This is the title of such a dialog box.
# A 'large object' is a logical chunk of text, such as a paragraph, a list,
# a table, etc.
SN_TITLE_LARGE_OBJECT = C_("structural navigation", "Large Objects")

# Translators: Orca has a command that presents a list of structural navigation
# objects in a dialog box so that users can navigate more quickly than they
# could with native keyboard navigation. This is the title of such a dialog box.
SN_TITLE_LINK = C_("structural navigation", "Links")

# Translators: Orca has a command that presents a list of structural navigation
# objects in a dialog box so that users can navigate more quickly than they
# could with native keyboard navigation. This is the title of such a dialog box.
SN_TITLE_LIST = C_("structural navigation", "Lists")

# Translators: Orca has a command that presents a list of structural navigation
# objects in a dialog box so that users can navigate more quickly than they
# could with native keyboard navigation. This is the title of such a dialog box.
SN_TITLE_LIST_ITEM = C_("structural navigation", "List Items")

# Translators: Orca has a command that presents a list of structural navigation
# objects in a dialog box so that users can navigate more quickly than they
# could with native keyboard navigation. This is the title of such a dialog box.
SN_TITLE_PARAGRAPH = C_("structural navigation", "Paragraphs")

# Translators: Orca has a command that presents a list of structural navigation
# objects in a dialog box so that users can navigate more quickly than they
# could with native keyboard navigation. This is the title of such a dialog box.
SN_TITLE_RADIO_BUTTON = C_("structural navigation", "Radio Buttons")

# Translators: Orca has a command that presents a list of structural navigation
# objects in a dialog box so that users can navigate more quickly than they
# could with native keyboard navigation. This is the title of such a dialog box.
SN_TITLE_TABLE = C_("structural navigation", "Tables")

# Translators: Orca has a command that presents a list of structural navigation
# objects in a dialog box so that users can navigate more quickly than they
# could with native keyboard navigation. This is the title of such a dialog box.
SN_TITLE_UNVISITED_LINK = C_("structural navigation", "Unvisited Links")

# Translators: Orca has a command that presents a list of structural navigation
# objects in a dialog box so that users can navigate more quickly than they
# could with native keyboard navigation. This is the title of such a dialog box.
SN_TITLE_VISITED_LINK = C_("structural navigation", "Visited Links")

# Translators: This is the title of a panel holding options for how to navigate
# HTML content (e.g., Orca caret navigation, positioning of caret, structural
# navigation, etc.).
PAGE_NAVIGATION = _("Page Navigation")

# Translators: When the user loads a new web page, they can optionally have Orca
# automatically start reading the page from beginning to end. This is the label
# of a checkbox in which users can indicate their preference.
READ_PAGE_UPON_LOAD = \
    _("Automatically start speaking a page when it is first _loaded")

# Translators: This string will appear in the list of available voices for the
# current speech engine. "%s" will be replaced by the name of the current speech
# engine, such as "Festival default voice" or "IBMTTS default voice". It refers
# to the default voice configured for given speech engine within the speech
# subsystem. Apart from this item, the list will contain the names of all
# available "real" voices provided by the speech engine.
SPEECH_DEFAULT_VOICE = _("%s default voice")

# Translators this label refers to the name of particular speech synthesis
# system. (http://devel.freebsoft.org/speechd)
SPEECH_DISPATCHER = _("Speech Dispatcher")

# Translators: This is a label for an option to tell Orca whether or not it
# should speak the coordinates of the current spread sheet cell. Coordinates are
# the row and column position within the spread sheet (i.e. A1, B1, C2 ...)
SPREADSHEET_SPEAK_CELL_COORDINATES = _("Speak spread sheet cell coordinates")

# Translators: This is a label for an option for whether or not to speak the
# header of a table cell in document content.
TABLE_ANNOUNCE_CELL_HEADER = _("Announce cell _header")

# Translators: This is the title of a panel containing options for specifying
# how to navigate tables in document content.
TABLE_NAVIGATION = _("Table Navigation")

# Translators: This is a label for an option to tell Orca to skip over empty/
# blank cells when navigating tables in document content.
TABLE_SKIP_BLANK_CELLS = _("Skip _blank cells")

# Translators: This is a label for an option to tell Orca whether or not it
# should speak table cell coordinates in document content.
TABLE_SPEAK_CELL_COORDINATES = _("Speak _cell coordinates")

# Translators: This is a label for an option to tell Orca whether or not it
# should speak the span size of a table cell (e.g., how many rows and columns
# a particular table cell spans in a table).
TABLE_SPEAK_CELL_SPANS = _("Speak _multiple cell spans")

# Translators: Gecko native caret navigation is where Firefox itself controls
# how the arrow keys move the caret around HTML content. It's often broken, so
# Orca needs to provide its own support. As such, Orca offers the user the
# ability to switch between the Firefox mode and the Orca mode. This is the
# label of a checkbox in which users can indicate their default preference.
USE_CARET_NAVIGATION = _("Use _Orca Caret Navigation")

# Translators: Orca provides keystrokes to navigate HTML content in a structural
# manner: go to previous/next header, list item, table, etc. This is the label
# of a checkbox in which users can indicate their default preference.
USE_STRUCTURAL_NAVIGATION = _("Use Orca _Structural Navigation")
