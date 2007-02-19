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

""" Custom script for Thunderbird 3.
"""

__id__        = "$Id: $"
__version__   = "$Revision: $"
__date__      = "$Date: $"
__copyright__ = "Copyright (c) 2005-2007 Sun Microsystems Inc."
__license__   = "LGPL"

import orca.orca as orca
import orca.atspi as atspi
import orca.debug as debug
import orca.default as default
import orca.rolenames as rolenames
import orca.settings as settings
import orca.braille as braille
import orca.braillegenerator as braillegenerator
import orca.speech as speech
import orca.speechgenerator as speechgenerator
import orca.util as util
import orca.Gecko as Gecko

from orca.orca_i18n import _

########################################################################
#                                                                      #
# Custom BrailleGenerator                                              #
#                                                                      #
########################################################################

class BrailleGenerator(braillegenerator.BrailleGenerator):
    """Provides a braille generator specific to Gecko.
    """

    def __init__(self, script):
        self.debugLevel = debug.LEVEL_FINEST

        self._debug("__init__")
        braillegenerator.BrailleGenerator.__init__(self, script)
        

    def _debug(self, msg):
        """ Convenience method for printing debug messages
        """
        debug.println(self.debugLevel, "Thunderbird.BrailleGenerator: "+msg)


    def _getBrailleRegionsForText(self, obj):
        """Get the braille for a text component.

        Arguments:
        - obj: the text component

        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """

        # Gecko._getBrailleRegionsForText does not return the correct
        # braille for Thunderbird. Let the default braillegenerator
        # handle this.
        return braillegenerator.BrailleGenerator._getBrailleRegionsForText(
                self, obj)



########################################################################
#                                                                      #
# Custom SpeechGenerator for Thunderbird                               #
#                                                                      #
########################################################################

class SpeechGenerator(speechgenerator.SpeechGenerator):
    """Provides a speech generator specific to Thunderbird.
    """

    def __init__(self, script):
        # Set the debug level for all the methods in this script.
        #
        self.debugLevel = debug.LEVEL_FINEST

        self._debug("__init__")
        speechgenerator.SpeechGenerator.__init__(self, script)
        

    def _debug(self, msg):
        """ Convenience method for printing debug messages
        """
        debug.println(self.debugLevel, "Thunderbird.SpeechGenerator: "+msg)
        

    def getSpeechContext(self, obj, stopAncestor=None):
        """Get the speech that describes the names and role of
        the container hierarchy of the object, stopping at and
        not including the stopAncestor.

        This code is almost identical to the getSpeechContext
        in Gecko.py. If Gecko.getSpeechContext changes, this
        method may need to be modified too.

        Arguments:
        - obj: the object
        - stopAncestor: the ancestor to stop at and not include (None
          means include all ancestors)

        Returns a list of utterances to be spoken.
        """

        utterances = []

        if not obj:
            return utterances

        if obj is stopAncestor:
            return utterances

        parent = obj.parent
        while parent and (parent.parent != parent):
            if parent == stopAncestor:
                break

            # Skip these containers
            if (parent.role == rolenames.ROLE_FILLER) \
                or (parent.role == rolenames.ROLE_AUTOCOMPLETE) \
                or (parent.role == rolenames.ROLE_PANEL) \
                or (parent.role == rolenames.ROLE_FORM) \
                or (parent.role == rolenames.ROLE_LIST_ITEM) \
                or (parent.role == rolenames.ROLE_LIST) \
                or (parent.role == rolenames.ROLE_PARAGRAPH) \
                or (parent.role == rolenames.ROLE_SECTION) \
                or (parent.role == rolenames.ROLE_LAYERED_PANE) \
                or (parent.role == rolenames.ROLE_SPLIT_PANE) \
                or (parent.role == rolenames.ROLE_SCROLL_PANE) \
                or (parent.role == rolenames.ROLE_UNKNOWN) \
                or (self._script.isLayoutOnly(parent)):
                parent = parent.parent
                continue

            # Append the text and label. Skip displayed text
            # that starts with "chrome://"
            text = util.getDisplayedText(parent)
            label = util.getDisplayedLabel(parent)
            if text and (text != label) and len(text) and \
                   (not text.startswith("chrome://")):
                utterances.append(text)
            if label and len(label):
                utterances.append(label)

            parent = parent.parent

        utterances.reverse()
        self._debug("'%s'" % utterances)

        return utterances
    

