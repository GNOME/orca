# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
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

# pylint: disable=too-many-public-methods
# pylint: disable=too-many-lines
# pylint:disable=too-many-branches
# pylint:disable=too-many-return-statements
# pylint:disable=wrong-import-position

"""Provides typing echo support."""

# This must be the first non-docstring line in the module to make linters happy.
from __future__ import annotations


import string
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Iterable, TYPE_CHECKING

from . import cmdnames
from . import command_manager
from . import dbus_service
from . import debug
from . import guilabels
from . import input_event
from . import messages
from . import preferences_grid_base
from . import presentation_manager
from . import settings
from . import speech_presenter
from .ax_text import AXText
from .ax_utilities import AXUtilities
from . import gsettings_registry

if TYPE_CHECKING:
    from gi.repository import Atspi

    from .scripts import default


class PreferenceCategory(Enum):
    """Categories of typing echo preferences for UI grouping."""

    PRIMARY = "primary"
    KEY = "key"
    TEXT = "text"


@dataclass(frozen=True)
class TypingEchoPreference:
    """Descriptor for a single typing echo preference."""

    prefs_key: str
    label: str
    category: PreferenceCategory
    getter: Callable[[], bool]
    setter: Callable[[bool], bool]


class TypingEchoPreferencesGrid(preferences_grid_base.AutoPreferencesGrid):
    """GtkGrid containing the Typing Echo preferences page."""

    _gsettings_schema = "typing-echo"

    def __init__(self, presenter: "TypingEchoPresenter") -> None:
        self._enable_key_echo_control = preferences_grid_base.BooleanPreferenceControl(
            label=guilabels.ECHO_ENABLE_KEY_ECHO,
            getter=presenter.get_key_echo_enabled,
            setter=presenter.set_key_echo_enabled,
            prefs_key="enableKeyEcho",
        )

        controls = [
            self._enable_key_echo_control,
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.ECHO_ALPHABETIC_KEYS,
                getter=presenter.get_alphabetic_keys_enabled,
                setter=presenter.set_alphabetic_keys_enabled,
                prefs_key="enableAlphabeticKeys",
                member_of=guilabels.ECHO_KEYS_TO_ECHO,
                determine_sensitivity=presenter.get_key_echo_enabled,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.ECHO_NUMERIC_KEYS,
                getter=presenter.get_numeric_keys_enabled,
                setter=presenter.set_numeric_keys_enabled,
                prefs_key="enableNumericKeys",
                member_of=guilabels.ECHO_KEYS_TO_ECHO,
                determine_sensitivity=presenter.get_key_echo_enabled,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.ECHO_PUNCTUATION_KEYS,
                getter=presenter.get_punctuation_keys_enabled,
                setter=presenter.set_punctuation_keys_enabled,
                prefs_key="enablePunctuationKeys",
                member_of=guilabels.ECHO_KEYS_TO_ECHO,
                determine_sensitivity=presenter.get_key_echo_enabled,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.ECHO_SPACE,
                getter=presenter.get_space_enabled,
                setter=presenter.set_space_enabled,
                prefs_key="enableSpace",
                member_of=guilabels.ECHO_KEYS_TO_ECHO,
                determine_sensitivity=presenter.get_key_echo_enabled,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.ECHO_MODIFIER_KEYS,
                getter=presenter.get_modifier_keys_enabled,
                setter=presenter.set_modifier_keys_enabled,
                prefs_key="enableModifierKeys",
                member_of=guilabels.ECHO_KEYS_TO_ECHO,
                determine_sensitivity=presenter.get_key_echo_enabled,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.ECHO_FUNCTION_KEYS,
                getter=presenter.get_function_keys_enabled,
                setter=presenter.set_function_keys_enabled,
                prefs_key="enableFunctionKeys",
                member_of=guilabels.ECHO_KEYS_TO_ECHO,
                determine_sensitivity=presenter.get_key_echo_enabled,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.ECHO_ACTION_KEYS,
                getter=presenter.get_action_keys_enabled,
                setter=presenter.set_action_keys_enabled,
                prefs_key="enableActionKeys",
                member_of=guilabels.ECHO_KEYS_TO_ECHO,
                determine_sensitivity=presenter.get_key_echo_enabled,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.ECHO_NAVIGATION_KEYS,
                getter=presenter.get_navigation_keys_enabled,
                setter=presenter.set_navigation_keys_enabled,
                prefs_key="enableNavigationKeys",
                member_of=guilabels.ECHO_KEYS_TO_ECHO,
                determine_sensitivity=presenter.get_key_echo_enabled,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.ECHO_DIACRITICAL_KEYS,
                getter=presenter.get_diacritical_keys_enabled,
                setter=presenter.set_diacritical_keys_enabled,
                prefs_key="enableDiacriticalKeys",
                member_of=guilabels.ECHO_KEYS_TO_ECHO,
                determine_sensitivity=presenter.get_key_echo_enabled,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.ECHO_CHARACTER,
                getter=presenter.get_character_echo_enabled,
                setter=presenter.set_character_echo_enabled,
                prefs_key="enableEchoByCharacter",
                member_of=guilabels.ECHO_TYPING_ECHO,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.ECHO_WORD,
                getter=presenter.get_word_echo_enabled,
                setter=presenter.set_word_echo_enabled,
                prefs_key="enableEchoByWord",
                member_of=guilabels.ECHO_TYPING_ECHO,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.ECHO_SENTENCE,
                getter=presenter.get_sentence_echo_enabled,
                setter=presenter.set_sentence_echo_enabled,
                prefs_key="enableEchoBySentence",
                member_of=guilabels.ECHO_TYPING_ECHO,
            ),
        ]

        self._presenter = presenter
        super().__init__(guilabels.ECHO, controls, info_message=guilabels.ECHO_INFO)


