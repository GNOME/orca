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

from . import cmdnames
from . import debug
from . import focus_manager
from . import input_event_manager
from . import guilabels
from . import input_event
from . import keybindings
from . import messages
from . import script_manager
from . import settings
from . import settings_manager
from .ax_object import AXObject
from .ax_utilities import AXUtilities

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
        except Exception:
            return False
        else:
            return True

#############################################################################
#                                                                           #
# Chat                                                                      #
#                                                                           #
#############################################################################

class Chat:
    """Provides chat functionality available to scripts for chat apps."""

    def __init__(self, script):
        self._script = script

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
        self.input_event_handlers = {}
        self.setup_input_event_handlers()
        self.key_bindings = self.get_key_bindings()

        # The length of the message history will be based on how many keys
        # are bound to the task of providing it.
        #
        self.messageListLength = len(self.messageKeys)
        self._conversationList = ConversationList(self.messageListLength)

        self.focusedChannelRadioButton = None
        self.allChannelsRadioButton = None
        self.allMessagesRadioButton = None
        self.buddyTypingCheckButton = None
        self.chatRoomHistoriesCheckButton = None
        self.speakNameCheckButton = None

    def setup_input_event_handlers(self):
        """Defines the input event handlers for this chat instance."""

        self.input_event_handlers["togglePrefixHandler"] = \
            input_event.InputEventHandler(
                self.togglePrefix,
                cmdnames.CHAT_TOGGLE_ROOM_NAME_PREFIX)

        self.input_event_handlers["toggleBuddyTypingHandler"] = \
            input_event.InputEventHandler(
                self.toggleBuddyTyping,
                cmdnames.CHAT_TOGGLE_BUDDY_TYPING)

        self.input_event_handlers["toggleMessageHistoriesHandler"] = \
            input_event.InputEventHandler(
                self.toggleMessageHistories,
                cmdnames.CHAT_TOGGLE_MESSAGE_HISTORIES)

        self.input_event_handlers["reviewMessage"] = \
            input_event.InputEventHandler(
                self.readPreviousMessage,
                cmdnames.CHAT_PREVIOUS_MESSAGE)

        return

    def get_key_bindings(self):
        """Defines and returns the key bindings for this script."""

        keyBindings = keybindings.KeyBindings()

        keyBindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self.input_event_handlers["togglePrefixHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self.input_event_handlers["toggleBuddyTypingHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self.input_event_handlers["toggleMessageHistoriesHandler"]))

        for messageKey in self.messageKeys:
            keyBindings.add(
                keybindings.KeyBinding(
                    messageKey,
                    self.messageKeyModifier,
                    keybindings.ORCA_MODIFIER_MASK,
                    self.input_event_handlers["reviewMessage"]))

        return keyBindings

    def get_app_preferences_gui(self):
        """Return a GtkGrid containing the application unique configuration
        GUI items for the current application. """

        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk

        grid = Gtk.Grid()
        grid.set_border_width(12)

        label = guilabels.CHAT_SPEAK_ROOM_NAME
        value = settings_manager.get_manager().get_setting('chatSpeakRoomName')
        self.speakNameCheckButton = Gtk.CheckButton.new_with_mnemonic(label)
        self.speakNameCheckButton.set_active(value)
        grid.attach(self.speakNameCheckButton, 0, 0, 1, 1)

        label = guilabels.CHAT_ANNOUNCE_BUDDY_TYPING
        value = settings_manager.get_manager().get_setting('chatAnnounceBuddyTyping')
        self.buddyTypingCheckButton = Gtk.CheckButton.new_with_mnemonic(label)
        self.buddyTypingCheckButton.set_active(value)
        grid.attach(self.buddyTypingCheckButton, 0, 1, 1, 1)

        label = guilabels.CHAT_SEPARATE_MESSAGE_HISTORIES
        value = settings_manager.get_manager().get_setting('chatRoomHistories')
        self.chatRoomHistoriesCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.chatRoomHistoriesCheckButton.set_active(value)
        grid.attach(self.chatRoomHistoriesCheckButton, 0, 2, 1, 1)

        messagesFrame = Gtk.Frame()
        grid.attach(messagesFrame, 0, 3, 1, 1)
        label = Gtk.Label(f"<b>{guilabels.CHAT_SPEAK_MESSAGES_FROM}</b>")
        label.set_use_markup(True)
        messagesFrame.set_label_widget(label)

        messagesAlignment = Gtk.Alignment.new(0.5, 0.5, 1, 1)
        messagesAlignment.set_padding(0, 0, 12, 0)
        messagesFrame.add(messagesAlignment)
        messagesGrid = Gtk.Grid()
        messagesAlignment.add(messagesGrid)

        value = settings_manager.get_manager().get_setting('chatMessageVerbosity')

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
            AXObject.get_name(self._script.app)
        rb3 = Gtk.RadioButton.new_with_mnemonic(None, label)
        rb3.join_group(rb1)
        rb3.set_active(value == settings.CHAT_SPEAK_ALL_IF_FOCUSED)
        self.allChannelsRadioButton = rb3
        messagesGrid.attach(self.allChannelsRadioButton, 0, 2, 1, 1)

        grid.show_all()

        return grid

    def get_preferences_from_gui(self):
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
        speakRoomName = settings_manager.get_manager().get_setting('chatSpeakRoomName')
        settings_manager.get_manager().set_setting('chatSpeakRoomName', not speakRoomName)
        if speakRoomName:
            line = messages.CHAT_ROOM_NAME_PREFIX_OFF
        self._script.present_message(line)

        return True

    def toggleBuddyTyping(self, script, inputEvent):
        """ Toggle whether we announce when our buddies are typing a message.

        Arguments:
        - script: the script associated with this event
        - inputEvent: if not None, the input event that caused this action.
        """

        line = messages.CHAT_BUDDY_TYPING_ON
        announceTyping = settings_manager.get_manager().get_setting('chatAnnounceBuddyTyping')
        settings_manager.get_manager().set_setting(
            'chatAnnounceBuddyTyping', not announceTyping)
        if announceTyping:
            line = messages.CHAT_BUDDY_TYPING_OFF
        self._script.present_message(line)

        return True

    def toggleMessageHistories(self, script, inputEvent):
        """ Toggle whether we provide chat room specific message histories.

        Arguments:
        - script: the script associated with this event
        - inputEvent: if not None, the input event that caused this action.
        """

        line = messages.CHAT_SEPARATE_HISTORIES_ON
        roomHistories = settings_manager.get_manager().get_setting('chatRoomHistories')
        settings_manager.get_manager().set_setting('chatRoomHistories', not roomHistories)
        if roomHistories:
            line = messages.CHAT_SEPARATE_HISTORIES_OFF
        self._script.present_message(line)

        return True

    def readPreviousMessage(self, script, inputEvent=None, index=0):
        """ Speak/braille a previous chat room message.

        Arguments:
        - script: the script associated with this event
        - inputEvent: if not None, the input event that caused this action.
        - index: The index of the message to read -- by default, the most
          recent message. If we get an inputEvent, however, the value of
          index is ignored and the index of the keyval_name with respect
          to self.messageKeys is used instead.
        """

        try:
            index = self.messageKeys.index(inputEvent.keyval_name)
        except Exception:
            pass

        messageNumber = self.messageListLength - (index + 1)
        message, chatRoomName = None, None

        if settings_manager.get_manager().get_setting('chatRoomHistories'):
            conversation = self.getConversation(focus_manager.get_manager().get_locus_of_focus())
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
        verbosity = settings_manager.get_manager().get_app_setting(
            self._script.app, 'chatMessageVerbosity')
        script = script_manager.get_manager().get_active_script()
        if script is not None and script.name != self._script.name \
           and verbosity == settings.CHAT_SPEAK_ALL_IF_FOCUSED:
            return
        elif not focused and verbosity == settings.CHAT_SPEAK_FOCUSED_CHANNEL:
            return

        text = ""
        if chatRoomName and \
           settings_manager.get_manager().get_app_setting(self._script.app, 'chatSpeakRoomName'):
            text = messages.CHAT_MESSAGE_FROM_ROOM % chatRoomName

        if not settings.presentChatRoomLast:
            text = f"{text} {message}"
        else:
            text = f"{message} {text}"

        if len(text.strip()):
            voice = self._script.speech_generator.voice(string=text)
            self._script.speak_message(text, voice=voice)
        self._script.display_message(text)

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

        if self.isInBuddyList(event.source):
            # These are status changes. What the Pidgin script currently
            # does for these is ignore them. It might be nice to add
            # some options to allow the user to customize what status
            # changes are presented. But for now, we'll ignore them
            # across the board.
            #
            return True

        if self.isTypingStatusChangedEvent(event):
            self.presentTypingStatusChange(event, event.any_data)
            return True

        if self.isChatRoomMsg(event.source):
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

        if self.isAutoCompletedTextEvent(event):
            text = event.any_data
            voice = self._script.speech_generator.voice(string=text)
            self._script.speak_message(text, voice=voice)
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

        if settings_manager.get_manager().get_setting('chatAnnounceBuddyTyping'):
            conversation = self.getConversation(event.source)
            if conversation and (status != conversation.getTypingStatus()):
                voice = self._script.speech_generator.voice(string=status)
                self._script.speak_message(status, voice=voice)
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

        return AXUtilities.is_editable(obj) and AXUtilities.is_single_line(obj)

    def _is_scrollable_list(self, obj):
        """Returns True if obj is a list-like scrollable widget."""

        scroll_pane = AXObject.find_ancestor(obj, AXUtilities.is_scroll_pane)
        if not scroll_pane:
            return False

        return AXUtilities.is_tree_or_tree_table(obj) \
            or AXUtilities.is_list_box(obj) or AXUtilities.is_list(obj)

    def isBuddyList(self, obj):
        """Returns True if obj is believed to be the buddy list."""

        # Note: This is a very simple heuristic based on existing chat apps.
        # Subclasses can override this function.

        if not self._is_scrollable_list(obj):
            return False

        if AXObject.find_ancestor(obj, AXUtilities.is_frame) is None:
            return False

        tokens = ["CHAT:", obj, "believed to be buddy list."]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return True

    def isInBuddyList(self, obj, includeList=True):
        """Returns True if obj is, or is inside of, the buddy list."""

        if includeList and self.isBuddyList(obj):
            return True

        buddy_list =  AXObject.find_ancestor(obj, self._is_scrollable_list)
        if buddy_list is None:
            return False

        return self.isBuddyList(buddy_list)

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
        if (AXUtilities.is_text(obj) or AXUtilities.is_entry(obj)) \
           and AXUtilities.is_editable(obj):
            name = self.getChatRoomName(obj)

        for conversation in self._conversationList.conversations:
            if name:
                if name == conversation.name:
                    return conversation
            elif obj == conversation.accHistory:
                return conversation

        return None

    def isChatRoomMsg(self, obj):
        """Returns True if the given accessible is the text object for
        associated with a chat room conversation.

        Arguments:
        - obj: the accessible object to examine.
        """

        if AXUtilities.is_text(obj) and AXUtilities.is_scroll_pane(AXObject.get_parent(obj)):
            return not AXUtilities.is_editable(obj) and AXUtilities.is_multi_line(obj)
        return False

    def isFocusedChat(self, obj):
        """Returns True if we plan to treat this chat as focused for
        the purpose of deciding whether or not a message should be
        presented to the user.

        Arguments:
        - obj: the accessible object to examine.
        """

        if AXUtilities.is_showing(obj):
            active = self._script.utilities.top_level_object_is_active_and_current(obj)
            tokens = ["INFO:", obj, "'s window is focused chat:", active]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return active

        tokens = ["INFO:", obj, "is not focused chat (not showing)"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
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
        def pred(x):
            if not (AXUtilities.is_page_tab(x) or AXUtilities.is_frame(x)):
                return False
            return bool(AXObject.get_name(x))

        ancestor = AXObject.find_ancestor(obj, pred)
        if ancestor:
            return AXObject.get_name(ancestor)
        return ""

    def isAutoCompletedTextEvent(self, event):
        """Returns True if event is associated with text being autocompleted.

        Arguments:
        - event: the accessible event being examined
        """

        if not AXUtilities.is_text(event.source):
            return False

        if input_event_manager.get_manager().last_event_was_tab() \
           and event.any_data and event.any_data != "\t":
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
