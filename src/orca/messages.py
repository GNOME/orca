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

# pylint: disable=too-many-lines

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

from .orca_i18n import _, C_, ngettext # pylint: disable=import-error
from .orca_platform import version # pylint: disable=import-error

# Translators: Sometimes when we attempt to get the name of an accessible
# software application, we fail because the app or one of its elements is
# defunct. This is a generic name so that we can still refer to this element
# in messages.
APPLICATION_NO_NAME = C_("generic name", "application")

# Translators: Orca has a command to report the battery status. This message
# is presented to the user when they use this command but Orca was unable to
# retrieve any information about the battery.
BATTERY_STATUS_UNKNOWN = _("Battery status unknown")

# Translators: Orca has a command to report the battery status. This message
# presents the battery level as a percent.
BATTERY_LEVEL = _("Battery: %d%%")

# Translators: Orca has a command to report the battery status. This message
# presents the plugged-in status to the user.
BATTERY_PLUGGED_IN_TRUE = C_("Battery", "plugged in")

# Translators: Orca has a command to report the battery status. This message
# presents the plugged-in status to the user.
BATTERY_PLUGGED_IN_FALSE = C_("Battery", "not plugged in")

# Translators: This is presented when the user has navigated to an empty line.
BLANK = _("blank")

# Translators: This refers to font weight.
BOLD = _("bold")

# Translators: Orca has a feature in which users can store/save a particular
# location in an application window and return to it later by pressing a
# keystroke. These stored/saved locations are "bookmarks". This string is
# presented to the user when a new bookmark has been entered into the list
# of bookmarks.
BOOKMARK_ENTERED = _("bookmark entered")

# Translators: Orca has a feature in which users can store/save a particular
# location in an application window and return to it later by pressing a
# keystroke. These stored/saved locations are "bookmarks". This string is
# presented to the user when the active list of bookmarks have been saved to
# disk.
BOOKMARKS_SAVED = _("bookmarks saved")

# Translators: Orca has a feature in which users can store/save a particular
# location in an application window and return to it later by pressing a
# keystroke. These stored/saved locations are "bookmarks". This string is
# presented to the user when an error was encountered, preventing the active
# list of bookmarks being saved to disk.
BOOKMARKS_SAVED_FAILURE = _("bookmarks could not be saved")

# Translators: Orca has a feature in which users can store/save a particular
# location in an application window and return to it later by pressing a
# keystroke. These stored/saved locations are "bookmarks". This string is
# presented to the user when they try to go to a bookmark, but don't have
# any bookmarks.
BOOKMARKS_NOT_FOUND = _("No bookmarks found.")

# Translators: Orca has a feature in which users can store/save a particular
# location in an application window and return to it later by pressing a
# keystroke. These stored/saved locations are "bookmarks". This string is
# presented to the user when they try to go to a bookmark at a particular
# index (e.g. bookmark 1 or bookmark 2) but there is no bookmark stored at
# that index.
BOOKMARK_NOT_FOUND = _("Bookmark not found.")

# Translators: Orca has a command which toggles all (other) Orca commands so that
# the associated keystroke can by consumed by the native application. For example,
# if there were an Orca command bound to Alt+Down, normally pressing Alt+Down
# would cause the Orca command to be used. This would mean Alt+Down could not be
# used in editors to move the current line of text down. By temporarily disabling
# Orca commands, Alt+Down would be ignored by Orca and work as expected in the
# editor. This string is what Orca presents to the user when Orca's commands are
# being toggled off.
BYPASS_MODE_ENABLED = _("Orca command keys off.")

# Translators: Orca has a command which toggles all (other) Orca commands so that
# the associated keystroke can by consumed by the native application. For example,
# if there were an Orca command bound to Alt+Down, normally pressing Alt+Down
# would cause the Orca command to be used. This would mean Alt+Down could not be
# used in editors to move the current line of text down. By temporarily disabling
# Orca commands, Alt+Down would be ignored by Orca and work as expected in the
# editor. This string is what Orca presents to the user when Orca's commands are
# being toggled back on.
BYPASS_MODE_DISABLED = _("Orca command keys on.")

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

# Translators: Native application caret navigation does not always work as the
# Orca user wants. As such, Orca offers the user the ability to toggle between
# the application controlling the caret and Orca controlling it. This message
# is presented to indicate that the application's native caret navigation is
# active / not being overridden by Orca.
CARET_CONTROL_APP = _("The application is controlling the caret.")

# Translators: Gecko native caret navigation is where Firefox (or Thunderbird)
# itself controls how the arrow keys move the caret around HTML content. It's
# often broken, so Orca needs to provide its own support. As such, Orca offers
# the user the ability to toggle which application is controlling the caret.
CARET_CONTROL_ORCA = _("The screen reader is controlling the caret.")

# Translators: this is the name of a cell in a spreadsheet.
CELL = _("Cell %s")

# Translators: this message is spoken to announce that a table cell just became
# selected (e.g as a result of navigation via Shift + Arrows). The string
# substitution is the cell name. In the case of a spreadsheet the cell name
# will be something like "B3".
CELL_SELECTED = C_("cell", "%s selected")

# Translators: this message is spoken to announce that multiple table cells just
# became selected (e.g as a result of navigation via Shift + Arrows). The first
# string substitution is the name of the first cell in the range. The second string
# substitution is for the name of the last cell in the range. An example message
# for Calc would be "A1 through A30 selected".
CELL_RANGE_SELECTED = C_("cell", "%s through %s selected")

# Translators: this message is spoken to announce that multiple table cells just
# became unselected (e.g as a result of navigation via Shift + Arrows). The first
# string substitution is the name of the first cell in the range. The second string
# substitution is for the name of the last cell in the range. An example message
# for Calc would be "A1 through A30 unselected".
CELL_RANGE_UNSELECTED = C_("cell", "%s through %s unselected")

# Translators: this message is spoken to announce that a table cell just became
# unselected (e.g as a result of navigation via Shift + Arrows). The string
# substitution is the cell name. In the case of a spreadsheet the cell name
# will be something like "B3".
CELL_UNSELECTED = C_("cell", "%s unselected")

# Translators: This is the description of command line option '-d, --disable'
# which allows the user to specify an option to disable as Orca is started.
CLI_DISABLE_OPTION = _("Prevent use of option")

# Translators: this is the description of command line option '-e, --enable'
# which allows the user to specify an option to enable as Orca is started.
CLI_ENABLE_OPTION = _("Force use of option")

# Translators: This string indicates to the user what should be provided when
# using the '-e, --enable' or '-d, --disable' command line options.
CLI_OPTION = _("OPTION")

# Translators: This string appears when using 'Orca -h' at the command line.
# It serves as a sort of title and is followed by a detailed list of Orca's
# optional command-line arguments.
CLI_OPTIONAL_ARGUMENTS = _("Optional arguments")

# Translators: This string appears when using 'Orca -h' at the command line.
# It is followed by a brief list of Orca's optional command-line arguments.
CLI_USAGE = _("Usage: ")

# Translators: This message is displayed when the user starts Orca from the
# command line and includes an invalid option or argument. After the message,
# the list of invalid items, as typed by the user, is displayed.
CLI_INVALID_OPTIONS = _("The following are not valid: ")

# Translators: This is the description of command line option '-l, --list-apps'
# which prints the names of running applications which can be seen by assistive
# technologies such as Orca and Accerciser.
CLI_LIST_APPS = _("Print the known running applications")

# Translators: This is the description of command line option '-p, --profile'
# which allows you to specify a profile to be loaded. A profile stores a group
# of Orca settings configured by the user for a particular purpose, such as a
# 'Spanish' profile which would include Spanish braille and text-to-speech.
# An Orca settings file contains one or more profiles.
CLI_LOAD_PROFILE = _("Load profile")

# Translators: This message is presented to the user when the specified profile
# could not be loaded. A profile stores a group of Orca settings configured for
# a particular purpose, such as a Spanish profile which would include Spanish
# braille and Spanish text-to-speech. The string substituted in is the user-
# provided profile name.
CLI_LOAD_PROFILE_ERROR = _("Profile could not be loaded: %s")

# Translators: This message is presented to the user who attempts to launch Orca
# from some other environment than the graphical desktop.
CLI_NO_DESKTOP_ERROR = \
    _("Cannot start the screen reader because it cannot connect to the Desktop.")

# Translators: This message is presented to the user who attempts to launch Orca
# but the launch fails due to an error related to the settings manager.
CLI_SETTINGS_MANAGER_ERROR = \
    _("Could not activate the settings manager. Exiting.")

# Translators: This message is presented to the user when he/she tries to launch
# Orca, but Orca is already running.
CLI_OTHER_ORCAS_ERROR = \
    _('Another screen reader process is already running for this ' \
      'session.\nRun “orca --replace” to replace that ' \
      'process with a new one.')

# Translators: This string indicates to the user what should be provided when
# using the '-p, --profile' command line option.
CLI_PROFILE_NAME = _("NAME")

# Translators: This is the description of command line option '-u, --user-prefs'
# that allows you to specify an alternate location from which to load the user
# preferences.
CLI_LOAD_PREFS = _("Use alternate directory for user preferences")

# Translators: This string indicates to the user what should be provided when
# using the '-u, --user-prefs' command line option.
CLI_PREFS_DIR = _("DIR")

# Translators: This is the description of command line option '--speech-system'
# which allows you to specify a speech system to use. A speech system provides
# various synthesizers with different voices and languages.
# This option can be used to override the configured default speech system.
CLI_SPEECH_SYSTEM = _("Speech system")

# Translators: This message is presented to the user when the specified speech
# system is unavailable. A speech system provides various synthesizers with
# different voices and languages. The first string substituted in is the user-
# provided speech system. The second string substituted is a comma separated
# list of avaialable speech systems.
CLI_SPEECH_SYSTEM_ERROR = _("Speech system “%s” is unavailable (available: %s)")

# Translators: This string indicates to the user what should be provided when
# using the '--speech-system' command line option.
CLI_SPEECH_SYSTEM_NAME = _("NAME")

# Translators: This is the description of command line option '-v, --version'
# which prints the version of Orca. E.g. '1.23.4'.
CLI_VERSION = _("Version of this application")

# Translators: This is the description of command line option '-r, --replace'
# which tells Orca to replace any existing Orca process that might be running.
CLI_REPLACE = _("Replace a currently running instance of this screen reader")

# Translators: this is the description of command line option '-h, --help'
# which lists all the available command line options.
CLI_HELP = _("Show this help message and exit")

# Translators: This is the description of command line option '--debug' which
# causes debugging output for Orca to be sent to a file. The YYYY-MM-DD-HH:MM:SS
# portion of the string indicates the file name will be formed from the current
# date and time with 'debug' in front and '.out' at the end. The 'debug' and
# '.out' portions of this string should not be translated (i.e. it should always
# start with 'debug' and end with '.out', regardless of the locale.).
CLI_ENABLE_DEBUG = _("Send debug output to debug-YYYY-MM-DD-HH:MM:SS.out")

# Translators: This is the description of command line option '--debug-file'
# which allows the user to override the default date-based name of the debugging
# output file.
CLI_DEBUG_FILE = _("Send debug output to the specified file")

# Translators: This string indicates to the user what should be provided when
# using the '--debug-file' command line option.
CLI_DEBUG_FILE_NAME = _("FILE")

# Translators: This is the description of command line option '-t, --text-setup'
# that will initially display a list of questions in text form, that the user
# will need to answer, before Orca will startup. For this to happen properly,
# Orca will need to be run from a terminal window.
CLI_SETUP = _("Set up user preferences (text version)")

# Translators: This is the description of command line option '-s, --setup'
# that will place the user in Orca's GUI preferences dialog.
CLI_GUI_SETUP = _("Set up user preferences (GUI version)")

# Translators: This text is the description displayed when Orca is launched
# from the command line and the help text is displayed.
CLI_EPILOG = _("Report bugs on https://gitlab.gnome.org/GNOME/orca/-/issues.")

# Translators: Orca has a command to present the contents of the clipboard without
# the user having to switch to a clipboard manager. This message is spoken by Orca
# before speaking the text which is in the clipboard. The string substitution is
# for the clipboard contents.
CLIPBOARD_CONTAINS = _("Clipboard contains: %s")

# Translators: Orca normal speaks the text which was just deleted from a
# document via command. Depending on the circumstances, that might be a
# large string. Therefore, if the text which has just been deleted from a
# document matches the clipboard contents, Orca will indicate that fact
# instead of presenting the full string which was just deleted. This message
# is the full/verbose indication.
CLIPBOARD_CUT_FULL = _("Cut selection to clipboard.")

# Translators: Orca normal speaks the text which was just deleted from a
# document via command. Depending on the circumstances, that might be a
# large string. Therefore, if the text which has just been deleted from a
# document matches the clipboard contents, Orca will indicate that fact
# instead of presenting the full string which was just deleted. This message
# is the brief indication.
CLIPBOARD_CUT_BRIEF = C_("clipboard", "cut")

# Translators: This message is the detailed message presented when the contents
# of the clipboard have changed and match the current selection.
CLIPBOARD_COPIED_FULL = _("Copied selection to clipboard.")

# Translators: This message is the brief message presented when the contents
# of the clipboard have changed and match the current selection.
CLIPBOARD_COPIED_BRIEF = C_("clipboard", "copied")

# Translators: Orca normal speaks the text which was just inserted into a
# document via command. Depending on the circumstances, that might be a
# large string. Therefore, if the text which has just been inserted into a
# document matches the clipboard contents, Orca will indicate that fact
# instead of presenting the full string which was just inserted. This message
# is the full/verbose indication.
CLIPBOARD_PASTED_FULL = _("Pasted contents from clipboard.")

# Translators: Orca normal speaks the text which was just inserted into a
# document via command. Depending on the circumstances, that might be a
# large string. Therefore, if the text which has just been inserted into a
# document matches the clipboard contents, Orca will indicate that fact
# instead of presenting the full string which was just inserted. This message
# is the brief indication.
CLIPBOARD_PASTED_BRIEF = C_("clipboard", "pasted")

# Translators: In chat applications, it is often possible to see that a "buddy"
# is typing currently (e.g. via a keyboard icon or status text). Some users like
# to have this typing status announced by Orca; others find that announcement
# unpleasant. Therefore, it is a setting in Orca. This string to be translated
# is presented when the value of the setting is toggled.
CHAT_BUDDY_TYPING_OFF = _("Do not announce when your buddies are typing.")

