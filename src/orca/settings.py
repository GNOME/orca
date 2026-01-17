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
enableAutoLanguageSwitching: bool = True
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
speakProgressBarUpdates: bool = True
progressBarSpeechInterval: int = 10
progressBarSpeechVerbosity: int = PROGRESS_BAR_APPLICATION

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
brailleRolenameStyle: int = VERBOSITY_LEVEL_VERBOSE
brailleSelectorIndicator: int = BRAILLE_UNDERLINE_BOTH
brailleLinkIndicator: int = BRAILLE_UNDERLINE_BOTH
textAttributesBrailleIndicator: int = BRAILLE_UNDERLINE_NONE
brailleVerbosityLevel: int = VERBOSITY_LEVEL_VERBOSE
brailleProgressBarUpdates: bool = False
progressBarBrailleInterval: int = 10
progressBarBrailleVerbosity: int = PROGRESS_BAR_APPLICATION

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
tableNavigationEnabled: bool = True
skipBlankCells: bool = False

# Managed by live_region_presenter.py
enableLiveRegions: bool = True
presentLiveRegionFromInactiveTab: bool = False

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

# Managed by sound_presenter.py
beepProgressBarUpdates: bool = False
progressBarBeepInterval: int = 0
progressBarBeepVerbosity: int = PROGRESS_BAR_APPLICATION
enableSound: bool = True
soundVolume: float = 0.5

# Keyboard
keyboardLayout: int = GENERAL_KEYBOARD_LAYOUT_DESKTOP
orcaModifierKeys: list[str] = DESKTOP_MODIFIER_KEYS
doubleClickTimeout: float = 0.5

# Mouse
presentToolTips: bool = False

# Document navigation and content
nativeNavTriggersFocusMode: bool = True
layoutMode: bool = True
sayAllOnLoad: bool = True
pageSummaryOnLoad: bool = True

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
ignoreStatusBarProgressBars: bool = True

# TODO - JD: This is here until the UI conversion is done.
progressBarUpdateInterval: int = 10
