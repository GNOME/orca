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
# pylint:disable=too-many-branches
# pylint:disable=too-many-return-statements

"""Provides typing echo support."""

# This must be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc." \
                "Copyright (c) 2011-2025 Igalia, S.L."
__license__   = "LGPL"

import string
from typing import TYPE_CHECKING

from . import braille
from . import cmdnames
from . import dbus_service
from . import debug
from . import input_event
from . import keybindings
from . import messages
from . import settings
from . import settings_manager
from . import speech
from .ax_text import AXText
from .ax_utilities import AXUtilities

if TYPE_CHECKING:
    import gi
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

    from .scripts import default

class TypingEchoPresenter:
    """Provides typing echo support."""

    def __init__(self) -> None:
        self._handlers: dict[str, input_event.InputEventHandler] = self.get_handlers(True)
        self._bindings: keybindings.KeyBindings = keybindings.KeyBindings()
        self._last_indentation_description: str = ""
        self._last_error_description: str = ""

        msg = "TYPING ECHO PRESENTER: Registering D-Bus commands."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        controller = dbus_service.get_remote_controller()
        controller.register_decorated_module("TypingEchoPresenter", self)

    def get_bindings(
        self, refresh: bool = False, is_desktop: bool = True
    ) -> keybindings.KeyBindings:
        """Returns the typing echo presenter keybindings."""

        if refresh:
            msg = f"TYPING ECHO PRESENTER: Refreshing bindings.  Is desktop: {is_desktop}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._bindings.remove_key_grabs("TYPING ECHO PRESENTER: Refreshing bindings.")
            self._setup_bindings()
        elif self._bindings.is_empty():
            self._setup_bindings()

        return self._bindings

    def get_handlers(self, refresh: bool = False) -> dict[str, input_event.InputEventHandler]:
        """Returns the typing echo presenter handlers."""

        if refresh:
            msg = "TYPING ECHO PRESENTER: Refreshing handlers."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._setup_handlers()

        return self._handlers

    def _setup_handlers(self) -> None:
        """Sets up the typing echo input event handlers."""

        self._handlers = {}

        self._handlers["cycleKeyEchoHandler"] = \
            input_event.InputEventHandler(
                self.cycle_key_echo,
                cmdnames.CYCLE_KEY_ECHO)

        msg = "TYPING ECHO PRESENTER: Handlers set up."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def _setup_bindings(self) -> None:
        """Sets up the typing echo key bindings."""

        self._bindings = keybindings.KeyBindings()

        self._bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["cycleKeyEchoHandler"]))

        msg = "TYPING ECHO PRESENTER: Bindings set up."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    @dbus_service.command
    def cycle_key_echo(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Cycle through the key echo levels."""

        tokens = ["TYPING ECHO PRESENTER: cycle_key_echo. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        manager = settings_manager.get_manager()
        (new_key, new_word, new_sentence) = (False, False, False)
        key = manager.get_setting("enableKeyEcho")
        word = manager.get_setting("enableEchoByWord")
        sentence = manager.get_setting("enableEchoBySentence")

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

        manager.set_setting("enableKeyEcho", new_key)
        manager.set_setting("enableEchoByWord", new_word)
        manager.set_setting("enableEchoBySentence", new_sentence)
        if script is not None and notify_user:
            script.present_message(full, brief)
        return True

    @dbus_service.getter
    def get_key_echo_enabled(self) -> bool:
        """Returns whether echo of key presses is enabled. See also get_character_echo_enabled."""

        return settings_manager.get_manager().get_setting("enableKeyEcho")

    @dbus_service.setter
    def set_key_echo_enabled(self, value: bool) -> bool:
        """Sets whether echo of key pressses is enabled. See also set_character_echo_enabled."""

        msg = f"TYPING ECHO PRESENTER: Setting enable key echo to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("enableKeyEcho", value)
        return True

    @dbus_service.getter
    def get_character_echo_enabled(self) -> bool:
        """Returns whether echo of inserted characters is enabled."""

        return settings_manager.get_manager().get_setting("enableEchoByCharacter")

    @dbus_service.setter
    def set_character_echo_enabled(self, value: bool) -> bool:
        """Sets whether echo of inserted characters is enabled."""

        msg = f"TYPING ECHO PRESENTER: Setting enable character echo to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("enableEchoByCharacter", value)
        return True

    @dbus_service.getter
    def get_word_echo_enabled(self) -> bool:
        """Returns whether word echo is enabled."""

        return settings_manager.get_manager().get_setting("enableEchoByWord")

    @dbus_service.setter
    def set_word_echo_enabled(self, value: bool) -> bool:
        """Sets whether word echo is enabled."""

        msg = f"TYPING ECHO PRESENTER: Setting enable word echo to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("enableEchoByWord", value)
        return True

    @dbus_service.getter
    def get_sentence_echo_enabled(self) -> bool:
        """Returns whether sentence echo is enabled."""

        return settings_manager.get_manager().get_setting("enableEchoBySentence")

    @dbus_service.setter
    def set_sentence_echo_enabled(self, value: bool) -> bool:
        """Sets whether sentence echo is enabled."""

        msg = f"TYPING ECHO PRESENTER: Setting enable sentence echo to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("enableEchoBySentence", value)
        return True

    @dbus_service.getter
    def get_alphabetic_keys_enabled(self) -> bool:
        """Returns whether alphabetic keys will be echoed when key echo is enabled."""

        return settings_manager.get_manager().get_setting("enableAlphabeticKeys")

    @dbus_service.setter
    def set_alphabetic_keys_enabled(self, value: bool) -> bool:
        """Sets whether alphabetic keys will be echoed when key echo is enabled."""

        msg = f"TYPING ECHO PRESENTER: Setting enable alphabetic keys to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("enableAlphabeticKeys", value)
        return True

    @dbus_service.getter
    def get_numeric_keys_enabled(self) -> bool:
        """Returns whether numeric keys will be echoed when key echo is enabled."""

        return settings_manager.get_manager().get_setting("enableNumericKeys")

    @dbus_service.setter
    def set_numeric_keys_enabled(self, value: bool) -> bool:
        """Sets whether numeric keys will be echoed when key echo is enabled."""

        msg = f"TYPING ECHO PRESENTER: Setting enable numeric keys to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("enableNumericKeys", value)
        return True

    @dbus_service.getter
    def get_punctuation_keys_enabled(self) -> bool:
        """Returns whether punctuation keys will be echoed when key echo is enabled."""

        return settings_manager.get_manager().get_setting("enablePunctuationKeys")

    @dbus_service.setter
    def set_punctuation_keys_enabled(self, value: bool) -> bool:
        """Sets whether punctuation keys will be echoed when key echo is enabled."""

        msg = f"TYPING ECHO PRESENTER: Setting enable punctuation keys to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("enablePunctuationKeys", value)
        return True

    @dbus_service.getter
    def get_space_enabled(self) -> bool:
        """Returns whether space key will be echoed when key echo is enabled."""

        return settings_manager.get_manager().get_setting("enableSpace")

    @dbus_service.setter
    def set_space_enabled(self, value: bool) -> bool:
        """Sets whether space key will be echoed when key echo is enabled."""

        msg = f"TYPING ECHO PRESENTER: Setting enable space to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("enableSpace", value)
        return True

    @dbus_service.getter
    def get_modifier_keys_enabled(self) -> bool:
        """Returns whether modifier keys will be echoed when key echo is enabled."""

        return settings_manager.get_manager().get_setting("enableModifierKeys")

    @dbus_service.setter
    def set_modifier_keys_enabled(self, value: bool) -> bool:
        """Sets whether modifier keys will be echoed when key echo is enabled."""

        msg = f"TYPING ECHO PRESENTER: Setting enable modifier keys to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("enableModifierKeys", value)
        return True

    @dbus_service.getter
    def get_function_keys_enabled(self) -> bool:
        """Returns whether function keys will be echoed when key echo is enabled."""

        return settings_manager.get_manager().get_setting("enableFunctionKeys")

    @dbus_service.setter
    def set_function_keys_enabled(self, value: bool) -> bool:
        """Sets whether function keys will be echoed when key echo is enabled."""

        msg = f"TYPING ECHO PRESENTER: Setting enable function keys to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("enableFunctionKeys", value)
        return True

    @dbus_service.getter
    def get_action_keys_enabled(self) -> bool:
        """Returns whether action keys will be echoed when key echo is enabled."""

        return settings_manager.get_manager().get_setting("enableActionKeys")

    @dbus_service.setter
    def set_action_keys_enabled(self, value: bool) -> bool:
        """Sets whether action keys will be echoed when key echo is enabled."""

        msg = f"TYPING ECHO PRESENTER: Setting enable action keys to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("enableActionKeys", value)
        return True

    @dbus_service.getter
    def get_navigation_keys_enabled(self) -> bool:
        """Returns whether navigation keys will be echoed when key echo is enabled."""

        return settings_manager.get_manager().get_setting("enableNavigationKeys")

    @dbus_service.setter
    def set_navigation_keys_enabled(self, value: bool) -> bool:
        """Sets whether navigation keys will be echoed when key echo is enabled."""

        msg = f"TYPING ECHO PRESENTER: Setting enable navigation keys to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("enableNavigationKeys", value)
        return True

    @dbus_service.getter
    def get_diacritical_keys_enabled(self) -> bool:
        """Returns whether diacritical keys will be echoed when key echo is enabled."""

        return settings_manager.get_manager().get_setting("enableDiacriticalKeys")

    @dbus_service.setter
    def set_diacritical_keys_enabled(self, value: bool) -> bool:
        """Sets whether diacritical keys will be echoed when key echo is enabled."""

        msg = f"TYPING ECHO PRESENTER: Setting enable diacritical keys to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("enableDiacriticalKeys", value)
        return True

    @dbus_service.getter
    def get_locking_keys_presented(self) -> bool:
        """Returns whether locking keys are presented."""

        # TODO - JD: It turns out there's no UI for this setting, so it defaults to None.

        manager = settings_manager.get_manager()
        result = manager.get_setting("presentLockingKeys")
        if result is not None:
            return result

        return not manager.get_setting("onlySpeakDisplayedText")

    @dbus_service.setter
    def set_locking_keys_presented(self, value: bool | None) -> bool:
        """Sets whether locking keys are presented."""

        msg = f"TYPING ECHO PRESENTER: Setting present locking keys to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("presentLockingKeys", value)
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
        script.speak_message(sentence, voice, obj=obj)
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
        script.speak_message(word, voice, obj=obj)
        return True

    # pylint: disable-next=too-many-statements
    def should_echo_keyboard_event(self, event: input_event.KeyboardEvent) -> bool:
        """Returns whether the given keyboard event should be echoed."""

        name = event.get_key_name()
        msg = f"TYPING ECHO PRESENTER: should_echo_keyboard_event: '{name}'?"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        if not event.is_pressed_key():
            msg = "TYPING ECHO PRESENTER: Not echoing keyboard event: key is not pressed."
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

        if not self.get_key_echo_enabled():
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

        if AXUtilities.is_password_text(event.get_object()):
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

    def echo_keyboard_event(self, script: default.Script, event: input_event.KeyboardEvent) -> None:
        """Presents the KeyboardEvent event."""

        if script.get_sleep_mode_manager().is_active_for_app(script.app):
            msg = "TYPING ECHO PRESENTER: Ignoring keyboard event, sleep mode active."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        obj = event.get_object()
        if AXUtilities.is_terminal(obj) and event.is_printable_key() and event.is_pressed_key():
            # We have no reliable way of knowing a password is being entered into
            # a terminal -- other than the fact that the text typed isn't there.
            char, start = AXText.get_character_at_offset(obj)[0:2]
            prev_char = AXText.get_character_at_offset(obj, start - 1)[0]
            name = event.get_key_name()
            if name not in [prev_char, " ", char]:
                msg = "TYPING ECHO PRESENTER: Possible password entry in terminal."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return

        if not event.is_pressed_key():
            script.utilities.clear_cached_command_state_deprecated()

        if not self.should_echo_keyboard_event(event):
            return

        if locking_state_string := event.get_locking_state_string():
            keyname = event.get_key_name()
            msg = f"{keyname} {locking_state_string}"
            braille.displayMessage(msg, flashTime=settings.brailleFlashTime)

        orca_modifier_pressed = event.is_orca_modifier() and event.is_pressed_key()
        if self.is_character_echoable(event) and not orca_modifier_pressed:
            return

        msg = "TYPING ECHO PRESENTER: Presenting keyboard event"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        key_name = None
        if event.is_printable_key():
            key_name = event.get_key_name()

        voice = script.speech_generator.voice(string=key_name)
        speech.speak_key_event(event, voice[0] if voice else None)

_presenter: TypingEchoPresenter = TypingEchoPresenter()

def get_presenter() -> TypingEchoPresenter:
    """Returns the Typing Echo Presenter"""

    return _presenter
