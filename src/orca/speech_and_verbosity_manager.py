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
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments

"""Configures speech and verbosity settings and adjusts strings accordingly."""

# This must be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc." \
                "Copyright (c) 2016-2025 Igalia, S.L."
__license__   = "LGPL"

import importlib
import queue
import re
import string
import threading
from enum import Enum
from typing import TYPE_CHECKING

from . import cmdnames
from . import dbus_service
from . import debug
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
from . import speechserver
from .acss import ACSS
from .ax_document import AXDocument
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

class CapitalizationStyle(Enum):
    """Capitalization style enumeration with string values from settings."""

    NONE = settings.CAPITALIZATION_STYLE_NONE
    SPELL = settings.CAPITALIZATION_STYLE_SPELL
    ICON = settings.CAPITALIZATION_STYLE_ICON

class PunctuationStyle(Enum):
    """Punctuation style enumeration with int values from settings."""

    NONE = settings.PUNCTUATION_STYLE_NONE
    SOME = settings.PUNCTUATION_STYLE_SOME
    MOST = settings.PUNCTUATION_STYLE_MOST
    ALL = settings.PUNCTUATION_STYLE_ALL

    @property
    def string_name(self) -> str:
        """Returns the lowercase string name for this enum value."""

        return self.name.lower()

