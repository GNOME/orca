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

"""Custom script for Thunderbird"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2004-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi

from orca.scripts.web import speech_generator


class SpeechGenerator(speech_generator.SpeechGenerator):
    """Provides a speech generator specific to Thunderbird."""

    def __init__(self, script):
        super().__init__(script)

    def _generateColumnHeader(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the column header for an object
        that is in a table, if it exists.  Otherwise, an empty array
        is returned.
        """

        # Don't speak Thunderbird column headers, since
        # it's not possible to navigate across a row.
        return []
