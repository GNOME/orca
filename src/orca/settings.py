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

# Managed by typing_echo_presenter.py
presentLockingKeys: bool | None = None

# Managed by speech_manager.py
capitalizationStyle: str = "none"
speakNumbersAsDigits: bool = False

# Managed by braille_presenter.py
enableBraille: bool = True
enableBrailleWordWrap: bool = False
enableContractedBraille: bool = False
brailleContractionTable: str = ""
enableComputerBrailleAtCursor: bool = True
enableBrailleEOL: bool = True
brailleRolenameStyle: int = 1
brailleSelectorIndicator: int = 0xC0
brailleLinkIndicator: int = 0xC0
textAttributesBrailleIndicator: int = 0x00

# Managed by text_attribute_manager.py
textAttributesToSpeak: list[str] = []
textAttributesToBraille: list[str] = []

# Profiles
profile: list[str] = ["Default", "default"]

# Speech
speechFactoryModules: list[str] = ["speechdispatcherfactory", "spiel"]

# Managed by sound_presenter.py
soundVolume: float = 0.5

# Keyboard
doubleClickTimeout: float = 0.5

# N.B. The following are experimental and may change or go away at any time.
enableSadPidginHack: bool = False
ignoreStatusBarProgressBars: bool = True
