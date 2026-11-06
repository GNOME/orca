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

# pylint: disable=import-outside-toplevel

"""Shared private file tree and window preparation for file-manager tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def create_tree(root: Path) -> None:
    """Creates predictable navigation, selection, and scrolling targets."""

    for name in ("01 Empty", "02 Nested/Child", "02 Nested/Sibling/Child", "03 Scrolling"):
        (root / name).mkdir(parents=True)
    for name in (
        "alpha.txt",
        "bravo.txt",
        "charlie.txt",
        "delta.txt",
        "echo.txt",
        "file with spaces.txt",
        "golf.txt",
        "hotel.txt",
        "india.txt",
        "juliet.txt",
        "long filename for testing braille panning and file navigation.txt",
        ".hidden",
    ):
        (root / name).write_text("Test file.\n", encoding="utf-8")
    for index in range(1, 61):
        (root / "03 Scrolling" / f"item {index:02}.txt").write_text(
            "Test file.\n", encoding="utf-8"
        )


def prepare_window(pid: int) -> None:
    """Sizes and focuses the owned file-manager window on Xvfb, without a window manager."""

    from Xlib import X, display  # type: ignore[import-untyped]

    connection = display.Display()
    try:
        pid_atom = connection.intern_atom("_NET_WM_PID")
        for window in connection.screen().root.query_tree().children:
            owner = window.get_full_property(pid_atom, X.AnyPropertyType)
            if owner is None or owner.value[0] != pid:
                continue
            attributes = window.get_attributes()
            if attributes.map_state != X.IsViewable or attributes.win_class != X.InputOutput:
                continue
            window.configure(x=0, y=0, width=1023, height=767)
            window.set_input_focus(X.RevertToParent, X.CurrentTime)
            connection.sync()
            return
        raise RuntimeError(f"No mapped file-manager window found for pid {pid}")
    finally:
        connection.close()
