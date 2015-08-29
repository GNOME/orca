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

from . import messages
from .acss import ACSS

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
    "disableBrailleEOL",
    "brailleVerbosityLevel",
    "brailleRolenameStyle",
    "brailleSelectorIndicator",
    "brailleLinkIndicator",
    "brailleAlignmentStyle",
    "enableBrailleMonitor",
    "verbalizePunctuationStyle",
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
    "speakSpreadsheetCoordinates",
    "speakCellSpan",
    "speakCellHeaders",
    "skipBlankCells",
    "largeObjectTextLength",
    "structuralNavigationEnabled",
    "wrappedStructuralNavigation",
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
    "spellcheckSpellError",
    "spellcheckSpellSuggestion",
    "spellcheckPresentContext",
    "useColorNames",
    "findResultsVerbosity",
    "findResultsMinimumLength",
    "structNavTriggersFocusMode",
    "caretNavTriggersFocusMode",
    "layoutMode",
]

GENERAL_KEYBOARD_LAYOUT_DESKTOP = 1
GENERAL_KEYBOARD_LAYOUT_LAPTOP  = 2

DESKTOP_MODIFIER_KEYS = ["Insert", "KP_Insert"]
LAPTOP_MODIFIER_KEYS  = ["Caps_Lock"]

VERBOSITY_LEVEL_BRIEF   = 0
VERBOSITY_LEVEL_VERBOSE = 1

BRAILLE_ALIGN_BY_EDGE   = 0
BRAILLE_ALIGN_BY_MARGIN = 1
BRAILLE_ALIGN_BY_WORD   = 2

BRAILLE_UNDERLINE_NONE = 0x00 # 00000000
BRAILLE_UNDERLINE_7    = 0x40 # 01000000
BRAILLE_UNDERLINE_8    = 0x80 # 10000000
BRAILLE_UNDERLINE_BOTH = 0xc0 # 11000000

BRAILLE_ROLENAME_STYLE_SHORT = 0 # three letter abbreviations
BRAILLE_ROLENAME_STYLE_LONG  = 1 # full rolename

PUNCTUATION_STYLE_NONE = 3
PUNCTUATION_STYLE_SOME = 2
PUNCTUATION_STYLE_MOST = 1
PUNCTUATION_STYLE_ALL  = 0

CAPITALIZATION_STYLE_NONE  = "none"
CAPITALIZATION_STYLE_SPELL = "spell"
CAPITALIZATION_STYLE_ICON = "icon"

SAYALL_STYLE_LINE     = 0
SAYALL_STYLE_SENTENCE = 1

PROGRESS_BAR_ALL         = 0
PROGRESS_BAR_APPLICATION = 1
PROGRESS_BAR_WINDOW      = 2

CHAT_SPEAK_ALL             = 0
CHAT_SPEAK_ALL_IF_FOCUSED  = 1
CHAT_SPEAK_FOCUSED_CHANNEL = 2

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
    UPPERCASE_VOICE: ACSS({ACSS.AVERAGE_PITCH : 7.0}),
    HYPERLINK_VOICE: ACSS({}),
    SYSTEM_VOICE: ACSS({}),
}

# Profiles
startingProfile = ['Default', 'default']
activeProfile   = ['Default', 'default']
profile         = ['Default', 'default']

# Speech
speechFactoryModules         = ["speechdispatcherfactory"]
speechServerFactory          = "speechdispatcherfactory"
speechServerInfo             = None # None means let the factory decide.
enableSpeech                 = True
silenceSpeech                = False
enableTutorialMessages       = False
enableMnemonicSpeaking       = False
enablePositionSpeaking       = False
enableSpeechIndentation      = False
onlySpeakDisplayedText       = False
presentToolTips              = False
speakBlankLines              = True
repeatCharacterLimit         = 4
readTableCellRow             = True
speakCellCoordinates         = True
speakCellSpan                = True
speakCellHeaders             = True
speakSpreadsheetCoordinates  = True
speakMultiCaseStringsAsWords = False
useColorNames                = True
usePronunciationDictionary   = True
sayAllStyle                  = SAYALL_STYLE_SENTENCE
capitalizationStyle          = CAPITALIZATION_STYLE_NONE
verbalizePunctuationStyle    = PUNCTUATION_STYLE_MOST
speechVerbosityLevel         = VERBOSITY_LEVEL_VERBOSE
messageVerbosityLevel        = VERBOSITY_LEVEL_VERBOSE
enablePauseBreaks            = True

