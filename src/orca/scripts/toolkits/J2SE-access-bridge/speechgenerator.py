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

import orca.rolenames as rolenames
import orca.speechgenerator as speechgenerator

from orca.orca_i18n import _ # for gettext support

########################################################################
#                                                                      #
# Speech Generator                                                     #
#                                                                      #
########################################################################

class SpeechGenerator(speechgenerator.SpeechGenerator):
    def __init__(self, script):
        speechgenerator.SpeechGenerator.__init__(self, script)

    def _getSpeechForLabel(self, obj, already_focused):
        """Get the speech for a label.

        Arguments:
        - obj: the label
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = []
        if (not already_focused):
            text = self._script.getDisplayedText(obj)
            if not text:
                text = rolenames.getSpeechForRoleName(obj)
            if text:
                utterances.append(text)

        # In Java, tree objects are labels, so we need to look at their
        # states in order to tell whether they are expanded or collapsed.
        #
        state = obj.getState()
        if state.contains(pyatspi.STATE_EXPANDED):
            # Translators: this represents the state of a node in a tree.
            # 'expanded' means the children are showing.
            # 'collapsed' means the children are not showing.
            #
            utterances.append(_("expanded"))
        elif not state.contains(pyatspi.STATE_EXPANDED) and \
                 state.contains(pyatspi.STATE_EXPANDABLE):
            # Translators: this represents the state of a node in a tree.
            # 'expanded' means the children are showing.
            # 'collapsed' means the children are not showing.
            #
            utterances.append(_("collapsed"))

        self._debugGenerator("J2SE-access-bridge:_getSpeechForLabel",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def getSpeechContext(self, obj, stopAncestor=None):
        """This method is identical to speechgeneratior.getSpeechContext
        with one exception. The following test in
        speechgenerator.getSpeechContext:

            if not text and 'Text' in pyatspi.listInterfaces(parent):
                text = self._script.getDisplayedText(parent)

        has be replaced by

           if not text:
               text = self._script.getDisplayedText(parent)

        The Swing toolkit has labelled panels that do not implement the
        AccessibleText interface, but getDisplayedText returns
        a meaningful string that needs to be used if getDisplayedLabel
        returns None.
        """

        utterances = []

        if not obj:
            return utterances

        if obj == stopAncestor:
            return utterances

        parent = obj.parent
        if parent \
            and (obj.getRole() == pyatspi.ROLE_TABLE_CELL) \
            and (parent.getRole() == pyatspi.ROLE_TABLE_CELL):
            parent = parent.parent

        while parent and (parent.parent != parent):
            if parent == stopAncestor:
                break
            if not self._script.isLayoutOnly(parent):
                text = self._script.getDisplayedLabel(parent)
                if not text and (parent.getRole() == pyatspi.ROLE_PANEL):
                    text = self._script.getDisplayedText(parent)
                if text and len(text.strip()):
                    # Push announcement of cell to the end
                    #
                    if parent.getRole() not in [pyatspi.ROLE_TABLE_CELL,
                                                pyatspi.ROLE_FILLER]:
                        utterances.append(\
                            rolenames.getSpeechForRoleName(parent))
                    utterances.append(text)
                    if parent.getRole() == pyatspi.ROLE_TABLE_CELL:
                        utterances.append(\
                            rolenames.getSpeechForRoleName(parent))
            parent = parent.parent

        utterances.reverse()

        return utterances
