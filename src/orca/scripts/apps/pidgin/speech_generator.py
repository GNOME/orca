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

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2004-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import orca.speech_generator as speech_generator

class SpeechGenerator(speech_generator.SpeechGenerator):

    def _generateExpandableState(self, obj, **args):
        cell = self._script.utilities.getExpanderCellFor(obj) or obj
        return super()._generateExpandableState(cell, **args)

    def _generateNumberOfChildren(self, obj, **args):
        cell = self._script.utilities.getExpanderCellFor(obj) or obj
        return super()._generateNumberOfChildren(cell, **args)
