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

"""Launches Konsole with a fixed terminal size."""

from __future__ import annotations

import os
import shutil
import sys
import time
from pathlib import Path


def prepare_window(pid: int) -> None:
    """Waits for the owned Konsole window to be mapped, then focuses it on Xvfb."""

    from Xlib import X, display  # type: ignore[import-untyped]

    connection = display.Display()
    try:
        pid_atom = connection.intern_atom("_NET_WM_PID")
        deadline = time.monotonic() + 5.0
        while time.monotonic() < deadline:
            for window in connection.screen().root.query_tree().children:
                owner = window.get_full_property(pid_atom, X.AnyPropertyType)
                if owner is None or owner.value[0] != pid:
                    continue
                attributes = window.get_attributes()
                if attributes.map_state != X.IsViewable or attributes.win_class != X.InputOutput:
                    continue
                window.set_input_focus(X.RevertToParent, X.CurrentTime)
                connection.sync()
                return
            time.sleep(0.05)
        raise RuntimeError(f"No mapped Konsole window found for pid {pid} within 5 seconds")
    finally:
        connection.close()


def main() -> None:
    """Runs the requested program in Konsole."""

    os.environ["QT_QPA_PLATFORM"] = "xcb"
    os.environ["QT_LINUX_ACCESSIBILITY_ALWAYS_ON"] = "1"
    os.environ["QT_STYLE_OVERRIDE"] = "Fusion"
    config = Path(os.environ["XDG_CONFIG_HOME"])
    config.mkdir(parents=True, exist_ok=True)
    (config / "konsolerc").write_text(
        "[KonsoleWindow]\nRememberWindowSize=false\n",
        encoding="utf-8",
    )
    binary = shutil.which("konsole")
    assert binary is not None
    argv = [
        binary,
        "--separate",
        "--builtin-profile",
        "--hide-menubar",
        "--hide-tabbar",
        "--hide-toolbars",
    ]
    for setting in (
        "TerminalColumns=40",
        "TerminalRows=8",
        "HistoryMode=0",
        "ScrollBarPosition=2",
        # Keep 40 columns above Konsole's minimum window width.
        "Font=DejaVu Sans Mono,16",
        "BlinkingCursorEnabled=false",
    ):
        argv.extend(["-p", setting])
    env = [
        "TERM=xterm",
        "LANG=en_US.UTF-8",
        "LC_ALL=en_US.UTF-8",
        "PS1=$ ",
        "PS2=> ",
        f"HOME={os.environ['HOME']}",
        f"PATH={os.environ.get('PATH', '/usr/bin')}",
    ]
    env.extend(
        f"{name}={value}"
        for name in ("TERMINFO", "TERMINFO_DIRS")
        if (value := os.environ.get(name))
    )
    argv.extend(["--workdir", sys.argv[1], "-e", "/usr/bin/env", "-i", *env, *sys.argv[2:]])
    os.execv(binary, argv)  # noqa: S606 - replaces the owned launcher process


if __name__ == "__main__":
    main()
