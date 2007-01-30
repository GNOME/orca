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


    def _getDefaultBrailleRegions(self, obj):
        """Gets text to be displayed for the current object's name,
        role, and any accelerators.  This is usually the fallback
        braille generator should no other specialized braille
        generator exist for this object.

        Arguments:
        - obj: an Accessible

        Returns a list where the first element is a list of Regions to
        display and the second element is the Region which should get
        focus.
        """

        self._debug("_getDefaultBrailleRegions: name='%s', role='%s'" % \
                    (obj.name, obj.role))
        
        regions = []
        text = ""

        if obj.text:
            # Handle preferences that contain editable text fields. If
            # the object with keyboard focus is editable text field,
            # examine the previous and next sibling to get the order
            # for speaking the preference objects. This is a temporary
            # workaround for Thunderbird not setting the LABEL_FOR relation
            # for some labels.
            #
            # Returns whether to consume the event.
            
            self._debug("_getDefaultBrailleRegions: childCount=%d, index=%d" % \
                        (obj.parent.childCount, obj.index))
            
            if obj.index > 0:
                prev = obj.parent.child(obj.index - 1)
                if prev:
                    self._debug("_getDefaultBrailleRegions: prev='%s', role='%s'" \
                                % (prev.name, prev.role))
                
                if obj.parent.childCount > obj.index:
                    next = obj.parent.child(obj.index + 1)
                    if next:
                        self._debug("_getDefaultBrailleRegions: next='%s', role='%s'" \
                                    % (next.name, next.role))

            # Get the entry text.
            [word, startOffset, endOffset] = obj.text.getTextAtOffset(0,
                atspi.Accessibility.TEXT_BOUNDARY_LINE_START)
            if len(word) == 0:
                # The above may incorrectly return an empty string
                # if the entry contains a single character.
                [word, startOffset, endOffset] = obj.text.getTextAtOffset(0,
                    atspi.Accessibility.TEXT_BOUNDARY_CHAR)

            self._debug("_getDefaultBrailleRegions: word='%s'" % word)
            
            # Determine the order for speaking the component parts.
            if len(word) > 0:
                if prev and prev.role == rolenames.ROLE_LABEL:
                    if next and next.role == rolenames.ROLE_LABEL:
                        text = _("%s text %s %s") % (obj.name, word, next.name)
                    else:
                        text = _("%s text %s") % (obj.name, word)
                else:
                    if next and next.role == rolenames.ROLE_LABEL:
                        text = _("%s text %s %s") % (obj.name, word, next.name)
                    else:
                        text = _("text %s %s") % (word, obj.name)
            
        else: # non-text object
            text = util.appendString(text, util.getDisplayedLabel(obj))
            text = util.appendString(text, util.getDisplayedText(obj))
            text = util.appendString(text, self._getTextForValue(obj))
            text = util.appendString(text, self._getTextForRole(obj))
            
        self._debug("_getDefaultBrailleRegions: text='%s'" % text)

        regions = []
        componentRegion = braille.Component(obj, text)
        regions.append(componentRegion)

        return [regions, componentRegion]


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


    def _getSpeechForAlert(self, obj, already_focused):
        """Gets the title of the dialog and the contents of labels inside the
        dialog that are not associated with any other objects.

        Arguments:
        - obj: the Accessible dialog
        - already_focused: False if object just received focus

        Returns a list of utterances be spoken.
        """

        utterances = []
        label = self._getSpeechForObjectLabel(obj)
        utterances.extend(label)
        name = self._getSpeechForObjectName(obj)
        if name != label:
            utterances.extend(name)

        # Find all the unrelated labels in the dialog and speak them.
        #
        labels = util.findUnrelatedLabels(obj)

        for label in labels:
            if label.name.endswith(_(":")):
                # Filter out unrelated labels that end with a colon.
                # This is a temporary workaround for a Thunderbird
                # bug, where many (all?) unrelated labels ending in a
                # colon, do not have the LABEL_FOR relation set.
                continue
            utterances.append(label.name)

        self._debug("unrelated labels='%s'" % utterances)
        
        return utterances


    def getSpeechContext(self, obj, stopAncestor=None):
        """Get the speech that describes the names and role of
        the container hierarchy of the object, stopping at and
        not including the stopAncestor.

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

            # We try to omit things like fillers off the bat...
            # Also, ignores panels.
            #
            if (parent.role == rolenames.ROLE_FILLER) \
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

            # Well...if we made it this far, we will now append the
            # role, then the text, and then the label.
            #
            if parent.role != rolenames.ROLE_TABLE_CELL:
                self._debug("gettingSpeechForRole: '%s'" % parent.role)
                utterances.append(rolenames.getSpeechForRoleName(parent))

            # Now...autocompletes are wierd.  We'll let the handling of
            # the entry give us the name.
            #
            if parent.role == rolenames.ROLE_AUTOCOMPLETE:
                parent = parent.parent
                continue

            # Finally, put in the text and label (if they exist)
            # Skip displayed text that starts with "chrome://"
            #
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
        #
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
        top = util.getTopLevel(obj)
        consume = False

        self._debug("onFocus: name='%s', role='%s'" \
                    % (obj.name, obj.role))

        # Don't speak a chrome URL.
        if obj.name.startswith(_("chrome://")):
            return

        # Handle dialogs.
        if top.role == rolenames.ROLE_DIALOG:

            self._speakEnclosingPanel(obj)

            if obj.role == rolenames.ROLE_ENTRY:
                consume = self._handleTextEntry(obj)

        if not consume:
            Gecko.Script.onFocus(self, event)
            

    def _speakEnclosingPanel(self, obj):
        # Speak the enclosing panel if it is named. Going two
        # containers up the hierarchy appears to be far enough
        # to find a named panel, if there is one.
        
        self._debug("_speakEnclosingPanel")

        parent = obj.parent
        if not parent:
            return
        
        if parent.name != "" and \
               (not parent.name.startswith(_("chrome://"))) and \
               parent.role == rolenames.ROLE_PANEL:
            
            # Speak the panel name only once.
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
                
                # Speak the panel name only once.
                if grandparent.name != self._containingPanelName:
                    self._containingPanelName = grandparent.name
                    utterances = []
                    text = _("%s panel") % grandparent.name
                    utterances.append(text)
                    speech.speakUtterances(utterances)

                        
    def _handleTextEntry(self, obj):
        # Handle preferences that contain editable text fields. If
        # the object with keyboard focus is editable text field,
        # examine the previous and next sibling to get the order
        # for speaking the preference objects.
        #
        # Returns whether to consume the event.
        
        self._debug("_handleTextEntry: childCount=%d, index=%d, caretOffset=%d, length=%d" % \
                    (obj.parent.childCount, obj.index, obj.text.caretOffset, obj.text.characterCount))

        if obj.index > 0:
            prev = obj.parent.child(obj.index - 1)
            if prev:
                self._debug("_handleTextEntry: prev='%s', role='%s'" \
                            % (prev.name, prev.role))
            
        if obj.index <= obj.parent.childCount - 1:
            next = obj.parent.child(obj.index + 1)
            if next:
                self._debug("_handleTextEntry: next='%s', role='%s'" \
                            % (next.name, next.role))

        # Get the entry text.
        [word, startOffset, endOffset] = obj.text.getTextAtOffset(0,
            atspi.Accessibility.TEXT_BOUNDARY_LINE_START)
        
        if len(word) == 0:
            [word, startOffset, endOffset] = obj.text.getTextAtOffset(obj.text.caretOffset,
                atspi.Accessibility.TEXT_BOUNDARY_LINE_START)

        if len(word) == 0:
            [word, startOffset, endOffset] = obj.text.getTextAtOffset(0,
                atspi.Accessibility.TEXT_BOUNDARY_WORD_START)

        if len(word) == 0:
            # The above may incorrectly return an empty string
            # if the entry contains a single character.
            [word, startOffset, endOffset] = obj.text.getTextAtOffset(0,
                atspi.Accessibility.TEXT_BOUNDARY_CHAR)

        self._debug("_handleTextEntry: word='%s'" % word)

        # Determine the order for speaking the component parts.
        if len(word) > 0:
            if prev and prev.role == rolenames.ROLE_LABEL:
                if next and next.role == rolenames.ROLE_LABEL:
                    text = _("%s text %s %s") % (obj.name, word, next.name)
                else:
                    text = _("%s text %s") % (obj.name, word)
            else:
                if next and next.role == rolenames.ROLE_LABEL:
                    text = _("%s text %s %s") % (obj.name, word, next.name)
                else:
                    text = _("text %s %s") % (word, obj.name)
                    
            speech.speakUtterances([text])
            return True

        return False
