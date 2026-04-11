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

# pylint: disable=too-many-public-methods

"""Provides MathCAT-based math presentation support for speech and braille."""

from __future__ import annotations

import contextlib
import locale
import os
from enum import Enum
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
from .extension import Extension

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


@gsettings_registry.get_registry().gsettings_enum(
    "org.gnome.Orca.MathCopyFormat",
    values={"mathml": 0, "latex": 1, "asciimath": 2, "speech": 3},
)
class MathCopyFormat(Enum):
    """Format for copying math content to the clipboard."""

    MATHML = 0
    LATEX = 1
    ASCIIMATH = 2
    SPEECH = 3


@gsettings_registry.get_registry().gsettings_enum(
    "org.gnome.Orca.MathNavMode",
    values={"enhanced": 0, "simple": 1, "character": 2},
)
class MathNavMode(Enum):
    """Navigation granularity for math exploration."""

    ENHANCED = 0
    SIMPLE = 1
    CHARACTER = 2


@gsettings_registry.get_registry().gsettings_enum(
    "org.gnome.Orca.MathBrailleNavHighlight",
    values={"off": 0, "first-char": 1, "end-points": 2, "all": 3},
)
class MathBrailleNavHighlight(Enum):
    """Braille navigation highlight style for the current math node."""

    OFF = 0
    FIRST_CHAR = 1
    END_POINTS = 2
    ALL = 3


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
            preferences_grid_base.EnumPreferenceControl(
                label=guilabels.MATH_COPY_FORMAT,
                options=["MathML", "LaTeX", "ASCIIMath", guilabels.SPEECH],
                values=["mathml", "latex", "asciimath", "speech"],
                getter=presenter.get_copy_format,
                setter=presenter.set_copy_format,
                prefs_key=MathPresenter.KEY_COPY_FORMAT,
            ),
            preferences_grid_base.EnumPreferenceControl(
                label=guilabels.MATH_NAV_MODE,
                options=[
                    guilabels.MATH_NAV_MODE_ENHANCED,
                    guilabels.MATH_NAV_MODE_SIMPLE,
                    guilabels.MATH_NAV_MODE_CHARACTER,
                ],
                values=["enhanced", "simple", "character"],
                getter=presenter.get_nav_mode,
                setter=presenter.set_nav_mode,
                prefs_key=MathPresenter.KEY_NAV_MODE,
            ),
            preferences_grid_base.EnumPreferenceControl(
                label=guilabels.MATH_BRAILLE_NAV_HIGHLIGHT,
                options=[
                    guilabels.MATH_BRAILLE_HIGHLIGHT_NONE,
                    guilabels.MATH_BRAILLE_HIGHLIGHT_FIRST_CHAR,
                    guilabels.MATH_BRAILLE_HIGHLIGHT_END_POINTS,
                    guilabels.MATH_BRAILLE_HIGHLIGHT_ALL,
                ],
                values=["off", "first-char", "end-points", "all"],
                getter=presenter.get_braille_nav_highlight,
                setter=presenter.set_braille_nav_highlight,
                prefs_key=MathPresenter.KEY_BRAILLE_NAV_HIGHLIGHT,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.MATH_AUTO_ZOOM_OUT,
                getter=presenter.get_auto_zoom_out,
                setter=presenter.set_auto_zoom_out,
                prefs_key=MathPresenter.KEY_AUTO_ZOOM_OUT,
            ),
        ]
        super().__init__(guilabels.MATH_PRESENTATION, controls)