class VerbosityLevel(Enum):
    """Verbosity level enumeration with int values from settings."""

    BRIEF = settings.VERBOSITY_LEVEL_BRIEF
    VERBOSE = settings.VERBOSITY_LEVEL_VERBOSE

    @property
    def string_name(self) -> str:
        """Returns the lowercase string name for this enum value."""

        return self.name.lower()

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
            self._bindings.remove_key_grabs("SPEECH AND VERBOSITY MANAGER: Refreshing bindings.")
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

    def _get_server(self) -> SpeechServer | None:
        """Returns the speech server if it is responsive.."""

        result = speech.get_speech_server()
        if result is None:
            msg = "SPEECH AND VERBOSITY MANAGER: Speech server is None."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return None

        result_queue: queue.Queue[bool] = queue.Queue()

        def health_check_thread():
            result.get_output_module()
            result_queue.put(True)

        thread = threading.Thread(target=health_check_thread, daemon=True)
        thread.start()

        try:
            result_queue.get(timeout=2.0)
        except queue.Empty:
            msg = "SPEECH AND VERBOSITY MANAGER: Speech server health check timed out"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return None

        tokens = ["SPEECH AND VERBOSITY MANAGER: Speech server is", result]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    def _get_available_servers(self) -> list[str]:
        """Returns a list of available speech servers."""

        return list(self._get_server_module_map().keys())

    def _get_server_module_map(self) -> dict[str, str]:
        """Returns a mapping of server names to module names."""

        result = {}
        for module_name in settings.speechFactoryModules:
            try:
                factory = importlib.import_module(f"orca.{module_name}")
            except ImportError:
                try:
                    factory = importlib.import_module(module_name)
                except ImportError:
                    continue

            try:
                speech_server_class = factory.SpeechServer
                if server_name := speech_server_class.get_factory_name():
                    result[server_name] = module_name

            except (AttributeError, TypeError, ImportError) as error:
                tokens = [f"SPEECH AND VERBOSITY MANAGER: {module_name} not available:", error]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        return result

    def _switch_server(self, target_server: str) -> bool:
        """Switches to the specified server."""

        server_module_map = self._get_server_module_map()
        target_module = server_module_map.get(target_server)
        if not target_module:
            return False

        self.shutdown_speech()
        settings_manager.get_manager().set_setting("speechServerFactory", target_module)
        self.start_speech()
        return self.get_current_server() == target_server

    @dbus_service.getter
    def get_available_servers(self) -> list[str]:
        """Returns a list of available servers."""

        result = self._get_available_servers()
        msg = f"SPEECH AND VERBOSITY MANAGER: Available servers: {result}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return result

    @dbus_service.getter
    def get_current_server(self) -> str:
        """Returns the name of the current speech server (Speech Dispatcher or Spiel)."""

        server = self._get_server()
        if server is None:
            msg = "SPEECH AND VERBOSITY MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return ""

        name = server.get_factory_name()
        msg = f"SPEECH AND VERBOSITY MANAGER: Server is: {name}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return name

    @dbus_service.setter
    def set_current_server(self, value: str) -> bool:
        """Sets the current speech server (e.g. Speech Dispatcher or Spiel)."""

        return self._switch_server(value)

    @dbus_service.getter
    def get_current_synthesizer(self) -> str:
        """Returns the current synthesizer of the speech server."""

        server = self._get_server()
        if server is None:
            msg = "SPEECH AND VERBOSITY MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return ""

        result = server.get_output_module()
        msg = f"SPEECH AND VERBOSITY MANAGER: Synthesizer is: {result}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return result

    @dbus_service.setter
    def set_current_synthesizer(self, value: str) -> bool:
        """Sets the current synthesizer of the active speech server."""

        server = self._get_server()
        if server is None:
            msg = "SPEECH AND VERBOSITY MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        available = self.get_available_synthesizers()
        if value not in available:
            tokens = [f"SPEECH AND VERBOSITY MANAGER: '{value}' is not in", available]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting synthesizer to: {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        server.set_output_module(value)
        return server.get_output_module() == value

    @dbus_service.getter
    def get_available_synthesizers(self) -> list[str]:
        """Returns a list of available synthesizers of the speech server."""

        server = self._get_server()
        if server is None:
            msg = "SPEECH AND VERBOSITY MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return []

        synthesizers = server.get_speech_servers()
        result = [s.get_info()[1] for s in synthesizers]
        msg = f"SPEECH AND VERBOSITY MANAGER: Available synthesizers: {result}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return result

    @dbus_service.getter
    def get_available_voices(self) -> list[str]:
        """Returns a list of available voices for the current synthesizer."""

        server = self._get_server()
        if server is None:
            return []

        voices = server.get_voice_families()
        if not voices:
            return []

        result = []
        for voice in voices:
            if voice_name := voice.get(speechserver.VoiceFamily.NAME, ""):
                result.append(voice_name)
        result = sorted(set(result))
        return result

    @dbus_service.parameterized_command
    def get_voices_for_language(
        self,
        language: str,
        variant: str = "",
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = False
    ) -> list[tuple[str, str, str]]:
        """Returns a list of available voices for the specified language."""

        tokens = ["SPEECH AND VERBOSITY MANAGER: get_voices_for_language. Language:", language,
                  "Variant:", variant, "Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        server = self._get_server()
        if server is None:
            return []

        voices = server.get_voice_families_for_language(language, variant)
        result = []
        for name, lang, var in voices:
            result.append((name, lang or "", var or ""))

        msg = f"SPEECH AND VERBOSITY MANAGER: Found {len(result)} voice(s) for '{language}'."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return result

    @dbus_service.getter
    def get_current_voice(self) -> str:
        """Returns the current voice name."""

        server = self._get_server()
        if server is None:
            return ""

        result = ""
        if voice_family := server.get_voice_family():
            result = voice_family.get(speechserver.VoiceFamily.NAME, "")

        return result

    @dbus_service.setter
    def set_current_voice(self, voice_name: str) -> bool:
        """Sets the current voice for the active synthesizer."""

        server = self._get_server()
        if server is None:
            return False

        available = self.get_available_voices()
        if voice_name not in available:
            msg = f"SPEECH AND VERBOSITY MANAGER: '{voice_name}' is not in {available}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        voices = server.get_voice_families()
        if not voices:
            return False

        result = False
        for voice_family in voices:
            family_name = voice_family.get(speechserver.VoiceFamily.NAME, "")
            if family_name == voice_name:
                server.set_voice_family(voice_family)
                result = True
                break

        msg = f"SPEECH AND VERBOSITY MANAGER: Set voice to '{voice_name}': {result}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return result

    def get_current_speech_server_info(self) -> tuple[str, str]:
        """Returns the name and ID of the current speech server."""

        # TODO - JD: The result is not in sync with the current output module. Should it be?
        # TODO - JD: The only caller is the preferences dialog. And the useful functionality is in
        # the methods to get (and set) the output module. So why exactly do we need this?
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
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
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
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
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
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = False
    ) -> bool:
        """Shuts down the speech server."""

        tokens = ["SPEECH AND VERBOSITY MANAGER: shutdown_speech. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if server := self._get_server():
            server.shutdown_active_servers()
            speech.deprecated_clear_server()

        return True

    @dbus_service.command
    def refresh_speech(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = False
    ) -> bool:
        """Shuts down and re-initializes speech."""

        tokens = ["SPEECH AND VERBOSITY MANAGER: refresh_speech. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self.shutdown_speech()
        self.start_speech()
        return True

    @dbus_service.getter
    def get_rate(self) -> int:
        """Returns the current speech rate."""

        result = 50
        default_voice = settings.voices.get(settings.DEFAULT_VOICE)
        if default_voice and ACSS.RATE in default_voice:
            result = default_voice[ACSS.RATE]

        msg = f"SPEECH AND VERBOSITY MANAGER: Current rate is: {result}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return result

    @dbus_service.setter
    def set_rate(self, value: int) -> bool:
        """Sets the current speech rate (0-100, default: 50)."""

        if not isinstance(value, (int, float)):
            return False

        default_voice = settings.voices.get(settings.DEFAULT_VOICE)
        if default_voice and ACSS.RATE in default_voice:
            default_voice[ACSS.RATE] = value

        msg = f"SPEECH AND VERBOSITY MANAGER: Set rate to: {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    @dbus_service.command
    def decrease_rate(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Decreases the speech rate."""

        tokens = ["SPEECH AND VERBOSITY MANAGER: decrease_rate. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        server = self._get_server()
        if server is None:
            msg = "SPEECH AND VERBOSITY MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        server.decrease_speech_rate()
        if notify_user and script is not None:
            script.present_message(messages.SPEECH_SLOWER)

        return True

    @dbus_service.command
    def increase_rate(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
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

        server.increase_speech_rate()
        if notify_user and script is not None:
            script.present_message(messages.SPEECH_FASTER)

        return True

    @dbus_service.getter
    def get_pitch(self) -> float:
        """Returns the current speech pitch."""

        result = 5.0
        default_voice = settings.voices.get(settings.DEFAULT_VOICE)
        if default_voice and ACSS.AVERAGE_PITCH in default_voice:
            result = default_voice[ACSS.AVERAGE_PITCH]

        msg = f"SPEECH AND VERBOSITY MANAGER: Current pitch is: {result}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return result

    @dbus_service.setter
    def set_pitch(self, value: float) -> bool:
        """Sets the current speech pitch (0.0-10.0, default: 5.0)."""

        if not isinstance(value, (int, float)):
            return False

        default_voice = settings.voices.get(settings.DEFAULT_VOICE)
        if default_voice and ACSS.AVERAGE_PITCH in default_voice:
            default_voice[ACSS.AVERAGE_PITCH] = value

        msg = f"SPEECH AND VERBOSITY MANAGER: Set pitch to: {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    @dbus_service.command
    def decrease_pitch(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
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

        server.decrease_speech_pitch()
        if notify_user and script is not None:
            script.present_message(messages.SPEECH_LOWER)

        return True

    @dbus_service.command
    def increase_pitch(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
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

        server.increase_speech_pitch()
        if notify_user and script is not None:
            script.present_message(messages.SPEECH_HIGHER)

        return True

    @dbus_service.getter
    def get_volume(self) -> float:
        """Returns the current speech volume."""

        result = 10.0
        default_voice = settings.voices.get(settings.DEFAULT_VOICE)
        if default_voice and ACSS.GAIN in default_voice:
            result = default_voice[ACSS.GAIN]

        msg = f"SPEECH AND VERBOSITY MANAGER: Current volume is: {result}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return result

    @dbus_service.setter
    def set_volume(self, value: float) -> bool:
        """Sets the current speech volume (0.0-10.0, default: 10.0)."""

        if not isinstance(value, (int, float)):
            return False

        default_voice = settings.voices.get(settings.DEFAULT_VOICE)
        if default_voice and ACSS.GAIN in default_voice:
            default_voice[ACSS.GAIN] = value

        msg = f"SPEECH AND VERBOSITY MANAGER: Set volume to: {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    @dbus_service.command
    def decrease_volume(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
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

        server.decrease_speech_volume()
        if notify_user and script is not None:
            script.present_message(messages.SPEECH_SOFTER)

        return True

    @dbus_service.command
    def increase_volume(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
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

        server.increase_speech_volume()
        if notify_user and script is not None:
            script.present_message(messages.SPEECH_LOUDER)

        return True

    @dbus_service.getter
    def get_capitalization_style(self) -> str:
        """Returns the current capitalization style."""

        return settings_manager.get_manager().get_setting("capitalizationStyle")

    @dbus_service.setter
    def set_capitalization_style(self, value: str) -> bool:
        """Sets the capitalization style."""

        try:
            style = CapitalizationStyle[value.upper()]
        except KeyError:
            msg = f"SPEECH AND VERBOSITY MANAGER: Invalid capitalization style: {value}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return False

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting capitalization style to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("capitalizationStyle", style.value)
        self.update_capitalization_style()
        return True

    @dbus_service.command
    def cycle_capitalization_style(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
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
            script.present_message(full, brief)
        self.update_capitalization_style()
        return True

    def update_capitalization_style(self) -> bool:
        """Updates the capitalization style based on the value in settings."""

        server = self._get_server()
        if server is None:
            msg = "SPEECH AND VERBOSITY MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        server.update_capitalization_style()
        return True

    @dbus_service.getter
    def get_punctuation_level(self) -> str:
        """Returns the current punctuation level."""

        int_value = settings_manager.get_manager().get_setting("verbalizePunctuationStyle")
        return PunctuationStyle(int_value).string_name

    @dbus_service.setter
    def set_punctuation_level(self, value: str) -> bool:
        """Sets the punctuation level."""

        try:
            style = PunctuationStyle[value.upper()]
        except KeyError:
            msg = f"SPEECH AND VERBOSITY MANAGER: Invalid punctuation level: {value}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return False

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting punctuation level to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("verbalizePunctuationStyle", style.value)
        self.update_punctuation_level()
        return True

    @dbus_service.command
    def cycle_punctuation_level(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
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
            script.present_message(full, brief)
        self.update_punctuation_level()
        return True

    def update_punctuation_level(self) -> bool:
        """Updates the punctuation level based on the value in settings."""

        server = self._get_server()
        if server is None:
            msg = "SPEECH AND VERBOSITY MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        server.update_punctuation_level()
        return True

    def update_synthesizer(self, server_id: str | None = "") -> None:
        """Updates the synthesizer to the specified id or value from settings."""

        server = self._get_server()
        if server is None:
            msg = "SPEECH AND VERBOSITY MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        active_id = server.get_output_module()
        info = settings.speechServerInfo or ["", ""]
        if not server_id and len(info) == 2:
            server_id = info[1]

        if server_id and server_id != active_id:
            msg = (
                f"SPEECH AND VERBOSITY MANAGER: Updating synthesizer from {active_id} "
                f"to {server_id}."
            )
            debug.print_message(debug.LEVEL_INFO, msg, True)
            server.set_output_module(server_id)

    @dbus_service.command
    def cycle_synthesizer(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
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

        current = server.get_output_module()
        if not current:
            msg = "SPEECH AND VERBOSITY MANAGER: Cannot get current output module."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        try:
            index = available.index(current) + 1
            if index == len(available):
                index = 0
        except ValueError:
            index = 0

        server.set_output_module(available[index])
        if script is not None and notify_user:
            script.present_message(available[index])
        return True

    @dbus_service.getter
    def get_speak_misspelled_indicator(self) -> bool:
        """Returns whether the misspelled indicator is spoken."""

        return settings_manager.get_manager().get_setting("speakMisspelledIndicator")

    @dbus_service.setter
    def set_speak_misspelled_indicator(self, value: bool) -> bool:
        """Sets whether the misspelled indicator is spoken."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting speak misspelled indicator to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("speakMisspelledIndicator", value)
        return True

    @dbus_service.getter
    def get_speak_description(self) -> bool:
        """Returns whether object descriptions are spoken."""

        return settings_manager.get_manager().get_setting("speakDescription")

    @dbus_service.setter
    def set_speak_description(self, value: bool) -> bool:
        """Sets whether object descriptions are spoken."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting speak description to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("speakDescription", value)
        return True

    @dbus_service.getter
    def get_speak_position_in_set(self) -> bool:
        """Returns whether the position and set size of objects are spoken."""

        return settings_manager.get_manager().get_setting("enablePositionSpeaking")

    @dbus_service.setter
    def set_speak_position_in_set(self, value: bool) -> bool:
        """Sets whether the position and set size of objects are spoken."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting speak position in set to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("enablePositionSpeaking", value)
        return True

    @dbus_service.getter
    def get_speak_widget_mnemonic(self) -> bool:
        """Returns whether widget mnemonics are spoken."""

        return settings_manager.get_manager().get_setting("enableMnemonicSpeaking")

    @dbus_service.setter
    def set_speak_widget_mnemonic(self, value: bool) -> bool:
        """Sets whether widget mnemonics are spoken."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting speak widget mnemonics to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("enableMnemonicSpeaking", value)
        return True

    @dbus_service.getter
    def get_speak_tutorial_messages(self) -> bool:
        """Returns whether tutorial messages are spoken."""

        return settings_manager.get_manager().get_setting("enableTutorialMessages")

    @dbus_service.setter
    def set_speak_tutorial_messages(self, value: bool) -> bool:
        """Sets whether tutorial messages are spoken."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting speak tutorial messages to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("enableTutorialMessages", value)
        return True

    @dbus_service.getter
    def get_insert_pauses_between_utterances(self) -> bool:
        """Returns whether pauses are inserted between utterances, e.g. between name and role."""

        return settings_manager.get_manager().get_setting("enablePauseBreaks")

    @dbus_service.setter
    def set_insert_pauses_between_utterances(self, value: bool) -> bool:
        """Sets whether pauses are inserted between utterances, e.g. between name and role."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting insert pauses to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("enablePauseBreaks", value)
        return True

    @dbus_service.getter
    def get_repeated_character_limit(self) -> int:
        """Returns the count at which repeated, non-alphanumeric symbols will be described."""

        return settings_manager.get_manager().get_setting("repeatCharacterLimit")

    @dbus_service.setter
    def set_repeated_character_limit(self, value: int) -> bool:
        """Sets the count at which repeated, non-alphanumeric symbols will be described."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting repeated character limit to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("repeatCharacterLimit", value)
        return True

    @dbus_service.getter
    def get_use_pronunciation_dictionary(self) -> bool:
        """Returns whether the user's pronunciation dictionary should be applied."""

        return settings_manager.get_manager().get_setting("usePronunciationDictionary")

    @dbus_service.setter
    def set_use_pronunciation_dictionary(self, value: bool) -> bool:
        """Sets whether the user's pronunciation dictionary should be applied."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting use pronunciation dictionary to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("usePronunciationDictionary", value)
        return True

    @dbus_service.getter
    def get_speak_blank_lines(self) -> bool:
        """Returns whether blank lines will be spoken."""

        return settings_manager.get_manager().get_setting("speakBlankLines")

    @dbus_service.setter
    def set_speak_blank_lines(self, value: bool) -> bool:
        """Sets whether blank lines will be spoken."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting speak blank lines to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("speakBlankLines", value)
        return True

    @dbus_service.getter
    def get_speak_row_in_gui_table(self) -> bool:
        """Returns whether Up/Down in GUI tables speaks the row or just the cell."""

        return settings_manager.get_manager().get_setting("readFullRowInGUITable")

    @dbus_service.setter
    def set_speak_row_in_gui_table(self, value: bool) -> bool:
        """Sets whether Up/Down in GUI tables speaks the row or just the cell."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting speak row in GUI table to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("readFullRowInGUITable", value)
        return True

    @dbus_service.getter
    def get_speak_row_in_document_table(self) -> bool:
        """Returns whether Up/Down in text-document tables speaks the row or just the cell."""

        return settings_manager.get_manager().get_setting("readFullRowInDocumentTable")

    @dbus_service.setter
    def set_speak_row_in_document_table(self, value: bool) -> bool:
        """Sets whether Up/Down in text-document tables speaks the row or just the cell."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting speak row in document table to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("readFullRowInDocumentTable", value)
        return True

    @dbus_service.getter
    def get_speak_row_in_spreadsheet(self) -> bool:
        """Returns whether Up/Down in spreadsheets speaks the row or just the cell."""

        return settings_manager.get_manager().get_setting("readFullRowInSpreadSheet")

    @dbus_service.setter
    def set_speak_row_in_spreadsheet(self, value: bool) -> bool:
        """Sets whether Up/Down in spreadsheets speaks the row or just the cell."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting speak row in spreadsheet to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("readFullRowInSpreadSheet", value)
        return True

    @dbus_service.getter
    def get_announce_cell_span(self) -> bool:
        """Returns whether cell spans are announced when greater than 1."""

        return settings_manager.get_manager().get_setting("speakCellSpan")

    @dbus_service.setter
    def set_announce_cell_span(self, value: bool) -> bool:
        """Sets whether cell spans are announced when greater than 1."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting announce cell spans to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("speakCellSpan", value)
        return True

    @dbus_service.getter
    def get_announce_cell_coordinates(self) -> bool:
        """Returns whether (non-spreadsheet) cell coordinates are announced."""

        return settings_manager.get_manager().get_setting("speakCellCoordinates")

    @dbus_service.setter
    def set_announce_cell_coordinates(self, value: bool) -> bool:
        """Sets whether (non-spreadsheet) cell coordinates are announced."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting announce cell coordinates to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("speakCellCoordinates", value)
        return True

    @dbus_service.getter
    def get_announce_spreadsheet_cell_coordinates(self) -> bool:
        """Returns whether spreadsheet cell coordinates are announced."""

        return settings_manager.get_manager().get_setting("speakSpreadsheetCoordinates")

    @dbus_service.setter
    def set_announce_spreadsheet_cell_coordinates(self, value: bool) -> bool:
        """Sets whether spreadsheet cell coordinates are announced."""

        msg = (
            f"SPEECH AND VERBOSITY MANAGER: Setting announce spreadsheet cell coordinates to "
            f"{value}."
        )
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("speakSpreadsheetCoordinates", value)
        return True

    @dbus_service.getter
    def get_always_announce_selected_range_in_spreadsheet(self) -> bool:
        """Returns whether the selected range in spreadsheets is always announced."""

        return settings_manager.get_manager().get_setting("alwaysSpeakSelectedSpreadsheetRange")

    @dbus_service.setter
    def set_always_announce_selected_range_in_spreadsheet(self, value: bool) -> bool:
        """Sets whether the selected range in spreadsheets is always announced."""

        msg = (
            f"SPEECH AND VERBOSITY MANAGER: Setting always announce selected spreadsheet range to "
            f"{value}."
        )
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("alwaysSpeakSelectedSpreadsheetRange", value)
        return True

    @dbus_service.getter
    def get_announce_cell_headers(self) -> bool:
        """Returns whether cell headers are announced."""

        return settings_manager.get_manager().get_setting("speakCellHeaders")

    @dbus_service.setter
    def set_announce_cell_headers(self, value: bool) -> bool:
        """Sets whether cell headers are announced."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting announce cell headers to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("speakCellHeaders", value)
        return True

    @dbus_service.getter
    def get_announce_blockquote(self) -> bool:
        """Returns whether blockquotes are announced when entered."""

        return settings_manager.get_manager().get_setting("speakContextBlockquote")

    @dbus_service.setter
    def set_announce_blockquote(self, value: bool) -> bool:
        """Sets whether blockquotes are announced when entered."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting announce blockquotes to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("speakContextBlockquote", value)
        return True

    @dbus_service.getter
    def get_announce_form(self) -> bool:
        """Returns whether non-landmark forms are announced when entered."""

        return settings_manager.get_manager().get_setting("speakContextNonLandmarkForm")

    @dbus_service.setter
    def set_announce_form(self, value: bool) -> bool:
        """Sets whether non-landmark forms are announced when entered."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting announce forms to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("speakContextNonLandmarkForm", value)
        return True

    @dbus_service.getter
    def get_announce_grouping(self) -> bool:
        """Returns whether groupings are announced when entered."""

        return settings_manager.get_manager().get_setting("speakContextPanel")

    @dbus_service.setter
    def set_announce_grouping(self, value: bool) -> bool:
        """Sets whether groupings are announced when entered."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting announce groupings to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("speakContextPanel", value)
        return True

    @dbus_service.getter
    def get_announce_landmark(self) -> bool:
        """Returns whether landmarks are announced when entered."""

        return settings_manager.get_manager().get_setting("speakContextLandmark")

    @dbus_service.setter
    def set_announce_landmark(self, value: bool) -> bool:
        """Sets whether landmarks are announced when entered."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting announce landmarks to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("speakContextLandmark", value)
        return True

    @dbus_service.getter
    def get_announce_list(self) -> bool:
        """Returns whether lists are announced when entered."""

        return settings_manager.get_manager().get_setting("speakContextList")

    @dbus_service.setter
    def set_announce_list(self, value: bool) -> bool:
        """Sets whether lists are announced when entered."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting announce lists to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("speakContextList", value)
        return True

    @dbus_service.getter
    def get_announce_table(self) -> bool:
        """Returns whether tables are announced when entered."""

        return settings_manager.get_manager().get_setting("speakContextTable")

    @dbus_service.setter
    def set_announce_table(self, value: bool) -> bool:
        """Sets whether tables are announced when entered."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting announce tables to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("speakContextTable", value)
        return True

    @dbus_service.getter
    def get_use_color_names(self) -> bool:
        """Returns whether colors are announced by name or as RGB values."""

        return settings_manager.get_manager().get_setting("useColorNames")

    @dbus_service.setter
    def set_use_color_names(self, value: bool) -> bool:
        """Sets whether colors are announced by name or as RGB values."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting use color names to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("useColorNames", value)
        return True

    @dbus_service.getter
    def get_speak_numbers_as_digits(self) -> bool:
        """Returns whether numbers are spoken as digits."""

        return settings_manager.get_manager().get_setting("speakNumbersAsDigits")

    @dbus_service.setter
    def set_speak_numbers_as_digits(self, value: bool) -> bool:
        """Sets whether numbers are spoken as digits."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting speak numbers as digits to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("speakNumbersAsDigits", value)
        return True

    @dbus_service.command
    def change_number_style(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Changes spoken number style between digits and words."""

        tokens = ["SPEECH AND VERBOSITY MANAGER: change_number_style. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        speak_digits = self.get_speak_numbers_as_digits()
        if speak_digits:
            brief = messages.NUMBER_STYLE_WORDS_BRIEF
            full = messages.NUMBER_STYLE_WORDS_FULL
        else:
            brief = messages.NUMBER_STYLE_DIGITS_BRIEF
            full = messages.NUMBER_STYLE_DIGITS_FULL

        self.set_speak_numbers_as_digits(not speak_digits)
        if script is not None and notify_user:
            script.present_message(full, brief)
        return True

    def get_speech_is_enabled_and_not_muted(self) -> bool:
        """Returns whether speech is enabled and not muted."""

        return self.get_speech_is_enabled() and not self.get_speech_is_muted()

    @dbus_service.getter
    def get_speech_is_muted(self) -> bool:
        """Returns whether speech output is temporarily muted."""

        return settings_manager.get_manager().get_setting("silenceSpeech")

    @dbus_service.setter
    def set_speech_is_muted(self, value: bool) -> bool:
        """Sets whether speech output is temporarily muted."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting speech muted to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("silenceSpeech", value)
        return True

    @dbus_service.getter
    def get_speech_is_enabled(self) -> bool:
        """Returns whether the speech server is enabled. See also is-muted."""

        return settings_manager.get_manager().get_setting("enableSpeech")

    @dbus_service.setter
    def set_speech_is_enabled(self, value: bool) -> bool:
        """Sets whether the speech server is enabled. See also is-muted."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting speech enabled to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("enableSpeech", value)
        return True

    @dbus_service.getter
    def get_only_speak_displayed_text(self) -> bool:
        """Returns whether only displayed text should be spoken."""

        return settings_manager.get_manager().get_setting("onlySpeakDisplayedText")

    @dbus_service.setter
    def set_only_speak_displayed_text(self, value: bool) -> bool:
        """Sets whether only displayed text should be spoken."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting only speak displayed text to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("onlySpeakDisplayedText", value)
        return True

    @dbus_service.command
    def toggle_speech(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Toggles speech on and off."""

        tokens = ["SPEECH AND VERBOSITY MANAGER: toggle_speech. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if script is not None:
            script.interrupt_presentation()
        if self.get_speech_is_muted():
            self.set_speech_is_muted(False)
            if script is not None and notify_user:
                script.present_message(messages.SPEECH_ENABLED)
        elif not settings_manager.get_manager().get_setting("enableSpeech"):
            settings_manager.get_manager().set_setting("enableSpeech", True)
            speech.init()
            if script is not None and notify_user:
                script.present_message(messages.SPEECH_ENABLED)
        else:
            if script is not None and notify_user:
                script.present_message(messages.SPEECH_DISABLED)
            self.set_speech_is_muted(True)
        return True

    @dbus_service.getter
    def get_messages_are_detailed(self) -> bool:
        """Returns whether informative messages will be detailed or brief."""

        return settings_manager.get_manager().get_setting("messagesAreDetailed")

    @dbus_service.setter
    def set_messages_are_detailed(self, value: bool) -> bool:
        """Sets whether informative messages will be detailed or brief."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting messages are detailed to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("messagesAreDetailed", value)
        return True

    def use_verbose_speech(self) -> bool:
        """Returns whether the speech verbosity level is set to verbose."""

        level = settings_manager.get_manager().get_setting("speechVerbosityLevel")
        return level == settings.VERBOSITY_LEVEL_VERBOSE

    @dbus_service.getter
    def get_verbosity_level(self) -> str:
        """Returns the current speech verbosity level for object presentation."""

        int_value = settings_manager.get_manager().get_setting("speechVerbosityLevel")
        return VerbosityLevel(int_value).string_name

    @dbus_service.setter
    def set_verbosity_level(self, value: str) -> bool:
        """Sets the speech verbosity level for object presentation."""

        try:
            level = VerbosityLevel[value.upper()]
        except KeyError:
            msg = f"SPEECH AND VERBOSITY MANAGER: Invalid verbosity level: {value}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return False

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting verbosity level to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("speechVerbosityLevel", level.value)
        return True

    @dbus_service.command
    def toggle_verbosity(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
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
                script.present_message(messages.SPEECH_VERBOSITY_VERBOSE)
            manager.set_setting("speechVerbosityLevel", settings.VERBOSITY_LEVEL_VERBOSE)
        else:
            if script is not None and notify_user:
                script.present_message(messages.SPEECH_VERBOSITY_BRIEF)
            manager.set_setting("speechVerbosityLevel", settings.VERBOSITY_LEVEL_BRIEF)
        return True

    @dbus_service.getter
    def get_speak_indentation_and_justification(self) -> bool:
        """Returns whether speaking of indentation and justification is enabled."""

        return settings_manager.get_manager().get_setting("enableSpeechIndentation")

    @dbus_service.setter
    def set_speak_indentation_and_justification(self, value: bool) -> bool:
        """Sets whether speaking of indentation and justification is enabled."""

        msg = (
            f"SPEECH AND VERBOSITY MANAGER: Setting speak indentation and justification to {value}."
        )
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("enableSpeechIndentation", value)
        return True

    @dbus_service.getter
    def get_speak_indentation_only_if_changed(self) -> bool:
        """Returns whether indentation will be announced only if it has changed."""

        return settings_manager.get_manager().get_setting("speakIndentationOnlyIfChanged")

    @dbus_service.setter
    def set_speak_indentation_only_if_changed(self, value: bool) -> bool:
        """Sets whether indentation will be announced only if it has changed."""

        msg = f"SPEECH AND VERBOSITY MANAGER: Setting speak indentation only if changed to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("speakIndentationOnlyIfChanged", value)
        return True

    @dbus_service.command
    def toggle_indentation_and_justification(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Toggles the speaking of indentation and justification."""

        tokens = ["SPEECH AND VERBOSITY MANAGER: toggle_indentation_and_justification. ",
                  "Script:", script, "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        value = self.get_speak_indentation_and_justification()
        self.set_speak_indentation_and_justification(not value)
        if self.get_speak_indentation_and_justification():
            full = messages.INDENTATION_JUSTIFICATION_ON_FULL
            brief = messages.INDENTATION_JUSTIFICATION_ON_BRIEF
        else:
            full = messages.INDENTATION_JUSTIFICATION_OFF_FULL
            brief = messages.INDENTATION_JUSTIFICATION_OFF_BRIEF
        if script is not None and notify_user:
            script.present_message(full, brief)
        return True

    @dbus_service.command
    def toggle_table_cell_reading_mode(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
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
            script.present_message(messages.TABLE_NOT_IN_A)
            return True

        # TODO - JD: Use the new getters and setters for this.
        if not script.utilities.get_document_for_object(table):
            setting_name = "readFullRowInGUITable"
        elif script.utilities.is_spreadsheet_table(table):
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
            script.present_message(msg)
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

    def _adjust_for_repeats(self, text: str) -> str:
        """Adjust line to include a description of repeated symbols."""

        def replacement(match):
            char = match.group(1)
            count = len(match.group(0))
            if match.start() > 0 and text[match.start() - 1].isalnum():
                return f" {messages.repeated_char_count(char, count)}"
            return messages.repeated_char_count(char, count)

        limit = self.get_repeated_character_limit()
        if len(text) < 4 or limit < 4:
            return text

        pattern = re.compile(r"([^a-zA-Z0-9\s])\1{" + str(limit - 1) + ",}")
        return re.sub(pattern, replacement, text)

    @staticmethod
    def _should_verbalize_punctuation(obj: Atspi.Accessible) -> bool:
        """Returns True if punctuation should be verbalized."""

        ancestor = AXObject.find_ancestor_inclusive(obj, AXUtilities.is_code)
        if ancestor is None:
            return False

        document = AXObject.find_ancestor_inclusive(ancestor, AXUtilities.is_document)
        if AXDocument.is_plain_text(document):
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

    def _apply_pronunciation_dictionary(self, text: str) -> str:
        """Applies the pronunciation dictionary to the text."""

        if not self.get_use_pronunciation_dictionary():
            return text

        words = re.split(r"(\W+)", text)
        return "".join(map(pronunciation_dict.get_pronunciation, words))

    def get_indentation_description(
        self,
        line: str,
        only_if_changed: bool | None = None
    ) -> str:
        """Returns a description of the indentation in the given line."""

        if self.get_only_speak_displayed_text() \
           or not self.get_speak_indentation_and_justification():
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
                result += f"{messages.spaces_count(span[1] - span[0])} "
            else:
                result += f"{messages.tabs_count(span[1] - span[0])} "

        if only_if_changed is None:
            only_if_changed = self.get_speak_indentation_only_if_changed()

        if only_if_changed:
            if self._last_indentation_description == result:
                return ""

            if not result and self._last_indentation_description:
                self._last_indentation_description = ""
                return messages.spaces_count(0)

        self._last_indentation_description = result
        return result

    def get_error_description(
        self,
        obj: Atspi.Accessible,
        offset: int | None = None,
        only_if_changed: bool | None = True
    ) -> str:
        """Returns a description of the error at the current offset."""

        if not self.get_speak_misspelled_indicator():
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
        start_offset: int | None = None
    ) -> str:
        """Adjusts text for spoken presentation."""

        tokens = [f"SPEECH AND VERBOSITY MANAGER: Adjusting '{text}' from",
                  obj, f"start_offset: {start_offset}"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if AXUtilities.is_math_related(obj):
            text = mathsymbols.adjust_for_speech(text)

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
