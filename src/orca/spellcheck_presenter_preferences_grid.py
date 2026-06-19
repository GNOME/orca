# Orca
#
# Copyright 2014-2026 Igalia, S.L.
#
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

"""Preferences grid for spell check support."""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import guilabels, preferences_grid_base, spellcheck_presenter

if TYPE_CHECKING:
    from .spellcheck_presenter import SpellCheckPresenter


class SpellCheckPreferencesGrid(preferences_grid_base.AutoPreferencesGrid):
    """GtkGrid containing the Spell Check preferences page."""

    _gsettings_schema = "spellcheck"
    _documentation_summary = (
        "Use these settings to control what Orca announces while reviewing spelling and "
        "grammar suggestions."
    )

    @classmethod
    def get_documentation(cls) -> preferences_grid_base.PreferencePanelDoc:
        """Return documentation metadata for spell-check preferences."""

        return preferences_grid_base.PreferencePanelDoc(
            title=guilabels.SPELL_CHECK,
            panel_id="spellcheck_presenter.spell-check",
            description=guilabels.SPELL_CHECK_DESCRIPTION,
            schema="spellcheck",
            controls=(
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.SPELL_CHECK_SPELL_ERROR,
                    kind="switch",
                    summary=(
                        "Controls whether Orca spells out the current error after speaking it."
                    ),
                    schema="spellcheck",
                    key=spellcheck_presenter.SpellCheckPresenter.KEY_SPELL_ERROR,
                ),
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.SPELL_CHECK_SPELL_SUGGESTION,
                    kind="switch",
                    summary=(
                        "Controls whether Orca spells out the current suggestion after speaking it."
                    ),
                    schema="spellcheck",
                    key=spellcheck_presenter.SpellCheckPresenter.KEY_SPELL_SUGGESTION,
                ),
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.SPELL_CHECK_PRESENT_CONTEXT,
                    kind="switch",
                    summary=(
                        "Controls whether Orca presents the surrounding text in which the "
                        "mistake occurred."
                    ),
                    schema="spellcheck",
                    key=spellcheck_presenter.SpellCheckPresenter.KEY_PRESENT_CONTEXT,
                ),
            ),
        )

    def __init__(self, presenter: SpellCheckPresenter) -> None:
        controls = [
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.SPELL_CHECK_SPELL_ERROR,
                getter=presenter.get_spell_error,
                setter=presenter.set_spell_error,
                prefs_key=spellcheck_presenter.SpellCheckPresenter.KEY_SPELL_ERROR,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.SPELL_CHECK_SPELL_SUGGESTION,
                getter=presenter.get_spell_suggestion,
                setter=presenter.set_spell_suggestion,
                prefs_key=spellcheck_presenter.SpellCheckPresenter.KEY_SPELL_SUGGESTION,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.SPELL_CHECK_PRESENT_CONTEXT,
                getter=presenter.get_present_context,
                setter=presenter.set_present_context,
                prefs_key=spellcheck_presenter.SpellCheckPresenter.KEY_PRESENT_CONTEXT,
            ),
        ]

        super().__init__(
            guilabels.SPELL_CHECK,
            controls,
            info_message=guilabels.SPELL_CHECK_DESCRIPTION,
        )
