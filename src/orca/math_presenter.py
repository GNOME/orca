# Orca
#
# Copyright 2026 Igalia, S.L.
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

"""Provides MathCAT-based math presentation support for speech and braille."""

from __future__ import annotations

import contextlib
import locale
import os
from typing import TYPE_CHECKING

from . import (  # pylint: disable=no-name-in-module
    dbus_service,
    debug,
    gsettings_registry,
    guilabels,
    orca_platform,
    preferences_grid_base,
)
from .ax_utilities_math import AXUtilitiesMath

try:
    from . import libmathcat_py  # type: ignore[attr-defined]

    _LIB_AVAILABLE = True
except ImportError:
    libmathcat_py = None  # type: ignore[assignment]
    _LIB_AVAILABLE = False

if TYPE_CHECKING:
    import gi

    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi


class MathPreferencesGrid(preferences_grid_base.AutoPreferencesGrid):
    """Sub-grid for math settings within the Documents page."""

    _gsettings_schema = "math-presentation"

    def __init__(self, presenter: MathPresenter) -> None:
        languages = presenter.get_language_choices()
        speech_styles = presenter.get_speech_style_choices()
        braille_codes = presenter.get_braille_code_choices()
        verbosity_labels = [
            guilabels.MATH_VERBOSITY_TERSE,
            guilabels.MATH_VERBOSITY_MEDIUM,
            guilabels.MATH_VERBOSITY_VERBOSE,
        ]
        verbosity_values = ["Terse", "Medium", "Verbose"]
        controls: list[preferences_grid_base.ControlType] = [
            preferences_grid_base.EnumPreferenceControl(
                label=guilabels.LANGUAGE,
                options=languages,
                values=languages,
                getter=presenter.get_language,
                setter=presenter.set_language,
                prefs_key=MathPresenter.KEY_LANGUAGE,
            ),
            preferences_grid_base.EnumPreferenceControl(
                label=guilabels.MATH_SPEECH_STYLE,
                options=speech_styles,
                values=speech_styles,
                getter=presenter.get_speech_style,
                setter=presenter.set_speech_style,
                prefs_key=MathPresenter.KEY_SPEECH_STYLE,
            ),
            preferences_grid_base.EnumPreferenceControl(
                label=guilabels.VERBOSITY,
                options=verbosity_labels,
                values=verbosity_values,
                getter=presenter.get_verbosity,
                setter=presenter.set_verbosity,
                prefs_key=MathPresenter.KEY_VERBOSITY,
            ),
            preferences_grid_base.EnumPreferenceControl(
                label=guilabels.MATH_BRAILLE_CODE,
                options=braille_codes,
                values=braille_codes,
                getter=presenter.get_braille_code,
                setter=presenter.set_braille_code,
                prefs_key=MathPresenter.KEY_BRAILLE_CODE,
            ),
        ]
        super().__init__(guilabels.MATH_PRESENTATION, controls)


