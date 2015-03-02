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

"""The gnome-terminal script mainly handles the unique interaction model
of manipulating text - both the user and the system put text into the
system and we try to determine which was which and why."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi

import orca.scripts.toolkits.gtk as gtk
import orca.speech as speech

########################################################################
#                                                                      #
# The GnomeTerminal script class.                                      #
#                                                                      #
########################################################################

class Script(gtk.Script):

    def __init__(self, app):
        """Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """

        gtk.Script.__init__(self, app)

        # By default, don't present if gnome-terminal is not the active 
        # application.
        #
        self.presentIfInactive = False

    def locusOfFocusChanged(self, event, oldLocusOfFocus, newLocusOfFocus):
        """Called when the visual object with focus changes.

        Arguments:
        - event: if not None, the Event that caused the change
        - oldLocusOfFocus: Accessible that is the old locus of focus
        - newLocusOfFocus: Accessible that is the new locus of focus
        """

        # If the new locus of focus has a role of "terminal", then update
        # the braille display accordingly. Also speak the page tab that this
        # terminal is in if it's sensitive (i.e. there are two or more tabs)
        # and if the old locus of focus also had a "terminal role.
        # See bug #518762 for more details.
        #
        if newLocusOfFocus and \
           newLocusOfFocus.getRole() == pyatspi.ROLE_TERMINAL:
            pageTab = event.source.parent.parent.parent
            if oldLocusOfFocus \
               and oldLocusOfFocus.getRole() == pyatspi.ROLE_TERMINAL and \
               pageTab.getRole() == pyatspi.ROLE_PAGE_TAB and \
               pageTab.getState().contains(pyatspi.STATE_SENSITIVE):
                self.updateBraille(newLocusOfFocus)
                utterances = self.speechGenerator.generateSpeech(pageTab)
                speech.speak(utterances)

        gtk.Script.locusOfFocusChanged(self, event,
                                           oldLocusOfFocus, newLocusOfFocus)

    def getTextLineAtCaret(self, obj, offset=None, startOffset=None, endOffset=None):
        """To-be-removed. Returns the string, caretOffset, startOffset."""

        string, caretOffset, lineOffset = \
            super().getTextLineAtCaret(obj, offset, startOffset, endOffset)

        # Sometimes, gnome-terminal will give us very odd values when
        # the user is editing using 'vi' and has positioned the caret
        # at the first character of the first line.  In this case, we
        # end up getting a very large negative number for the line offset.
        # So, we just assume the user is at the first character.
        #
        if lineOffset < 0:
            caretOffset = 0
            lineOffset = 0
            texti = acc.queryText()
            string, startOffset, endOffset = \
                    texti.getTextAtOffset(0,
                                          pyatspi.TEXT_BOUNDARY_LINE_START)

        return string, caretOffset, lineOffset

