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
    "readFullRowInGUITable",
    "readFullRowInDocumentTable",
    "readFullRowInSpreadSheet",
    "enableSpeechIndentation",
    "enableEchoByCharacter",
    "enableEchoByWord",
    "enableEchoBySentence",
    "enableKeyEcho",
    "enableAlphabeticKeys",
    "enableNumericKeys",
    "enablePunctuationKeys",
    "enableSpace",
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
    "disableBrailleEOL",
    "brailleVerbosityLevel",
    "brailleRolenameStyle",
    "brailleSelectorIndicator",
    "brailleLinkIndicator",
    "enableSound",
    "soundVolume",
    "playSoundForRole",
    "playSoundForState",
    "playSoundForPositionInSet",
    "playSoundForValue",
    "verbalizePunctuationStyle",
    "presentToolTips",
    "sayAllStyle",
    "keyboardLayout",
    "speakBlankLines",
    "speakNumbersAsDigits",
    "speakMisspelledIndicator",
    "textAttributesToSpeak",
    "textAttributesToBraille",
    "textAttributesBrailleIndicator",
    "profile",
    "speakProgressBarUpdates",
    "brailleProgressBarUpdates",
    "beepProgressBarUpdates",
    "progressBarUpdateInterval",
    "progressBarVerbosity",
    "ignoreStatusBarProgressBars",
    "enableBrailleWordWrap",
    "enableContractedBraille",
    "brailleContractionTable",
    "enableMouseReview",
    "speakCellCoordinates",
    "speakSpreadsheetCoordinates",
    "alwaysSpeakSelectedSpreadsheetRange",
    "speakCellSpan",
    "speakCellHeaders",
    "skipBlankCells",
    "largeObjectTextLength",
    "structuralNavigationEnabled",
    "wrappedStructuralNavigation",
    "chatMessageVerbosity",
    "chatSpeakRoomName",
    "chatAnnounceBuddyTyping",
    "chatRoomHistories",
    "enableFlashMessages",
    "brailleFlashTime",
    "flashIsPersistent",
    "flashIsDetailed",
    "messagesAreDetailed",
    "presentDateFormat",
    "presentTimeFormat",
    "activeProfile",
    "startingProfile",
    "spellcheckSpellError",
    "spellcheckSpellSuggestion",
    "spellcheckPresentContext",
    "useColorNames",
    "capitalizationStyle",
    "findResultsVerbosity",
    "findResultsMinimumLength",
    "structNavTriggersFocusMode",
    "caretNavTriggersFocusMode",
    "layoutMode",
    "nativeNavTriggersFocusMode",
    "rewindAndFastForwardInSayAll",
    "structNavInSayAll",
    "speakDescription",
    "speakContextBlockquote",
    "speakContextPanel",
    "speakContextLandmark",
    "speakContextNonLandmarkForm",
    "speakContextList",
    "speakContextTable",
    "sayAllContextBlockquote",
    "sayAllContextPanel",
    "sayAllContextLandmark",
    "sayAllContextNonLandmarkForm",
    "sayAllContextList",
    "sayAllContextTable"
]

GENERAL_KEYBOARD_LAYOUT_DESKTOP = 1
GENERAL_KEYBOARD_LAYOUT_LAPTOP  = 2

DESKTOP_MODIFIER_KEYS = ["Insert", "KP_Insert"]
LAPTOP_MODIFIER_KEYS  = ["Caps_Lock", "Shift_Lock"]

