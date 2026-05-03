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

"""Chromium launched in --app mode for integration tests."""

import os
import shutil
import sys
import tempfile
from pathlib import Path

BINARY_NAMES = ("chromium", "chromium-browser")
READY_SUFFIX = " ready"


def build_argv(
    url: str,
    profile_dir: Path,
    binary: str,
    *,
    window_size: tuple[int, int] = (1024, 768),
) -> list[str]:
    """Returns argv for launching Chromium deterministically against url."""

    return [
        binary,
        f"--app={url}",
        f"--user-data-dir={profile_dir}",
        f"--window-size={window_size[0]},{window_size[1]}",
        "--window-position=0,0",
        # Fedora's chromium defaults to Wayland; the wrapper unsets WAYLAND_DISPLAY.
        "--ozone-platform=x11",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-extensions",
        "--force-renderer-accessibility",
        "--disable-background-timer-throttling",
        "--disable-renderer-backgrounding",
        "--disable-backgrounding-occluded-windows",
        "--no-sandbox",  # already inside the Xvfb + private-a11y wrapper sandbox
        "--test-type",  # suppress the "unsupported command-line flag" infobar
        "--password-store=basic",
        "--disable-gpu",  # Xvfb has no GPU; skip the failed init dance
    ]


def main() -> int:
    """Standalone entry: takes URL [profile_dir] [binary] and execs chromium."""

    if len(sys.argv) < 2:
        print(
            "Usage: python -m tests.integration_tests.apps.chromium_browser "
            "<url> [profile_dir] [binary]",
            file=sys.stderr,
        )
        return 2
    url = sys.argv[1]
    if len(sys.argv) > 2:
        profile_dir = Path(sys.argv[2])
    else:
        profile_dir = Path(tempfile.mkdtemp(prefix="orca-chromium-debug-"))
    profile_dir.mkdir(parents=True, exist_ok=True)
    if len(sys.argv) > 3:
        binary: str | None = sys.argv[3]
    else:
        binary = next((p for p in (shutil.which(name) for name in BINARY_NAMES) if p), None)
    if binary is None:
        print(f"No chromium binary found; tried {BINARY_NAMES!r}.", file=sys.stderr)
        return 2
    argv = build_argv(url, profile_dir, binary)
    os.execvp(argv[0], argv)  # noqa: S606
    return 0  # unreachable: execvp replaces the process


if __name__ == "__main__":
    sys.exit(main())
