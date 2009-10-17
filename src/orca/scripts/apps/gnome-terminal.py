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

"""The gnome-terminal script mainly handles the unique interaction model
of manipulating text - both the user and the system put text into the
system and we try to determine which was which and why."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi

import orca.default as default
import orca.input_event as input_event
import orca.orca as orca
import orca.orca_state as orca_state
import orca.settings as settings
import orca.speech as speech

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

    def echoKey(self, keyEvent):
        """Determine whether this script should echo the current key event.
        If this is a printable key, then return False.

        Note that the keyEcho() method in orca.py will still take into
        account whatever the user's various preferences for key echoing
        are, which may override what is return by this echoKey() method.

        Arguments:
        - keyEvent - the key event

        Returns an indication of whether a key echo event should be
        allowed to happen for this script.
        """

        if orca.isPrintableKey(keyEvent.event_string):
            return False

        return True

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
            if oldLocusOfFocus.getRole() == pyatspi.ROLE_TERMINAL and \
               pageTab.getRole() == pyatspi.ROLE_PAGE_TAB and \
               pageTab.getState().contains(pyatspi.STATE_SENSITIVE):
                self.updateBraille(newLocusOfFocus)
                utterances = self.speechGenerator.generateSpeech(pageTab)
                speech.speak(utterances)

        default.Script.locusOfFocusChanged(self, event, 
                                           oldLocusOfFocus, newLocusOfFocus)

    #def onWindowActivated(self, event):
    #    # Sets the context to the top level window first, so we can
    #    # get information about it the window we just moved to.
    #    #
    #    orca.setLocusOfFocus(event, event.source)
    #
    #    # Now we find the focused object and set the locus of focus to it.
    #    #
    #    obj = self.findFocusedObject(self.app)
    #    if obj:
    #        orca.setLocusOfFocus(event, obj)
    #    else:
    #        default.Script.onWindowActivated(self, event)

    def onTextDeleted(self, event):
        """Called whenever text is deleted from an object.

        Arguments:
        - event: the Event
        """

        if orca_state.lastInputEvent \
               and isinstance(orca_state.lastInputEvent,
                              input_event.KeyboardEvent):
            event_string = orca_state.lastNonModifierKeyEvent.event_string
        else:
            event_string = None

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
        character = event.any_data.decode("UTF-8")[0].encode("UTF-8")
        if character.isupper():
            voice = self.voices[settings.UPPERCASE_VOICE]
        else:
            voice = self.voices[settings.DEFAULT_VOICE]

        if len(character.decode('utf-8')) == 1:
            speech.speakCharacter(character, voice)
        else:
            speech.speak(character, voice, False)

    def onTextInserted(self, event):
        """Called whenever text is inserted into an object.

        Arguments:
        - event: the Event
        """

        # We only do special things for terminals.
        #
        if event.source.getRole() != pyatspi.ROLE_TERMINAL:
            default.Script.onTextInserted(self, event)
            return

        # Ignore text insertions from non-focused objects, unless the
        # currently focused object is the parent of the object from which
        # text was inserted.
        #
        if (event.source != orca_state.locusOfFocus) \
            and (event.source.parent != orca_state.locusOfFocus):
            return

        self.updateBraille(event.source)

        text = event.any_data

        # When one does a delete in a terminal, the remainder of the
        # line is "inserted" instead of being shifted left.  We will
        # detect this by seeing if the keystring was a delete action.
        # If we run into this case, we don't really want to speak the
        # rest of the line.
        #
        # We'll let our super class handle "Delete".  We'll handle Ctrl+D.
        #

        if not orca_state.lastInputEvent:
            return

        matchFound = False
        speakThis = False
        if isinstance(orca_state.lastInputEvent, input_event.KeyboardEvent):
            keyString = orca_state.lastNonModifierKeyEvent.event_string

            controlPressed = orca_state.lastInputEvent.modifiers \
                             & settings.CTRL_MODIFIER_MASK

            if (keyString == "Delete") or (keyString == "BackSpace"):
                return
            elif (keyString == "D") and controlPressed:
                text = text.decode("UTF-8")[0].decode("UTF-8")

            # If the last input event was a keyboard event, check to see if
            # the text for this event matches what the user typed. If it does,
            # then call orca.keyEcho() to echo it (based on the user's key
            # echo preferences).
            #
            # Note that the text widgets sometimes compress their events,
            # thus we might get a longer string from a single text inserted
            # event, while we also get individual keyboard events for the
            # characters used to type the string.  This is ugly.  We attempt
            # to handle it here by only echoing text if we think it was the
            # result of a command (e.g., a paste operation).
            #
            # Note that we have to special case the space character as it
            # comes across as "space" in the keyboard event and " " in the
            # text event.
            #
            # For terminal, Return usually ends up in more text from the
            # system, which we want to hear.  Tab is also often used for
            # command line completion, so we want to hear that, too.
            #
            # Finally, if we missed some command and the system is giving
            # us a string typically longer than what the length of a
            # compressed string is (we choose 5 here), then output that.
            #
            wasCommand = orca_state.lastInputEvent.modifiers \
                         & settings.COMMAND_MODIFIER_MASK
            wasCommand = wasCommand \
                         or (keyString == "Return") \
                         or (keyString == "Tab")
            if (text == " " and keyString == "space") \
                or (text == keyString):
                matchFound = True
            elif wasCommand or (len(text) > 5):
                speakThis = True

        elif isinstance(orca_state.lastInputEvent, \
                        input_event.MouseButtonEvent) and \
             orca_state.lastInputEvent.button == "2":
            speakThis = True

        if matchFound:
            echoed = orca.keyEcho(orca_state.lastInputEvent)
        else:
            echoed = False

        if not echoed:
            # We might need to echo this if it is a single character.
            #
            speakThis = speakThis \
                or ((settings.enableEchoByCharacter \
                     or (settings.enableKeyEcho \
                         and settings.enablePrintableKeys)) \
                    and text \
                    and event.source.getRole() \
                        != pyatspi.ROLE_PASSWORD_TEXT \
                    and len(text.decode("UTF-8")) == 1)

        if speakThis:
            if text.decode("UTF-8").isupper():
                speech.speak(text, self.voices[settings.UPPERCASE_VOICE])
            else:
                speech.speak(text)

        if settings.enableEchoByWord \
           and self.isWordDelimiter(text.decode("UTF-8")[-1:]):
            if matchFound:
                self.echoPreviousWord(event.source)

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