@gsettings_registry.get_registry().gsettings_schema(
    "org.gnome.Orca.MathPresentation", name="math-presentation"
)
class MathPresenter(Extension):
    """Provides MathCAT-based math presentation support."""

    MODULE_NAME = "MathPresenter"

    _SCHEMA = "math-presentation"

    KEY_LANGUAGE = "language"
    KEY_SPEECH_STYLE = "speech-style"
    KEY_VERBOSITY = "verbosity"
    KEY_BRAILLE_CODE = "braille-code"
    KEY_COPY_FORMAT = "copy-format"
    KEY_NAV_MODE = "nav-mode"
    KEY_BRAILLE_NAV_HIGHLIGHT = "braille-nav-highlight"
    KEY_AUTO_ZOOM_OUT = "auto-zoom-out"

    def __init__(self) -> None:
        self._initialized = False
        self._available = False
        super().__init__()

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

        system_locale = locale.getlocale()[0]
        if system_locale:
            return system_locale.split("_")[0]

        return "en"

    def _apply_preferences(self) -> None:
        """Applies stored preferences to MathCAT."""

        if lang_code := self._resolve_language():
            try:
                supported = libmathcat_py.GetSupportedLanguages()
            except OSError as err:
                msg = f"MATH PRESENTER: GetSupportedLanguages failed: {err}"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                supported = []

            if lang_code not in supported:
                msg = f"MATH PRESENTER: Language {lang_code} not supported, "
                if "en" in supported:
                    lang_code = "en"
                elif supported:
                    lang_code = supported[0]
                else:
                    lang_code = ""
                msg += f"falling back to {lang_code!r}"
                debug.print_message(debug.LEVEL_INFO, msg, True)

            if lang_code:
                libmathcat_py.SetPreference("Language", lang_code)
                msg = f"MATH PRESENTER: Language set to {lang_code}"
                debug.print_message(debug.LEVEL_INFO, msg, True)

        if speech_style := self.get_speech_style():
            libmathcat_py.SetPreference("SpeechStyle", speech_style)

        if verbosity := self.get_verbosity():
            libmathcat_py.SetPreference("Verbosity", verbosity)

        if braille_code := self.get_braille_code():
            libmathcat_py.SetPreference("BrailleCode", braille_code)

        if nav_mode := self.get_nav_mode():
            libmathcat_py.SetPreference("NavMode", nav_mode.capitalize())

        if braille_highlight := self.get_braille_nav_highlight():
            nick_to_mathcat = {
                "off": "Off",
                "first-char": "FirstChar",
                "end-points": "EndPoints",
                "all": "All",
            }
            libmathcat_py.SetPreference(
                "BrailleNavHighlight",
                nick_to_mathcat.get(braille_highlight, "Off"),
            )

        libmathcat_py.SetPreference("AutoZoomOut", str(self.get_auto_zoom_out()).lower())

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

    @gsettings_registry.get_registry().gsetting(
        key=KEY_COPY_FORMAT,
        schema="math-presentation",
        genum="org.gnome.Orca.MathCopyFormat",
        default="mathml",
        summary="Format for copying math content to clipboard",
        migration_key="mathCopyFormat",
    )
    @dbus_service.getter
    def get_copy_format(self) -> str:
        """Returns the format used when copying math content."""

        return gsettings_registry.get_registry().layered_lookup(
            self._SCHEMA,
            self.KEY_COPY_FORMAT,
            "",
            genum="org.gnome.Orca.MathCopyFormat",
            default="mathml",
        )

    @dbus_service.setter
    def set_copy_format(self, value: str) -> bool:
        """Sets the format used when copying math content."""

        msg = f"MATH PRESENTER: Setting copy format to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_COPY_FORMAT,
            value,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_NAV_MODE,
        schema="math-presentation",
        genum="org.gnome.Orca.MathNavMode",
        default="enhanced",
        summary="Math navigation granularity (enhanced, simple, character)",
        migration_key="mathNavMode",
    )
    @dbus_service.getter
    def get_nav_mode(self) -> str:
        """Returns the math navigation mode."""

        return gsettings_registry.get_registry().layered_lookup(
            self._SCHEMA,
            self.KEY_NAV_MODE,
            "",
            genum="org.gnome.Orca.MathNavMode",
            default="enhanced",
        )

    @dbus_service.setter
    def set_nav_mode(self, value: str) -> bool:
        """Sets the math navigation mode."""

        msg = f"MATH PRESENTER: Setting nav mode to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_NAV_MODE,
            value,
        )
        if self._available:
            mathcat_value = value.capitalize()
            libmathcat_py.SetPreference("NavMode", mathcat_value)
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_BRAILLE_NAV_HIGHLIGHT,
        schema="math-presentation",
        genum="org.gnome.Orca.MathBrailleNavHighlight",
        default="off",
        summary="Braille navigation highlight style (off, first-char, end-points, all)",
        migration_key="mathBrailleNavHighlight",
    )
    @dbus_service.getter
    def get_braille_nav_highlight(self) -> str:
        """Returns the braille navigation highlight style."""

        return gsettings_registry.get_registry().layered_lookup(
            self._SCHEMA,
            self.KEY_BRAILLE_NAV_HIGHLIGHT,
            "",
            genum="org.gnome.Orca.MathBrailleNavHighlight",
            default="off",
        )

    @dbus_service.setter
    def set_braille_nav_highlight(self, value: str) -> bool:
        """Sets the braille navigation highlight style."""

        msg = f"MATH PRESENTER: Setting braille nav highlight to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_BRAILLE_NAV_HIGHLIGHT,
            value,
        )
        if self._available:
            nick_to_mathcat = {
                "off": "Off",
                "first-char": "FirstChar",
                "end-points": "EndPoints",
                "all": "All",
            }
            libmathcat_py.SetPreference("BrailleNavHighlight", nick_to_mathcat.get(value, "Off"))
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_AUTO_ZOOM_OUT,
        schema="math-presentation",
        gtype="b",
        default=False,
        summary="Automatically exit 2D math structures when moving past the edge",
        migration_key="mathAutoZoomOut",
    )
    @dbus_service.getter
    def get_auto_zoom_out(self) -> bool:
        """Returns whether auto zoom out is enabled."""

        return gsettings_registry.get_registry().layered_lookup(
            self._SCHEMA,
            self.KEY_AUTO_ZOOM_OUT,
            "b",
            default=False,
        )

    @dbus_service.setter
    def set_auto_zoom_out(self, value: bool) -> bool:
        """Sets whether auto zoom out is enabled."""

        msg = f"MATH PRESENTER: Setting auto zoom out to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_AUTO_ZOOM_OUT,
            value,
        )
        if self._available:
            libmathcat_py.SetPreference("AutoZoomOut", str(value).lower())
        return True

    # pylint: disable-next=too-many-return-statements
    def get_navigation_content_for_copy(self) -> str:
        """Returns the current navigation node content in the configured copy format."""

        copy_format = self.get_copy_format()

        if copy_format == "mathml":
            try:
                mathml, _offset = libmathcat_py.GetNavigationMathML()
                return mathml.strip()
            except OSError as err:
                msg = f"MATH PRESENTER: GetNavigationMathML failed: {err}"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return ""

        if copy_format == "speech":
            try:
                return libmathcat_py.GetSpokenText()
            except OSError as err:
                msg = f"MATH PRESENTER: GetSpokenText failed: {err}"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return ""

        if copy_format in ("latex", "asciimath"):
            braille_code = "LaTeX" if copy_format == "latex" else "ASCIIMath"
            original_code = self.get_braille_code()
            try:
                libmathcat_py.SetPreference("BrailleCode", braille_code)
                return libmathcat_py.GetNavigationBraille()
            except OSError as err:
                msg = f"MATH PRESENTER: GetNavigationBraille({braille_code}) failed: {err}"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return ""
            finally:
                libmathcat_py.SetPreference("BrailleCode", original_code)

        return ""

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
        nav_mode = libmathcat_py.GetPreference("NavMode")
        msg = (
            f"MATH PRESENTER: Speech ({lang}, {style},"
            f" verbosity={verbosity}, nav={nav_mode}): {speech}"
        )
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
        highlight = libmathcat_py.GetPreference("BrailleNavHighlight")
        msg = f"MATH PRESENTER: Braille ({code}, highlight={highlight}): {braille}"
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
