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

from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

from . import (
    cmdnames,
    command_manager,
    dbus_service,
    debug,
    focus_manager,
    gsettings_registry,
    guilabels,
    input_event,
    input_event_manager,
    messages,
    preferences_grid_base,
    presentation_manager,
    script_manager,
)
from .ax_object import AXObject
from .ax_selection import AXSelection
from .ax_text import AXText
from .ax_utilities import AXUtilities

if TYPE_CHECKING:
    from collections.abc import Iterator

    from gi.repository import Atspi

    from .scripts import default


@gsettings_registry.get_registry().gsettings_enum(
    "org.gnome.Orca.ChatMessageVerbosity",
    values={"all": 0, "all-if-focused": 1, "focused-channel": 2, "active-channel": 3},
)
class ChatMessageVerbosity(Enum):
    """Chat message verbosity level enumeration."""

    ALL_ANY_APP = 0
    ALL_ACTIVE_APP = 1
    CURRENT_ACTIVE_APP = 2
    CURRENT_ANY_APP = 3

    @property
    def string_name(self) -> str:
        """Returns the lowercase string name for this enum value."""

        return self.name.lower().replace("_", "-")


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

    def get_log(self) -> Atspi.Accessible:
        """Returns the conversation log accessible."""

        return self._log

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

    def get_message_and_name(self, index: int) -> tuple[str, str, Atspi.Accessible | None]:
        """Returns the indexed message, room-name, and log from the message history."""

        msg = self._messages[index]
        if msg.conversation:
            return msg.text, msg.conversation.get_name(), msg.conversation.get_log()
        return msg.text, "", None

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
                focus_manager.get_manager().get_locus_of_focus(),
            )
            if conversation:
                return conversation.get_message_count()
            return 0
        return self._conversation_list.get_message_count()

    def get_message_and_name(self, index: int) -> tuple[str, str, Atspi.Accessible | None]:
        """Returns the indexed message, room name, and log from the conversation list."""

        return self._conversation_list.get_message_and_name(index)

    def add_message(self, message: str, conversation: Conversation) -> None:
        """Adds a message to the conversation list."""

        self._conversation_list.add_message(message, conversation)

    def _is_scrollable_list(self, obj: Atspi.Accessible) -> bool:
        """Returns True if obj is a list-like scrollable widget."""

        scroll_pane = AXObject.find_ancestor(obj, AXUtilities.is_scroll_pane)
        if not scroll_pane:
            return False

        return (
            AXUtilities.is_tree_or_tree_table(obj)
            or AXUtilities.is_list_box(obj)
            or AXUtilities.is_list(obj)
        )

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

    def is_current_channel_in_active_app(self, obj: Atspi.Accessible) -> bool:
        """Returns True if obj is from the active chat room in the focused window."""

        if not self.is_active_channel(obj):
            return False
        return self._script.utilities.top_level_object_is_active_and_current(obj)

    def is_active_channel(self, obj: Atspi.Accessible) -> bool:
        """Returns True if obj is in the active/selected channel."""

        if page_tab := AXObject.find_ancestor(obj, AXUtilities.is_page_tab):
            tab_list = AXObject.get_parent(page_tab)
            selected = AXSelection.get_selected_child(tab_list, 0)
            result = selected == page_tab
            tokens = [
                "CHAT:",
                obj,
                "tab:",
                page_tab,
                "selected tab:",
                selected,
                "is active channel:",
                result,
            ]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return result

        if AXUtilities.is_showing(obj):
            tokens = ["CHAT:", obj, "is in active channel (showing)"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        tokens = ["CHAT:", obj, "is not in active channel (not showing, no tab)"]
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

        return (
            input_event_manager.get_manager().last_event_was_tab()
            and event.any_data
            and event.any_data != "\t"
        )

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

    _gsettings_schema = "chat"

    def __init__(self, presenter: ChatPresenter) -> None:
        options = [
            guilabels.CHAT_SPEAK_MESSAGES_ALL,
            guilabels.CHAT_SPEAK_MESSAGES_ACTIVE_CHANNEL,
            guilabels.CHAT_SPEAK_MESSAGES_ALL_IF_FOCUSED,
            guilabels.CHAT_SPEAK_MESSAGES_ACTIVE,
        ]
        values = [
            ChatMessageVerbosity.ALL_ANY_APP.value,
            ChatMessageVerbosity.CURRENT_ANY_APP.value,
            ChatMessageVerbosity.ALL_ACTIVE_APP.value,
            ChatMessageVerbosity.CURRENT_ACTIVE_APP.value,
        ]

        controls: list[
            preferences_grid_base.BooleanPreferenceControl
            | preferences_grid_base.SelectionPreferenceControl
        ] = [
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.CHAT_SPEAK_ROOM_NAME,
                getter=presenter.get_speak_room_name,
                setter=presenter.set_speak_room_name,
                prefs_key="speak-room-name",
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.CHAT_SPEAK_ROOM_NAME_LAST,
                getter=presenter.get_speak_room_name_last,
                setter=presenter.set_speak_room_name_last,
                prefs_key="speak-room-name-last",
                determine_sensitivity=presenter.get_speak_room_name,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.CHAT_ANNOUNCE_BUDDY_TYPING,
                getter=presenter.get_announce_buddy_typing,
                setter=presenter.set_announce_buddy_typing,
                prefs_key="announce-buddy-typing",
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.CHAT_SEPARATE_MESSAGE_HISTORIES,
                getter=presenter.get_room_histories,
                setter=presenter.set_room_histories,
                prefs_key="room-histories",
            ),
            preferences_grid_base.SelectionPreferenceControl(
                label=guilabels.CHAT_SPEAK_MESSAGES_FROM,
                options=options,
                values=values,
                getter=presenter.get_message_verbosity,
                setter=presenter.set_message_verbosity,
                prefs_key="message-verbosity",
            ),
        ]

        super().__init__(guilabels.KB_GROUP_CHAT, controls)


