# Orca
#
# Copyright 2011-2025 Igalia, S.L.
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

"""Implements generic chat support."""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2011-2025 Igalia, S.L."
__license__   = "LGPL"

from collections import deque
from dataclasses import dataclass
from typing import Any, Iterator, TYPE_CHECKING

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from . import cmdnames
from . import command_manager
from . import dbus_service
from . import debug
from . import focus_manager
from . import guilabels
from . import input_event
from . import input_event_manager
from . import messages
from . import preferences_grid_base
from . import script_manager
from . import settings
from . import settings_manager
from .ax_object import AXObject
from .ax_text import AXText
from .ax_utilities import AXUtilities

if TYPE_CHECKING:
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

    from .scripts import default

class Conversation:
    """Represents a conversation or chat room."""

    HISTORY_SIZE = 9

    def __init__(self, name: str, log: Atspi.Accessible) -> None:
        self._name = name
        self._log = log
        self._messages: deque[str] = deque(maxlen=Conversation.HISTORY_SIZE)
        self._typing_status = ""

    def get_name(self) -> str:
        """Returns the conversation name."""

        return self._name

    def is_log(self, obj: Atspi.Accessible) -> bool:
        """Returns true if obj is the conversation log."""

        return self._log == obj

    def add_message(self, message: str) -> None:
        """Adds the current message to the message history."""

        self._messages.append(message)

    def get_message(self, index: int) -> str:
        """Returns the indexed message from the message history."""

        return self._messages[index]

    def has_messages(self) -> bool:
        """Returns True if there are any messages in the history."""

        return len(self._messages) > 0

    def get_message_count(self) -> int:
        """Returns the number of messages in the history."""

        return len(self._messages)

    def get_typing_status(self) -> str:
        """Returns the typing status of the buddy in this conversation."""

        return self._typing_status

    def set_typing_status(self, status: str) -> None:
        """Sets the typing status of the buddy in this conversation."""

        self._typing_status = status


@dataclass
class Message:
    """Represents a chat message with its associated conversation."""

    text: str
    conversation: Conversation | None


class ConversationList:
    """Represents a list of Conversations."""

    def __init__(self) -> None:
        self._conversations: list[Conversation] = []
        self._messages: deque[Message] = deque(maxlen=Conversation.HISTORY_SIZE)

    def __iter__(self) -> Iterator[Conversation]:
        """Allows iteration over conversations."""

        return iter(self._conversations)

    def add_message(self, message: str, conversation: Conversation | None) -> None:
        """Adds the current message to the message history."""

        if conversation and conversation not in self._conversations:
            self._conversations.append(conversation)

        msg = Message(text=message, conversation=conversation)
        self._messages.append(msg)

    def get_message_and_name(self, index: int) -> tuple[str, str]:
        """Returns the indexed message, room-name tuple from the message history."""

        msg = self._messages[index]
        name = msg.conversation.get_name() if msg.conversation else ""
        return msg.text, name

    def has_messages(self) -> bool:
        """Returns True if there are any messages in the history."""

        return len(self._messages) > 0

    def get_message_count(self) -> int:
        """Returns the number of messages in the history."""

        return len(self._messages)


