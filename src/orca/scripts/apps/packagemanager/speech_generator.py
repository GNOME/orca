# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., Franklin Street, Fifth Floor,
# Boston MA  02110-1301 USA.

"""Custom speech generator for Packagemanager."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi

import orca.speech_generator as speech_generator

class SpeechGenerator(speech_generator.SpeechGenerator):
    """Special handling to minimize chattiness and maximize accuracy when
    presenting the package list toggle.
    """

    def __init__(self, script):
        speech_generator.SpeechGenerator.__init__(self, script)

    def generateSpeech(self, obj, **args):
        results = []
        oldRole = None
        if self._script.isLink(obj):
            oldRole = self._overrideRole(pyatspi.ROLE_LINK, args)
        results.extend(
            speech_generator.SpeechGenerator.generateSpeech(self, obj, **args))
        if oldRole:
            self._restoreRole(oldRole, args)

        return results

    def _generateColumnHeader(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the column header for an object
        that is in a table, if it exists.  Otherwise, an empty array
        is returned. Overridden here because we don't want to do this
        for the toggle in the package list.
        """

        result = []
        if not self._script.isPackageListToggle(obj):
            result.extend(speech_generator.SpeechGenerator.\
                _generateColumnHeader(self, obj, **args))
        return result

    def _generateColumnHeaderIfToggleAndNoText(self, obj, **args):
        """If this table cell has a "toggle" action, and doesn't have any
        label associated with it then also speak the table column
        header. Unless we're in the package list.
        """

        result = []
        if not self._script.isPackageListToggle(obj):
            result.extend(speech_generator.SpeechGenerator.\
                _generateColumnHeaderIfToggleAndNoText(self, obj, **args))
        return result

    def _generateAvailability(self, obj, **args):
        """Returns an array of strings for use by speech and braille that
        represent the grayed/sensitivity/availability state of the
        object, but only if it is insensitive (i.e., grayed out and
        inactive).  Otherwise, and empty array will be returned.
        """
        result = []
        if not self._script.isLink(obj):
            result.extend(speech_generator.SpeechGenerator.\
                _generateAvailability(self, obj, **args))
        return result
