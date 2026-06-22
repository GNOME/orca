# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
# Copyright 2011-2026 Igalia, S.L.
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

"""Command definitions for speech management."""

from __future__ import annotations

import functools
from typing import TYPE_CHECKING

from . import cmdnames, keybindings
from .command import Command, KeyboardCommand

if TYPE_CHECKING:
    from .speech_manager import SpeechManager


def get_commands(owner: SpeechManager) -> list[Command]:
    """Returns commands for speech management."""

    kb_orca_s = keybindings.KeyBinding("s", keybindings.ORCA_MODIFIER_MASK)

    return [
        KeyboardCommand(
            "cycleCapitalizationStyleHandler",
            owner.cycle_capitalization_style,
            owner.GROUP_LABEL,
            cmdnames.CYCLE_CAPITALIZATION_STYLE,
        ),
        KeyboardCommand(
            "cycleSpeakingPunctuationLevelHandler",
            owner.cycle_punctuation_level,
            owner.GROUP_LABEL,
            cmdnames.CYCLE_PUNCTUATION_LEVEL,
        ),
        KeyboardCommand(
            "cycleSynthesizerHandler",
            owner.cycle_synthesizer,
            owner.GROUP_LABEL,
            cmdnames.CYCLE_SYNTHESIZER,
        ),
        KeyboardCommand(
            "cycleVoiceSetHandler",
            owner.cycle_voice_set,
            owner.GROUP_LABEL,
            cmdnames.CYCLE_VOICE_SET,
        ),
        KeyboardCommand(
            "toggleSilenceSpeechHandler",
            owner.toggle_speech,
            owner.GROUP_LABEL,
            cmdnames.TOGGLE_SPEECH,
            desktop_keybinding=kb_orca_s,
            laptop_keybinding=kb_orca_s,
        ),
        KeyboardCommand(
            "decreaseSpeechRateHandler",
            owner.decrease_rate,
            owner.GROUP_LABEL,
            cmdnames.DECREASE_SPEECH_RATE,
        ),
        KeyboardCommand(
            "increaseSpeechRateHandler",
            owner.increase_rate,
            owner.GROUP_LABEL,
            cmdnames.INCREASE_SPEECH_RATE,
        ),
        KeyboardCommand(
            "decreaseSpeechPitchHandler",
            owner.decrease_pitch,
            owner.GROUP_LABEL,
            cmdnames.DECREASE_SPEECH_PITCH,
        ),
        KeyboardCommand(
            "increaseSpeechPitchHandler",
            owner.increase_pitch,
            owner.GROUP_LABEL,
            cmdnames.INCREASE_SPEECH_PITCH,
        ),
        KeyboardCommand(
            "decreaseSpeechInflectionHandler",
            owner.decrease_pitch_range,
            owner.GROUP_LABEL,
            cmdnames.DECREASE_SPEECH_INFLECTION,
        ),
        KeyboardCommand(
            "increaseSpeechInflectionHandler",
            owner.increase_pitch_range,
            owner.GROUP_LABEL,
            cmdnames.INCREASE_SPEECH_INFLECTION,
        ),
        KeyboardCommand(
            "decreaseSpeechVolumeHandler",
            owner.decrease_volume,
            owner.GROUP_LABEL,
            cmdnames.DECREASE_SPEECH_VOLUME,
        ),
        KeyboardCommand(
            "increaseSpeechVolumeHandler",
            owner.increase_volume,
            owner.GROUP_LABEL,
            cmdnames.INCREASE_SPEECH_VOLUME,
        ),
    ]


def get_voice_set_commands(owner: SpeechManager) -> list[KeyboardCommand]:
    """Returns one unbound activation command per available voice set."""

    return [
        KeyboardCommand(
            f"switch-voice-set-{set_id}",
            functools.partial(owner.activate_voice_set, set_id),
            owner.GROUP_LABEL,
            cmdnames.SWITCH_VOICE_SET % owner._voice_set_display_name(set_id),  # pylint: disable=protected-access
            desktop_keybinding=None,
            laptop_keybinding=None,
            transient=True,
        )
        for set_id in owner.get_available_voice_sets()
    ]