class Chat:
    """Provides chat state and detection helpers for chat apps."""

    def __init__(self, script: default.Script) -> None:
        self._script = script
        self._conversation_list = ConversationList()
        self._current_index = Conversation.HISTORY_SIZE  # Sentinel for "not navigating"

    def get_current_index(self) -> int:
        """Returns the current message navigation index."""

        return self._current_index

    def set_current_index(self, value: int) -> None:
        """Sets the current message navigation index."""

        self._current_index = value

    def get_message_count(self) -> int:
        """Returns the message count based on current history setting."""

        if get_presenter().get_room_histories():
            conversation = self.get_conversation_for_object(
                focus_manager.get_manager().get_locus_of_focus()
            )
            if conversation:
                return conversation.get_message_count()
            return 0
        return self._conversation_list.get_message_count()

    def get_message_and_name(self, index: int) -> tuple[str, str]:
        """Returns the indexed message and room name from the conversation list."""

        return self._conversation_list.get_message_and_name(index)

    def add_message(self, message: str, conversation: Conversation) -> None:
        """Adds a message to the conversation list."""

        self._conversation_list.add_message(message, conversation)

    def _is_scrollable_list(self, obj: Atspi.Accessible) -> bool:
        """Returns True if obj is a list-like scrollable widget."""

        scroll_pane = AXObject.find_ancestor(obj, AXUtilities.is_scroll_pane)
        if not scroll_pane:
            return False

        return AXUtilities.is_tree_or_tree_table(obj) \
            or AXUtilities.is_list_box(obj) or AXUtilities.is_list(obj)

    def is_buddy_list(self, obj: Atspi.Accessible) -> bool:
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

    def is_in_buddy_list(self, obj: Atspi.Accessible) -> bool:
        """Returns True if obj is, or is inside of, the buddy list."""

        if self.is_buddy_list(obj):
            return True

        buddy_list = AXObject.find_ancestor(obj, self._is_scrollable_list)
        if buddy_list is None:
            return False

        return self.is_buddy_list(buddy_list)

    def get_conversation_for_object(self, obj: Atspi.Accessible) -> Conversation | None:
        """Attempts to locate the conversation associated with obj."""

        if obj is None:
            return None

        name = self.get_chat_room_name(obj)
        for conversation in self._conversation_list:
            if name:
                if name == conversation.get_name():
                    return conversation
            elif conversation.is_log(obj):
                return conversation

        return None

    def is_chat_room_message(self, obj: Atspi.Accessible) -> bool:
        """Returns True if obj holds a chat room conversation."""

        if AXUtilities.is_text(obj) and AXUtilities.is_scroll_pane(AXObject.get_parent(obj)):
            return not AXUtilities.is_editable(obj) and AXUtilities.is_multi_line(obj)
        return False

    def is_focused_chat(self, obj: Atspi.Accessible) -> bool:
        """Returns True if obj is from the active chat room."""

        if AXUtilities.is_showing(obj):
            active = self._script.utilities.top_level_object_is_active_and_current(obj)
            tokens = ["INFO:", obj, "'s window is focused chat:", active]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return active

        # TODO - JD: This was in the smuxi-frontend-gnome Chat class. Who knows if it's
        # still relevant?
        if page_tab := AXObject.find_ancestor(obj, AXUtilities.is_page_tab):
            result = AXUtilities.is_showing(page_tab)
            tokens = ["INFO:", obj, "is in focused tab:", result]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return result

        tokens = ["INFO:", obj, "is not focused chat (not showing)"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return False

    def get_chat_room_name(self, obj: Atspi.Accessible) -> str:
        """Attempts to find the name of the current chat room."""

        def pred(x: Atspi.Accessible) -> bool:
            if not (AXUtilities.is_page_tab(x) or AXUtilities.is_frame(x)):
                return False
            return bool(AXObject.get_name(x))

        ancestor = AXObject.find_ancestor(obj, pred)
        if ancestor:
            return AXObject.get_name(ancestor)
        return ""

    def is_auto_completed_text_event(self, event: Atspi.Event) -> bool:
        """Returns True if event is associated with text being autocompleted."""

        if not AXUtilities.is_text(event.source):
            return False

        if input_event_manager.get_manager().last_event_was_tab() \
           and event.any_data and event.any_data != "\t":
            return True

        return False

    def is_typing_status_changed_event(self, event: Atspi.Event) -> bool:
        """Returns True if event is associated with a change in typing status."""

        if not event.type.startswith("object:text-changed:insert"):
            return False

        # TODO - JD: This is from 15 years ago. Who knows if it still works?
        # Bit of a hack. Pidgin inserts text into the chat history when the
        # user is typing. We seem able to (more or less) reliably distinguish
        # this text via its attributes because these attributes are absent
        # from user inserted text -- no matter how that text is formatted.
        attr = AXText.get_text_attributes_at_offset(event.source, event.detail1)[0]
        return float(attr.get("scale", "1")) < 1 or int(attr.get("weight", "400")) < 400


class ChatPreferencesGrid(preferences_grid_base.AutoPreferencesGrid):
    """Preferences grid for Chat settings."""

    def __init__(self, presenter: ChatPresenter) -> None:
        options = [
            guilabels.CHAT_SPEAK_MESSAGES_ALL,
            guilabels.CHAT_SPEAK_MESSAGES_ACTIVE,
            guilabels.CHAT_SPEAK_MESSAGES_ALL_IF_FOCUSED,
        ]
        values = [
            settings.CHAT_SPEAK_ALL,
            settings.CHAT_SPEAK_FOCUSED_CHANNEL,
            settings.CHAT_SPEAK_ALL_IF_FOCUSED,
        ]

        controls: list[
            preferences_grid_base.BooleanPreferenceControl
            | preferences_grid_base.SelectionPreferenceControl
        ] = [
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.CHAT_SPEAK_ROOM_NAME,
                getter=presenter.get_speak_room_name,
                setter=presenter.set_speak_room_name,
                prefs_key="chatSpeakRoomName"
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.CHAT_SPEAK_ROOM_NAME_LAST,
                getter=presenter.get_speak_room_name_last,
                setter=presenter.set_speak_room_name_last,
                prefs_key="presentChatRoomLast",
                determine_sensitivity=presenter.get_speak_room_name
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.CHAT_ANNOUNCE_BUDDY_TYPING,
                getter=presenter.get_announce_buddy_typing,
                setter=presenter.set_announce_buddy_typing,
                prefs_key="chatAnnounceBuddyTyping"
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.CHAT_SEPARATE_MESSAGE_HISTORIES,
                getter=presenter.get_room_histories,
                setter=presenter.set_room_histories,
                prefs_key="chatRoomHistories"
            ),
            preferences_grid_base.SelectionPreferenceControl(
                label=guilabels.CHAT_SPEAK_MESSAGES_FROM,
                options=options,
                values=values,
                getter=presenter.get_message_verbosity,
                setter=presenter.set_message_verbosity,
                prefs_key="chatMessageVerbosity"
            ),
        ]

        super().__init__(guilabels.KB_GROUP_CHAT, controls)