# Translators: In chat applications, it is often possible to see that a "buddy"
# is typing currently (e.g. via a keyboard icon or status text). Some users like
# to have this typing status announced by Orca; others find that announcement
# unpleasant. Therefore, it is a setting in Orca. This string to be translated
# is presented when the value of the setting is toggled.
CHAT_BUDDY_TYPING_ON = _("announce when your buddies are typing.")

# Translators: In chat applications, Orca automatically presents incoming
# messages in speech and braille. If a user is in multiple conversations or
# channels at the same time, it can be confusing to know what room or channel
# a given message came from just from hearing/reading it. This string to be
# translated is presented to the user to clarify where an incoming message
# came from. The name of the chat room is the string substitution.
CHAT_MESSAGE_FROM_ROOM = _("Message from chat room %s")

# Translators: This message is presented to inform the user that a new chat
# conversation has been added to the existing conversations. The "tab" here
# refers to the tab which contains the label for a GtkNotebook page. The
# label on the tab is the string substitution.
CHAT_NEW_TAB = _("New chat tab %s")

# Translators: In chat applications, Orca automatically presents incoming
# messages in speech and braille. If a user is in multiple conversations or
# channels at the same time, it can be confusing to know what room or channel
# a given message came from just from hearing/reading it. For this reason, Orca
# has an option to present the name of the room first ("#a11y <joanie> hello!"
# instead of "<joanie> hello!"). This string to be translated is presented when
# the value of the setting is toggled.
CHAT_ROOM_NAME_PREFIX_OFF = _("Do not speak chat room name.")

# Translators: In chat applications, Orca automatically presents incoming
# messages in speech and braille. If a user is in multiple conversations or
# channels at the same time, it can be confusing to know what room or channel
# a given message came from just from hearing/reading it. For this reason, Orca
# has an option to present the name of the room first ("#a11y <joanie> hello!"
# instead of "<joanie> hello!"). This string to be translated is presented when
# the value of the setting is toggled.
CHAT_ROOM_NAME_PREFIX_ON = _("speak chat room name.")

# Translators: Orca has a command to review previous chat room messages in
# speech and braille. Some users prefer to have this message history combined
# (e.g. the last ten messages which came in, no matter what room they came
# from). Other users prefer to have specific room history (e.g. the last ten
# messages from #a11y). Therefore, this is a setting in Orca. This string to be
# translated is presented when the value of the setting is toggled.
CHAT_SEPARATE_HISTORIES_OFF = \
    _("Do not provide chat room specific message histories.")

# Translators: Orca has a command to review previous chat room messages in
# speech and braille. Some users prefer to have this message history combined
# (e.g. the last ten messages which came in, no matter what room they came
# from). Other users prefer to have specific room history (e.g. the last ten
# messages from #a11y). Therefore, this is a setting in Orca. This string to be
# translated is presented when the value of the setting is toggled.
CHAT_SEPARATE_HISTORIES_ON = _("Provide chat room specific message histories.")

DATE_FORMAT_LOCALE = "%x"
DATE_FORMAT_NUMBERS_DM = "%d/%m"
DATE_FORMAT_NUMBERS_MD = "%m/%d"
DATE_FORMAT_NUMBERS_DMY = "%d/%m/%Y"
DATE_FORMAT_NUMBERS_MDY = "%m/%d/%Y"
DATE_FORMAT_NUMBERS_YMD = "%Y/%m/%d"
DATE_FORMAT_FULL_DM = "%A, %-d %B"
DATE_FORMAT_FULL_MD = "%A, %B %-d"
DATE_FORMAT_FULL_DMY = "%A, %-d %B, %Y"
DATE_FORMAT_FULL_MDY = "%A, %B %-d, %Y"
DATE_FORMAT_FULL_YMD = "%Y. %B %-d, %A"
DATE_FORMAT_ABBREVIATED_DM = "%a, %-d %b"
DATE_FORMAT_ABBREVIATED_MD = "%a, %b %-d"
DATE_FORMAT_ABBREVIATED_DMY = "%a, %-d %b, %Y"
DATE_FORMAT_ABBREVIATED_MDY = "%a, %b %-d, %Y"
DATE_FORMAT_ABBREVIATED_YMD = "%Y. %b %-d, %a"

# Translators: This phrase is spoken to inform the user that what is about to
# be said is content marked for deletion in a document, such as content which
# is inside an HTML 'del' element, or the removed code in a diff.
CONTENT_DELETION_START = C_("content", "deletion start")

# Translators: This phrase is spoken to inform the user that they have reached
# the end of content marked for deletion in a document, such as content which
# is inside an HTML 'del' element, or the removed code in a diff.
CONTENT_DELETION_END = C_("content", "deletion end")

# Translators: This phrase is spoken to inform the user that what is about to
# be said is content marked for insertion in a document, such as content which
# is inside an HTML 'ins' element, or the added code in a diff.
CONTENT_INSERTION_START = C_("content", "insertion start")

# Translators: This phrase is spoken to inform the user that they have reached
# the end of content marked for deletion in a document, such as content which
# is inside an HTML 'ins' element, or the added code in a diff.
CONTENT_INSERTION_END = C_("content", "insertion end")

# Translators: This phrase is spoken to inform the user that what is about to
# be said is content marked/highlighted in a document, such as content which
# is inside an HTML 'mark' element.
CONTENT_MARK_START = C_("content", "highlight start")

# Translators: This phrase is spoken to inform the user that they have reached
# the end of content marked/highlighted in a document, such as content which
# is inside an HTML 'mark' element.
CONTENT_MARK_END = C_("content", "highlight end")

# Translators: This phrase is spoken to inform the user that the content being
# presented is the end of an inline suggestion a document. A "suggestion" is a
# proposed change. This change can include the insertion and/or deletion
# of content, and would typically be seen in a collaborative editor, such as
# in Google Docs.
CONTENT_SUGGESTION_END = C_("content", "suggestion end")

# Translators: This is for navigating document content by moving to the start
# or end of a container. Examples of containers include tables, lists, and
# blockquotes. When moving to the end of a container, Orca attempts to place
# the caret at the content which follows that container. If this is cannot be
# done (e.g. because the container is the last element on the page), Orca will
# instead present this message as an indication that the container was not
# exited as expected.
CONTAINER_END = _("End of container.")

# Translators: This is for navigating document content by moving to the start
# or end of a container. Examples of containers include tables, lists, and
# blockquotes. If the user attempts to use this command in an object which is
# not a container, this message will be presented.
CONTAINER_NOT_IN_A = _("Not in a container.")

# Translators: This message is presented when the user selects all of the items
# in a container that supports selection, such as a GUI table or a list of icons.
CONTAINER_SELECTED_ALL = _("all items selected")

# Translators: This message is presented when the user is in a date picker and
# navigates to the item which reflects the current date.
CURRENT_DATE = _("Current date")

# Translators: This message is presented wwhen the user is in a time picker/schedule
# and navigates to the item which reflects the current time.
CURRENT_TIME = _("Current time")

# Translators: This message is presented when the user is in a map or flow chart and
# navigates to the item which reflects the current location.
CURRENT_LOCATION = _("Current location")

# Translators: This message is presented when the user is in a table of contents or
# other set of pagination links and navigates to the item which reflects the current
# page.
CURRENT_PAGE = _("Current page")

# Translators: This message is presented when the user is in a wizard or other
# step-based interface and navigates to the item which reflects the current step.
CURRENT_STEP = _("Current step")

# Translators: This message is presented when the user is in a list of generic or
# unspecified items and navigates to the link/object which reflects the current item.
CURRENT_ITEM = _("Current item")

# Translators: Orca has a command to report CPU and memory usage. This message
# is presented to the user when they use this command but Orca was unable to
# retrieve this information.
CPU_AND_MEMORY_USAGE_UNKNOWN = _("CPU and memory usage unknown")

# Translators: Orca has a command to report CPU and memory usage levels. This
# message presents the levels to the user.
CPU_AND_MEMORY_USAGE_LEVELS = _("CPU: %d%%. Memory: %d%%")

# Translators: Orca has a command for advanced users and developers to clear
# the AT-SPI cache in case there is stale information due to an application
# bug. This message is presented when the user tried to clear the cache but
# an error occurred.
DEBUG_CLEAR_CACHE_FAILED = _("Clearing cache failed.")

# Translators: Orca has a command for advanced users and developers to clear
# the AT-SPI cache in case there is stale information due to an application
# bug. This message is presented when the user performs the command.
DEBUG_CLEAR_CACHE = _("Clearing cache.")

# Translators: this is a debug message for advanced users and developers. It
# describes a command to print detailed debugging information about the current
# state with respect to the accessible applications being used, such as the
# accessibility tree of the current window, a list of all the running accessible
# objects, etc. This message is presented to confirm to the user that the snapshot
# capture has begun.
DEBUG_CAPTURE_SNAPSHOT_START = _("Capturing debugging snapshot")

# Translators: this is a debug message for advanced users and developers. It
# describes a command to print detailed debugging information about the current
# state with respect to the accessible applications being used, such as the
# accessibility tree of the current window, a list of all the running accessible
# objects, etc. This message is presented to confirm to the user that the snapshot
# capture has begun.
DEBUG_CAPTURE_SNAPSHOT_END = _("Debugging snapshot captured")

# Translators: The "default" button in a dialog box is the button that gets
# activated when Enter is pressed anywhere within that dialog box. The string
# substitution is the name of the button (e.g. "OK" or "Close").
DEFAULT_BUTTON_IS = _("Default button is %s")

# Translators: The "default" button in a dialog box is the button that gets
# activated when Enter is pressed anywhere within that dialog box. This
# message is presented when the default button was found but is insensitive /
# grayed out / cannot be activated. The string substitution is the name of
# the button (e.g. "OK" or "Close"). When translating "Grayed," please use
# the same word used for the string in object_properties.py.
DEFAULT_BUTTON_IS_GRAYED = _("Default button is %s. Grayed")

# Translators: The "default" button in a dialog box is the button that gets
# activated when Enter is pressed anywhere within that dialog box. Orca has
# a command to present the default button. This is the message Orca will
# present if it could not find the default button.
DEFAULT_BUTTON_NOT_FOUND = _("Default button not found")

# Translators: This string is part of the presentation of an item that includes
# one or several consecutive subscripted characters. For example, 'X' followed
# by 'subscript 2' followed by 'subscript 3' should be presented to the user as
# 'X subscript 23'.
DIGITS_SUBSCRIPT =  _(" subscript %s")

# Translators: This string is part of the presentation of an item that includes
# one or several consecutive superscripted characters. For example, 'X' followed
# by 'superscript 2' followed by 'superscript 3' should be presented to the user
# as 'X superscript 23'.
DIGITS_SUPERSCRIPT =  _(" superscript %s")

# Translators: this message is presented when the user tries to perform a command
# specific to dialog boxes, such as presenting the default button, but is not in
# a dialog.
DIALOG_NOT_IN_A = _("Not in a dialog")

# Translators: when the user selects (highlights) or unselects text in a
# document, Orca will speak information about what they have selected or
# unselected. This message is presented when the user selects the entire
# document by pressing Ctrl+A.
DOCUMENT_SELECTED_ALL = _("entire document selected")

# Translators: when the user selects (highlights) or unselects text in a
# document, Orca will speak information about what they have selected or
# unselected. This message is presented when the entire document had been
# selected but the user presses a key (e.g. an arrow key) causing the
# selection to be completely removed.
DOCUMENT_UNSELECTED_ALL = _("entire document unselected")

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

# Translators: This is the size of a file in kilobytes
FILE_SIZE_KB = _("%.2f kilobytes")

# Translators: This is the size of a file in megabytes
FILE_SIZE_MB = _("%.2f megabytes")

# Translators: This message is presented to the user after performing a file
# search to indicate there were no matches.
FILES_NOT_FOUND = _("No files found.")

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

# Translators: the 'flat review' feature of Orca allows the blind user to
# explore the text in a window in a 2D fashion.  That is, Orca treats all
# the text from all objects in a window (e.g., buttons, labels, etc.) as a
# sequence of words in a sequence of lines.  This message is presented to
# let the user know that flat review is being restricted to the current
# object of interest.
FLAT_REVIEW_RESTRICTED = _("Flat review restricted to the current object")

# Translators: the 'flat review' feature of Orca allows the blind user to
# explore the text in a window in a 2D fashion.  That is, Orca treats all
# the text from all objects in a window (e.g., buttons, labels, etc.) as a
# sequence of words in a sequence of lines.  This message is presented to
# let the user know that flat review is unrestricted,
# that is, the entire window can be explored.
FLAT_REVIEW_UNRESTRICTED = _("Flat review unrestricted")

# Translators: this means a particular cell in a spreadsheet has a formula
# (e.g., "=sum(a1:d1)")
HAS_FORMULA = _("has formula")

# Translators: this message will be presented to indicate the focused object
# will cause a dialog to appear if activated.
HAS_POPUP_DIALOG = _("opens dialog")

# Translators: this message will be presented to indicate the focused object
# will cause a grid to appear if activated. A grid is an interactive table.
HAS_POPUP_GRID = _("opens grid")

# Translators: this message will be presented to indicate the focused object
# will cause a listbox to appear if activated.
HAS_POPUP_LISTBOX = _("opens listbox")

# Translators: this message will be presented to indicate the focused object
# will cause a menu to appear if activated.
HAS_POPUP_MENU = _("opens menu")

# Translators: this message will be presented to indicate the focused object
# will cause a tree to appear if activated. A tree is a list with sub-levels
# which can be expanded or collapsed, similar to the list of folders in an
# email client.
HAS_POPUP_TREE = _("opens tree")

# Translators: this message will be presented to indicate the focused object
# will cause a popup to appear if activated.
HAS_POPUP = _("opens popup")

# Translators: The following string is spoken to let the user know that he/she
# is on a link within an image map. An image map is an image/graphic which has
# been divided into regions. Each region can be clicked on and has an associated
# link. Please see http://en.wikipedia.org/wiki/Imagemap for more information
# and examples.
IMAGE_MAP_LINK = _("image map link")

