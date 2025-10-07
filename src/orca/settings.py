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

"""Settings managed by Orca."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2004-2009 Sun Microsystems Inc."
__license__   = "LGPL"

from typing import Any

from . import messages
from .acss import ACSS

userCustomizableSettings: list[str] = [
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
    "enableBrailleContext",
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
    "caretNavigationEnabled",
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

GENERAL_KEYBOARD_LAYOUT_DESKTOP: int = 1
GENERAL_KEYBOARD_LAYOUT_LAPTOP: int = 2

DESKTOP_MODIFIER_KEYS: list[str] = ["Insert", "KP_Insert"]
LAPTOP_MODIFIER_KEYS: list[str] = ["Caps_Lock", "Shift_Lock"]

VERBOSITY_LEVEL_BRIEF: int = 0
VERBOSITY_LEVEL_VERBOSE: int = 1

BRAILLE_UNDERLINE_NONE: int = 0x00 # 00000000
BRAILLE_UNDERLINE_7: int = 0x40 # 01000000
BRAILLE_UNDERLINE_8: int = 0x80 # 10000000
BRAILLE_UNDERLINE_BOTH: int = 0xc0 # 11000000

BRAILLE_ROLENAME_STYLE_SHORT: int = 0 # three letter abbreviations
BRAILLE_ROLENAME_STYLE_LONG: int = 1 # full rolename

PUNCTUATION_STYLE_NONE: int = 3
PUNCTUATION_STYLE_SOME: int = 2
PUNCTUATION_STYLE_MOST: int = 1
PUNCTUATION_STYLE_ALL: int = 0

CAPITALIZATION_STYLE_NONE: str = "none"
CAPITALIZATION_STYLE_SPELL: str = "spell"
CAPITALIZATION_STYLE_ICON: str = "icon"

SAYALL_STYLE_LINE: int = 0
SAYALL_STYLE_SENTENCE: int = 1

PROGRESS_BAR_ALL: int = 0
PROGRESS_BAR_APPLICATION: int = 1
PROGRESS_BAR_WINDOW: int = 2

CHAT_SPEAK_ALL: int = 0
CHAT_SPEAK_ALL_IF_FOCUSED: int = 1
CHAT_SPEAK_FOCUSED_CHANNEL: int = 2

DEFAULT_VOICE: str = "default"
UPPERCASE_VOICE: str = "uppercase"
HYPERLINK_VOICE: str = "hyperlink"
SYSTEM_VOICE: str = "system"

voicesKeys: dict[str, str] = {
"DEFAULT_VOICE"     : "default",
"UPPERCASE_VOICE"   : "uppercase",
"HYPERLINK_VOICE"   : "hyperlink",
"SYSTEM_VOICE"      : "system"
}


voices: dict[str, ACSS] = {
    DEFAULT_VOICE: ACSS({}),
    UPPERCASE_VOICE: ACSS({ACSS.AVERAGE_PITCH : 7.0}),
    HYPERLINK_VOICE: ACSS({}),
    SYSTEM_VOICE: ACSS({}),
}

# Managed by typing_echo_presenter.py
enableKeyEcho: bool = True
enableAlphabeticKeys: bool = True
enableNumericKeys: bool = True
enablePunctuationKeys: bool = True
enableSpace: bool = True
enableModifierKeys: bool = True
enableFunctionKeys: bool = True
enableActionKeys: bool = True
enableNavigationKeys: bool = False
enableDiacriticalKeys: bool = False
enableEchoByCharacter: bool = False
enableEchoByWord: bool = False
enableEchoBySentence: bool = False
presentLockingKeys: bool | None = None

# Managed by speech_and_verbosity_manager.py
silenceSpeech: bool = False
enableSpeech: bool = True
enablePauseBreaks: bool = True
speakNumbersAsDigits: bool = False
speakMisspelledIndicator: bool = True
enableSpeechIndentation: bool = False
speakIndentationOnlyIfChanged: bool = False
speakBlankLines: bool = True
onlySpeakDisplayedText: bool = False
enableTutorialMessages: bool = True
speakDescription: bool = True
enablePositionSpeaking: bool = False
enableMnemonicSpeaking: bool = False
speakContextNonLandmarkForm: bool = True
speakContextBlockquote: bool = True
speakContextPanel: bool = True
speakContextLandmark: bool = True
speakContextList: bool = True
speakContextTable: bool = True
useColorNames: bool = True
readFullRowInGUITable: bool = True
readFullRowInDocumentTable: bool = True
readFullRowInSpreadSheet: bool = False
speakCellSpan: bool = True
speakCellCoordinates: bool = True
speakCellHeaders: bool = True
speakSpreadsheetCoordinates: bool = True
alwaysSpeakSelectedSpreadsheetRange: bool = False
messagesAreDetailed: bool = True
usePronunciationDictionary: bool = True
repeatCharacterLimit: int = 4
speechVerbosityLevel: int = VERBOSITY_LEVEL_VERBOSE
verbalizePunctuationStyle: int = PUNCTUATION_STYLE_MOST
capitalizationStyle: str = CAPITALIZATION_STYLE_NONE

# Managed by say_all_presenter.py
sayAllContextBlockquote: bool = True
sayAllContextPanel: bool = True
sayAllContextNonLandmarkForm: bool = True
sayAllContextLandmark: bool = True
sayAllContextList: bool = True
sayAllContextTable: bool = True
sayAllStyle: int = SAYALL_STYLE_SENTENCE
structNavInSayAll: bool = False
rewindAndFastForwardInSayAll: bool = False

# Managed by flat_review_presenter.py
flatReviewIsRestricted: bool = False

# Managed by braille_presenter.py
enableBraille: bool = True
enableBrailleContext: bool = True
enableFlashMessages: bool = True
brailleFlashTime: int = 5000
flashIsPersistent: bool = False
flashIsDetailed: bool = True
enableBrailleWordWrap: bool = False
enableContractedBraille: bool = False
brailleContractionTable: str = ''
disableBrailleEOL: bool = False
brailleRolenameStyle: int = BRAILLE_ROLENAME_STYLE_LONG
brailleSelectorIndicator: int = BRAILLE_UNDERLINE_BOTH
brailleLinkIndicator: int = BRAILLE_UNDERLINE_BOTH
textAttributesBrailleIndicator: int = BRAILLE_UNDERLINE_NONE
brailleVerbosityLevel: int = VERBOSITY_LEVEL_VERBOSE

# Managed by mouse_review.py
enableMouseReview: bool = False

# Managed by structural_navigator.py
largeObjectTextLength: int = 75
wrappedStructuralNavigation: bool = True
structNavTriggersFocusMode: bool = False
structuralNavigationEnabled: bool = True

# Managed by caret_navigator.py
caretNavTriggersFocusMode: bool = False
caretNavigationEnabled: bool = True

# Managed by table_navigator.py
skipBlankCells: bool = False

# Managed by system_information_presenter.py
presentDateFormat: str = messages.DATE_FORMAT_LOCALE
presentTimeFormat: str = messages.TIME_FORMAT_LOCALE

# Profiles
startingProfile: list[str] = ['Default', 'default']
activeProfile: list[str] = ['Default', 'default']
profile: list[str] = ['Default', 'default']

# Speech
speechFactoryModules: list[str] = ["speechdispatcherfactory", "spiel"]
speechServerFactory: str = "speechdispatcherfactory"
speechServerInfo: list[str] | None = None # None means let the factory decide.
speechSystemOverride: str | None = None

# Braille Monitor
enableBrailleMonitor: bool = False

# Sound
enableSound: bool = True
soundVolume: float = 0.5
playSoundForRole: bool = False
playSoundForState: bool = False
playSoundForPositionInSet: bool = False
playSoundForValue: bool = False

# Keyboard
keyboardLayout: int = GENERAL_KEYBOARD_LAYOUT_DESKTOP
orcaModifierKeys: list[str] = DESKTOP_MODIFIER_KEYS
doubleClickTimeout: float = 0.5

# Mouse
presentToolTips: bool = False

# Progressbars
speakProgressBarUpdates: bool = True
brailleProgressBarUpdates: bool = False
beepProgressBarUpdates: bool = False
progressBarUpdateInterval: int = 10
progressBarSpeechInterval: int | None = None
progressBarBrailleInterval: int | None = None
progressBarBeepInterval: int = 0
progressBarVerbosity: int = PROGRESS_BAR_APPLICATION
ignoreStatusBarProgressBars: bool = True

# Document navigation and content
nativeNavTriggersFocusMode: bool = True
layoutMode: bool = True
inferLiveRegions: bool = True

# Chat
chatMessageVerbosity: int = CHAT_SPEAK_ALL
chatSpeakRoomName: bool = False
chatAnnounceBuddyTyping: bool = False
chatRoomHistories: bool = False

# Spellcheck
spellcheckSpellError: bool = True
spellcheckSpellSuggestion: bool = True
spellcheckPresentContext: bool = True

# App search support
FIND_SPEAK_NONE: int = 0
FIND_SPEAK_IF_LINE_CHANGED: int = 1
FIND_SPEAK_ALL: int = 2
findResultsVerbosity: int = FIND_SPEAK_ALL
findResultsMinimumLength: int = 4

textAttributesToSpeak: list[str] = []
textAttributesToBraille: list[str] = []

# Latent support to allow the user to override/define keybindings
# and braille bindings. Unsupported and undocumented for now.
# Use at your own risk.
#
keyBindingsMap: dict[str, Any] = {}
brailleBindingsMap: dict[str, Any] = {}

# N.B. The following are experimental and may change or go away at any time.
enableSadPidginHack: bool = False
presentChatRoomLast: bool = False
presentLiveRegionFromInactiveTab: bool = False
