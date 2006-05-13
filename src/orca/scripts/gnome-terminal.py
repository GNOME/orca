# Orca
#
# Copyright 2005-2006 Sun Microsystems Inc.
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

"""The gnome-terminal script mainly handles the unique interaction model
of manipulating text - both the user and the system put text into the
system and we try to determine which was which and why."""

import orca.atspi as atspi
import orca.debug as debug
import orca.default as default
import orca.input_event as input_event
import orca.util as util
import orca.orca as orca
import orca.rolenames as rolenames
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

    #def onWindowActivated(self, event):
    #    # Sets the context to the top level window first, so we can
    #    # get information about it the window we just moved to.
    #    #
    #    orca.setLocusOfFocus(event, event.source)
    #
    #    # Now we find the focused object and set the locus of focus to it.
    #    #
    #    obj = util.findFocusedObject(self.app)
    #    if obj:
    #        orca.setLocusOfFocus(event, obj)
    #    else:
    #        default.Script.onWindowActivated(self, event)

    def onTextInserted(self, event):
        """Called whenever text is inserted into an object.

        Arguments:
        - event: the Event
        """

        # We only do special things for terminals.
        #
        if event.source.role != rolenames.ROLE_TERMINAL:
            default.Script.onTextInserted(self, event)
            return
        
        # Ignore text insertions from non-focused objects, unless the
        # currently focused object is the parent of the object from which
        # text was inserted.
        #
        if (event.source != orca.locusOfFocus) \
            and (event.source.parent != orca.locusOfFocus):
            return

        self.updateBraille(event.source)

        text = event.any_data.value()

        # When one does a delete in a terminal, the remainder of the
        # line is "inserted" instead of being shifted left.  We will
        # detect this by seeing if the keystring was a delete action.
        # If we run into this case, we don't really want to speak the
        # rest of the line.
        #
        # We'll let our super class handle "Delete".  We'll handle Ctrl+D.
        #
        keyString = orca.lastInputEvent.event_string
        
        controlPressed = orca.lastInputEvent.modifiers \
                         & (1 << atspi.Accessibility.MODIFIER_CONTROL)

        if (keyString == "Delete"):
            return
        elif (keyString == "D") and controlPressed:
            text = text[0]
        
        # If the last input event was a keyboard event, check to see if
        # the text for this event matches what the user typed. If it does,
        # then don't speak it.
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
        if isinstance(orca.lastInputEvent, input_event.KeyboardEvent):
            wasCommand = orca.lastInputEvent.modifiers \
                         & (1 << atspi.Accessibility.MODIFIER_CONTROL \
                            | 1 << atspi.Accessibility.MODIFIER_ALT \
                            | 1 << atspi.Accessibility.MODIFIER_META \
                            | 1 << atspi.Accessibility.MODIFIER_META2 \
                            | 1 << atspi.Accessibility.MODIFIER_META3)
            wasCommand = wasCommand \
                         or (keyString == "Return") \
                         or (keyString == "Tab")
            if (text == " " and keyString == "space") \
                or (text == keyString):
                pass
            elif wasCommand or (len(text) > 5):
                if text.isupper():
                    speech.speak(text, self.voices[settings.UPPERCASE_VOICE])
                else:
                    speech.speak(text)

        if settings.enableEchoByWord and util.isWordDelimiter(text[-1:]):
            self.echoPreviousWord(event.source)