# Translators: This is a spoken and/or brailled message letting the user know
# that the key combination (e.g., Ctrl+Alt+f) they just entered has already been
# bound to another command and is thus unavailable. The string substituted in is
# the name of the command which already has the binding.
KB_ALREADY_BOUND = _("The key entered is already bound to %s")

# Translators: This is a spoken and/or brailled message letting the user know
# that Orca has recorded a new key combination (e.g. Alt+Ctrl+g) as a result of
# their input. The string substituted in is the new key combination.
KB_CAPTURED = _("Key captured: %s. Press enter to confirm.")

# Translators: This is a spoken and/or brailled message letting the user know
# that Orca has assigned a new key combination (e.g. Alt+Ctrl+g) as a result of
# their input. The string substituted in is the new key combination.
KB_CAPTURED_CONFIRMATION = _("The new key is: %s")

# Translators: This is a spoken and/or brailled message letting the user know
# Orca is about to delete an existing key combination (e.g. Alt+Ctrl+g) as a
# result of their input.
KB_DELETED = _("Key binding deleted. Press enter to confirm.")

# Translators: This is a spoken and/or brailled message letting the user know
# Orca has deleted an existing key combination (e.g. Alt+Ctrl+g) as a result of
# their input.
KB_DELETED_CONFIRMATION = _("The keybinding has been removed.")

# Translators: This is a spoken and/or brailled message asking the user to press
# a new key combination (e.g., Alt+Ctrl+g) to create a new key binding for an
# Orca command.
KB_ENTER_NEW_KEY = _("enter new key")

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
KEY_ECHO_KEY_FULL = _("Echo set to key.")

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
KEY_ECHO_NONE_FULL = _("Echo set to None.")

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
KEY_ECHO_KEY_AND_WORD_FULL = _("Echo set to key and word.")

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
KEY_ECHO_SENTENCE_FULL = _("Echo set to sentence.")

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
KEY_ECHO_WORD_FULL = _("Echo set to word.")

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
KEY_ECHO_WORD_AND_SENTENCE_FULL = _("Echo set to word and sentence.")

# Translators: This phrase is spoken to inform the user of all of the MathML
# enclosure notations associated with a given mathematical expression. For
# instance, the expression x+y could be enclosed by a box, or enclosed by a
# circle. It could also be enclosed by a box and a circle and long division
# sign and have a line on the left and on the right and a vertical strike.
# (Though let's hope not.) Given that we do not know the enclosures, their
# order, or their combination, we'll present them as a list. The string
# substitution is for that list of enclosure types. For more information
# about the MathML 'menclose' element and its notation types, see:
# http://www.w3.org/TR/MathML3/chapter3.html#presm.menclose
MATH_ENCLOSURE_ENCLOSED_BY = C_("math enclosure", "Enclosed by: %s")

# Translators: This phrase is spoken to describe one MathML enclosure notation
# associated with a mathematical expression. Because an expression, such as
# x+y, can have one or many enclosure notations (box, circle, long division,
# line on the left, vertical strike), we present them as a list of notations.
# For more information about the MathML 'menclose' element and its notation
# types, see: http://www.w3.org/TR/MathML3/chapter3.html#presm.menclose
MATH_ENCLOSURE_ACTUARIAL = C_("math enclosure", "an actuarial symbol")

# Translators: This phrase is spoken to describe one MathML enclosure notation
# associated with a mathematical expression. Because an expression, such as
# x+y, can have one or many enclosure notations (box, circle, long division,
# line on the left, vertical strike), we present them as a list of notations.
# For more information about the MathML 'menclose' element and its notation
# types, see: http://www.w3.org/TR/MathML3/chapter3.html#presm.menclose
MATH_ENCLOSURE_BOX = C_("math enclosure", "a box")

# Translators: This phrase is spoken to describe one MathML enclosure notation
# associated with a mathematical expression. Because an expression, such as
# x+y, can have one or many enclosure notations (box, circle, long division,
# line on the left, vertical strike), we present them as a list of notations.
# For more information about the MathML 'menclose' element and its notation
# types, see: http://www.w3.org/TR/MathML3/chapter3.html#presm.menclose
MATH_ENCLOSURE_CIRCLE = C_("math enclosure", "a circle")

# Translators: This phrase is spoken to describe one MathML enclosure notation
# associated with a mathematical expression. Because an expression, such as
# x+y, can have one or many enclosure notations (box, circle, long division,
# line on the left, vertical strike), we present them as a list of notations.
# For more information about the MathML 'menclose' element and its notation
# types, see: http://www.w3.org/TR/MathML3/chapter3.html#presm.menclose
MATH_ENCLOSURE_LONGDIV = C_("math enclosure", "a long division sign")

# Translators: This phrase is spoken to describe one MathML enclosure notation
# associated with a mathematical expression. Because an expression, such as
# x+y, can have one or many enclosure notations (box, circle, long division,
# line on the left, vertical strike), we present them as a list of notations.
# For more information about the MathML 'menclose' element and its notation
# types, see: http://www.w3.org/TR/MathML3/chapter3.html#presm.menclose
MATH_ENCLOSURE_RADICAL = C_("math enclosure", "a radical")

# Translators: This phrase is spoken to describe one MathML enclosure notation
# associated with a mathematical expression. Because an expression, such as
# x+y, can have one or many enclosure notations (box, circle, long division,
# line on the left, vertical strike), we present them as a list of notations.
# For more information about the MathML 'menclose' element and its notation
# types, see: http://www.w3.org/TR/MathML3/chapter3.html#presm.menclose
MATH_ENCLOSURE_ROUNDEDBOX = C_("math enclosure", "a rounded box")

# Translators: This phrase is spoken to describe one MathML enclosure notation
# associated with a mathematical expression. Because an expression, such as
# x+y, can have one or many enclosure notations (box, circle, long division,
# line on the left, vertical strike), we present them as a list of notations.
# For more information about the MathML 'menclose' element and its notation
# types, see: http://www.w3.org/TR/MathML3/chapter3.html#presm.menclose
MATH_ENCLOSURE_HORIZONTALSTRIKE = C_("math enclosure", "a horizontal strike")

# Translators: This phrase is spoken to describe one MathML enclosure notation
# associated with a mathematical expression. Because an expression, such as
# x+y, can have one or many enclosure notations (box, circle, long division,
# line on the left, vertical strike), we present them as a list of notations.
# For more information about the MathML 'menclose' element and its notation
# types, see: http://www.w3.org/TR/MathML3/chapter3.html#presm.menclose
MATH_ENCLOSURE_VERTICALSTRIKE = C_("math enclosure", "a vertical strike")

# Translators: This phrase is spoken to describe one MathML enclosure notation
# associated with a mathematical expression. Because an expression, such as
# x+y, can have one or many enclosure notations (box, circle, long division,
# line on the left, vertical strike), we present them as a list of notations.
# For more information about the MathML 'menclose' element and its notation
# types, see: http://www.w3.org/TR/MathML3/chapter3.html#presm.menclose
MATH_ENCLOSURE_DOWNDIAGONALSTRIKE = C_("math enclosure", "a down diagonal strike")

# Translators: This phrase is spoken to describe one MathML enclosure notation
# associated with a mathematical expression. Because an expression, such as
# x+y, can have one or many enclosure notations (box, circle, long division,
# line on the left, vertical strike), we present them as a list of notations.
# For more information about the MathML 'menclose' element and its notation
# types, see: http://www.w3.org/TR/MathML3/chapter3.html#presm.menclose
MATH_ENCLOSURE_UPDIAGONALSTRIKE = C_("math enclosure", "an up diagonal strike")

# Translators: This phrase is spoken to describe one MathML enclosure notation
# associated with a mathematical expression. Because an expression, such as
# x+y, can have one or many enclosure notations (box, circle, long division,
# line on the left, vertical strike), we present them as a list of notations.
# For more information about the MathML 'menclose' element and its notation
# types, see: http://www.w3.org/TR/MathML3/chapter3.html#presm.menclose
MATH_ENCLOSURE_NORTHEASTARROW = C_("math enclosure", "a northeast arrow")

# Translators: This phrase is spoken to describe one MathML enclosure notation
# associated with a mathematical expression. Because an expression, such as
# x+y, can have one or many enclosure notations (box, circle, long division,
# line on the left, vertical strike), we present them as a list of notations.
# For more information about the MathML 'menclose' element and its notation
# types, see: http://www.w3.org/TR/MathML3/chapter3.html#presm.menclose
MATH_ENCLOSURE_BOTTOM = C_("math enclosure", "a line at the bottom")

# Translators: This phrase is spoken to describe one MathML enclosure notation
# associated with a mathematical expression. Because an expression, such as
# x+y, can have one or many enclosure notations (box, circle, long division,
# line on the left, vertical strike), we present them as a list of notations.
# For more information about the MathML 'menclose' element and its notation
# types, see: http://www.w3.org/TR/MathML3/chapter3.html#presm.menclose
MATH_ENCLOSURE_LEFT = C_("math enclosure", "a line on the left")

# Translators: This phrase is spoken to describe one MathML enclosure notation
# associated with a mathematical expression. Because an expression, such as
# x+y, can have one or many enclosure notations (box, circle, long division,
# line on the left, vertical strike), we present them as a list of notations.
# For more information about the MathML 'menclose' element and its notation
# types, see: http://www.w3.org/TR/MathML3/chapter3.html#presm.menclose
MATH_ENCLOSURE_RIGHT = C_("math enclosure", "a line on the right")

# Translators: This phrase is spoken to describe one MathML enclosure notation
# associated with a mathematical expression. Because an expression, such as
# x+y, can have one or many enclosure notations (box, circle, long division,
# line on the left, vertical strike), we present them as a list of notations.
# For more information about the MathML 'menclose' element and its notation
# types, see: http://www.w3.org/TR/MathML3/chapter3.html#presm.menclose
MATH_ENCLOSURE_TOP = C_("math enclosure", "a line at the top")

# Translators: This phrase is spoken to describe one MathML enclosure notation
# associated with a mathematical expression. Because an expression, such as
# x+y, can have one or many enclosure notations (box, circle, long division,
# line on the left, vertical strike), we present them as a list of notations.
# For more information about the MathML 'menclose' element and its notation
# types, see: http://www.w3.org/TR/MathML3/chapter3.html#presm.menclose
MATH_ENCLOSURE_PHASOR_ANGLE = C_("math enclosure", "a phasor angle")

# Translators: This phrase is spoken to describe one MathML enclosure notation
# associated with a mathematical expression. Because an expression, such as
# x+y, can have one or many enclosure notations (box, circle, long division,
# line on the left, vertical strike), we present them as a list of notations.
# For more information about the MathML 'menclose' element and its notation
# types, see: http://www.w3.org/TR/MathML3/chapter3.html#presm.menclose
# This particular string is for the "madruwb" notation type.
MATH_ENCLOSURE_MADRUWB = C_("math enclosure", "an arabic factorial symbol")

# Translators: This phrase is spoken to inform the user of all of the MathML
# enclosure notations associated with a given mathematical expression. For
# instance, the expression x+y could be enclosed by a box, or enclosed by a
# circle. It could also be enclosed by a box and a circle and long division
# sign and have a line on the left and on the right and a vertical strike.
# (Though let's hope not.) Given that we do not know the enclosures, their
# order, or their combination, we'll present them as a list. This string
# will be inserted before the final item in the list if there is more than
# one enclosure notation. For more information about the MathML 'menclose'
# element and its notation types, see:
# http://www.w3.org/TR/MathML3/chapter3.html#presm.menclose
MATH_ENCLOSURE_AND = C_("math enclosure", "and")

# Translators: This phrase is spoken to inform the user that what is about to
# be said is part of a mathematical fraction. For instance, given x+1/y+2, Orca
# would say "fraction start, x+1 over y+2, fraction end."
MATH_FRACTION_START = _("fraction start")

# Translators: This phrase is spoken to inform the user that what is about to
# be said is part of a mathematical fraction whose bar is not displayed. See
# https://en.wikipedia.org/wiki/Combination for an example. Note that the
# comma is inserted here to cause a very brief pause in the speech. Otherwise,
# in English, the resulting speech sounds like we have a fraction which lacks
# the start of the bar. If this is a non-issue for your language, the comma and
# the pause which results is not needed. You should be able to test this with
# "spd-say <your text here>" in a terminal on a machine where speech-dispatcher
# is installed.
MATH_FRACTION_WITHOUT_BAR_START = _("fraction without bar, start")

# Translators: This word refers to the line separating the numerator from the
# denominator in a mathematical fraction. For instance, given x+1/y+2, Orca
# would would say "fraction start, x+1 over y+2, fraction end."
MATH_FRACTION_LINE = C_("math fraction", "over")

# Translators: This phrase is spoken to inform the user that the last spoken
# phrase is the end of a mathematical fraction. For instance, given x+1/y+2,
# Orca would would say "fraction start, x+1 over y+2, fraction end."
MATH_FRACTION_END = _("fraction end")

# Translators: This phrase is spoken to inform the user that what is about to
# be spoken is a square root. For instance, for √9 Orca would say "square root
# of 9, root end" (assuming the user settings indicate that root endings should
# be spoken). Note that the radicand, which follows the "of", is unknown and
# might not even be a simple string; it might be the square root of another
# expression such as a fraction.
MATH_SQUARE_ROOT_OF = _("square root of")

# Translators: This phrase is spoken to inform the user that what is about to
# be spoken is a cube root. For instance, for the cube root of 9 Orca would
# say "cube root of 9, root end" (assuming the user settings indicate that root
# endings should  be spoken). Note that the radicand, which follows the "of",
# is unknown and might not even be a simple string; it might be the cube root
# of another expression such as a fraction.
MATH_CUBE_ROOT_OF = _("cube root of")

# Translators: This phrase is spoken to inform the user that what is about to
# be spoken is an nth root. https://en.wikipedia.org/wiki/Nth_root. For instance,
# for the fourth root of 9, Orca would say "fourth root of 9, root end" (assuming
# the user settings indicate that root endings should be spoken). Note that the
# index, which precedes this string, is unknown and might not even be a simple
# expression like "fourth"; the index might instead be a fraction.
MATH_ROOT_OF = _("root of")

