# Orca
#
# Copyright 2005-2007 Sun Microsystems Inc.
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

"""Custom script for gnome-mud."""

__id__        = "$Id:$"
__version__   = "$Revision:$"
__date__      = "$Date:$"
__copyright__ = "Copyright (c) 2005-2007 Sun Microsystems Inc."
__license__   = "LGPL"

import orca.debug as debug
import orca.default as default
import orca.atspi as atspi
import orca.input_event as input_event
import orca.debug as debug
import orca.keybindings as keybindings
import orca.rolenames as rolenames
import orca.braille as braille
import orca.orca_state as orca_state
import orca.speech as speech
import orca.settings as settings

from orca.orca_i18n import _ # for gettext support

########################################################################
#                                                                      #
# Ring List. A fixed size circular list by Flavio Catalani             #
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/435902       #
#                                                                      #
########################################################################

class RingList:
    def __init__(self, length):
        self.__data__ = []
        self.__full__ = 0
        self.__max__ = length
        self.__cur__ = 0

    def append(self, x):
        if self.__full__ == 1:
            for i in range (0, self.__cur__ - 1):
                self.__data__[i] = self.__data__[i + 1]
            self.__data__[self.__cur__ - 1] = x
        else:
            self.__data__.append(x)
            self.__cur__ += 1
            if self.__cur__ == self.__max__:
                self.__full__ = 1

    def get(self):
        return self.__data__

    def remove(self):
        if (self.__cur__ > 0):
            del self.__data__[self.__cur__ - 1]
            self.__cur__ -= 1

    def size(self):
        return self.__cur__

    def maxsize(self):
        return self.__max__

    def __str__(self):
        return ''.join(self.__data__)


class Script(default.Script):

    def __init__(self, app):
        """Creates a new script for the given application.
           This script tries to fix some accessibility problems found in
           the gnome-mud application, and also improves the user experience. 
           For more details see bug #
 

        Arguments:
        - app: the application to create a script for.
        """
        # Set the debug level for all the methods in this script.
        #
        self.debugLevel=debug.LEVEL_FINEST

        self.MESSAGE_LIST_LENGTH=10
        self.previousMessages=RingList(self.MESSAGE_LIST_LENGTH)

        #Initially populate the cyclic list with empty strings
        for i in range(0, self.previousMessages.maxsize()):
           self.previousMessages.append("")

        default.Script.__init__(self, app)


    def setupInputEventHandlers(self):
        debug.println(self.debugLevel, "gnome-mud.setupInputEventHandlers.")

        default.Script.setupInputEventHandlers(self)
        self.inputEventHandlers["readPreviousMessageHandler"] = \
            input_event.InputEventHandler(
                Script.readPreviousMessage,
                _("Read the latest n messages in the incoming messages text \
                    area."))

    def getKeyBindings(self):

        debug.println(self.debugLevel, "gnome-mud.getKeyBindings.")

        keyBindings = default.Script.getKeyBindings(self)

        #Here we define keybindings alt+1 to alt+0. We chosen the alt modifier
        #to don't interfere with the laptop keybindings 7, 8 and 9.
        messageKeys = [ "1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
        for i in range(0, len(messageKeys)):
            keyBindings.add(
                keybindings.KeyBinding(
                    messageKeys[i],
                    1 << atspi.Accessibility.MODIFIER_ALT,
                    1 << atspi.Accessibility.MODIFIER_ALT,
                    self.inputEventHandlers["readPreviousMessageHandler"]))

        return keyBindings

    def readPreviousMessage(self, inputEvent):
        #This function speaks the latest n messages. Alt+1 the latest one, 
        #alt+2 the latest two and so.

        debug.println(self.debugLevel, "gnome-mud.readPreviousMessage.")

        if inputEvent.event_string == "0":
           inputEvent.event_string="10"
        i = int(inputEvent.event_string)
        messageNo = self.MESSAGE_LIST_LENGTH-i
     
        text=""
        messages = self.previousMessages.get()
        for i in range (messageNo, self.MESSAGE_LIST_LENGTH):
            message = messages[i]
            text += message

        speech.speak(text)


    def onTextInserted(self, event):

        rolesList=[rolenames.ROLE_TERMINAL,
                   rolenames.ROLE_FILLER]
        #Whenever a new text is inserted in the incoming message text area,
        #We want to speak and add it to the ringList structure only those lines
        #that contain some text and if the application is the current
        #locusOfFocus. 
        if self.isDesiredFocusedItem(event.source, rolesList):
            if self.flatReviewContext:
                self.toggleFlatReviewMode()
            message=event.any_data
            if message and (not message.isspace()) and message != "\n":
                debug.println(debug.LEVEL_FINEST, \
                    message + " inserted in ringlist:")
                self.previousMessages.append(message)
                if event.source.app == orca_state.locusOfFocus.app:
                    speech.speak(message)

        else:
            default.Script.onTextInserted(self, event)
