# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
# Copyright 2006-2009 Brailcom, o.p.s.
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
# pylint: disable=unused-argument
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments

"""Functionality for working with speech servers."""

from __future__ import annotations

import locale
from enum import Enum, StrEnum
from typing import TYPE_CHECKING, Any

from . import debug, gsettings_registry, guilabels
from .acss import ACSS
from .ax_utilities_debugging import AXUtilitiesDebugging


class VoiceType(StrEnum):
    """Voice type identifiers. Values match GSettings path components."""

    DEFAULT = "default"
    UPPERCASE = "uppercase"
    HYPERLINK = "hyperlink"
    SYSTEM = "system"


@gsettings_registry.get_registry().gsettings_enum(
    "org.gnome.Orca.PunctuationStyle",
    values={"all": 0, "most": 1, "some": 2, "none": 3},
)
class PunctuationStyle(Enum):
    """Punctuation style enumeration."""

    NONE = 3
    SOME = 2
    MOST = 1
    ALL = 0

    @property
    def string_name(self) -> str:
        """Returns the lowercase string name for this enum value."""

        return self.name.lower()


@gsettings_registry.get_registry().gsettings_enum(
    "org.gnome.Orca.CapitalizationStyle",
    values={"none": 0, "spell": 1, "icon": 2},
)
class CapitalizationStyle(Enum):
    """Capitalization style enumeration with string values from settings."""

    NONE = "none"
    SPELL = "spell"
    ICON = "icon"

    @property
    def string_name(self) -> str:
        """Returns the lowercase string name for this enum value."""

        return self.name.lower()


if TYPE_CHECKING:
    from collections.abc import Callable, Iterator
    from typing import ClassVar

    import gi

    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

    from . import input_event


class VoiceFamily(dict):
    """Holds the family description for a voice."""

    NAME = "name"
    GENDER = "gender"
    LANG = "lang"
    DIALECT = "dialect"
    VARIANT = "variant"

    MALE = "male"
    FEMALE = "female"

    settings: ClassVar[dict[str, str | None]] = {
        NAME: None,
        GENDER: None,
        LANG: None,
        DIALECT: None,
        VARIANT: None,
    }

    def __init__(self, props: dict[str, Any] | None) -> None:
        """Create and initialize VoiceFamily."""
        dict.__init__(self)

        self.update(VoiceFamily.settings)
        if props:
            self.update(props)


class SayAllContext:
    """Contains information about the current state of a Say All operation."""

    PROGRESS = 0
    INTERRUPTED = 1
    COMPLETED = 2

    def __init__(
        self,
        obj: Atspi.Accessible,
        utterance: str,
        start_offset: int = -1,
        end_offset: int = -1,
    ) -> None:
        self.obj = obj
        self.utterance = utterance
        self.start_offset = start_offset
        self.end_offset = end_offset
        self.current_offset = start_offset
        self.current_end_offset = None

    def __str__(self) -> str:
        obj_string = AXUtilitiesDebugging.as_string(self.obj)
        return (
            f"SAY ALL: {obj_string} '{self.utterance}' ({self.start_offset}-{self.end_offset}, "
            f"current: {self.current_offset})"
        )

    def copy(self) -> SayAllContext:
        """Returns a copy of this SayAllContext."""

        new = SayAllContext(self.obj, self.utterance, self.start_offset, self.end_offset)
        new.current_offset = self.current_offset
        new.current_end_offset = self.current_end_offset
        return new

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SayAllContext):
            return False
        return (
            self.start_offset == other.start_offset
            and self.end_offset == other.end_offset
            and self.obj == other.obj
            and self.utterance == other.utterance
        )

    def __hash__(self) -> int:
        return hash((self.start_offset, self.end_offset, self.obj, self.utterance))