# Braille
tty = 7
enableBraille                  = True
enableBrailleMonitor           = False
enableBrailleContext           = True
enableFlashMessages            = True
brailleFlashTime               = 5000
flashIsPersistent              = False
enableContractedBraille        = False
brailleContractionTable        = ''
disableBrailleEOL              = False
brailleRolenameStyle           = BRAILLE_ROLENAME_STYLE_LONG
brailleSelectorIndicator       = BRAILLE_UNDERLINE_BOTH
brailleLinkIndicator           = BRAILLE_UNDERLINE_BOTH
textAttributesBrailleIndicator = BRAILLE_UNDERLINE_NONE
brailleVerbosityLevel          = VERBOSITY_LEVEL_VERBOSE
flashVerbosityLevel            = VERBOSITY_LEVEL_VERBOSE
brailleAlignmentStyle          = BRAILLE_ALIGN_BY_EDGE
brailleAlignmentMargin         = 3
brailleMaximumJump             = 8

# Keyboard and Echo
keyboardLayout               = GENERAL_KEYBOARD_LAYOUT_DESKTOP
orcaModifierKeys             = DESKTOP_MODIFIER_KEYS
doubleClickTimeout           = 0.5
enableKeyEcho                = True
enablePrintableKeys          = True
enableModifierKeys           = True
enableFunctionKeys           = True
enableActionKeys             = True
enableNavigationKeys         = False
enableDiacriticalKeys        = False
enableEchoByCharacter        = False
enableEchoByWord             = False
enableEchoBySentence         = False
presentLockingKeys           = None

# Mouse review
enableMouseReview          = False
mouseDwellDelay            = 0
mouseDwellMaxDrift         = 3

# Progressbars
enableProgressBarUpdates   = True
progressBarUpdateInterval  = 10
progressBarVerbosity       = PROGRESS_BAR_APPLICATION

# Structural navigation
structuralNavigationEnabled = True
skipBlankCells              = False
largeObjectTextLength       = 75
wrappedStructuralNavigation = True
inferLiveRegions            = True
ariaLandmarks = [
    "application",
    "banner",
    "complementary",
    "contentinfo",
    "form",
    "main",
    "navigation",
    "region",
    "search",
]

# Chat
chatMessageVerbosity       = CHAT_SPEAK_ALL
chatSpeakRoomName          = False
chatAnnounceBuddyTyping    = False
chatRoomHistories          = False

# Spellcheck
spellcheckSpellError = True
spellcheckSpellSuggestion = True
spellcheckPresentContext = True

# Day and time
presentDateFormat = messages.DATE_FORMAT_LOCALE
presentTimeFormat = messages.TIME_FORMAT_LOCALE

# App search support
FIND_SPEAK_NONE = 0
FIND_SPEAK_IF_LINE_CHANGED  = 1
FIND_SPEAK_ALL = 2
findResultsVerbosity = FIND_SPEAK_ALL
findResultsMinimumLength = 4

# The complete list of possible text attributes.
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
    "paragraph-style:; text-spelling:none; fg-color:; bg-color:;"

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

# Latent support to allow the user to override/define keybindings
# and braille bindings. Unsupported and undocumented for now.
# Use at your own risk.
#
keyBindingsMap          = {}
brailleBindingsMap      = {}

# TODO - JD: Is this still needed now that AT-SPI has its own timeout?
timeoutTime             = 10   # a value of 0 means don't do hang checking
timeoutCallback         = None # Set by orca.py:init to orca.timeout

structNavTriggersFocusMode = False
caretNavTriggersFocusMode = False

layoutMode = True

# NOTE: The following are experimental and may be changed or removed at
# any time
rewindAndFastForwardInSayAll = False
structNavInSayAll = False