# Translators: This phrase is spoken to inform the user that what is about to
# be said is part of a mathematical root (square root, cube root, nth root).
# It is primarily intended to be spoken when the index of the root is not a
# simple expression. For instance, for the fourth root of 9, simply speaking
# "fourth root of 9" may be sufficient for the user. But if the index is not
# 4, but instead the fraction x/4, beginning the phrase with "root start" can
# help the user better understand that x/4 is the index of the root.
MATH_ROOT_START = _("root start")

# Translators: This phrase is spoken to inform the user that the last spoken
# phrase is the end of a mathematical root (square root, cube root, nth root).
# For instance, for the cube root of 9, Orca would say "cube root of 9, root
# end" (assuming the user settings indicate that root endings should be spoken).
MATH_ROOT_END = _("root end")

# Translators: This phrase is spoken to inform the user that what is about to
# be spoken is subscripted text in a mathematical expression. Note that the
# subscript might be simple text or may itself be a mathematical expression,
# and in this instance we have no additional context through which a more user-
# friendly word or phrase can reliably be chosen.
MATH_SUBSCRIPT = C_("math script generic", "subscript")

# Translators: This phrase is spoken to inform the user that what is about to
# be spoken is superscripted text in a mathematical expression. Note that the
# superscript might be simple text or may itself be a mathematical expression,
# and in this instance we have no additional context through which a more user-
# friendly word or phrase can reliably be chosen.
MATH_SUPERSCRIPT = C_("math script generic", "superscript")

# Translators: This phrase is spoken to inform the user that what is about to
# be spoken is subscripted text which precedes the base in a mathematical
# expression. See, for instance, the MathML mmultiscripts element:
# http://www.w3.org/TR/MathML3/chapter3.html#presm.mmultiscripts
# https://developer.mozilla.org/en-US/docs/Web/MathML/Element/mmultiscripts
MATH_PRE_SUBSCRIPT = C_("math script", "pre-subscript")

# Translators: This phrase is spoken to inform the user that what is about to
# be spoken is superscripted text which precedes the base in a mathematical
# expression. See, for instance, the MathML mmultiscripts element:
# http://www.w3.org/TR/MathML3/chapter3.html#presm.mmultiscripts
# https://developer.mozilla.org/en-US/docs/Web/MathML/Element/mmultiscripts
MATH_PRE_SUPERSCRIPT = C_("math script", "pre-superscript")

# Translators: This phrase is spoken to inform the user that what is about to
# be spoken is underscripted text in a mathematical expression. Note that the
# underscript might be simple text or may itself be a mathematical expression,
# and in this instance we have no additional context through which a more user-
# friendly word or phrase can reliably be chosen. Examples of underscripts:
# http://www.w3.org/TR/MathML/chapter3.html#presm.munder
# https://reference.wolfram.com/language/ref/Underscript.html
MATH_UNDERSCRIPT = C_("math script generic", "underscript")

# Translators: This phrase is spoken to inform the user that what is about to
# be spoken is overscripted text in a mathematical expression. Note that the
# overscript might be simple text or may itself be a mathematical expression,
# and in this instance we have no additional context through which a more user-
# friendly word or phrase can reliably be chosen. Examples of overscripts:
# http://www.w3.org/TR/MathML/chapter3.html#presm.mover
# https://reference.wolfram.com/language/ref/Overscript.html
MATH_OVERSCRIPT = C_("math script generic", "overscript")

# Translators: This phrase is spoken to inform the user that the last spoken
# phrase is the end of a mathematical table.
MATH_TABLE_END = C_("math table", "table end")

# Translators: This phrase is spoken to inform the user that the last spoken
# phrase is the end of a mathematical table which is nested inside another
# mathematical table.
MATH_NESTED_TABLE_END = C_("math table", "nested table end")

# Translators: Inaccessible means that the application cannot be read by Orca.
# This usually means the application is not friendly to the assistive technology
# infrastructure.
INACCESSIBLE = _("inaccessible")

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

# Translators: Orca announces when a widget has an associated error, such as
# disallowed characters in an input, or a must-check box that is not checked
# (e.g. "I read and agree to the terms of service."). When this error message
# goes away as a consequence of the user fixing the error, Orca will present
# this string. When translating this string please use language similar to
# that used for `C_("error", "invalid entry")` in object_properties.py.
INVALID_ENTRY_FIXED = C_("error", "Entry valid.")

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
      "To view the screen reader’s documentation, press F1. " \
      "To get a list of the screen reader’s default shortcuts, press F2. " \
      "To get a list of the screen reader’s shortcuts for the current application, " \
      "press F3. " \
      "To exit learn mode, press the escape key.")

# Translators: This message is presented when a user is navigating within a
# blockquote and then navigates out of it.
LEAVING_BLOCKQUOTE = _("leaving blockquote.")

# Translators: In web content, authors can identify an element which contains
# detailed information about another element. For instance, for a password
# field, there may be a list of requirements (number of characters, number of
# special symbols, etc.). For an image, there may be an extended description
# before or after the image. Often there are visual clues connecting the
# detailed information to its related object. We need to convey this non-visually.
# This message is presented when a user just navigated out of a container holding
# detailed information about another object.
# See https://w3c.github.io/aria/#aria-details
LEAVING_DETAILS = _("leaving details.")

# Translators: This message is presented when a user is navigating within
# an object and then navigates out of it. The word or phrase that follows
# "leaving" should be consistent with the translation provided for the
# corresponding term with context "role" found in object_properties.py
LEAVING_FEED = C_("role", "leaving feed.")

# Translators: This message is presented when a user is navigating within
# an object and then navigates out of it. The word or phrase that follows
# "leaving" should be consistent with the translation provided for the
# corresponding term with context "role" found in object_properties.py
LEAVING_FIGURE = C_("role", "leaving figure.")

# Translators: This message is presented when a user is navigating within a
# form and then navigates out of it.
LEAVING_FORM = _("leaving form.")

# Translators: This message is presented when a user is navigating within a
# panel and then navigates out of it. A grouping is a container of related
# widgets.
LEAVING_GROUPING = _("leaving grouping.")

# Translators: This message is presented when a user is navigating within
# a type of landmark and then navigates out of it. The word or phrase that
# follows "leaving" should be consistent with the translation provided for
# the corresponding term with context "role" found in object_properties.py
LEAVING_LANDMARK_BANNER = C_("role", "leaving banner.")

# Translators: This message is presented when a user is navigating within
# a type of landmark and then navigates out of it. The word or phrase that
# follows "leaving" should be consistent with the translation provided for
# the corresponding term with context "role" found in object_properties.py
LEAVING_LANDMARK_COMPLEMENTARY = C_("role", "leaving complementary content.")

# Translators: This message is presented when a user is navigating within
# a type of landmark and then navigates out of it. The word or phrase that
# follows "leaving" should be consistent with the translation provided for
# the corresponding term with context "role" found in object_properties.py
LEAVING_LANDMARK_CONTENTINFO = C_("role", "leaving information.")

# Translators: This message is presented when a user is navigating within
# a type of landmark and then navigates out of it. The word or phrase that
# follows "leaving" should be consistent with the translation provided for
# the corresponding term with context "role" found in object_properties.py
LEAVING_LANDMARK_MAIN = C_("role", "leaving main content.")

# Translators: This message is presented when a user is navigating within
# a type of landmark and then navigates out of it. The word or phrase that
# follows "leaving" should be consistent with the translation provided for
# the corresponding term with context "role" found in object_properties.py
LEAVING_LANDMARK_NAVIGATION =  C_("role", "leaving navigation.")

# Translators: This message is presented when a user is navigating within
# a type of landmark and then navigates out of it. The word or phrase that
# follows "leaving" should be consistent with the translation provided for
# the corresponding term with context "role" found in object_properties.py
LEAVING_LANDMARK_REGION =  C_("role", "leaving region.")

# Translators: This message is presented when a user is navigating within
# a type of landmark and then navigates out of it. The word or phrase that
# follows "leaving" should be consistent with the translation provided for
# the corresponding term with context "role" found in object_properties.py
LEAVING_LANDMARK_SEARCH = C_("role", "leaving search.")

# Translators: This message is presented when a user is navigating within a
# list and then navigates out of it.
LEAVING_LIST = _("leaving list.")

# Translators: This message is presented when a user is navigating within a
# panel and then navigates out of it. A panel is a generic container of
# objects, such as a group of related form fields.
LEAVING_PANEL = _("leaving panel.")

# Translators: This message is presented when a user is navigating within a
# table and then navigates out of it.
LEAVING_TABLE = _("leaving table.")

# Translators: This message is presented when a user is navigating within a
# tooltip in a web application and then navigates out of it.
LEAVING_TOOL_TIP = _("leaving tooltip.")

# Translators: This message is presented when a user is navigating within
# a document container and then navigates out of it. The word or phrase
# that follows "leaving" should be consistent with the translation provided
# for the corresponding term with context "role" found in object_properties.py
LEAVING_ABSTRACT = C_("role", "leaving abstract.")

# Translators: This message is presented when a user is navigating within
# a document container and then navigates out of it. The word or phrase
# that follows "leaving" should be consistent with the translation provided
# for the corresponding term with context "role" found in object_properties.py
LEAVING_ACKNOWLEDGMENTS = C_("role", "leaving acknowledgments.")

# Translators: This message is presented when a user is navigating within
# a document container and then navigates out of it. The word or phrase
# that follows "leaving" should be consistent with the translation provided
# for the corresponding term with context "role" found in object_properties.py
LEAVING_AFTERWORD = C_("role", "leaving afterword.")

# Translators: This message is presented when a user is navigating within
# a document container and then navigates out of it. The word or phrase
# that follows "leaving" should be consistent with the translation provided
# for the corresponding term with context "role" found in object_properties.py
LEAVING_APPENDIX = C_("role", "leaving appendix.")

# Translators: This message is presented when a user is navigating within
# a document container and then navigates out of it. The word or phrase
# that follows "leaving" should be consistent with the translation provided
# for the corresponding term with context "role" found in object_properties.py
LEAVING_BIBLIOGRAPHY = C_("role", "leaving bibliography.")

# Translators: This message is presented when a user is navigating within
# a document container and then navigates out of it. The word or phrase
# that follows "leaving" should be consistent with the translation provided
# for the corresponding term with context "role" found in object_properties.py
LEAVING_CHAPTER = C_("role", "leaving chapter.")

# Translators: This message is presented when a user is navigating within
# a document container and then navigates out of it. The word or phrase
# that follows "leaving" should be consistent with the translation provided
# for the corresponding term with context "role" found in object_properties.py
LEAVING_COLOPHON = C_("role", "leaving colophon.")

# Translators: This message is presented when a user is navigating within
# a document container and then navigates out of it. The word or phrase
# that follows "leaving" should be consistent with the translation provided
# for the corresponding term with context "role" found in object_properties.py
LEAVING_CONCLUSION = C_("role", "leaving conclusion.")

# Translators: This message is presented when a user is navigating within
# a document container and then navigates out of it. The word or phrase
# that follows "leaving" should be consistent with the translation provided
# for the corresponding term with context "role" found in object_properties.py
LEAVING_CREDIT = C_("role", "leaving credit.")

# Translators: This message is presented when a user is navigating within
# a document container and then navigates out of it. The word or phrase
# that follows "leaving" should be consistent with the translation provided
# for the corresponding term with context "role" found in object_properties.py
LEAVING_CREDITS = C_("role", "leaving credits.")

# Translators: This message is presented when a user is navigating within
# a document container and then navigates out of it. The word or phrase
# that follows "leaving" should be consistent with the translation provided
# for the corresponding term with context "role" found in object_properties.py
LEAVING_DEDICATION = C_("role", "leaving dedication.")

# Translators: This message is presented when a user is navigating within
# a document container and then navigates out of it. The word or phrase
# that follows "leaving" should be consistent with the translation provided
# for the corresponding term with context "role" found in object_properties.py
LEAVING_ENDNOTES = C_("role", "leaving endnotes.")

# Translators: This message is presented when a user is navigating within
# a document container and then navigates out of it. The word or phrase
# that follows "leaving" should be consistent with the translation provided
# for the corresponding term with context "role" found in object_properties.py
LEAVING_EPIGRAPH = C_("role", "leaving epigraph.")

# Translators: This message is presented when a user is navigating within
# a document container and then navigates out of it. The word or phrase
# that follows "leaving" should be consistent with the translation provided
# for the corresponding term with context "role" found in object_properties.py
LEAVING_EPILOGUE = C_("role", "leaving epilogue.")

# Translators: This message is presented when a user is navigating within
# a document container and then navigates out of it. The word or phrase
# that follows "leaving" should be consistent with the translation provided
# for the corresponding term with context "role" found in object_properties.py
LEAVING_ERRATA = C_("role", "leaving errata.")

# Translators: This message is presented when a user is navigating within
# a document container and then navigates out of it. The word or phrase
# that follows "leaving" should be consistent with the translation provided
# for the corresponding term with context "role" found in object_properties.py
LEAVING_EXAMPLE = C_("role", "leaving example.")

# Translators: This message is presented when a user is navigating within
# a document container and then navigates out of it. The word or phrase
# that follows "leaving" should be consistent with the translation provided
# for the corresponding term with context "role" found in object_properties.py
LEAVING_FOREWORD = C_("role", "leaving foreword.")

# Translators: This message is presented when a user is navigating within
# a document container and then navigates out of it. The word or phrase
# that follows "leaving" should be consistent with the translation provided
# for the corresponding term with context "role" found in object_properties.py
LEAVING_GLOSSARY = C_("role", "leaving glossary.")

# Translators: This message is presented when a user is navigating within
# a document container and then navigates out of it. The word or phrase
# that follows "leaving" should be consistent with the translation provided
# for the corresponding term with context "role" found in object_properties.py
LEAVING_INDEX = C_("role", "leaving index.")

# Translators: This message is presented when a user is navigating within
# a document container and then navigates out of it. The word or phrase
# that follows "leaving" should be consistent with the translation provided
# for the corresponding term with context "role" found in object_properties.py
LEAVING_INTRODUCTION = C_("role", "leaving introduction.")

# Translators: This message is presented when a user is navigating within
# a document container and then navigates out of it. The word or phrase
# that follows "leaving" should be consistent with the translation provided
# for the corresponding term with context "role" found in object_properties.py
LEAVING_PAGELIST = C_("role", "leaving page list.")

