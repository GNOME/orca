# Orca
#
# Copyright 2004-2008 Sun Microsystems Inc.
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

"""Custom script for gaim.  This provides the ability for Orca to
monitor both the IM input and IM output text areas at the same time.

The following script specific key sequences are supported:

  Insert-h      -  Toggle whether we prefix chat room messages with
                   the name of the chat room.
  Insert-[1-9]  -  Speak and braille a previous chat room message.
"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi

import orca.settings as settings
import orca.speechgenerator as speechgenerator

from orca.orca_i18n import _
from orca.orca_i18n import ngettext  # for ngettext support

########################################################################
#                                                                      #
# Custom SpeechGenerator                                               #
#                                                                      #
########################################################################

class SpeechGenerator(speechgenerator.SpeechGenerator):
    """Overrides _getSpeechForTableCell() so that we can provide access
    to the expanded/collapsed state and node count for the buddy list.
    """

    def __init__(self, script):
        speechgenerator.SpeechGenerator.__init__(self, script)

    def _getSpeechForTableCell(self, obj, already_focused):
        """Get the speech utterances for a single table cell

        Arguments:
        - obj: the table cell
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = speechgenerator.SpeechGenerator._getSpeechForTableCell( \
            self, obj, already_focused)

        if not self._script.isInBuddyList(obj):
            return utterances

        # The Pidgin buddy list consists of two columns. The column which
        # is set as the expander column and which also contains the node
        # relationship is hidden.  Hidden columns are not included among
        # a table's columns.  The hidden object of interest seems to always
        # immediately precede the visible object.
        #
        expanderCell = obj.parent[obj.getIndexInParent() - 1]
        if not expanderCell:
            return utterances

        state = expanderCell.getState()
        if state.contains(pyatspi.STATE_EXPANDABLE):
            if state.contains(pyatspi.STATE_EXPANDED):
                # Translators: this represents the state of a node in a tree.
                # 'expanded' means the children are showing.
                # 'collapsed' means the children are not showing.
                #
                utterances.append(_("expanded"))
                childNodes = self._script.getChildNodes(expanderCell)
                children = len(childNodes)

                if not children \
                   or (settings.speechVerbosityLevel == \
                       settings.VERBOSITY_LEVEL_VERBOSE):
                    # Translators: this is the number of items in a layered
                    # pane or table.
                    #
                    itemString = ngettext("%d item",
                                          "%d items",
                                          children) % children
                    utterances.append(itemString)
            else:
                # Translators: this represents the state of a node in a tree.
                # 'expanded' means the children are showing.
                # 'collapsed' means the children are not showing.
                #
                utterances.append(_("collapsed"))

        self._debugGenerator("gaim._getSpeechForTableCell",
                             obj,
                             already_focused,
                             utterances)

        return utterances

