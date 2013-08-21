# Orca
#
# Copyright 2013 The Orca Team.
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

"""Custom speech generator for gnome-documents."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2013 The Orca Team"
__license__   = "LGPL"

import orca.speech_generator as speech_generator

class SpeechGenerator(speech_generator.SpeechGenerator):

    def __init__(self, script):
        speech_generator.SpeechGenerator.__init__(self, script)

    def _generateUnselectedCell(self, obj, **args):
        # There are a number of objects in gnome-documents which claim to
        # be selectable, but cannot actually be selected. Until we find and
        # fix those issues, this will keep Orca from constantly tacking on
        # "not selected" when presenting these objects.
        return []
