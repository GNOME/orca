# Orca
#
# Copyright 2006-2008 Sun Microsystems Inc.
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

__id__        = "$Id: J2SE-access-bridge.py 3882 2008-05-07 18:22:10Z richb $"
__version__   = "$Revision: 3882 $"
__date__      = "$Date: 2008-05-07 14:22:10 -0400 (Wed, 07 May 2008) $"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi

import orca.braille as braille
import orca.braillegenerator as braillegenerator

from orca.orca_i18n import _ # for gettext support

########################################################################
#                                                                      #
# Braille Generator                                                    #
#                                                                      #
########################################################################

class BrailleGenerator(braillegenerator.BrailleGenerator):
    def __init__(self, script):
        braillegenerator.BrailleGenerator.__init__(self, script)

    def _getBrailleRegionsForLabel(self, obj):
        """Get the braille for a label.

        Arguments:
        - obj: the label

        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """

        self._debugGenerator("J2SE-access-bridge:_getBrailleRegionsForLabel",
                             obj)

        regions = []

        text = self._script.getDisplayedText(obj)

        # In Java, tree objects are labels, so we need to look at their
        # states in order to tell whether they are expanded or collapsed.
        #
        state = obj.getState()
        if state.contains(pyatspi.STATE_EXPANDABLE):
            if state.contains(pyatspi.STATE_EXPANDED):
                # Translators: this represents the state of a node in a tree.
                # 'expanded' means the children are showing.
                # 'collapsed' means the children are not showing.
                #
                text = self._script.appendString(text, _('expanded'))
            else:
                # Translators: this represents the state of a node in a tree.
                # 'expanded' means the children are showing.
                # 'collapsed' means the children are not showing.
                #
                text = self._script.appendString(text, _('collapsed'))

        level = self._script.getNodeLevel(obj)
        if level >= 0:
            # Translators: this represents the depth of a node in a tree
            # view (i.e., how many ancestors a node has).
            #
            text = self._script.appendString(text,
                                             _("TREE LEVEL %d") % (level + 1))

        region = braille.Component(obj, text)
        regions.append(region)

        return [regions, region]
