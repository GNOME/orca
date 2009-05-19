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

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import orca.speechgenerator as speechgenerator

########################################################################
#                                                                      #
# Custom SpeechGenerator                                               #
#                                                                      #
########################################################################

class SpeechGenerator(speechgenerator.SpeechGenerator):
    """Overrides _getSpeechForTableCell() so that we can provide access
    to the expanded/collapsed state and node count for the buddy list.
    """

    # pylint: disable-msg=W0142

    def __init__(self, script):
        speechgenerator.SpeechGenerator.__init__(self, script)

    def _getExpandableState(self, obj, **args):
        result = []
        if self._script.isInBuddyList(obj):
            # The Pidgin buddy list consists of two columns. The
            # column which is set as the expander column and which
            # also contains the node relationship is hidden.  Hidden
            # columns are not included among a table's columns.  The
            # hidden object of interest seems to always immediately
            # precede the visible object.
            #
            expanderCell = obj.parent[obj.getIndexInParent() - 1]
            if expanderCell:
                result.extend(
                    speechgenerator.SpeechGenerator._getExpandableState(
                        self, expanderCell, **args))
            else:
                result.extend(
                    speechgenerator.SpeechGenerator._getExpandableState(
                        self, obj, **args))
        else:
            result.extend(
                speechgenerator.SpeechGenerator._getExpandableState(
                    self, obj, **args))
        return result

    def _getNumberOfChildren(self, obj, **args):
        result = []
        if self._script.isInBuddyList(obj):
            # The Pidgin buddy list consists of two columns. The
            # column which is set as the expander column and which
            # also contains the node relationship is hidden.  Hidden
            # columns are not included among a table's columns.  The
            # hidden object of interest seems to always immediately
            # precede the visible object.
            #
            expanderCell = obj.parent[obj.getIndexInParent() - 1]
            if expanderCell:
                result.extend(
                    speechgenerator.SpeechGenerator._getNumberOfChildren(
                        self, expanderCell, **args))
            else:
                result.extend(
                    speechgenerator.SpeechGenerator._getNumberOfChildren(
                        self, obj, **args))
        else:
            result.extend(
                speechgenerator.SpeechGenerator._getNumberOfChildren(
                    self, obj, **args))
        return result
