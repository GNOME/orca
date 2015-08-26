# Orca
#
# Copyright 2010-2011 The Orca Team
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

"""Implements generic chat support."""

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2010-2011 The Orca Team"
__license__   = "LGPL"

import pyatspi

from . import cmdnames
from . import guilabels
from . import input_event
from . import keybindings
from . import messages
from . import orca_state
from . import settings
from . import settings_manager
from . import speech

_settingsManager = settings_manager.getManager()

#############################################################################
#                                                                           #
# Ring List. A fixed size circular list by Flavio Catalani                  #
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/435902            #
#                                                                           #
# Included here to keep track of conversation histories.                    #
#                                                                           #
#############################################################################

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

#############################################################################
#                                                                           #
# Conversation                                                              #
#                                                                           #
#############################################################################

class Conversation:

    # The number of messages to keep in the history
    #
    MESSAGE_LIST_LENGTH = 9

    def __init__(self, name, accHistory, inputArea=None):

        """Creates a new instance of the Conversation class.

        Arguments:
        - name: the chatroom/conversation name
        - accHistory: the accessible which holds the conversation history
        - inputArea: the editable text object for this conversation.
        """

        self.name = name
        self.accHistory = accHistory
        self.inputArea = inputArea

        # A cyclic list to hold the chat room history for this conversation
        #
        self._messageHistory = RingList(Conversation.MESSAGE_LIST_LENGTH)

        # Initially populate the cyclic lists with empty strings.
        #
        i = 0
        while i < self._messageHistory.maxsize():
            self.addMessage("")
            i += 1

        # Keep track of the last typing status because some platforms (e.g.
        # MSN) seem to issue the status constantly and even though it has
        # not changed.
        #
        self._typingStatus = ""

    def addMessage(self, message):
        """Adds the current message to the message history.

        Arguments:
        - message: A string containing the message to add
        """

        self._messageHistory.append(message)

    def getNthMessage(self, messageNumber):
        """Returns the specified message from the message history.

        Arguments:
        - messageNumber: the index of the message to get.
        """

        messages = self._messageHistory.get()

        return messages[messageNumber]

    def getTypingStatus(self):
        """Returns the typing status of the buddy in this conversation."""

        return self._typingStatus

    def setTypingStatus(self, status):
        """Sets the typing status of the buddy in this conversation.

        Arguments:
        - status: a string describing the current status.
        """

        self._typingStatus = status

#############################################################################
#                                                                           #
# ConversationList                                                          #
#                                                                           #
#############################################################################

class ConversationList:

    def __init__(self, messageListLength):

        """Creates a new instance of the ConversationList class.

        Arguments:
        - messageListLength: the size of the message history to keep.
        """

        self.conversations = []

        # A cyclic list to hold the most recent (messageListLength) previous
        # messages for all conversations in the ConversationList.
        #
        self._messageHistory = RingList(messageListLength)

        # A corresponding cyclic list to hold the name of the conversation
        # associated with each message in the messageHistory.
        #
        self._roomHistory = RingList(messageListLength)

        # Initially populate the cyclic lists with empty strings.
        #
        i = 0
        while i < self._messageHistory.maxsize():
            self.addMessage("", None)
            i += 1

    def addMessage(self, message, conversation):
        """Adds the current message to the message history.

        Arguments:
        - message: A string containing the message to add
        - conversation: The instance of the Conversation class with which
          the message is associated
        """

        if not conversation:
            name = ""
        else:
            if not self.hasConversation(conversation):
                self.addConversation(conversation)
            name = conversation.name

        self._messageHistory.append(message)
        self._roomHistory.append(name)

    def getNthMessageAndName(self, messageNumber):
        """Returns a list containing the specified message from the message
        history and the name of the chatroom/conversation associated with
        that message.

        Arguments:
        - messageNumber: the index of the message to get.
        """

        messages = self._messageHistory.get()
        rooms = self._roomHistory.get()

        return messages[messageNumber], rooms[messageNumber]

    def hasConversation(self, conversation):
        """Returns True if we know about this conversation.

        Arguments:
        - conversation: the conversation of interest
        """

        return conversation in self.conversations

    def getNConversations(self):
        """Returns the number of conversations we currently know about."""

        return len(self.conversations)

    def addConversation(self, conversation):
        """Adds conversation to the list of conversations.

        Arguments:
        - conversation: the conversation to add
        """

        self.conversations.append(conversation)

    def removeConversation(self, conversation):
        """Removes conversation from the list of conversations.

        Arguments:
        - conversation: the conversation to remove

        Returns True if conversation was successfully removed.
        """

        # TODO - JD: In the Pidgin script, I do not believe we handle the
        # case where a conversation window is closed. I *think* it remains
        # in the overall chat history. What do we want to do in that case?
        # I would assume that we'd want to remove it.... So here's a method
        # to do so. Nothing in the Chat class uses it yet.
        #
        try:
            self.conversations.remove(conversation)
        except:
            return False
        else:
            return True