class SpeechServer:
    """Provides speech server abstraction."""

    _LOG_PREFIX: ClassVar[str] = "SPEECH"
    _active_servers: ClassVar[dict[str, SpeechServer]] = {}

    DEFAULT_SERVER_ID = "default"
    _SERVER_NAMES: ClassVar[dict[str, str]] = {
        DEFAULT_SERVER_ID: guilabels.DEFAULT_SYNTHESIZER,
    }

    _ACSS_DEFAULTS: ClassVar[tuple[tuple[str, Any], ...]] = (
        (ACSS.FAMILY, {}),
        (ACSS.RATE, 50),
        (ACSS.AVERAGE_PITCH, 5.0),
        (ACSS.PITCH_RANGE, 5.0),
        (ACSS.GAIN, 10.0),
    )

    def __init__(self, server_id: str = "") -> None:
        self._id = server_id
        self._default_voice: dict[str, Any] = {}
        self._default_voice_name: str = ""
        self._current_voice_properties: dict[str, Any] = {}
        self._current_punctuation_level: PunctuationStyle = PunctuationStyle.MOST

    @staticmethod
    def get_factory_name() -> str:
        """Returns a localized name describing this factory."""

        return ""

    @staticmethod
    def get_speech_servers() -> list[Any]:
        """Returns a list of available speech servers."""

        return []

    @classmethod
    def _get_speech_server(cls, server_id: str) -> SpeechServer | None:
        """Return an active server for given id.

        Attempt to create the server if it doesn't exist yet.  Returns None
        when it is not possible to create the server.
        """

        if server_id not in cls._active_servers:
            cls(server_id)
        return cls._active_servers.get(server_id)

    @classmethod
    def get_speech_server(cls, info: list[str] | None = None) -> SpeechServer | None:
        """Gets a given SpeechServer based upon the [name, id] info."""

        this_id = info[1] if info is not None else cls.DEFAULT_SERVER_ID
        return cls._get_speech_server(this_id)

    @classmethod
    def shutdown_active_servers(cls) -> None:
        """Cleans up and shuts down this factory."""

        servers = list(cls._active_servers.values())
        for server in servers:
            server.shutdown()

    def get_info(self) -> list[str]:
        """Returns [name, id] of the current speech server."""

        return [self._SERVER_NAMES.get(self._id, self._id), self._id]

    def get_voice_families(self) -> list[VoiceFamily]:
        """Returns a list of all known VoiceFamily instances provided by the server."""

        return []

    def _get_default_voice_language(
        self,
        voices: tuple[tuple[str, str, str | None], ...],
    ) -> str:
        """Returns the default language string based on the current locale and available voices."""

        current_locale = locale.getlocale(locale.LC_MESSAGES)[0]
        if current_locale is None or "_" not in current_locale:
            return ""

        locale_lang, locale_dialect = current_locale.split("_")
        locale_language = f"{locale_lang}-{locale_dialect}"
        for _name, lang, _variant in voices:
            if lang == locale_language:
                return locale_language
        for _name, lang, _variant in voices:
            if lang == locale_lang:
                return locale_lang
        return locale_language

    def _build_voice_families(
        self,
        voices: tuple[tuple[str, str, str | None], ...],
    ) -> list[VoiceFamily]:
        """Builds VoiceFamily list from raw voice tuples, prepending the default voice."""

        default_lang = self._get_default_voice_language(voices)
        voices = ((self._default_voice_name, default_lang, None), *voices)

        families = []
        for name, lang, variant in voices:
            families.append(
                VoiceFamily(
                    {
                        VoiceFamily.NAME: name,
                        VoiceFamily.LANG: lang.partition("-")[0],
                        VoiceFamily.DIALECT: lang.partition("-")[2],
                        VoiceFamily.VARIANT: variant,
                    },
                ),
            )
        return families

    def get_voice_family(self) -> VoiceFamily:
        """Returns the current voice family as a VoiceFamily dictionary."""

        return VoiceFamily({})

    def set_voice_family(self, family: VoiceFamily) -> None:
        """Sets the voice family to family VoiceFamily dictionary."""

    def speak_character(
        self,
        character: str,
        acss: ACSS | None = None,
        cap_style: CapitalizationStyle | None = None,
    ) -> None:
        """Speaks character."""

    def speak_key_event(self, event: input_event.KeyboardEvent, acss: ACSS | None = None) -> None:
        """Speaks event."""

    def speak(self, text: str | None = None, acss: ACSS | None = None) -> None:
        """Speaks text using the voice specified by acss."""

    def say_all(
        self,
        utterance_iterator: Iterator[tuple[SayAllContext, ACSS]],
        progress_callback: Callable[[SayAllContext, int], None],
    ) -> None:
        """Iterates through the given utterance_iterator, speaking each utterance."""

    def set_default_voice(self, default_voice: dict[str, Any]) -> None:
        """Sets the default voice ACSS properties for fallback use."""

        self._default_voice = default_voice

    def _apply_acss(self, acss: dict[str, Any] | None) -> None:
        """Merges default voice with acss and stores in current voice properties."""

        merged: dict[str, Any] = dict(self._default_voice)
        if acss is not None:
            merged.update(acss)
        for acss_property, default in self._ACSS_DEFAULTS:
            self._current_voice_properties[acss_property] = merged.get(acss_property, default)

    def _change_default_speech_rate(self, step: int, decrease: bool = False) -> None:
        delta = step * (-1 if decrease else 1)
        rate = self._default_voice.get(ACSS.RATE, 50)
        new_rate = max(0, min(100, rate + delta))
        self._default_voice[ACSS.RATE] = new_rate
        self._current_voice_properties[ACSS.RATE] = new_rate
        msg = f"{self._LOG_PREFIX}: Rate set to {new_rate}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def _change_default_speech_pitch(self, step: float, decrease: bool = False) -> None:
        delta = step * (-1 if decrease else 1)
        pitch = self._default_voice.get(ACSS.AVERAGE_PITCH, 5)
        new_pitch = max(0, min(10, pitch + delta))
        self._default_voice[ACSS.AVERAGE_PITCH] = new_pitch
        self._current_voice_properties[ACSS.AVERAGE_PITCH] = new_pitch
        msg = f"{self._LOG_PREFIX}: Pitch set to {new_pitch}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def _change_default_speech_volume(self, step: float, decrease: bool = False) -> None:
        delta = step * (-1 if decrease else 1)
        volume = self._default_voice.get(ACSS.GAIN, 10)
        new_volume = max(0, min(10, volume + delta))
        self._default_voice[ACSS.GAIN] = new_volume
        self._current_voice_properties[ACSS.GAIN] = new_volume
        msg = f"{self._LOG_PREFIX}: Volume set to {new_volume}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def _change_default_speech_pitch_range(self, step: float, decrease: bool = False) -> None:
        delta = step * (-1 if decrease else 1)
        pitch_range = self._default_voice.get(ACSS.PITCH_RANGE, 5)
        new_pitch_range = max(0, min(10, pitch_range + delta))
        self._default_voice[ACSS.PITCH_RANGE] = new_pitch_range
        self._current_voice_properties[ACSS.PITCH_RANGE] = new_pitch_range
        msg = f"{self._LOG_PREFIX}: Pitch range set to {new_pitch_range}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def increase_speech_rate(self, step: int = 5) -> None:
        """Increases the speech rate."""

        self._change_default_speech_rate(step)

    def decrease_speech_rate(self, step: int = 5) -> None:
        """Decreases the speech rate."""

        self._change_default_speech_rate(step, decrease=True)

    def increase_speech_pitch(self, step: float = 0.5) -> None:
        """Increases the speech pitch."""

        self._change_default_speech_pitch(step)

    def decrease_speech_pitch(self, step: float = 0.5) -> None:
        """Decreases the speech pitch."""

        self._change_default_speech_pitch(step, decrease=True)

    def increase_speech_volume(self, step: float = 0.5) -> None:
        """Increases the speech volume."""

        self._change_default_speech_volume(step)

    def decrease_speech_volume(self, step: float = 0.5) -> None:
        """Decreases the speech volume."""

        self._change_default_speech_volume(step, decrease=True)

    def increase_speech_inflection(self, step: float = 0.5) -> None:
        """Increases the speech inflection (pitch range)."""

        self._change_default_speech_pitch_range(step)

    def decrease_speech_inflection(self, step: float = 0.5) -> None:
        """Decreases the speech inflection (pitch range)."""

        self._change_default_speech_pitch_range(step, decrease=True)

    def update_capitalization_style(self, style: str) -> None:
        """Updates the capitalization style used by the speech server."""

    def update_punctuation_level(self, level: PunctuationStyle) -> None:
        """Punctuation level changed, inform this speechServer."""

        self._current_punctuation_level = level

    def stop(self) -> None:
        """Stops ongoing speech and flushes the queue."""

    def shutdown(self) -> None:
        """Shuts down the speech engine."""

    def reset(self) -> None:
        """Resets the speech engine."""

    def clear_cached_voice_properties(self) -> None:
        """Clear cached voice properties to force reapplication on next speech."""

        msg = f"{self._LOG_PREFIX}: Clearing cached voice properties"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self._current_voice_properties.clear()

    def get_output_module(self) -> str:
        """Returns the output module associated with this speech server."""

        return ""

    def set_output_module(self, module_id: str) -> None:
        """Sets the output module associated with this speech server."""

    def list_output_modules(self) -> tuple[str, ...]:
        """Return names of available output modules as a tuple of strings."""

        return ()

    def get_voice_families_for_language(
        self,
        language: str,
        dialect: str = "",
        variant: str | None = None,
        maximum: int | None = None,
    ) -> list[tuple[str, str, str | None]]:
        """Returns the families for language available in the current synthesizer."""

        return []

    def _filter_voices_for_language(
        self,
        voices: tuple[tuple[str, str, str | None], ...] | list[tuple[str, str, str | None]],
        target_language: str,
        target_dialect: str,
        variant: str | None = None,
        maximum: int | None = None,
    ) -> tuple[list[tuple[str, str, str | None]], list[tuple[str, str, str | None]]]:
        """Filters voices by language and dialect, returning candidates and fallbacks."""

        candidates: list[tuple[str, str, str | None]] = []
        fallbacks: list[tuple[str, str, str | None]] = []
        for voice in voices:
            normalized_language, normalized_dialect = self._normalized_language_and_dialect(
                voice[1],
            )
            if normalized_language != target_language:
                continue
            if variant not in (None, "none", "None") and voice[2] != variant:
                continue
            if normalized_dialect == target_dialect or (
                not normalized_dialect and target_dialect == normalized_language
            ):
                candidates.append(voice)
            elif not target_dialect:
                if normalized_dialect == target_language:
                    candidates.append(voice)
                if len(normalized_dialect) == 2:
                    fallbacks.append(voice)
            if maximum is not None and len(candidates) >= maximum:
                break
        return candidates, fallbacks

    def _get_language_and_dialect(self, acss_family: dict[str, Any] | None) -> tuple[str, str]:
        """Returns the language and dialect from the ACSS family dictionary."""

        if acss_family is None:
            acss_family = {}

        language = acss_family.get(VoiceFamily.LANG)
        dialect = acss_family.get(VoiceFamily.DIALECT)

        if not language:
            family_locale, _encoding = locale.getlocale()

            language, dialect = "", ""
            if family_locale:
                locale_values = family_locale.split("_")
                language = locale_values[0]
                if len(locale_values) == 2:
                    dialect = locale_values[1]

        return str(language), str(dialect)

    def _normalized_language_and_dialect(self, language: str, dialect: str = "") -> tuple[str, str]:
        """Attempts to ensure consistency across inconsistent formats."""

        if "-" in language:
            normalized_language = language.split("-", 1)[0].lower()
            normalized_dialect = language.split("-", 1)[-1].lower()
        else:
            normalized_language = language.lower()
            normalized_dialect = dialect.lower()

        return normalized_language, normalized_dialect

    def get_language_and_dialect(self, acss_family: dict[str, Any] | None) -> tuple[str, str]:
        """Returns the language and dialect from the ACSS family dictionary."""

        return self._get_language_and_dialect(acss_family)