# Translators: This message is presented when a user is navigating within
# a document container and then navigates out of it. The word or phrase
# that follows "leaving" should be consistent with the translation provided
# for the corresponding term with context "role" found in object_properties.py
LEAVING_PART = C_("role", "leaving part.")

# Translators: This message is presented when a user is navigating within
# a document container and then navigates out of it. The word or phrase
# that follows "leaving" should be consistent with the translation provided
# for the corresponding term with context "role" found in object_properties.py
LEAVING_PREFACE = C_("role", "leaving preface.")

# Translators: This message is presented when a user is navigating within
# a document container and then navigates out of it. The word or phrase
# that follows "leaving" should be consistent with the translation provided
# for the corresponding term with context "role" found in object_properties.py
LEAVING_PROLOGUE = C_("role", "leaving prologue.")

# Translators: This message is presented when a user is navigating within
# a document container and then navigates out of it. The word or phrase
# that follows "leaving" should be consistent with the translation provided
# for the corresponding term with context "role" found in object_properties.py
LEAVING_PULLQUOTE = C_("role", "leaving pullquote.")

# Translators: This message is presented when a user is navigating within
# a document container and then navigates out of it. The word or phrase
# that follows "leaving" should be consistent with the translation provided
# for the corresponding term with context "role" found in object_properties.py
LEAVING_QNA = C_("role", "leaving QNA.")

# Translators: This message is presented when a user is navigating within a
# suggestion and then navigates out of it. A "suggestion" is a container with
# a proposed change. This change can include the insertion and/or deletion
# of content, and would typically be seen in a collaborative editor, such as
# in Google Docs.
LEAVING_SUGGESTION = C_("role", "leaving suggestion.")

# Translators: This message is presented when a user is navigating within
# a document container and then navigates out of it. The word or phrase
# that follows "leaving" should be consistent with the translation provided
# for the corresponding term with context "role" found in object_properties.py
LEAVING_TOC = C_("role", "leaving table of contents.")

# Translators: Orca has a "Learn Mode" that will allow the user to type any key
# on the keyboard and hear what the effects of that key would be.  The effects
# might be what Orca would do if it had a handler for the particular key
# combination, or they might just be to echo the name of the key if Orca doesn't
# have a handler. This message is what is presented in speech and braille when
# exiting Learn Mode.
LEARN_MODE_STOP = _("Exiting learn mode.")

# Translators: this indicates that this piece of text is a hypertext link.
LINK = _("link")

# Translators: this is an indication that a given link points to an object
# that is on the same page.
LINK_SAME_PAGE = _("same page")

# Translators: this is an indication that a given link points to an object
# that is at the same site (but not on the same page as the link).
LINK_SAME_SITE = _("same site")

# Translators: this is an indication that a given link points to an object
# that is at a different site than that of the link.
LINK_DIFFERENT_SITE = _("different site")

# Translators: this refers to a link to a file, where the first item is the
# protocol (ftp, ftps, or file) and the second item the name of the file being
# linked to.
LINK_TO_FILE = _("%(uri)s link to %(file)s")

# Translators: this message conveys the protocol of a link eg. http, mailto.
LINK_WITH_PROTOCOL = _("%s link")

# Translators: this message conveys the protocol of a link eg. http, mailto.
# along with the visited state of that link.
LINK_WITH_PROTOCOL_VISITED = _("visited %s link")

# Translators: The following string instructs the user how to navigate amongst
# the list of commands presented in learn mode, as well as how to exit the list
# when finished.
LIST_NAVIGATION = \
    _("Use Up and Down Arrow to navigate the list. Press Escape to exit.")

# Translators: A live region is an area of a web page that is periodically
# updated, e.g. stock ticker. http://www.w3.org/TR/wai-aria/terms#def_liveregion
# The "politeness" level is an indication of when the user wishes to be notified
# about a change to live region content. Examples include: never ("off"), when
# idle ("polite"), and when there is a change ("assertive"). Orca has several
# features to facilitate accessing live regions. This message is presented to
# inform the user that Orca's live region's "politeness" level has changed to
# "off" for all of the live regions.
LIVE_REGIONS_ALL_OFF = _("All live regions set to off")

# Translators: A live region is an area of a web page that is periodically
# updated, e.g. stock ticker. http://www.w3.org/TR/wai-aria/terms#def_liveregion
# The "politeness" level is an indication of when the user wishes to be notified
# about a change to live region content. Examples include: never ("off"), when
# idle ("polite"), and when there is a change ("assertive"). Orca has several
# features to facilitate accessing live regions. This message is presented to
# inform the user that Orca's live region's "politeness" level for all live
# regions has been restored to their original values.
LIVE_REGIONS_ALL_RESTORED = _("live regions politeness levels restored")

# Translators: A live region is an area of a web page that is periodically
# updated, e.g. stock ticker. http://www.w3.org/TR/wai-aria/terms#def_liveregion
# The "politeness" level is an indication of when the user wishes to be notified
# about a change to live region content. Examples include: never ("off"), when
# idle ("polite"), and when there is a change ("assertive"). Orca has several
# features to facilitate accessing live regions. This message is presented to
# inform the user of the "politeness" level for the current live region.
LIVE_REGIONS_LEVEL = _("politeness level %s")

# Translators: A live region is an area of a web page that is periodically
# updated, e.g. stock ticker. http://www.w3.org/TR/wai-aria/terms#def_liveregion
# The "politeness" level is an indication of when the user wishes to be notified
# about a change to live region content. Examples include: never ("off"), when
# idle ("polite"), and when there is a change ("assertive"). Orca has several
# features to facilitate accessing live regions. This message is presented to
# inform the user that Orca's live region's "politeness" level has changed for
# the current live region.
LIVE_REGIONS_LEVEL_ASSERTIVE = _("setting live region to assertive")

# Translators: A live region is an area of a web page that is periodically
# updated, e.g. stock ticker. http://www.w3.org/TR/wai-aria/terms#def_liveregion
# The "politeness" level is an indication of when the user wishes to be notified
# about a change to live region content. Examples include: never ("off"), when
# idle ("polite"), and when there is a change ("assertive"). Orca has several
# features to facilitate accessing live regions. This message is presented to
# inform the user that Orca's live region's "politeness" level has changed for
# the current live region.
LIVE_REGIONS_LEVEL_OFF = _("setting live region to off")

# Translators: A live region is an area of a web page that is periodically
# updated, e.g. stock ticker. http://www.w3.org/TR/wai-aria/terms#def_liveregion
# The "politeness" level is an indication of when the user wishes to be notified
# about a change to live region content. Examples include: never ("off"), when
# idle ("polite"), and when there is a change ("assertive"). Orca has several
# features to facilitate accessing live regions. This message is presented to
# inform the user that Orca's live region's "politeness" level has changed for
# the current live region.
LIVE_REGIONS_LEVEL_POLITE = _("setting live region to polite")

# Translators: A live region is an area of a web page that is periodically
# updated, e.g. stock ticker. http://www.w3.org/TR/wai-aria/terms#def_liveregion
# Orca has several features to facilitate accessing live regions. This message
# is presented in response to a command that toggles whether or not Orca pays
# attention to changes in live regions. Note that turning off monitoring of live
# events is NOT the same as turning the politeness level to "off". The user can
# opt to have no notifications presented (politeness level of "off") and still
# manually review recent updates to live regions via Orca commands for doing so
# -- as long as the monitoring of live regions is enabled.
LIVE_REGIONS_MONITORING_OFF = _("Live regions monitoring off")

# Translators: A live region is an area of a web page that is periodically
# updated, e.g. stock ticker. http://www.w3.org/TR/wai-aria/terms#def_liveregion
# Orca has several features to facilitate accessing live regions. This message
# is presented in response to a command that toggles whether or not Orca pays
# attention to changes in live regions. Note that turning off monitoring of live
# events is NOT the same as turning the politeness level to "off". The user can
# opt to have no notifications presented (politeness level of "off") and still
# manually review recent updates to live regions via Orca commands for doing so
# -- as long as the monitoring of live regions is enabled.
LIVE_REGIONS_MONITORING_ON = _("Live regions monitoring on")

# Translators: A live region is an area of a web page that is periodically
# updated, e.g. stock ticker. http://www.w3.org/TR/wai-aria/terms#def_liveregion
# Orca has several features to facilitate accessing live regions. This message
# is presented to inform the user that a cached message is not available for the
# the current live region.
LIVE_REGIONS_NO_MESSAGE = _("no live message saved")

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

# Translators: This string is used to present the state of a locking key, such
# as Caps Lock. If Caps Lock is "off", then letters typed will appear in
# lowercase; if Caps Lock is "on", they will instead appear in uppercase. This
# string is also applied to Num Lock and potentially will be applied to similar
# keys in the future.
LOCKING_KEY_STATE_OFF = C_("locking key state", "off")

# Translators: This string is used to present the state of a locking key, such
# as Caps Lock. If Caps Lock is "off", then letters typed will appear in
# lowercase; if Caps Lock is "on", they will instead appear in uppercase. This
# string is also applied to Num Lock and potentially will be applied to similar
# keys in the future.
LOCKING_KEY_STATE_ON = C_("locking key state", "on")

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

# Translators: Orca has a number of commands that override the default
# behavior within an application. For instance, on a web page, "h" moves
# you to the next heading. What should happen when you press an "h" in
# an entry on a web page depends: If you want to resume reading content,
# "h" should move to the next heading; if you want to enter text, "h"
# should not move you to the next heading. Similarly, if you are
# at the bottom of an entry and press Down arrow, should you leave the
# entry? Again, it depends on if you want to resume reading content or
# if you are editing the text in the entry. Because Orca doesn't know
# what you want to do, it has two modes: In browse mode, Orca treats
# key presses as commands to read the content; in focus mode, Orca treats
# key presses as something that should be handled by the focused widget.
# This string is the message presented when Orca switches to browse mode.
MODE_BROWSE = _("Browse mode")

# Translators: Orca has a number of commands that override the default
# behavior within an application. For instance, on a web page, "h" moves
# you to the next heading. What should happen when you press an "h" in
# an entry on a web page depends: If you want to resume reading content,
# "h" should move to the next heading; if you want to enter text, "h"
# should not move you to the next heading. Similarly, if you are
# at the bottom of an entry and press Down arrow, should you leave the
# entry? Again, it depends on if you want to resume reading content or
# if you are editing the text in the entry. Because Orca doesn't know
# what you want to do, it has two modes: In browse mode, Orca treats
# key presses as commands to read the content; in focus mode, Orca treats
# key presses as something that should be handled by the focused widget.
# This string is the message presented when Orca switches to focus mode.
MODE_FOCUS = _("Focus mode")

# Translators: Orca has a number of commands that override the default
# behavior within an application. For instance, on a web page, "h" moves
# you to the next heading. What should happen when you press an "h" in
# an entry on a web page depends: If you want to resume reading content,
# "h" should move to the next heading; if you want to enter text, "h"
# should not move you to the next heading. Similarly, if you are
# at the bottom of an entry and press Down arrow, should you leave the
# entry? Again, it depends on if you want to resume reading content or
# if you are editing the text in the entry. Because Orca doesn't know
# what you want to do, it has two modes: In browse mode, Orca treats
# key presses as commands to read the content; in focus mode, Orca treats
# key presses as something that should be handled by the focused widget.
# This string is a tutorial message presented to the user who has just
# navigated to a widget in browse mode to inform them of the keystroke
# they must press to enable focus mode for the purposes of interacting
# with the widget. The substituted string is a human-consumable keybinding
# such as "Alt+Shift+A."
MODE_FOCUS_TUTORIAL = _("To enable focus mode press %s.")

# Translators: (Please see the previous, detailed translator notes about
# Focus mode and Browse mode.) In order to minimize the amount of work Orca
# users need to do to switch between focus mode and browse mode, Orca attempts
# to automatically switch to the mode which is appropriate to the current
# web element. Sometimes, however, this automatic mode switching is not what
# the user wants. A good example being web apps which have their own keyboard
# navigation and use interaction model. As a result, Orca has a command which
# enables setting a "sticky" focus mode which disables all automatic toggling.
# This string is the message presented when Orca switches to sticky focus mode.
MODE_FOCUS_IS_STICKY = _("Focus mode is sticky.")

# Translators: (Please see the previous, detailed translator notes about
# Focus mode and Browse mode.) In order to minimize the amount of work Orca
# users need to do to switch between focus mode and browse mode, Orca attempts
# to automatically switch to the mode which is appropriate to the current
# web element. Sometimes, however, this automatic mode switching is not what
# the user wants. A good example being web apps which have their own keyboard
# navigation and use interaction model. As a result, Orca has a command which
# enables setting a "sticky" browse mode which disables all automatic toggling.
# This string is the message presented when Orca switches to sticky browse mode.
MODE_BROWSE_IS_STICKY = _("Browse mode is sticky.")

# Translators: When presenting the content of a line on a web page, Orca by
# default presents the full line, including any links or form fields on that
# line, in order to reflect the on-screen layout as seen by sighted users.
# Not all users like this presentation, however, and prefer to have objects
# treated as if they were on individual lines, such as is done by Windows
# screen readers, so that unrelated objects (e.g. links in a navbar) are not
# all jumbled together. As a result, this is now configurable. If layout mode
# is enabled, Orca will present the full line as it appears on the screen; if
# it is disabled, Orca will treat each object as if it were on a separate line,
# both for presentation and navigation. This string is presented when the user
# switches to layout mode via an Orca command.
MODE_LAYOUT = _("Layout mode.")

# Translators: When presenting the content of a line on a web page, Orca by
# default presents the full line, including any links or form fields on that
# line, in order to reflect the on-screen layout as seen by sighted users.
# Not all users like this presentation, however, and prefer to have objects
# treated as if they were on individual lines, such as is done by Windows
# screen readers, so that unrelated objects (e.g. links in a navbar) are not
# all jumbled together. As a result, this is now configurable. If layout mode
# is enabled, Orca will present the full line as it appears on the screen; if
# it is disabled, Orca will treat each object as if it were on a separate line,
# both for presentation and navigation. This string is presented when the user
# toggles layout mode off via an Orca command and switches to the aforementioned
# object-based presentation.
MODE_OBJECT = _("Object mode.")

