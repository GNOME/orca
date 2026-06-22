# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
# Copyright 2011-2026 Igalia, S.L.
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
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=too-many-locals
# pylint: disable=too-many-lines

"""Manages the speech engine: server, synthesizer, voice, and output parameters."""

from __future__ import annotations

import importlib
import os
from typing import TYPE_CHECKING, Any

from . import (
    command_manager,
    dbus_service,
    debug,
    gsettings_registry,
    guilabels,
    input_event,
    language_utilities,
    messages,
    presentation_manager,
    speech_manager_command_definitions,
    speechserver,
    systemd,
)
from .acss import ACSS
from .extension import Extension
from .speechserver import CapitalizationStyle, PunctuationStyle

if TYPE_CHECKING:
    from .command import Command, KeyboardCommand
    from .dbus_service import UInt32
    from .scripts import default
    from .speech_manager_preferences_grid import VoicesPreferencesGrid, VoiceTypesPreferencesGrid
    from .speechserver import SpeechServer

SPEECH_FACTORY_MODULES: list[str] = ["speechdispatcherfactory", "spiel"]


@gsettings_registry.get_registry().gsettings_schema("org.gnome.Orca.Speech", name="speech")
@gsettings_registry.get_registry().gsettings_schema("org.gnome.Orca.Voice", name="voice")
class SpeechManager(Extension):
    """Manages the speech engine: server, synthesizer, voice, and output parameters."""

    GROUP_LABEL = guilabels.KB_GROUP_SPEECH_VERBOSITY

    SPEECH_SCHEMA = "speech"
    _VOICE_SCHEMA = "voice"

    KEY_ENABLE = "enable"
    KEY_SPEECH_SERVER = "speech-server"
    KEY_SPEECH_SERVER_FACTORY = "speech-server-factory"
    KEY_SYNTHESIZER = "synthesizer"
    KEY_SPEAK_NUMBERS_AS_DIGITS = "speak-numbers-as-digits"
    KEY_USE_COLOR_NAMES = "use-color-names"
    KEY_INSERT_PAUSES_BETWEEN_UTTERANCES = "insert-pauses-between-utterances"
    KEY_USE_PRONUNCIATION_DICTIONARY = "use-pronunciation-dictionary"
    KEY_AUTO_LANGUAGE_SWITCHING = "auto-language-switching"
    KEY_AUTO_LANGUAGE_SWITCHING_UI = "auto-language-switching-ui"
    KEY_ONLY_SWITCH_CONFIGURED_LANGUAGES = "only-switch-configured-languages"
    KEY_CAPITALIZATION_STYLE = "capitalization-style"
    KEY_PUNCTUATION_LEVEL = "punctuation-level"

    KEY_ESTABLISHED = "established"
    KEY_RATE = "rate"
    KEY_PITCH = "pitch"
    KEY_PITCH_RANGE = "pitch-range"
    KEY_VOLUME = "volume"
    KEY_FAMILY_NAME = "family-name"
    KEY_FAMILY_LANG = "family-lang"
    KEY_FAMILY_DIALECT = "family-dialect"
    KEY_FAMILY_GENDER = "family-gender"
    KEY_FAMILY_VARIANT = "family-variant"

    def _get_setting(
        self,
        key: str,
        gtype: str,
        default: Any,
        app_name: str | None = None,
        genum: str | None = None,
    ) -> Any:
        """Returns the dconf value for key, or default if not in dconf."""

        return gsettings_registry.get_registry().layered_lookup(
            self.SPEECH_SCHEMA,
            key,
            gtype,
            genum=genum,
            default=default,
            app_name=app_name,
        )

    def get_voice_properties(
        self,
        voice_type: str = "",
        app_name: str | None = None,
        voice_set: str = gsettings_registry.PRIMARY_VOICE_SET,
    ) -> ACSS:
        """Returns voice properties from dconf for the given voice type and set."""

        vtype = voice_type or speechserver.VoiceType.DEFAULT

        if voice_set != gsettings_registry.PRIMARY_VOICE_SET:
            return self._get_voice_set_properties(vtype, voice_set)

        lookup = gsettings_registry.get_registry().layered_lookup
        voice: dict[str, Any] = {}

        established = lookup(
            self._VOICE_SCHEMA,
            self.KEY_ESTABLISHED,
            "b",
            voice_type=vtype,
            app_name=app_name,
        )
        if established is not None:
            voice["established"] = established

        rate = lookup(self._VOICE_SCHEMA, self.KEY_RATE, "i", voice_type=vtype, app_name=app_name)
        if rate is not None:
            voice[ACSS.RATE] = rate
        pitch = lookup(self._VOICE_SCHEMA, self.KEY_PITCH, "d", voice_type=vtype, app_name=app_name)
        if pitch is not None:
            voice[ACSS.AVERAGE_PITCH] = pitch
        pitch_range = lookup(
            self._VOICE_SCHEMA, self.KEY_PITCH_RANGE, "d", voice_type=vtype, app_name=app_name
        )
        if pitch_range is not None:
            voice[ACSS.PITCH_RANGE] = pitch_range
        volume = lookup(
            self._VOICE_SCHEMA, self.KEY_VOLUME, "d", voice_type=vtype, app_name=app_name
        )
        if volume is not None:
            voice[ACSS.GAIN] = volume

        family: dict[str, str] = {}
        for dconf_key, family_key in (
            (self.KEY_FAMILY_NAME, speechserver.VoiceFamily.NAME),
            (self.KEY_FAMILY_LANG, speechserver.VoiceFamily.LANG),
            (self.KEY_FAMILY_DIALECT, speechserver.VoiceFamily.DIALECT),
            (self.KEY_FAMILY_GENDER, speechserver.VoiceFamily.GENDER),
            (self.KEY_FAMILY_VARIANT, speechserver.VoiceFamily.VARIANT),
        ):
            value = lookup(self._VOICE_SCHEMA, dconf_key, "s", voice_type=vtype, app_name=app_name)
            if value:
                family[family_key] = value
        if family:
            voice[ACSS.FAMILY] = family

        return ACSS(voice)

    def get_voice_set_voice(
        self, voice_type: str, voice_set: str, fall_back_to_default: bool = True
    ) -> ACSS:
        """Returns the set's voice for voice_type, optionally falling back to its default voice."""

        if fall_back_to_default:
            types: tuple[str, ...] = (voice_type, speechserver.VoiceType.DEFAULT)
        else:
            types = (voice_type,)
        for vtype in types:
            config = self.get_voice_properties(vtype, voice_set=voice_set)
            if config and config.get(self.KEY_ESTABLISHED):
                return config
        return ACSS({})

    def _set_runtime_voice(self, voice_type: str, voice: ACSS) -> None:
        """Overrides the runtime voice for voice_type, clearing any previous override."""

        registry = gsettings_registry.get_registry()
        prosody = (
            (ACSS.RATE, self.KEY_RATE),
            (ACSS.AVERAGE_PITCH, self.KEY_PITCH),
            (ACSS.PITCH_RANGE, self.KEY_PITCH_RANGE),
            (ACSS.GAIN, self.KEY_VOLUME),
        )
        families = (
            (speechserver.VoiceFamily.NAME, self.KEY_FAMILY_NAME),
            (speechserver.VoiceFamily.LANG, self.KEY_FAMILY_LANG),
            (speechserver.VoiceFamily.DIALECT, self.KEY_FAMILY_DIALECT),
            (speechserver.VoiceFamily.GENDER, self.KEY_FAMILY_GENDER),
            (speechserver.VoiceFamily.VARIANT, self.KEY_FAMILY_VARIANT),
        )
        for _attr, key in ((None, self.KEY_ESTABLISHED), *prosody, *families):
            registry.remove_runtime_value(self._VOICE_SCHEMA, key, voice_type=voice_type)
        # A non-default voice type is only used if it is established; mirror that here so the
        # generator applies it rather than falling back to the default voice.
        registry.set_runtime_value(
            self._VOICE_SCHEMA,
            self.KEY_ESTABLISHED,
            bool(voice.get("established")),
            voice_type=voice_type,
        )
        for acss_key, key in prosody:
            if acss_key in voice:
                registry.set_runtime_value(
                    self._VOICE_SCHEMA, key, voice[acss_key], voice_type=voice_type
                )
        family = voice.get(ACSS.FAMILY, {})
        for family_key, key in families:
            if family.get(family_key):
                registry.set_runtime_value(
                    self._VOICE_SCHEMA, key, family[family_key], voice_type=voice_type
                )

    def apply_live_voice(self, voice: ACSS) -> None:
        """Auditions voice as the live default voice, bypassing voice-set rerouting."""

        self._auditioning_voice = True
        self._set_runtime_voice(speechserver.VoiceType.DEFAULT, voice)
        if (server := self.get_server()) is not None:
            server.set_default_voice(voice)
            server.clear_cached_voice_properties()

    def restore_live_voices(self, voices: dict[str, ACSS]) -> None:
        """Makes each staged voice live by voice type and resumes normal voice-set processing."""

        self._auditioning_voice = False
        for voice_type, voice in voices.items():
            self._set_runtime_voice(voice_type, voice)
        if (server := self.get_server()) is not None:
            server.set_default_voice(voices.get(speechserver.VoiceType.DEFAULT, ACSS({})))
            server.clear_cached_voice_properties()

    @staticmethod
    def apply_voice_overrides(base: ACSS, override: ACSS) -> ACSS:
        """Overlays family and prosody from override onto base, returning the merged ACSS."""

        tokens = ["SPEECH MANAGER: Applying voice overrides:", override, "onto:", base]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if ACSS.FAMILY in override:
            family = dict(base.get(ACSS.FAMILY, {}))
            family.update(override[ACSS.FAMILY])
            base[ACSS.FAMILY] = family
        for prop in (ACSS.RATE, ACSS.AVERAGE_PITCH, ACSS.PITCH_RANGE, ACSS.GAIN):
            if prop in override:
                base[prop] = override[prop]
        return base

    def apply_voice_set(self, voice: ACSS) -> ACSS:
        """Overlays the active voice set, or the set matching the voice's language."""

        if self._auditioning_voice:
            # A voice is being auditioned in preferences; let it be heard as configured.
            return voice
        voice_type = voice.get(ACSS.VOICE_TYPE, speechserver.VoiceType.DEFAULT)
        fall_back_to_default = True
        if self._active_voice_set != gsettings_registry.PRIMARY_VOICE_SET:
            # A command loaded a set manually; it overrides every voice type. The system
            # voice is used only if the set configures one; otherwise status messages stay
            # in Orca's own voice rather than borrowing the set's default voice.
            voice_set = self._active_voice_set
            fall_back_to_default = voice_type != speechserver.VoiceType.SYSTEM
        else:
            # Otherwise follow the voice's own language (automatic switching).
            family = voice.get(ACSS.FAMILY)
            if not family:
                return voice
            lang = family.get(speechserver.VoiceFamily.LANG, "")
            if not lang:
                return voice
            dialect = family.get(speechserver.VoiceFamily.DIALECT, "")
            voice_set = f"{lang}-{dialect}".lower() if dialect else lang.lower()
            voice_set_names = self.get_voice_set_names()
            if voice_set not in voice_set_names:
                voice_set = lang.lower()
            if voice_set not in voice_set_names:
                return voice

        voice.pop(ACSS.VOICE_TYPE, None)
        config = self.get_voice_set_voice(voice_type, voice_set, fall_back_to_default)
        if not config:
            return voice

        tokens = ["SPEECH MANAGER: Applying voice set", voice_set, "for", voice_type]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return self.apply_voice_overrides(voice, config)

    def _get_voice_set_properties(self, voice_type: str, voice_set: str) -> ACSS:
        """Returns voice properties for a non-primary voice set."""

        registry = gsettings_registry.get_registry()
        sub = gsettings_registry.get_registry().voice_set_sub_path(voice_type, voice_set)
        gs = registry.get_settings("voice", registry.get_active_profile(), sub)
        if gs is None:
            return ACSS({})

        voice: dict[str, Any] = {}
        for key, acss_key in (
            (self.KEY_RATE, ACSS.RATE),
            (self.KEY_PITCH, ACSS.AVERAGE_PITCH),
            (self.KEY_PITCH_RANGE, ACSS.PITCH_RANGE),
            (self.KEY_VOLUME, ACSS.GAIN),
        ):
            if gs.get_user_value(key) is not None:
                voice[acss_key] = gs.get_value(key).unpack()

        established = gs.get_user_value(self.KEY_ESTABLISHED)
        if established is not None:
            voice["established"] = established.get_boolean()

        family: dict[str, str] = {}
        for dconf_key, family_key in (
            (self.KEY_FAMILY_NAME, speechserver.VoiceFamily.NAME),
            (self.KEY_FAMILY_LANG, speechserver.VoiceFamily.LANG),
            (self.KEY_FAMILY_DIALECT, speechserver.VoiceFamily.DIALECT),
            (self.KEY_FAMILY_GENDER, speechserver.VoiceFamily.GENDER),
            (self.KEY_FAMILY_VARIANT, speechserver.VoiceFamily.VARIANT),
        ):
            val = gs.get_user_value(dconf_key)
            if val is not None:
                family[family_key] = val.get_string()
        if family:
            voice[ACSS.FAMILY] = family

        return ACSS(voice)

    def set_voice_set_properties(self, voice_type: str, voice_set: str, properties: ACSS) -> None:
        """Stores voice properties for a voice set."""

        registry = gsettings_registry.get_registry()
        sub = gsettings_registry.get_registry().voice_set_sub_path(voice_type, voice_set)
        gs = registry.get_settings("voice", registry.get_active_profile(), sub)
        if gs is None:
            return

        gs.set_boolean(self.KEY_ESTABLISHED, True)

        for key, acss_key, setter in (
            (self.KEY_RATE, ACSS.RATE, gs.set_int),
            (self.KEY_PITCH, ACSS.AVERAGE_PITCH, gs.set_double),
            (self.KEY_PITCH_RANGE, ACSS.PITCH_RANGE, gs.set_double),
            (self.KEY_VOLUME, ACSS.GAIN, gs.set_double),
        ):
            if acss_key in properties:
                setter(key, properties[acss_key])

        family = properties.get(ACSS.FAMILY, {})
        for dconf_key, family_key in (
            (self.KEY_FAMILY_NAME, speechserver.VoiceFamily.NAME),
            (self.KEY_FAMILY_LANG, speechserver.VoiceFamily.LANG),
            (self.KEY_FAMILY_DIALECT, speechserver.VoiceFamily.DIALECT),
            (self.KEY_FAMILY_GENDER, speechserver.VoiceFamily.GENDER),
            (self.KEY_FAMILY_VARIANT, speechserver.VoiceFamily.VARIANT),
        ):
            if family.get(family_key):
                gs.set_string(dconf_key, family[family_key])

    def get_voice_set_names(self) -> list[str]:
        """Returns the names of configured voice sets (excluding primary)."""

        registry = gsettings_registry.get_registry()
        profile = registry.get_active_profile()
        gs = registry.get_settings(
            "voice", profile, f"voice-sets/{gsettings_registry.PRIMARY_VOICE_SET}/default"
        )
        if gs is None:
            return []

        entries = gsettings_registry.GSettingsRegistry.dconf_list(
            f"{gsettings_registry.GSETTINGS_PATH_PREFIX}"
            f"{gsettings_registry.GSettingsRegistry.sanitize_gsettings_path(profile)}/voice-sets/"
        )
        return [e for e in entries if e != gsettings_registry.PRIMARY_VOICE_SET]

    def __init__(self) -> None:
        self._families_sorted: bool = False
        self._mute_speech: bool = False
        self._server: SpeechServer | None = None
        self._active_voice_set: str = gsettings_registry.PRIMARY_VOICE_SET
        self._auditioning_voice = False
        self._voice_set_command_names: set[str] = set()
        super().__init__()
        gsettings_registry.get_registry().add_profile_change_observer(
            self.refresh_voice_set_commands
        )

    def _get_commands(self) -> list[Command]:
        """Returns commands for registration."""

        commands = speech_manager_command_definitions.get_commands(self)
        commands.extend(self._build_voice_set_commands())
        return commands

    def _build_voice_set_commands(self) -> list[KeyboardCommand]:
        """Returns one unbound activation command per available voice set."""

        commands = speech_manager_command_definitions.get_voice_set_commands(self)
        self._voice_set_command_names = {cmd.get_name() for cmd in commands}
        return commands

    def refresh_voice_set_commands(self, _profile: str = "") -> None:
        """Re-registers the per-set activation commands after the available sets change."""

        if not self._commands_initialized:
            return

        manager = command_manager.get_manager()
        previous = self._voice_set_command_names
        commands = self._build_voice_set_commands()
        for name in previous:
            manager.remove_command(name)
        for command in commands:
            manager.add_command(command)

    def get_server(self) -> SpeechServer | None:
        """Returns the speech server instance, or None if not initialized."""

        return self._server

    def _get_server(self) -> SpeechServer | None:
        """Returns the speech server if it is responsive."""

        result = self._server
        if result is None:
            msg = "SPEECH MANAGER: Speech server is None."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return None

        if not result.is_responsive():
            msg = "SPEECH MANAGER: Speech server is not responsive."
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return None

        tokens = ["SPEECH MANAGER: Speech server is", result]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    def _get_available_servers(self) -> list[str]:
        """Returns a list of available speech servers."""

        return list(self._get_server_module_map().keys())

    def _get_server_module_map(self) -> dict[str, str]:
        """Returns a mapping of server names to module names."""

        result = {}
        for module_name in SPEECH_FACTORY_MODULES:
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
                tokens = [f"SPEECH MANAGER: {module_name} not available:", error]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        return result

    def _switch_server(self, target_server: str) -> bool:
        """Switches to the specified server."""

        server_module_map = self._get_server_module_map()
        target_module = server_module_map.get(target_server)
        if not target_module:
            return False

        self.shutdown_speech()
        gsettings_registry.get_registry().set_runtime_value(
            self.SPEECH_SCHEMA,
            self.KEY_SPEECH_SERVER_FACTORY,
            target_module,
        )
        self.start_speech()
        return self.get_current_server() == target_server

    @dbus_service.getter
    def get_available_servers(self) -> list[str]:
        """Returns a list of available servers."""

        result = self._get_available_servers()
        msg = f"SPEECH MANAGER: Available servers: {result}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return result

    @gsettings_registry.get_registry().gsetting(
        key=KEY_SPEECH_SERVER,
        schema="speech",
        gtype="s",
        default="",
        summary="Speech server name",
    )
    @dbus_service.getter
    def get_current_server(self) -> str:
        """Returns the name of the current speech server (Speech Dispatcher or Spiel)."""

        server = self._get_server()
        if server is None:
            msg = "SPEECH MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return ""

        name = server.get_factory_name()
        msg = f"SPEECH MANAGER: Server is: {name}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return name

    @dbus_service.setter
    def set_current_server(self, value: str) -> bool:
        """Sets the current speech server (e.g. Speech Dispatcher or Spiel)."""

        return self._switch_server(value)

    def get_speech_server(self, app_name: str | None = None) -> str:
        """Returns the speech server setting."""

        return self._get_setting(self.KEY_SPEECH_SERVER, "s", "", app_name=app_name)

    @gsettings_registry.get_registry().gsetting(
        key=KEY_SPEECH_SERVER_FACTORY,
        schema="speech",
        gtype="s",
        default="speechdispatcherfactory",
        summary="Speech server factory module",
        migration_key="speechServerFactory",
    )
    def get_speech_server_factory(self) -> str:
        """Returns the speech server factory module name."""

        # Test override: the integration test harness points this at a no-audio server.
        if override := os.environ.get("ORCA_TEST_SPEECH_SERVER_FACTORY"):
            return override
        return self._get_setting(self.KEY_SPEECH_SERVER_FACTORY, "s", "speechdispatcherfactory")

    @gsettings_registry.get_registry().gsetting(
        key=KEY_SYNTHESIZER,
        schema="speech",
        gtype="s",
        default="",
        summary="Speech synthesizer",
    )
    @dbus_service.getter
    def get_current_synthesizer(self) -> str:
        """Returns the current synthesizer of the speech server."""

        server = self._get_server()
        if server is None:
            msg = "SPEECH MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return ""

        result = server.get_output_module()
        msg = f"SPEECH MANAGER: Synthesizer is: {result}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return result

    @dbus_service.setter
    def set_current_synthesizer(self, value: str) -> bool:
        """Sets the current synthesizer of the active speech server."""

        server = self._get_server()
        if server is None:
            msg = "SPEECH MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        available = self.get_available_synthesizers()
        if value not in available:
            tokens = [f"SPEECH MANAGER: '{value}' is not in", available]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        msg = f"SPEECH MANAGER: Setting synthesizer to: {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        server.set_output_module(value)
        return server.get_output_module() == value

    def get_synthesizer(self, app_name: str | None = None) -> str:
        """Returns the synthesizer setting."""

        return self._get_setting(self.KEY_SYNTHESIZER, "s", "", app_name=app_name)

    @dbus_service.getter
    def get_available_synthesizers(self) -> list[str]:
        """Returns a list of available synthesizers of the speech server."""

        server = self._get_server()
        if server is None:
            msg = "SPEECH MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return []

        synthesizers = server.get_speech_servers()
        result = [s.get_info()[1] for s in synthesizers]
        msg = f"SPEECH MANAGER: Available synthesizers: {result}."
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

        result = sorted(
            {
                voice_name
                for voice in voices
                if (voice_name := voice.get(speechserver.VoiceFamily.NAME, ""))
            },
        )
        return result

    def get_voice_families(self) -> list[speechserver.VoiceFamily]:
        """Returns the full list of voice family dictionaries for the current synthesizer.
        Each dictionary contains NAME, LANG, DIALECT, and VARIANT fields."""

        server = self._get_server()
        if server is None:
            return []

        return server.get_voice_families() or []

    @dbus_service.parameterized_command
    def get_voices_for_language(
        self,
        language: str,
        variant: str = "",
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
    ) -> list[tuple[str, str, str]]:
        """Returns a list of available voices for the specified language."""

        tokens = [
            "SPEECH MANAGER: get_voices_for_language. Language:",
            language,
            "Variant:",
            variant,
            "Script:",
            script,
            "Event:",
            event,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        server = self._get_server()
        if server is None:
            return []

        voices = server.get_voice_families_for_language(language=language, variant=variant)
        result = []
        for name, lang, var in voices:
            result.append((name, lang or "", var or ""))

        msg = f"SPEECH MANAGER: Found {len(result)} voice(s) for '{language}'."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return result

    @gsettings_registry.get_registry().gsetting(
        key=KEY_FAMILY_NAME,
        schema="voice",
        gtype="s",
        default="",
        summary="Voice family name",
    )
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

    @gsettings_registry.get_registry().gsetting(
        key=KEY_FAMILY_LANG,
        schema="voice",
        gtype="s",
        default="",
        summary="Voice family language",
    )
    def get_current_voice_lang(self) -> str:
        """Returns the language of the current voice."""

        server = self._get_server()
        if server is None:
            return ""

        if voice_family := server.get_voice_family():
            return voice_family.get(speechserver.VoiceFamily.LANG, "") or ""

        return ""

    @gsettings_registry.get_registry().gsetting(
        key=KEY_FAMILY_DIALECT,
        schema="voice",
        gtype="s",
        default="",
        summary="Voice family dialect",
    )
    def get_current_voice_dialect(self) -> str:
        """Returns the dialect of the current voice."""

        server = self._get_server()
        if server is None:
            return ""

        if voice_family := server.get_voice_family():
            return voice_family.get(speechserver.VoiceFamily.DIALECT, "") or ""

        return ""

    @gsettings_registry.get_registry().gsetting(
        key=KEY_FAMILY_GENDER,
        schema="voice",
        gtype="s",
        default="",
        summary="Voice family gender",
    )
    def get_current_voice_gender(self) -> str:
        """Returns the gender of the current voice."""

        server = self._get_server()
        if server is None:
            return ""

        if voice_family := server.get_voice_family():
            return voice_family.get(speechserver.VoiceFamily.GENDER, "") or ""

        return ""

    @gsettings_registry.get_registry().gsetting(
        key=KEY_FAMILY_VARIANT,
        schema="voice",
        gtype="s",
        default="",
        summary="Voice family variant",
    )
    def get_current_voice_variant(self) -> str:
        """Returns the variant of the current voice."""

        server = self._get_server()
        if server is None:
            return ""

        if voice_family := server.get_voice_family():
            return voice_family.get(speechserver.VoiceFamily.VARIANT, "") or ""

        return ""

    @dbus_service.setter
    def set_current_voice(self, voice_name: str) -> bool:
        """Sets the current voice for the active synthesizer."""

        server = self._get_server()
        if server is None:
            return False

        available = self.get_available_voices()
        if voice_name not in available:
            msg = f"SPEECH MANAGER: '{voice_name}' is not in {available}"
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

        msg = f"SPEECH MANAGER: Set voice to '{voice_name}': {result}"
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
        msg = f"SPEECH MANAGER: Speech server info: {server_name}, {server_id}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return server_name, server_id

    def check_speech_setting(self) -> None:
        """Checks the speech setting and initializes speech if necessary."""

        if not self.get_speech_is_enabled():
            msg = "SPEECH MANAGER: Speech is not enabled. Shutting down speech."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self.shutdown_speech()
            return

        msg = "SPEECH MANAGER: Speech is enabled."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self.start_speech()

    @dbus_service.command
    def start_speech(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = False,
    ) -> bool:
        """Starts the speech server."""

        tokens = [
            "SPEECH MANAGER: start_speech. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        self._init_server()
        return True

    def _init_server(self) -> None:
        """Initializes the speech server."""

        debug.print_message(debug.LEVEL_INFO, "SPEECH MANAGER: Initializing server", True)
        if self._server:
            debug.print_message(debug.LEVEL_INFO, "SPEECH MANAGER: Already initialized", True)
            return

        factory = self.get_speech_server_factory()
        self._server = self._init_server_from_module(factory, None)

        if not self._server:
            for module_name in SPEECH_FACTORY_MODULES:
                if module_name != factory:
                    self._server = self._init_server_from_module(module_name, None)
                    if self._server:
                        factory = module_name
                        break

        if self._server:
            tokens = ["SPEECH MANAGER: Using speech server factory:", factory]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

            synth = self._get_setting(self.KEY_SYNTHESIZER, "s", "")
            if synth:
                self._server.set_output_module(synth)

            self._server.set_default_voice(self.get_voice_properties())
            level_str = self.get_punctuation_level()
            self._server.update_punctuation_level(PunctuationStyle[level_str.upper()])
            self._server.update_capitalization_style(self.get_capitalization_style())
        else:
            msg = "SPEECH MANAGER: Speech not available"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            systemd.get_manager().set_status("Speech", "not available")

        debug.print_message(debug.LEVEL_INFO, "SPEECH MANAGER: Server initialized", True)
        if self._server:
            systemd.get_manager().set_status("Speech", "enabled")

    @staticmethod
    def _init_server_from_module(
        module_name: str,
        speech_server_info: list[str] | None,
    ) -> SpeechServer | None:
        """Attempts to initialize a speech server from the given module."""

        if not module_name:
            return None

        factory = None
        try:
            factory = importlib.import_module(f"orca.{module_name}")
        except ImportError:
            try:
                factory = importlib.import_module(module_name)
            except ImportError:
                debug.print_exception(debug.LEVEL_SEVERE)

        if not factory:
            msg = f"SPEECH MANAGER: Failed to import module: {module_name}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return None

        server = None
        if speech_server_info:
            server = factory.SpeechServer.get_speech_server(speech_server_info)

        if not server:
            if speech_server_info:
                tokens = ["SPEECH MANAGER: Could not use server info:", speech_server_info]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            server = factory.SpeechServer.get_speech_server()

        if not server:
            msg = f"SPEECH MANAGER: No speech server for factory: {module_name}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)

        return server

    @dbus_service.command
    def interrupt_speech(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = False,
    ) -> bool:
        """Interrupts the speech server."""

        tokens = [
            "SPEECH MANAGER: interrupt_speech. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if server := self._get_server():
            server.stop()

        return True

    @dbus_service.command
    def shutdown_speech(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = False,
    ) -> bool:
        """Shuts down the speech server."""

        tokens = [
            "SPEECH MANAGER: shutdown_speech. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if server := self._get_server():
            server.shutdown_active_servers()
            self._server = None

        return True

    @dbus_service.command
    def refresh_speech(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = False,
    ) -> bool:
        """Shuts down and re-initializes speech."""

        tokens = [
            "SPEECH MANAGER: refresh_speech. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self.shutdown_speech()
        self.start_speech()
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_ESTABLISHED,
        schema="voice",
        gtype="b",
        default=False,
        migration_key="established",
        summary="Whether this voice type has been user-customized",
    )
    def get_established(self) -> bool:
        """Returns whether the current voice type has been customized."""

        return False

    @gsettings_registry.get_registry().gsetting(
        key=KEY_RATE,
        schema="voice",
        gtype="i",
        default=50,
        summary="Speech rate (0-100)",
    )
    @dbus_service.getter
    def get_rate(self) -> UInt32:
        """Returns the current speech rate."""

        return gsettings_registry.get_registry().layered_lookup(
            self._VOICE_SCHEMA,
            self.KEY_RATE,
            "i",
            default=50,
        )

    def _sync_runtime_value_to_all_voice_types(self, key: str, value: Any) -> None:
        """Sets a runtime value override for all voice types."""

        registry = gsettings_registry.get_registry()
        for vtype in speechserver.VoiceType:
            registry.set_runtime_value(self._VOICE_SCHEMA, key, value, voice_type=vtype)

    @dbus_service.setter
    def set_rate(self, value: UInt32) -> bool:
        """Sets the current speech rate (0-100, default: 50)."""

        if not isinstance(value, (int, float)):
            return False

        registry = gsettings_registry.get_registry()
        registry.set_runtime_value(self._VOICE_SCHEMA, self.KEY_RATE, value)
        self._sync_runtime_value_to_all_voice_types(self.KEY_RATE, value)

        msg = f"SPEECH MANAGER: Set rate to: {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    @dbus_service.command
    def decrease_rate(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Decreases the speech rate."""

        tokens = [
            "SPEECH MANAGER: decrease_rate. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        server = self._get_server()
        if server is None:
            msg = "SPEECH MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        server.decrease_speech_rate()
        new_rate = max(0, self.get_rate() - 5)
        self.set_rate(new_rate)
        if notify_user and script is not None:
            full = f"{messages.SPEECH_SLOWER} {new_rate}"
            presentation_manager.get_manager().present_message(full, str(new_rate))

        return True

    @dbus_service.command
    def increase_rate(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Increases the speech rate."""

        tokens = [
            "SPEECH MANAGER: increase_rate. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        server = self._get_server()
        if server is None:
            msg = "SPEECH MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        server.increase_speech_rate()
        new_rate = min(100, self.get_rate() + 5)
        self.set_rate(new_rate)
        if notify_user and script is not None:
            full = f"{messages.SPEECH_FASTER} {new_rate}"
            presentation_manager.get_manager().present_message(full, str(new_rate))

        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_PITCH,
        schema="voice",
        gtype="d",
        default=5.0,
        summary="Speech pitch (0.0-10.0)",
    )
    @dbus_service.getter
    def get_pitch(self) -> float:
        """Returns the current speech pitch."""

        return gsettings_registry.get_registry().layered_lookup(
            self._VOICE_SCHEMA,
            self.KEY_PITCH,
            "d",
            default=5.0,
        )

    @dbus_service.setter
    def set_pitch(self, value: float) -> bool:
        """Sets the current speech pitch (0.0-10.0, default: 5.0)."""

        if not isinstance(value, (int, float)):
            return False

        registry = gsettings_registry.get_registry()
        registry.set_runtime_value(self._VOICE_SCHEMA, self.KEY_PITCH, value)
        self._sync_runtime_value_to_all_voice_types(self.KEY_PITCH, value)

        msg = f"SPEECH MANAGER: Set pitch to: {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    @dbus_service.command
    def decrease_pitch(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Decreases the speech pitch"""

        tokens = [
            "SPEECH MANAGER: decrease_pitch. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        server = self._get_server()
        if server is None:
            msg = "SPEECH MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        server.decrease_speech_pitch()
        new_pitch = max(0.0, self.get_pitch() - 0.5)
        self.set_pitch(new_pitch)
        if notify_user and script is not None:
            full = f"{messages.SPEECH_LOWER} {new_pitch:g}"
            presentation_manager.get_manager().present_message(full, f"{new_pitch:g}")

        return True

    @dbus_service.command
    def increase_pitch(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Increase the speech pitch"""

        tokens = [
            "SPEECH MANAGER: increase_pitch. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        server = self._get_server()
        if server is None:
            msg = "SPEECH MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        server.increase_speech_pitch()
        new_pitch = min(10.0, self.get_pitch() + 0.5)
        self.set_pitch(new_pitch)
        if notify_user and script is not None:
            full = f"{messages.SPEECH_HIGHER} {new_pitch:g}"
            presentation_manager.get_manager().present_message(full, f"{new_pitch:g}")

        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_PITCH_RANGE,
        schema="voice",
        gtype="d",
        default=5.0,
        summary="Speech inflection / pitch range (0.0-10.0)",
    )
    @dbus_service.getter
    def get_pitch_range(self) -> float:
        """Returns the current speech inflection (pitch range)."""

        return gsettings_registry.get_registry().layered_lookup(
            self._VOICE_SCHEMA,
            self.KEY_PITCH_RANGE,
            "d",
            default=5.0,
        )

    @dbus_service.setter
    def set_pitch_range(self, value: float) -> bool:
        """Sets the current speech inflection / pitch range (0.0-10.0, default: 5.0)."""

        if not isinstance(value, (int, float)):
            return False

        registry = gsettings_registry.get_registry()
        registry.set_runtime_value(self._VOICE_SCHEMA, self.KEY_PITCH_RANGE, value)
        self._sync_runtime_value_to_all_voice_types(self.KEY_PITCH_RANGE, value)

        msg = f"SPEECH MANAGER: Set pitch range to: {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    @dbus_service.command
    def decrease_pitch_range(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Decreases the speech inflection (pitch range)."""

        tokens = [
            "SPEECH MANAGER: decrease_pitch_range. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        server = self._get_server()
        if server is None:
            msg = "SPEECH MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        server.decrease_speech_inflection()
        new_pitch_range = max(0.0, self.get_pitch_range() - 0.5)
        self.set_pitch_range(new_pitch_range)
        if notify_user and script is not None:
            full = f"{messages.SPEECH_LESS_INFLECTION} {new_pitch_range:g}"
            presentation_manager.get_manager().present_message(full, f"{new_pitch_range:g}")

        return True

    @dbus_service.command
    def increase_pitch_range(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Increases the speech inflection (pitch range)."""

        tokens = [
            "SPEECH MANAGER: increase_pitch_range. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        server = self._get_server()
        if server is None:
            msg = "SPEECH MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        server.increase_speech_inflection()
        new_pitch_range = min(10.0, self.get_pitch_range() + 0.5)
        self.set_pitch_range(new_pitch_range)
        if notify_user and script is not None:
            full = f"{messages.SPEECH_MORE_INFLECTION} {new_pitch_range:g}"
            presentation_manager.get_manager().present_message(full, f"{new_pitch_range:g}")

        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_VOLUME,
        schema="voice",
        gtype="d",
        default=10.0,
        summary="Speech volume (0.0-10.0)",
    )
    @dbus_service.getter
    def get_volume(self) -> float:
        """Returns the current speech volume."""

        return gsettings_registry.get_registry().layered_lookup(
            self._VOICE_SCHEMA,
            self.KEY_VOLUME,
            "d",
            default=10.0,
        )

    @dbus_service.setter
    def set_volume(self, value: float) -> bool:
        """Sets the current speech volume (0.0-10.0, default: 10.0)."""

        if not isinstance(value, (int, float)):
            return False

        registry = gsettings_registry.get_registry()
        registry.set_runtime_value(self._VOICE_SCHEMA, self.KEY_VOLUME, value)
        self._sync_runtime_value_to_all_voice_types(self.KEY_VOLUME, value)

        msg = f"SPEECH MANAGER: Set volume to: {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    @dbus_service.command
    def decrease_volume(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Decreases the speech volume"""

        tokens = [
            "SPEECH MANAGER: decrease_volume. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        server = self._get_server()
        if server is None:
            msg = "SPEECH MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        server.decrease_speech_volume()
        new_volume = max(0.0, self.get_volume() - 0.5)
        self.set_volume(new_volume)
        if notify_user and script is not None:
            full = f"{messages.SPEECH_SOFTER} {new_volume:g}"
            presentation_manager.get_manager().present_message(full, f"{new_volume:g}")

        return True

    @dbus_service.command
    def increase_volume(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Increases the speech volume"""

        tokens = [
            "SPEECH MANAGER: increase_volume. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        server = self._get_server()
        if server is None:
            msg = "SPEECH MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        server.increase_speech_volume()
        new_volume = min(10.0, self.get_volume() + 0.5)
        self.set_volume(new_volume)
        if notify_user and script is not None:
            full = f"{messages.SPEECH_LOUDER} {new_volume:g}"
            presentation_manager.get_manager().present_message(full, f"{new_volume:g}")

        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_CAPITALIZATION_STYLE,
        schema="speech",
        genum="org.gnome.Orca.CapitalizationStyle",
        default="none",
        summary="Capitalization style (none, spell, icon)",
        migration_key="capitalizationStyle",
    )
    @dbus_service.getter
    def get_capitalization_style(self, app_name: str | None = None) -> str:
        """Returns the current capitalization style."""

        return self._get_setting(
            self.KEY_CAPITALIZATION_STYLE,
            "",
            default="none",
            app_name=app_name,
            genum="org.gnome.Orca.CapitalizationStyle",
        )

    @dbus_service.setter
    def set_capitalization_style(self, value: str) -> bool:
        """Sets the capitalization style."""

        try:
            style = CapitalizationStyle[value.upper()]
        except KeyError:
            msg = f"SPEECH MANAGER: Invalid capitalization style: {value}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return False

        msg = f"SPEECH MANAGER: Setting capitalization style to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self.SPEECH_SCHEMA,
            self.KEY_CAPITALIZATION_STYLE,
            style.string_name,
        )
        self.update_capitalization_style()
        return True

    @dbus_service.command
    def cycle_capitalization_style(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Cycle through the speech-dispatcher capitalization styles."""

        tokens = [
            "SPEECH MANAGER: cycle_capitalization_style. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        current_style = self.get_capitalization_style()
        if current_style == "none":
            self.set_capitalization_style("spell")
            full = messages.CAPITALIZATION_SPELL_FULL
            brief = messages.CAPITALIZATION_SPELL_BRIEF
        elif current_style == "spell":
            self.set_capitalization_style("icon")
            full = messages.CAPITALIZATION_ICON_FULL
            brief = messages.CAPITALIZATION_ICON_BRIEF
        else:
            self.set_capitalization_style("none")
            full = messages.CAPITALIZATION_NONE_FULL
            brief = messages.CAPITALIZATION_NONE_BRIEF

        if script is not None and notify_user:
            presentation_manager.get_manager().present_message(full, brief)
        return True

    def update_capitalization_style(self) -> bool:
        """Updates the capitalization style on the speech server."""

        server = self._get_server()
        if server is None:
            msg = "SPEECH MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        server.update_capitalization_style(self.get_capitalization_style())
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_PUNCTUATION_LEVEL,
        schema="speech",
        genum="org.gnome.Orca.PunctuationStyle",
        default="most",
        summary="Punctuation verbosity level (none, some, most, all)",
        migration_key="verbalizePunctuationStyle",
    )
    @dbus_service.getter
    def get_punctuation_level(self, app_name: str | None = None) -> str:
        """Returns the current punctuation level."""

        return self._get_setting(
            self.KEY_PUNCTUATION_LEVEL,
            "",
            default="most",
            app_name=app_name,
            genum="org.gnome.Orca.PunctuationStyle",
        )

    @dbus_service.setter
    def set_punctuation_level(self, value: str) -> bool:
        """Sets the punctuation level."""

        try:
            style = PunctuationStyle[value.upper()]
        except KeyError:
            msg = f"SPEECH MANAGER: Invalid punctuation level: {value}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return False

        msg = f"SPEECH MANAGER: Setting punctuation level to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self.SPEECH_SCHEMA,
            self.KEY_PUNCTUATION_LEVEL,
            style.string_name,
        )
        self.update_punctuation_level()
        return True

    @dbus_service.command
    def cycle_punctuation_level(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Cycles through punctuation levels for speech."""

        tokens = [
            "SPEECH MANAGER: cycle_punctuation_level. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        current_level = self.get_punctuation_level()
        if current_level == "none":
            self.set_punctuation_level("some")
            full = messages.PUNCTUATION_SOME_FULL
            brief = messages.PUNCTUATION_SOME_BRIEF
        elif current_level == "some":
            self.set_punctuation_level("most")
            full = messages.PUNCTUATION_MOST_FULL
            brief = messages.PUNCTUATION_MOST_BRIEF
        elif current_level == "most":
            self.set_punctuation_level("all")
            full = messages.PUNCTUATION_ALL_FULL
            brief = messages.PUNCTUATION_ALL_BRIEF
        else:
            self.set_punctuation_level("none")
            full = messages.PUNCTUATION_NONE_FULL
            brief = messages.PUNCTUATION_NONE_BRIEF

        if script is not None and notify_user:
            presentation_manager.get_manager().present_message(full, brief)
        return True

    def update_punctuation_level(self) -> bool:
        """Updates the punctuation level on the speech server."""

        server = self._get_server()
        if server is None:
            msg = "SPEECH MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        level_str = self.get_punctuation_level()
        server.update_punctuation_level(PunctuationStyle[level_str.upper()])
        return True

    def update_synthesizer(self, server_id: str | None = "") -> None:
        """Updates the synthesizer to the specified id or value from settings."""

        server = self._get_server()
        if server is None:
            msg = "SPEECH MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        active_id = server.get_output_module()
        if not server_id:
            server_id = self._get_setting(self.KEY_SYNTHESIZER, "s", "")

        if server_id and server_id != active_id:
            msg = f"SPEECH MANAGER: Updating synthesizer from {active_id} to {server_id}."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            server.set_output_module(server_id)

    @dbus_service.command
    def cycle_synthesizer(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Cycles through available speech synthesizers."""

        tokens = [
            "SPEECH MANAGER: cycle_synthesizer. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        server = self._get_server()
        if server is None:
            msg = "SPEECH MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        available = server.list_output_modules()
        if not available:
            msg = "SPEECH MANAGER: Cannot get output modules."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        current = server.get_output_module()
        if not current:
            msg = "SPEECH MANAGER: Cannot get current output module."
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
            presentation_manager.get_manager().present_message(available[index])
        return True

    def get_speech_is_enabled_and_not_muted(self) -> bool:
        """Returns whether speech is enabled and not muted."""

        return self.get_speech_is_enabled() and not self.get_speech_is_muted()

    @dbus_service.getter
    def get_speech_is_muted(self) -> bool:
        """Returns whether speech output is temporarily muted."""

        return self._mute_speech

    @dbus_service.setter
    def set_speech_is_muted(self, value: bool) -> bool:
        """Sets whether speech output is temporarily muted."""

        msg = f"SPEECH MANAGER: Setting speech muted to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self._mute_speech = value
        return True

    @dbus_service.getter
    def get_available_voice_sets(self) -> list[str]:
        """Returns the valid values for the active voice set."""

        result = [gsettings_registry.PRIMARY_VOICE_SET, *sorted(self.get_voice_set_names())]
        msg = f"SPEECH MANAGER: Available voice sets: {result}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return result

    @dbus_service.getter
    def get_active_voice_set(self) -> str:
        """Returns the name of the active voice set used for speech output."""

        return self._active_voice_set

    @dbus_service.setter
    def set_active_voice_set(self, name: str) -> bool:
        """Sets the active voice set used for speech output."""

        if name != gsettings_registry.PRIMARY_VOICE_SET and name not in self.get_voice_set_names():
            msg = f"SPEECH MANAGER: Ignoring unknown voice set {name!r}."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False
        msg = f"SPEECH MANAGER: Setting active voice set to {name}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self._active_voice_set = name
        return True

    def _voice_set_display_name(self, set_id: str) -> str:
        """Returns the user-facing name for the given voice set."""

        if set_id == gsettings_registry.PRIMARY_VOICE_SET:
            return guilabels.VOICE_SET_GLOBAL
        return language_utilities.get_language_display_name(set_id, in_own_language=True)

    @dbus_service.parameterized_command
    def activate_voice_set(
        self,
        set_id: str,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Makes set_id the active voice set and announces the change."""

        tokens = ["SPEECH MANAGER: activate_voice_set", set_id, "Script:", script, "Event:", event]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if not self.set_active_voice_set(set_id):
            return True

        if script is not None and notify_user:
            presentation_manager.get_manager().present_message(
                self._voice_set_display_name(set_id), voice_type=speechserver.VoiceType.DEFAULT
            )
        return True

    @dbus_service.command
    def cycle_voice_set(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Switches to the next available voice set, wrapping after the last."""

        tokens = ["SPEECH MANAGER: cycle_voice_set. Script:", script, "Event:", event]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        available = self.get_available_voice_sets()
        try:
            index = available.index(self._active_voice_set) + 1
        except ValueError:
            index = 0
        if index == len(available):
            index = 0

        return self.activate_voice_set(available[index], script, event, notify_user)

    @gsettings_registry.get_registry().gsetting(
        key=KEY_ENABLE,
        schema="speech",
        gtype="b",
        default=True,
        summary="Enable speech output",
        migration_key="enableSpeech",
    )
    @dbus_service.getter
    def get_speech_is_enabled(self) -> bool:
        """Returns whether the speech server is enabled. See also is-muted."""

        return self._get_setting(self.KEY_ENABLE, "b", True)

    @dbus_service.setter
    def set_speech_is_enabled(self, value: bool) -> bool:
        """Sets whether the speech server is enabled. See also is-muted."""

        if value == self.get_speech_is_enabled():
            return True

        msg = f"SPEECH MANAGER: Setting speech enabled to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)

        gsettings_registry.get_registry().set_runtime_value(
            self.SPEECH_SCHEMA, self.KEY_ENABLE, value
        )
        if value:
            self.start_speech()
            presentation_manager.get_manager().present_message(messages.SPEECH_ENABLED)
            systemd.get_manager().set_status("Speech", "enabled")
        else:
            presentation_manager.get_manager().present_message(messages.SPEECH_DISABLED)
            self.shutdown_speech()
            systemd.get_manager().set_status("Speech", "disabled")

        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_SPEAK_NUMBERS_AS_DIGITS,
        schema="speech",
        gtype="b",
        default=False,
        summary="Speak numbers as individual digits",
        migration_key="speakNumbersAsDigits",
    )
    @dbus_service.getter
    def get_speak_numbers_as_digits(self, app_name: str | None = None) -> bool:
        """Returns whether numbers are spoken as digits."""

        return self._get_setting(self.KEY_SPEAK_NUMBERS_AS_DIGITS, "b", False, app_name=app_name)

    @dbus_service.setter
    def set_speak_numbers_as_digits(self, value: bool) -> bool:
        """Sets whether numbers are spoken as digits."""

        msg = f"SPEECH MANAGER: Setting speak numbers as digits to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self.SPEECH_SCHEMA,
            self.KEY_SPEAK_NUMBERS_AS_DIGITS,
            value,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_USE_COLOR_NAMES,
        schema="speech",
        gtype="b",
        default=True,
        summary="Use color names instead of values",
        migration_key="useColorNames",
    )
    @dbus_service.getter
    def get_use_color_names(self, app_name: str | None = None) -> bool:
        """Returns whether colors are announced by name or as RGB values."""

        return self._get_setting(self.KEY_USE_COLOR_NAMES, "b", True, app_name=app_name)

    @dbus_service.setter
    def set_use_color_names(self, value: bool) -> bool:
        """Sets whether colors are announced by name or as RGB values."""

        msg = f"SPEECH MANAGER: Setting use color names to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self.SPEECH_SCHEMA,
            self.KEY_USE_COLOR_NAMES,
            value,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_INSERT_PAUSES_BETWEEN_UTTERANCES,
        schema="speech",
        gtype="b",
        default=True,
        summary="Insert pauses between utterances",
        migration_key="enablePauseBreaks",
    )
    @dbus_service.getter
    def get_insert_pauses_between_utterances(self, app_name: str | None = None) -> bool:
        """Returns whether pauses are inserted between utterances, e.g. between name and role."""

        return self._get_setting(
            self.KEY_INSERT_PAUSES_BETWEEN_UTTERANCES, "b", True, app_name=app_name
        )

    @dbus_service.setter
    def set_insert_pauses_between_utterances(self, value: bool) -> bool:
        """Sets whether pauses are inserted between utterances, e.g. between name and role."""

        msg = f"SPEECH MANAGER: Setting insert pauses to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self.SPEECH_SCHEMA,
            self.KEY_INSERT_PAUSES_BETWEEN_UTTERANCES,
            value,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_USE_PRONUNCIATION_DICTIONARY,
        schema="speech",
        gtype="b",
        default=True,
        summary="Apply user pronunciation dictionary",
        migration_key="usePronunciationDictionary",
    )
    @dbus_service.getter
    def get_use_pronunciation_dictionary(self, app_name: str | None = None) -> bool:
        """Returns whether the user's pronunciation dictionary should be applied."""

        return self._get_setting(
            self.KEY_USE_PRONUNCIATION_DICTIONARY, "b", True, app_name=app_name
        )

    @dbus_service.setter
    def set_use_pronunciation_dictionary(self, value: bool) -> bool:
        """Sets whether the user's pronunciation dictionary should be applied."""

        msg = f"SPEECH MANAGER: Setting use pronunciation dictionary to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self.SPEECH_SCHEMA,
            self.KEY_USE_PRONUNCIATION_DICTIONARY,
            value,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_AUTO_LANGUAGE_SWITCHING,
        schema="speech",
        gtype="b",
        default=True,
        summary="Automatically switch voice based on document content language",
        migration_key="enableAutoLanguageSwitching",
    )
    @dbus_service.getter
    def get_auto_language_switching(self, app_name: str | None = None) -> bool:
        """Returns whether automatic language switching for document content is enabled."""

        return self._get_setting(self.KEY_AUTO_LANGUAGE_SWITCHING, "b", True, app_name=app_name)

    @dbus_service.setter
    def set_auto_language_switching(self, value: bool) -> bool:
        """Sets whether automatic language switching for document content is enabled."""

        msg = f"SPEECH MANAGER: Setting auto language switching for content to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self.SPEECH_SCHEMA,
            self.KEY_AUTO_LANGUAGE_SWITCHING,
            value,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_AUTO_LANGUAGE_SWITCHING_UI,
        schema="speech",
        gtype="b",
        default=False,
        summary="Automatically switch voice based on UI element language",
    )
    @dbus_service.getter
    def get_auto_language_switching_ui(self, app_name: str | None = None) -> bool:
        """Returns whether automatic language switching for UI elements is enabled."""

        return self._get_setting(self.KEY_AUTO_LANGUAGE_SWITCHING_UI, "b", False, app_name=app_name)

    @dbus_service.setter
    def set_auto_language_switching_ui(self, value: bool) -> bool:
        """Sets whether automatic language switching for UI elements is enabled."""

        msg = f"SPEECH MANAGER: Setting auto language switching for UI to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self.SPEECH_SCHEMA,
            self.KEY_AUTO_LANGUAGE_SWITCHING_UI,
            value,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_ONLY_SWITCH_CONFIGURED_LANGUAGES,
        schema="speech",
        gtype="b",
        default=False,
        summary="Only switch languages that have a configured voice set",
    )
    @dbus_service.getter
    def get_only_switch_configured_languages(self, app_name: str | None = None) -> bool:
        """Returns whether language switching is limited to configured voice sets."""

        return self._get_setting(
            self.KEY_ONLY_SWITCH_CONFIGURED_LANGUAGES, "b", False, app_name=app_name
        )

    @dbus_service.setter
    def set_only_switch_configured_languages(self, value: bool) -> bool:
        """Sets whether language switching is limited to configured voice sets."""

        msg = f"SPEECH MANAGER: Setting only switch configured languages to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self.SPEECH_SCHEMA,
            self.KEY_ONLY_SWITCH_CONFIGURED_LANGUAGES,
            value,
        )
        return True

    @dbus_service.command
    def toggle_speech(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Toggles speech on and off."""

        tokens = [
            "SPEECH MANAGER: toggle_speech. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if script is not None:
            presentation_manager.get_manager().interrupt_presentation()
        if self.get_speech_is_muted():
            self.set_speech_is_muted(False)
            if script is not None and notify_user:
                presentation_manager.get_manager().present_message(messages.SPEECH_ENABLED)
        elif not self.get_speech_is_enabled():
            gsettings_registry.get_registry().set_runtime_value(
                self.SPEECH_SCHEMA, self.KEY_ENABLE, True
            )
            self._init_server()
            if script is not None and notify_user:
                presentation_manager.get_manager().present_message(messages.SPEECH_ENABLED)
        else:
            if script is not None and notify_user:
                presentation_manager.get_manager().present_message(messages.SPEECH_DISABLED)
            gsettings_registry.get_registry().remove_runtime_value(
                self.SPEECH_SCHEMA, self.KEY_ENABLE
            )
            if not self.get_speech_is_enabled():
                self.shutdown_speech()
            else:
                self.set_speech_is_muted(True)
        return True

    def create_voices_preferences_grid(self, app_name: str = "") -> VoicesPreferencesGrid:
        """Returns the GtkGrid containing the voices preferences UI."""

        # pylint: disable-next=import-outside-toplevel
        from .speech_manager_preferences_grid import VoicesPreferencesGrid

        return VoicesPreferencesGrid(self, app_name=app_name)

    def create_voice_types_preferences_grid(
        self, voices_grid: VoicesPreferencesGrid
    ) -> VoiceTypesPreferencesGrid:
        """Returns the GtkGrid containing the voice types preferences UI."""

        # pylint: disable-next=import-outside-toplevel
        from .speech_manager_preferences_grid import VoiceTypesPreferencesGrid

        return VoiceTypesPreferencesGrid(voices_grid)


_manager: SpeechManager = SpeechManager()


def get_manager() -> SpeechManager:
    """Returns the Speech Manager"""

    return _manager
