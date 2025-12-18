# Unit tests for chat_presenter.py methods.
#
# Copyright 2025 Igalia, S.L.
# Author: Joanmarie Diggs <jdiggs@igalia.com>
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

# pylint: disable=wrong-import-position
# pylint: disable=import-outside-toplevel
# pylint: disable=protected-access

"""Unit tests for chat_presenter.py methods."""

from __future__ import annotations

from typing import TYPE_CHECKING

import gi
import pytest

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

if TYPE_CHECKING:
    from unittest.mock import Mock

    from .orca_test_context import OrcaTestContext


@pytest.mark.unit
class TestConversation:
    """Test Conversation class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, Mock]:
        """Returns dependencies for chat module testing."""

        essential_modules = test_context.setup_shared_dependencies([
            "orca.ax_utilities",
            "orca.ax_text",
            "orca.input_event_manager",
        ])

        debug_mock = essential_modules["orca.debug"]
        debug_mock.print_message = test_context.Mock()
        debug_mock.print_tokens = test_context.Mock()

        return essential_modules

    def test_init(self, test_context: OrcaTestContext) -> None:
        """Test Conversation.__init__."""

        self._setup_dependencies(test_context)
        from orca.chat_presenter import Conversation

        mock_log = test_context.Mock(spec=Atspi.Accessible)
        conversation = Conversation("TestRoom", mock_log)

        assert conversation.get_name() == "TestRoom"
        assert conversation._log == mock_log
        assert not conversation.has_messages()
        assert conversation.get_message_count() == 0

    def test_get_name(self, test_context: OrcaTestContext) -> None:
        """Test Conversation.get_name returns the conversation name."""

        self._setup_dependencies(test_context)
        from orca.chat_presenter import Conversation

        mock_log = test_context.Mock(spec=Atspi.Accessible)
        conversation = Conversation("MyChannel", mock_log)

        assert conversation.get_name() == "MyChannel"

    def test_is_log(self, test_context: OrcaTestContext) -> None:
        """Test Conversation.is_log identifies the log object."""

        self._setup_dependencies(test_context)
        from orca.chat_presenter import Conversation

        mock_log = test_context.Mock(spec=Atspi.Accessible)
        other_obj = test_context.Mock(spec=Atspi.Accessible)
        conversation = Conversation("TestRoom", mock_log)

        assert conversation.is_log(mock_log) is True
        assert conversation.is_log(other_obj) is False

    def test_add_and_get_message(self, test_context: OrcaTestContext) -> None:
        """Test Conversation.add_message and get_message."""

        self._setup_dependencies(test_context)
        from orca.chat_presenter import Conversation

        mock_log = test_context.Mock(spec=Atspi.Accessible)
        conversation = Conversation("TestRoom", mock_log)

        conversation.add_message("Hello")
        conversation.add_message("World")

        assert conversation.get_message(-1) == "World"
        assert conversation.get_message(-2) == "Hello"

    def test_has_messages_and_count(self, test_context: OrcaTestContext) -> None:
        """Test Conversation.has_messages and get_message_count."""

        self._setup_dependencies(test_context)
        from orca.chat_presenter import Conversation

        mock_log = test_context.Mock(spec=Atspi.Accessible)
        conversation = Conversation("TestRoom", mock_log)

        assert not conversation.has_messages()
        assert conversation.get_message_count() == 0

        conversation.add_message("Message 1")
        assert conversation.has_messages()
        assert conversation.get_message_count() == 1

        conversation.add_message("Message 2")
        assert conversation.get_message_count() == 2

    def test_message_history_limit(self, test_context: OrcaTestContext) -> None:
        """Test that Conversation respects HISTORY_SIZE limit."""

        self._setup_dependencies(test_context)
        from orca.chat_presenter import Conversation

        mock_log = test_context.Mock(spec=Atspi.Accessible)
        conversation = Conversation("TestRoom", mock_log)

        # Add more messages than HISTORY_SIZE
        for i in range(Conversation.HISTORY_SIZE + 3):
            conversation.add_message(f"Message {i}")

        assert conversation.get_message_count() == Conversation.HISTORY_SIZE
        # Oldest messages should have been dropped
        assert conversation.get_message(-1) == f"Message {Conversation.HISTORY_SIZE + 2}"

    def test_typing_status(self, test_context: OrcaTestContext) -> None:
        """Test Conversation typing status methods."""

        self._setup_dependencies(test_context)
        from orca.chat_presenter import Conversation

        mock_log = test_context.Mock(spec=Atspi.Accessible)
        conversation = Conversation("TestRoom", mock_log)

        assert conversation.get_typing_status() == ""

        conversation.set_typing_status("User is typing...")
        assert conversation.get_typing_status() == "User is typing..."

    def test_get_message_invalid_index(self, test_context: OrcaTestContext) -> None:
        """Test Conversation.get_message raises IndexError for invalid index."""

        self._setup_dependencies(test_context)
        from orca.chat_presenter import Conversation

        mock_log = test_context.Mock(spec=Atspi.Accessible)
        conversation = Conversation("TestRoom", mock_log)

        # Empty conversation should raise IndexError
        with pytest.raises(IndexError):
            conversation.get_message(-1)

        # Add one message
        conversation.add_message("Hello")

        # Valid indices work
        assert conversation.get_message(-1) == "Hello"

        # Out of bounds still raises
        with pytest.raises(IndexError):
            conversation.get_message(-2)


@pytest.mark.unit
class TestConversationList:
    """Test ConversationList class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, Mock]:
        """Returns dependencies for chat module testing."""

        essential_modules = test_context.setup_shared_dependencies([
            "orca.ax_utilities",
            "orca.ax_text",
            "orca.input_event_manager",
        ])

        return essential_modules

    def test_init(self, test_context: OrcaTestContext) -> None:
        """Test ConversationList.__init__."""

        self._setup_dependencies(test_context)
        from orca.chat_presenter import ConversationList

        conv_list = ConversationList()

        assert not conv_list.has_messages()
        assert conv_list.get_message_count() == 0

    def test_add_message_without_conversation(self, test_context: OrcaTestContext) -> None:
        """Test ConversationList.add_message with no conversation."""

        self._setup_dependencies(test_context)
        from orca.chat_presenter import ConversationList

        conv_list = ConversationList()
        conv_list.add_message("Hello", None)

        assert conv_list.has_messages()
        assert conv_list.get_message_count() == 1

        message, name = conv_list.get_message_and_name(-1)
        assert message == "Hello"
        assert name == ""

    def test_add_message_with_conversation(self, test_context: OrcaTestContext) -> None:
        """Test ConversationList.add_message with a conversation."""

        self._setup_dependencies(test_context)
        from orca.chat_presenter import ConversationList, Conversation

        mock_log = test_context.Mock(spec=Atspi.Accessible)
        conversation = Conversation("TestRoom", mock_log)

        conv_list = ConversationList()
        conv_list.add_message("Hello from room", conversation)

        message, name = conv_list.get_message_and_name(-1)
        assert message == "Hello from room"
        assert name == "TestRoom"

    def test_iteration(self, test_context: OrcaTestContext) -> None:
        """Test ConversationList iteration."""

        self._setup_dependencies(test_context)
        from orca.chat_presenter import ConversationList, Conversation

        mock_log1 = test_context.Mock(spec=Atspi.Accessible)
        mock_log2 = test_context.Mock(spec=Atspi.Accessible)
        conv1 = Conversation("Room1", mock_log1)
        conv2 = Conversation("Room2", mock_log2)

        conv_list = ConversationList()
        conv_list.add_message("Msg1", conv1)
        conv_list.add_message("Msg2", conv2)

        conversations = list(conv_list)
        assert len(conversations) == 2
        assert conv1 in conversations
        assert conv2 in conversations

    def test_iteration_empty(self, test_context: OrcaTestContext) -> None:
        """Test ConversationList iteration when empty."""

        self._setup_dependencies(test_context)
        from orca.chat_presenter import ConversationList

        conv_list = ConversationList()
        conversations = list(conv_list)
        assert len(conversations) == 0

    def test_message_history_limit(self, test_context: OrcaTestContext) -> None:
        """Test that ConversationList respects HISTORY_SIZE limit."""

        self._setup_dependencies(test_context)
        from orca.chat_presenter import ConversationList, Conversation

        conv_list = ConversationList()

        # Add more messages than HISTORY_SIZE
        for i in range(Conversation.HISTORY_SIZE + 3):
            conv_list.add_message(f"Message {i}", None)

        assert conv_list.get_message_count() == Conversation.HISTORY_SIZE

    def test_get_message_and_name_invalid_index(self, test_context: OrcaTestContext) -> None:
        """Test ConversationList.get_message_and_name raises IndexError for invalid index."""

        self._setup_dependencies(test_context)
        from orca.chat_presenter import ConversationList

        conv_list = ConversationList()

        # Empty list should raise IndexError
        with pytest.raises(IndexError):
            conv_list.get_message_and_name(-1)

        # Add one message
        conv_list.add_message("Hello", None)

        # Valid index works
        message, name = conv_list.get_message_and_name(-1)
        assert message == "Hello"

        # Out of bounds still raises
        with pytest.raises(IndexError):
            conv_list.get_message_and_name(-2)


