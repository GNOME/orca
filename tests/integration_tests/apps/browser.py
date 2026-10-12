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

"""Browser selection and the shared integration-test browser entry point."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from . import chromium_browser, firefox_browser

BROWSERS = {"chromium": chromium_browser, "firefox": firefox_browser}
USER_AGENTS = {"chromium": "chromium", "gecko": "firefox"}
_SELECTED_BROWSER: str | None = None


def configure(user_agent: str | None) -> None:
    """Sets the browser selected by the Meson suite, if any."""

    global _SELECTED_BROWSER  # noqa: PLW0603
    _SELECTED_BROWSER = USER_AGENTS[user_agent] if user_agent is not None else None


def selected_browser() -> str:
    """Returns the browser selected by the Meson suite."""

    if _SELECTED_BROWSER is None:
        raise RuntimeError("Browser tests require the chromium or gecko Meson suite")
    return _SELECTED_BROWSER


def resolve_binary(name: str) -> str | None:
    """Resolves the override or the selected browser's default executable."""

    if override := os.environ.get("ORCA_TEST_USER_AGENT_PATH"):
        return override
    return BROWSERS[name].resolve_binary()


def main(*, browser_name: str | None = None) -> int:
    """Launches the requested browser with its profile and flags."""

    args = sys.argv[1:]
    name = browser_name or (args.pop(0) if args else None)
    if name not in BROWSERS or not args:
        print(
            "Usage: python -m tests.integration_tests.apps.browser "
            "<browser> <url> [profile_dir] [binary] [--caret-browsing] [extra browser flags...]",
            file=sys.stderr,
        )
        return 2
    app = BROWSERS[name]
    os.environ.update(app.ENVIRONMENT)
    url = args[0]
    profile_dir = (
        Path(args[1]) if len(args) > 1 else Path(tempfile.mkdtemp(prefix=f"orca-{name}-debug-"))
    )
    profile_dir.mkdir(parents=True, exist_ok=True)
    binary = args[2] if len(args) > 2 else resolve_binary(name)
    if binary is None:
        print(f"No {name} binary found; tried {app.BINARY_NAMES!r}.", file=sys.stderr)
        return 2
    flags = args[3:]
    caret_browsing = "--caret-browsing" in flags
    if caret_browsing:
        flags.remove("--caret-browsing")
    launch_flags = app.prepare_launch(profile_dir, caret_browsing=caret_browsing)
    argv = app.build_argv(url, profile_dir, binary, extra_flags=(*launch_flags, *flags))
    if os.environ.get("ORCA_TEST_DEBUG_DIR"):
        print(f"[diagnostics] {name} argv: {argv!r}", file=sys.stderr)
        subprocess.run([binary, "--version"], check=False, timeout=30)
        if shutil.which("fc-match"):
            for family in ("serif", "sans-serif", "monospace"):
                print(f"[diagnostics] Font match for {family}:", flush=True)
                subprocess.run(["fc-match", family], check=False)
    os.execvp(argv[0], argv)  # noqa: S606
    return 0  # unreachable: execvp replaces the process


if __name__ == "__main__":
    sys.exit(main())
