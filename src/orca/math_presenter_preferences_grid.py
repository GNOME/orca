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

"""Preferences grid for MathCAT presentation support."""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import guilabels, math_presenter, preferences_grid_base

if TYPE_CHECKING:
    from .math_presenter import MathPresenter


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
                prefs_key=math_presenter.MathPresenter.KEY_LANGUAGE,
            ),
            preferences_grid_base.EnumPreferenceControl(
                label=guilabels.MATH_SPEECH_STYLE,
                options=speech_styles,
                values=speech_styles,
                getter=presenter.get_speech_style,
                setter=presenter.set_speech_style,
                prefs_key=math_presenter.MathPresenter.KEY_SPEECH_STYLE,
            ),
            preferences_grid_base.EnumPreferenceControl(
                label=guilabels.VERBOSITY,
                options=verbosity_labels,
                values=verbosity_values,
                getter=presenter.get_verbosity,
                setter=presenter.set_verbosity,
                prefs_key=math_presenter.MathPresenter.KEY_VERBOSITY,
            ),
            preferences_grid_base.EnumPreferenceControl(
                label=guilabels.MATH_BRAILLE_CODE,
                options=braille_codes,
                values=braille_codes,
                getter=presenter.get_braille_code,
                setter=presenter.set_braille_code,
                prefs_key=math_presenter.MathPresenter.KEY_BRAILLE_CODE,
            ),
            preferences_grid_base.EnumPreferenceControl(
                label=guilabels.MATH_COPY_FORMAT,
                options=["MathML", "LaTeX", "ASCIIMath", guilabels.SPEECH],
                values=["mathml", "latex", "asciimath", "speech"],
                getter=presenter.get_copy_format,
                setter=presenter.set_copy_format,
                prefs_key=math_presenter.MathPresenter.KEY_COPY_FORMAT,
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
                prefs_key=math_presenter.MathPresenter.KEY_NAV_MODE,
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
                prefs_key=math_presenter.MathPresenter.KEY_BRAILLE_NAV_HIGHLIGHT,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.MATH_AUTO_ZOOM_OUT,
                getter=presenter.get_auto_zoom_out,
                setter=presenter.set_auto_zoom_out,
                prefs_key=math_presenter.MathPresenter.KEY_AUTO_ZOOM_OUT,
            ),
        ]
        super().__init__(guilabels.MATH_PRESENTATION, controls)
