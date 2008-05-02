# Orca
#
# Copyright 2004-2007 Sun Microsystems Inc.
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
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

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
__copyright__ = "Copyright (c) 2005-2007 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi

import orca.debug as debug
import orca.orca_state as orca_state
import orca.rolenames as rolenames
import orca.speech as speech
import orca.where_am_I as where_am_I

from orca.orca_i18n import _

########################################################################
#                                                                      #
# Custom WhereAmI                                                      #
#                                                                      #
######################################################################## 

class WhereAmI(where_am_I.WhereAmI):
    """Overrides _speakTableCell() so that we can provide access
    to the expanded/collapsed state for items in the buddy list.
    """

    def __init__(self, script):
        where_am_I.WhereAmI.__init__(self, script)
        self._script = script
        
    def _speakTableCell(self, obj, doubleClick):
        """Tree Tables present the following information (an example is
        'Tree table, Mike Pedersen, row 8 of 10, tree level 2'):

        1. label, if any
        2. role
        3. current row (regardless of speak cell/row setting)
        4. relative position
        5. if expandable/collapsible: expanded/collapsed
        6. if applicable, the level

        """

        if not self._script.isInBuddyList(obj):
            return where_am_I.WhereAmI._speakTableCell(self, obj, doubleClick)

        # Speak the first two items (and possibly the position)
        #
        utterances = []
        if obj.parent.getRole() == pyatspi.ROLE_TABLE_CELL:
            obj = obj.parent
        parent = obj.parent

        text = self._getObjLabel(obj)
        utterances.append(text)

        text = rolenames.getSpeechForRoleName(obj)
        utterances.append(text)
        debug.println(self._debugLevel, "first table cell utterances=%s" % \
                      utterances)
        speech.speakUtterances(utterances)

        utterances = []
        if doubleClick:
            table = parent.queryTable()
            row = table.getRowAtIndex(
              orca_state.locusOfFocus.getIndexInParent())
            # Translators: this in reference to a row in a table.
            #
            text = _("row %d of %d") % ((row+1), table.nRows)
            utterances.append(text)
            speech.speakUtterances(utterances)

        # Speak the current row
        #
        utterances = self._getTableRow(obj)
        debug.println(self._debugLevel, "second table cell utterances=%s" % \
                      utterances)
        speech.speakUtterances(utterances)

        # Speak the remaining items.
        #
        utterances = []

        if not doubleClick:
            try:
                table = parent.queryTable()
            except NotImplementedError:
                debug.println(self._debugLevel, 
                              "??? parent=%s" % parent.getRoleName())
                return
            else:
                row = \
                    table.getRowAtIndex(
                       orca_state.locusOfFocus.getIndexInParent())
                # Translators: this in reference to a row in a table.
                #
                text = _("row %d of %d") % ((row+1), table.nRows)
                utterances.append(text)

        # The difference/reason for overriding:  We obtain the expanded
        # state from the hidden object that immediately precedes obj.
        #
        try:
            state = obj.parent[obj.getIndexInParent() - 1].getState()
        except:
            state = obj.getState()

        if state.contains(pyatspi.STATE_EXPANDABLE):
            if state.contains(pyatspi.STATE_EXPANDED):
                # Translators: this represents the state of a node in a tree.
                # 'expanded' means the children are showing.
                # 'collapsed' means the children are not showing.
                #
                text = _("expanded")
            else:
                # Translators: this represents the state of a node in a tree.
                # 'expanded' means the children are showing.
                # 'collapsed' means the children are not showing.
                #
                text = _("collapsed")
            utterances.append(text)

        level = self._script.getNodeLevel(orca_state.locusOfFocus)
        if level >= 0:
            # Translators: this represents the depth of a node in a tree
            # view (i.e., how many ancestors a node has).
            #
            utterances.append(_("tree level %d") % (level + 1))

        debug.println(self._debugLevel, "third table cell utterances=%s" % \
                      utterances)
        speech.speakUtterances(utterances)