VERBOSITY_LEVEL_BRIEF   = 0
VERBOSITY_LEVEL_VERBOSE = 1

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
speechFactoryModules         = ["speechdispatcherfactory", "spiel"]
speechServerFactory          = "speechdispatcherfactory"
speechServerInfo             = None # None means let the factory decide.
speechSystemOverride         = None
enableSpeech                 = True
silenceSpeech                = False
enableTutorialMessages       = True
enableMnemonicSpeaking       = False
enablePositionSpeaking       = False
enableSpeechIndentation      = False
onlySpeakDisplayedText       = False
presentToolTips              = False
speakBlankLines              = True
repeatCharacterLimit         = 4
readFullRowInGUITable        = True
readFullRowInDocumentTable   = True
readFullRowInSpreadSheet     = False
speakCellCoordinates         = True
speakCellSpan                = True
speakCellHeaders             = True
speakSpreadsheetCoordinates  = True
alwaysSpeakSelectedSpreadsheetRange = False
speakNumbersAsDigits         = False
speakMisspelledIndicator     = True
useColorNames                = True
usePronunciationDictionary   = True
sayAllStyle                  = SAYALL_STYLE_SENTENCE
capitalizationStyle          = CAPITALIZATION_STYLE_NONE
verbalizePunctuationStyle    = PUNCTUATION_STYLE_MOST
speechVerbosityLevel         = VERBOSITY_LEVEL_VERBOSE
messagesAreDetailed          = True
enablePauseBreaks            = True
speakDescription             = True
speakContextBlockquote       = True
speakContextPanel            = True
speakContextNonLandmarkForm  = True
speakContextLandmark         = True
speakContextList             = True
speakContextTable            = True
sayAllContextBlockquote      = True
sayAllContextPanel           = True
sayAllContextNonLandmarkForm = True
sayAllContextLandmark        = True
sayAllContextList            = True
sayAllContextTable           = True

# Braille
enableBraille                  = True
enableBrailleMonitor           = False
enableFlashMessages            = True
brailleFlashTime               = 5000
flashIsPersistent              = False
flashIsDetailed                = True
enableBrailleWordWrap          = False
enableContractedBraille        = False
brailleContractionTable        = ''
disableBrailleEOL              = False
brailleRolenameStyle           = BRAILLE_ROLENAME_STYLE_LONG
brailleSelectorIndicator       = BRAILLE_UNDERLINE_BOTH
brailleLinkIndicator           = BRAILLE_UNDERLINE_BOTH
textAttributesBrailleIndicator = BRAILLE_UNDERLINE_NONE
brailleVerbosityLevel          = VERBOSITY_LEVEL_VERBOSE

# Sound
enableSound = True
soundVolume = 0.5
playSoundForRole = False
playSoundForState = False
playSoundForPositionInSet = False
playSoundForValue = False

# Keyboard and Echo
keyboardLayout               = GENERAL_KEYBOARD_LAYOUT_DESKTOP
orcaModifierKeys             = DESKTOP_MODIFIER_KEYS
doubleClickTimeout           = 0.5
enableKeyEcho                = True
enableAlphabeticKeys         = True
enableNumericKeys            = True
enablePunctuationKeys        = True
enableSpace                  = True
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

# Flat review
flatReviewIsRestricted = False

# Progressbars
speakProgressBarUpdates    = True
brailleProgressBarUpdates  = False
beepProgressBarUpdates     = False
progressBarUpdateInterval  = 10
progressBarSpeechInterval  = None
progressBarBrailleInterval = None
progressBarBeepInterval    = 0
progressBarVerbosity       = PROGRESS_BAR_APPLICATION
ignoreStatusBarProgressBars = True

# Structural navigation
structuralNavigationEnabled = True
skipBlankCells              = False
largeObjectTextLength       = 75
wrappedStructuralNavigation = True
inferLiveRegions            = True

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

textAttributesToSpeak = []
textAttributesToBraille = []

# Latent support to allow the user to override/define keybindings
# and braille bindings. Unsupported and undocumented for now.
# Use at your own risk.
#
keyBindingsMap          = {}
brailleBindingsMap      = {}

structNavTriggersFocusMode = False
caretNavTriggersFocusMode = False
nativeNavTriggersFocusMode = True

layoutMode = True

rewindAndFastForwardInSayAll = False
structNavInSayAll = False

# N.B. The following are experimental and may change or go away at any time.
enableSadPidginHack = False
presentChatRoomLast = False
presentLiveRegionFromInactiveTab = False
speakIndentationOnlyIfChanged = False
speakPresentationMode = True
beepPresentationMode = False
