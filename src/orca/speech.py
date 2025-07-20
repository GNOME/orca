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

# pylint: disable=too-many-branches

"""Manages the default speech server for Orca."""

from __future__ import annotations

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import importlib
from typing import Any, Callable, TYPE_CHECKING

from . import debug
from . import settings
from . import speech_generator
from .acss import ACSS
from .speechserver import VoiceFamily

if TYPE_CHECKING:
    from types import ModuleType
    from . import input_event
    from . import speechserver

# The speech server to use for all speech operations.
#
_speechserver: speechserver.SpeechServer | None = None

def _init_speech_server(module_name: str, speech_server_info: list[str] | None) -> None:

    global _speechserver

    if not module_name:
        return

    factory: ModuleType | None = None
    try:
        factory = importlib.import_module(f"orca.{module_name}")
    except ImportError:
        try:
            factory = importlib.import_module(module_name)
        except ImportError:
            debug.print_exception(debug.LEVEL_SEVERE)

    # Now, get the speech server we care about.
    #
    if not factory:
        msg = f"SPEECH: Failed to import module: {module_name}"
        debug.print_message(debug.LEVEL_WARNING, msg, True)
        return

    speech_server_info = settings.speechServerInfo
    if speech_server_info:
        _speechserver = factory.SpeechServer.get_speech_server(speech_server_info)

    if not _speechserver:
        _speechserver = factory.SpeechServer.get_speech_server()
        if speech_server_info:
            tokens = ["SPEECH: Invalid speechServerInfo:", speech_server_info]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

    if not _speechserver:
        msg = f"SPEECH: No speech server for factory: {module_name}"
        debug.print_message(debug.LEVEL_WARNING, msg, True)

def init() -> None:
    """Initializes the speech server."""

    debug.print_message(debug.LEVEL_INFO, "SPEECH: Initializing", True)
    if _speechserver:
        debug.print_message(debug.LEVEL_INFO, "SPEECH: Already initialized", True)
        return

    # HACK: Orca goes to incredible lengths to avoid a broken configuration, so this
    #       last-chance override exists to get the speech system loaded, without risking
    #       it being written to disk unintentionally.
    if settings.speechSystemOverride:
        setattr(settings, "speechServerFactory", settings.speechSystemOverride)
        setattr(settings, "speechServerInfo", ["Default Synthesizer", "default"])

    module_name = settings.speechServerFactory
    _init_speech_server(module_name, settings.speechServerInfo)

    if not _speechserver:
        # Try fallback modules
        module_names = settings.speechFactoryModules
        for module_name in module_names:
            if module_name != settings.speechServerFactory:
                _init_speech_server(module_name, None)
                if _speechserver:
                    break

    if _speechserver:
        tokens = ["SPEECH: Using speech server factory:", module_name]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
    else:
        msg = "SPEECH: Not available"
        debug.print_message(debug.LEVEL_INFO, msg, True)

    debug.print_message(debug.LEVEL_INFO, "SPEECH: Initialized", True)

def __resolve_acss(acss: ACSS | dict[str, Any] | list[dict[str, Any]] | None = None) -> ACSS:
    if isinstance(acss, ACSS):
        family = acss.get(acss.FAMILY)
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
    voices = settings.voices
    return ACSS(voices[settings.DEFAULT_VOICE])

def say_all(utterance_iterator: Any, progress_callback: Callable[..., Any]) -> None:
    """Speaks each item in the utterance_iterator."""

    if settings.silenceSpeech:
        return
    if _speechserver:
        _speechserver.say_all(utterance_iterator, progress_callback)
    else:
        for [context, _acss] in utterance_iterator:
            log_line = f"SPEECH OUTPUT: '{context.utterance}'"
            debug.print_message(debug.LEVEL_INFO, log_line, True)

def _speak(text: str, acss: ACSS | dict[str, Any] | None, interrupt: bool) -> None:
    """Speaks the individual string using the given ACSS."""

    if not _speechserver:
        log_line = f"SPEECH OUTPUT: '{text}' {acss}"
        debug.print_message(debug.LEVEL_INFO, log_line, True)
        return

    voice = ACSS(settings.voices.get(settings.DEFAULT_VOICE))
    try:
        voice.update(__resolve_acss(acss))
    except (TypeError, ValueError, AttributeError) as error:
        msg = f"SPEECH: Exception updating voice with {acss}: {error}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

    resolved_voice = __resolve_acss(voice)
    msg = f"SPEECH OUTPUT: '{text}' {resolved_voice}"
    debug.print_message(debug.LEVEL_INFO, msg, True)
    _speechserver.speak(text, resolved_voice, interrupt)

def speak(content: Any, acss: ACSS | dict[str, Any] | None = None, interrupt: bool = True) -> None:
    """Speaks the given content.  The content can be either a simple
    string or an array of arrays of objects returned by a speech
    generator."""

    if settings.silenceSpeech:
        return

    valid_types = (str, list, speech_generator.Pause, ACSS)
    error = "SPEECH: Bad content sent to speak():"
    if not isinstance(content, valid_types):
        debug.print_message(debug.LEVEL_INFO, error + str(content), True, True)
        return

    if isinstance(content, str):
        msg = f"SPEECH: Speak '{content}' acss: {acss}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
    else:
        tokens = ["SPEECH: Speak", content, ", acss:", acss]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

    if isinstance(content, str):
        _speak(content, acss, interrupt)
    if not isinstance(content, list):
        return

    to_speak = []
    active_voice = acss
    if acss is not None:
        active_voice = ACSS(acss)

    for element in content:
        if not isinstance(element, valid_types):
            debug.print_message(debug.LEVEL_INFO, error + str(element), True, True)
        elif isinstance(element, list):
            speak(element, acss, interrupt)
        elif isinstance(element, str):
            if len(element):
                to_speak.append(element)
        elif to_speak:
            new_voice = ACSS(acss)
            new_items_to_speak = []
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
                string = " ".join(to_speak)
                _speak(string, active_voice, interrupt)
            active_voice = new_voice
            to_speak = new_items_to_speak

    if to_speak:
        string = " ".join(to_speak)
        _speak(string, active_voice, interrupt)

def speak_key_event(
    event: input_event.KeyboardEvent,
    acss: ACSS | dict[str, Any] | None = None
) -> None:
    """Speaks event immediately using the voice specified by acss."""

    if settings.silenceSpeech:
        return

    key_name = event.get_key_name()
    acss = __resolve_acss(acss)
    msg = f"{key_name} {event.get_locking_state_string()}"
    log_line = f"SPEECH OUTPUT: '{msg.strip()}' {acss}"
    debug.print_message(debug.LEVEL_INFO, log_line, True)
    if _speechserver:
        _speechserver.speak_key_event(event, acss)

def speak_character(character: str, acss: ACSS | dict[str, Any] | None = None) -> None:
    """Speaks character immediately using the voice specified by acss."""

    if settings.silenceSpeech:
        return

    acss = __resolve_acss(acss)
    log_line = f"SPEECH OUTPUT: '{character}'"
    tokens = [log_line, acss]
    debug.print_tokens(debug.LEVEL_INFO, tokens, True)
    if _speechserver:
        _speechserver.speak_character(character, acss=acss)

def get_speech_server() -> speechserver.SpeechServer | None:
    """Returns the current speech server."""

    return _speechserver

def deprecated_clear_server() -> None:
    """This is a sad workaround for the current global _speechserver."""

    global _speechserver
    _speechserver = None