@pytest.mark.unit
class TestChat:
    """Test Chat class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, Mock]:
        """Returns dependencies for Chat class testing."""

        essential_modules = test_context.setup_shared_dependencies([
            "orca.ax_utilities",
            "orca.ax_text",
            "orca.input_event_manager",
        ])

        debug_mock = essential_modules["orca.debug"]
        debug_mock.print_message = test_context.Mock()
        debug_mock.print_tokens = test_context.Mock()

        cmdnames_mock = essential_modules["orca.cmdnames"]
        cmdnames_mock.CHAT_TOGGLE_ROOM_NAME_PREFIX = "Toggle room name prefix"
        cmdnames_mock.CHAT_TOGGLE_BUDDY_TYPING = "Toggle buddy typing"
        cmdnames_mock.CHAT_TOGGLE_MESSAGE_HISTORIES = "Toggle message histories"
        cmdnames_mock.CHAT_PREVIOUS_MESSAGE = "Previous message"
        cmdnames_mock.CHAT_NEXT_MESSAGE = "Next message"

        messages_mock = essential_modules["orca.messages"]
        messages_mock.CHAT_NO_MESSAGES = "No chat messages"
        messages_mock.CHAT_LIST_TOP = "Top"
        messages_mock.CHAT_LIST_BOTTOM = "Bottom"
        messages_mock.CHAT_ROOM_NAME_PREFIX_ON = "Room name prefix on"
        messages_mock.CHAT_ROOM_NAME_PREFIX_OFF = "Room name prefix off"
        messages_mock.CHAT_BUDDY_TYPING_ON = "Buddy typing on"
        messages_mock.CHAT_BUDDY_TYPING_OFF = "Buddy typing off"
        messages_mock.CHAT_SEPARATE_HISTORIES_ON = "Separate histories on"
        messages_mock.CHAT_SEPARATE_HISTORIES_OFF = "Separate histories off"

        input_event_mock = essential_modules["orca.input_event"]
        input_event_handler_mock = test_context.Mock()
        input_event_mock.InputEventHandler = test_context.Mock(
            return_value=input_event_handler_mock
        )

        keybindings_mock = essential_modules["orca.keybindings"]
        keybindings_mock.NO_MODIFIER_MASK = 0
        keybindings_mock.ORCA_MODIFIER_MASK = 4

        settings_manager_mock = essential_modules["orca.settings_manager"]
        manager_instance = test_context.Mock()
        manager_instance.set_setting = test_context.Mock()
        manager_instance.override_key_bindings = test_context.Mock(
            side_effect=lambda h, b, d: b
        )
        settings_manager_mock.get_manager = test_context.Mock(
            return_value=manager_instance
        )

        # Set chat-related settings
        settings_mock = essential_modules["orca.settings"]
        settings_mock.chatSpeakRoomName = False
        settings_mock.chatAnnounceBuddyTyping = False
        settings_mock.chatRoomHistories = False

        return essential_modules

    def test_init(self, test_context: OrcaTestContext) -> None:
        """Test Chat.__init__."""

        self._setup_dependencies(test_context)
        from orca.chat_presenter import Chat

        mock_script = test_context.Mock()
        chat = Chat(mock_script)

        assert chat._script == mock_script

    def test_get_conversation_for_object_name_mismatch(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test get_conversation_for_object when name doesn't match log's room."""

        self._setup_dependencies(test_context)
        from orca.chat_presenter import Chat, Conversation

        mock_script = test_context.Mock()
        chat = Chat(mock_script)

        mock_log1 = test_context.Mock(spec=Atspi.Accessible)
        conversation1 = Conversation("Room1", mock_log1)
        chat._conversation_list.add_message("Hello", conversation1)

        chat.get_chat_room_name = test_context.Mock(return_value="Room2")

        result = chat.get_conversation_for_object(mock_log1)

        assert result is None


