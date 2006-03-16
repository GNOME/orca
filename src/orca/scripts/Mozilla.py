# Orca
#
# Copyright 2005 Sun Microsystems Inc.
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

import orca.atspi as atspi
import orca.debug as debug
import orca.default as default
import orca.orca as orca
import orca.rolenames as rolenames
import orca.settings as settings
import orca.speech as speech
import orca.speechgenerator as speechgenerator

from orca.orca_i18n import _

class SpeechGenerator(speechgenerator.SpeechGenerator):
    """Overrides getSpeechContext to handle Mozilla's unique
    hiearchical representation, such as menus duplicating themselves
    in the hierarchy and tables used for layout and indentation purposes.
    """

    def getSpeechContext(self, obj, stopAncestor=None):
        """Get the speech that describes the names and role of
        the container hierarchy of the object, stopping at and
        not including the stopAncestor.

        Arguments:
        - obj: the object
        - stopAncestor: the anscestor to stop at and not include (None
          means include all ancestors)

        Returns a list of utterances to be spoken.
        """

        utterances = []

        if not obj:
            return utterances

        if obj is stopAncestor:
            return utterances

        parent = obj.parent

        # Just skip cells inside cells - it's kind of a nonsensical
        # hierarchy.
        #
        while True:
            if parent \
                and (obj.role == rolenames.ROLE_TABLE_CELL) \
                and (parent.role == rolenames.ROLE_TABLE_CELL):
                parent = parent.parent
            else:
                break
            
        # We'll eliminate toolbars if we're in a menu.  The reason for
        # this is that Mozilla puts its menu bar in a couple of nested
        # toolbars.
        #
        inMenuBar = False
        
        while parent and (parent.parent != parent):
            if parent == stopAncestor:
                break

            if parent.role == rolenames.ROLE_MENU_BAR:
                inMenuBar = True
                
            # We try to omit things like fillers off the bat...
            #
            if (parent.role != rolenames.ROLE_FILLER) \
                and (parent.role != rolenames.ROLE_SPLIT_PANE) \
                and (parent.role != rolenames.ROLE_UNKNOWN):

                # If it has a label, we typically want to speak it, unless
                # we're on a menu, but the menu is not FOCUSABLE (this
                # is the way to identify the menu that's duplicated in the
                # hierarchy)
                #
                if len(parent.label) > 0:
                    if (parent.role == rolenames.ROLE_MENU) \
                       and not parent.state.count(\
                                   atspi.Accessibility.STATE_FOCUSABLE):
                        pass
                    else:
                        utterances.append(parent.label + " " \
                                      + rolenames.getSpeechForRoleName(parent))
                # Otherwise, we won't speak it if it is a panel with
                # no name,
                elif parent.role == rolenames.ROLE_PANEL:
                    pass
                # Or if we're in a menu and this is a toolbar,
                #
                elif inMenuBar and (parent.role == rolenames.ROLE_TOOL_BAR):
                    pass
                else:
                    utterances.append(rolenames.getSpeechForRoleName(parent))

            parent = parent.parent

        utterances.reverse()

        return utterances

class Script(default.Script):
    """The script for Firefox.

    NOTE: THIS IS UNDER DEVELOPMENT AND DOES NOT PROVIDE ANY COMPELLING
    ACCESS TO FIREFOX AT THIS POINT.
    """
    
    def __init__(self, app):
        #print "Mozilla.__init__"
        default.Script.__init__(self, app)
        
    def getSpeechGenerator(self):
        """Returns the speech generator for this script.
        """
        return SpeechGenerator()

    def onCaretMoved(self, event):
        #print "Mozilla.onCaretMoved"
        #print "  source        =", event.source
        #print "  source.parent =", event.source.parent
        #print "  lof           =", orca.locusOfFocus
        
        # We always automatically go back to focus tracking mode when
        # the caret moves in the focused object.
        #
        if self.flatReviewContext:
            self.toggleFlatReviewMode()

        [string, startOffset, endOffset] = event.source.text.getTextAtOffset(
            event.source.text.caretOffset,
            atspi.Accessibility.TEXT_BOUNDARY_LINE_START)
        #print "  text line at offset", string
        
        self._presentTextAtNewCaretPosition(event)
        
    def onNameChanged(self, event):
        """Called whenever a property on an object changes.

        Arguments:
        - event: the Event
        """

        # We ignore these because Mozilla just happily keeps generating
        # name changed events for objects whose name doesn't change.
        #
        return
    
    # This function is called whenever an object within Mozilla receives
    # focus
    #
    def onFocus(self, event):
        #print "Mozilla.onFocus:", event.type, event.source.toString()

        # We're going to ignore focus events on the frame.  They
        # are often intermingled with menu activity, wreaking havoc
        # on the context.
        #
        if event.source.role == rolenames.ROLE_FRAME:
            return

        # We're also going to ignore menus that are children of menu
        # bars.  They never really get focus themselves - it's always
        # a transient event and one of the menu items or submenus will
        # get focus immediately after the menu gets focus.  So...we
        # compress the events.
        #
        if (event.source.role == rolenames.ROLE_MENU) \
           and event.source.parent \
           and (event.source.parent.role == rolenames.ROLE_MENU_BAR):
            return
        
        default.Script.onFocus(self, event)

    # This function is called when a hyperlink is selected - This happens
    # when a link is navigated to using tab/shift-tab
    #
    def onLinkSelected(self, event):
        text = event.source.text
        hypertext = event.source.hypertext
        linkIndex = default.getLinkIndex(event.source, text.caretOffset)
        
        if linkIndex >= 0:
            link = hypertext.getLink(linkIndex)
            linkText = text.getText(link.startIndex, link.endIndex)
            [string, startOffset, endOffset] = text.getTextAtOffset(
                text.caretOffset,
                atspi.Accessibility.TEXT_BOUNDARY_LINE_START)
            #print "onLinkSelected", event.source.role, string,
            #print "  caretOffset:     ", text.caretOffset
            #print "  line startOffset:", startOffset
            #print "  line endOffset:  ", startOffset
            #print "  caret in line:   ", text.caretOffset - startOffset
            speech.speak(linkText, self.voices[settings.HYPERLINK_VOICE])
        else:
            speech.speak(_("link"), self.voices[settings.HYPERLINK_VOICE])
            
        self.updateBraille(event.source)

    def locusOfFocusChanged(self, event, oldLocusOfFocus, newLocusOfFocus):
        """Called when the visual object with focus changes.

        Arguments:
        - event: if not None, the Event that caused the change
        - oldLocusOfFocus: Accessible that is the old locus of focus
        - newLocusOfFocus: Accessible that is the new locus of focus
        """
        # Don't bother speaking all the information about the HTML
        # container - it's duplicated all over the place.  So, we
        # just speak the role.
        #
        if newLocusOfFocus \
           and newLocusOfFocus.role == rolenames.ROLE_HTML_CONTAINER:
            # We always automatically go back to focus tracking mode when
            # the focus changes.
            #
            if self.flatReviewContext:
                self.toggleFlatReviewMode()
            self.updateBraille(newLocusOfFocus)
            speech.speak(rolenames.getSpeechForRoleName(newLocusOfFocus))
        else:
            default.Script.locusOfFocusChanged(self,
                                               event,
                                               oldLocusOfFocus,
                                               newLocusOfFocus)
