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

"""Labels for Orca's GUIs. These have been put in their own module so that we
can present them in the correct language when users change the language on the
fly without having to reload a bunch of modules."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2004-2009 Sun Microsystems Inc." \
                "Copyright (c) 2010-2013 The Orca Team"
__license__   = "LGPL"

from .orca_i18n import _, C_, ngettext # pylint: disable=import-error

# Translators: This string appears on a button in a dialog. "Activating" the
# selected item will perform the action that one would expect to occur if the
# object were clicked on with the mouse. If the object is a link, activating
# it will bring you to a new page. If the object is a button, activating it
# will press the button. If the object is a combobox, activating it will expand
# it to show all of its contents. And so on.
ACTIVATE = _("_Activate")

# Translators: Orca has a number of commands that override the default behavior
# within an application. For instance, on a web page Orca's Structural Navigation
# command "h" moves you to the next heading. What should happen when you press
# "h" in an entry on a web page depends: If you want to resume reading content,
# "h" should move to the next heading; if you want to enter text, "h" should not
# move you to the next heading. Because Orca doesn't know what you want to do,
# it has two modes: In browse mode, Orca treats key presses as commands to read
# the content; in focus mode, Orca treats key presses as something that should be
# handled by the focused widget. Orca optionally can attempt to detect which mode
# is appropriate for the current situation and switch automatically. This string
# is a label for a GUI option to enable such automatic switching when structural
# navigation commands are used. As an example, if this setting were enabled,
# pressing "e" to move to the next entry would move focus there and also turn
# focus mode on so that the next press of "e" would type an "e" into the entry.
# If this setting is not enabled, the second press of "e" would continue to be
# a navigation command to move amongst entries.
AUTO_FOCUS_MODE_STRUCT_NAV = _("Automatic focus mode during structural navigation")

# Translators: Orca has a number of commands that override the default behavior
# within an application. For instance, if you are at the bottom of an entry and
# press Down arrow, should you leave the entry? It depends on if you want to
# resume reading content or if you are editing the text in the entry. Because
# Orca doesn't know what you want to do, it has two modes: In browse mode, Orca
# treats key presses as commands to read the content; in focus mode, Orca treats
# key presses as something that should be handled by the focused widget. Orca
# optionally can attempt to detect which mode is appropriate for the current
# situation and switch automatically. This string is a label for a GUI option to
# enable such automatic switching when caret navigation commands are used. As an
# example, if this setting were enabled, pressing Down Arrow would allow you to
# move into an entry but once you had done so, Orca would switch to Focus mode
# and subsequent presses of Down Arrow would be controlled by the web browser
# and not by Orca. If this setting is not enabled, Orca would continue to control
# what happens when you press an arrow key, thus making it possible to arrow out
# of the entry.
AUTO_FOCUS_MODE_CARET_NAV = _("Automatic focus mode during caret navigation")

# Translators: Orca has a number of commands that override the default behavior
# within an application. For instance, if you are at the bottom of an entry and
# press Down arrow, should you leave the entry? It depends on if you want to
# resume reading content or if you are editing the text in the entry. Because
# Orca doesn't know what you want to do, it has two modes: In browse mode, Orca
# treats key presses as commands to read the content; in focus mode, Orca treats
# key presses as something that should be handled by the focused widget. Orca
# optionally can attempt to detect which mode is appropriate for the current
# situation and switch automatically. This string is a label for a GUI option to
# enable such automatic switching when native navigation commands are used.
# Here "native" means "not Orca"; it could be a browser navigation command such
# as the Tab key, or it might be a web page behavior, such as the search field
# automatically gaining focus when the page loads.
AUTO_FOCUS_MODE_NATIVE_NAV = _("Automatic focus mode during native navigation")

# Translators: A single braille cell on a refreshable braille display consists
# of 8 dots. Dot 7 is the dot in the bottom left corner. If the user selects
# this option, Dot 7 will be used to 'underline' text of interest, e.g. when
# "marking"/indicating that a given word is bold.
BRAILLE_DOT_7 = _("Dot _7")

# Translators: A single braille cell on a refreshable braille display consists
# of 8 dots. Dot 8 is the dot in the bottom right corner. If the user selects
# this option, Dot 8 will be used to 'underline' text of interest,  e.g. when
# "marking"/indicating that a given word is bold.
BRAILLE_DOT_8 = _("Dot _8")

# Translators: A single braille cell on a refreshable braille display consists
# of 8 dots. Dots 7-8 are the dots at the bottom. If the user selects this
# option, Dots 7-8 will be used to 'underline' text of interest,  e.g. when
# "marking"/indicating that a given word is bold.
BRAILLE_DOT_7_8 = _("Dots 7 an_d 8")

# Translators: This is the label for a button in a dialog.
BTN_CANCEL = _("_Cancel")

# Translators: This is the label for a button in a dialog.
BTN_JUMP_TO = _("_Jump to")

# Translators: This is the label for a button in a dialog.
BTN_OK = _("_OK")

# Translators: Orca uses Speech Dispatcher to present content to users via
# text-to-speech. Speech Dispatcher has a feature to control how capital
# letters are presented: Do nothing at all, say the word 'capital' prior to
# presenting a capital letter (which Speech Dispatcher refers to as 'spell'),
# or play a tone (which Speech Dispatcher refers to as a sound 'icon'.) This
# string to be translated appears as a combo box item in Orca's Preferences.
CAPITALIZATION_STYLE_ICON = C_("capitalization style", "Icon")

# Translators: Orca uses Speech Dispatcher to present content to users via
# text-to-speech. Speech Dispatcher has a feature to control how capital
# letters are presented: Do nothing at all, say the word 'capital' prior to
# presenting a capital letter (which Speech Dispatcher refers to as 'spell'),
# or play a tone (which Speech Dispatcher refers to as a sound 'icon'.) This
# string to be translated appears as a combo box item in Orca's Preferences.
CAPITALIZATION_STYLE_NONE = C_("capitalization style", "None")

# Translators: Orca uses Speech Dispatcher to present content to users via
# text-to-speech. Speech Dispatcher has a feature to control how capital
# letters are presented: Do nothing at all, say the word 'capital' prior to
# presenting a capital letter (which Speech Dispatcher refers to as 'spell'),
# or play a tone (which Speech Dispatcher refers to as a sound 'icon'.) This
# string to be translated appears as a combo box item in Orca's Preferences.
CAPITALIZATION_STYLE_SPELL = C_("capitalization style", "Spell")

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
# has focus. The string substitution is for the application name (e.g Pidgin).
CHAT_SPEAK_MESSAGES_ALL_IF_FOCUSED = _("All channels when an_y %s window is active")

# Translators: This is the label of a radio button. If it is selected, Orca will
# only speak new chat messages for the currently active channel, irrespective of
# whether the chat application has focus.
CHAT_SPEAK_MESSAGES_ACTIVE = _("A channel only if its _window is active")

# Translators: If this checkbox is checked, then Orca will speak the name of the
# chat room prior to presenting an incoming message.
CHAT_SPEAK_ROOM_NAME = _("_Speak Chat Room name")

# Translators: When presenting the content of a line on a web page, Orca by
# default presents the full line, including any links or form fields on that
# line, in order to reflect the on-screen layout as seen by sighted users.
# Not all users like this presentation, however, and prefer to have objects
# treated as if they were on individual lines, such as is done by Windows
# screen readers, so that unrelated objects (e.g. links in a navbar) are not
# all jumbled together. As a result, this is now configurable. If layout mode
# is enabled, Orca will present the full line as it appears on the screen; if
# it is disabled, Orca will treat each object as if it were on a separate line,
# both for presentation and navigation.
CONTENT_LAYOUT_MODE = _("Enable layout mode for content")

# Translators: Orca's keybindings support double and triple "clicks" or key
# presses, similar to using a mouse. This string appears in Orca's preferences
# dialog after a keybinding which requires a double click.
CLICK_COUNT_DOUBLE = _("double click")

# Translators: Orca's keybindings support double and triple "clicks" or key
# presses, similar to using a mouse. This string appears in Orca's preferences
# dialog after a keybinding which requires a triple click.
CLICK_COUNT_TRIPLE = _("triple click")

# Translators: This is a label which will appear in the list of available speech
# engines as a special item. It refers to the default engine configured within
# the speech subsystem. Apart from this item, the user will have a chance to
# select a particular speech engine by its real name (Festival, IBMTTS, etc.)
DEFAULT_SYNTHESIZER = _("Default Synthesizer")

# Translators: This is a label for a column header in Orca's pronunciation
# dictionary. The pronunciation dictionary allows the user to correct words
# which the speech synthesizer mispronounces (e.g. a person's name, a technical
# word) or doesn't pronounce as the user desires (e.g. an acronym) by providing
# an alternative string. The "Actual String" here refers to the word to be
# corrected as it would actually appear in text being read. Example: "LOL".
DICTIONARY_ACTUAL_STRING = _("Actual String")

# Translators: This is a label for a column header in Orca's pronunciation
# dictionary. The pronunciation dictionary allows the user to correct words
# which the speech synthesizer mispronounces (e.g. a person's name, a technical
# word) or doesn't pronounce as the user desires (e.g. an acronym) by providing
# an alternative string. The "Replacement String" here refers to how the user
# would like the "Actual String" to be pronounced by the speech synthesizer.
# Example: "L O L" or "Laughing Out Loud" (for Actual String "LOL").
DICTIONARY_REPLACEMENT_STRING = _("Replacement String")

# Translators: Orca has an "echo" feature to present text as it is being written
# by the user. While Orca's "key echo" options present the actual keyboard keys
# being pressed, "character echo" presents the character/string of length 1 that
# is inserted as a result of the keypress.
ECHO_CHARACTER = _("Enable echo by cha_racter")

# Translators: Orca has an "echo" feature to present text as it is being written
# by the user. This string refers to a "key echo" option. When this option is
# enabled, dead keys will be announced when pressed.
ECHO_DIACRITICAL = _("Enable non-spacing _diacritical keys")

# Translators: Orca has a "find" feature which allows the user to search the
# active application for on screen text and widgets. This string is the title
# of the dialog box.
FIND_DIALOG_TITLE = _("Find")
KB_GROUP_FIND = FIND_DIALOG_TITLE

# Translators: Orca has a "find" feature which allows the user to search the
# active application for on screen text and widgets. This label is associated
# with the text entry where the user types the term to search for.
FIND_SEARCH_FOR = _("_Search for:")

# Translators: Orca has a "find" feature which allows the user to search the
# active application for on screen text and widgets. This label is associated
# with a group of options related to where the search should begin. The options
# are to begin the search from the current location or from the top of the window.
FIND_START_FROM = _("Start from:")

# Translators: Orca has a "find" feature which allows the user to search the
# active application for on screen text and widgets. This label is associated
# with the radio button to begin the search from the current location rather
# than from the top of the window.
FIND_START_AT_CURRENT_LOCATION = _("C_urrent location")

# Translators: Orca has a "find" feature which allows the user to search the
# active application for on screen text and widgets. This label is associated
# with the radio button to begin the search from the top of the window rather
# than the current location.
FIND_START_AT_TOP_OF_WINDOW = _("_Top of window")

# Translators: Orca has a "find" feature which allows the user to search the
# active application for on screen text and widgets. This label is associated
# with a group of options related to the direction of the search. The options
# are to search backwards and to wrap.
FIND_SEARCH_DIRECTION = _("Search direction:")

# Translators: Orca has a "find" feature which allows the user to search the
# active application for on screen text and widgets. This label is associated
# with the checkbox to perform the search in the reverse direction.
FIND_SEARCH_BACKWARDS = _("Search _backwards")

# Translators: Orca has a "find" feature which allows the user to search the
# active application for on screen text and widgets. This label is associated
# with the checkbox to wrap around when the top/bottom of the window has been
# reached.
FIND_WRAP_AROUND = _("_Wrap around")

# Translators: Orca has a "find" feature which allows the user to search the
# active application for on screen text and widgets. This label is associated
# with a group of options related to what constitutes a match. The options are
# to match case and to match the entire word only.
FIND_MATCH_OPTIONS = _("Match options:")

# Translators: Orca has a "find" feature which allows the user to search the
# active application for on screen text and widgets. This label is associated
# with the checkbox to make the search case-sensitive.
FIND_MATCH_CASE = _("_Match case")

# Translators: Orca has a "find" feature which allows the user to search the
# active application for on screen text and widgets. This label is associated
# with the checkbox to only match if the full word consists of the search term.
FIND_MATCH_ENTIRE_WORD = _("Match _entire word only")

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

# Translators: Command is a table column header where the cells in the column
# are a sentence that briefly describes what action Orca will take if and when
# the user invokes that keyboard command.
KB_HEADER_FUNCTION = _("Command")

# Translators: Key Binding is a table column header where the cells in the
# column represent keyboard combinations the user can press to invoke Orca
# commands.
KB_HEADER_KEY_BINDING = _("Key Binding")

# Translators: This string is a label for the group of Orca commands which
# can be used in any setting, task, or application. They are not specific
# to, for instance, web browsing.
KB_GROUP_DEFAULT = C_("keybindings", "Default")

# Translators: This string is a label for the group of Orca commands which
# are related to debugging.
KB_GROUP_DEBUGGING_TOOLS = C_("keybindings", "Debugging Tools")

# Translators: This string is a label for the group of Orca commands which
# are related to its "learn mode". Please use the same translation as done
# in cmdnames.py
KB_GROUP_LEARN_MODE = C_("keybindings", "Learn mode")

# Translators: This string is a label for the group of Orca commands which
# are related to presenting and performing the accessible actions associated
# with the current object.
KB_GROUP_ACTIONS = _("Actions")
ACTIONS_LIST = KB_GROUP_ACTIONS

# Translators: An external braille device has buttons on it that permit the
# user to create input gestures from the braille device. The braille bindings
# are what determine the actions Orca will take when the user presses these
# buttons.
KB_GROUP_BRAILLE = _("Braille Bindings")

# Translators: This string is a label for the group of Orca commands which
# are related to saving and jumping among objects via "bookmarks".
KB_GROUP_BOOKMARKS = _("Bookmarks")

# Translators: This string is a label for the group of Orca commands which
# are related to the clipboard.
KB_GROUP_CLIPBOARD = _("Clipboard")

# Translators: This string is a label for the group of Orca commands which
# are related to presenting the date and time.
KB_GROUP_DATE_AND_TIME = _("Date and time")

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
# resume working. This string is a label for the group of Orca commands which
# are related to sleep mode.
KB_GROUP_SLEEP_MODE = _("Sleep mode")

# Translators: This string is a label for the group of Orca commands which
# are related to presenting the object under the mouse pointer in speech
# and/or braille. The translation should be consistent with the string
# used in cmdnames.py.
KB_GROUP_MOUSE_REVIEW = _("Mouse review")

# Translators: This string is a label for the group of Orca commands which
# are related to object navigation.
KB_GROUP_OBJECT_NAVIGATION = _("Object navigation")

# Translators: This string is a label for a group of Orca commands which are
# related to presenting information about the system, such as date, time,
# battery status, CPU status, etc.
KB_GROUP_SYSTEM_INFORMATION = _("System information")

# Translators: This string is a label for the group of Orca commands which
# are related to structural navigation, such as moving to the next heading,
# paragraph, form field, etc. in a given direction.
KB_GROUP_STRUCTURAL_NAVIGATION = _("Structural navigation")

# Translators: This string is a label for the group of Orca commands which
# are related to table navigation, such as moving to the next cell in a
# given direction.
KB_GROUP_TABLE_NAVIGATION = _("Table navigation")

# Translators: This string is a label for the group of Orca commands which
# are related to presenting information about the current location, such as
# the title, status bar, and default button of the current window; the
# name, role, and location of the currently-focused object; the selected
# text in the currently-focused object; etc.
KB_GROUP_WHERE_AM_I = _("Object details")

# Translators: This string is a label for the group of Orca commands which
# are related to Orca's "flat review" feature. This feature allows the blind
# user to explore the text in a window in a 2D fashion. That is, Orca treats
# all the text from all objects in a window (e.g., buttons, labels, etc.) as
# a sequence of words in a sequence of lines.  The flat review feature allows
# the user to explore this text by the {previous,next} {line,word,character}.
# Those commands are all listed under this group label.
KB_GROUP_FLAT_REVIEW = _("Flat review")

# Translators: This string is a label for the group of Orca commands which
# are related to Orca's speech and verbosity settings. This group of commands
# allows on-the-fly configuration of how much (or little) Orca says about a
# particular object, as well certain aspects of the voice with which things
# are spoken.
KB_GROUP_SPEECH_VERBOSITY = _("Speech and verbosity")

# Translators: the 'flat review' feature of Orca allows the blind user to
# explore the text in a window in a 2D fashion.  That is, Orca treats all
# the text from all objects in a window (e.g., buttons, labels, etc.) as a
# sequence of words in a sequence of lines.  The flat review feature allows
# the user to explore this text by the {previous,next} {line,word,character}.
# Normally the contents are navigated without leaving the application being
# reviewed. There is a command which will place the entire contents of the
# flat review representation into a text view to make it easy to review
# and copy the text. This string is the title of the window with the text view.
FLAT_REVIEW_CONTENTS = _("Flat review contents")

# Translators: Modified is a table column header in Orca's preferences dialog.
# This column contains a checkbox which indicates whether a key binding
# for an Orca command has been changed by the user to something other than its
# default value.
KB_MODIFIED = C_("keybindings", "Modified")

# Translators: This label refers to the keyboard layout (desktop or laptop).
KEYBOARD_LAYOUT_DESKTOP = _("_Desktop")

# Translators: Orca has a feature to list all of the notification messages
# received, similar to the functionality gnome-shell provides when you press
# Super+M, but it works in all desktop environments. Orca's list is a table
# with two columns, one column for the text of the notification and one
# column for the time of the notification. This string is a column header
# for the text of the notifications.
NOTIFICATIONS_COLUMN_HEADER = C_("notification presenter", "Notifications")

# Translators: Orca has a feature to list all of the notification messages
# received, similar to the functionality gnome-shell provides when you press
# Super+M, but it works in all desktop environments. Orca's list is a table
# with two columns, one column for the text of the notification and one
# column for the time of the notification. This string is a column header
# for the time, which will be relative (e.g. "10 minutes ago") or absolute.
NOTIFICATIONS_RECEIVED_TIME = C_("notification presenter", "Received")

# Translators: This string is a label for the group of Orca commands which
# are associated with presenting notifications.
KB_GROUP_NOTIFICATIONS = _("Notification presenter")

# Translators: Orca's preferences can be configured on a per-application basis,
# allowing users to customize Orca's behavior, keybindings, etc. to work one
# way in LibreOffice and another way in a chat application. This string is the
# title of Orca's application-specific preferences dialog for an application.
# The string substituted in is the accessible name of the application (e.g.
# "Gedit", "Firefox", etc.
PREFERENCES_APPLICATION_TITLE = _("Screen Reader Preferences for %s")

# Translators: This is a table column header. This column consists of a single
# checkbox. If the checkbox is checked, Orca will indicate the associated item
# or attribute by "marking" it in braille. "Marking" is not the same as writing
# out the word; instead marking refers to adding some other indicator, e.g.
# "underlining" with braille dots 7-8 a word that is bold.
PRESENTATION_MARK_IN_BRAILLE = _("Mark in braille")

# Translators: "Present Unless" is a column header of the text attributes panel
# of the Orca preferences dialog. On this panel, the user can select a set of
# text attributes that they would like spoken and/or indicated in braille.
# Because the list of attributes could get quite lengthy, we provide the option
# to always speak/braille a text attribute *unless* its value is equal to the
# value given by the user in this column of the list. For example, given the
# text attribute "underline" and a present unless value of "none", the user is
# stating that he/she would like to have underlined text announced for all cases
# (single, double, low, etc.) except when the value of underline is none (i.e.
# when it's not underlined). "Present" here is being used as a verb.
PRESENTATION_PRESENT_UNLESS = _("Present Unless")

# Translators: This is a table column header. The "Speak" column consists of a
# single checkbox. If the checkbox is checked, Orca will speak the associated
# item or attribute (e.g. saying "Bold" as part of the information presented
# when the user gives the Orca command to obtain the format and font details of
# the current text).
PRESENTATION_SPEAK = _("Speak")

# Translators: This is the title of a message dialog informing the user that
# he/she attempted to save a new user profile under a name which already exists.
# A "user profile" is a collection of settings which apply to a given task, such
# as a "Spanish" profile which would use Spanish text-to-speech and Spanish
# braille and selected when reading Spanish content.
PROFILE_CONFLICT_TITLE = _("Save Profile As Conflict")

# Translators: This is the label of a message dialog informing the user that
# he/she attempted to save a new user profile under a name which already exists.
# A "user profile" is a collection of settings which apply to a given task, such
# as a "Spanish" profile which would use Spanish text-to-speech and Spanish
# braille and selected when reading Spanish content.
PROFILE_CONFLICT_LABEL = _("User Profile Conflict!")

# Translators: This is the message in a dialog informing the user that he/she
# attempted to save a new user profile under a name which already exists.
# A "user profile" is a collection of settings which apply to a given task, such
# as a "Spanish" profile which would use Spanish text-to-speech and Spanish
# braille and selected when reading Spanish content.
PROFILE_CONFLICT_MESSAGE = _("Profile %s already exists.\n" \
                             "Continue updating the existing profile with " \
                             "these new changes?")

# Translators: This text is displayed in a message dialog when a user indicates
# he/she wants to switch to a new user profile which will cause him/her to lose
# settings which have been altered but not yet saved. A "user profile" is a
# collection of settings which apply to a given task such as a "Spanish" profile
# which would use Spanish text-to-speech and Spanish braille and selected when
# reading Spanish content.
PROFILE_LOAD_LABEL = _("Load user profile")

# Translators: This text is displayed in a message dialog when a user indicates
# he/she wants to switch to a new user profile which will cause him/her to lose
# settings which have been altered but not yet saved. A "user profile" is a
# collection of settings which apply to a given task such as a "Spanish" profile
# which would use Spanish text-to-speech and Spanish braille and selected when
# reading Spanish content.
PROFILE_LOAD_MESSAGE = \
    _("You are about to change the active profile. If you\n" \
      "have just made changes in your preferences, they will\n" \
      "be dropped at profile load.\n\n" \
      "Continue loading profile discarding previous changes?")

# Translators: Profiles in Orca make it possible for users to quickly switch
# amongst a group of pre-defined settings (e.g. an 'English' profile for reading
# text written in English using an English-language speech synthesizer and
# braille rules, and a similar 'Spanish' profile for reading Spanish text. The
# following string is the title of a dialog in which users can save a newly-
# defined profile.
PROFILE_SAVE_AS_TITLE = _("Save Profile As")

# Translators: Profiles in Orca make it possible for users to quickly switch
# amongst a group of pre-defined settings (e.g. an 'English' profile for reading
# text written in English using an English-language speech synthesizer and
# braille rules, and a similar 'Spanish' profile for reading Spanish text. The
# following string is the label for a text entry in which the user enters the
# name of a new settings profile being saved via the 'Save Profile As' dialog.
PROFILE_NAME_LABEL = _("_Profile Name:")

# Translators: Profiles in Orca make it possible for users to quickly switch
# amongst a group of pre-defined settings (e.g. an 'English' profile for reading
# text written in English using an English-language speech synthesizer and
# braille rules, and a similar 'Spanish' profile for reading Spanish text.
# The following is a label in a dialog informing the user that he/she
# is about to remove a user profile, and action that cannot be undone.
PROFILE_REMOVE_LABEL = _("Remove user profile")

# Translators: Profiles in Orca make it possible for users to quickly switch
# amongst a group of pre-defined settings (e.g. an 'English' profile for reading
# text written in English using an English-language speech synthesizer and
# braille rules, and a similar 'Spanish' profile for reading Spanish text.
# The following is a message in a dialog informing the user that he/she
# is about to remove a user profile, an action that cannot be undone.
PROFILE_REMOVE_MESSAGE = _("You are about to remove profile %s. " \
                           "All unsaved settings and settings saved in this " \
                           "profile will be lost. Do you want to continue " \
                           "and remove this profile and all related settings?")

# Translators: Orca has a setting which determines which progress bar updates
# should be announced. Choosing "All" means that Orca will present progress bar
# updates regardless of what application and window they happen to be in.
PROGRESS_BAR_ALL = C_("ProgressBar", "All")

# Translators: Orca has a setting which determines which progress bar updates
# should be announced. Choosing "Application" means that Orca will present
# progress bar updates as long as the progress bar is in the active application
# (but not necessarily in the current window).
PROGRESS_BAR_APPLICATION = C_("ProgressBar", "Application")

# Translators: Orca has a setting which determines which progress bar updates
# should be announced. Choosing "Window" means that Orca will present progress
# bar updates as long as the progress bar is in the active window.
PROGRESS_BAR_WINDOW = C_("ProgressBar", "Window")

# Translators: If this setting is chosen, no punctuation symbols will be spoken
# as a user reads a document.
PUNCTUATION_STYLE_NONE = C_("punctuation level", "_None")

# Translators: If this setting is chosen, common punctuation symbols (like
# comma, period, question mark) will not be spoken as a user reads a document,
# but less common symbols (such as #, @, $) will.
PUNCTUATION_STYLE_SOME = _("So_me")

# Translators: If this setting is chosen, the majority of punctuation symbols
# will be spoken as a user reads a document.
PUNCTUATION_STYLE_MOST = _("M_ost")

# Translators: If this setting is chosen and the user is reading over an entire
# document, Orca will pause at the end of each line.
SAY_ALL_STYLE_LINE = _("Line")

# Translators: If this setting is chosen and the user is reading over an entire
# document, Orca will pause at the end of each sentence.
SAY_ALL_STYLE_SENTENCE = _("Sentence")

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
# contains the text displayed for a web element with an "onClick" handler.
SN_HEADER_CLICKABLE = C_("structural navigation", "Clickable")

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
# contains the title associated with an iframe.
SN_HEADER_IFRAME = C_("structural navigation", "Internal Frame")

# Translators: Orca has a command that presents a list of structural navigation
# objects in a dialog box so that users can navigate more quickly than they
# could with native keyboard navigation. This is the title for a column which
# contains the text (alt text, title, etc.) associated with an image.
SN_HEADER_IMAGE = C_("structural navigation", "Image")

# Translators: Orca has a command that presents a list of structural navigation
# objects in a dialog box so that users can navigate more quickly than they
# could with native keyboard navigation. This is the title for a column which
# contains the label of a form field.
SN_HEADER_LABEL = C_("structural navigation", "Label")

# Translators: Orca has a command that presents a list of structural navigation
# objects in a dialog box so that users can navigate more quickly than they
# could with native keyboard navigation. This is the title for a column which
# contains the text of a landmark. ARIA role landmarks are the W3C defined HTML
# tag attribute 'role' used to identify important part of webpage like banners,
# main context, search etc.
SN_HEADER_LANDMARK = C_("structural navigation", "Landmark")

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
SN_HEADER_SELECTED_ITEM = C_("structural navigation", "Selected Item")

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
# "Clickables" are web elements which have an "onClick" handler.
SN_TITLE_CLICKABLE = C_("structural navigation", "Clickables")

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
SN_TITLE_IFRAME = C_("structural navigation", "Internal Frames")

# Translators: Orca has a command that presents a list of structural navigation
# objects in a dialog box so that users can navigate more quickly than they
# could with native keyboard navigation. This is the title of such a dialog box.
SN_TITLE_IMAGE = C_("structural navigation", "Images")

# Translators: Orca has a command that presents a list of structural navigation
# objects in a dialog box so that users can navigate more quickly than they
# could with native keyboard navigation. This is the title of such a dialog box.
# Level will be a "1" for <h1>, a "2" for <h2>, and so on.
SN_TITLE_HEADING_AT_LEVEL = C_("structural navigation", "Headings at Level %d")

# Translators: Orca has a command that presents a list of structural navigation
# objects in a dialog box so that users can navigate more quickly than they
# could with native keyboard navigation. This is the title of such a dialog box.
# ARIA role landmarks are the W3C defined HTML tag attribute 'role' used to
# identify important part of webpage like banners, main context, search etc.
SN_TITLE_LANDMARK = C_("structural navigation", "Landmarks")

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

# Translators: When the user loads a new web page, they can optionally have Orca
# automatically summarize details about the page, such as the number of elements
# (landmarks, forms, links, tables, etc.).
PAGE_SUMMARY_UPON_LOAD = _("_Present summary of a page when it is first loaded")

# Translators: Different speech systems and speech engines work differently when
# it comes to handling pauses (e.g. sentence boundaries). This property allows
# the user to specify whether speech should be sent to the speech synthesis
# system immediately when a pause directive is encountered or if it should be
# queued up and sent to the speech synthesis system once the entire set of
# utterances has been calculated.
SPEECH_BREAK_INTO_CHUNKS = _("Break speech into ch_unks between pauses")

# Translators: This string will appear in the list of available voices for the
# current speech engine. "%s" will be replaced by the name of the current speech
# engine, such as "Festival default voice" or "IBMTTS default voice". It refers
# to the default voice configured for given speech engine within the speech
# subsystem. Apart from this item, the list will contain the names of all
# available "real" voices provided by the speech engine.
SPEECH_DEFAULT_VOICE = _("%s default voice")

# Translators: This refers to the voice used by Orca when presenting the content
# of the screen and other messages.
SPEECH_VOICE_TYPE_DEFAULT = C_("VoiceType", "Default")

# Translators: This refers to the voice used by Orca when presenting one or more
# characters which is part of a hyperlink.
SPEECH_VOICE_TYPE_HYPERLINK = C_("VoiceType", "Hyperlink")

# Translators: This refers to the voice used by Orca when presenting information
# which is not displayed on the screen as text, but is still being communicated
# by the system in some visual fashion. For instance, Orca says "misspelled" to
# indicate the presence of the red squiggly line found under a spelling error;
# Orca might say "3 of 6" when a user Tabs into a list of six items and the
# third item is selected. And so on.
SPEECH_VOICE_TYPE_SYSTEM = C_("VoiceType", "System")

# Translators: This refers to the voice used by Orca when presenting one or more
# characters which is written in uppercase.
SPEECH_VOICE_TYPE_UPPERCASE = C_("VoiceType", "Uppercase")

# Translators this label refers to the name of particular speech synthesis
# system. (http://devel.freebsoft.org/speechd)
SPEECH_DISPATCHER = _("Speech Dispatcher")

# Translators this label refers to the name of particular speech synthesis
# system. (https://github.com/eeejay/spiel)
SPIEL = _("Spiel")

# Translators: This is a label for a group of options related to Orca's behavior
# when presenting an application's spell check dialog.
SPELL_CHECK = C_("OptionGroup", "Spell Check")

# Translators: This is a label for a checkbox associated with an Orca setting.
# When this option is enabled, Orca will spell out the current error in addition
# to speaking it. For example, if the misspelled word is "foo," enabling this
# setting would cause Orca to speak "f o o" after speaking "foo".
SPELL_CHECK_SPELL_ERROR = _("Spell _error")

# Translators: This is a label for a checkbox associated with an Orca setting.
# When this option is enabled, Orca will spell out the current suggestion in
# addition to speaking it. For example, if the misspelled word is "foo," and
# the first suggestion is "for" enabling this setting would cause Orca to speak
# "f o r" after speaking "for".
SPELL_CHECK_SPELL_SUGGESTION = _("Spell _suggestion")

# Translators: This is a label for a checkbox associated with an Orca setting.
# When this option is enabled, Orca will present the context (surrounding text,
# typically the sentence or line) in which the mistake occurred.
SPELL_CHECK_PRESENT_CONTEXT = _("Present _context of error")

# Translators: This is a label for an option to tell Orca whether or not it
# should speak the coordinates of the current spreadsheet cell. Coordinates are
# the row and column position within the spreadsheet (i.e. A1, B1, C2 ...)
SPREADSHEET_SPEAK_CELL_COORDINATES = _("Speak spreadsheet cell coordinates")

# Translators: This is a label for an option which controls what Orca speaks when
# presenting selection changes in a spreadsheet. By default, Orca will speak just
# what changed. For instance, if cells A1 through A8 are already selected, and the
# user adds A9 to the selection, Orca by default would just say "A9 selected."
# Some users, however, prefer to have Orca always announce the entire selected range,
# i.e. in the same scenario say "A1 through A9 selected." Those users should enable
# this option.
SPREADSHEET_SPEAK_SELECTED_RANGE = _("Always speak selected spreadsheet range")

# Translators: This is a label for an option for whether or not to speak the
# header of a table cell in document content.
TABLE_ANNOUNCE_CELL_HEADER = _("Announce cell _header")

# Translators: This is the title of a panel containing options for specifying
# how to navigate tables in document content.
TABLE_NAVIGATION = _("Table Navigation")

# Translators: This is a label for an option to tell Orca to skip over empty/
# blank cells when navigating tables in document content.
TABLE_SKIP_BLANK_CELLS = _("Skip _blank cells")

# Translators: When users are navigating a table, they sometimes want the entire
# row of a table read; other times they want just the current cell presented to
# them. This label is associated with the default presentation to be used.
TABLE_SPEAK_CELL = _("Speak _cell")

# Translators: This is a label for an option to tell Orca whether or not it
# should speak table cell coordinates in document content.
TABLE_SPEAK_CELL_COORDINATES = _("Speak _cell coordinates")

# Translators: This is a label for an option to tell Orca whether or not it
# should speak the span size of a table cell (e.g., how many rows and columns
# a particular table cell spans in a table).
TABLE_SPEAK_CELL_SPANS = _("Speak _multiple cell spans")

# Translators: This is a table column header. "Attribute" here refers to text
# attributes such as bold, underline, family-name, etc.
TEXT_ATTRIBUTE_NAME = _("Attribute Name")

# Translators: Gecko native caret navigation is where Firefox itself controls
# how the arrow keys move the caret around HTML content. It's often broken, so
# Orca needs to provide its own support. As such, Orca offers the user the
# ability to switch between the Firefox mode and the Orca mode. This is the
# label of a checkbox in which users can indicate their default preference.
USE_CARET_NAVIGATION = _("Control caret navigation")

# Translators: Orca provides keystrokes to navigate HTML content in a structural
# manner: go to previous/next header, list item, table, etc. This is the label
# of a checkbox in which users can indicate their default preference.
USE_STRUCTURAL_NAVIGATION = _("Enable _structural navigation")

# Translators: This refers to the amount of information Orca provides about a
# particular object that receives focus.
VERBOSITY_LEVEL_BRIEF = _("Brie_f")

def notifications_count(count):
    """Returns the gui label representing the notifications count."""

    # Translators: Orca has a feature to list all of the notification messages
    # received, similar to the functionality gnome-shell provides when you press
    # Super+M, but it works in all desktop environments. This string is the title
    # of the dialog that contains the list of notification messages. The string
    # substitution is for the number of messages in the list.
    return ngettext("%d notification", "%d notifications", count) % count
