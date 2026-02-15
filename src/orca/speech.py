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

"""Speech output functions for Orca."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, TYPE_CHECKING

from . import debug
from . import speech_generator
from .acss import ACSS
from .speechserver import VoiceFamily

if TYPE_CHECKING:
    from . import input_event
    from . import speechserver


@dataclass
class _State:  # pylint: disable=too-many-instance-attributes
    """Mutable state for the speech module."""

    server: speechserver.SpeechServer | None = None
    mute_speech: bool = False
    monitor_group_depth: int = 0
    write_text: Callable[[str], None] | None = None
    write_key: Callable[[str], None] | None = None
    write_character: Callable[[str], None] | None = None
    begin_group: Callable[[], None] | None = None
    end_group: Callable[[], None] | None = None


_state = _State()


def set_server(server: speechserver.SpeechServer | None) -> None:
    """Sets the speech server, called by SpeechManager."""

    _state.server = server


def get_mute_speech() -> bool:
    """Returns whether speech output is temporarily muted."""

    return _state.mute_speech


def set_mute_speech(mute: bool) -> None:
    """Sets whether speech should be muted, called by SpeechManager."""

    _state.mute_speech = mute


def set_monitor_callbacks(
    write_text: Callable[[str], None] | None = None,
    write_key: Callable[[str], None] | None = None,
    write_character: Callable[[str], None] | None = None,
    begin_group: Callable[[], None] | None = None,
    end_group: Callable[[], None] | None = None,
) -> None:
    """Sets the callbacks for updating the speech monitor display."""

    _state.write_text = write_text
    _state.write_key = write_key
    _state.write_character = write_character
    _state.begin_group = begin_group
    _state.end_group = end_group


def _resolve_acss(acss: ACSS | dict[str, Any] | list[dict[str, Any]] | None = None) -> ACSS:
    if isinstance(acss, ACSS):
        family = acss.get(acss.FAMILY)
        if family is not None:
            try:
                family = VoiceFamily(family)
            except (TypeError, ValueError):
                family = VoiceFamily({})
            acss[acss.FAMILY] = family
        return acss
    if isinstance(acss, list) and len(acss) == 1:
        return ACSS(acss[0])
    if isinstance(acss, dict):
        return ACSS(acss)
    return ACSS({})


def say_all(utterance_iterator: Any, progress_callback: Callable[..., Any]) -> None:
    """Speaks each item in the utterance_iterator."""

    if _state.mute_speech:
        return

    server = _state.server
    if server:
        server.say_all(utterance_iterator, progress_callback)
    else:
        for [context, _acss] in utterance_iterator:
            log_line = f"SPEECH OUTPUT: '{context.utterance}'"
            debug.print_message(debug.LEVEL_INFO, log_line, True)


def _speak(text: str, acss: ACSS | dict[str, Any] | None) -> None:
    """Speaks the individual string using the given ACSS."""

    server = _state.server
    if not server:
        log_line = f"SPEECH OUTPUT: '{text}' {acss}"
        debug.print_message(debug.LEVEL_INFO, log_line, True)
        return

    resolved_voice = _resolve_acss(acss)
    msg = f"SPEECH OUTPUT: '{text}' {resolved_voice}"
    debug.print_message(debug.LEVEL_INFO, msg, True)
    server.speak(text, resolved_voice)
    if _state.write_text is not None:
        _state.write_text(text)


def speak(content: Any, acss: ACSS | dict[str, Any] | None = None) -> None:
    """Speaks the given content, which can be a string or a list from the speech generator."""

    if _state.mute_speech:
        return

    if isinstance(content, str):
        msg = f"SPEECH: Speak '{content}' acss: {acss}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        _speak(content, acss)
        return

    if isinstance(content, list):
        tokens = ["SPEECH: Speak", content, ", acss:", acss]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        _begin_monitor_group()
        try:
            _speak_list(content, acss)
        finally:
            _end_monitor_group()
        return

    if not isinstance(content, (speech_generator.Pause, ACSS)):
        msg = f"SPEECH: Bad content sent to speak(): {content}"
        debug.print_message(debug.LEVEL_INFO, msg, True, True)


def _begin_monitor_group() -> None:
    """Signals the start of a grouped utterance to the speech monitor."""

    if _state.monitor_group_depth == 0 and _state.begin_group is not None:
        _state.begin_group()
    _state.monitor_group_depth += 1


def _end_monitor_group() -> None:
    """Signals the end of a grouped utterance to the speech monitor."""

    _state.monitor_group_depth -= 1
    if _state.monitor_group_depth == 0 and _state.end_group is not None:
        _state.end_group()


# pylint: disable-next=too-many-branches
def _speak_list(content: list, acss: ACSS | dict[str, Any] | None) -> None:
    """Processes a list of speech content items."""

    valid_types = (str, list, speech_generator.Pause, ACSS)

    to_speak: list[str] = []
    active_voice = ACSS(acss) if acss is not None else acss

    for element in content:
        if not isinstance(element, valid_types):
            msg = f"SPEECH: Bad content sent to speak(): {element}"
            debug.print_message(debug.LEVEL_INFO, msg, True, True)
        elif isinstance(element, list):
            _speak_list(element, acss)
        elif isinstance(element, str):
            if element:
                to_speak.append(element)
        elif to_speak:
            new_voice = ACSS(acss)
            new_items_to_speak: list[str] = []
            if isinstance(element, speech_generator.Pause):
                if to_speak[-1] and to_speak[-1][-1].isalnum():
                    to_speak[-1] += "."
            elif isinstance(element, ACSS):
                new_voice.update(element)
                if active_voice is None:
                    active_voice = new_voice
                if new_voice == active_voice:
                    continue
                tokens = ["SPEECH: New voice", new_voice, " != active voice", active_voice]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                new_items_to_speak.append(to_speak.pop())

            if to_speak:
                _speak(" ".join(to_speak), active_voice)
            active_voice = new_voice
            to_speak = new_items_to_speak

    if to_speak:
        _speak(" ".join(to_speak), active_voice)


def speak_key_event(
    event: input_event.KeyboardEvent, acss: ACSS | dict[str, Any] | None = None
) -> None:
    """Speaks event immediately using the voice specified by acss."""

    if _state.mute_speech:
        return

    key_name = event.get_key_name()
    acss = _resolve_acss(acss)
    msg = f"{key_name} {event.get_locking_state_string()}"
    log_line = f"SPEECH OUTPUT: '{msg.strip()}' {acss}"
    debug.print_message(debug.LEVEL_INFO, log_line, True)

    server = _state.server
    if server:
        server.speak_key_event(event, acss)
    if _state.write_key is not None:
        _state.write_key(key_name)


def speak_character(character: str, acss: ACSS | dict[str, Any] | None = None) -> None:
    """Speaks character immediately using the voice specified by acss."""

    if _state.mute_speech:
        return

    acss = _resolve_acss(acss)
    log_line = f"SPEECH OUTPUT: '{character}'"
    tokens = [log_line, acss]
    debug.print_tokens(debug.LEVEL_INFO, tokens, True)

    server = _state.server
    if server:
        server.speak_character(character, acss=acss)
    if _state.write_character is not None:
        _state.write_character(character)
