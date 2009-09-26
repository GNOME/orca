# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
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

"""Custom script for the Device Driver Utility."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi

import orca.default as default
import orca.orca_state as orca_state
import orca.speech as speech

########################################################################
#                                                                      #
# The DDU script class.                                                #
#                                                                      #
########################################################################

class Script(default.Script):

    def __init__(self, app):
        """Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """

        default.Script.__init__(self, app)
        self._progressBarShowing = False
        self._resultsLabel = None

    def _presentResults(self):
        """Presents the results found by the DDU. If we present the results
        also resets self._resultsLabel so that we don't present it twice.

        Returns True if the results were presented; False otherwise.
        """

        if self._resultsLabel:
            text = self.getDisplayedText(self._resultsLabel)
            if text:
                # TODO - JD: Might be a good candidate for a flash
                # braille message.
                #
                speech.speak(text)
                self._resultsLabel = None
                return True

        return False

    def _isBogusCellText(self, cell, string):
        """Attempts to identify text in a cell which the DDU is exposing
        to us, but which is not actually displayed to the user.

        Arguments:
        - cell: The cell we wish to examine.
        - string: The string we're considering for that cell

        Returns True if we think the string should not be presented to
        the user.
        """

        if string.isdigit() and self.getCellIndex(cell) == 2 \
           and cell.parent.getRole() == pyatspi.ROLE_TABLE_CELL:
            try:
                table = cell.parent.parent.queryTable()
            except:
                pass
            else:
                index = self.getCellIndex(cell.parent)
                col = table.getColumnAtIndex(index)
                if col == 0:
                    return True

        return False

    def stopSpeechOnActiveDescendantChanged(self, event):
        """Whether or not speech should be stopped prior to setting the
        locusOfFocus in onActiveDescendantChanged.

        Arguments:
        - event: the Event

        Returns True if speech should be stopped; False otherwise.
        """

        # Intentionally doing an equality check for performance
        # purposes.
        #
        if event.any_data == orca_state.locusOfFocus:
            return False

        return True

    def getRealActiveDescendant(self, obj):
        """Given an object that should be a child of an object that
        manages its descendants, return the child that is the real
        active descendant carrying useful information.

        Arguments:
        - obj: an object that should be a child of an object that
        manages its descendants.
        """

        try:
            return self.generatorCache[self.REAL_ACTIVE_DESCENDANT][obj]
        except:
            if not self.generatorCache.has_key(self.REAL_ACTIVE_DESCENDANT):
                self.generatorCache[self.REAL_ACTIVE_DESCENDANT] = {}
            realActiveDescendant = None

        # If obj is a table cell and all of it's children are table cells
        # (probably cell renderers), then return the first child which has
        # a non zero length text string. If no such object is found, just
        # fall through and use the default approach below. See bug #376791
        # for more details.
        #
        if obj.getRole() == pyatspi.ROLE_TABLE_CELL and obj.childCount:
            nonTableCellFound = False
            for child in obj:
                if child.getRole() != pyatspi.ROLE_TABLE_CELL:
                    nonTableCellFound = True
            if not nonTableCellFound:
                for child in obj:
                    try:
                        text = child.queryText()
                    except NotImplementedError:
                        continue
                    else:
                        # Here is where this method differs from the default
                        # scripts: We break once we find text, and we hack
                        # out the number in the first column.
                        #
                        string = text.getText(0, -1)
                        if string:
                            if not self._isBogusCellText(child, string):
                                realActiveDescendant = child
                            break

        self.generatorCache[self.REAL_ACTIVE_DESCENDANT][obj] = \
            realActiveDescendant or obj
        return self.generatorCache[self.REAL_ACTIVE_DESCENDANT][obj]

    def onStateChanged(self, event):
        """Called whenever an object's state changes.

        Arguments:
        - event: the Event
        """

        if event.type.startswith("object:state-changed:showing") \
           and event.detail1 == 1 and self._progressBarShowing \
           and event.source.getRole() == pyatspi.ROLE_FILLER:
            self._progressBarShowing = False
            labels = self.findByRole(event.source, pyatspi.ROLE_LABEL)
            if len(labels) == 1:
                # Most of the time, the label has its text by the time
                # the progress bar disappears. On occasion, we have to
                # wait for a text inserted event. So we'll store the
                # results label, try to present it now, and be ready
                # to present it later.
                #
                self._resultsLabel = labels[0]
                self._presentResults()
                return

        default.Script.onStateChanged(self, event)

    def onTextInserted(self, event):
        """Called whenever text is inserted into an object.

        Arguments:
        - event: the Event
        """

        if self.isSameObject(event.source, self._resultsLabel):
            if self._presentResults():
                return

        default.Script.onTextInserted(self, event)

    def onValueChanged(self, event):
        """Called whenever an object's value changes.

        Arguments:
        - event: the Event
        """

        # When the progress bar appears, its events are initially emitted
        # by an object of ROLE_SPLIT_PANE. Looking for it is sufficient
        # hierarchy tickling to cause it to emit the expected events.
        #
        if event.source.getRole() == pyatspi.ROLE_SPLIT_PANE:
            if self.findByRole(event.source.parent, pyatspi.ROLE_PROGRESS_BAR):
                self._progressBarShowing = True

        default.Script.onValueChanged(self, event)
