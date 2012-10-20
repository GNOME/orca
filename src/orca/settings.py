# Orca
#
# Copyright 2004-2009 Sun Microsystems Inc.
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

"""Manages the settings for Orca.  This will defer to user settings first, but
fallback to local settings if the user settings doesn't exist (e.g., in the
case of gdm) or doesn't have the specified attribute."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2004-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi

from .acss import ACSS
from .orca_i18n import _
from .orca_i18n import C_

# These are the settings that Orca supports the user customizing.
#
userCustomizableSettings = [
    "orcaModifierKeys",
    "enableSpeech",
    "onlySpeakDisplayedText",
    "speechServerFactory",
    "speechServerInfo",
    "voices",
    "speechVerbosityLevel",
    "readTableCellRow",
    "enableSpeechIndentation",
    "enableEchoByCharacter",
    "enableEchoByWord",
    "enableEchoBySentence",
    "enableKeyEcho",
    "enablePrintableKeys",
    "enableModifierKeys",
    "enableFunctionKeys",
    "enableActionKeys",
    "enableNavigationKeys",
    "enableDiacriticalKeys",
    "enablePauseBreaks",
    "enableTutorialMessages",
    "enableMnemonicSpeaking",
    "enablePositionSpeaking",
    "enableBraille",
    "enableBrailleContext",
    "enableBrailleGrouping",
    "disableBrailleEOL",
    "brailleEOLIndicator",
    "brailleVerbosityLevel",
    "brailleRolenameStyle",
    "brailleSelectorIndicator",
    "brailleLinkIndicator",
    "brailleAlignmentStyle",
    "enableBrailleMonitor",
    "verbalizePunctuationStyle",
    "showMainWindow",
    "quitOrcaNoConfirmation",
    "presentToolTips",
    "sayAllStyle",
    "keyboardLayout",
    "speakBlankLines",
    "speakMultiCaseStringsAsWords",
    "enabledSpokenTextAttributes",
    "enabledBrailledTextAttributes",
    "textAttributesBrailleIndicator",
    "enableProgressBarUpdates",
    "profile",
    "progressBarUpdateInterval",
    "progressBarVerbosity",
    "enableContractedBraille",
    "brailleContractionTable",
    "enableMouseReview",
    "mouseDwellDelay",
    "speakCellCoordinates",
    "speakCellSpan",
    "speakCellHeaders",
    "skipBlankCells",
    "largeObjectTextLength",
    "wrappedStructuralNavigation",
    "presentRequiredState",
    "brailleRequiredStateString",
    "speechRequiredStateString",
    "chatMessageVerbosity",
    "chatSpeakRoomName",
    "chatAnnounceBuddyTyping",
    "chatRoomHistories",
    "enableFlashMessages",
    "brailleFlashTime",
    "flashIsPersistent",
    "flashVerbosityLevel",
    "messageVerbosityLevel",
    "presentDateFormat",
    "presentTimeFormat",
    "activeProfile",
    "startingProfile",
]

excludeKeys = ["pronunciations",
               "keybindings",
               "startingProfile",
               "activeProfile"]

# Profiles
#
startingProfile = ['Default', 'default']
activeProfile = ['Default', 'default']
profile = ['Default', 'default']

# A list of keys that can serve as the Orca modifier key.  The list is
# so we can provide better cross platform support (e.g., Sun keyboard
# vs. PC-104 keyboard layouts).  When any of these keys is pressed,
# the orca.MODIFIER_ORCA bit will be set in the 'modifiers' field of
# a KeyboardEvent input event.  The keys are currently compared to the
# event_string of a keyboard input event from AT-SPI.
#
# The initial set of modifier keys is dependant upon whether the user
# has specified a desktop or a laptop keyboard layout.
#
DESKTOP_MODIFIER_KEYS = ["Insert", "KP_Insert"]
LAPTOP_MODIFIER_KEYS  = ["Caps_Lock"]
orcaModifierKeys      = DESKTOP_MODIFIER_KEYS

# A new modifier to use (set by the press of any key in the
# orcaModifierKeys list) to represent the Orca modifier.
#
MODIFIER_ORCA = 8

# Verbosity levels (see setBrailleVerbosityLevel and
# setSpeechVerbosityLevel).  These will have an impact on the various
# individual verbosity levels for rolenames, accelerators, etc.
#
VERBOSITY_LEVEL_BRIEF   = 0
VERBOSITY_LEVEL_VERBOSE = 1
speechVerbosityLevel    = VERBOSITY_LEVEL_VERBOSE
brailleVerbosityLevel   = VERBOSITY_LEVEL_VERBOSE
flashVerbosityLevel     = VERBOSITY_LEVEL_VERBOSE
messageVerbosityLevel   = VERBOSITY_LEVEL_VERBOSE

BRAILLE_ROLENAME_STYLE_SHORT = 0 # three letter abbreviations
BRAILLE_ROLENAME_STYLE_LONG  = 1 # full rolename
brailleRolenameStyle    = BRAILLE_ROLENAME_STYLE_LONG

# Roles to force to be displayed even when the verbosity level
# is not verbose.
#
brailleForceRoles = [pyatspi.ROLE_COMBO_BOX,
                     pyatspi.ROLE_MENU,
                     pyatspi.ROLE_TEAROFF_MENU_ITEM]

# Braille Selection Indicator (see brailleSelectorIndicator).
# The values represent the character to be used in the attrOr
# field of brlAPI's writeStruct.
#
BRAILLE_SEL_NONE = 0x00 # 00000000
BRAILLE_SEL_7    = 0x40 # 01000000
BRAILLE_SEL_8    = 0x80 # 10000000
BRAILLE_SEL_BOTH = 0xc0 # 11000000
brailleSelectorIndicator = BRAILLE_SEL_BOTH

# Braille Link Indicator (see brailleLinkIndicator).
# The values represent the character to be used in the attrOr
# field of brlAPI's writeStruct.
#
BRAILLE_LINK_NONE = 0x00 # 00000000
BRAILLE_LINK_7    = 0x40 # 01000000
BRAILLE_LINK_8    = 0x80 # 10000000
BRAILLE_LINK_BOTH = 0xc0 # 11000000
brailleLinkIndicator = BRAILLE_LINK_BOTH

# Braille alignment styles.  These say how to align text on the
# edges of the braille display.  The brailleAlignmentMargin value
# says how close to the edge of the braille the display the cursor
# cell can get.  The brailleMaximumJump says how far we can jump
# the display when aligning by word.
#
ALIGN_BRAILLE_BY_EDGE   = 0
ALIGN_BRAILLE_BY_MARGIN = 1
ALIGN_BRAILLE_BY_WORD   = 2
brailleAlignmentMargin  = 3
brailleMaximumJump      = 8
brailleAlignmentStyle   = ALIGN_BRAILLE_BY_EDGE

# Speech punctuation levels (see verbalizePunctuationStyle).
#
PUNCTUATION_STYLE_NONE = 3
PUNCTUATION_STYLE_SOME = 2
PUNCTUATION_STYLE_MOST = 1
PUNCTUATION_STYLE_ALL  = 0
verbalizePunctuationStyle = PUNCTUATION_STYLE_MOST

# Say All styles (see sayAllStyle).
#
SAYALL_STYLE_LINE     = 0
SAYALL_STYLE_SENTENCE = 1
sayAllStyle = SAYALL_STYLE_SENTENCE

# The absolue amount to change the speech rate when
# increasing or decreasing speech.  This is a numerical
# value that represents an ACSS rate value.
#
speechRateDelta         = 5

# The absolue amount to change the speech pitch when
# increasing or decreasing pitch.  This is a numerical
# value that represents an ACSS pitch value.
#
speechPitchDelta        = 0.5

# If True, enable speech.
#
enableSpeech            = True
enableSpeechCallbacks   = True

# If True, speech has been temporarily silenced.
#
silenceSpeech           = False

# If True, only text which is displayed on screen will be spoken
# (roles, states, etc. will not be).
#
onlySpeakDisplayedText = False

# Settings that apply to the particular speech engine to
# use as well details on the default voices to use.
#
speechFactoryModules    = ["speechdispatcherfactory"]
speechServerFactory     = "speechdispatcherfactory"
speechServerInfo        = None # None means let the factory decide.

DEFAULT_VOICE           = "default"
UPPERCASE_VOICE         = "uppercase"
HYPERLINK_VOICE         = "hyperlink"
SYSTEM_VOICE            = "system"

voicesKeys = {
"DEFAULT_VOICE"     : "default",
"UPPERCASE_VOICE"   : "uppercase",
"HYPERLINK_VOICE"   : "hyperlink",
"SYSTEM_VOICE"      : "system"
}


voices = {
    DEFAULT_VOICE: ACSS({}),
    UPPERCASE_VOICE: ACSS({ACSS.AVERAGE_PITCH : 5.6}),
    HYPERLINK_VOICE: ACSS({}),
    SYSTEM_VOICE: ACSS({}),
}

# If True, enable speaking of speech indentation and justification.
#
enableSpeechIndentation = False

# If True, enable braille.
#
enableBraille           = False

# If True, add the hierarchical context of an object to the braille
# line.  People with very large braille displays may want to set this
# to False.
#
enableBrailleContext    = True

# If True, enable the grouping of children on the braille display.
# This is for things like displaying all items of a menu, tab list,
# menu bar, etc., on a single line of the braille display.
#
enableBrailleGrouping   = False

# If True, enable braille flash messages. Note that braille or braille
# monitor will also need to be enabled for this setting to work.
#
enableFlashMessages     = True

# The timeout (in milliseconds) to use for messages flashed in braille.
#
brailleFlashTime        = 5000

# If True, flash messages should continue to be displayed until some
# other message comes along, or the user presses a key.
#
flashIsPersistent       = False

# If True, enable braille monitor.
#
enableBrailleMonitor    = False

# if True, enable character echo.
# Note that it is allowable for both enableEchoByCharacter and enableKeyEcho
# to be True
#
enableEchoByCharacter   = False

# if True, enable word echo.
# Note that it is allowable for both enableEchoByWord and enableKeyEcho
# to be True
#
enableEchoByWord        = False

# if True, enable Sentence echo.
# Note that it is allowable for both enableEchoByWord and enableEchoBySentence
# to be True.
#
enableEchoBySentence    = False

# If True, enable key echo.
# Note that it is allowable for both enableEchoByWord and enableKeyEcho
# to be True
#
enableKeyEcho           = True

# If True and key echo is enabled, echo Alphanumeric and punctuation keys.
#
enablePrintableKeys     = True

# If True and key echo is enabled, echo Modifier keys.
#
enableModifierKeys      = True

# If True and key echo is enabled, echo Function keys.
#
enableFunctionKeys      = True

# If True and key echo is enabled, echo Action keys.
#
enableActionKeys        = True

# If True and key echo is enabled, echo Navigation keys.
#
enableNavigationKeys    = False

# If True and key echo is enabled, echo Diacritical keys.
#
enableDiacriticalKeys   = False

# If True, tutorial strings defined will be spoken.
#
enableTutorialMessages = False

# If True, mnemonics will be spoken.
#
enableMnemonicSpeaking = False

# If true, position indexes  will be spoken automaticaly
#
enablePositionSpeaking = False

# If True, show the main Orca window.
#
showMainWindow          = True

# If True, show the splash window.
#
showSplashWindow          = True

# If True, quit Orca without confirmation when the user presses
# <Orca-modifier>-q.
#
quitOrcaNoConfirmation  = False

# If True, always present locking key state changes; if False, never present
# locking key state changes. If None, make the decision based on Orca's normal
# behavior.
#
presentLockingKeys = None

# If True, ignore the directive in the autostart file which prevents the
# main window from showing up.
#
overrideDisabledMainWindow = False

# Whether the user wants tooltips presented or not.
#
presentToolTips = False

# Keyboard layout options (see keyboardLayout).
#
GENERAL_KEYBOARD_LAYOUT_DESKTOP = 1
GENERAL_KEYBOARD_LAYOUT_LAPTOP  = 2
keyboardLayout                  = GENERAL_KEYBOARD_LAYOUT_DESKTOP

# The red, green, blue values to use to outline the current item in
# flat review mode. They are values between 0 and 65535 (0xFFFF), with
# 65535 (0xFFFF) indicating full intensitiy
#
outlineColor = [ 0xFFFF, 0x0000, 0x0000 ]

# Thickness in pixels of the outline around the the current item in flat
# review mode.
#
outlineThickness = 4

# Margin between the object being outlined and the actual outline
#
outlineMargin = 1

# The kind of outlining to do for flat review mode.
#
OUTLINE_NONE = 0
OUTLINE_BOX = 1
OUTLINE_LINE = 2
OUTLINE_WEDGES = 3
outlineStyle = OUTLINE_BOX

# If True, speak blank lines.
#
speakBlankLines         = True

# if True, process multi case strings as words.
#
speakMultiCaseStringsAsWords = False

# If True, reads all the table cells in the current row rather than just
# the current one.
#
readTableCellRow    = True

# If True, enable speaking of progress bar updates.
#
enableProgressBarUpdates = True

# The interval (in seconds) between speaking progress bar updates. A value
# of zero means that progress bar updates should not be spoken at all.
#
progressBarUpdateInterval = 10

# When progress bar updates should be spoken, assuming they are enabled.
# ALL means that any progress bar update will be spoken. APPLICATION
# means that progress bar updates from the active application will be
# spoken, even if they are not in the active window. WINDOW means that
# the progress bar must be contained in the active window in order to
# be spoken. The default verbosity level is APPLICATION.
#
PROGRESS_BAR_ALL = 0
PROGRESS_BAR_APPLICATION = 1
PROGRESS_BAR_WINDOW = 2
progressBarVerbosity = PROGRESS_BAR_APPLICATION

# Whether or not to present the 'read only' attribute of text areas
# if we can detect they are read only or not.
#
presentReadOnlyText = True

# The complete list of possible text attributes.
#
allTextAttributes = \
    "bg-color:; bg-full-height:; bg-stipple:; direction:; editable:; " \
    "family-name:; fg-color:; fg-stipple:; font-effect:none; indent:0; " \
    "invisible:; justification:left; language:; left-margin:; " \
    "line-height:100%; paragraph-style:Default; pixels-above-lines:; " \
    "pixels-below-lines:; pixels-inside-wrap:; right-margin:; rise:; " \
    "scale:; size:; stretch:; strikethrough:false; style:normal; " \
    "text-decoration:none; text-rotation:0; text-shadow:none; " \
    "text-spelling:none; underline:none; variant:; " \
    "vertical-align:baseline; weight:400; wrap-mode:; writing-mode:lr-tb;"

# The default set of text attributes to speak to the user. Specific
# application scripts (or individual users can override these values if
# so desired. Each of these text attributes is of the form <key>:<value>;
# The <value> part will be the "default" value for that attribute. In
# other words, if the attribute for a given piece of text has that value,
# it won't be spoken. If no value part is given, then that attribute will
# always be spoken.

enabledSpokenTextAttributes = \
    "size:; family-name:; weight:400; indent:0; underline:none; " \
    "strikethrough:false; justification:left; style:normal; " \
    "paragraph-style:; text-spelling:none;"

# The default set of text attributes to be brailled for the user. Specific
# application scripts (or individual users can override these values if
# so desired. Each of these text attributes is of the form <key>:<value>;
# The <value> part will be the "default" value for that attribute. In
# other words, if the attribute for a given piece of text has that value,
# it won't be spoken. If no value part is given, then that attribute will
# always be brailled.

enabledBrailledTextAttributes = \
    "size:; family-name:; weight:400; indent:0; underline:none; " \
    "strikethrough:false; justification:left; style:normal; " \
    "text-spelling:none;"

# Text Attributes Braille Indicator (see textAttributesBrailleIndicator).
# The values represent the character to be used in the attrOr
# field of brlAPI's writeStruct.
#
TEXT_ATTR_BRAILLE_NONE = 0x00 # 00000000
TEXT_ATTR_BRAILLE_7    = 0x40 # 01000000
TEXT_ATTR_BRAILLE_8    = 0x80 # 10000000
TEXT_ATTR_BRAILLE_BOTH = 0xc0 # 11000000
textAttributesBrailleIndicator = TEXT_ATTR_BRAILLE_NONE

# The limit to enable a repeat character count to be spoken.
# If set to 0, then there will be no repeat character count.
# Each character will be spoken singularly (i.e. "dash dash
# dash dash dash" instead of "five dash characters").
# If the value is set to 1, 2 or 3 then it's treated as if it was
# zero. In other words, no repeat character count is given.
#
repeatCharacterLimit = 4

# Tags associated with ARIA landmarks.
#
ariaLandmarks = [
    "application",
    "article",
    "banner",
    "complementary",
    "contentinfo",
    "definition",
    "directory",
    "document",
    "grid",
    "log",
    "main",
    "menubar",
    "navigation",
    "note",
    "region",
    "search",
    "secondary",
    "seealso",
    "status",
]

# Script developer feature.  If False, just the default script
# will be used.  Helps determine difference between custom
# scripts and the default script behavior.
#
enableCustomScripts     = True

# Latent support to allow the user to override/define keybindings
# and braille bindings.  Unsupported and undocumented for now.
# Use at your own risk.
#
keyBindingsMap          = {}
brailleBindingsMap      = {}

# Script developer feature.  If False, no AT-SPI object values
# will be cached locally.  Helps determine if there might be a
# problem related to the cache being out of sync with the real
# objects.
#
cacheValues             = True
cacheDescriptions       = True

# Script developer feature.  If False, no AT-SPI objects
# will be cached locally.  Helps determine if there might be a
# problem related to the cache being out of sync with the real
# objects.
#
cacheAccessibles        = True

# If non-zero, we use time.sleep() in various places to attempt to
# free up the global interpreter lock.  Take a look at the following
# URLs for more information:
#
# http://mail.python.org/pipermail/python-list/2002-October/126632.html
# http://twistedmatrix.com/pipermail/twisted-python/2005-July/011052.html
# http://www.pyzine.com/Issue001/Section_Articles/ \
#                                 article_ThreadingGlobalInterpreter.html
#
gilSleepTime            = 0.00001

# The value of the 'gil' parameter in the call to pyatspi.Registry.start
# See http://bugzilla.gnome.org/show_bug.cgi?id=576954.
#
useGILIdleHandler       = False

# If True, use the gidle __blockPreventor() code in atspi.py.
#
useBlockPreventor       = False

# If True, we handle events asynchronously - our normal mode of
# queueing events and processing them later on the gidle thread.
# If False, we handle events immediately - helpful for testing.
#
asyncMode               = True

# A list of toolkits whose events we need to process synchronously.
# This was originally added for the Java toolkit (see bug #531869), but
# we put this here to allow more toolkits to be more easily added.
#
synchronousToolkits     = ['VCL']

# If True, we output debug information for the event queue.  We
# use this in addition to log level to prevent debug logic from
# bogging down event handling.
#
debugEventQueue         = False

# The timeout value (in seconds) and callback used to determine if
# Orca has hung or not.  The only setting one should muck with here is
# the timeoutTime unless you want to create a custom callback handler
# for the timeout.  See braille.py, atspi.py, and orca.py:init for how
# these are used.
#
timeoutTime             = 10   # a value of 0 means don't do hang checking
timeoutCallback         = None # Set by orca.py:init to orca.timeout

# Keyboard double-click period. If the same key is pressed within
# this time period, it's considered to be a double-click and might
# provide different functionality (for example, Numpad 5 double-click
# spells the current word rather than speaks it).
#
doubleClickTimeout = 0.5

# Available options indicating which chat messages Orca should speak.
#
CHAT_SPEAK_ALL             = 0
CHAT_SPEAK_ALL_IF_FOCUSED  = 1
CHAT_SPEAK_FOCUSED_CHANNEL = 2

chatMessageVerbosity = CHAT_SPEAK_ALL

# Whether we prefix chat room messages with the name of the chat room.
#
chatSpeakRoomName = False

# Whether we announce when a buddy is typing.
#
chatAnnounceBuddyTyping = False

# Whether we provide chat room specific message histories.
#
chatRoomHistories = False

# Allow for the customization of key bindings.
#
def overrideKeyBindings(script, keyBindings):
    from . import settings_manager
    _settingsManager = settings_manager.getManager()
    return _settingsManager.overrideKeyBindings(script, keyBindings)

# Allow for user customization of pronunciations.
#
def overridePronunciations(script, pronunciations):
    return pronunciations

# This is a list of events that Orca should immidiately drop and never look at.
#
ignoredEventsList = ['object:bounds-changed']

# Listen to Live Region events.  Tells Gecko.onChildrenChanged() and
# onTextInserted() event handlers to monitor these events for live region
# changes.
#
inferLiveRegions = True

# Contracted braille support.
#
enableContractedBraille = False

# Contracted braille table.
#
brailleContractionTable = ''

# Use Collection Interface?
#
useCollection = True

# Whether or not to speak the cell's coordinates when navigating
# from cell to cell in a table.
#
speakCellCoordinates = True

# Whether or not to speak the number of cells spanned by a cell
# that occupies more than one row or column of a table.
#
speakCellSpan = True

# Whether or not to announce the header that applies to the current
# when navigating from cell to cell in a table.
#
speakCellHeaders = True

# Whether blank cells should be skipped when navigating in a table
# using table navigation commands.
#
skipBlankCells = False

# The minimum size in characters to be considered a "large object"
# or "chunk" for structural navigation.
#
largeObjectTextLength = 75

# Whether to wrap around the document when structural navigation is used.
wrappedStructuralNavigation = True

# Report object under mouse.
#
enableMouseReview = False

# Mouse dwell delay in milliseconds for mouse review mode.
# If the value is zero, the review will be read time.
#
mouseDwellDelay = 0

# Maximum allowed drift while pointer is dwelling in mouse review mode.
#
mouseDwellMaxDrift = 3

# The different modifiers/modifier masks associated with keybindings
#
NO_MODIFIER_MASK              =  0
ALT_MODIFIER_MASK             =  1 << pyatspi.MODIFIER_ALT
CTRL_MODIFIER_MASK            =  1 << pyatspi.MODIFIER_CONTROL
ORCA_MODIFIER_MASK            =  1 << MODIFIER_ORCA
ORCA_ALT_MODIFIER_MASK        = (1 << MODIFIER_ORCA |
                                 1 << pyatspi.MODIFIER_ALT)
ORCA_CTRL_MODIFIER_MASK       = (1 << MODIFIER_ORCA |
                                 1 << pyatspi.MODIFIER_CONTROL)
ORCA_CTRL_ALT_MODIFIER_MASK   = (1 << MODIFIER_ORCA |
                                 1 << pyatspi.MODIFIER_CONTROL |
                                 1 << pyatspi.MODIFIER_ALT)
ORCA_SHIFT_MODIFIER_MASK      = (1 << MODIFIER_ORCA |
                                 1 << pyatspi.MODIFIER_SHIFT)
SHIFT_MODIFIER_MASK           =  1 << pyatspi.MODIFIER_SHIFT
SHIFT_ALT_MODIFIER_MASK       = (1 << pyatspi.MODIFIER_SHIFT |
                                 1 << pyatspi.MODIFIER_ALT)
COMMAND_MODIFIER_MASK         = (1 << pyatspi.MODIFIER_ALT |
                                 1 << pyatspi.MODIFIER_CONTROL |
                                 1 << pyatspi.MODIFIER_META2 |
                                 1 << pyatspi.MODIFIER_META3)
NON_LOCKING_MODIFIER_MASK     = (1 << pyatspi.MODIFIER_SHIFT |
                                 1 << pyatspi.MODIFIER_ALT |
                                 1 << pyatspi.MODIFIER_CONTROL |
                                 1 << pyatspi.MODIFIER_META2 |
                                 1 << pyatspi.MODIFIER_META3 |
                                 1 << MODIFIER_ORCA)
ALL_BUT_NUMLOCK_MODIFIER_MASK = (1 << MODIFIER_ORCA |
                                 1 << pyatspi.MODIFIER_SHIFT |
                                 1 << pyatspi.MODIFIER_SHIFTLOCK |
                                 1 << pyatspi.MODIFIER_CONTROL |
                                 1 << pyatspi.MODIFIER_ALT |
                                 1 << pyatspi.MODIFIER_META2 |
                                 1 << pyatspi.MODIFIER_META3)

# The 2nd parameter used when creating a keybinding refers to the
# modifiers "we care about."  We typically care about all of the
# modifiers which are not locking keys because we want to avoid
# conflicts with other commands, such as Orca's command for moving
# among headings (H) and the Help menu (Alt+H).
#
defaultModifierMask = NON_LOCKING_MODIFIER_MASK

# Whether or not we should present objects with STATE_REQUIRED to
# the user. Currently, this is only seen with ARIA widgets.
#
presentRequiredState = False

########################################################################
#                                                                      #
# Sounds                                                               #
#                                                                      #
########################################################################

# A dictionary where the keys are rolenames and the values are
# filenames containing audio snippets.
#
sounds = {}

########################################################################
#                                                                      #
# Strings for speech and braille                                       #
#                                                                      #
########################################################################

# Translators: "blank" is a short word to mean the
# user has navigated to an empty line.
#
speechBlankString = _("blank")

# Translators: Certain objects (such as form controls on web pages)
# can have STATE_REQUIRED set on them to inform the user that this
# field must be filled out. This string is the default string which
# will be spoken and displayed in braille to indicate this state is
# present.
#
speechRequiredStateString = _("required")

# Translators: this is used to indicate the user is in a text
# area that is not editable.  It is meant to be spoken to the user.
#
speechReadOnlyString = C_("text", "read only")

# Translators: this represents an item on the screen that has
# been set insensitive (or grayed out).
#
speechInsensitiveString = _("grayed")

# Translators: this represents the state of a checkbox.  It is meant
# to be spoken to the user.
#
speechCheckboxIndicators = [_("not checked"),
                            _("checked"),
                            _("partially checked")]

# Translators: this represents the state of a radio button.  It is
# meant to be spoken to the user.
#
speechRadioButtonIndicators = [C_("radiobutton", "not selected"),
                               C_("radiobutton", "selected")]

# Translators: this represents the state of a toggle button.  It is
# meant to be spoken to the user.
#
speechToggleButtonIndicators = [_("not pressed"), _("pressed")]

# Translators: this represents the state of a node in a tree.
# 'expanded' means the children are showing.  'collapsed' means the
# children are not showing.
#
speechExpansionIndicators = [_("collapsed"), _("expanded")]

# Translators: "multi-select" refers to a web form list
# in which more than one item can be selected at a time.
#
speechMultiSelectString = _("multi-select")

# Translators: this represents the depth of a node in a tree
# view (i.e., how many ancestors a node has).  It is meant to be
# spoken.
#
speechNodeLevelString = _("tree level %d")

# Translators: this represents a list item in a document.
# The nesting level is how 'deep' the item is (e.g., a
# level of 2 represents a list item inside a list that's
# inside another list). This is meant to be spoken.
#
speechNestingLevelString = _("Nesting level %d")

# Translators: this is a indication of the focused icon and the
# count of the total number of icons within an icon panel. An
# example of an icon panel is the Nautilus folder view.
#
speechIconIndexString = _("on %(index)d of %(total)d")

# Translators: this refers to the position of an item in a list
# or group of objects, such as menu items in a menu, radio buttons
# in a radio button group, combobox item in a combobox, etc.
#
speechGroupIndexString = _("%(index)d of %(total)d")

# string to indicate end of printed line for braille displays:
#
disableBrailleEOL = False
brailleEOLIndicator = " $l"

# Translators: Certain objects (such as form controls on web pages)
# can have STATE_REQUIRED set on them to inform the user that this
# field must be filled out. This string is the default string which
# will be spoken and displayed in braille to indicate this state is
# present.
#
brailleRequiredStateString = _("required")

# Translators: this is used to indicate the user is in a text
# area that is not editable.  It is meant to be a short abbreviation
# to be presented on the braille display.
#
brailleReadOnlyString = C_("text", "rdonly")

# Translators: this represents an item on the screen that has
# been set insensitive (or grayed out).
#
brailleInsensitiveString = _("grayed")

# Strings used to indicate checkbox/radio button states in braille:
#
brailleCheckBoxIndicators = ["< >", "<x>", "<->"]
brailleRadioButtonIndicators = ["& y", "&=y"]
brailleToggleButtonIndicators = ["& y", "&=y"]

# Translators: this represents the state of a node in a tree.
# 'expanded' means the children are showing.  'collapsed' means the
# children are not showing.
#
brailleExpansionIndicators = [_("collapsed"), _("expanded")]

# Translators: this represents the depth of a node in a tree
# view (i.e., how many ancestors a node has).  It is meant to
# be presented on a braille display.
#
brailleNodeLevelString = _("TREE LEVEL %d")

# Translators: this represents a list item in a document.
# The nesting level is how 'deep' the item is (e.g., a
# level of 2 represents a list item inside a list that's
# inside another list).  It is meant to be presented on
# the braille display.
#
brailleNestingLevelString = _("LEVEL %d")

# String for delimiters between table cells
#
brailleTableCellDelimiter = " "

# This is for bug #585417 - Allow pauses to be inserted into speech
# output. We're keeping it separate for now until we get the pauses
# sorted out just right.
#
useExperimentalSpeechProsody = True

# If True, whenever a 'pause' keyword is found in a speech formatting
# string, any string being created will be sent to the speech synthesis
# system immediately.  This is for bug #585417 and allows for some
# adaptation to how different systems handle queued speech.  For example,
# some introduce unnaturally long pauses between requests to speak.
#
enablePauseBreaks = True

# Format directives to use in presentTime function.
# By default we use the time format according to the current locale.
# These format strings are passed to python's time.strftime function. To see
# possible directives to embed in the format strings check:
# http://docs.python.org/library/time.html#time.strftime
#
TIME_FORMAT_LOCALE = "%X"
TIME_FORMAT_24_HMS = "%H:%M:%S"
# Translators: Orca has a feature to speak the time
# when the user presses a shortcut key.
# This is one of the alternative formats that the 
# user may wish to be presented with.
#
TIME_FORMAT_24_HMS_WITH_WORDS = _("%H hours, %M minutes and %S seconds.")
TIME_FORMAT_24_HM = "%H:%M"
# Translators: Orca has a feature to speak the time
# when the user presses a shortcut key.
# This is one of the alternative formats that the 
# user may wish to be presented with.
#
TIME_FORMAT_24_HM_WITH_WORDS = _("%H hours and %M minutes.")
TIME_FORMAT_CUSTOM = "%X"
presentTimeFormat = TIME_FORMAT_LOCALE

# Format directives to use in presentDate function.
# By default we use the date format according to the current locale.
# These format strings are passed to python's time.strftime function. To see
# possible directives to embed in the format strings check:
# http://docs.python.org/library/time.html#time.strftime
#
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
DATE_FORMAT_FULL_YMD = "%Y. %B %-d, %A."
DATE_FORMAT_ABBREVIATED_DM = "%a, %-d %b"
DATE_FORMAT_ABBREVIATED_MD = "%a, %b %-d"
DATE_FORMAT_ABBREVIATED_DMY = "%a, %-d %b, %Y"
DATE_FORMAT_ABBREVIATED_MDY = "%a, %b %-d, %Y"
DATE_FORMAT_ABBREVIATED_YMD = "%Y. %b %-d, %a."

# To keep Orca from spitting up upon launch.
#
DATE_FORMAT_WITH_LONG_NAMES = DATE_FORMAT_FULL_DMY
DATE_FORMAT_WITH_SHORT_NAMES = DATE_FORMAT_ABBREVIATED_DMY

presentDateFormat = DATE_FORMAT_LOCALE

# Default tty to pass along to brlapi.
tty = 7
