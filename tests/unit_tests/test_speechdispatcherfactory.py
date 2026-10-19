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

# pylint: disable=protected-access,import-outside-toplevel

"""Speech Dispatcher punctuation overrides and restoration."""

from __future__ import annotations

from unittest.mock import Mock

import pytest


@pytest.fixture
def dispatcher(test_context, monkeypatch):
    """Use the real backend with a recording Speech Dispatcher connection."""

    speechd = pytest.importorskip("speechd")
    i18n = Mock()
    i18n._ = lambda value: value
    i18n.C_ = lambda _context, value: value
    i18n.ngettext = lambda singular, plural, count: singular if count == 1 else plural
    test_context.patch_module("orca.orca_i18n", i18n)
    from orca import speechserver
    from orca.speechdispatcherfactory import SpeechServer
    from orca.speechserver import PunctuationStyle

    server = SpeechServer.__new__(SpeechServer)
    speechserver.SpeechServer.__init__(server)
    server._applied_punctuation_level = None
    server._punctuation_mode_map = {
        style: getattr(speechd.PunctuationMode, style.name, speechd.PunctuationMode.SOME)
        for style in PunctuationStyle
    }
    current = None
    requests = []
    queued = []

    def set_punctuation(value):
        nonlocal current
        current = value
        requests.append(value)

    def record(text, **_kwargs):
        queued.append((text, current))

    server._client = Mock(set_punctuation=Mock(side_effect=set_punctuation))
    server._client.speak.side_effect = record
    server._client.char.side_effect = record
    monkeypatch.setattr(server, "_debug_sd_values", lambda _text: None)
    server._callback_type_map = {}
    server.update_punctuation_level(PunctuationStyle.MOST)
    requests.clear()
    return server, requests, queued


@pytest.mark.unit
@pytest.mark.parametrize("level", ["none", "some", "most", "all"])
@pytest.mark.parametrize("failure", [False, True])
def test_punctuation_override_is_scoped_to_utterance(dispatcher, level, failure):
    """Code retains its override until the next ordinary utterance, even after failure."""

    from orca.acss import ACSS
    from orca.speechserver import PunctuationStyle, SayAllContext

    server, requests, queued = dispatcher
    initial = PunctuationStyle[level.upper()]
    server.update_punctuation_level(initial)
    requests.clear()
    if failure:
        record = server._client.speak.side_effect

        def fail(text, **kwargs):
            record(text, **kwargs)
            raise RuntimeError("synthesis failed")

        server._client.speak.side_effect = fail

    # Both navigation and Say All submit through the same backend path.
    server.speak("return 0;", ACSS({ACSS.PUNCTUATIONS: "all"}))
    assert server._current_punctuation_level == initial
    context = SayAllContext(None, "    }", 0, 5)
    server._say_all(iter([(context, ACSS({ACSS.PUNCTUATIONS: "all"}))]), Mock())
    server.speak("Following prose.", ACSS({}))

    all_mode = server._punctuation_mode_map[PunctuationStyle.ALL]
    initial_mode = server._punctuation_mode_map[initial]
    assert [mode for _text, mode in queued] == [all_mode, all_mode, initial_mode]
    assert server._current_punctuation_level == initial
    assert requests == ([all_mode, initial_mode] if initial != PunctuationStyle.ALL else [])


@pytest.mark.unit
@pytest.mark.parametrize("method", ["speak", "speak_character", "speak_key_event"])
def test_character_after_code_uses_configured_punctuation(dispatcher, method):
    """Character and key presentation also replace the preceding utterance's override."""

    from orca.acss import ACSS
    from orca.speechserver import PunctuationStyle

    server, requests, queued = dispatcher
    server.speak("return 0;", ACSS({ACSS.PUNCTUATIONS: "all"}))
    argument = ";"
    if method == "speak_key_event":
        argument = Mock()
        argument.get_key_name.return_value = ";"
        argument.get_locking_state_string.return_value = ""
    getattr(server, method)(argument)

    all_mode = server._punctuation_mode_map[PunctuationStyle.ALL]
    configured_mode = server._punctuation_mode_map[PunctuationStyle.MOST]
    assert requests == [all_mode, configured_mode]
    assert [mode for _text, mode in queued] == [all_mode, configured_mode]


@pytest.mark.unit
def test_setting_changed_during_override_is_used_for_next_utterance(dispatcher):
    """An override must not replace or restore an outdated user preference."""

    from orca.acss import ACSS
    from orca.speechserver import PunctuationStyle

    server, _requests, queued = dispatcher
    server.speak("return 0;", ACSS({ACSS.PUNCTUATIONS: "all"}))
    server.update_punctuation_level(PunctuationStyle.NONE)
    server.speak("Following prose.")
    assert queued[-1][1] == server._punctuation_mode_map[PunctuationStyle.NONE]
    assert server._current_punctuation_level == PunctuationStyle.NONE


@pytest.mark.unit
def test_failed_punctuation_change_is_retried(dispatcher):
    """Only successful commands update the applied punctuation cache."""

    from orca.acss import ACSS
    from orca.speechserver import PunctuationStyle

    server, _requests, queued = dispatcher
    setter = server._client.set_punctuation.side_effect
    server._client.set_punctuation.side_effect = RuntimeError("punctuation command failed")
    with pytest.raises(RuntimeError, match="punctuation command failed"):
        server.speak("return 0;", ACSS({ACSS.PUNCTUATIONS: "all"}))
    server._client.set_punctuation.side_effect = setter
    server.speak("return 0;", ACSS({ACSS.PUNCTUATIONS: "all"}))
    assert queued[-1][1] == server._punctuation_mode_map[PunctuationStyle.ALL]


@pytest.mark.unit
def test_new_connection_reapplies_configured_punctuation(dispatcher, monkeypatch):
    """A new connection must not inherit the previous connection's cached level."""

    import speechd

    from orca.speechserver import PunctuationStyle

    server, requests, _queued = dispatcher
    server._output_module = None
    monkeypatch.setattr(speechd, "SSIPClient", Mock(return_value=server._client))
    server._init()
    assert requests == [server._punctuation_mode_map[PunctuationStyle.MOST]]
