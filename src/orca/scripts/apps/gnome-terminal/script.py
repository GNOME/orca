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

import orca.scripts.default as default
import orca.orca_state as orca_state
import orca.settings as settings
import orca.settings_manager as settings_manager
import orca.speech as speech

_settingsManager = settings_manager.getManager()

########################################################################
#                                                                      #
# The GnomeTerminal script class.                                      #
#                                                                      #
########################################################################

class Script(default.Script):

    def __init__(self, app):
        """Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """

        default.Script.__init__(self, app)

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

        default.Script.locusOfFocusChanged(self, event, 
                                           oldLocusOfFocus, newLocusOfFocus)

    def onTextDeleted(self, event):
        """Called whenever text is deleted from an object.

        Arguments:
        - event: the Event
        """

        event_string, mods = self.utilities.lastKeyAndModifiers()

        # We only do special things when people press backspace
        # in terminals.
        #
        if (event.source.getRole() != pyatspi.ROLE_TERMINAL) \
            or (event_string != "BackSpace"):
            default.Script.onTextDeleted(self, event)
            return

        # Ignore text deletions from non-focused objects, unless the
        # currently focused object is the parent of the object from which
        # text was deleted.
        #
        if (event.source != orca_state.locusOfFocus) \
            and (event.source.parent != orca_state.locusOfFocus):
            return

        self.updateBraille(event.source)

        # Speak the character that has just been deleted.
        #
        character = event.any_data
        if character.decode("UTF-8").isupper():
            voice = self.voices[settings.UPPERCASE_VOICE]
        else:
            voice = self.voices[settings.DEFAULT_VOICE]

        if len(character.decode('utf-8')) == 1:
            speech.speakCharacter(character, voice)
        else:
            speech.speak(character, voice, False)

    def getTextLineAtCaret(self, acc, offset=None):
        """Gets the line of text where the caret is.

        Argument:
        - obj: an Accessible object that implements the AccessibleText
          interface
        - offset: an optional caret offset to use.

        Returns the [string, caretOffset, startOffset] for the line of text
        where the caret is.
        """
        string, caretOffset, lineOffset = \
                default.Script.getTextLineAtCaret(self, acc)

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
        
    def getTextEndOffset(self, textInterface):
        """Returns the offset which should be used as the end offset.
        By default, this is -1. However, this value triggers an assertion
        in certain apps. See bug 598797.

        Argument:
        - textInterface: the accessible text interface for which the end
          offset is desired.

        """

        return textInterface.characterCount