#############################################################################
#                                                                           #
# Chat                                                                      #
#                                                                           #
#############################################################################

class Chat:
    """This class implements the chat functionality which is available to
    scripts.
    """

    def __init__(self, script, buddyListAncestries):
        """Creates an instance of the Chat class.

        Arguments:
        - script: the script with which this instance is associated.
        - buddyListAncestries: a list of lists of pyatspi roles beginning
          with the the object serving as the actual buddy list (e.g.
          ROLE_TREE_TABLE) and ending with the top level object (e.g.
          ROLE_FRAME).
        """

        self._script = script
        self._buddyListAncestries = buddyListAncestries

        # Keybindings to provide conversation message history. The message
        # review order will be based on the index within the list. Thus F1
        # is associated with the most recent message, F2 the message before
        # that, and so on. A script could override this. Setting messageKeys
        # to ["a", "b", "c" ... ] will cause "a" to be associated with the
        # most recent message, "b" to be associated with the message before
        # that, etc. Scripts can also override the messageKeyModifier.
        #
        self.messageKeys = \
            ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9"]
        self.messageKeyModifier = keybindings.ORCA_MODIFIER_MASK
        self.inputEventHandlers = {}
        self.setupInputEventHandlers()
        self.keyBindings = self.getKeyBindings()

        # The length of the message history will be based on how many keys
        # are bound to the task of providing it.
        #
        self.messageListLength = len(self.messageKeys)
        self._conversationList = ConversationList(self.messageListLength)

        # To make pylint happy.
        #
        self.focusedChannelRadioButton = None
        self.allChannelsRadioButton = None
        self.allMessagesRadioButton = None
        self.buddyTypingCheckButton = None
        self.chatRoomHistoriesCheckButton = None
        self.speakNameCheckButton = None

    def setupInputEventHandlers(self):
        """Defines InputEventHandler fields for chat functions which
        will be used by the script associated with this chat instance."""

        self.inputEventHandlers["togglePrefixHandler"] = \
            input_event.InputEventHandler(
                self.togglePrefix,
                cmdnames.CHAT_TOGGLE_ROOM_NAME_PREFIX)

        self.inputEventHandlers["toggleBuddyTypingHandler"] = \
            input_event.InputEventHandler(
                self.toggleBuddyTyping,
                cmdnames.CHAT_TOGGLE_BUDDY_TYPING)

        self.inputEventHandlers["toggleMessageHistoriesHandler"] = \
            input_event.InputEventHandler(
                self.toggleMessageHistories,
                cmdnames.CHAT_TOGGLE_MESSAGE_HISTORIES)

        self.inputEventHandlers["reviewMessage"] = \
            input_event.InputEventHandler(
                self.readPreviousMessage,
                cmdnames.CHAT_PREVIOUS_MESSAGE)

        return

    def getKeyBindings(self):
        """Defines the chat-related key bindings which will be used by
        the script associated with this chat instance.

        Returns: an instance of keybindings.KeyBindings.
        """

        keyBindings = keybindings.KeyBindings()

        keyBindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self.inputEventHandlers["togglePrefixHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self.inputEventHandlers["toggleBuddyTypingHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self.inputEventHandlers["toggleMessageHistoriesHandler"]))

        for messageKey in self.messageKeys:
            keyBindings.add(
                keybindings.KeyBinding(
                    messageKey,
                    self.messageKeyModifier,
                    keybindings.ORCA_MODIFIER_MASK,
                    self.inputEventHandlers["reviewMessage"]))

        return keyBindings

    def getAppPreferencesGUI(self):
        """Return a GtkGrid containing the application unique configuration
        GUI items for the current application. """

        from gi.repository import Gtk

        grid = Gtk.Grid()
        grid.set_border_width(12)

        label = guilabels.CHAT_SPEAK_ROOM_NAME
        value = _settingsManager.getSetting('chatSpeakRoomName')
        self.speakNameCheckButton = Gtk.CheckButton.new_with_mnemonic(label)
        self.speakNameCheckButton.set_active(value)
        grid.attach(self.speakNameCheckButton, 0, 0, 1, 1)

        label = guilabels.CHAT_ANNOUNCE_BUDDY_TYPING
        value = _settingsManager.getSetting('chatAnnounceBuddyTyping')
        self.buddyTypingCheckButton = Gtk.CheckButton.new_with_mnemonic(label)
        self.buddyTypingCheckButton.set_active(value)
        grid.attach(self.buddyTypingCheckButton, 0, 1, 1, 1)

        label = guilabels.CHAT_SEPARATE_MESSAGE_HISTORIES
        value = _settingsManager.getSetting('chatRoomHistories')
        self.chatRoomHistoriesCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.chatRoomHistoriesCheckButton.set_active(value)
        grid.attach(self.chatRoomHistoriesCheckButton, 0, 2, 1, 1)

        messagesFrame = Gtk.Frame()
        grid.attach(messagesFrame, 0, 3, 1, 1)
        label = Gtk.Label("<b>%s</b>" % guilabels.CHAT_SPEAK_MESSAGES_FROM)
        label.set_use_markup(True)
        messagesFrame.set_label_widget(label)

        messagesAlignment = Gtk.Alignment.new(0.5, 0.5, 1, 1)
        messagesAlignment.set_padding(0, 0, 12, 0)
        messagesFrame.add(messagesAlignment)
        messagesGrid = Gtk.Grid()
        messagesAlignment.add(messagesGrid)

        value = _settingsManager.getSetting('chatMessageVerbosity')

        label = guilabels.CHAT_SPEAK_MESSAGES_ALL
        rb1 = Gtk.RadioButton.new_with_mnemonic(None, label)
        rb1.set_active(value == settings.CHAT_SPEAK_ALL)
        self.allMessagesRadioButton = rb1
        messagesGrid.attach(self.allMessagesRadioButton, 0, 0, 1, 1)

        label = guilabels.CHAT_SPEAK_MESSAGES_ACTIVE
        rb2 = Gtk.RadioButton.new_with_mnemonic(None, label)
        rb2.join_group(rb1)
        rb2.set_active(value == settings.CHAT_SPEAK_FOCUSED_CHANNEL)
        self.focusedChannelRadioButton = rb2
        messagesGrid.attach(self.focusedChannelRadioButton, 0, 1, 1, 1)

        label = guilabels.CHAT_SPEAK_MESSAGES_ALL_IF_FOCUSED % \
            self._script.app.name
        rb3 = Gtk.RadioButton.new_with_mnemonic(None, label)
        rb3.join_group(rb1)
        rb3.set_active(value == settings.CHAT_SPEAK_ALL_IF_FOCUSED)
        self.allChannelsRadioButton = rb3
        messagesGrid.attach(self.allChannelsRadioButton, 0, 2, 1, 1)

        grid.show_all()

        return grid

    def getPreferencesFromGUI(self):
        """Returns a dictionary with the app-specific preferences."""

        if self.allChannelsRadioButton.get_active():
            verbosity = settings.CHAT_SPEAK_ALL_IF_FOCUSED
        elif self.focusedChannelRadioButton.get_active():
            verbosity = settings.CHAT_SPEAK_FOCUSED_CHANNEL
        else:
            verbosity = settings.CHAT_SPEAK_ALL

        return {
            'chatMessageVerbosity': verbosity,
            'chatSpeakRoomName': self.speakNameCheckButton.get_active(),
            'chatAnnounceBuddyTyping': self.buddyTypingCheckButton.get_active(),
            'chatRoomHistories': self.chatRoomHistoriesCheckButton.get_active(),
        }

    ########################################################################
    #                                                                      #
    # InputEvent handlers and supporting utilities                         #
    #                                                                      #
    ########################################################################

    def togglePrefix(self, script, inputEvent):
        """ Toggle whether we prefix chat room messages with the name of
        the chat room.

        Arguments:
        - script: the script associated with this event
        - inputEvent: if not None, the input event that caused this action.
        """

        line = messages.CHAT_ROOM_NAME_PREFIX_ON
        speakRoomName = _settingsManager.getSetting('chatSpeakRoomName')
        _settingsManager.setSetting('chatSpeakRoomName', not speakRoomName)
        if speakRoomName:
            line = messages.CHAT_ROOM_NAME_PREFIX_OFF
        self._script.presentMessage(line)

        return True

    def toggleBuddyTyping(self, script, inputEvent):
        """ Toggle whether we announce when our buddies are typing a message.

        Arguments:
        - script: the script associated with this event
        - inputEvent: if not None, the input event that caused this action.
        """

        line = messages.CHAT_BUDDY_TYPING_ON
        announceTyping = _settingsManager.getSetting('chatAnnounceBuddyTyping')
        _settingsManager.setSetting(
            'chatAnnounceBuddyTyping', not announceTyping)
        if announceTyping:
            line = messages.CHAT_BUDDY_TYPING_OFF
        self._script.presentMessage(line)

        return True

    def toggleMessageHistories(self, script, inputEvent):
        """ Toggle whether we provide chat room specific message histories.

        Arguments:
        - script: the script associated with this event
        - inputEvent: if not None, the input event that caused this action.
        """

        line = messages.CHAT_SEPARATE_HISTORIES_ON
        roomHistories = _settingsManager.getSetting('chatRoomHistories')
        _settingsManager.setSetting('chatRoomHistories', not roomHistories)
        if roomHistories:
            line = messages.CHAT_SEPARATE_HISTORIES_OFF
        self._script.presentMessage(line)

        return True

    def readPreviousMessage(self, script, inputEvent=None, index=0):
        """ Speak/braille a previous chat room message.

        Arguments:
        - script: the script associated with this event
        - inputEvent: if not None, the input event that caused this action.
        - index: The index of the message to read -- by default, the most
          recent message. If we get an inputEvent, however, the value of
          index is ignored and the index of the event_string with respect
          to self.messageKeys is used instead.
        """

        try:
            index = self.messageKeys.index(inputEvent.event_string)
        except:
            pass

        messageNumber = self.messageListLength - (index + 1)
        message, chatRoomName = None, None

        if _settingsManager.getSetting('chatRoomHistories'):
            conversation = self.getConversation(orca_state.locusOfFocus)
            if conversation:
                message = conversation.getNthMessage(messageNumber)
                chatRoomName = conversation.name
        else:
            message, chatRoomName = \
                self._conversationList.getNthMessageAndName(messageNumber)

        if message and chatRoomName:
            self.utterMessage(chatRoomName, message, True)

    def utterMessage(self, chatRoomName, message, focused=True):
        """ Speak/braille a chat room message.

        Arguments:
        - chatRoomName: name of the chat room this message came from
        - message: the chat room message
        - focused: whether or not the current chatroom has focus. Defaults
          to True so that we can use this method to present chat history
          as well as incoming messages.
        """

        # Only speak/braille the new message if it matches how the user
        # wants chat messages spoken.
        #
        verbosity = _settingsManager.getAppSetting(self._script.app, 'chatMessageVerbosity')
        if orca_state.activeScript.name != self._script.name \
           and verbosity == settings.CHAT_SPEAK_ALL_IF_FOCUSED:
            return
        elif not focused and verbosity == settings.CHAT_SPEAK_FOCUSED_CHANNEL:
            return

        text = ""
        if _settingsManager.getSetting('chatSpeakRoomName') and chatRoomName:
            text = message.CHAT_MESSAGE_FROM_ROOM % chatRoomName
        text = self._script.utilities.appendString(text, message)

        if len(text.strip()):
            speech.speak(text)
        self._script.displayBrailleMessage(text)

    def getMessageFromEvent(self, event):
        """Get the actual displayed message. This will almost always be the
        unaltered any_data from an event of type object:text-changed:insert.

        Arguments:
        - event: the Event from which to take the text.

        Returns the string which should be presented as the newly-inserted
        text. (Things like chatroom name prefacing get handled elsewhere.)
        """

        return event.any_data

    def presentInsertedText(self, event):
        """Gives the Chat class an opportunity to present the text from the
        text inserted Event.

        Arguments:
        - event: the text inserted Event

        Returns True if we handled this event here; otherwise False, which
        tells the associated script that is not a chat event that requires
        custom handling.
        """

        if not event \
           or not event.type.startswith("object:text-changed:insert") \
           or not event.any_data:
            return False

        if self.isGenericTextObject(event.source):
            # The script should handle non-chat specific text areas (e.g.,
            # adding a new account).
            #
            return False

        elif self.isInBuddyList(event.source):
            # These are status changes. What the Pidgin script currently
            # does for these is ignore them. It might be nice to add
            # some options to allow the user to customize what status
            # changes are presented. But for now, we'll ignore them
            # across the board.
            #
            return True

        elif self.isTypingStatusChangedEvent(event):
            self.presentTypingStatusChange(event, event.any_data)
            return True

        elif self.isChatRoomMsg(event.source):
            # We always automatically go back to focus tracking mode when
            # someone sends us a message.
            #
            if self._script.flatReviewContext:
                self._script.toggleFlatReviewMode()

            if self.isNewConversation(event.source):
                name = self.getChatRoomName(event.source)
                conversation = Conversation(name, event.source)
            else:
                conversation = self.getConversation(event.source)
                name = conversation.name
            message = self.getMessageFromEvent(event).strip("\n")
            if message:
                self.addMessageToHistory(message, conversation)

            # The user may or may not want us to present this message. Also,
            # don't speak the name if it's the focused chat.
            #
            focused = self.isFocusedChat(event.source)
            if focused:
                name = ""
            if message:
                self.utterMessage(name, message, focused)
            return True

        elif self.isAutoCompletedTextEvent(event):
            text = event.any_data
            if text.isupper():
                speech.speak(text,
                             self._script.voices[settings.UPPERCASE_VOICE])
            else:
                speech.speak(text)
            return True

        return False

    def presentTypingStatusChange(self, event, status):
        """Presents a change in typing status for the current conversation
        if the status has indeed changed and if the user wants to hear it.

        Arguments:
        - event: the accessible Event
        - status: a string containing the status change

        Returns True if we spoke the change; False otherwise
        """

        if _settingsManager.getSetting('chatAnnounceBuddyTyping'):
            conversation = self.getConversation(event.source)
            if conversation and (status != conversation.getTypingStatus()):
                speech.speak(status)
                conversation.setTypingStatus(status)
                return True

        return False

    def addMessageToHistory(self, message, conversation):
        """Adds message to both the individual conversation's history
        as well as to the complete history stored in our conversation
        list.

        Arguments:
        - message: a string containing the message to be added
        - conversation: the instance of the Conversation class to which
          this message belongs
        """

        conversation.addMessage(message)
        self._conversationList.addMessage(message, conversation)

    ########################################################################
    #                                                                      #
    # Convenience methods for identifying, locating different accessibles  #
    #                                                                      #
    ########################################################################

    def isGenericTextObject(self, obj):
        """Returns True if the given accessible seems to be something
        unrelated to the custom handling we're attempting to do here.

        Arguments:
        - obj: the accessible object to examine.
        """

        state = obj.getState()
        if state.contains(pyatspi.STATE_EDITABLE) \
           and state.contains(pyatspi.STATE_SINGLE_LINE):
            return True

        return False

    def isBuddyList(self, obj):
        """Returns True if obj is the list of buddies in the buddy list
        window. Note that this method relies upon a hierarchical check,
        using a list of hierarchies provided by the script. Scripts
        which have more reliable means of identifying the buddy list
        can override this method.

        Arguments:
        - obj: the accessible being examined
        """

        if obj:
            for roleList in self._buddyListAncestries:
                if self._script.utilities.hasMatchingHierarchy(obj, roleList):
                    return True

        return False

    def isInBuddyList(self, obj, includeList=True):
        """Returns True if obj is, or is inside of, the buddy list.

        Arguments:
        - obj: the accessible being examined
        - includeList: whether or not the list itself should be
          considered "in" the buddy list.
        """

        if includeList and self.isBuddyList(obj):
            return True

        for roleList in self._buddyListAncestries:
            buddyListRole = roleList[0]
            candidate = self._script.utilities.ancestorWithRole(
                obj, [buddyListRole], [pyatspi.ROLE_FRAME])
            if self.isBuddyList(candidate):
                return True

        return False

    def isNewConversation(self, obj):
        """Returns True if the given accessible is the chat history
        associated with a new conversation.

        Arguments:
        - obj: the accessible object to examine.
        """

        conversation = self.getConversation(obj)
        return not self._conversationList.hasConversation(conversation)

    def getConversation(self, obj):
        """Attempts to locate the conversation associated with obj.

        Arguments:
        - obj: the accessible of interest

        Returns the conversation if found; None otherwise
        """

        if not obj:
            return None

        name = ""
        # TODO - JD: If we have multiple chats going on and those
        # chats have the same name, and we're in the input area,
        # this approach will fail. What I should probably do instead
        # is, upon creation of a new conversation, figure out where
        # the input area is and save it. For now, I just want to get
        # things working. And people should not be in multiple chat
        # rooms with identical names anyway. :-)
        #
        if obj.getRole() in [pyatspi.ROLE_TEXT, pyatspi.ROLE_ENTRY] \
           and obj.getState().contains(pyatspi.STATE_EDITABLE):
            name = self.getChatRoomName(obj)

        for conversation in self._conversationList.conversations:
            if name:
                if name == conversation.name:
                    return conversation
            # Doing an equality check seems to be preferable here to
            # utilities.isSameObject as a result of false positives.
            #
            elif obj == conversation.accHistory:
                return conversation

        return None

    def isChatRoomMsg(self, obj):
        """Returns True if the given accessible is the text object for
        associated with a chat room conversation.

        Arguments:
        - obj: the accessible object to examine.
        """

        if obj and obj.getRole() == pyatspi.ROLE_TEXT \
           and obj.parent.getRole() == pyatspi.ROLE_SCROLL_PANE:
            state = obj.getState()
            if not state.contains(pyatspi.STATE_EDITABLE) \
               and state.contains(pyatspi.STATE_MULTI_LINE):
                return True

        return False

    def isFocusedChat(self, obj):
        """Returns True if we plan to treat this chat as focused for
        the purpose of deciding whether or not a message should be
        presented to the user.

        Arguments:
        - obj: the accessible object to examine.
        """

        if obj and obj.getState().contains(pyatspi.STATE_SHOWING):
            topLevel = self._script.utilities.topLevelObject(obj)
            if topLevel and topLevel.getState().contains(pyatspi.STATE_ACTIVE):
                return True

        return False

    def getChatRoomName(self, obj):
        """Attempts to find the name of the current chat room.

        Arguments:
        - obj: The accessible of interest

        Returns a string containing what we think is the chat room name.
        """

        # Most of the time, it seems that the name can be found in the
        # page tab which is the ancestor of the chat history. Failing
        # that, we'll look at the frame name. Failing that, scripts
        # should override this method. :-)
        #
        ancestor = self._script.utilities.ancestorWithRole(
            obj,
            [pyatspi.ROLE_PAGE_TAB, pyatspi.ROLE_FRAME],
            [pyatspi.ROLE_APPLICATION])
        name = ""
        try:
            text = self._script.utilities.displayedText(ancestor)
            if text.lower().strip() != self._script.name.lower().strip():
                name = text
        except:
            pass

        # Some applications don't trash their page tab list when there is
        # only one active chat, but instead they remove the text or hide
        # the item. Therefore, we'll give it one more shot.
        #
        if not name:
            ancestor = self._script.utilities.ancestorWithRole(
                ancestor, [pyatspi.ROLE_FRAME], [pyatspi.ROLE_APPLICATION])
            try:
                text = self._script.utilities.displayedText(ancestor)
                if text.lower().strip() != self._script.name.lower().strip():
                    name = text
            except:
                pass     

        return name

    def isAutoCompletedTextEvent(self, event):
        """Returns True if event is associated with text being autocompleted.

        Arguments:
        - event: the accessible event being examined
        """

        lastKey, mods = self._script.utilities.lastKeyAndModifiers()
        if lastKey == "Tab" and event.any_data and event.any_data != "\t":
            return True

        return False

    def isTypingStatusChangedEvent(self, event):
        """Returns True if event is associated with a change in typing status.

        Arguments:
        - event: the accessible event being examined
        """

        # TODO - JD: I still need to figure this one out. Pidgin seems to
        # no longer be presenting this change in the conversation history
        # as it was doing before. And I'm not yet sure what other apps do.
        # In the meantime, scripts can override this.
        #
        return False
