# Orca
#
# Copyright 2024 Igalia, S.L.
# Copyright 2024 GNOME Foundation Inc.
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

# pylint: disable=wrong-import-position

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2024 Igalia, S.L." \
                "Copyright (c) 2024 GNOME Foundation Inc."
__license__   = "LGPL"

"""Custom speech generator for WebKitGTK."""

from orca import debug
from orca import speech_generator
from orca.scripts import web


class SpeechGenerator(web.SpeechGenerator):
    """Custom speech generator for WebKitGTK."""

    def generateSpeech(self, obj, **args):
        if self._script.utilities.inDocumentContent(obj):
            return super().generateSpeech(obj, **args)

        msg = "WEBKITGTK: Using default speech generator"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        return speech_generator.SpeechGenerator.generateSpeech(self, obj, **args)
