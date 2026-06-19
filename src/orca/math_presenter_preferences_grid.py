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
    _documentation_summary = (
        "Use these settings to control speech, braille, copying, and navigation for math content."
    )

    @classmethod
    def get_documentation(cls) -> preferences_grid_base.PreferencePanelDoc:
        """Return documentation metadata for math presentation preferences."""

        return preferences_grid_base.PreferencePanelDoc(
            title=guilabels.MATH_PRESENTATION,
            panel_id="math_presenter.math-presentation",
            description=(
                "Math presentation settings control how Orca speaks, brailles, copies, "
                "and navigates mathematical expressions."
            ),
            schema="math-presentation",
            controls=(
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.LANGUAGE,
                    kind="combo",
                    summary="Selects the language Orca uses for math presentation.",
                    schema="math-presentation",
                    key=math_presenter.MathPresenter.KEY_LANGUAGE,
                    dynamic_values=True,
                ),
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.MATH_SPEECH_STYLE,
                    kind="combo",
                    summary="Selects the style Orca uses when speaking math.",
                    schema="math-presentation",
                    key=math_presenter.MathPresenter.KEY_SPEECH_STYLE,
                    dynamic_values=True,
                ),
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.VERBOSITY,
                    kind="combo",
                    summary="Selects how much detail Orca speaks for math.",
                    schema="math-presentation",
                    key=math_presenter.MathPresenter.KEY_VERBOSITY,
                    value_docs=(
                        preferences_grid_base.PreferenceValueDoc(
                            label=guilabels.MATH_VERBOSITY_TERSE,
                            value="Terse",
                            summary="Speaks less detail.",
                        ),
                        preferences_grid_base.PreferenceValueDoc(
                            label=guilabels.MATH_VERBOSITY_MEDIUM,
                            value="Medium",
                            summary="Speaks a moderate amount of detail.",
                        ),
                        preferences_grid_base.PreferenceValueDoc(
                            label=guilabels.MATH_VERBOSITY_VERBOSE,
                            value="Verbose",
                            summary="Speaks the most detail.",
                        ),
                    ),
                ),
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.MATH_BRAILLE_CODE,
                    kind="combo",
                    summary=("Selects the braille code Orca uses for mathematical expressions."),
                    schema="math-presentation",
                    key=math_presenter.MathPresenter.KEY_BRAILLE_CODE,
                    dynamic_values=True,
                ),
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.MATH_COPY_FORMAT,
                    kind="combo",
                    summary="Selects the format used when copying math content.",
                    schema="math-presentation",
                    key=math_presenter.MathPresenter.KEY_COPY_FORMAT,
                    values=("MathML", "LaTeX", "ASCIIMath", guilabels.SPEECH),
                ),
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.MATH_NAV_MODE,
                    kind="combo",
                    summary="Selects how Orca moves through math during navigation.",
                    schema="math-presentation",
                    key=math_presenter.MathPresenter.KEY_NAV_MODE,
                    value_docs=(
                        preferences_grid_base.PreferenceValueDoc(
                            label=guilabels.MATH_NAV_MODE_ENHANCED,
                            value="enhanced",
                            summary="Groups related items together for faster navigation.",
                        ),
                        preferences_grid_base.PreferenceValueDoc(
                            label=guilabels.MATH_NAV_MODE_SIMPLE,
                            value="simple",
                            summary="Visits each math element individually.",
                        ),
                        preferences_grid_base.PreferenceValueDoc(
                            label=guilabels.MATH_NAV_MODE_CHARACTER,
                            value="character",
                            summary="Visits individual symbols one at a time.",
                        ),
                    ),
                ),
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.MATH_BRAILLE_NAV_HIGHLIGHT,
                    kind="combo",
                    summary=("Selects how Orca marks the current math position in braille."),
                    schema="math-presentation",
                    key=math_presenter.MathPresenter.KEY_BRAILLE_NAV_HIGHLIGHT,
                    value_docs=(
                        preferences_grid_base.PreferenceValueDoc(
                            label=guilabels.MATH_BRAILLE_HIGHLIGHT_NONE,
                            value="off",
                            summary="Does not mark the current math position.",
                        ),
                        preferences_grid_base.PreferenceValueDoc(
                            label=guilabels.MATH_BRAILLE_HIGHLIGHT_FIRST_CHAR,
                            value="first-char",
                            summary="Marks the first cell of the current math item.",
                        ),
                        preferences_grid_base.PreferenceValueDoc(
                            label=guilabels.MATH_BRAILLE_HIGHLIGHT_END_POINTS,
                            value="end-points",
                            summary="Marks the first and last cells of the current math item.",
                        ),
                        preferences_grid_base.PreferenceValueDoc(
                            label=guilabels.MATH_BRAILLE_HIGHLIGHT_ALL,
                            value="all",
                            summary="Marks every cell of the current math item.",
                        ),
                    ),
                ),
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.MATH_AUTO_ZOOM_OUT,
                    kind="switch",
                    summary=(
                        "Controls whether Orca automatically exits a two-dimensional math "
                        "structure when you navigate past its edge."
                    ),
                    schema="math-presentation",
                    key=math_presenter.MathPresenter.KEY_AUTO_ZOOM_OUT,
                ),
            ),
        )

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
