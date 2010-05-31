# Orca
#
# Copyright 2010 Informal Informatica LTDA.
# Author: Jose Vilmar <vilmar@informal.com.br>
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

"""Custom script for Eclipse."""
__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2010 Informal Informatica LTDA."
__license__   = "LGPL"

import orca.default as default
import pyatspi
from script_utilities import Utilities

########################################################################
#                                                                      #
# The Eclipse script class.                                            #
#                                                                      #
########################################################################
class Script(default.Script):

    def __init__(self, app):
        """Creates a new script for the given application."""
        default.Script.__init__(self, app)
        self._textInserted = False
        self.movementKeys = ["Up", "Down", "Left", "Right", "Page_Up",
                             "Page_Down", "Home", "End"]

    def _presentTextAtNewCaretPosition(self, event, otherObj=None):
        """Updates braille, magnification, and outputs speech for the
        event.source or the otherObj. Overridden here so that we can
        give more feedback to user
        """

        if self.utilities.isDuplicateEvent(event):
            return

        # We will retrieve information from the last object spoken
        try:
            oldObj, oldOffset = self.pointOfReference["lastCursorPosition"]
        except:
            oldObj = None
            oldOffset = -1

        # Let the default script's normal behavior do its thing
        #
        default.Script._presentTextAtNewCaretPosition(self, event, otherObj)

        textInserted = self._textInserted
        self._textInserted = False
        # check if the obj was spoken in the default script
        lastKey, mods = self.utilities.lastKeyAndModifiers()
        if lastKey in self.movementKeys:
            # already spoken in default script
            return

        # check if text was inserted before
        if textInserted:
            # we will ignore this event because text was spoken in
            # onTextInserted
            return

        obj = otherObj or event.source
        offset = obj.queryText().caretOffset

        difChars = offset - oldOffset
        if obj == oldObj and (difChars == 1 or difChars == -1):
            # it seems that the caret moved one position, forward or backward
            # probably the user is typing, we don't want to speak the entire
            # line
            return

        self.sayLine(obj)

    def onFocus(self, event):
        """Called whenever an object gets focus.  Overridden here so that
        we can save the current text cursor position when the event is an
        object:state-changed:focused and source is a pyatspi.ROLE_TEXT
        Perhaps this should be moved to the default.py???

        Arguments:
        - event: the Event
        """

        # Let the default script's normal behavior do its thing
        #
        default.Script.onFocus(self, event)
        #
        if event.type.startswith("object:state-changed:focused") \
                 and event.source.getRole() == pyatspi.ROLE_TEXT:
            # probably it was announced, time to save.
            self._saveLastCursorPosition(event.source, \
                   event.source.queryText().caretOffset)

    def getUtilities(self):
        """Returns the utilites for this script."""

        return Utilities(self)

    def onTextInserted(self, event):
        """Called whenever text is inserted into an object. Overridden here
        so that we can avoid speaking text when caret moves after new text
        is inserted.

        Arguments:
        - event: the Event
        """

        # Let the default script's normal behavior do its thing
        #
        default.Script.onTextInserted(self, event)

        self._textInserted = (event.source.getRole() == pyatspi.ROLE_TEXT)
