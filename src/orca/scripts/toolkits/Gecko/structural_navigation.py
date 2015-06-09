# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
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

        [obj, offset] = self._script.utilities.getCaretContext()
        return obj

    def _findPreviousObject(self, obj, stopAncestor):
        """Finds the object prior to this one, where the tree we're
        dealing with is a DOM and 'prior' means the previous object
        in a linear presentation sense.

        Arguments:
        -obj: the object where to start.
        -stopAncestor: the ancestor at which the search should stop
        """

        return self._script.utilities.getPreviousObjectInDocument(obj, stopAncestor)

    def _findNextObject(self, obj, stopAncestor):
        """Finds the object after to this one, where the tree we're
        dealing with is a DOM and 'next' means the next object
        in a linear presentation sense.

        Arguments:
        -obj: the object where to start.
        -stopAncestor: the ancestor at which the search should stop
        """

        return self._script.utilities.getNextObjectInDocument(obj, stopAncestor)

    def _findLastObject(self, ancestor):
        """Returns the last object in ancestor.

        Arguments:
        - ancestor: the accessible object whose last (child) object
          is sought.
        """

        return self._script.utilities.getLastObjectInDocument(ancestor)

    def _getDocument(self):
        """Returns the document or other object in which the object of
        interest is contained.
        """

        return self._script.utilities.documentFrame()

    def _isInDocument(self, obj):
        """Returns True of the object is inside of the document."""

        return self._script.utilities.inDocumentContent(obj)

    def _setCaretPosition(self, obj, characterOffset):
        """Sets the caret at the specified offset within obj."""

        self._script.utilities.setCaretPosition(obj, characterOffset)

    #####################################################################
    #                                                                   #
    # Methods for presenting objects                                    #
    #                                                                   #
    #####################################################################

    def _presentLine(self, obj, offset):
        """Presents the first line of the object to the user."""

        if self._presentWithSayAll(obj, offset):
            return

        self._script.presentLine(obj, offset)

    def _presentObject(self, obj, offset):
        """Presents the entire object to the user."""

        if not obj:
            return

        if self._presentWithSayAll(obj, offset):
            return

        contents = self._script.utilities.getObjectContentsAtOffset(obj, offset)
        self._script.speakContents(contents)
        self._script.displayContents(contents)
