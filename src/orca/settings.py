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

# pylint:disable=invalid-name

"""Settings managed by Orca."""

GENERAL_KEYBOARD_LAYOUT_DESKTOP: int = 1
GENERAL_KEYBOARD_LAYOUT_LAPTOP: int = 2

DESKTOP_MODIFIER_KEYS: list[str] = ["Insert", "KP_Insert"]
LAPTOP_MODIFIER_KEYS: list[str] = ["Caps_Lock", "Shift_Lock"]

VERBOSITY_LEVEL_BRIEF: int = 0
VERBOSITY_LEVEL_VERBOSE: int = 1

BRAILLE_UNDERLINE_NONE: int = 0x00  # 00000000
BRAILLE_UNDERLINE_7: int = 0x40  # 01000000
BRAILLE_UNDERLINE_8: int = 0x80  # 10000000
BRAILLE_UNDERLINE_BOTH: int = 0xC0  # 11000000

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

CHAT_SPEAK_ALL_ANY_APP: int = 0
CHAT_SPEAK_ALL_ACTIVE_APP: int = 1
CHAT_SPEAK_CURRENT_ACTIVE_APP: int = 2
CHAT_SPEAK_CURRENT_ANY_APP: int = 3

DEFAULT_VOICE: str = "default"
UPPERCASE_VOICE: str = "uppercase"
HYPERLINK_VOICE: str = "hyperlink"
SYSTEM_VOICE: str = "system"

# Managed by typing_echo_presenter.py
presentLockingKeys: bool | None = None

# Managed by speech_manager.py
capitalizationStyle: str = CAPITALIZATION_STYLE_NONE
speakNumbersAsDigits: bool = False

# Managed by say_all_presenter.py
sayAllStyle: int = SAYALL_STYLE_SENTENCE

# Managed by braille_presenter.py
enableBraille: bool = True
enableBrailleWordWrap: bool = False
enableContractedBraille: bool = False
brailleContractionTable: str = ""
enableComputerBrailleAtCursor: bool = True
disableBrailleEOL: bool = False  # Deprecated. Use enableBrailleEOL.
enableBrailleEOL: bool = not disableBrailleEOL
brailleRolenameStyle: int = VERBOSITY_LEVEL_VERBOSE
brailleSelectorIndicator: int = BRAILLE_UNDERLINE_BOTH
brailleLinkIndicator: int = BRAILLE_UNDERLINE_BOTH
textAttributesBrailleIndicator: int = BRAILLE_UNDERLINE_NONE
brailleVerbosityLevel: int = VERBOSITY_LEVEL_VERBOSE

# Managed by document_presenter.py
FIND_SPEAK_NONE: int = 0
FIND_SPEAK_IF_LINE_CHANGED: int = 1
FIND_SPEAK_ALL: int = 2

# Managed by text_attribute_manager.py
textAttributesToSpeak: list[str] = []
textAttributesToBraille: list[str] = []

# Managed by structural_navigator.py
structuralNavigationEnabled: bool = True

# Managed by caret_navigator.py
caretNavigationEnabled: bool = True

# Managed by table_navigator.py
tableNavigationEnabled: bool = True

# Managed by live_region_presenter.py
enableLiveRegions: bool = True

# Profiles
startingProfile: list[str] = ["Default", "default"]
activeProfile: list[str] = ["Default", "default"]
profile: list[str] = ["Default", "default"]

# Speech
speechFactoryModules: list[str] = ["speechdispatcherfactory", "spiel"]
speechServerFactory: str = "speechdispatcherfactory"
speechServerInfo: list[str] | None = None  # None means let the factory decide.

# Managed by braille_presenter.py
brailleMonitorCellCount: int = 32
brailleMonitorShowDots: bool = False
brailleMonitorForeground: str = "#000000"
brailleMonitorBackground: str = "#ffffff"

# Managed by speech_presenter.py
speechMonitorFontSize: int = 14
speechMonitorForeground: str = "#ffffff"
speechMonitorBackground: str = "#000000"

# Managed by sound_presenter.py
soundVolume: float = 0.5

# Keyboard
keyboardLayout: int = GENERAL_KEYBOARD_LAYOUT_DESKTOP
orcaModifierKeys: list[str] = DESKTOP_MODIFIER_KEYS
doubleClickTimeout: float = 0.5

# Managed by chat_presenter.py
chatMessageVerbosity: int = CHAT_SPEAK_ALL_ANY_APP

# N.B. The following are experimental and may change or go away at any time.
enableSadPidginHack: bool = False
ignoreStatusBarProgressBars: bool = True
