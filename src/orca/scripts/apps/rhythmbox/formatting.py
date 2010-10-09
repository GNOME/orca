# Orca
#
# Copyright 2006-2009 Sun Microsystems Inc.
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

"""Custom formatting for rhythmbox."""

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import copy

import pyatspi

import orca.formatting

formatting = {
    'speech': {
        # When the rating widget changes values, it emits an accessible
        # name changed event. Because it is of ROLE_UNKNOWN, the default
        # speech_generator's _getDefaultSpeech handles it. And because
        # the widget is already focused, it doesn't speak anything. We
        # want to speak the widget's name as it contains the number of
        # stars being displayed.
        #
        pyatspi.ROLE_UNKNOWN: {
            'focused': 'labelAndName'
            },
    }
}

class Formatting(orca.formatting.Formatting):
    def __init__(self, script):
        orca.formatting.Formatting.__init__(self, script)
        self.update(copy.deepcopy(formatting))
