# Orca
#
# Copyright 2016 Orca Team.
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

"""Utilities for playing sounds."""

import os

import gi
from gi.repository import GLib

try:
    gi.require_version("Gst", "1.0")
    from gi.repository import Gst
except (ImportError, ValueError, gi.repository.GLib.GError):
    _GSTREAMER_AVAILABLE = False
else:
    _GSTREAMER_AVAILABLE = True

from . import debug


class Icon:
    """Sound file representing a particular aspect of an object."""

    def __init__(self, location: str, filename: str) -> None:
        self.path = os.path.join(location, filename)
        msg = f"SOUND: Looking for '{filename}' in {location}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def __str__(self) -> str:
        return f"Icon(path: {self.path}, is_valid: {self.is_valid()})"

    def is_valid(self) -> bool:
        """Returns True if the path associated with this icon is valid."""
        return os.path.isfile(self.path)


class Tone:
    """Tone representing a particular aspect of an object."""

    SINE_WAVE = 0
    SQUARE_WAVE = 1
    SAW_WAVE = 2
    TRIANGLE_WAVE = 3
    SILENCE = 4
    WHITE_UNIFORM_NOISE = 5
    PINK_NOISE = 6
    SINE_WAVE_USING_TABLE = 7
    PERIODIC_TICKS = 8
    WHITE_GAUSSIAN_NOISE = 9
    RED_NOISE = 10
    INVERTED_PINK_NOISE = 11
    INVERTED_RED_NOISE = 12

    def __init__(
        self, duration: float, frequency: int, volume: float = 1.0, wave: int = SINE_WAVE
    ) -> None:
        self.duration = duration
        self.frequency = min(max(0, frequency), 20000)
        self.volume = volume
        self.wave = wave

    def __str__(self) -> str:
        return (
            f"Tone(duration: {self.duration}, "
            f"frequency: {self.frequency}, "
            f"volume: {self.volume}, "
            f"wave: {self.wave})"
        )


class Player:
    """Plays Icons and Tones."""

    def __init__(self) -> None:
        self._initialized: bool = False
        self._source: Gst.Element | None = None
        self._sink: Gst.Element | None = None
        self._player: Gst.Element | None = None
        self._pipeline: Gst.Pipeline | None = None
        self._gstreamer_available: bool = _GSTREAMER_AVAILABLE

        if not self._gstreamer_available:
            msg = "SOUND: Gstreamer is not available"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        self.init()

    def _on_player_message(self, _bus: Gst.Bus, message: Gst.Message) -> None:
        assert self._player is not None
        if message.type == Gst.MessageType.EOS:
            self._player.set_state(Gst.State.NULL)
        elif message.type == Gst.MessageType.ERROR:
            self._player.set_state(Gst.State.NULL)
            error, _info = message.parse_error()
            msg = f"SOUND ERROR: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)

    def _on_pipleline_message(self, _bus: Gst.Bus, message: Gst.Message) -> None:
        assert self._pipeline is not None
        if message.type == Gst.MessageType.EOS:
            self._pipeline.set_state(Gst.State.NULL)
        elif message.type == Gst.MessageType.ERROR:
            self._pipeline.set_state(Gst.State.NULL)
            error, _info = message.parse_error()
            msg = f"SOUND: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)

    def _on_timeout(self, element: Gst.Element) -> bool:
        element.set_state(Gst.State.NULL)
        return False

    def _play_icon(self, icon: Icon, interrupt: bool = True) -> None:
        """Plays a sound icon, interrupting the current play first unless specified."""

        assert self._player is not None
        if interrupt:
            self._player.set_state(Gst.State.NULL)

        self._player.set_property("uri", f"file://{icon.path}")
        self._player.set_state(Gst.State.PLAYING)

    def _play_tone(self, tone: Tone, interrupt: bool = True) -> None:
        """Plays a tone, interrupting the current play first unless specified."""

        assert self._pipeline is not None
        assert self._source is not None
        if interrupt:
            self._pipeline.set_state(Gst.State.NULL)

        self._source.set_property("volume", tone.volume)
        self._source.set_property("freq", tone.frequency)
        self._source.set_property("wave", tone.wave)
        self._pipeline.set_state(Gst.State.PLAYING)
        duration = int(1000 * tone.duration)
        GLib.timeout_add(duration, self._on_timeout, self._pipeline)

    def init(self) -> None:
        """(Re)Initializes the Player."""

        if self._initialized:
            return

        if not self._gstreamer_available:
            return

        Gst.init(None)

        self._player = Gst.ElementFactory.make("playbin", "player")
        if self._player is None:
            msg = "SOUND: Gstreamer is available, but player is None"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        bus = self._player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self._on_player_message)

        self._pipeline = Gst.Pipeline(name="orca-pipeline")
        bus = self._pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self._on_pipleline_message)

        self._source = Gst.ElementFactory.make("audiotestsrc", "src")
        self._sink = Gst.ElementFactory.make("autoaudiosink", "output")
        if self._source is None or self._sink is None:
            return

        self._pipeline.add(self._source)
        self._pipeline.add(self._sink)
        self._source.link(self._sink)

        self._initialized = True

    def play(self, item: Icon | Tone, interrupt: bool = True) -> None:
        """Plays a sound, interrupting the current play first unless specified."""

        if isinstance(item, Icon):
            self._play_icon(item, interrupt)
        elif isinstance(item, Tone):
            self._play_tone(item, interrupt)
        else:
            tokens = ["SOUND:", item, "is not an Icon or Tone"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

    def stop(self, element: Gst.Element | None = None) -> None:
        """Stops play."""

        if not self._gstreamer_available:
            return

        if element:
            element.set_state(Gst.State.NULL)
            return

        if self._player:
            self._player.set_state(Gst.State.NULL)

        if self._pipeline:
            self._pipeline.set_state(Gst.State.NULL)

    def shutdown(self) -> None:
        """Shuts down the sound utilities."""

        if not self._gstreamer_available:
            return

        self.stop()
        self._initialized = False
        self._gstreamer_available = False


_player: Player = Player()


def get_player() -> Player:
    """Returns the Player singleton."""

    return _player
