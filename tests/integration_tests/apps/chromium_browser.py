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

import shutil
import sys
import warnings
from pathlib import Path

BINARY_NAMES = ("chromium", "chromium-browser")
ENVIRONMENT = {"ACCESSIBILITY_ENABLED": "1"}
READY_SUFFIX = " ready"
_BETA_PATH = "/opt/google/chrome-beta/chrome"


def resolve_binary() -> str | None:
    """Returns the selected Chromium executable, preferring the beta used for expectations."""

    if Path(_BETA_PATH).is_file():
        return _BETA_PATH
    binary = next((p for p in (shutil.which(name) for name in BINARY_NAMES) if p), None)
    if binary is not None:
        warnings.warn(
            f"Web test expectations were captured against {_BETA_PATH}; using {binary}. "
            "Set ORCA_TEST_BROWSER_BINARY to choose a different build.",
            stacklevel=2,
        )
    return binary


def build_argv(
    url: str,
    profile_dir: Path,
    binary: str,
    *,
    window_size: tuple[int, int] = (1024, 768),
    extra_flags: tuple[str, ...] = (),
    force_accessibility: bool = True,
) -> list[str]:
    """Returns argv for launching Chromium deterministically against url."""

    return [
        binary,
        f"--app={url}",
        f"--user-data-dir={profile_dir}",
        f"--window-size={window_size[0]},{window_size[1]}",
        "--window-position=0,0",
        "--force-device-scale-factor=1",
        # Fedora's chromium defaults to Wayland; the wrapper unsets WAYLAND_DISPLAY.
        "--ozone-platform=x11",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-extensions",
        *(["--force-renderer-accessibility"] if force_accessibility else []),
        "--disable-background-timer-throttling",
        "--disable-renderer-backgrounding",
        "--disable-backgrounding-occluded-windows",
        "--no-sandbox",  # already inside the Xvfb + private-a11y wrapper sandbox
        "--test-type",  # suppress the "unsupported command-line flag" infobar
        "--password-store=basic",
        "--disable-gpu",  # Xvfb has no GPU; skip the failed init dance
        *extra_flags,
    ]


def prepare_launch(profile_dir: Path, *, caret_browsing: bool = False) -> tuple[str, ...]:
    """Prepares browser-specific settings and returns additional launch flags."""

    return ("--enable-caret-browsing",) if caret_browsing else ()


def is_ready_title(title: str) -> bool:
    """Returns whether a top-level accessible has the test page's ready title."""

    return title.endswith(READY_SUFFIX)


if __name__ == "__main__":
    from .browser import main

    sys.exit(main(browser_name="chromium"))
