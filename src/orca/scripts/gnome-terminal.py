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

        # Ignore text insertions from non-focused objects, unless the
        # currently focused object is the parent of the object from which
        # text was inserted.
        #
        if (event.source != orca.locusOfFocus) \
            and (event.source.parent != orca.locusOfFocus):
            return

        # We'll also ignore sliders because we get their output via
        # their values changing.
        #
        if event.source.role == rolenames.ROLE_SLIDER:
            return

        self.updateBraille(event.source)

        text = event.any_data.value()

        debug.println(debug.eventDebugLevel, "text='%s'" % text)

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
        if isinstance(orca.lastInputEvent, input_event.KeyboardEvent):
            keyString = orca.lastInputEvent.event_string
            wasCommand = orca.lastInputEvent.modifiers \
                         & (atspi.Accessibility.MODIFIER_CONTROL \
                            | atspi.Accessibility.MODIFIER_ALT \
                            | atspi.Accessibility.MODIFIER_META \
                            | atspi.Accessibility.MODIFIER_META2 \
                            | atspi.Accessibility.MODIFIER_META3)
            wasCommand = wasCommand or (keyString == "Return")
            if (text == " " and keyString == "space") \
                or (text == keyString):
                pass
            elif wasCommand:
                if text.isupper():
                    speech.speak(text, self.voices[settings.UPPERCASE_VOICE])
                else:
                    speech.speak(text)

        if settings.enableEchoByWord \
               and ((keyString == "Return") \
                    or util.isWordDelimiter(text[-1:])):
            self.echoPreviousWord(event.source)

