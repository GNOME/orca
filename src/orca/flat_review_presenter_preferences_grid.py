# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
# Copyright 2016-2026 Igalia, S.L.
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

"""Preferences grid for flat review support."""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import flat_review_presenter, guilabels, preferences_grid_base

if TYPE_CHECKING:
    from .flat_review_presenter import FlatReviewPresenter


class FlatReviewPreferencesGrid(preferences_grid_base.AutoPreferencesGrid):
    """GtkGrid containing the Flat Review preferences page."""

    _gsettings_schema = "flat-review"

    def __init__(self, presenter: FlatReviewPresenter) -> None:
        controls: list[preferences_grid_base.ControlType] = [
            preferences_grid_base.EnumPreferenceControl(
                label=guilabels.FLAT_REVIEW_FOLLOW_FOCUS,
                options=[
                    guilabels.FLAT_REVIEW_FOLLOW_ALWAYS,
                    guilabels.FLAT_REVIEW_FOLLOW_AUTOMATICALLY,
                    guilabels.FLAT_REVIEW_FOLLOW_NEVER,
                ],
                values=[
                    flat_review_presenter.FocusTracking.ON.value,
                    flat_review_presenter.FocusTracking.AUTO.value,
                    flat_review_presenter.FocusTracking.OFF.value,
                ],
                getter=presenter.get_focus_tracking,
                setter=presenter.set_focus_tracking,
                prefs_key=flat_review_presenter.FlatReviewPresenter.KEY_FOCUS_TRACKING,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.FLAT_REVIEW_SPEAK_UPDATES,
                getter=presenter.get_speaks_updates,
                setter=presenter.set_speaks_updates,
                prefs_key=flat_review_presenter.FlatReviewPresenter.KEY_SPEAK_UPDATES,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.FLAT_REVIEW_DISPLAY_UPDATES,
                getter=presenter.get_displays_updates,
                setter=presenter.set_displays_updates,
                prefs_key=flat_review_presenter.FlatReviewPresenter.KEY_DISPLAY_UPDATES,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.FLAT_REVIEW_RESTRICT,
                getter=presenter.get_is_restricted,
                setter=presenter.set_is_restricted,
                prefs_key=flat_review_presenter.FlatReviewPresenter.KEY_RESTRICTED,
            ),
        ]
        super().__init__(guilabels.FLAT_REVIEW, controls)
