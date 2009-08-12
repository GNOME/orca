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

"""Custom structural navigation for the Gecko toolkit."""

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi

import orca.structural_navigation as structural_navigation
import orca.settings as settings

########################################################################
#                                                                      #
# Custom Structural Navigation                                         #
#                                                                      #
########################################################################

class GeckoStructuralNavigation(structural_navigation.StructuralNavigation):

    def __init__(self, script, enabledTypes, enabled):
        """Gecko specific Structural Navigation."""

        structural_navigation.StructuralNavigation.__init__(self,
                                                            script,
                                                            enabledTypes,
                                                            enabled)

    #####################################################################
    #                                                                   #
    # Methods for finding and moving to objects                         #
    #                                                                   #
    #####################################################################

    def getCurrentObject(self):
        """Returns the current object -- normally, the locusOfFocus. But
        in the case of Gecko, that doesn't always work.
        """

        [obj, offset] = self._script.getCaretContext()
        return obj

    def _findPreviousObject(self, obj, stopAncestor):
        """Finds the object prior to this one, where the tree we're
        dealing with is a DOM and 'prior' means the previous object
        in a linear presentation sense.

        Arguments:
        -obj: the object where to start.
        -stopAncestor: the ancestor at which the search should stop
        """

        return self._script.findPreviousObject(obj, stopAncestor)

    def _findNextObject(self, obj, stopAncestor):
        """Finds the object after to this one, where the tree we're
        dealing with is a DOM and 'next' means the next object
        in a linear presentation sense.

        Arguments:
        -obj: the object where to start.
        -stopAncestor: the ancestor at which the search should stop
        """

        return self._script.findNextObject(obj, stopAncestor)

    def _findLastObject(self, ancestor):
        """Returns the last object in ancestor.

        Arguments:
        - ancestor: the accessible object whose last (child) object
          is sought.
        """

        return self._script.getLastObject(ancestor)

    def _getDocument(self):
        """Returns the document or other object in which the object of
        interest is contained.
        """

        return self._script.getDocumentFrame()

    def _isInDocument(self, obj):
        """Returns True of the object is inside of the document."""

        return self._script.inDocumentContent(obj)

    def _getCaretPosition(self, obj):
        """Returns the [obj, characterOffset] where the caret should be
        positioned.
        """

        obj, offset = self._script.findFirstCaretContext(obj, 0)
        # If it's an anchor, look for the first object of use.
        # See bug #591592.
        #
        if obj.getRole() == pyatspi.ROLE_LINK \
           and not obj.getState().contains(pyatspi.STATE_FOCUSABLE):
            obj, offset = self._script.findNextCaretInOrder(obj, offset)

        return obj, offset

    def _setCaretPosition(self, obj, characterOffset):
        """Sets the caret at the specified offset within obj."""

        self._script.setCaretPosition(obj, characterOffset)

    def _isUselessObject(self, obj):
        """Returns true if the given object is an obj that doesn't
        have any meaning associated with it.
        """

        return self._script.isUselessObject(obj)

    #####################################################################
    #                                                                   #
    # Methods for presenting objects                                    #
    #                                                                   #
    #####################################################################

    def _presentLine(self, obj, offset):
        """Presents the first line of the object to the user."""

        self._script.presentLine(obj, offset)

    def _presentObject(self, obj, offset):
        """Presents the entire object to the user."""

        if obj.getRole() == pyatspi.ROLE_LINK:
            try:
                obj.queryComponent().grabFocus()
            except:
                pass

        self._script.updateBraille(obj)
        contents = self._script.getObjectContentsAtOffset(obj, offset)
        self._script.speakContents(contents)

    #########################################################################
    #                                                                       #
    # Objects                                                               #
    #                                                                       #
    #########################################################################

    ########################
    #                      #
    # Chunks/Large Objects #
    #                      #
    ########################

    def _chunkPredicate(self, obj, arg=None):
        """The predicate to be used for verifying that the object
        obj is a chunk.

        Arguments:
        - obj: the accessible object under consideration.
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        role = obj.getRole()
        if not role in self.OBJECT_ROLES:
            return False
 
        embeddedObjectChar = self._script.EMBEDDED_OBJECT_CHARACTER
        if role in [pyatspi.ROLE_LIST, pyatspi.ROLE_TABLE]:
            # These roles are often serving as containers. We want to see
            # if what they contain is a bunch of text (as opposed to a
            # bunch of links or other embedded objects).  As for lists:
            # We only care about those of the (un)ordered variety. Form
            # field lists are not chunks.
            #
            if not obj.getState().contains(pyatspi.STATE_FOCUSABLE):
                charCount = 0
                for child in obj:
                    try:
                        text = child.queryText()
                    except:
                        text = None
                    if not text:
                        continue

                    string = text.getText(0, -1)
                    if not string.count(embeddedObjectChar):
                        charCount += text.characterCount
                        if charCount > settings.largeObjectTextLength:
                            return True
            return False
        else:
            # We're going to have to take a guess.  It's probably a big
            # chunk of text if it contains at least the number of characters
            # specified by largeObjectTextLength, AND
            # - Guess #1: No more than 5% of the object's total characters
            #   are EOCs, OR
            # - Guess #2: No more than 0.5% of the object's initial n
            #   characters are EOCs, where n is the largeObjectTextLength.
            #
            try:
                text = obj.queryText()
            except:
                return False
            if text \
               and text.characterCount > settings.largeObjectTextLength:
                string = text.getText(0, -1).decode("UTF-8")
                eocs = float(string.count(embeddedObjectChar))
                if eocs/text.characterCount < 0.05:
                    # print "Guess #1", string, eocs/text.characterCount
                    return True
                else:
                    string = string[0:settings.largeObjectTextLength]
                    eocs = float(string.count(embeddedObjectChar))
                    # print "Guess #2", string, eocs/len(string)
                    return eocs/len(string) < 0.005