@gsettings_registry.get_registry().gsettings_schema("org.gnome.Orca.TypingEcho", name="typing-echo")
class TypingEchoPresenter:
    """Provides typing echo support."""

    _SCHEMA = "typing-echo"

    def _get_setting(self, key: str, fallback: bool) -> bool:
        """Returns the dconf value for key, or fallback if not in dconf."""

        return gsettings_registry.get_registry().layered_lookup(
            self._SCHEMA, key, "b", fallback=fallback
        )

    def __init__(self) -> None:
        self._delayed_terminal_press: input_event.KeyboardEvent | None = None
        self._initialized: bool = False
        msg = "TYPING ECHO PRESENTER: Registering D-Bus commands."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        controller = dbus_service.get_remote_controller()
        controller.register_decorated_module("TypingEchoPresenter", self)

    def set_up_commands(self) -> None:
        """Sets up commands with CommandManager."""

        if self._initialized:
            return
        self._initialized = True

        manager = command_manager.get_manager()
        group_label = guilabels.KB_GROUP_DEFAULT

        manager.add_command(
            command_manager.KeyboardCommand(
                "cycleKeyEchoHandler",
                self.cycle_key_echo,
                group_label,
                cmdnames.CYCLE_KEY_ECHO,
                desktop_keybinding=None,
                laptop_keybinding=None,
            )
        )

        msg = "TYPING ECHO PRESENTER: Commands set up."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def create_preferences_grid(self) -> TypingEchoPreferencesGrid:
        """Returns the GtkGrid containing the Typing Echo preferences UI."""

        return TypingEchoPreferencesGrid(self)

    def get_typing_echo_preferences(self) -> tuple[TypingEchoPreference, ...]:
        """Return descriptors for all typing echo preferences."""

        return (
            TypingEchoPreference(
                "enableKeyEcho",
                guilabels.ECHO_ENABLE_KEY_ECHO,
                PreferenceCategory.PRIMARY,
                self.get_key_echo_enabled,
                self.set_key_echo_enabled,
            ),
            TypingEchoPreference(
                "enableAlphabeticKeys",
                guilabels.ECHO_ALPHABETIC_KEYS,
                PreferenceCategory.KEY,
                self.get_alphabetic_keys_enabled,
                self.set_alphabetic_keys_enabled,
            ),
            TypingEchoPreference(
                "enableNumericKeys",
                guilabels.ECHO_NUMERIC_KEYS,
                PreferenceCategory.KEY,
                self.get_numeric_keys_enabled,
                self.set_numeric_keys_enabled,
            ),
            TypingEchoPreference(
                "enablePunctuationKeys",
                guilabels.ECHO_PUNCTUATION_KEYS,
                PreferenceCategory.KEY,
                self.get_punctuation_keys_enabled,
                self.set_punctuation_keys_enabled,
            ),
            TypingEchoPreference(
                "enableSpace",
                guilabels.ECHO_SPACE,
                PreferenceCategory.KEY,
                self.get_space_enabled,
                self.set_space_enabled,
            ),
            TypingEchoPreference(
                "enableModifierKeys",
                guilabels.ECHO_MODIFIER_KEYS,
                PreferenceCategory.KEY,
                self.get_modifier_keys_enabled,
                self.set_modifier_keys_enabled,
            ),
            TypingEchoPreference(
                "enableFunctionKeys",
                guilabels.ECHO_FUNCTION_KEYS,
                PreferenceCategory.KEY,
                self.get_function_keys_enabled,
                self.set_function_keys_enabled,
            ),
            TypingEchoPreference(
                "enableActionKeys",
                guilabels.ECHO_ACTION_KEYS,
                PreferenceCategory.KEY,
                self.get_action_keys_enabled,
                self.set_action_keys_enabled,
            ),
            TypingEchoPreference(
                "enableNavigationKeys",
                guilabels.ECHO_NAVIGATION_KEYS,
                PreferenceCategory.KEY,
                self.get_navigation_keys_enabled,
                self.set_navigation_keys_enabled,
            ),
            TypingEchoPreference(
                "enableDiacriticalKeys",
                guilabels.ECHO_DIACRITICAL_KEYS,
                PreferenceCategory.KEY,
                self.get_diacritical_keys_enabled,
                self.set_diacritical_keys_enabled,
            ),
            TypingEchoPreference(
                "enableEchoByCharacter",
                guilabels.ECHO_CHARACTER,
                PreferenceCategory.TEXT,
                self.get_character_echo_enabled,
                self.set_character_echo_enabled,
            ),
            TypingEchoPreference(
                "enableEchoByWord",
                guilabels.ECHO_WORD,
                PreferenceCategory.TEXT,
                self.get_word_echo_enabled,
                self.set_word_echo_enabled,
            ),
            TypingEchoPreference(
                "enableEchoBySentence",
                guilabels.ECHO_SENTENCE,
                PreferenceCategory.TEXT,
                self.get_sentence_echo_enabled,
                self.set_sentence_echo_enabled,
            ),
        )

    def apply_typing_echo_preferences(
        self, updates: Iterable[tuple[TypingEchoPreference, bool]]
    ) -> dict[str, bool]:
        """Apply the provided preference values and return the saved mapping."""

        result: dict[str, bool] = {}
        for descriptor, value in updates:
            descriptor.setter(value)
            result[descriptor.prefs_key] = value
        return result

    @dbus_service.command
    def cycle_key_echo(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Cycle through the key echo levels."""

        tokens = [
            "TYPING ECHO PRESENTER: cycle_key_echo. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        (new_key, new_word, new_sentence) = (False, False, False)
        key = self.get_key_echo_enabled()
        word = self.get_word_echo_enabled()
        sentence = self.get_sentence_echo_enabled()

        if (key, word, sentence) == (False, False, False):
            (new_key, new_word, new_sentence) = (True, False, False)
            full = messages.KEY_ECHO_KEY_FULL
            brief = messages.KEY_ECHO_KEY_BRIEF
        elif (key, word, sentence) == (True, False, False):
            (new_key, new_word, new_sentence) = (False, True, False)
            full = messages.KEY_ECHO_WORD_FULL
            brief = messages.KEY_ECHO_WORD_BRIEF
        elif (key, word, sentence) == (False, True, False):
            (new_key, new_word, new_sentence) = (False, False, True)
            full = messages.KEY_ECHO_SENTENCE_FULL
            brief = messages.KEY_ECHO_SENTENCE_BRIEF
        elif (key, word, sentence) == (False, False, True):
            (new_key, new_word, new_sentence) = (True, True, False)
            full = messages.KEY_ECHO_KEY_AND_WORD_FULL
            brief = messages.KEY_ECHO_KEY_AND_WORD_BRIEF
        elif (key, word, sentence) == (True, True, False):
            (new_key, new_word, new_sentence) = (False, True, True)
            full = messages.KEY_ECHO_WORD_AND_SENTENCE_FULL
            brief = messages.KEY_ECHO_WORD_AND_SENTENCE_BRIEF
        else:
            (new_key, new_word, new_sentence) = (False, False, False)
            full = messages.KEY_ECHO_NONE_FULL
            brief = messages.KEY_ECHO_NONE_BRIEF

        self.set_key_echo_enabled(new_key)
        self.set_word_echo_enabled(new_word)
        self.set_sentence_echo_enabled(new_sentence)
        if script is not None and notify_user:
            presentation_manager.get_manager().present_message(full, brief)
        return True

    @gsettings_registry.get_registry().gsetting(
        key="key-echo",
        schema="typing-echo",
        gtype="b",
        default=True,
        summary="Enable key echo",
        settings_key="enableKeyEcho",
    )
    @dbus_service.getter
    def get_key_echo_enabled(self) -> bool:
        """Returns whether echo of key presses is enabled. See also get_character_echo_enabled."""

        return self._get_setting("key-echo", settings.enableKeyEcho)

    @dbus_service.setter
    def set_key_echo_enabled(self, value: bool) -> bool:
        """Sets whether echo of key presses is enabled. See also set_character_echo_enabled."""

        msg = f"TYPING ECHO PRESENTER: Setting enable key echo to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(self._SCHEMA, "key-echo", value)
        return True

    @gsettings_registry.get_registry().gsetting(
        key="character-echo",
        schema="typing-echo",
        gtype="b",
        default=False,
        summary="Echo inserted characters",
        settings_key="enableEchoByCharacter",
    )
    @dbus_service.getter
    def get_character_echo_enabled(self) -> bool:
        """Returns whether echo of inserted characters is enabled."""

        return self._get_setting("character-echo", settings.enableEchoByCharacter)

    @dbus_service.setter
    def set_character_echo_enabled(self, value: bool) -> bool:
        """Sets whether echo of inserted characters is enabled."""

        msg = f"TYPING ECHO PRESENTER: Setting enable character echo to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(self._SCHEMA, "character-echo", value)
        return True

    @gsettings_registry.get_registry().gsetting(
        key="word-echo",
        schema="typing-echo",
        gtype="b",
        default=False,
        summary="Echo completed words",
        settings_key="enableEchoByWord",
    )
    @dbus_service.getter
    def get_word_echo_enabled(self) -> bool:
        """Returns whether word echo is enabled."""

        return self._get_setting("word-echo", settings.enableEchoByWord)

    @dbus_service.setter
    def set_word_echo_enabled(self, value: bool) -> bool:
        """Sets whether word echo is enabled."""

        msg = f"TYPING ECHO PRESENTER: Setting enable word echo to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(self._SCHEMA, "word-echo", value)
        return True

    @gsettings_registry.get_registry().gsetting(
        key="sentence-echo",
        schema="typing-echo",
        gtype="b",
        default=False,
        summary="Echo completed sentences",
        settings_key="enableEchoBySentence",
    )
    @dbus_service.getter
    def get_sentence_echo_enabled(self) -> bool:
        """Returns whether sentence echo is enabled."""

        return self._get_setting("sentence-echo", settings.enableEchoBySentence)

    @dbus_service.setter
    def set_sentence_echo_enabled(self, value: bool) -> bool:
        """Sets whether sentence echo is enabled."""

        msg = f"TYPING ECHO PRESENTER: Setting enable sentence echo to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(self._SCHEMA, "sentence-echo", value)
        return True

    @gsettings_registry.get_registry().gsetting(
        key="alphabetic-keys",
        schema="typing-echo",
        gtype="b",
        default=True,
        summary="Echo alphabetic keys",
        settings_key="enableAlphabeticKeys",
    )
    @dbus_service.getter
    def get_alphabetic_keys_enabled(self) -> bool:
        """Returns whether alphabetic keys will be echoed when key echo is enabled."""

        return self._get_setting("alphabetic-keys", settings.enableAlphabeticKeys)

    @dbus_service.setter
    def set_alphabetic_keys_enabled(self, value: bool) -> bool:
        """Sets whether alphabetic keys will be echoed when key echo is enabled."""

        msg = f"TYPING ECHO PRESENTER: Setting enable alphabetic keys to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(self._SCHEMA, "alphabetic-keys", value)
        return True

    @gsettings_registry.get_registry().gsetting(
        key="numeric-keys",
        schema="typing-echo",
        gtype="b",
        default=True,
        summary="Echo numeric keys",
        settings_key="enableNumericKeys",
    )
    @dbus_service.getter
    def get_numeric_keys_enabled(self) -> bool:
        """Returns whether numeric keys will be echoed when key echo is enabled."""

        return self._get_setting("numeric-keys", settings.enableNumericKeys)

    @dbus_service.setter
    def set_numeric_keys_enabled(self, value: bool) -> bool:
        """Sets whether numeric keys will be echoed when key echo is enabled."""

        msg = f"TYPING ECHO PRESENTER: Setting enable numeric keys to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(self._SCHEMA, "numeric-keys", value)
        return True

    @gsettings_registry.get_registry().gsetting(
        key="punctuation-keys",
        schema="typing-echo",
        gtype="b",
        default=True,
        summary="Echo punctuation keys",
        settings_key="enablePunctuationKeys",
    )
    @dbus_service.getter
    def get_punctuation_keys_enabled(self) -> bool:
        """Returns whether punctuation keys will be echoed when key echo is enabled."""

        return self._get_setting("punctuation-keys", settings.enablePunctuationKeys)

    @dbus_service.setter
    def set_punctuation_keys_enabled(self, value: bool) -> bool:
        """Sets whether punctuation keys will be echoed when key echo is enabled."""

        msg = f"TYPING ECHO PRESENTER: Setting enable punctuation keys to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(self._SCHEMA, "punctuation-keys", value)
        return True

    @gsettings_registry.get_registry().gsetting(
        key="space",
        schema="typing-echo",
        gtype="b",
        default=True,
        summary="Echo space key",
        settings_key="enableSpace",
    )
    @dbus_service.getter
    def get_space_enabled(self) -> bool:
        """Returns whether space key will be echoed when key echo is enabled."""

        return self._get_setting("space", settings.enableSpace)

    @dbus_service.setter
    def set_space_enabled(self, value: bool) -> bool:
        """Sets whether space key will be echoed when key echo is enabled."""

        msg = f"TYPING ECHO PRESENTER: Setting enable space to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(self._SCHEMA, "space", value)
        return True

    @gsettings_registry.get_registry().gsetting(
        key="modifier-keys",
        schema="typing-echo",
        gtype="b",
        default=True,
        summary="Echo modifier keys",
        settings_key="enableModifierKeys",
    )
    @dbus_service.getter
    def get_modifier_keys_enabled(self) -> bool:
        """Returns whether modifier keys will be echoed when key echo is enabled."""

        return self._get_setting("modifier-keys", settings.enableModifierKeys)

    @dbus_service.setter
    def set_modifier_keys_enabled(self, value: bool) -> bool:
        """Sets whether modifier keys will be echoed when key echo is enabled."""

        msg = f"TYPING ECHO PRESENTER: Setting enable modifier keys to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(self._SCHEMA, "modifier-keys", value)
        return True

    @gsettings_registry.get_registry().gsetting(
        key="function-keys",
        schema="typing-echo",
        gtype="b",
        default=True,
        summary="Echo function keys",
        settings_key="enableFunctionKeys",
    )
    @dbus_service.getter
    def get_function_keys_enabled(self) -> bool:
        """Returns whether function keys will be echoed when key echo is enabled."""

        return self._get_setting("function-keys", settings.enableFunctionKeys)

    @dbus_service.setter
    def set_function_keys_enabled(self, value: bool) -> bool:
        """Sets whether function keys will be echoed when key echo is enabled."""

        msg = f"TYPING ECHO PRESENTER: Setting enable function keys to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(self._SCHEMA, "function-keys", value)
        return True

    @gsettings_registry.get_registry().gsetting(
        key="action-keys",
        schema="typing-echo",
        gtype="b",
        default=True,
        summary="Echo action keys",
        settings_key="enableActionKeys",
    )
    @dbus_service.getter
    def get_action_keys_enabled(self) -> bool:
        """Returns whether action keys will be echoed when key echo is enabled."""

        return self._get_setting("action-keys", settings.enableActionKeys)

    @dbus_service.setter
    def set_action_keys_enabled(self, value: bool) -> bool:
        """Sets whether action keys will be echoed when key echo is enabled."""

        msg = f"TYPING ECHO PRESENTER: Setting enable action keys to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(self._SCHEMA, "action-keys", value)
        return True

    @gsettings_registry.get_registry().gsetting(
        key="navigation-keys",
        schema="typing-echo",
        gtype="b",
        default=False,
        summary="Echo navigation keys",
        settings_key="enableNavigationKeys",
    )
    @dbus_service.getter
    def get_navigation_keys_enabled(self) -> bool:
        """Returns whether navigation keys will be echoed when key echo is enabled."""

        return self._get_setting("navigation-keys", settings.enableNavigationKeys)

    @dbus_service.setter
    def set_navigation_keys_enabled(self, value: bool) -> bool:
        """Sets whether navigation keys will be echoed when key echo is enabled."""

        msg = f"TYPING ECHO PRESENTER: Setting enable navigation keys to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(self._SCHEMA, "navigation-keys", value)
        return True

    @gsettings_registry.get_registry().gsetting(
        key="diacritical-keys",
        schema="typing-echo",
        gtype="b",
        default=False,
        summary="Echo diacritical keys",
        settings_key="enableDiacriticalKeys",
    )
    @dbus_service.getter
    def get_diacritical_keys_enabled(self) -> bool:
        """Returns whether diacritical keys will be echoed when key echo is enabled."""

        return self._get_setting("diacritical-keys", settings.enableDiacriticalKeys)

    @dbus_service.setter
    def set_diacritical_keys_enabled(self, value: bool) -> bool:
        """Sets whether diacritical keys will be echoed when key echo is enabled."""

        msg = f"TYPING ECHO PRESENTER: Setting enable diacritical keys to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(self._SCHEMA, "diacritical-keys", value)
        return True

    @dbus_service.getter
    def get_locking_keys_presented(self) -> bool:
        """Returns whether locking keys are presented."""

        # TODO - JD: It turns out there's no UI for this setting, so it defaults to None.

        result = settings.presentLockingKeys
        if result is not None:
            return result

        return not speech_presenter.get_presenter().get_only_speak_displayed_text()

    @dbus_service.setter
    def set_locking_keys_presented(self, value: bool | None) -> bool:
        """Sets whether locking keys are presented."""

        msg = f"TYPING ECHO PRESENTER: Setting present locking keys to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings.presentLockingKeys = value
        return True

    def echo_previous_sentence(self, script: default.Script, obj: Atspi.Accessible) -> bool:
        """Speaks the sentence prior to the caret if at a sentence boundary."""

        if not self.get_sentence_echo_enabled():
            return False

        offset = AXText.get_caret_offset(obj)
        char, start = AXText.get_character_at_offset(obj, offset - 1)[0:-1]
        previous_char, previous_start = AXText.get_character_at_offset(obj, start - 1)[0:-1]
        if not (char in string.whitespace + "\u00a0" and previous_char in "!.?:;"):
            return False

        sentence = AXText.get_sentence_at_offset(obj, previous_start)[0]
        if not sentence:
            msg = "TYPING ECHO PRESENTER: At a sentence boundary, but no sentence found."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        voice = script.speech_generator.voice(obj=obj, string=sentence)
        presentation_manager.get_manager().speak_message(sentence, voice, obj=obj)
        return True

    def echo_previous_word(self, script: default.Script, obj: Atspi.Accessible) -> bool:
        """Speaks the word prior to the caret if at a word boundary."""

        if not self.get_word_echo_enabled():
            return False

        offset = AXText.get_caret_offset(obj)
        if offset == -1:
            offset = AXText.get_character_count(obj)

        if offset <= 0:
            return False

        # If the previous character is not a word delimiter, there's nothing to echo.
        prev_char, prev_start = AXText.get_character_at_offset(obj, offset - 1)[0:-1]
        if prev_char not in string.punctuation + string.whitespace + "\u00a0":
            return False

        # Two back-to-back delimiters should not result in a re-echo.
        prev_char, prev_start = AXText.get_character_at_offset(obj, prev_start - 1)[0:-1]
        if prev_char in string.punctuation + string.whitespace + "\u00a0":
            return False

        word = AXText.get_word_at_offset(obj, prev_start)[0]
        if not word:
            return False

        voice = script.speech_generator.voice(obj=obj, string=word)
        presentation_manager.get_manager().speak_message(word, voice, obj=obj)
        return True

    # pylint: disable-next=too-many-statements
    def should_echo_keyboard_event(self, event: input_event.KeyboardEvent) -> bool:
        """Returns whether the given keyboard event should be echoed."""

        should_obscure = event.should_obscure()
        name = event.get_key_name() if not should_obscure else "(obscured)"
        msg = f"TYPING ECHO PRESENTER: should_echo_keyboard_event: '{name}'?"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        if not event.is_pressed_key():
            msg = "TYPING ECHO PRESENTER: Not echoing keyboard event: key is not pressed."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        key_echo_enabled = self.get_key_echo_enabled()

        if event.is_orca_modifier():
            click_count = event.get_click_count()
            if click_count == 2:
                msg = "TYPING ECHO PRESENTER: Echoing Orca modifier double-click."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return True

            result = click_count == 1 and key_echo_enabled and self.get_modifier_keys_enabled()
            msg = f"TYPING ECHO PRESENTER: Echoing modifier Orca modifier event: {result}."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return result

        # Historically we had only filtered out Orca-modified events. But it seems strange to
        # treat the Orca modifier as special. A change to make Orca-modified events echoed in
        # the same fashion as other modified events received some negative feedback, specifically
        # in relation to flat review commands in laptop layout. Feedback regarding whether any
        # command-like modifier should result in no echo has thus far ranged from yes to
        # it's "not disturbing" to hear echo with other modifiers. Given the lack of demand
        # for echo with modifiers, treat all command modifiers the same and suppress echo.
        if event.is_alt_control_or_orca_modified():
            msg = "TYPING ECHO PRESENTER: Not echoing keyboard event due to modifier."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if self.is_character_echoable(event):
            msg = "TYPING ECHO PRESENTER: Not echoing keyboard event: is character echoable."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if event.is_locking_key():
            result = self.get_locking_keys_presented()
            msg = f"TYPING ECHO PRESENTER: Echoing locking keyboard event: {result}."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return result

        if not key_echo_enabled:
            msg = "TYPING ECHO PRESENTER: Not echoing keyboard event: key echo is not enabled."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if event.is_navigation_key():
            result = self.get_navigation_keys_enabled()
            msg = f"TYPING ECHO PRESENTER: Echoing navigation keyboard event: {result}."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return result

        if event.is_action_key():
            result = self.get_action_keys_enabled()
            msg = f"TYPING ECHO PRESENTER: Echoing action keyboard event: {result}."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return result

        if event.is_modifier_key():
            result = self.get_modifier_keys_enabled()
            msg = f"TYPING ECHO PRESENTER: Echoing modifier keyboard event: {result}."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return result

        if event.is_function_key():
            result = self.get_function_keys_enabled()
            msg = f"TYPING ECHO PRESENTER: Echoing function keyboard event: {result}."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return result

        if AXUtilities.is_password_text(event.get_object()) and event.should_obscure():
            msg = "TYPING ECHO PRESENTER: Not echoing keyboard event: is password text."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if event.is_diacritical_key():
            result = self.get_diacritical_keys_enabled()
            msg = f"TYPING ECHO PRESENTER: Echoing diacritical keyboard event: {result}."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return result

        if event.is_alphabetic_key():
            result = self.get_alphabetic_keys_enabled()
            msg = f"TYPING ECHO PRESENTER: Echoing alphabetic keyboard event: {result}."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return result

        if event.is_numeric_key():
            result = self.get_numeric_keys_enabled()
            msg = f"TYPING ECHO PRESENTER: Echoing numeric keyboard event: {result}."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return result

        if event.is_punctuation_key():
            result = self.get_punctuation_keys_enabled()
            msg = f"TYPING ECHO PRESENTER: Echoing punctuation keyboard event: {result}."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return result

        if event.is_space():
            result = self.get_space_enabled() or self.get_character_echo_enabled()
            msg = f"TYPING ECHO PRESENTER: Echoing space keyboard event: {result}."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return result

        msg = "TYPING ECHO PRESENTER: Not echoing keyboard event: key type unknown."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return False

    def is_character_echoable(self, event: input_event.KeyboardEvent) -> bool:
        """Returns True if the script will echo this event as part of character echo."""

        if not self.get_character_echo_enabled():
            return False

        if event.is_alt_control_or_orca_modified():
            msg = "TYPING ECHO PRESENTER: Not character echoable due to modifier."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if not event.is_printable_key():
            msg = "TYPING ECHO PRESENTER: Not character echoable, is not printable key."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        obj = event.get_object()
        if AXUtilities.is_password_text(obj):
            msg = "TYPING ECHO PRESENTER: Not character echoable, is password text."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if AXUtilities.is_editable(obj) or AXUtilities.is_terminal(obj):
            msg = "TYPING ECHO PRESENTER: Character echoable, is editable or terminal."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        msg = "TYPING ECHO PRESENTER: Not character echoable, no reason to echo."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return False

    def echo_delayed_terminal_press(self, _script: default.Script, event: Atspi.Event) -> None:
        """Echoes a previously delayed terminal key press if it matches the inserted text."""

        if self._delayed_terminal_press is None:
            msg = "TYPING ECHO PRESENTER: No rejected terminal press to echo."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        if self._delayed_terminal_press.get_object() != event.source:
            msg = "TYPING ECHO PRESENTER: Delayed terminal press does not match event source."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        character = self._delayed_terminal_press.get_key_name().lower()
        if event.any_data.lower() == character:
            msg = "TYPING ECHO PRESENTER: Echoing delayed terminal press."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            presentation_manager.get_manager().present_key_event(self._delayed_terminal_press)
            self._delayed_terminal_press = None

    def echo_keyboard_event(self, script: default.Script, event: input_event.KeyboardEvent) -> None:
        """Presents the KeyboardEvent event."""

        if not event.is_pressed_key():
            script.utilities.clear_cached_command_state_deprecated()
            return

        self._delayed_terminal_press = None
        if not self.should_echo_keyboard_event(event):
            return

        obj = event.get_object()
        if AXUtilities.is_terminal(obj) and event.is_printable_key():
            # We have no reliable way of knowing a password is being entered into a terminal --
            # other than the fact that the text typed isn't there. Before we waited for the
            # release event and echoed that. But that is laggy. So delay presentation until we
            # see the text appear. If it doesn't appear, we never echo it.
            msg = "TYPING ECHO PRESENTER: Delaying terminal key press echo."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._delayed_terminal_press = event
            return

        if locking_state_string := event.get_locking_state_string():
            keyname = event.get_key_name()
            msg = f"{keyname} {locking_state_string}"
            presentation_manager.get_manager().present_braille_message(msg)

        presentation_manager.get_manager().present_key_event(event)


_presenter: TypingEchoPresenter = TypingEchoPresenter()


def get_presenter() -> TypingEchoPresenter:
    """Returns the Typing Echo Presenter"""

    return _presenter
