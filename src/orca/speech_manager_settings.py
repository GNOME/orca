# Orca
#
# Copyright 2026 Igalia, S.L.
# Author: Joanmarie Diggs <jdiggs@igalia.com>
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

"""Settings keys for speech and voices."""

from __future__ import annotations


class SpeechManagerSettings:
    """The speech and voices settings keys."""

    KEY_AUTO_LANGUAGE_SWITCHING = "auto-language-switching"
    KEY_AUTO_LANGUAGE_SWITCHING_UI = "auto-language-switching-ui"
    KEY_CAPITALIZATION_STYLE = "capitalization-style"
    KEY_ENABLE = "enable"
    KEY_ESTABLISHED = "established"
    KEY_FAMILY_DIALECT = "family-dialect"
    KEY_FAMILY_GENDER = "family-gender"
    KEY_FAMILY_LANG = "family-lang"
    KEY_FAMILY_NAME = "family-name"
    KEY_FAMILY_VARIANT = "family-variant"
    KEY_INSERT_PAUSES_BETWEEN_UTTERANCES = "insert-pauses-between-utterances"
    KEY_ONLY_SWITCH_CONFIGURED_LANGUAGES = "only-switch-configured-languages"
    KEY_PITCH = "pitch"
    KEY_PITCH_RANGE = "pitch-range"
    KEY_PUNCTUATION_LEVEL = "punctuation-level"
    KEY_RATE = "rate"
    KEY_SPEAK_NUMBERS_AS_DIGITS = "speak-numbers-as-digits"
    KEY_SPEECH_SERVER = "speech-server"
    KEY_SPEECH_SERVER_FACTORY = "speech-server-factory"
    KEY_SYNTHESIZER = "synthesizer"
    KEY_USE_COLOR_NAMES = "use-color-names"
    KEY_USE_PRONUNCIATION_DICTIONARY = "use-pronunciation-dictionary"
    KEY_VOLUME = "volume"
