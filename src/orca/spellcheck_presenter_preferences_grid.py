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

from . import guilabels, preferences_grid_base
from .help_metadata import (
    PreferenceCategoryDoc,
    PreferenceControlDoc,
    PreferencePanelDoc,
)
from .spellcheck_presenter_settings import SpellCheckSettings

if TYPE_CHECKING:
    from .spellcheck_presenter import SpellCheckPresenter


class SpellCheckPreferencesGrid(preferences_grid_base.AutoPreferencesGrid):
    """GtkGrid containing the Spell Check preferences page."""

    _gsettings_schema = "spellcheck"

    @classmethod
    def get_documentation(cls) -> PreferencePanelDoc:
        """Return documentation metadata for spell-check preferences."""

        return PreferencePanelDoc(
            title=guilabels.SPELL_CHECK,
            panel_id="spellcheck_presenter.spell-check",
            category=PreferenceCategoryDoc(
                category_id="spell-check",
                title="Spell Check",
                description=(
                    "Configure the information Orca presents while you use a supported "
                    "application's spell checker."
                ),
                panels=("spellcheck_presenter.spell-check",),
            ),
            schema="spellcheck",
            controls=(
                PreferenceControlDoc(
                    label=guilabels.SPELL_CHECK_SPELL_ERROR,
                    kind="switch",
                    summary=(
                        "Controls whether Orca spells out the current error after speaking it."
                    ),
                    schema="spellcheck",
                    key=SpellCheckSettings.KEY_SPELL_ERROR,
                ),
                PreferenceControlDoc(
                    label=guilabels.SPELL_CHECK_SPELL_SUGGESTION,
                    kind="switch",
                    summary=(
                        "Controls whether Orca spells out the current suggestion after speaking it."
                    ),
                    schema="spellcheck",
                    key=SpellCheckSettings.KEY_SPELL_SUGGESTION,
                ),
                PreferenceControlDoc(
                    label=guilabels.SPELL_CHECK_PRESENT_CONTEXT,
                    kind="switch",
                    summary=(
                        "Controls whether Orca presents the surrounding text in which the "
                        "mistake occurred."
                    ),
                    schema="spellcheck",
                    key=SpellCheckSettings.KEY_PRESENT_CONTEXT,
                ),
            ),
        )

    def __init__(self, presenter: SpellCheckPresenter) -> None:
        controls = [
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.SPELL_CHECK_SPELL_ERROR,
                getter=presenter.get_spell_error,
                setter=presenter.set_spell_error,
                prefs_key=SpellCheckSettings.KEY_SPELL_ERROR,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.SPELL_CHECK_SPELL_SUGGESTION,
                getter=presenter.get_spell_suggestion,
                setter=presenter.set_spell_suggestion,
                prefs_key=SpellCheckSettings.KEY_SPELL_SUGGESTION,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.SPELL_CHECK_PRESENT_CONTEXT,
                getter=presenter.get_present_context,
                setter=presenter.set_present_context,
                prefs_key=SpellCheckSettings.KEY_PRESENT_CONTEXT,
            ),
        ]

        super().__init__(
            guilabels.SPELL_CHECK,
            controls,
            info_message=guilabels.SPELL_CHECK_DESCRIPTION,
        )