# Translators: This message is presented to the user when the command to move
# the mouse pointer to a particular object is believed to have succeeded.
MOUSE_MOVED_SUCCESS = _("Pointer moved to object.")

# Translators: Orca has a feature to speak the item under the pointer. This feature,
# known as mouse review, can be enabled and disabled via command. The following is
# the message which Orca will present when mouse review is toggled off via command.
MOUSE_REVIEW_DISABLED = _("Mouse review disabled.")

# Translators: Orca has a feature to speak the item under the pointer. This feature,
# known as mouse review, can be enabled and disabled via command. The following is
# the message which Orca will present when mouse review is toggled on via command.
MOUSE_REVIEW_ENABLED = _("Mouse review enabled.")

# Translators: Orca has a command that presents a list of structural navigation
# objects in a dialog box so that users can navigate more quickly than they
# could with native keyboard navigation. This is a message that will be
# presented to the user when an error (such as the operation timing out) kept us
# from getting these objects.
NAVIGATION_DIALOG_ERROR = _("Error: Could not create list of objects.")

# Translators: the object navigator allows users to explore UI objects presented
# as a hierarchy. This message is spoken when the current node in the hierarchy
# has no children.
NAVIGATOR_NO_CHILDREN = _("No children.")

# Translators: the object navigator allows users to explore UI objects presented
# as a hierarchy. This message is spoken when the current node in the hierarchy
# has no next sibling.
NAVIGATOR_NO_NEXT = _("No next.")

# Translators: the object navigator allows users to explore UI objects presented
# as a hierarchy. This message is spoken when the current node in the hierarchy
# has no parent.
NAVIGATOR_NO_PARENT = _("No parent.")

# Translators: the object navigator allows users to explore UI objects presented
# as a hierarchy. This message is spoken when the current node in the hierarchy
# has no previous sibling.
NAVIGATOR_NO_PREVIOUS = _("No previous.")

# Translators: the object navigator allows users to explore UI objects presented
# as a hierarchy. This hierarchy can be simplified to aid with navigation. This
# message is spoken when the simplified view is enabled.
NAVIGATOR_SIMPLIFIED_ENABLED = _("Simplified navigation enabled.")

# Translators: the object navigator allows users to explore UI objects presented
# as a hierarchy. This hierarchy can be simplified to aid with navigation. This
# message is spoken when the simplified view is disabled.
NAVIGATOR_SIMPLIFIED_DISABLED = _("Simplified navigation disabled.")

# Translators: This message describes a list item in a document. Nesting level
# is how "deep" the item is (e.g., a level of 2 represents a list item inside a
# list that's inside another list).
NESTING_LEVEL = _("Nesting level %d")

# Translators: Orca has a command that moves the mouse pointer to the current
# location on a web page. If moving the mouse pointer caused an item to appear
# such as a pop-up menu, we want to present that fact.
NEW_ITEM_ADDED = _("New item has been added")

# Translators: Orca has a command which presents a menu with accessible actions
# that can be performed on the current object. This is the message that Orca
# presents when the object has no actions. The string substitution will be the
# name of the object if it has a name (e.g. "OK" or "Close") or it's accessible,
# localized rolename if it does not.
NO_ACTIONS_FOUND_ON = _("No actions found on: %s")

# Translators: This is intended to be a short phrase to present the fact that no
# no accessible component has keyboard focus.
NO_FOCUS =  _("No focus")

# Translators: This message presents the fact that no accessible application has
# has keyboard focus.
NO_FOCUSED_APPLICATION =  _("No application has focus.")

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
NO_MORE_LARGE_OBJECTS = _("No more large objects.")

# Translators: This is for navigating document content by moving amongst web
# elements which have an "onClick" action. This is a detailed message which
# will be presented to the user if no more clickable elements can be found.
NO_MORE_CLICKABLES = _("No more clickables.")

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

# Translators: This is for navigating document content by moving from iframe
# to iframe. This is a detailed message which will be presented to the user
# if no more iframes can be found.
NO_MORE_IFRAMES = _("No more internal frames.")

# Translators: This is for navigating document content by moving from image
# to image. This is a detailed message which will be presented to the user
# if no more images can be found.
NO_MORE_IMAGES = _("No more images.")

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

# Translators: Orca has a dedicated command to speak the currently-selected
# text. This message is what Orca will present if the user performs this
# command when no text is selected.
NO_SELECTED_TEXT = _("No selected text.")

# Translators: Orca has a dedicated command to speak detailed information
# about the currently-focused link. This message is what Orca will present
# if the user performs this command when not on a link.
NOT_ON_A_LINK = _("Not on a link.")

# Translators: Orca has commands to navigate among objects by object type.
# When the user moves to a focusable object, such as a button, Orca grabs
# focus on the object. This should update the focus in the GUI, e.g. so the
# user could then use native application keyboard shortcuts (Tab, Space, Enter)
# to interact with the application. Unfortunately, not all apps support
# updating the focus in response to a grab. Therefore Orca will present this
# message to indicate that the focus was not updated.
NOT_FOCUSED = _("Not focused.")

# Translators: This message alerts the user to the fact that what will be
# presented next came from a notification.
NOTIFICATION = _("Notification")

# Translators: This is a brief message presented to the user when the bottom of
# the list of notifications is reached.
NOTIFICATION_LIST_BOTTOM = C_("notification", "Bottom")

# Translators: This is a brief message presented to the user when the top of the
# list of notifications is reached.
NOTIFICATION_LIST_TOP = C_("notification", "Top")

# Translators: This message is presented to the user when the notifications list
# is empty.
NOTIFICATION_NO_MESSAGES = _("No notification messages")

# Translators: Orca has a setting through which users can control how a number is
# spoken. The options are digits ("1 2 3") and words ("one hundred and twenty
# three"). There is an associated Orca command for quickly toggling between the
# two options. This string to be translated is the brief message spoken when the
# user has enabled speaking numbers as digits.
NUMBER_STYLE_DIGITS_BRIEF = C_("number style", "digits")

# Translators: Orca has a setting through which users can control how a number is
# spoken. The options are digits ("1 2 3") and words ("one hundred and twenty
# three"). There is an associated Orca command for quickly toggling between the
# two options. This string to be translated is the verbose message spoken when
# the user has enabled speaking numbers as digits.
NUMBER_STYLE_DIGITS_FULL = _("Speak numbers as digits.")

# Translators: Orca has a setting through which users can control how a number is
# spoken. The options are digits ("1 2 3") and words ("one hundred and twenty
# three"). There is an associated Orca command for quickly toggling between the
# two options. This string to be translated is the brief message spoken when the
# user has enabled speaking numbers as words.
NUMBER_STYLE_WORDS_BRIEF = C_("number style", "words")

# Translators: Orca has a setting through which users can control how a number is
# spoken. The options are digits ("1 2 3") and words ("one hundred and twenty
# three"). There is an associated Orca command for quickly toggling between the
# two options. This string to be translated is the verbose message spoken when
# the user has enabled speaking numbers as words.
NUMBER_STYLE_WORDS_FULL = _("Speak numbers as words.")

# Translators: This brief message is presented to indicate the state of widgets
# (checkboxes, push buttons, toggle buttons) on a toolbar which are associated
# with text formatting (bold, italics, underlining, justification, etc.).
OFF = _("off")

# Translators: This brief message is presented to indicate the state of widgets
# (checkboxes, push buttons, toggle buttons) on a toolbar which are associated
# with text formatting (bold, italics, underlining, justification, etc.).
ON = _("on")

# Translators: This message is presented to the user when a web page or similar
# item has started loading.
PAGE_LOADING_START = _("Loading.  Please wait.")

# Translators: This message is presented to the user when a web page or similar
# item has finished loading.
PAGE_LOADING_END = _("Finished loading.")

# Translators: This message is presented to the user when a web page or similar
# item has finished loading. The string substitution is for the name of the
# object which has just finished loading (most likely the page's title).
PAGE_LOADING_END_NAMED = _("Finished loading %s.")

# Translators: This message is presented to the user when the page of the
# current document changes, e.g. as a result of navigation or scrolling.
# The string substitution is the number of the current page.
PAGE_NUMBER = _("Page %d")

# Translators: When the user loads a new web page, they can optionally have Orca
# automatically summarize details about the page, such as the number of elements
# (landmarks, forms, links, tables, etc.). The following string precedes the
# presentation of the summary. The string substitution is a list of items, such
# as "10 headings, 1 form, 52 links".
PAGE_SUMMARY_PREFIX = _("Page has %s.")

# Translators: This message appears in a warning dialog when the user performs
# the command to get into Orca's preferences dialog when the preferences dialog
# is already open.
PREFERENCES_WARNING_DIALOG = \
    _('You already have an instance of an Orca preferences dialog ' \
      'open.\nPlease close it before opening a new one.')

# Translators: This message is an indication of the position of the focused
# slide and the total number of slides in the presentation.
PRESENTATION_SLIDE_POSITION = _("slide %(position)d of %(count)d")

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
# All punctuation marks will be spoken, None will be spoken, Most will be
# spoken, or Some will be spoken.
PUNCTUATION_ALL_BRIEF = C_("spoken punctuation", "All")

# Translators: This detailed message will be presented as the user cycles
# through the different levels of spoken punctuation. The options are:
# All punctuation marks will be spoken, None will be spoken, Most will be
# spoken, or Some will be spoken.
PUNCTUATION_ALL_FULL = _("Punctuation level set to all.")

# Translators: This brief message will be presented as the user cycles
# through the different levels of spoken punctuation. The options are:
# All punctuation marks will be spoken, None will be spoken, Most will be
# spoken, or Some will be spoken.
PUNCTUATION_MOST_BRIEF = C_("spoken punctuation", "Most")

# Translators: This detailed message will be presented as the user cycles
# through the different levels of spoken punctuation. The options are:
# All punctuation marks will be spoken, None will be spoken, Most will be
# spoken, or Some will be spoken.
PUNCTUATION_MOST_FULL = _("Punctuation level set to most.")

# Translators: This brief message will be presented as the user cycles
# through the different levels of spoken punctuation. The options are:
# All punctuation marks will be spoken, None will be spoken, Most will be
# spoken, or Some will be spoken.
PUNCTUATION_NONE_BRIEF = C_("spoken punctuation", "None")

# Translators: This detailed message will be presented as the user cycles
# through the different levels of spoken punctuation. The options are:
# All punctuation marks will be spoken, None will be spoken, Most will be
# spoken, or Some will be spoken.
PUNCTUATION_NONE_FULL = _("Punctuation level set to none.")

# Translators: This brief message will be presented as the user cycles
# through the different levels of spoken punctuation. The options are:
# All punctuation marks will be spoken, None will be spoken, Most will be
# spoken, or Some will be spoken.
PUNCTUATION_SOME_BRIEF = C_("spoken punctuation", "Some")

# Translators: This detailed message will be presented as the user cycles
# through the different levels of spoken punctuation. The options are:
# All punctuation marks will be spoken, None will be spoken, Most will be
# spoken, or Some will be spoken.
PUNCTUATION_SOME_FULL = _("Punctuation level set to some.")

# Translators: This message is presented to indicate that a search has begun
# or is still taking place.
SEARCHING = _("Searching.")

# Translators: This message is presented to indicate a search executed by the
# user has been completed.
SEARCH_COMPLETE = _("Search complete.")

# Translators: This message is presented to the user when Orca's preferences
# have been reloaded.
SETTINGS_RELOADED = _("Screen reader settings reloaded.")

# Translators: Orca has a dedicated command to speak the currently-selected
# text. This message is spoken by Orca before speaking the text which is
# selected. The string substitution is for the selected text.
SELECTED_TEXT_IS = _("Selected text is: %s")

# Translators: Orca normal speaks the text which was just deleted from a
# document via command. Depending on the circumstances, that might be a
# large string. Therefore, if the text which has just been deleted from a
# document matches the previously-selected contents, Orca will indicate that
# fact instead of presenting the full string which was just deleted.
SELECTION_DELETED = _("Selection deleted.")

# Translators: Orca normal speaks the text which was just inserted into a
# document via command. Depending on the circumstances, that might be a
# large string. Therefore, if the text which has just been inserted into a
# document is also already selected, it is likely that the insertion is
# due to having been restored (e.g. the user selected text, deleted it,
# and then pressed Ctrl+Z to undo that deletion). In this instance, Orca
# will indicate the restoration rather than presenting the full string
# which was just inserted.
SELECTION_RESTORED = _("Selection restored.")

# Translators: This message is presented to the user when text had been
# selected in a document and no longer is, e.g. as the result of navigating
# without holding down the shift key.
SELECTION_REMOVED = _("Text unselected.")

# Translators: Orca has a command which presents the size and position of the
# current object in pixels. This string refers to the brief/non-verbose output
# presented in response to the command. The string substitutions are all for
# quantities (in pixels).
SIZE_AND_POSITION_BRIEF = _("Size: %d, %d. Location: %d, %d.")

# Translators: Orca has a command which presents the size and position of the
# current object in pixels. This string refers to the full/verbose output
# presented in response to the command. The string substitutions are all for
# quantities (in pixels).
SIZE_AND_POSITION_FULL = _("Width: %d. Height: %d. %d from left. %d from top.")

# Translators: This message is presented to the user when speech synthesis
# has been temporarily turned off.
SPEECH_DISABLED = _("Speech disabled.")

# Translators: This message is presented to the user when speech synthesis
# has been turned back on.
SPEECH_ENABLED = _("Speech enabled.")

# Translators: Orca has a sleep mode which causes Orca to essentially behave as
# if it were not running for a given application. Some use cases include self-
# voicing apps with associated commands (e.g. ChromeVox) and VMs. In the former
# case, the self-voicing app is expected to provide all needed commands as well
# as speech and braille. In the latter case, we want to ensure that Orca's
# commands and speech/braille do not interfere with that of the VM and any
# screen reader being used in that VM. Thus when an application is being used
# in sleep mode, nearly all Orca commands become unbound/free, and nothing is
# spoken or brailled. But if the user toggles sleep mode off or switches to
# another application window, Orca commands, speech, and braille immediately
# resume working. This string is the message Orca presents when sleep mode is
# disabled by the user. The string substitution is the name of the application.
# For example "Sleep mode disabled for VirtualBox."
SLEEP_MODE_DISABLED_FOR = _("Sleep mode disabled for %s.")

