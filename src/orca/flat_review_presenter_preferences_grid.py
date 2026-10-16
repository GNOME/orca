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
from .help_metadata import (
    PreferenceCategoryDoc,
    PreferenceControlDoc,
    PreferencePanelDoc,
    PreferenceValueDoc,
)

if TYPE_CHECKING:
    from .flat_review_presenter import FlatReviewPresenter


class FlatReviewPreferencesGrid(preferences_grid_base.AutoPreferencesGrid):
    """GtkGrid containing the Flat Review preferences page."""

    _gsettings_schema = "flat-review"

    @classmethod
    def get_documentation(cls) -> PreferencePanelDoc:
        """Return documentation metadata for flat review preferences."""

        return PreferencePanelDoc(
            title=guilabels.FLAT_REVIEW,
            panel_id="flat_review_presenter.flat-review",
            category=PreferenceCategoryDoc(
                category_id="flat-review",
                title="Flat Review",
                description=(
                    "Flat review lets you examine visible window content without moving focus "
                    "or the caret. Configure how it follows your location and presents updates."
                ),
                panels=("flat_review_presenter.flat-review",),
            ),
            command_groups=("commands.flat-review",),
            schema="flat-review",
            controls=(
                PreferenceControlDoc(
                    label=guilabels.FLAT_REVIEW_FOLLOW_FOCUS,
                    kind="choice",
                    summary=(
                        "Controls when the flat review location moves to follow the focus or caret."
                    ),
                    schema="flat-review",
                    key=flat_review_presenter.FlatReviewPresenter.KEY_FOCUS_TRACKING,
                    value_docs=(
                        PreferenceValueDoc(
                            label=guilabels.FLAT_REVIEW_FOLLOW_ALWAYS,
                            value="on",
                            summary=(
                                "Flat review moves whenever the focus or caret location changes."
                            ),
                        ),
                        PreferenceValueDoc(
                            label=guilabels.FLAT_REVIEW_FOLLOW_AUTOMATICALLY,
                            value="auto",
                            summary=(
                                "Orca decides when moving flat review to the focus or caret "
                                "location is useful."
                            ),
                        ),
                        PreferenceValueDoc(
                            label=guilabels.FLAT_REVIEW_FOLLOW_NEVER,
                            value="off",
                            summary="Flat review stays where you last moved it.",
                        ),
                    ),
                ),
                PreferenceControlDoc(
                    label=guilabels.FLAT_REVIEW_SPEAK_UPDATES,
                    kind="switch",
                    summary=(
                        "Controls whether Orca speaks content changes at the flat review location."
                    ),
                    schema="flat-review",
                    key=flat_review_presenter.FlatReviewPresenter.KEY_SPEAK_UPDATES,
                ),
                PreferenceControlDoc(
                    label=guilabels.FLAT_REVIEW_DISPLAY_UPDATES,
                    kind="switch",
                    summary=(
                        "Controls whether Orca refreshes braille when content changes at "
                        "the flat review location."
                    ),
                    schema="flat-review",
                    key=flat_review_presenter.FlatReviewPresenter.KEY_DISPLAY_UPDATES,
                ),
                PreferenceControlDoc(
                    label=guilabels.FLAT_REVIEW_RESTRICT,
                    kind="switch",
                    summary=(
                        "Controls whether flat review is limited to the current object "
                        "instead of the whole window."
                    ),
                    schema="flat-review",
                    key=flat_review_presenter.FlatReviewPresenter.KEY_RESTRICTED,
                ),
            ),
        )

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
