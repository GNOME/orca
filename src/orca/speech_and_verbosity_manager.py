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

"""Configures speech and verbosity settings and adjusts strings accordingly."""

# This must be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc." \
                "Copyright (c) 2016-2025 Igalia, S.L."
__license__   = "LGPL"

import re
import string
from typing import Optional, TYPE_CHECKING

from . import cmdnames
from . import debug
from . import dbus_service
from . import focus_manager
from . import input_event
from . import keybindings
from . import mathsymbols
from . import messages
from . import object_properties
from . import pronunciation_dict
from . import settings
from . import settings_manager
from . import speech
from .ax_hypertext import AXHypertext
from .ax_object import AXObject
from .ax_table import AXTable
from .ax_text import AXText
from .ax_utilities import AXUtilities

if TYPE_CHECKING:
    import gi
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

    from .scripts import default
    from .speechserver import SpeechServer

class SpeechAndVerbosityManager:
    """Configures speech and verbosity settings and adjusts strings accordingly."""

    def __init__(self) -> None:
        self._handlers: dict[str, input_event.InputEventHandler] = self.get_handlers(True)
        self._bindings: keybindings.KeyBindings = keybindings.KeyBindings()
        self._last_indentation_description: str = ""
        self._last_error_description: str = ""

        msg = "SPEECH AND VERBOSITY MANAGER: Registering D-Bus commands."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        controller = dbus_service.get_remote_controller()
        controller.register_decorated_module("SpeechAndVerbosityManager", self)

    def get_bindings(
        self, refresh: bool = False, is_desktop: bool = True
    ) -> keybindings.KeyBindings:
        """Returns the speech and verbosity manager keybindings."""

        if refresh:
            msg = f"SPEECH AND VERBOSITY MANAGER: Refreshing bindings.  Is desktop: {is_desktop}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._setup_bindings()
        elif self._bindings.is_empty():
            self._setup_bindings()

        return self._bindings

    def get_handlers(self, refresh: bool = False) -> dict[str, input_event.InputEventHandler]:
        """Returns the speech and verbosity manager handlers."""

        if refresh:
            msg = "SPEECH AND VERBOSITY MANAGER: Refreshing handlers."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._setup_handlers()

        return self._handlers

    def _setup_handlers(self) -> None:
        """Sets up the speech and verbosity input event handlers."""

        self._handlers = {}

        self._handlers["cycleCapitalizationStyleHandler"] = \
            input_event.InputEventHandler(
                self.cycle_capitalization_style,
                cmdnames.CYCLE_CAPITALIZATION_STYLE)

        self._handlers["cycleSpeakingPunctuationLevelHandler"] = \
            input_event.InputEventHandler(
                self.cycle_punctuation_level,
                cmdnames.CYCLE_PUNCTUATION_LEVEL)

        self._handlers["cycleSynthesizerHandler"] = \
            input_event.InputEventHandler(
                self.cycle_synthesizer,
                cmdnames.CYCLE_SYNTHESIZER)

        self._handlers["cycleKeyEchoHandler"] = \
            input_event.InputEventHandler(
                self.cycle_key_echo,
                cmdnames.CYCLE_KEY_ECHO)

        self._handlers["changeNumberStyleHandler"] = \
            input_event.InputEventHandler(
                self.change_number_style,
                cmdnames.CHANGE_NUMBER_STYLE)

        self._handlers["toggleSilenceSpeechHandler"] = \
            input_event.InputEventHandler(
                self.toggle_speech,
                cmdnames.TOGGLE_SPEECH)

        self._handlers["toggleSpeechVerbosityHandler"] = \
            input_event.InputEventHandler(
                self.toggle_verbosity,
                cmdnames.TOGGLE_SPEECH_VERBOSITY)

        self._handlers["toggleSpeakingIndentationJustificationHandler"] = \
            input_event.InputEventHandler(
                self.toggle_indentation_and_justification,
                cmdnames.TOGGLE_SPOKEN_INDENTATION_AND_JUSTIFICATION)

        self._handlers["toggleTableCellReadModeHandler"] = \
            input_event.InputEventHandler(
                self.toggle_table_cell_reading_mode,
                cmdnames.TOGGLE_TABLE_CELL_READ_MODE)

        self._handlers["decreaseSpeechRateHandler"] = \
            input_event.InputEventHandler(
                self.decrease_rate,
                cmdnames.DECREASE_SPEECH_RATE)

        self._handlers["increaseSpeechRateHandler"] = \
            input_event.InputEventHandler(
                self.increase_rate,
                cmdnames.INCREASE_SPEECH_RATE)

        self._handlers["decreaseSpeechPitchHandler"] = \
            input_event.InputEventHandler(
                self.decrease_pitch,
                cmdnames.DECREASE_SPEECH_PITCH)

        self._handlers["increaseSpeechPitchHandler"] = \
            input_event.InputEventHandler(
                self.increase_pitch,
                cmdnames.INCREASE_SPEECH_PITCH)

        self._handlers["decreaseSpeechVolumeHandler"] = \
            input_event.InputEventHandler(
                self.decrease_volume,
                cmdnames.DECREASE_SPEECH_VOLUME)

        self._handlers["increaseSpeechVolumeHandler"] = \
            input_event.InputEventHandler(
                self.increase_volume,
                cmdnames.INCREASE_SPEECH_VOLUME)

        msg = "SPEECH AND VERBOSITY MANAGER: Handlers set up."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def _setup_bindings(self) -> None:
        """Sets up the speech and verbosity key bindings."""

        self._bindings = keybindings.KeyBindings()

        self._bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["cycleCapitalizationStyleHandler"]))

        self._bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["cycleSpeakingPunctuationLevelHandler"]))

        self._bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["cycleSynthesizerHandler"]))

        self._bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["cycleKeyEchoHandler"]))

        self._bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["changeNumberStyleHandler"]))

        self._bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["decreaseSpeechRateHandler"]))

        self._bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["increaseSpeechRateHandler"]))

        self._bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["decreaseSpeechPitchHandler"]))

        self._bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["increaseSpeechPitchHandler"]))

        self._bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["decreaseSpeechVolumeHandler"]))

        self._bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["increaseSpeechVolumeHandler"]))

        self._bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["toggleSpeakingIndentationJustificationHandler"]))

        self._bindings.add(
            keybindings.KeyBinding(
                "s",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers["toggleSilenceSpeechHandler"]))

        self._bindings.add(
            keybindings.KeyBinding(
                "v",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers["toggleSpeechVerbosityHandler"]))

        self._bindings.add(
            keybindings.KeyBinding(
                "F11",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers["toggleTableCellReadModeHandler"]))

        msg = "SPEECH AND VERBOSITY MANAGER: Bindings set up."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def _get_server(self) -> Optional[SpeechServer]:
        result = speech.get_speech_server()
        tokens = ["SPEECH AND VERBOSITY MANAGER: Speech server is", result]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    def get_current_speech_server_info(self) -> tuple[str, str]:
        """Returns the name and ID of the current speech server."""

        # TODO - JD: The result is not in sync with the current output module. Should it be?
        server = self._get_server()
        if server is None:
            return ("", "")

        server_name, server_id = server.get_info()
        msg = f"SPEECH AND VERBOSITY MANAGER: Speech server info: {server_name}, {server_id}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return server_name, server_id

    def check_speech_setting(self) -> None:
        """Checks the speech setting and initializes speech if necessary."""

        manager = settings_manager.get_manager()
        if not manager.get_setting("enableSpeech"):
            msg = "SPEECH AND VERBOSITY MANAGER: Speech is not enabled. Shutting down speech."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self.shutdown_speech()
            return

        msg = "SPEECH AND VERBOSITY MANAGER: Speech is enabled."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self.start_speech()

    @dbus_service.command
    def start_speech(
        self,
        script: Optional[default.Script] = None,
        event: Optional[input_event.InputEvent] = None,
        notify_user: bool = False
    ) -> bool:
        """Starts the speech server."""

        tokens = ["SPEECH AND VERBOSITY MANAGER: start_speech. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        speech.init()
        return True

    @dbus_service.command
    def interrupt_speech(
        self,
        script: Optional[default.Script] = None,
        event: Optional[input_event.InputEvent] = None,
        notify_user: bool = False
    ) -> bool:
        """Interrupts the speech server."""

        tokens = ["SPEECH AND VERBOSITY MANAGER: interrupt_speech. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if server := self._get_server():
            server.stop()

        return True

    @dbus_service.command
    def shutdown_speech(
        self,
        script: Optional[default.Script] = None,
        event: Optional[input_event.InputEvent] = None,
        notify_user: bool = False
    ) -> bool:
        """Shuts down the speech server."""

        tokens = ["SPEECH AND VERBOSITY MANAGER: shutdown_speech. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if server := self._get_server():
            server.shutdownActiveServers()
            speech.deprecated_clear_server()

        return True

    @dbus_service.command
    def refresh_speech(
        self,
        script: Optional[default.Script] = None,
        event: Optional[input_event.InputEvent] = None,
        notify_user: bool = False
    ) -> bool:
        """Shuts down and re-initializes speech."""

        tokens = ["SPEECH AND VERBOSITY MANAGER: refresh_speech. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self.shutdown_speech()
        self.start_speech()
        return True

    @dbus_service.command
    def decrease_rate(
        self,
        script: Optional[default.Script] = None,
        event: Optional[input_event.InputEvent] = None,
        notify_user: bool = True
    ) -> bool:
        """Decreases the speech rate"""

        tokens = ["SPEECH AND VERBOSITY MANAGER: decrease_rate. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        server = self._get_server()
        if server is None:
            msg = "SPEECH AND VERBOSITY MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        server.decreaseSpeechRate()
        if notify_user and script is not None:
            script.presentMessage(messages.SPEECH_SLOWER)

        return True

    @dbus_service.command
    def increase_rate(
        self,
        script: Optional[default.Script] = None,
        event: Optional[input_event.InputEvent] = None,
        notify_user: bool = True
    ) -> bool:
        """Increases the speech rate."""

        tokens = ["SPEECH AND VERBOSITY MANAGER: increase_rate. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        server = self._get_server()
        if server is None:
            msg = "SPEECH AND VERBOSITY MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        server.increaseSpeechRate()
        if notify_user and script is not None:
            script.presentMessage(messages.SPEECH_FASTER)

        return True

    @dbus_service.command
    def decrease_pitch(
        self,
        script: Optional[default.Script] = None,
        event: Optional[input_event.InputEvent] = None,
        notify_user: bool = True
    ) -> bool:
        """Decreases the speech pitch"""

        tokens = ["SPEECH AND VERBOSITY MANAGER: decrease_pitch. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        server = self._get_server()
        if server is None:
            msg = "SPEECH AND VERBOSITY MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        server.decreaseSpeechPitch()
        if notify_user and script is not None:
            script.presentMessage(messages.SPEECH_LOWER)

        return True

    @dbus_service.command
    def increase_pitch(
        self,
        script: Optional[default.Script] = None,
        event: Optional[input_event.InputEvent] = None,
        notify_user: bool = True
    ) -> bool:
        """Increase the speech pitch"""

        tokens = ["SPEECH AND VERBOSITY MANAGER: increase_pitch. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        server = self._get_server()
        if server is None:
            msg = "SPEECH AND VERBOSITY MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        server.increaseSpeechPitch()
        if notify_user and script is not None:
            script.presentMessage(messages.SPEECH_HIGHER)

        return True

    @dbus_service.command
    def decrease_volume(
        self,
        script: Optional[default.Script] = None,
        event: Optional[input_event.InputEvent] = None,
        notify_user: bool = True
    ) -> bool:
        """Decreases the speech volume"""

        tokens = ["SPEECH AND VERBOSITY MANAGER: decrease_volume. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        server = self._get_server()
        if server is None:
            msg = "SPEECH AND VERBOSITY MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        server.decreaseSpeechVolume()
        if notify_user and script is not None:
            script.presentMessage(messages.SPEECH_SOFTER)

        return True

    @dbus_service.command
    def increase_volume(
        self,
        script: Optional[default.Script] = None,
        event: Optional[input_event.InputEvent] = None,
        notify_user: bool = True
    ) -> bool:
        """Increases the speech volume"""

        tokens = ["SPEECH AND VERBOSITY MANAGER: increase_volume. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        server = self._get_server()
        if server is None:
            msg = "SPEECH AND VERBOSITY MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        server.increaseSpeechVolume()
        if notify_user and script is not None:
            script.presentMessage(messages.SPEECH_LOUDER)

        return True

    def update_capitalization_style(self) -> bool:
        """Updates the capitalization style based on the value in settings."""

        server = self._get_server()
        if server is None:
            msg = "SPEECH AND VERBOSITY MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        server.updateCapitalizationStyle()
        return True

    def update_punctuation_level(self) -> bool:
        """Updates the punctuation level based on the value in settings."""

        server = self._get_server()
        if server is None:
            msg = "SPEECH AND VERBOSITY MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        server.updatePunctuationLevel()
        return True

    def update_synthesizer(self, server_id: Optional[str] = "") -> None:
        """Updates the synthesizer to the specified id or value from settings."""

        server = self._get_server()
        if server is None:
            msg = "SPEECH AND VERBOSITY MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        active_id = server.getOutputModule()
        info = settings.speechServerInfo or ["", ""]
        if not server_id and len(info) == 2:
            server_id = info[1]

        if server_id and server_id != active_id:
            msg = (
                f"SPEECH AND VERBOSITY MANAGER: Updating synthesizer from {active_id} "
                f"to {server_id}."
            )
            debug.print_message(debug.LEVEL_INFO, msg, True)
            server.setOutputModule(server_id)

    @dbus_service.command
    def cycle_synthesizer(
        self,
        script: Optional[default.Script] = None,
        event: Optional[input_event.InputEvent] = None,
        notify_user: bool = True
    ) -> bool:
        """Cycles through available speech synthesizers."""

        tokens = ["SPEECH AND VERBOSITY MANAGER: cycle_synthesizer. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        server = self._get_server()
        if server is None:
            msg = "SPEECH AND VERBOSITY MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        available = server.list_output_modules()
        if not available:
            msg = "SPEECH AND VERBOSITY MANAGER: Cannot get output modules."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        current = server.getOutputModule()
        if not current:
            msg = "SPEECH AND VERBOSITY MANAGER: Cannot get current output module."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        index = available.index(current) + 1
        if index == len(available):
            index = 0

        server.setOutputModule(available[index])
        if script is not None and notify_user:
            script.presentMessage(available[index])
        return True

    @dbus_service.command
    def cycle_capitalization_style(
        self,
        script: Optional[default.Script] = None,
        event: Optional[input_event.InputEvent] = None,
        notify_user: bool = True
    ) -> bool:
        """Cycle through the speech-dispatcher capitalization styles."""

        tokens = ["SPEECH AND VERBOSITY MANAGER: cycle_capitalization_style. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        manager = settings_manager.get_manager()
        current_style = manager.get_setting("capitalizationStyle")
        if current_style == settings.CAPITALIZATION_STYLE_NONE:
            new_style = settings.CAPITALIZATION_STYLE_SPELL
            full = messages.CAPITALIZATION_SPELL_FULL
            brief = messages.CAPITALIZATION_SPELL_BRIEF
        elif current_style == settings.CAPITALIZATION_STYLE_SPELL:
            new_style = settings.CAPITALIZATION_STYLE_ICON
            full = messages.CAPITALIZATION_ICON_FULL
            brief = messages.CAPITALIZATION_ICON_BRIEF
        else:
            new_style = settings.CAPITALIZATION_STYLE_NONE
            full = messages.CAPITALIZATION_NONE_FULL
            brief = messages.CAPITALIZATION_NONE_BRIEF

        manager.set_setting("capitalizationStyle", new_style)
        if script is not None and notify_user:
            script.presentMessage(full, brief)
        self.update_capitalization_style()
        return True

    @dbus_service.command
    def cycle_punctuation_level(
        self,
        script: Optional[default.Script] = None,
        event: Optional[input_event.InputEvent] = None,
        notify_user: bool = True
    ) -> bool:
        """Cycles through punctuation levels for speech."""

        tokens = ["SPEECH AND VERBOSITY MANAGER: cycle_punctuation_level. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        manager = settings_manager.get_manager()
        current_level = manager.get_setting("verbalizePunctuationStyle")
        if current_level == settings.PUNCTUATION_STYLE_NONE:
            new_level = settings.PUNCTUATION_STYLE_SOME
            full = messages.PUNCTUATION_SOME_FULL
            brief = messages.PUNCTUATION_SOME_BRIEF
        elif current_level == settings.PUNCTUATION_STYLE_SOME:
            new_level = settings.PUNCTUATION_STYLE_MOST
            full = messages.PUNCTUATION_MOST_FULL
            brief = messages.PUNCTUATION_MOST_BRIEF
        elif current_level == settings.PUNCTUATION_STYLE_MOST:
            new_level = settings.PUNCTUATION_STYLE_ALL
            full = messages.PUNCTUATION_ALL_FULL
            brief = messages.PUNCTUATION_ALL_BRIEF
        else:
            new_level = settings.PUNCTUATION_STYLE_NONE
            full = messages.PUNCTUATION_NONE_FULL
            brief = messages.PUNCTUATION_NONE_BRIEF

        manager.set_setting("verbalizePunctuationStyle", new_level)
        if script is not None and notify_user:
            script.presentMessage(full, brief)
        self.update_punctuation_level()
        return True

    @dbus_service.command
    def cycle_key_echo(
        self,
        script: Optional[default.Script] = None,
        event: Optional[input_event.InputEvent] = None,
        notify_user: bool = True
    ) -> bool:
        """Cycle through the key echo levels."""

        tokens = ["SPEECH AND VERBOSITY MANAGER: cycle_key_echo. Script:", script,
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
            script.presentMessage(full, brief)
        return True

    @dbus_service.command
    def change_number_style(
        self,
        script: Optional[default.Script] = None,
        event: Optional[input_event.InputEvent] = None,
        notify_user: bool = True
    ) -> bool:
        """Changes spoken number style between digits and words."""

        tokens = ["SPEECH AND VERBOSITY MANAGER: change_number_style. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        manager = settings_manager.get_manager()
        speak_digits = manager.get_setting("speakNumbersAsDigits")
        if speak_digits:
            brief = messages.NUMBER_STYLE_WORDS_BRIEF
            full = messages.NUMBER_STYLE_WORDS_FULL
        else:
            brief = messages.NUMBER_STYLE_DIGITS_BRIEF
            full = messages.NUMBER_STYLE_DIGITS_FULL

        manager.set_setting("speakNumbersAsDigits", not speak_digits)
        if script is not None and notify_user:
            script.presentMessage(full, brief)
        return True

    @dbus_service.command
    def toggle_speech(
        self,
        script: Optional[default.Script] = None,
        event: Optional[input_event.InputEvent] = None,
        notify_user: bool = True
    ) -> bool:
        """Toggles speech on and off."""

        tokens = ["SPEECH AND VERBOSITY MANAGER: toggle_speech. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        manager = settings_manager.get_manager()
        if script is not None:
            script.presentationInterrupt()
        if manager.get_setting("silenceSpeech"):
            manager.set_setting("silenceSpeech", False)
            if script is not None and notify_user:
                script.presentMessage(messages.SPEECH_ENABLED)
        elif not manager.get_setting("enableSpeech"):
            manager.set_setting("enableSpeech", True)
            speech.init()
            if script is not None and notify_user:
                script.presentMessage(messages.SPEECH_ENABLED)
        else:
            if script is not None and notify_user:
                script.presentMessage(messages.SPEECH_DISABLED)
            manager.set_setting("silenceSpeech", True)
        return True

    @dbus_service.command
    def toggle_verbosity(
        self,
        script: Optional[default.Script] = None,
        event: Optional[input_event.InputEvent] = None,
        notify_user: bool = True
    ) -> bool:
        """Toggles speech verbosity level between verbose and brief."""

        tokens = ["SPEECH AND VERBOSITY MANAGER: toggle_verbosity. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        manager = settings_manager.get_manager()
        value = manager.get_setting("speechVerbosityLevel")
        if value == settings.VERBOSITY_LEVEL_BRIEF:
            if script is not None and notify_user:
                script.presentMessage(messages.SPEECH_VERBOSITY_VERBOSE)
            manager.set_setting("speechVerbosityLevel", settings.VERBOSITY_LEVEL_VERBOSE)
        else:
            if script is not None and notify_user:
                script.presentMessage(messages.SPEECH_VERBOSITY_BRIEF)
            manager.set_setting("speechVerbosityLevel", settings.VERBOSITY_LEVEL_BRIEF)
        return True

    @dbus_service.command
    def toggle_indentation_and_justification(
        self,
        script: Optional[default.Script] = None,
        event: Optional[input_event.InputEvent] = None,
        notify_user: bool = True
    ) -> bool:
        """Toggles the speaking of indentation and justification."""

        tokens = ["SPEECH AND VERBOSITY MANAGER: toggle_indentation_and_justification. ",
                  "Script:", script, "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        manager = settings_manager.get_manager()
        value = manager.get_setting("enableSpeechIndentation")
        manager.set_setting("enableSpeechIndentation", not value)
        if manager.get_setting("enableSpeechIndentation"):
            full = messages.INDENTATION_JUSTIFICATION_ON_FULL
            brief = messages.INDENTATION_JUSTIFICATION_ON_BRIEF
        else:
            full = messages.INDENTATION_JUSTIFICATION_OFF_FULL
            brief = messages.INDENTATION_JUSTIFICATION_OFF_BRIEF
        if script is not None and notify_user:
            script.presentMessage(full, brief)
        return True

    @dbus_service.command
    def toggle_table_cell_reading_mode(
        self,
        script: Optional[default.Script] = None,
        event: Optional[input_event.InputEvent] = None,
        notify_user: bool = True
    ) -> bool:
        """Toggles between speak cell and speak row."""

        tokens = ["SPEECH AND VERBOSITY MANAGER: toggle_table_cell_reading_mode. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        # TODO - JD: This is due to the requirement on script utilities.
        if script is None:
            msg = "SPEECH AND VERBOSITY MANAGER: Toggling table cell reading mode requires script."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        table = AXTable.get_table(focus_manager.get_manager().get_locus_of_focus())
        if table is None and notify_user:
            script.presentMessage(messages.TABLE_NOT_IN_A)
            return True

        if not script.utilities.getDocumentForObject(table):
            setting_name = "readFullRowInGUITable"
        elif script.utilities.isSpreadSheetTable(table):
            setting_name = "readFullRowInSpreadSheet"
        else:
            setting_name = "readFullRowInDocumentTable"

        manager = settings_manager.get_manager()
        speak_row = manager.get_setting(setting_name)
        manager.set_setting(setting_name, not speak_row)

        if not speak_row:
            msg = messages.TABLE_MODE_ROW
        else:
            msg = messages.TABLE_MODE_CELL

        if notify_user:
            script.presentMessage(msg)
        return True

    @staticmethod
    def adjust_for_digits(obj: Atspi.Accessible, text: str) -> str:
        """Adjusts text to present numbers as digits."""

        def _convert(word):
            if word.isnumeric():
                word = " ".join(list(word))
            return word

        if not (settings.speakNumbersAsDigits or AXUtilities.is_text_input_telephone(obj)):
            return text

        return " ".join(map(_convert, text.split()))

    @staticmethod
    def _adjust_for_links(obj: Atspi.Accessible, line: str, start_offset: int) -> str:
        """Adjust line to include the word "link" after any hypertext links."""

        # This adjustment should only be made in cases where there is only presentable text.
        # In content where embedded objects are present, "link" is presented as the role of any
        # embedded link children.
        if "\ufffc" in line:
            return line

        end_offset = start_offset + len(line)
        links = AXHypertext.get_all_links_in_range(obj, start_offset, end_offset)
        offsets = [AXHypertext.get_link_end_offset(link) for link in links]
        offsets = sorted([offset - start_offset for offset in offsets], reverse=True)
        tokens = list(line)
        for o in offsets:
            if 0 <= o <= len(tokens):
                text = f" {messages.LINK}"
                if o < len(tokens) and tokens[o].isalnum():
                    text += " "
                tokens[o:o] = text
        return "".join(tokens)

    @staticmethod
    def _adjust_for_repeats(text: str) -> str:
        """Adjust line to include a description of repeated symbols."""

        def replacement(match):
            char = match.group(1)
            count = len(match.group(0))
            if match.start() > 0 and text[match.start() - 1].isalnum():
                return f" {messages.repeatedCharCount(char, count)}"
            return messages.repeatedCharCount(char, count)

        if len(text) < 4 or settings.repeatCharacterLimit < 4:
            return text

        pattern = re.compile(r"([^a-zA-Z0-9\s])\1{" + str(settings.repeatCharacterLimit - 1) + ",}")
        return re.sub(pattern, replacement, text)

    @staticmethod
    def _should_verbalize_punctuation(obj: Atspi.Accessible) -> bool:
        """Returns True if punctuation should be verbalized."""

        if AXObject.find_ancestor_inclusive(obj, AXUtilities.is_code) is None:
            return False

        # If the user has set their punctuation level to All, then the synthesizer will
        # do the work for us. If the user has set their punctuation level to None, then
        # they really don't want punctuation and we mustn't override that.
        style = settings_manager.get_manager().get_setting("verbalizePunctuationStyle")
        if style in [settings.PUNCTUATION_STYLE_ALL, settings.PUNCTUATION_STYLE_NONE]:
            return False

        return True

    @staticmethod
    def _adjust_for_verbalized_punctuation(obj: Atspi.Accessible, text: str) -> str:
        """Surrounds punctuation symbols with spaces to increase the likelihood of presentation."""

        if not SpeechAndVerbosityManager._should_verbalize_punctuation(obj):
            return text

        result = text
        punctuation = set(re.findall(r"[^\w\s]", result))
        for symbol in punctuation:
            result = result.replace(symbol, f" {symbol} ")

        return result

    @staticmethod
    def _apply_pronunciation_dictionary(text: str) -> str:
        """Applies the pronunciation dictionary to the text."""

        if not settings_manager.get_manager().get_setting("usePronunciationDictionary"):
            return text

        words = re.split(r"(\W+)", text)
        return "".join(map(pronunciation_dict.getPronunciation, words))

    def get_indentation_description(
        self,
        line: str,
        only_if_changed: Optional[bool] = None
    ) -> str:
        """Returns a description of the indentation in the given line."""

        if settings_manager.get_manager().get_setting("onlySpeakDisplayedText") \
           or not settings_manager.get_manager().get_setting("enableSpeechIndentation"):
            return ""

        line = line.replace("\u00a0", " ")
        end = re.search("[^ \t]", line)
        if end:
            line = line[:end.start()]

        result = ""
        spaces = [m.span() for m in re.finditer(" +", line)]
        tabs = [m.span() for m in re.finditer("\t+", line)]
        spans = sorted(spaces + tabs)
        for span in spans:
            if span in spaces:
                result += f"{messages.spacesCount(span[1] - span[0])} "
            else:
                result += f"{messages.tabsCount(span[1] - span[0])} "

        if only_if_changed is None:
            only_if_changed = settings_manager.get_manager().get_setting(
                "speakIndentationOnlyIfChanged")

        if only_if_changed:
            if self._last_indentation_description == result:
                return ""

            if not result and self._last_indentation_description:
                self._last_indentation_description = ""
                return messages.spacesCount(0)

        self._last_indentation_description = result
        return result

    def get_error_description(
        self,
        obj: Atspi.Accessible,
        offset: Optional[int] = None,
        only_if_changed: Optional[bool] = True
    ) -> str:
        """Returns a description of the error at the current offset."""

        if not settings_manager.get_manager().get_setting("speakMisspelledIndicator"):
            return ""

        # If we're on whitespace or punctuation, we cannot be on an error.
        char = AXText.get_character_at_offset(obj, offset)[0]
        if char in string.punctuation + string.whitespace + "\u00a0":
            return ""

        msg = ""
        if AXText.string_has_spelling_error(obj, offset):
            # TODO - JD: We're using the message here to preserve existing behavior.
            msg = messages.MISSPELLED
        elif AXText.string_has_grammar_error(obj, offset):
            msg = object_properties.STATE_INVALID_GRAMMAR_SPEECH

        if only_if_changed and msg == self._last_error_description:
            return ""

        self._last_error_description = msg
        return msg

    def adjust_for_presentation(
        self,
        obj: Atspi.Accessible,
        text: str,
        start_offset: Optional[int] = None
    ) -> str:
        """Adjusts text for spoken presentation."""

        tokens = [f"SPEECH AND VERBOSITY MANAGER: Adjusting '{text}' from",
                  obj, f"start_offset: {start_offset}"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if AXUtilities.is_math_related(obj):
            text = mathsymbols.adjustForSpeech(text)

        if start_offset is not None:
            text = self._adjust_for_links(obj, text, start_offset)

        text = self.adjust_for_digits(obj, text)
        text = self._adjust_for_repeats(text)
        text = self._adjust_for_verbalized_punctuation(obj, text)
        text = self._apply_pronunciation_dictionary(text)

        msg = F"SPEECH AND VERBOSITY MANAGER: Adjusted text: '{text}'"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return text


_manager: SpeechAndVerbosityManager = SpeechAndVerbosityManager()

def get_manager() -> SpeechAndVerbosityManager:
    """Returns the Speech and Verbosity Manager"""

    return _manager
