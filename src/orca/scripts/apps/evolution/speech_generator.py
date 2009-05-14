# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
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

"""Custom script for Evolution."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi

import orca.speechgenerator as speechgenerator

class SpeechGenerator(speechgenerator.SpeechGenerator):
    """Overrides _getSpeechForTableCell so that, if this is an expanded 
       table cell,  we can strip off the "0 items".
    """

    def __init__(self, script):
        speechgenerator.SpeechGenerator.__init__(self, script)

    def _getIsDesiredFocusedItem(self, obj, already_focused):
        # Check that we are in a table cell in the mail message header list.
        # If we are and this table cell has an expanded state, and the first
        # token of the last utterances is "0", then strip off that last 
        # utterance ("0 items"). See bug #432308 for more details.
        #
        rolesList = [pyatspi.ROLE_TABLE_CELL, \
                     pyatspi.ROLE_TREE_TABLE, \
                     pyatspi.ROLE_UNKNOWN]
        if self._script.isDesiredFocusedItem(obj, rolesList):
            return True
        else:
            return False