# Translators: Orca has a sleep mode which causes Orca to essentially behave as
# if it were not running for a given application. Some use cases include self-
# voicing apps with associated commands (e.g. ChromeVox) and VMs. In the former
# case, the self-voicing app is expected to provide all needed commands as well
# as speech and braille. In the latter case, we want to ensure that Orca's
# commands and speech/braille do not interfere with that of the VM and any
# screen reader being used in that VM. Thus when an application is being used
# in sleep mode, nearly all Orca commands become unbound/free, and nothing is
# spoken or brailled. But if the user toggles sleep mode off or switches to
# another application window, Orca commands, speech, and braille immediately
# resume working. This string is the message Orca presents when sleep mode is
# enabled by the user. The string substitution is the name of the application.
# For example "Sleep mode enabled for VirtualBox."
SLEEP_MODE_ENABLED_FOR = _("Sleep mode enabled for %s.")

# Translators: This string announces speech rate change.
SPEECH_FASTER = _("faster.")

# Translators: This string announces speech rate change.
SPEECH_SLOWER = _("slower.")

# Translators: This string announces speech pitch change.
SPEECH_HIGHER = _("higher.")

# Translators: This string announces speech pitch change.
SPEECH_LOWER  = _("lower.")

# Translators: This string announces speech volume change.
SPEECH_LOUDER = _("louder.")

# Translators: This string announces speech volume change.
SPEECH_SOFTER  = _("softer.")

# Translators: Orca's verbosity levels control how much (or how little)
# Orca will speak when presenting objects as the user navigates within
# applications and reads content. The two levels are "brief" and "verbose".
# The following string is a message spoken to the user upon toggling
# this setting via command.
SPEECH_VERBOSITY_BRIEF = C_("Speech", "Verbosity level: brief")

# Translators: Orca's verbosity levels control how much (or how little)
# Orca will speak when presenting objects as the user navigates within
# applications and reads content. The two levels are "brief" and "verbose".
# The following string is a message spoken to the user upon toggling
# this setting via command.
SPEECH_VERBOSITY_VERBOSE = C_("Speech", "Verbosity level: verbose")

# Translators: We replace the ellipses (both manual and UTF-8) with a spoken
# string. The extra space you see at the beginning is because we need the
# speech synthesis engine to speak the new string well. For example, "Open..."
# turns into "Open dot dot dot".
SPOKEN_ELLIPSIS = _(" dot dot dot")

# Translators: This message is presented when the user attempts to use a
# command specific to a spreadsheet, such as reading the input line, but is
# not in a spreadsheet.
SPREADSHEET_NOT_IN_A = _("Not in a spreadsheet.")

# Translators: This message is presented to the user when Orca is launched.
START_ORCA = _("Screen reader on.")

# Translators: This message is presented to the user when Orca is quit.
STOP_ORCA = _("Screen reader off.")

# Translators: This message means speech synthesis is not installed or working.
SPEECH_UNAVAILABLE = _("Speech is unavailable.")

# Translators: Orca has a command to present the contents of the status bar.
# This is a brief message which will be presented if Orca cannot find the
# status bar (e.g. because there isn't one).
STATUS_BAR_NOT_FOUND_BRIEF = C_("status bar", "Not found")

# Translators: Orca has a command to present the contents of the status bar.
# This is a detailed message which will be presented if Orca cannot find the
# status bar (e.g. because there isn't one).
STATUS_BAR_NOT_FOUND_FULL = _("Status bar not found")

# Translators: the Orca "Find" dialog allows a user to search for text in a
# window and then move focus to that text.  For example, they may want to find
# the "OK" button.  This message lets them know a string they were searching
# for was not found.
STRING_NOT_FOUND = _("string not found")

# Translators: The structural navigation keys are designed to move around in
# a document or other container by object type. H moves you to the next heading,
# Shift H to the previous heading, T to the next table, and so on. This message
# is presented when the user disables the structural navigation feature of Orca.
STRUCTURAL_NAVIGATION_KEYS_OFF = _("Structural navigation disabled")

# Translators: The structural navigation keys are designed to move around in
# a document or other container by object type. H moves you to the next heading,
# Shift H to the previous heading, T to the next table, and so on. This message
# is presented when the user enables the structural navigation feature for
# navigating within the current document.
STRUCTURAL_NAVIGATION_KEYS_DOCUMENT = _("Document mode")

# Translators: The structural navigation keys are designed to move around in
# a document or other container by object type. H moves you to the next heading,
# Shift H to the previous heading, T to the next table, and so on. This message
# is presented when the user enables the structural navigation feature for
# navigating within the GUI of the current application.
STRUCTURAL_NAVIGATION_KEYS_GUI = _("GUI mode")

# Translators: Orca has a command that allows the user to move to the next
# structural navigation object. In Orca, "structural navigation" refers to
# quickly moving through a container by jumping amongst objects of a given
# type, such as from link to link, or from heading to heading, or from form
# field to form field. This is a brief message which will be presented to the
# user if the desired structural navigation object could not be found.
STRUCTURAL_NAVIGATION_NOT_FOUND = C_("structural navigation", "Not found")

# Translators: Orca has a command that allows the user to move to the next
# structural navigation object. In Orca, "structural navigation" refers to
# quickly moving through a container by jumping amongst objects of a given
# type, such as from link to link, or from heading to heading, or from form
# field to form field. In order for this functionality to work, Orca uses
# the AtspiCollection interface. If an object claims to not support that
# interface, Orca will present this message to the user to indicate that
# structural navigation is not available. This is the detailed version.
STRUCTURAL_NAVIGATION_NOT_SUPPORTED_FULL = \
    _("Not supported for this location.")

# Translators: Orca has a command that allows the user to move to the next
# structural navigation object. In Orca, "structural navigation" refers to
# quickly moving through a container by jumping amongst objects of a given
# type, such as from link to link, or from heading to heading, or from form
# field to form field. In order for this functionality to work, Orca uses
# the AtspiCollection interface. If an object claims to not support that
# interface, Orca will present this message to the user to indicate that
# structural navigation is not available. This is the brief version.
STRUCTURAL_NAVIGATION_NOT_SUPPORTED_BRIEF = \
    C_("structural navigation", "Not supported")

# Translators: This message describes the (row, col) position of a table cell.
TABLE_CELL_COORDINATES = _("Row %(row)d, column %(column)d.")

# Translators: This message is presented to indicate the user is in the last
# cell of a table in a document.
TABLE_END = _("End of table")

# Translators: When users are navigating a table, they sometimes want the entire
# row of a table read; other times they want just the current cell presented.
# This string is a message presented to the user when this setting is toggled.
TABLE_MODE_CELL = _("Speak cell")

# Translators: When users are navigating a table, they sometimes want the entire
# row of a table read; other times they want just the current cell presented.
# This string is a message presented to the user when this setting is toggled.
TABLE_MODE_ROW = _("Speak row")

# Translators: a uniform table is one in which each table cell occupies one row
# and one column (i.e. a perfect grid). In contrast, a non-uniform table is one
# in which at least one table cell occupies more than one row and/or column.
TABLE_NON_UNIFORM = _("Non-uniform")

# Translators: This is for navigating document content by moving from table cell
# to table cell. If the user gives a table navigation command but is not in a
# table, presents this message.
TABLE_NOT_IN_A = _("Not in a table.")

# Translators: Orca has commands for navigating within a table, e.g. to the
# next cell in a given direction. This string is the message that will be
# presented when those commands are disabled.
TABLE_NAVIGATION_DISABLED = _("Table navigation disabled.")

# Translators: Orca has commands for navigating within a table, e.g. to the
# next cell in a given direction. This string is the message that will be
# presented when those commands are enabled.
TABLE_NAVIGATION_ENABLED = _("Table navigation enabled.")

# Translators: This is a message presented to users when the columns in a table
# have been reordered.
TABLE_REORDERED_COLUMNS = _("Columns reordered")

# Translators: This is a message presented to users when the rows in a table
# have been reordered.
TABLE_REORDERED_ROWS = _("Rows reordered")

# Translators: this is in reference to a column in a table. The substitution
# is the index (e.g. the first column is "column 1").
TABLE_COLUMN = _("column %d")

# Translators: this is in reference to a column in a table. If the user is in
# the first column of a table with five columns, the position is "column 1 of 5"
TABLE_COLUMN_DETAILED = _("column %(index)d of %(total)d")

# Translators: This is for navigating document content by moving from table cell
# to table cell. This is the message presented when the user attempts to move to
# the cell below the current cell and is already in the last row.
TABLE_COLUMN_BOTTOM = _("Bottom of column.")

# Translators: This is for navigating document content by moving from table cell
# to table cell. This is the message presented when the user attempts to move to
# the cell above the current cell and is already in the first row.
TABLE_COLUMN_TOP = _("Top of column.")

# Translators: this message is spoken to announce that a table column just became
# selected (e.g as a result of navigation via Shift + Arrows). The string substitution
# is the column label (e.g. "B").
TABLE_COLUMN_SELECTED = _("Column %s selected")

# Translators: this message is spoken to announce that multiple table columns just
# became selected (e.g as a result of navigation via Shift + Arrows). The first
# string substitution is the label of the first column in the range. The second string
# substitution is the label in the last column in the range. An example message for
# Calc would be "Columns B through F selected".
TABLE_COLUMN_RANGE_SELECTED = _("Columns %s through %s selected")

# Translators: this message is spoken to announce that multiple table columns just
# became unselected (e.g as a result of navigation via Shift + Arrows). The first
# string substitution is the label of the first column in the range. The second string
# substitution is the label in the last column in the range. An example message for
# Calc would be "Columns B through F unselected".
TABLE_COLUMN_RANGE_UNSELECTED = _("Columns %s through %s unselected")

# Translators: this message is spoken to announce that a table column just became
# unselected (e.g as a result of navigation via Shift + Arrows). The string substitution
# is the column label (e.g. "B").
TABLE_COLUMN_UNSELECTED = _("Column %s unselected")

# Translators: this is in reference to a row in a table. The substitution is
# the index (e.g. the first row is "row 1").
TABLE_ROW = _("row %d")

# Translators: this is in reference to a row in a table. If the user is in the
# the first row of a table with five rows, the position is "row 1 of 5"
TABLE_ROW_DETAILED = _("row %(index)d of %(total)d")

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

# Translators: this message is spoken to announce that a table row just became selected
# (e.g as a result of navigation via Shift + Arrows). The string substitution is the row
# label (e.g. "2").
TABLE_ROW_SELECTED = _("Row %s selected")

# Translators: this message is spoken to announce that multiple table rows just
# became selected (e.g as a result of navigation via Shift + Arrows). The first
# string substitution is the label of the first row in the range. The second string
# substitution is the label of the last row in the range. An example message for
# Calc would be "Rows 2 through 10 selected".
TABLE_ROW_RANGE_SELECTED = _("Rows %s through %s selected")

# Translators: this message is spoken to announce that multiple table rows just
# became unselected (e.g as a result of navigation via Shift + Arrows). The first
# string substitution is the label of the first row in the range. The second string
# substitution is the label of the last row in the range. An example message for
# Calc would be "Rows 2 through 10 unselected".
TABLE_ROW_RANGE_UNSELECTED = _("Rows %s through %s unselected")

# Translators: this message is spoken to announce that a table row just became
# unselected (e.g as a result of navigation via Shift + Arrows). The string
# substitution is the row label (e.g. "2").
TABLE_ROW_UNSELECTED = _("Row %s unselected")

# Translators: when the user selects (highlights) text in a document, Orca lets
# them know.
TEXT_SELECTED = C_("text", "selected")

# Translators: when the user unselects (un-highlights) text in a document, Orca
# lets them know.
TEXT_UNSELECTED = C_("text", "unselected")

TIME_FORMAT_LOCALE = "%X"
TIME_FORMAT_24_HMS = "%H:%M:%S"
TIME_FORMAT_24_HM  = "%H:%M"
TIME_FORMAT_12_HM  = "%I:%M %p"
TIME_FORMAT_12_HMS = "%I:%M:%S %p"

# Translators: Orca has a feature to speak the time when the user presses a
# shortcut key. This is one of the alternative formats that the user may wish
# it to be presented with.
TIME_FORMAT_24_HMS_WITH_WORDS = _("%H hours, %M minutes and %S seconds")

# Translators: Orca has a feature to speak the time when the user presses a
# shortcut key. This is one of the alternative formats that the user may wish
# it to be presented with.
TIME_FORMAT_24_HM_WITH_WORDS = _("%H hours and %M minutes")

# Translators: this is information about a unicode character reported to the
# user.  The value is the unicode number value of this character in hex.
UNICODE = _("Unicode %s")

# Translators: This string is presented when an application's undo command is
# used in a document resulting in a change to that document's contents.
UNDO = C_("command", "undo")

# Translators: This string is presented when an application's redo command is
# used in a document resulting in a change to that document's contents.
REDO = C_("command", "redo")

# Translators: This message presents the Orca version number.
VERSION = _("Screen reader version %s.") % version

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

# Translators, normally layered panes and tables have items in them. Thus it is
# noteworthy when this is not the case. This message is presented to the user to
# indicate the current layered pane or table contains zero items.
ZERO_ITEMS = _("0 items")

def cell_span(rowspan, colspan):
    """Returns a string description of the cell span in a table."""

    span_string = ""
    if colspan > 1 and rowspan > 1:
        # Translators: The cell here refers to a cell within a table within a
        # document. We need to announce when the cell occupies or "spans" more
        # than a single row and/or column.
        span_string = ngettext("Cell spans %d row",
                              "Cell spans %d rows",
                              rowspan) % rowspan

        # Translators: this represents the number of columns in a table.
        span_string += ngettext(" %d column",
                               " %d columns",
                               colspan) % colspan
    elif colspan > 1:
        # Translators: The cell here refers to a cell within a table within a
        # document. We need to announce when the cell occupies or "spans" more
        # than a single row and/or column.
        span_string = ngettext("Cell spans %d column",
                              "Cell spans %d columns",
                              colspan) % colspan
    elif rowspan > 1:
        # Translators: The cell here refers to a cell within a table within a
        # document. We need to announce when the cell occupies or "spans" more
        # than a single row and/or column.
        span_string = ngettext("Cell spans %d row",
                              "Cell spans %d rows",
                              rowspan) % rowspan

    return span_string