class ChatPresenter:
    """Presenter for chat preferences and commands."""

    def __init__(self) -> None:
        self._focused_channel_radio_button: Gtk.RadioButton | None = None
        self._all_channels_radio_button: Gtk.RadioButton | None = None
        self._all_messages_radio_button: Gtk.RadioButton | None = None
        self._buddy_typing_check_button: Gtk.CheckButton | None = None
        self._chat_room_histories_check_button: Gtk.CheckButton | None = None
        self._speak_name_check_button: Gtk.CheckButton | None = None
        self._initialized: bool = False

        msg = "CHAT PRESENTER: Registering D-Bus commands."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        controller = dbus_service.get_remote_controller()
        controller.register_decorated_module("ChatPresenter", self)

    def set_up_commands(self) -> None:
        """Sets up commands with CommandManager."""

        if self._initialized:
            return
        self._initialized = True

        manager = command_manager.get_manager()
        group_label = guilabels.KB_GROUP_CHAT

        commands_data = [
            ("chat_toggle_room_name_prefix", self.toggle_prefix,
             cmdnames.CHAT_TOGGLE_ROOM_NAME_PREFIX),
            ("chat_toggle_buddy_typing", self.toggle_buddy_typing,
             cmdnames.CHAT_TOGGLE_BUDDY_TYPING),
            ("chat_toggle_message_histories", self.toggle_message_histories,
             cmdnames.CHAT_TOGGLE_MESSAGE_HISTORIES),
            ("chat_previous_message", self.present_previous_message,
             cmdnames.CHAT_PREVIOUS_MESSAGE),
            ("chat_next_message", self.present_next_message,
             cmdnames.CHAT_NEXT_MESSAGE),
        ]

        for name, function, description in commands_data:
            manager.add_command(
                command_manager.KeyboardCommand(
                    name,
                    function,
                    group_label,
                    description,
                    desktop_keybinding=None,
                    laptop_keybinding=None,
                )
            )

        msg = "CHAT PRESENTER: Commands set up."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def get_app_preferences_gui(self, app: Atspi.Accessible) -> Gtk.Grid:
        """Return a GtkGrid containing app-specific chat preferences."""

        grid = Gtk.Grid()
        grid.set_border_width(12)

        label = guilabels.CHAT_SPEAK_ROOM_NAME
        self._speak_name_check_button = Gtk.CheckButton.new_with_mnemonic(label)
        self._speak_name_check_button.set_active(settings.chatSpeakRoomName)
        grid.attach(self._speak_name_check_button, 0, 0, 1, 1)

        label = guilabels.CHAT_ANNOUNCE_BUDDY_TYPING
        self._buddy_typing_check_button = Gtk.CheckButton.new_with_mnemonic(label)
        self._buddy_typing_check_button.set_active(settings.chatAnnounceBuddyTyping)
        grid.attach(self._buddy_typing_check_button, 0, 1, 1, 1)

        label = guilabels.CHAT_SEPARATE_MESSAGE_HISTORIES
        self._chat_room_histories_check_button = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self._chat_room_histories_check_button.set_active(settings.chatRoomHistories)
        grid.attach(self._chat_room_histories_check_button, 0, 2, 1, 1)

        messages_frame = Gtk.Frame()
        grid.attach(messages_frame, 0, 3, 1, 1)
        label = Gtk.Label(f"<b>{guilabels.CHAT_SPEAK_MESSAGES_FROM}</b>")
        label.set_use_markup(True)
        messages_frame.set_label_widget(label)

        messages_alignment = Gtk.Alignment.new(0.5, 0.5, 1, 1)
        messages_alignment.set_padding(0, 0, 12, 0)
        messages_frame.add(messages_alignment)
        messages_grid = Gtk.Grid()
        messages_alignment.add(messages_grid)

        label = guilabels.CHAT_SPEAK_MESSAGES_ALL
        rb1 = Gtk.RadioButton.new_with_mnemonic(None, label)
        rb1.set_active(settings.chatMessageVerbosity == settings.CHAT_SPEAK_ALL)
        self._all_messages_radio_button = rb1
        messages_grid.attach(self._all_messages_radio_button, 0, 0, 1, 1)

        label = guilabels.CHAT_SPEAK_MESSAGES_ACTIVE
        rb2 = Gtk.RadioButton.new_with_mnemonic(None, label)
        rb2.join_group(rb1)
        rb2.set_active(settings.chatMessageVerbosity == settings.CHAT_SPEAK_FOCUSED_CHANNEL)
        self._focused_channel_radio_button = rb2
        messages_grid.attach(self._focused_channel_radio_button, 0, 1, 1, 1)

        label = guilabels.CHAT_SPEAK_MESSAGES_ALL_IF_FOCUSED % AXObject.get_name(app)
        rb3 = Gtk.RadioButton.new_with_mnemonic(None, label)
        rb3.join_group(rb1)
        rb3.set_active(settings.chatMessageVerbosity == settings.CHAT_SPEAK_ALL_IF_FOCUSED)
        self._all_channels_radio_button = rb3
        messages_grid.attach(self._all_channels_radio_button, 0, 2, 1, 1)

        grid.show_all()

        return grid

    def get_preferences_from_gui(self) -> dict[str, Any]:
        """Returns a dictionary with the app-specific preferences."""

        assert self._all_channels_radio_button
        assert self._focused_channel_radio_button
        assert self._speak_name_check_button
        assert self._buddy_typing_check_button
        assert self._chat_room_histories_check_button

        if self._all_channels_radio_button.get_active():
            verbosity = settings.CHAT_SPEAK_ALL_IF_FOCUSED
        elif self._focused_channel_radio_button.get_active():
            verbosity = settings.CHAT_SPEAK_FOCUSED_CHANNEL
        else:
            verbosity = settings.CHAT_SPEAK_ALL

        return {
            "chatMessageVerbosity": verbosity,
            "chatSpeakRoomName": self._speak_name_check_button.get_active(),
            "chatAnnounceBuddyTyping": self._buddy_typing_check_button.get_active(),
            "chatRoomHistories": self._chat_room_histories_check_button.get_active(),
        }

    def create_preferences_grid(self) -> ChatPreferencesGrid:
        """Create and return the chat preferences grid."""

        return ChatPreferencesGrid(self)

    def utter_message(
        self,
        script: default.Script,
        room_name: str,
        message: str,
        focused: bool = True
    ) -> None:
        """Speak/braille a chat room message, taking user settings into account."""

        verbosity = self.get_message_verbosity(script.app)
        active_script = script_manager.get_manager().get_active_script()
        if active_script is not None and active_script.name != script.name \
           and verbosity == settings.CHAT_SPEAK_ALL_IF_FOCUSED:
            return
        if not focused and verbosity == settings.CHAT_SPEAK_FOCUSED_CHANNEL:
            return

        text = ""
        if room_name and self.get_speak_room_name():
            text = messages.CHAT_MESSAGE_FROM_ROOM % room_name

        if not self.get_speak_room_name_last():
            text = f"{text} {message}"
        else:
            text = f"{message} {text}"

        if text.strip():
            voice = script.speech_generator.voice(string=text)
            script.speak_message(text, voice=voice)
        script.display_message(text)

    def present_message_at_index(self, script: default.Script, index: int) -> None:
        """Presents the chat message at the specified index."""

        chat = script.chat
        message, chat_room_name = None, None

        if self.get_room_histories():
            conversation = chat.get_conversation_for_object(
                focus_manager.get_manager().get_locus_of_focus()
            )
            if conversation:
                message = conversation.get_message(index)
                chat_room_name = conversation.get_name()
        else:
            message, chat_room_name = chat.get_message_and_name(index)

        if message and chat_room_name:
            self.utter_message(script, chat_room_name, message, True)

    def present_inserted_text(self, script: default.Script, event: Atspi.Event) -> bool:
        """Presents text inserted into a chat application."""

        chat = script.chat
        if not event.any_data or AXUtilities.is_text_input(event.source):
            return False

        if chat.is_in_buddy_list(event.source):
            return True

        if chat.is_typing_status_changed_event(event):
            self._present_typing_status_change(script, event, event.any_data)
            return True

        if chat.is_chat_room_message(event.source):
            conversation = chat.get_conversation_for_object(event.source)
            if conversation is None:
                name = chat.get_chat_room_name(event.source)
                conversation = Conversation(name, event.source)
            name = conversation.get_name()
            message = event.any_data.strip("\n")
            if message:
                conversation.add_message(message)
                chat.add_message(message, conversation)

            focused = chat.is_focused_chat(event.source)
            if focused:
                name = ""
            if message:
                self.utter_message(script, name, message, focused)
            return True

        if chat.is_auto_completed_text_event(event):
            text = event.any_data
            voice = script.speech_generator.voice(string=text)
            script.speak_message(text, voice=voice)
            return True

        return False

    def _present_typing_status_change(
        self,
        script: default.Script,
        event: Atspi.Event,
        status: str
    ) -> bool:
        """Presents a change in typing status for the current conversation."""

        if not self.get_announce_buddy_typing():
            return False

        chat = script.chat
        conversation = chat.get_conversation_for_object(event.source)
        if conversation and status != conversation.get_typing_status():
            voice = script.speech_generator.voice(string=status)
            script.speak_message(status, voice=voice)
            conversation.set_typing_status(status)
            return True

        return False

    @dbus_service.command
    def present_previous_message(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Navigate to and present the previous chat message in the history."""

        tokens = ["CHAT PRESENTER: present_previous_message. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        chat = script.chat
        message_count = chat.get_message_count()
        if message_count == 0:
            if notify_user:
                script.present_message(messages.CHAT_NO_MESSAGES)
            return True

        oldest_index = -message_count
        current_index = chat.get_current_index()

        if current_index < oldest_index:
            current_index = oldest_index
            chat.set_current_index(current_index)

        if current_index == oldest_index:
            if notify_user:
                script.present_message(messages.CHAT_LIST_TOP)
            self.present_message_at_index(script, oldest_index)
            return True

        if current_index >= 0:
            chat.set_current_index(-1)
        else:
            chat.set_current_index(current_index - 1)

        self.present_message_at_index(script, chat.get_current_index())
        return True

    @dbus_service.command
    def present_next_message(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Navigate to and present the next chat message in the history."""

        tokens = ["CHAT PRESENTER: present_next_message. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        chat = script.chat
        message_count = chat.get_message_count()
        if message_count == 0:
            if notify_user:
                script.present_message(messages.CHAT_NO_MESSAGES)
            return True

        oldest_index = -message_count
        current_index = chat.get_current_index()

        if current_index < oldest_index:
            current_index = oldest_index
            chat.set_current_index(current_index)

        if current_index == -1:
            if notify_user:
                script.present_message(messages.CHAT_LIST_BOTTOM)
            self.present_message_at_index(script, -1)
            return True

        if current_index >= 0:
            chat.set_current_index(-1)
        else:
            chat.set_current_index(current_index + 1)

        self.present_message_at_index(script, chat.get_current_index())
        return True

    @dbus_service.getter
    def get_speak_room_name(self, app: Atspi.Accessible | None = None) -> bool:
        """Returns whether to speak the chat room name."""

        if app:
            result = settings_manager.get_manager().get_app_setting(app, "chatSpeakRoomName")
            if isinstance(result, bool):
                return result
        return settings.chatSpeakRoomName

    @dbus_service.setter
    def set_speak_room_name(self, value: bool) -> bool:
        """Sets whether to speak the chat room name."""

        settings.chatSpeakRoomName = value
        return value

    @dbus_service.getter
    def get_announce_buddy_typing(self) -> bool:
        """Returns whether to announce when buddies are typing."""

        return settings.chatAnnounceBuddyTyping

    @dbus_service.setter
    def set_announce_buddy_typing(self, value: bool) -> bool:
        """Sets whether to announce when buddies are typing."""

        settings.chatAnnounceBuddyTyping = value
        return value

    @dbus_service.getter
    def get_room_histories(self) -> bool:
        """Returns whether to provide chat room specific message histories."""

        return settings.chatRoomHistories

    @dbus_service.setter
    def set_room_histories(self, value: bool) -> bool:
        """Sets whether to provide chat room specific message histories."""

        settings.chatRoomHistories = value
        return value

    @dbus_service.getter
    def get_message_verbosity(self, app: Atspi.Accessible | None = None) -> int:
        """Returns the chat message verbosity setting."""

        if app:
            result = settings_manager.get_manager().get_app_setting(app, "chatMessageVerbosity")
            if isinstance(result, int):
                return result
        return settings.chatMessageVerbosity

    @dbus_service.setter
    def set_message_verbosity(self, value: int) -> int:
        """Sets the chat message verbosity setting."""

        settings.chatMessageVerbosity = value
        return value

    @dbus_service.getter
    def get_speak_room_name_last(self) -> bool:
        """Returns whether to speak the chat room name after the message."""

        return settings.presentChatRoomLast

    @dbus_service.setter
    def set_speak_room_name_last(self, value: bool) -> bool:
        """Sets whether to speak the chat room name after the message."""

        settings.presentChatRoomLast = value
        return value

    @dbus_service.command
    def toggle_prefix(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Toggles whether we prefix chat room messages with the name of the chat room."""

        tokens = ["CHAT PRESENTER: toggle_prefix. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        line = messages.CHAT_ROOM_NAME_PREFIX_ON
        speak_room_name = self.get_speak_room_name()
        self.set_speak_room_name(not speak_room_name)
        if speak_room_name:
            line = messages.CHAT_ROOM_NAME_PREFIX_OFF
        if notify_user:
            script.present_message(line)
        return True

    @dbus_service.command
    def toggle_buddy_typing(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Toggles whether we announce when our buddies are typing a message."""

        tokens = ["CHAT PRESENTER: toggle_buddy_typing. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        line = messages.CHAT_BUDDY_TYPING_ON
        announce_typing = self.get_announce_buddy_typing()
        self.set_announce_buddy_typing(not announce_typing)
        if announce_typing:
            line = messages.CHAT_BUDDY_TYPING_OFF
        if notify_user:
            script.present_message(line)
        return True

    @dbus_service.command
    def toggle_message_histories(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Toggles whether we provide chat room specific message histories."""

        tokens = ["CHAT PRESENTER: toggle_message_histories. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        line = messages.CHAT_SEPARATE_HISTORIES_ON
        room_histories = self.get_room_histories()
        self.set_room_histories(not room_histories)
        if room_histories:
            line = messages.CHAT_SEPARATE_HISTORIES_OFF
        if notify_user:
            script.present_message(line)
        return True


_presenter: ChatPresenter = ChatPresenter()


def get_presenter() -> ChatPresenter:
    """Returns the Chat Presenter."""

    return _presenter