########################################################################
#                                                                      #
# The Thunderbird script class.                                        #
#                                                                      #
########################################################################

class Script(Gecko.Script):

    _containingPanelName = ""

    def __init__(self, app):
        """ Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """

        # Set the debug level for all the methods in this script.
        self.debugLevel = debug.LEVEL_FINEST

        Gecko.Script.__init__(self, app)
        

    def getBrailleGenerator(self):
        """Returns the braille generator for this script.
        """
        return BrailleGenerator(self)
    
    
    def getSpeechGenerator(self):
        """Returns the speech generator for this script.
        """
        return SpeechGenerator(self)
    

    def _debug(self, msg):
        """ Convenience method for printing debug messages
        """
        debug.println(self.debugLevel, "Thunderbird.py: "+msg)
        

    def onFocus(self, event):
        """ Called whenever an object gets focus.

        Arguments:
        - event: the Event

        """
        obj = event.source
        parent = obj.parent
        top = util.getTopLevel(obj)
        consume = False

        self._debug("onFocus: name='%s', role='%s'" % (obj.name, obj.role))

        # Let onTextInsertion handle autocompletion.
        if parent and parent.role == rolenames.ROLE_AUTOCOMPLETE:
            return

        # Don't speak chrome URLs.
        if obj.name.startswith(_("chrome://")):
            return

        # This is a better fix for bug #405541. Thunderbird gives
        # focus to the cell in the column that is being sorted
        # (e.g., Date). Braille should show the row from the begining.
        # This fix calls orca.setLocusOfFocus to give focus to the
        # cell at the beginning of the row. It consume the event
        # so Gecko.py doesn't reset the focus.
        if obj.role == rolenames.ROLE_TABLE_CELL:
            table = parent.table
            row = table.getRowAtIndex(obj.index)
            cell = table.getAccessibleAt(row, 0)
            acc = atspi.Accessible.makeAccessible(cell)
            orca.setLocusOfFocus(event, acc)
            consume = True

        # Handle dialogs.
        if top.role == rolenames.ROLE_DIALOG:
            self._speakEnclosingPanel(obj)

        if not consume:
            Gecko.Script.onFocus(self, event)
            

    def onStateChanged(self, event):
        """Called whenever an object's state changes.

        Arguments:
        - event: the Event
        """

        # For now, we'll bypass the Gecko script's desire to
        # let someone know when a page has started/completed
        # loading.
        #
        default.Script.onStateChanged(self, event)


    def onTextInserted(self, event):
        """Called whenever text is inserted into an object.

        Arguments:
        - event: the Event
        """
        obj = event.source
        self._debug("onTextInserted: name='%s', role='%s', parent='%s'" %\
                    (obj.name, obj.role, obj.parent.role))

        parent = obj.parent

        if parent.role == rolenames.ROLE_AUTOCOMPLETE:
            # Thunderbird does not present all the text in an
            # autocompletion text entry. This is a workaround.
            speech.stop()

            utterances = []
            [text, caretOffset, startOffset] = util.getTextLineAtCaret(obj)
            utterances.append(text)
            self._debug("onTextInserted: utterances='%s'" % utterances)

            speech.speakUtterances(utterances)

        else:
            Gecko.Script.onTextInserted(self, event)
            

    def _speakEnclosingPanel(self, obj):
        # Speak the enclosing panel for the object, if it is
        # named. Going two containers up the hierarchy appears
        # to be far enough to find a named panel, if there is one.
        # Don't speak panels whose name begins with "chrome://"

        self._debug("_speakEnclosingPanel")

        parent = obj.parent
        if not parent:
            return

        if parent.name != "" and \
               (not parent.name.startswith(_("chrome://"))) and \
               parent.role == rolenames.ROLE_PANEL:

            # Speak the [arent panel name, but only once.
            if parent.name != self._containingPanelName:
                self._containingPanelName = parent.name
                utterances = []
                text = _("%s panel") % parent.name
                utterances.append(text)
                speech.speakUtterances(utterances)

        else:
            grandparent = parent.parent
            if grandparent and \
                   grandparent.name != "" and \
                   (not grandparent.name.startswith(_("chrome://"))) and \
                   grandparent.role == rolenames.ROLE_PANEL:

                # Speak the grandparent panel name, but only once.
                if grandparent.name != self._containingPanelName:
                    self._containingPanelName = grandparent.name
                    utterances = []
                    text = _("%s panel") % grandparent.name
                    utterances.append(text)
                    speech.speakUtterances(utterances)
