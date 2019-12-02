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

__id__        = "$Id:$"
__version__   = "$Revision:$"
__date__      = "$Date:$"
__copyright__ = "Copyright (c) 2016 Orca Team"
__license__   = "LGPL"

import gi
from gi.repository import GLib

try:
    gi.require_version('Gst', '1.0')
    from gi.repository import Gst
except:
    _gstreamerAvailable = False
else:
    _gstreamerAvailable, args = Gst.init_check(None)

from . import debug
from .sound_generator import Icon, Tone

class Player:
    """Plays Icons and Tones."""

    def __init__(self):
        self._initialized = False
        self._source = None
        self._sink = None

        if not _gstreamerAvailable:
            msg = 'SOUND ERROR: Gstreamer is not available'
            debug.println(debug.LEVEL_INFO, msg, True)
            return

        self.init()

    def _onPlayerMessage(self, bus, message):
        if message.type == Gst.MessageType.EOS:
            self._player.set_state(Gst.State.NULL)
        elif message.type == Gst.MessageType.ERROR:
            self._player.set_state(Gst.State.NULL)
            error, info = message.parse_error()
            msg = 'SOUND ERROR: %s' % error
            debug.println(debug.LEVEL_INFO, msg, True)

    def _onPipelineMessage(self, bus, message):
        if message.type == Gst.MessageType.EOS:
            self._pipeline.set_state(Gst.State.NULL)
        elif message.type == Gst.MessageType.ERROR:
            self._pipeline.set_state(Gst.State.NULL)
            error, info = message.parse_error()
            msg = 'SOUND ERROR: %s' % error
            debug.println(debug.LEVEL_INFO, msg, True)

    def _onTimeout(self, element):
        element.set_state(Gst.State.NULL)
        return False

    def _playIcon(self, icon, interrupt=True):
        """Plays a sound icon, interrupting the current play first unless specified."""

        if interrupt:
            self._player.set_state(Gst.State.NULL)

        self._player.set_property('uri', 'file://%s' % icon.path)
        self._player.set_state(Gst.State.PLAYING)

    def _playTone(self, tone, interrupt=True):
        """Plays a tone, interrupting the current play first unless specified."""

        if interrupt:
            self._pipeline.set_state(Gst.State.NULL)

        self._source.set_property('volume', tone.volume)
        self._source.set_property('freq', tone.frequency)
        self._source.set_property('wave', tone.wave)
        self._pipeline.set_state(Gst.State.PLAYING)
        duration = int(1000 * tone.duration)
        GLib.timeout_add(duration, self._onTimeout, self._pipeline)

    def init(self):
        """(Re)Initializes the Player."""

        if self._initialized:
            return

        if not _gstreamerAvailable:
            return

        self._player = Gst.ElementFactory.make('playbin', 'player')
        bus = self._player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self._onPlayerMessage)

        self._pipeline = Gst.Pipeline(name='orca-pipeline')
        bus = self._pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self._onPipelineMessage)

        self._source = Gst.ElementFactory.make('audiotestsrc', 'src')
        self._sink = Gst.ElementFactory.make('autoaudiosink', 'output')
        if self._source is None or self._sink is None:
            return

        self._pipeline.add(self._source)
        self._pipeline.add(self._sink)
        self._source.link(self._sink)

        self._initialized = True

    def play(self, item, interrupt=True):
        """Plays a sound, interrupting the current play first unless specified."""

        if isinstance(item, Icon):
            self._playIcon(item, interrupt)
        elif isinstance(item, Tone):
            self._playTone(item, interrupt)
        else:
            msg = 'SOUND ERROR: %s is not an Icon or Tone' % item
            debug.println(debug.LEVEL_INFO, msg, True)

    def stop(self, element=None):
        """Stops play."""

        if not _gstreamerAvailable:
            return

        if element:
            element.set_state(Gst.State.NULL)
            return

        self._player.set_state(Gst.State.NULL)
        self._pipeline.set_state(Gst.State.NULL)

    def shutdown(self):
        """Shuts down the sound utilities."""

        global _gstreamerAvailable
        if not _gstreamerAvailable:
            return

        self.stop()
        self._initialized = False
        _gstreamerAvailable = False

_player = Player()

def getPlayer():
    return _player