@gsettings_registry.get_registry().gsettings_schema(
    "org.gnome.Orca.MathPresentation", name="math-presentation"
)
class MathPresenter:
    """Provides MathCAT-based math presentation support."""

    _SCHEMA = "math-presentation"

    KEY_LANGUAGE = "language"
    KEY_SPEECH_STYLE = "speech-style"
    KEY_VERBOSITY = "verbosity"
    KEY_BRAILLE_CODE = "braille-code"

    def __init__(self) -> None:
        msg = "MATH PRESENTER: Registering D-Bus commands."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        controller = dbus_service.get_remote_controller()
        controller.register_decorated_module("MathPresenter", self)
        self._initialized = False
        self._available = False

    def _get_setting(self, key: str, gtype: str, default: str) -> str:
        """Returns the dconf value for key, or default if not in dconf."""

        return gsettings_registry.get_registry().layered_lookup(
            self._SCHEMA,
            key,
            gtype,
            default=default,
        )

    def _find_rules_dir(self) -> str:
        """Returns the path to the MathCAT Rules directory, or empty string if not found."""

        if configured_dir := orca_platform.mathcat_rules_dir:
            if os.path.isdir(configured_dir):
                return configured_dir

        return ""

    def initialize(self) -> None:
        """Initializes MathCAT. Called lazily on first use."""

        if self._initialized:
            return

        self._initialized = True

        if not _LIB_AVAILABLE:
            msg = "MATH PRESENTER: libmathcat_py module not found"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        if not (rules_dir := self._find_rules_dir()):
            msg = "MATH PRESENTER: No Rules directory found"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        try:
            libmathcat_py.SetRulesDir(rules_dir)
        except OSError as err:
            msg = f"MATH PRESENTER: SetRulesDir failed for {rules_dir}: {err}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        version = libmathcat_py.GetVersion()
        msg = f"MATH PRESENTER: Initialized version {version} with rules from {rules_dir}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        libmathcat_py.SetPreference("TTS", "none")
        self._available = True
        self._apply_preferences()

    def is_available(self) -> bool:
        """Returns True if MathCAT is loaded and initialized."""

        self.initialize()
        return self._available

    def _resolve_language(self) -> str:
        """Returns the language code to use, resolving 'Auto' to system locale."""

        lang = self.get_language()
        if lang and lang != "Auto":
            return lang

        return (locale.getlocale()[0] or "").split("_")[0]

    def _apply_preferences(self) -> None:
        """Applies stored preferences to MathCAT."""

        if lang_code := self._resolve_language():
            try:
                supported = libmathcat_py.GetSupportedLanguages()
            except OSError as err:
                msg = f"MATH PRESENTER: GetSupportedLanguages failed: {err}"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                supported = []

            if lang_code in supported:
                libmathcat_py.SetPreference("Language", lang_code)
                msg = f"MATH PRESENTER: Language set to {lang_code}"
                debug.print_message(debug.LEVEL_INFO, msg, True)
            else:
                msg = f"MATH PRESENTER: Language {lang_code} not supported"
                debug.print_message(debug.LEVEL_INFO, msg, True)

        if speech_style := self.get_speech_style():
            libmathcat_py.SetPreference("SpeechStyle", speech_style)

        if verbosity := self.get_verbosity():
            libmathcat_py.SetPreference("Verbosity", verbosity)

        if braille_code := self.get_braille_code():
            libmathcat_py.SetPreference("BrailleCode", braille_code)

    @gsettings_registry.get_registry().gsetting(
        key=KEY_LANGUAGE,
        schema="math-presentation",
        gtype="s",
        default="Auto",
        summary="Math speech language (Auto uses system locale)",
        migration_key="mathLanguage",
    )
    @dbus_service.getter
    def get_language(self) -> str:
        """Returns the current math language setting."""

        return self._get_setting(self.KEY_LANGUAGE, "s", "Auto")

    @dbus_service.setter
    def set_language(self, value: str) -> bool:
        """Sets the math language."""

        msg = f"MATH PRESENTER: Setting language to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA, self.KEY_LANGUAGE, value, "s"
        )
        if self._available:
            lang_code = value if value != "Auto" else (locale.getlocale()[0] or "").split("_")[0]
            libmathcat_py.SetPreference("Language", lang_code)
        return True

    def get_language_choices(self) -> list[str]:
        """Returns available languages, with 'Auto' as the first option."""

        choices = ["Auto"]
        if not self.is_available():
            return choices

        with contextlib.suppress(OSError):
            choices.extend(libmathcat_py.GetSupportedLanguages())
        return choices

    @gsettings_registry.get_registry().gsetting(
        key=KEY_SPEECH_STYLE,
        schema="math-presentation",
        gtype="s",
        default="ClearSpeak",
        summary="Math speech style",
        migration_key="mathSpeechStyle",
    )
    @dbus_service.getter
    def get_speech_style(self) -> str:
        """Returns the current math speech style."""

        return self._get_setting(self.KEY_SPEECH_STYLE, "s", "ClearSpeak")

    @dbus_service.setter
    def set_speech_style(self, value: str) -> bool:
        """Sets the math speech style."""

        msg = f"MATH PRESENTER: Setting speech style to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA, self.KEY_SPEECH_STYLE, value, "s"
        )
        if self._available:
            libmathcat_py.SetPreference("SpeechStyle", value)
        return True

    def get_speech_style_choices(self) -> list[str]:
        """Returns available speech styles."""

        if not self.is_available():
            return ["ClearSpeak", "SimpleSpeak"]

        try:
            lang = libmathcat_py.GetPreference("Language")
            return libmathcat_py.GetSupportedSpeechStyles(lang)
        except OSError:
            return ["ClearSpeak", "SimpleSpeak"]

    @gsettings_registry.get_registry().gsetting(
        key=KEY_VERBOSITY,
        schema="math-presentation",
        gtype="s",
        default="Medium",
        summary="Math speech verbosity",
        migration_key="mathVerbosity",
    )
    @dbus_service.getter
    def get_verbosity(self) -> str:
        """Returns the current math speech verbosity."""

        return self._get_setting(self.KEY_VERBOSITY, "s", "Medium")

    @dbus_service.setter
    def set_verbosity(self, value: str) -> bool:
        """Sets the math speech verbosity."""

        msg = f"MATH PRESENTER: Setting verbosity to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA, self.KEY_VERBOSITY, value, "s"
        )
        if self._available:
            libmathcat_py.SetPreference("Verbosity", value)
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_BRAILLE_CODE,
        schema="math-presentation",
        gtype="s",
        default="Nemeth",
        summary="Math braille code",
        migration_key="mathBrailleCode",
    )
    @dbus_service.getter
    def get_braille_code(self) -> str:
        """Returns the current math braille code."""

        return self._get_setting(self.KEY_BRAILLE_CODE, "s", "Nemeth")

    @dbus_service.setter
    def set_braille_code(self, value: str) -> bool:
        """Sets the math braille code."""

        msg = f"MATH PRESENTER: Setting braille code to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA, self.KEY_BRAILLE_CODE, value, "s"
        )
        if self._available:
            libmathcat_py.SetPreference("BrailleCode", value)
        return True

    def get_braille_code_choices(self) -> list[str]:
        """Returns available braille codes."""

        if not self.is_available():
            return ["Nemeth", "UEB"]

        try:
            return libmathcat_py.GetSupportedBrailleCodes()
        except OSError:
            return ["Nemeth", "UEB"]

    def create_preferences_grid(self) -> MathPreferencesGrid:
        """Returns the GtkGrid containing the math preferences UI."""

        return MathPreferencesGrid(self)

    def get_speech_for_math(self, obj: Atspi.Accessible) -> str:
        """Given a math accessible, returns MathCAT speech or empty string on failure."""

        if not self.is_available():
            return ""

        if not (mathml := AXUtilitiesMath.get_mathml(obj)):
            return ""

        try:
            libmathcat_py.SetMathML(mathml)
            speech = libmathcat_py.GetSpokenText()
        except OSError as err:
            msg = f"MATH PRESENTER: GetSpokenText failed: {err}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return ""

        lang = libmathcat_py.GetPreference("Language")
        style = libmathcat_py.GetPreference("SpeechStyle")
        verbosity = libmathcat_py.GetPreference("Verbosity")
        msg = f"MATH PRESENTER: Speech ({lang}, {style}, {verbosity}): {speech}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return speech

    def get_braille_for_math(self, obj: Atspi.Accessible) -> str:
        """Given a math accessible, returns MathCAT braille or empty string on failure."""

        if not self.is_available():
            return ""

        if not (mathml := AXUtilitiesMath.get_mathml(obj)):
            return ""

        try:
            libmathcat_py.SetMathML(mathml)
            braille = libmathcat_py.GetBraille("")
        except OSError as err:
            msg = f"MATH PRESENTER: GetBraille failed: {err}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return ""

        code = libmathcat_py.GetPreference("BrailleCode")
        msg = f"MATH PRESENTER: Braille ({code}): {braille}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return braille

    def get_where_am_i(self) -> str:
        """Returns MathCAT's where-am-I speech for the current navigation position."""

        try:
            return libmathcat_py.DoNavigateCommand("WhereAmI")
        except OSError as err:
            msg = f"MATH PRESENTER: WhereAmI failed: {err}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return ""

    def get_where_am_i_all(self) -> str:
        """Returns MathCAT's detailed where-am-I speech for the current navigation position."""

        try:
            return libmathcat_py.DoNavigateCommand("WhereAmIAll")
        except OSError as err:
            msg = f"MATH PRESENTER: WhereAmIAll failed: {err}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return ""


_presenter: MathPresenter = MathPresenter()


def get_presenter() -> MathPresenter:
    """Returns the Math Presenter"""

    return _presenter