def character_count(count):
    """Returns a string description of the number of characters in a string."""

    # Translators: This message describes the number of characters in a string.
    return ngettext("%d characters", "%d characters", count) % count

def selected_character_count(count):
    """Returns a string description of the number of selected characters in a string."""

    # Translators: This message describes the number of characters that were just
    # selected in a body of text.
    return ngettext("%d character selected", "%d characters selected", count) % count

def unselected_character_count(count):
    """Returns a string description of the number of unselected characters in a string."""

    # Translators: This message describes the number of characters that were just
    # unselected in a body of text.
    return ngettext("%d character unselected", "%d characters unselected", count) % count

def characters_too_long(count):
    """Returns a string description of the number of characters that don't fit in a cell."""

    # Translators: People can enter a string of text that is too wide to be
    # fully displayed in a spreadsheet cell. This message will be spoken if
    # such a cell is encountered.
    return ngettext("%d character too long",
                    "%d characters too long",
                    count) % count

def dialog_count_braille(count):
    """Returns a string description for braille of the number of unfocused alerts and dialogs."""

    # Translators: This message informs the user how many unfocused alert and
    # dialog windows a newly (re)focused application has. It is added at the
    # end of a braille message containing the app which just claimed focus.
    return ngettext("(%d dialog)", "(%d dialogs)", count) % count

def dialog_count_speech(count):
    """Returns a string description for speech of the number of unfocused alerts and dialogs."""

    # Translators: This message informs the user how many unfocused alert and
    # dialog windows a newly (re)focused application has. It is added at the
    # end of a spoken message containing the app which just claimed focus.
    return ngettext("%d unfocused dialog", "%d unfocused dialogs", count) % count

def file_size_bytes(size):
    """Returns a string description of the size of a file in bytes."""

    # Translators: This is the size of a file in bytes
    return ngettext("%d byte", "%d bytes", size) % size

def files_found(count):
    """Returns a string description of the number of files found."""

    # Translators: This message informs the user hoq many files were found as
    # a result of a search.
    return ngettext("%d file found", "%d files found", count) % count

def form_count(count, only_if_found=True):
    """Returns a string description of the number of forms in a document."""

    if not count and only_if_found:
        return ""

    # Translators: This message presents the number of forms in a document.
    return ngettext("%d form", "%d forms", count) % count

def heading_count(count, only_if_found=True):
    """Returns a string description of the number of headings in a document."""

    if not count and only_if_found:
        return ""

    # Translators: This message presents the number of headings in a document.
    return ngettext("%d heading", "%d headings", count) % count

def item_count(count):
    """Returns a string description of the number of items in a layered pane or table."""

    # Translators: This message presents the number of items in a layered pane
    # or table.
    return ngettext("%d item", "%d items", count) % count

def landmark_count(count, only_if_found=True):
    """Returns a string description of the number of landmarks in a document."""

    if not count and only_if_found:
        return ""

    # Translators: This message presents the number of landmarks in a document.
    # ARIA role landmarks are the W3C defined HTML tag attribute 'role' used to
    # identify important part of webpage like banners, main context, search etc.
    return ngettext("%d landmark", "%d landmarks", count) % count

def items_found(count):
    """Returns a string description of the number of items found in a search."""

    # Translators: Orca has several commands that search for, and present a list
    # of, objects based on one or more criteria. This is a message that will be
    # presented to the user to indicate how many matching items were found.
    return ngettext("%d item found", "%d items found", count) % count

def leaving_n_blockquotes(count):
    """Returns a string description of the number of blockquotes being exited."""

    # Translators: This message is presented when a user is navigating within a
    # series of nested blockquotes, such as can be seen in deep email threads,
    # and then navigates out of several levels at once.
    return ngettext("Leaving %d blockquote.", "Leaving %d blockquotes.", count) % count

def leaving_n_lists(count):
    """Returns a string description of the number of lists being exited."""

    # Translators: This message is presented when a user is navigating within a
    # series of nested lists and then navigates out of several levels at once.
    return ngettext("Leaving %d list.", "Leaving %d lists.", count) % count

def list_item_count(count):
    """Returns a string description of the number of items in a list."""

    if count == -1:
        # Translators: This message describes a list in web content for which the
        # size is unknown. Examples include unlimited scrolling news/article feeds
        # on social media sites, and message lists on services such as gmail where
        # you're currently viewing messages 1-100 out of some huge, unspecified
        # number. Normally Orca announces "list with n items" when the count is
        # known. This is the corresponding message for the unknown-count scenario.
        return _("List of unknown size")

    # Translators: This message describes a bulleted or numbered list.
    return ngettext("List with %d item", "List with %d items", count) % count

def nested_list_item_count(count):
    """Returns a string description of the number of items in a nested list."""

    # Translators: This message describes the number of items of a bulleted or numbered list
    # that is inside of another list.
    return ngettext("Nested list with %d item", "Nested list with %d items", count) % count

def feed_article_count(count):
    """Returns a string description of the number of articles in a feed."""

    if count == -1:
        # Translators: This message describes a news/article feed whose size is
        # unknown, such as can be found on social media sites that have unlimited
        # scrolling, adding and/or removing items as the user moves up or down.
        # Normally Orca announces "feed with n articles" when the count is known.
        # This is the corresponding message for the unknown-count scenario.
        return _("Feed of unknown size")

    # Translators: This message describes the number of articles (news items,
    # social media posts, etc.) in a feed.
    return ngettext("Feed with %d article", "Feed with %d articles", count) % count

def description_list_term_count(count):
    """Returns a string description of the number of terms in a description list."""

    # Translators: This message describes a description list.
    # See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/dl
    # Note that the "term" here corresponds to the "dt" element
    return ngettext("Description list with %d term",
                    "Description list with %d terms", count) % count

def tab_list_item_count(count):
    """Returns a string description of the number of items in a tab list."""

    # Translators: A GtkNotebook (https://docs.gtk.org/gtk4/class.Notebook.html) is an
    # example of a "tab list". This message describes the tab list to the user.
    return ngettext("Tab list with %d tab", "Tab list with %d tabs", count) % count

def value_count_for_term(count):
    """Returns a string description of the number of values for a term in a description list."""

    # Translators: This message describes a description list.
    # A given term ("dt" element) can have 0 or more values ("dd" elements).
    # This message presents the number values a particular term has.
    # See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/dl
    return ngettext("%d value", "%d values", count) % count

def math_table_size(n_rows, n_columns):
    """Returns a string description of the size of a mathematical table."""

    # Translators: this represents the number of rows in a mathematical table.
    # See http://www.w3.org/TR/MathML3/chapter3.html#presm.mtable
    row_string = ngettext("math table with %d row",
                          "math table with %d rows",
                          n_rows) % n_rows
    # Translators: this represents the number of columns in a mathematical table.
    # See http://www.w3.org/TR/MathML3/chapter3.html#presm.mtable
    col_string = ngettext("%d column",
                          "%d columns",
                          n_columns) % n_columns
    return row_string + " " + col_string

def math_nested_table_size(n_rows, n_columns):
    """Returns a string description of the size of a nested mathematical table."""

    # Translators: this represents the number of rows in a mathematical table
    # which is nested inside another mathematical table.
    # See http://www.w3.org/TR/MathML3/chapter3.html#presm.mtable
    row_string = ngettext("nested math table with %d row",
                          "nested math table with %d rows",
                           n_rows) % n_rows
    # Translators: this represents the number of rows in a mathematic table
    # which is nested inside another mathematical table.
    # See http://www.w3.org/TR/MathML3/chapter3.html#presm.mtable
    col_string = ngettext("%d column",
                          "%d columns",
                           n_columns) % n_columns

    return row_string + " " + col_string

def messages_count(count):
    """Returns a string description of the number of messages in a list."""

    # Translators: This message is presented to inform the user of the number of
    # messages in a list.
    return ngettext("%d message.\n", "%d messages.\n", count) % count

def percentage(value):
    """Returns a string description of a percentage value."""

    # Translators: This message is presented to inform the user of the value of
    # a slider, progress bar, or other such component.
    return ngettext("%d percent.", "%d percent.", value) % value

def percent_read(value):
    """Returns a string description of the percentage of a document that has been read."""

    # Translators: This message announces the percentage of the document that
    # has been read. The value is calculated by knowing the index of the current
    # position divided by the total number of objects on the page.
    return ngettext ("%d percent of document read",
                     "%d percent of document read",
                     value) % value

def pixel_count(n_pixels):
    """Returns a string description of the number of pixels in a measurement."""

    # Translators: this represents a text attribute expressed in pixels, such as
    # a margin, indentation, font size, etc.
    return ngettext("%d pixel", "%d pixels", n_pixels) % n_pixels

def repeated_char_count(repeated_char, count):
    """Returns a string description of the number of repeated characters in a line."""

    # Translators: Orca will tell you how many characters are repeated on a line
    # of text. For example: "22 space characters". The %d is the number and the
    # %s is the spoken word for the character.
    return ngettext("%(count)d %(repeatChar)s character",
                    "%(count)d %(repeatChar)s characters",
                    count) % {"count" : count, "repeatChar": repeated_char}

def selected_items_count(selected, total):
    """Returns a string description of the number of selected items in a group."""

    # Translators: This message is presented to indicate the number of selected
    # objects (e.g. icons) and the total number of those objects.
    return ngettext("%(index)d of %(total)d item selected",
                    "%(index)d of %(total)d items selected",
                    total) % {"index" : selected, "total" : total}

def shortcuts_found_orca(count):
    """Returns a string description of the number of Orca shortcuts found."""

    # Translators: This message is presented when the user is in a list of
    # shortcuts associated with Orca commands which are not specific to the
    # current application. It appears as the title of the dialog containing
    # the list.
    return ngettext("%d Screen reader default shortcut found.",
                    "%d Screen reader default shortcuts found.",
                    count) % count

def shortcuts_found_app(count, app_name):
    """Returns a string description of the number of Orca shortcuts found for a specific app."""

    # Translators: This message is presented when the user is in a list of
    # shortcuts associated with Orca commands specific to the current
    # application. It appears as the title of the dialog containing the list.
    return ngettext("%(count)d Screen reader shortcut for %(application)s found.",
                    "%(count)d Screen reader shortcuts for %(application)s found.",
                    count) % {"count" : count, "application" : app_name}

def spaces_count(count):
    """Returns a string description of the number of space characters in a string."""

    # Translators: This message is presented to inform the user of the number of
    # space characters in a string.
    return ngettext("%d space", "%d spaces", count) % count

def tabs_count(count):
    """Returns a string description of the number of tab characters in a string."""

    # Translators: This message is presented to inform the user of the number of
    # tab characters in a string.
    return ngettext("%d tab", "%d tabs", count) % count

def table_count(count, only_if_found=True):
    """Returns a string description of the number of tables in a document."""

    if not count and only_if_found:
        return ""

    # Translators: This message presents the number of tables in a document.
    return ngettext("%d table", "%d tables", count) % count

def table_size(n_rows, n_columns):
    """Returns a string description of the size of a table."""

    if n_rows == -1:
        if n_columns == -1:
            # Translators: This message describes a table for which both the
            # number of rows and the number of columns are unknown. Normally
            # Orca announces the table dimensions (e.g. "table with 100 rows
            # 15 columns"). When both counts are unknown, it presents this.
            return _("table of unknown size")

        # Translators: This message describes a table for which the number of
        # rows is unknown, but the number of columns is known. This might occur
        # in a vertically infinitely scrollable table or grid on the web.
        return ngettext("table with %d column, row count unknown",
                        "table with %d columns, row count unknown",
                        n_columns) % n_columns

    if n_columns == -1:
        # Translators: This message describes a table for which the number of
        # columns is unknown, but the number of rows is known. This might occur
        # in a horizontally infinitely scrollable table or grid on the web.
        return ngettext("table with %d row, column count unknown",
                        "table with %d rows, column count unknown",
                        n_rows) % n_rows

    # Translators: this represents the number of rows in a table.
    row_string = ngettext("table with %d row",
                         "table with %d rows",
                         n_rows) % n_rows

    # Translators: this represents the number of columns in a table.
    col_string = ngettext("%d column",
                         "%d columns",
                         n_columns) % n_columns

    return row_string + " " + col_string

def seconds_ago(count):
    """Returns a string description of how long ago something took place in seconds."""

    # Translators: This message informs the user how long ago something took
    # place in terms of seconds.
    return ngettext("%d second ago", "%d seconds ago", count) % count

def minutes_ago(count):
    """Returns a string description of how long ago something took place in minutes."""

    # Translators: This message informs the user how long ago something took
    # place in terms of minutes.
    return ngettext("%d minute ago", "%d minutes ago", count) % count

def hours_ago(count):
    """Returns a string description of how long ago something took place in hours."""

    # Translators: This message informs the user how long ago something took
    # place in terms of hours.
    return ngettext("%d hour ago", "%d hours ago", count) % count

def days_ago(count):
    """Returns a string description of how long ago something took place in days."""

    # Translators: This message informs the user how long ago something took
    # place in terms of days.
    return ngettext("%d day ago", "%d days ago", count) % count

def memory_usage_gb(used, total):
    """Returns a string description of the memory usage in GB."""

    # Translators: Orca has a command to report CPU and memory usage levels. This
    # message presents the amount of memory used and total amount in GB.
    return f"{used:.1f} of {total:.1f} GB used."

def memory_usage_mb(used, total):
    """Returns a string description of the memory usage in MB."""

    # Translators: Orca has a command to report CPU and memory usage levels. This
    # message presents the amount of memory used and total amount in MB.
    return f"{used:.1f} of {total:.1f} MB used."

def unvisited_link_count(count, only_if_found=True):
    """Returns a string description of the number of unvisited links in a document."""

    if not count and only_if_found:
        return ""

    # Translators: This message presents the number of unvisited links in a
    # document.
    return ngettext("%d unvisited link", "%d unvisited links", count) % count

def visited_link_count(count, only_if_found=True):
    """Returns a string description of the number of visited links in a document."""

    if not count and only_if_found:
        return ""

    # Translators: This message presents the number of visited links in a
    # document.
    return ngettext("%d visited link", "%d visited links", count) % count
