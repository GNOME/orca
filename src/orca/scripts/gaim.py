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

"""Custom script for gaim.  This provides the ability for Orca to
monitor both the IM input and IM output text areas at the same time.

The following script specific key sequences are supported:

  Insert-h      -  Toggle whether we prefix chat room messages with
                   the name of the chat room.
  Insert-[1-9]  -  Speak and braille a previous chat room message.
"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2007 Sun Microsystems Inc."
__license__   = "LGPL"

import gtk

import orca.atspi as atspi
import orca.braille as braille
import orca.debug as debug
import orca.default as default
import orca.input_event as input_event
import orca.keybindings as keybindings
import orca.orca_state as orca_state
import orca.rolenames as rolenames
import orca.settings as settings
import orca.speech as speech

from orca.orca_i18n import _

# Whether we prefix chat room messages with the name of the chat room.
#
prefixChatMessage = False

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

########################################################################
#                                                                      #
# The Gaim script class.                                               #
#                                                                      #
########################################################################

class Script(default.Script):

    def __init__(self, app):
        """Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """

        # Set the debug level for all the methods in this script.
        #
        self.debugLevel = debug.LEVEL_FINEST

        # Create two cyclic lists; one that will contain the previous
        # chat room messages and the other that will contain the names
        # of the associated chat rooms.
        #
        self.MESSAGE_LIST_LENGTH = 9
        self.previousMessages = RingList(self.MESSAGE_LIST_LENGTH)
        self.previousChatRoomNames = RingList(self.MESSAGE_LIST_LENGTH)

        # Initially populate the cyclic lists with empty strings.
        #
        for i in range(0, self.previousMessages.maxsize()):
            self.previousMessages.append("")
        for i in range(0, self.previousChatRoomNames.maxsize()):
            self.previousChatRoomNames.append("")

        # Keep track of the various text areas for chatting.
        # The key is the tab and the value is the text area where
        # the chat occurs.
        #
        self.chatAreas = {}

        default.Script.__init__(self, app)

    def getListeners(self):
        """Add in an AT-SPI event listener ""object:children-changed:"
        events, for this script.
        """

        listeners = default.Script.getListeners(self)
        listeners["object:children-changed:"] = self.onChildrenChanged

        return listeners

    def setupInputEventHandlers(self):
        """Defines InputEventHandler fields for this script that can be
        called by the key and braille bindings. In this particular case,
        we just want to be able to add a handler to toggle whether we
        prefix chat room messages with the name of the chat room.
        """

        debug.println(self.debugLevel, "gaim.setupInputEventHandlers.")

        default.Script.setupInputEventHandlers(self)
        self.inputEventHandlers["togglePrefixHandler"] = \
            input_event.InputEventHandler(
                Script.togglePrefix,
                _("Toggle whether we prefix chat room messages with the name of the chat room."))

        # In gaim/pidgin, we are overriding the default script's bookmark
        # feature and keybindings to provide chat room message history.
        #
        self.inputEventHandlers["goToBookmark"] = \
            input_event.InputEventHandler(
                Script.readPreviousMessage,
                _("Speak and braille a previous chat room message."))

    def getKeyBindings(self):
        """Defines the key bindings for this script. Setup the default
        key bindings, then add one in for toggling whether we prefix
        chat room messages with the name of the chat room.

        Returns an instance of keybindings.KeyBindings.
        """

        debug.println(self.debugLevel, "gaim.getKeyBindings.")

        keyBindings = default.Script.getKeyBindings(self)
        keyBindings.add(
            keybindings.KeyBinding(
                "h",
                1 << settings.MODIFIER_ORCA,
                1 << settings.MODIFIER_ORCA,
                self.inputEventHandlers["togglePrefixHandler"]))

        # In gaim/pidgin, we are overriding the default script's bookmark
        # feature and keybindings to provide chat room message history.
        #
        messageKeys = [ "1", "2", "3", "4", "5", "6", "7", "8", "9" ]
        for messageKey in messageKeys:
            keyBindings.add(
                keybindings.KeyBinding(
                    messageKey,
                    1 << settings.MODIFIER_ORCA,
                    1 << settings.MODIFIER_ORCA,
                    self.inputEventHandlers["goToBookmark"]))

        return keyBindings

    def getAppPreferencesGUI(self):
        """Return a GtkVBox contain the application unique configuration
        GUI items for the current application.
        """

        global prefixChatMessage

        vbox = gtk.VBox(False, 0)
        vbox.set_border_width(12)
        gtk.Widget.show(vbox)
        # Translators: If this checkbox is checked, then Orca will speak
        # the name of the chat room.
        #
        label = _("Speak Chat Room name")
        self.speakNameCheckButton = gtk.CheckButton(label)
        gtk.Widget.show(self.speakNameCheckButton)
        gtk.Box.pack_start(vbox, self.speakNameCheckButton, False, False, 0)
        gtk.ToggleButton.set_active(self.speakNameCheckButton,
                                    prefixChatMessage)

        return vbox

    def setAppPreferences(self, prefs):
        """Write out the application specific preferences lines and set the
        new values.

        Arguments:
        - prefs: file handle for application preferences.
        """

        global prefixChatMessage

        prefixChatMessage = self.speakNameCheckButton.get_active()
        prefs.writelines("\n")
        prefs.writelines("orca.scripts.gaim.prefixChatMessage = %s\n" % \
                         prefixChatMessage)

    def getAppState(self):
        """Returns an object that can be passed to setAppState.  This
        object will be use by setAppState to restore any state information
        that was being maintained by the script."""
        return [default.Script.getAppState(self),
                self.previousMessages,
                self.previousChatRoomNames,
                self.chatAreas]

    def setAppState(self, appState):
        """Sets the application state using the given appState object.

        Arguments:
        - appState: an object obtained from getAppState
        """
        try:
            [defaultAppState,
             self.previousMessages,
             self.previousChatRoomNames,
             self.chatAreas] = appState
            default.Script.setAppState(self, defaultAppState)
        except:
            debug.printException(debug.LEVEL_WARNING)
            pass

    def togglePrefix(self, inputEvent):
        """ Toggle whether we prefix chat room messages with the name of
        the chat room.

        Arguments:
        - inputEvent: if not None, the input event that caused this action.
        """

        global prefixChatMessage

        debug.println(self.debugLevel, "gaim.togglePrefix.")

        line = _("speak chat room name.")
        prefixChatMessage = not prefixChatMessage
        if not prefixChatMessage:
            line = _("Do not speak chat room name.")

        speech.speak(line)

        return True

    def utterMessage(self, chatRoomName, message):
        """ Speak/braille a chat room message.
        messages are kept.

        Arguments:
        - chatRoomName: name of the chat room this message came from.
        - message: the chat room message.
        """

        global prefixChatMessage

        text = ""
        if prefixChatMessage:
            if chatRoomName and chatRoomName != "":
                text += _("Message from chat room %s") % chatRoomName + " "
        if message and message != "":
            text += message

        if text != "":
            braille.displayMessage(text)
            speech.speak(text)

    def readPreviousMessage(self, inputEvent):
        """ Speak/braille a previous chat room message. Up to nine
        previous messages are kept.

        Arguments:
        - inputEvent: if not None, the input event that caused this action.
        """

        debug.println(self.debugLevel, "gaim.readPreviousMessage.")

        i = int(inputEvent.event_string)
        messageNo = self.MESSAGE_LIST_LENGTH-i

        chatRoomNames = self.previousChatRoomNames.get()
        chatRoomName = chatRoomNames[messageNo]

        messages = self.previousMessages.get()
        message = messages[messageNo]

        self.utterMessage(chatRoomName, message)

    def getChatRoomTab(self, obj):
        """Walk up the hierarchy until we've found the page tab for this
        chat room, and return that object.

        Arguments:
        - obj: the accessible component to start from.

        Returns the page tab component for the chat room.
        """

        if obj:
            while True:
                if obj:
                    if obj.role == rolenames.ROLE_APPLICATION:
                        break
                    elif obj.role == rolenames.ROLE_PAGE_TAB:
                        return obj
                    else:
                        obj = obj.parent
                else:
                    break

        return None

    def onChildrenChanged(self, event):
        """Called whenever a child object changes in some way.

        Arguments:
        - event: the text inserted Event
        """

        # Check to see if a new chat room tab has been created and if it
        # has, then announce its name. See bug #469098 for more details.
        #
        if event.type.startswith("object:children-changed:add"):
            rolesList = [rolenames.ROLE_PAGE_TAB_LIST, \
                         rolenames.ROLE_FILLER, \
                         rolenames.ROLE_FRAME]
            if self.isDesiredFocusedItem(event.source, rolesList):
                childCount = event.source.childCount

                # As it's possible to get this component hierarchy in other
                # places than the chat room (i.e. the Preferences dialog),
                # we check to see if the name of the frame is the same as one
                # of its children. If it is, then it's a chat room tab event.
                # For a final check, we only announce the new chat tab if the
                # last child has a name.
                #
                nameFound = False
                frameName = event.source.parent.parent.name
                for i in range(0, childCount):
                    child = event.source.child(i)
                    if frameName and (frameName == child.name):
                        nameFound = True
                if nameFound:
                    child = event.source.child(childCount-1)
                    if child.name:
                        line = _("New chat tab %s") % child.name
                        speech.speak(line)

    def onTextInserted(self, event):
        """Called whenever text is inserted into one of Gaim's text
        objects.  If the object is an instant message or chat, speak
        the text. If we're not watching anything, do the default
        behavior.

        Arguments:
        - event: the text inserted Event
        """

        chatRoomTab = self.getChatRoomTab(event.source)
        if not chatRoomTab:
            default.Script.onTextInserted(self, event)
            return

        # [[[TODO: HACK - it looks as though the GAIM chat area may
        # not start emitting text inserted events until we tickle it
        # by looking at it in the hierarchy.  The simple workaround of
        # entering flat review and exiting does this.  So, we tickle
        # the hierarchy here.  We probably should be trying somewhere
        # else since we may miss the first message in a chat area.  In
        # addition, this is a source of a very small memory leak since
        # we do not free up the entries when the tab goes away.  One
        # would have to engage in hundreds of chats with hundreds of
        # different people from the same instance of gaim for that
        # memory leak to have an issue here.  One thing we could do if
        # that is deemed a severe enough problem is to check for
        # children-changed events and clean up in that.]]]
        #
        chatArea = None
        if not self.chatAreas.has_key(chatRoomTab):
            # Different message types (AIM, IRC ...) have a different
            # component hierarchy for their chat rooms. By testing
            # with AIM and IRC, we've found that the messages area for
            # those two type of chats has an index that is the penultimate
            # text field. Hopefully this is true for other types of chat
            # as well, but is currently untested.
            #
            allTextFields = self.findByRole(chatRoomTab,
                                            rolenames.ROLE_TEXT,
                                            False)
            index = len(allTextFields) - 2
            if index >= 0:
                self.chatAreas[chatRoomTab] = allTextFields[index]
                chatArea = self.chatAreas[chatRoomTab]
        else:
            chatArea = self.chatAreas[chatRoomTab]

        if event.source and (event.source == chatArea):
            # We always automatically go back to focus tracking mode when
            # someone sends us a message.
            #
            if self.flatReviewContext:
                self.toggleFlatReviewMode()

            message = self.getText(event.source,
                                   event.detail1,
                                   event.detail1 + event.detail2)
            if message and message[0] == "\n":
                message = message[1:]

            chatRoomName = self.getDisplayedText(chatRoomTab)

            # If the new message came from the room with focus, we don't
            # want to speak its name even if prefixChatMessage is enabled.
            #
            if event.source.state.count(atspi.Accessibility.STATE_SHOWING):
                chatRoomName = ""
            self.utterMessage(chatRoomName, message)

            # Add the latest message to the list of saved ones. For each
            # one added, the oldest one automatically gets dropped off.
            #
            self.previousMessages.append(message)
            self.previousChatRoomNames.append(chatRoomName)

        elif isinstance(orca_state.lastInputEvent, input_event.KeyboardEvent) \
             and orca_state.lastNonModifierKeyEvent \
             and (orca_state.lastNonModifierKeyEvent.event_string == "Tab") \
             and event.any_data and (event.any_data != "\t"):
            # This is autocompleted text (the name of a user in an IRC
            # chatroom).  The default script isn't announcing it because
            # it's not selected.
            #
            text = event.any_data
            if text.isupper():
                speech.speak(text, self.voices[settings.UPPERCASE_VOICE])
            else:
                speech.speak(text)

        else:
            # Pass the event onto the parent class to be handled in the
            # default way.
            #
            default.Script.onTextInserted(self, event)
