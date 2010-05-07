# Orca
#
# Copyright 2010 Joanmarie Diggs.
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

"""Commonly-required utility methods needed by -- and potentially
   customized by -- application and toolkit scripts. They have
   been pulled out from the scripts because certain scripts had
   gotten way too large as a result of including these methods."""

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2010 Joanmarie Diggs."
__license__   = "LGPL"

import pyatspi

import orca.debug as debug
import orca.script_utilities as script_utilities

#############################################################################
#                                                                           #
# Utilities                                                                 #
#                                                                           #
#############################################################################

class Utilities(script_utilities.Utilities):

    def __init__(self, script):
        """Creates an instance of the Utilities class.

        Arguments:
        - script: the script with which this instance is associated.
        """

        script_utilities.Utilities.__init__(self, script)

    #########################################################################
    #                                                                       #
    # Utilities for finding, identifying, and comparing accessibles         #
    #                                                                       #
    #########################################################################

    def displayedText(self, obj):
        """Returns the text being displayed for an object. Overridden here
        because OpenOffice uses symbols (e.g. ">>" for buttons but exposes
        more useful information via the accessible's name.

        Arguments:
        - obj: the object

        Returns the text being displayed for an object or None if there isn't
        any text being shown.
        """

        if obj.getRole() == pyatspi.ROLE_PUSH_BUTTON and obj.name:
            return obj.name
        else:
            return script_utilities.Utilities.displayedText(self, obj)

    def isReadOnlyTextArea(self, obj):
        """Returns True if obj is a text entry area that is read only."""

        if not obj.getRole() == pyatspi.ROLE_TEXT:
            return False

        state = obj.getState()
        readOnly = state.contains(pyatspi.STATE_FOCUSABLE) \
                   and not state.contains(pyatspi.STATE_EDITABLE)
        debug.println(debug.LEVEL_ALL,
                      "soffice - isReadOnlyTextArea=%s for %s" \
                      % (readOnly, debug.getAccessibleDetails(obj)))

        return readOnly

    def frameAndDialog(self, obj):
        """Returns the frame and (possibly) the dialog containing
        the object. Overridden here for presentation of the title
        bar information: If the locusOfFocus is a spreadsheet cell,
        1) we are not in a dialog and 2) we need to present both the
        frame name and the sheet name. So we might as well return the
        sheet in place of the dialog so that the default code can do
        its thing.
        """

        if not self._script.isSpreadSheetCell(obj):
            return script_utilities.Utilities.frameAndDialog(self, obj)

        results = [None, None]

        parent = obj.parent
        while parent and (parent.parent != parent):
            if parent.getRole() == pyatspi.ROLE_FRAME:
                results[0] = parent
            if parent.getRole() == pyatspi.ROLE_TABLE:
                results[1] = parent
            parent = parent.parent

        return results

    def isFunctionalDialog(self, obj):
        """Returns true if the window is functioning as a dialog."""

        # The OOo Navigator window looks like a dialog, acts like a
        # dialog, and loses focus requiring the user to know that it's
        # there and needs Alt+F6ing into.  But officially it's a normal
        # window.

        # There doesn't seem to be (an efficient) top-down equivalent
        # of utilities.hasMatchingHierarchy(). But OOo documents have
        # root panes; this thing does not.
        #
        rolesList = [pyatspi.ROLE_FRAME,
                     pyatspi.ROLE_PANEL,
                     pyatspi.ROLE_PANEL,
                     pyatspi.ROLE_TOOL_BAR,
                     pyatspi.ROLE_PUSH_BUTTON]

        if obj.getRole() != rolesList[0]:
            # We might be looking at the child.
            #
            rolesList.pop(0)

        while obj and obj.childCount and len(rolesList):
            if obj.getRole() != rolesList.pop(0):
                return False
            obj = obj[0]

        return True

    def validParent(self, obj):
        """Returns the first valid parent/ancestor of obj. We need to do
        this in some applications and toolkits due to bogus hierarchies.

        See bugs:
        http://www.openoffice.org/issues/show_bug.cgi?id=78117
        http://bugzilla.gnome.org/show_bug.cgi?id=489490

        Arguments:
        - obj: the Accessible object
        """

        parent = obj.parent
        if parent and parent.getRole() in (pyatspi.ROLE_ROOT_PANE,
                                           pyatspi.ROLE_DIALOG):
            app = obj.getApplication()
            for frame in app:
                if frame.childCount < 1 \
                   or frame[0].getRole() not in (pyatspi.ROLE_ROOT_PANE,
                                                 pyatspi.ROLE_OPTION_PANE):
                    continue

                root_pane = frame[0]
                if obj in root_pane:
                    return root_pane

        return parent

    #########################################################################
    #                                                                       #
    # Utilities for working with the accessible text interface              #
    #                                                                       #
    #########################################################################

    def isWordMisspelled(self, obj, offset):
        """Identifies if the current word is flagged as misspelled by the
        application.

        Arguments:
        - obj: An accessible which implements the accessible text interface.
        - offset: Offset in the accessible's text for which to retrieve the
          attributes.

        Returns True if the word is flagged as misspelled.
        """

        attributes, start, end  = self.textAttributes(obj, offset, True)
        error = attributes.get("text-spelling")

        return error == "misspelled"

    def substring(self, obj, startOffset, endOffset):
        """Returns the substring of the given object's text specialization.

        NOTE: This is here to handle the problematic implementation of
        getText by OpenOffice.  See the bug discussion at:

           http://bugzilla.gnome.org/show_bug.cgi?id=356425)

        Once the OpenOffice issue has been resolved, this method probably
        should be removed.

        Arguments:
        - obj: an accessible supporting the accessible text specialization
        - startOffset: the starting character position
        - endOffset: the ending character position
        """

        text = obj.queryText().getText(0, -1).decode("UTF-8")
        if startOffset >= len(text):
            startOffset = len(text) - 1
        if endOffset == -1:
            endOffset = len(text)
        elif startOffset >= endOffset:
            endOffset = startOffset + 1
        string = text[max(0, startOffset):min(len(text), endOffset)]
        string = string.encode("UTF-8")

        return string

    def textAttributes(self, acc, offset, get_defaults=False):
        """Get the text attributes run for a given offset in a given accessible

        Arguments:
        - acc: An accessible.
        - offset: Offset in the accessible's text for which to retrieve the
        attributes.
        - get_defaults: Get the default attributes as well as the unique ones.
        Default is True

        Returns a dictionary of attributes, a start offset where the attributes
        begin, and an end offset. Returns ({}, 0, 0) if the accessible does not
        supprt the text attribute.
        """
        rv, start, end = script_utilities.Utilities.\
            textAttributes(self, acc, offset, get_defaults)

        # If there are no text attributes associated with the text at a
        # given offset, we might get some seriously bogus offsets, in
        # particular, an extremely large start offset and an extremely
        # large, but negative end offset. As a result, any text attributes
        # which are present on the line after the specified offset will
        # not be indicated by braille.py's getAttributeMask. Therefore,
        # we'll set the start offset to the character being examined,
        # and the end offset to the next character.
        #
        start = min(start, offset)
        if end < 0:
            debug.println(debug.LEVEL_WARNING,
                "soffice.script.py:getTextAttributes: detected a bogus " +
                "end offset. Start offset: %s, end offset: %s" % (start, end))
            end = offset + 1
        else:
            end -= 1

        return rv, start, end

    #########################################################################
    #                                                                       #
    # Miscellaneous Utilities                                               #
    #                                                                       #
    #########################################################################
