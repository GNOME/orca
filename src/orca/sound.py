# Orca
#
# Copyright 2009 Sun Microsystems Inc.
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

"""Provides support for playing audio files."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2009 Sun Microsystems Inc."
__license__   = "LGPL"

if False:
    # Don't require this until we actually use gst directly instead
    # of doing an os.system call.
    # 
    import pygst
    pygst.require("0.10")
    import gst

class Sound:
    """Class to hold a path to a sound file to play."""
    def __init__(self, path):
        self._path = path

    def play(self):
        if False:
            # WDW - this plays audio once, but then never plays it again.
            #
            pipe = gst.parse_launch(
                "filesrc location=%s ! wavparse ! autoaudiosink" % self._path)
            pipe.set_state(gst.STATE_PLAYING)
        elif True:
            import os
            os.system(
                'gst-launch filesrc location="%s" ! wavparse '\
                '! autoaudiosink > /dev/null 2>&1 &'\
                % self._path)
        else:
            # WDW - This has issues with linking up the pipeline. It
            # doesn't work.
            #
            player = gst.Pipeline("OrcaPlayer")
            source = gst.element_factory_make("filesrc", "file-source")
            decoder = gst.element_factory_make("wavparse", "wav-decoder")
            sink = gst.element_factory_make("autoaudiosink", "audio-sink")
            print(source, decoder, sink)
            player.add(source, decoder, sink)
            gst.element_link_many(source, decoder, sink)
            player.get_by_name("file-source").set_property(
                "location", self._path)
            player.set_state(gst.STATE_PLAYING)
