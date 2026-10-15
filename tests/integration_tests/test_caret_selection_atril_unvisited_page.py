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

"""Selection into a second PDF page which Atril has not displayed yet."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import caret_selection_helpers as commands
from .atril_helpers import (
    FIRST_PAGE,
    assert_step,
    selected_ranges,
    selection_session,
)
from .helpers import BrailleLine, capture
from .version_helpers import requires_atril_version

if TYPE_CHECKING:
    from .orca_fixtures import AtrilSession


@pytest.mark.native_app
@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason=(
        "Atril reports selection bounds (-1, -1) for a page that is not displayed: "
        "https://github.com/mate-desktop/atril/issues/734"
    ),
)
@requires_atril_version(1, 28, 7)
def test_selection_on_unvisited_page(atril: AtrilSession) -> None:
    """Retains the first page and selects text on the previously undisplayed second page."""

    # This file owns a fresh session: no earlier test can have rendered page two.
    with selection_session(atril, native=False):
        for _ in range(6):
            atril.orca.select_with_caret_navigator(commands.NEXT_LINE)
            capture(atril)
        assert selected_ranges(atril) == ([(0, len(FIRST_PAGE))], [])
        assert_step(
            atril,
            commands.NEXT_LINE,
            ["More pages!", "selected"],
            BrailleLine(1, "Here’s a new page.", "Here’s a new page.", "\x00" * 18),
            ([(0, len(FIRST_PAGE))], [(0, 11)]),
            native=False,
        )