@gsettings_registry.get_registry().gsettings_schema("org.gnome.Orca.Chat", name="chat")
class ChatPresenter:
    """Presenter for chat preferences and commands."""

    _SCHEMA = "chat"

    def _get_setting(self, key: str, default: bool) -> bool:
        """Returns the dconf value for key, or default if not in dconf."""

        return gsettings_registry.get_registry().layered_lookup(
            self._SCHEMA,
            key,
            "b",
            default=default,
        )

    def __init__(self) -> None:
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
            (
                "chat_toggle_room_name_prefix",
                self.toggle_prefix,
                cmdnames.CHAT_TOGGLE_ROOM_NAME_PREFIX,
            ),
            (
                "chat_toggle_buddy_typing",
                self.toggle_buddy_typing,
                cmdnames.CHAT_TOGGLE_BUDDY_TYPING,
            ),
            (
                "chat_toggle_message_histories",
                self.toggle_message_histories,
                cmdnames.CHAT_TOGGLE_MESSAGE_HISTORIES,
            ),
            (
                "chat_previous_message",
                self.present_previous_message,
                cmdnames.CHAT_PREVIOUS_MESSAGE,
            ),
            ("chat_next_message", self.present_next_message, cmdnames.CHAT_NEXT_MESSAGE),
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
                ),
            )

        msg = "CHAT PRESENTER: Commands set up."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def create_preferences_grid(self) -> ChatPreferencesGrid:
        """Create and return the chat preferences grid."""

        return ChatPreferencesGrid(self)

    def utter_message(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        script: default.Script,
        obj: Atspi.Accessible,
        room_name: str,
        message: str,
        focused: bool = True,
        active_channel: bool = True,
    ) -> None:
        """Speak/braille a chat room message, taking user settings into account."""

        verbosity = self.get_message_verbosity(script.app)
        active_script = script_manager.get_manager().get_active_script()
        if (
            active_script is not None
            and active_script.name != script.name
            and verbosity == ChatMessageVerbosity.ALL_ACTIVE_APP.value
        ):
            return
        if not focused and verbosity == ChatMessageVerbosity.CURRENT_ACTIVE_APP.value:
            return
        if not active_channel and verbosity == ChatMessageVerbosity.CURRENT_ANY_APP.value:
            return

        text = ""
        if room_name and self.get_speak_room_name():
            text = messages.CHAT_MESSAGE_FROM_ROOM % room_name

        if not self.get_speak_room_name_last():
            text = f"{text} {message}"
        else:
            text = f"{message} {text}"

        if text.strip():
            presentation_manager.get_manager().speak_accessible_text(obj, text)
        presentation_manager.get_manager().present_braille_message(text)

    def present_message_at_index(self, script: default.Script, index: int) -> None:
        """Presents the chat message at the specified index."""

        chat = script.chat
        if self.get_room_histories():
            conversation = chat.get_conversation_for_object(
                focus_manager.get_manager().get_locus_of_focus(),
            )
            if not conversation:
                return
            message = conversation.get_message(index)
            chat_room_name = conversation.get_name()
            log: Atspi.Accessible | None = conversation.get_log()
        else:
            message, chat_room_name, log = chat.get_message_and_name(index)

        if message and chat_room_name and log:
            self.utter_message(script, log, chat_room_name, message, True)

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

            focused = chat.is_current_channel_in_active_app(event.source)
            active_channel = chat.is_active_channel(event.source)
            if focused:
                name = ""
            if message:
                self.utter_message(script, event.source, name, message, focused, active_channel)
            return True

        if chat.is_auto_completed_text_event(event):
            text = event.any_data
            presentation_manager.get_manager().speak_accessible_text(event.source, text)
            return True

        return False

    def _present_typing_status_change(
        self,
        script: default.Script,
        event: Atspi.Event,
        status: str,
    ) -> bool:
        """Presents a change in typing status for the current conversation."""

        if not self.get_announce_buddy_typing():
            return False

        chat = script.chat
        conversation = chat.get_conversation_for_object(event.source)
        if conversation and status != conversation.get_typing_status():
            presentation_manager.get_manager().speak_accessible_text(event.source, status)
            conversation.set_typing_status(status)
            return True

        return False

    @dbus_service.command
    def present_previous_message(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Navigate to and present the previous chat message in the history."""

        tokens = [
            "CHAT PRESENTER: present_previous_message. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        chat = script.chat
        message_count = chat.get_message_count()
        if message_count == 0:
            if notify_user:
                presentation_manager.get_manager().present_message(messages.CHAT_NO_MESSAGES)
            return True

        oldest_index = -message_count
        current_index = chat.get_current_index()

        if current_index < oldest_index:
            current_index = oldest_index
            chat.set_current_index(current_index)

        if current_index == oldest_index:
            if notify_user:
                presentation_manager.get_manager().present_message(messages.CHAT_LIST_TOP)
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
        notify_user: bool = True,
    ) -> bool:
        """Navigate to and present the next chat message in the history."""

        tokens = [
            "CHAT PRESENTER: present_next_message. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        chat = script.chat
        message_count = chat.get_message_count()
        if message_count == 0:
            if notify_user:
                presentation_manager.get_manager().present_message(messages.CHAT_NO_MESSAGES)
            return True

        oldest_index = -message_count
        current_index = chat.get_current_index()

        if current_index < oldest_index:
            current_index = oldest_index
            chat.set_current_index(current_index)

        if current_index == -1:
            if notify_user:
                presentation_manager.get_manager().present_message(messages.CHAT_LIST_BOTTOM)
            self.present_message_at_index(script, -1)
            return True

        if current_index >= 0:
            chat.set_current_index(-1)
        else:
            chat.set_current_index(current_index + 1)

        self.present_message_at_index(script, chat.get_current_index())
        return True

    @gsettings_registry.get_registry().gsetting(
        key="speak-room-name",
        schema="chat",
        gtype="b",
        default=False,
        summary="Speak chat room name",
        migration_key="chatSpeakRoomName",
    )
    @dbus_service.getter
    def get_speak_room_name(self, app: Atspi.Accessible | None = None) -> bool:
        """Returns whether to speak the chat room name."""

        app_name = AXObject.get_name(app) if app else None
        return gsettings_registry.get_registry().layered_lookup(
            self._SCHEMA,
            "speak-room-name",
            "b",
            app_name=app_name,
            default=False,
        )

    @dbus_service.setter
    def set_speak_room_name(self, value: bool) -> bool:
        """Sets whether to speak the chat room name."""

        gsettings_registry.get_registry().set_runtime_value(self._SCHEMA, "speak-room-name", value)
        return value

    @gsettings_registry.get_registry().gsetting(
        key="announce-buddy-typing",
        schema="chat",
        gtype="b",
        default=False,
        summary="Announce when buddies are typing",
        migration_key="chatAnnounceBuddyTyping",
    )
    @dbus_service.getter
    def get_announce_buddy_typing(self) -> bool:
        """Returns whether to announce when buddies are typing."""

        return self._get_setting("announce-buddy-typing", False)

    @dbus_service.setter
    def set_announce_buddy_typing(self, value: bool) -> bool:
        """Sets whether to announce when buddies are typing."""

        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            "announce-buddy-typing",
            value,
        )
        return value

    @gsettings_registry.get_registry().gsetting(
        key="room-histories",
        schema="chat",
        gtype="b",
        default=False,
        summary="Provide chat room specific message histories",
        migration_key="chatRoomHistories",
    )
    @dbus_service.getter
    def get_room_histories(self) -> bool:
        """Returns whether to provide chat room specific message histories."""

        return self._get_setting("room-histories", False)

    @dbus_service.setter
    def set_room_histories(self, value: bool) -> bool:
        """Sets whether to provide chat room specific message histories."""

        gsettings_registry.get_registry().set_runtime_value(self._SCHEMA, "room-histories", value)
        return value

    @gsettings_registry.get_registry().gsetting(
        key="message-verbosity",
        schema="chat",
        genum="org.gnome.Orca.ChatMessageVerbosity",
        default="all",
        summary="Chat message verbosity (all, all-if-focused, focused-channel, active-channel)",
        migration_key="chatMessageVerbosity",
    )
    @dbus_service.getter
    def get_message_verbosity(self, app: Atspi.Accessible | None = None) -> int:
        """Returns the chat message verbosity setting."""

        app_name = AXObject.get_name(app) if app else None
        nick = gsettings_registry.get_registry().layered_lookup(
            self._SCHEMA,
            "message-verbosity",
            "",
            genum="org.gnome.Orca.ChatMessageVerbosity",
            app_name=app_name,
            default="all",
        )
        enum_values = gsettings_registry.get_registry().get_enum_values(
            "org.gnome.Orca.ChatMessageVerbosity",
        )
        if enum_values and nick in enum_values:
            return enum_values[nick]
        return 0

    @dbus_service.setter
    def set_message_verbosity(self, value: int) -> int:
        """Sets the chat message verbosity setting."""

        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            "message-verbosity",
            value,
        )
        return value

    @gsettings_registry.get_registry().gsetting(
        key="speak-room-name-last",
        schema="chat",
        gtype="b",
        default=False,
        summary="Speak chat room name after message",
        migration_key="presentChatRoomLast",
    )
    @dbus_service.getter
    def get_speak_room_name_last(self) -> bool:
        """Returns whether to speak the chat room name after the message."""

        return self._get_setting("speak-room-name-last", False)

    @dbus_service.setter
    def set_speak_room_name_last(self, value: bool) -> bool:
        """Sets whether to speak the chat room name after the message."""

        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            "speak-room-name-last",
            value,
        )
        return value

    @dbus_service.command
    def toggle_prefix(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Toggles whether we prefix chat room messages with the name of the chat room."""

        tokens = [
            "CHAT PRESENTER: toggle_prefix. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        line = messages.CHAT_ROOM_NAME_PREFIX_ON
        speak_room_name = self.get_speak_room_name()
        self.set_speak_room_name(not speak_room_name)
        if speak_room_name:
            line = messages.CHAT_ROOM_NAME_PREFIX_OFF
        if notify_user:
            presentation_manager.get_manager().present_message(line)
        return True

    @dbus_service.command
    def toggle_buddy_typing(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Toggles whether we announce when our buddies are typing a message."""

        tokens = [
            "CHAT PRESENTER: toggle_buddy_typing. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        line = messages.CHAT_BUDDY_TYPING_ON
        announce_typing = self.get_announce_buddy_typing()
        self.set_announce_buddy_typing(not announce_typing)
        if announce_typing:
            line = messages.CHAT_BUDDY_TYPING_OFF
        if notify_user:
            presentation_manager.get_manager().present_message(line)
        return True

    @dbus_service.command
    def toggle_message_histories(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Toggles whether we provide chat room specific message histories."""

        tokens = [
            "CHAT PRESENTER: toggle_message_histories. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        line = messages.CHAT_SEPARATE_HISTORIES_ON
        room_histories = self.get_room_histories()
        self.set_room_histories(not room_histories)
        if room_histories:
            line = messages.CHAT_SEPARATE_HISTORIES_OFF
        if notify_user:
            presentation_manager.get_manager().present_message(line)
        return True


_presenter: ChatPresenter = ChatPresenter()


def get_presenter() -> ChatPresenter:
    """Returns the Chat Presenter."""

    return _presenter