@pytest.mark.unit
class TestChatPresenter:
    """Test ChatPresenter class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, Mock]:
        """Returns dependencies for ChatPresenter class testing."""

        essential_modules = test_context.setup_shared_dependencies([
            "orca.ax_utilities",
            "orca.ax_text",
            "orca.input_event_manager",
        ])

        debug_mock = essential_modules["orca.debug"]
        debug_mock.print_message = test_context.Mock()
        debug_mock.print_tokens = test_context.Mock()

        cmdnames_mock = essential_modules["orca.cmdnames"]
        cmdnames_mock.CHAT_TOGGLE_ROOM_NAME_PREFIX = "Toggle room name prefix"
        cmdnames_mock.CHAT_TOGGLE_BUDDY_TYPING = "Toggle buddy typing"
        cmdnames_mock.CHAT_TOGGLE_MESSAGE_HISTORIES = "Toggle message histories"
        cmdnames_mock.CHAT_PREVIOUS_MESSAGE = "Previous message"
        cmdnames_mock.CHAT_NEXT_MESSAGE = "Next message"

        messages_mock = essential_modules["orca.messages"]
        messages_mock.CHAT_ROOM_NAME_PREFIX_ON = "Room name prefix on"
        messages_mock.CHAT_ROOM_NAME_PREFIX_OFF = "Room name prefix off"
        messages_mock.CHAT_BUDDY_TYPING_ON = "Buddy typing on"
        messages_mock.CHAT_BUDDY_TYPING_OFF = "Buddy typing off"
        messages_mock.CHAT_SEPARATE_HISTORIES_ON = "Separate histories on"
        messages_mock.CHAT_SEPARATE_HISTORIES_OFF = "Separate histories off"
        messages_mock.CHAT_NO_MESSAGES = "No messages"
        messages_mock.CHAT_LIST_TOP = "Top of chat"
        messages_mock.CHAT_LIST_BOTTOM = "Bottom of chat"
        messages_mock.CHAT_MESSAGE_FROM_ROOM = "Message from %s"

        input_event_mock = essential_modules["orca.input_event"]
        input_event_handler_mock = test_context.Mock()
        input_event_mock.InputEventHandler = test_context.Mock(
            return_value=input_event_handler_mock
        )

        keybindings_mock = essential_modules["orca.keybindings"]
        keybindings_mock.NO_MODIFIER_MASK = 0
        keybindings_mock.ORCA_MODIFIER_MASK = 4
        keybindings_mock.DEFAULT_MODIFIER_MASK = 8

        settings_manager_mock = essential_modules["orca.settings_manager"]
        manager_instance = test_context.Mock()
        manager_instance.set_setting = test_context.Mock()
        manager_instance.override_key_bindings = test_context.Mock(
            side_effect=lambda h, b, d: b
        )
        settings_manager_mock.get_manager = test_context.Mock(
            return_value=manager_instance
        )

        settings_mock = essential_modules["orca.settings"]
        settings_mock.chatSpeakRoomName = False
        settings_mock.chatAnnounceBuddyTyping = False
        settings_mock.chatRoomHistories = False
        settings_mock.chatMessageVerbosity = 0
        settings_mock.presentChatRoomLast = False

        return essential_modules

    def test_get_handlers(self, test_context: OrcaTestContext) -> None:
        """Test ChatPresenter.get_handlers returns handlers dict."""

        self._setup_dependencies(test_context)
        from orca.chat_presenter import get_presenter

        presenter = get_presenter()
        handlers = presenter.get_handlers()

        assert "chat_previous_message" in handlers
        assert "chat_next_message" in handlers
        assert "chat_toggle_room_name_prefix" in handlers
        assert "chat_toggle_buddy_typing" in handlers
        assert "chat_toggle_message_histories" in handlers

    def test_get_bindings(self, test_context: OrcaTestContext) -> None:
        """Test ChatPresenter.get_bindings returns bindings."""

        self._setup_dependencies(test_context)
        from orca.chat_presenter import get_presenter

        presenter = get_presenter()
        bindings = presenter.get_bindings()

        assert bindings is not None

    def test_toggle_prefix_on_to_off(self, test_context: OrcaTestContext) -> None:
        """Test toggle_prefix from on to off."""

        essential_modules = self._setup_dependencies(test_context)
        settings_mock = essential_modules["orca.settings"]
        from orca.chat_presenter import get_presenter

        settings_mock.chatSpeakRoomName = True
        mock_script = test_context.Mock()

        presenter = get_presenter()
        result = presenter.toggle_prefix(mock_script, None)

        assert result is True
        assert settings_mock.chatSpeakRoomName is False
        mock_script.present_message.assert_called_with(
            essential_modules["orca.messages"].CHAT_ROOM_NAME_PREFIX_OFF
        )

    def test_toggle_prefix_off_to_on(self, test_context: OrcaTestContext) -> None:
        """Test toggle_prefix from off to on."""

        essential_modules = self._setup_dependencies(test_context)
        settings_mock = essential_modules["orca.settings"]
        from orca.chat_presenter import get_presenter

        settings_mock.chatSpeakRoomName = False
        mock_script = test_context.Mock()

        presenter = get_presenter()
        result = presenter.toggle_prefix(mock_script, None)

        assert result is True
        assert settings_mock.chatSpeakRoomName is True
        mock_script.present_message.assert_called_with(
            essential_modules["orca.messages"].CHAT_ROOM_NAME_PREFIX_ON
        )

    def test_toggle_buddy_typing_on_to_off(self, test_context: OrcaTestContext) -> None:
        """Test toggle_buddy_typing from on to off."""

        essential_modules = self._setup_dependencies(test_context)
        settings_mock = essential_modules["orca.settings"]
        from orca.chat_presenter import get_presenter

        settings_mock.chatAnnounceBuddyTyping = True
        mock_script = test_context.Mock()

        presenter = get_presenter()
        result = presenter.toggle_buddy_typing(mock_script, None)

        assert result is True
        assert settings_mock.chatAnnounceBuddyTyping is False
        mock_script.present_message.assert_called_with(
            essential_modules["orca.messages"].CHAT_BUDDY_TYPING_OFF
        )

    def test_toggle_buddy_typing_off_to_on(self, test_context: OrcaTestContext) -> None:
        """Test toggle_buddy_typing from off to on."""

        essential_modules = self._setup_dependencies(test_context)
        settings_mock = essential_modules["orca.settings"]
        from orca.chat_presenter import get_presenter

        settings_mock.chatAnnounceBuddyTyping = False
        mock_script = test_context.Mock()

        presenter = get_presenter()
        result = presenter.toggle_buddy_typing(mock_script, None)

        assert result is True
        assert settings_mock.chatAnnounceBuddyTyping is True
        mock_script.present_message.assert_called_with(
            essential_modules["orca.messages"].CHAT_BUDDY_TYPING_ON
        )

    def test_toggle_message_histories_on_to_off(self, test_context: OrcaTestContext) -> None:
        """Test toggle_message_histories from on to off."""

        essential_modules = self._setup_dependencies(test_context)
        settings_mock = essential_modules["orca.settings"]
        from orca.chat_presenter import get_presenter

        settings_mock.chatRoomHistories = True
        mock_script = test_context.Mock()

        presenter = get_presenter()
        result = presenter.toggle_message_histories(mock_script, None)

        assert result is True
        assert settings_mock.chatRoomHistories is False
        mock_script.present_message.assert_called_with(
            essential_modules["orca.messages"].CHAT_SEPARATE_HISTORIES_OFF
        )

    def test_toggle_message_histories_off_to_on(self, test_context: OrcaTestContext) -> None:
        """Test toggle_message_histories from off to on."""

        essential_modules = self._setup_dependencies(test_context)
        settings_mock = essential_modules["orca.settings"]
        from orca.chat_presenter import get_presenter

        settings_mock.chatRoomHistories = False
        mock_script = test_context.Mock()

        presenter = get_presenter()
        result = presenter.toggle_message_histories(mock_script, None)

        assert result is True
        assert settings_mock.chatRoomHistories is True
        mock_script.present_message.assert_called_with(
            essential_modules["orca.messages"].CHAT_SEPARATE_HISTORIES_ON
        )

    def _setup_navigation_mocks(
        self, test_context: OrcaTestContext, essential_modules: dict[str, Mock]
    ) -> Mock:
        """Setup additional mocks needed for navigation tests. Returns mock_script."""

        settings_manager_mock = essential_modules["orca.settings_manager"]
        manager_instance = settings_manager_mock.get_manager.return_value
        manager_instance.get_app_setting = test_context.Mock(return_value=0)

        script_manager_mock = essential_modules["orca.script_manager"]
        script_manager_instance = script_manager_mock.get_manager.return_value
        script_manager_instance.get_active_script = test_context.Mock(return_value=None)

        mock_script = test_context.Mock()
        mock_script.speech_generator = test_context.Mock()
        mock_script.speech_generator.voice = test_context.Mock(return_value=None)
        mock_script.speak_message = test_context.Mock()
        mock_script.display_message = test_context.Mock()
        mock_script.app = test_context.Mock()

        return mock_script

    def test_present_previous_no_messages(self, test_context: OrcaTestContext) -> None:
        """Test present_previous_message with no messages."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.chat_presenter import Chat, get_presenter

        mock_script = test_context.Mock()
        chat = Chat(mock_script)
        mock_script.chat = chat

        presenter = get_presenter()
        result = presenter.present_previous_message(mock_script, None)

        assert result is True
        mock_script.present_message.assert_called_with(
            essential_modules["orca.messages"].CHAT_NO_MESSAGES
        )

    def test_present_next_no_messages(self, test_context: OrcaTestContext) -> None:
        """Test present_next_message with no messages."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.chat_presenter import Chat, get_presenter

        mock_script = test_context.Mock()
        chat = Chat(mock_script)
        mock_script.chat = chat

        presenter = get_presenter()
        result = presenter.present_next_message(mock_script, None)

        assert result is True
        mock_script.present_message.assert_called_with(
            essential_modules["orca.messages"].CHAT_NO_MESSAGES
        )

    def test_navigation_with_messages(self, test_context: OrcaTestContext) -> None:
        """Test navigation through message history."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.chat_presenter import Chat, Conversation, get_presenter

        mock_script = self._setup_navigation_mocks(test_context, essential_modules)
        chat = Chat(mock_script)
        mock_script.chat = chat

        mock_log = test_context.Mock(spec=Atspi.Accessible)
        conversation = Conversation("TestRoom", mock_log)
        chat._conversation_list.add_message("Message 1", conversation)
        chat._conversation_list.add_message("Message 2", conversation)
        chat._conversation_list.add_message("Message 3", conversation)

        presenter = get_presenter()
        presenter.present_previous_message(mock_script, None)
        assert chat._current_index == -1

        presenter.present_previous_message(mock_script, None)
        assert chat._current_index == -2

        presenter.present_next_message(mock_script, None)
        assert chat._current_index == -1

    def test_navigation_top_boundary(self, test_context: OrcaTestContext) -> None:
        """Test navigation stops at top boundary."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.chat_presenter import Chat, Conversation, get_presenter

        mock_script = self._setup_navigation_mocks(test_context, essential_modules)
        chat = Chat(mock_script)
        mock_script.chat = chat

        mock_log = test_context.Mock(spec=Atspi.Accessible)
        conversation = Conversation("TestRoom", mock_log)
        chat._conversation_list.add_message("Message 1", conversation)
        chat._conversation_list.add_message("Message 2", conversation)

        presenter = get_presenter()
        presenter.present_previous_message(mock_script, None)
        presenter.present_previous_message(mock_script, None)

        mock_script.present_message.reset_mock()
        presenter.present_previous_message(mock_script, None)

        mock_script.present_message.assert_called_with(
            essential_modules["orca.messages"].CHAT_LIST_TOP
        )

    def test_navigation_bottom_boundary(self, test_context: OrcaTestContext) -> None:
        """Test navigation stops at bottom boundary."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.chat_presenter import Chat, Conversation, get_presenter

        mock_script = self._setup_navigation_mocks(test_context, essential_modules)
        chat = Chat(mock_script)
        mock_script.chat = chat

        mock_log = test_context.Mock(spec=Atspi.Accessible)
        conversation = Conversation("TestRoom", mock_log)
        chat._conversation_list.add_message("Message 1", conversation)
        chat._conversation_list.add_message("Message 2", conversation)

        presenter = get_presenter()
        presenter.present_previous_message(mock_script, None)

        mock_script.present_message.reset_mock()
        presenter.present_next_message(mock_script, None)

        mock_script.present_message.assert_called_with(
            essential_modules["orca.messages"].CHAT_LIST_BOTTOM
        )
