# Orca
#
# Copyright 2004-2009 Sun Microsystems Inc.
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

""" Custom script for Thunderbird 3.
"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2004-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi

import orca.scripts.toolkits.Gecko as Gecko

from orca.orca_i18n import _

########################################################################
#                                                                      #
# Custom SpeechGenerator for Thunderbird                               #
#                                                                      #
########################################################################

class SpeechGenerator(Gecko.SpeechGenerator):
    """Provides a speech generator specific to Thunderbird.
    """

    # pylint: disable-msg=W0142

    def __init__(self, script):
        Gecko.SpeechGenerator.__init__(self, script)

    def _generateRoleName(self, obj, **args):
        """Prevents some roles from being spoken."""
        result = []
        role = args.get('role', obj.getRole())
        if role == pyatspi.ROLE_DOCUMENT_FRAME \
           and obj.getState().contains(pyatspi.STATE_EDITABLE):
            pass
        else:
            result.extend(Gecko.SpeechGenerator._generateRoleName(
                              self, obj, **args))

        return result

    def _generateColumnHeader(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the column header for an object
        that is in a table, if it exists.  Otherwise, an empty array
        is returned.
        """
        result = []

        # Don't speak Thunderbird column headers, since
        # it's not possible to navigate across a row.
        #
        return result

    def _generateUnrelatedLabels(self, obj, **args):
        """Finds all labels not in a label for or labelled by relation.
        If this is the spell checking dialog, then there are no
        unrelated labels.  See bug #535192 for more details.
        """
        result = []

        # Translators: this is what the name of the spell checking
        # dialog in Thunderbird begins with. The translated form
        # has to match what Thunderbird is using.  We hate keying
        # off stuff like this, but we're forced to do so in this case.
        #
        if obj.name.startswith(_("Check Spelling")) \
           and self._script.isDesiredFocusedItem(
                   obj, [pyatspi.ROLE_DIALOG,
                         pyatspi.ROLE_APPLICATION]):
            pass
        else:
            result.extend(Gecko.SpeechGenerator._generateUnrelatedLabels(
                              self, obj, **args))
        return result
