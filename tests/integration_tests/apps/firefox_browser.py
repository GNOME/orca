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

"""Firefox launched in kiosk mode with a fresh integration-test profile."""

from __future__ import annotations

import json
import shutil
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

BINARY_NAMES = ("firefox",)
ENVIRONMENT = {"GNOME_ACCESSIBILITY": "1"}


def resolve_binary() -> str | None:
    """Returns the Firefox executable found on PATH."""

    return shutil.which(BINARY_NAMES[0])


def prepare_launch(profile_dir: Path, *, caret_browsing: bool = False) -> tuple[str, ...]:
    """Prepares browser-specific settings and returns additional launch flags."""

    prefs = {
        "app.update.disabledForTesting": True,
        "browser.shell.checkDefaultBrowser": False,
        "browser.startup.homepage_override.mstone": "ignore",
        "browser.aboutwelcome.enabled": False,
        "browser.preonboarding.enabled": False,
        "datareporting.policy.dataSubmissionPolicyBypassNotification": True,
        "accessibility.browsewithcaret": caret_browsing,
        "accessibility.warn_on_browsewithcaret": False,
        "layout.css.devPixelsPerPx": "1.0",
    }
    (profile_dir / "user.js").write_text(
        "".join(
            f"user_pref({json.dumps(key)}, {json.dumps(value)});\n" for key, value in prefs.items()
        ),
        encoding="utf-8",
    )
    return ()


def build_argv(
    url: str,
    profile_dir: Path,
    binary: str,
    *,
    extra_flags: tuple[str, ...] = (),
) -> list[str]:
    """Returns argv for an isolated Firefox on the wrapper's fixed-size Xvfb screen."""

    return [binary, "--no-remote", "--profile", str(profile_dir), "--kiosk", *extra_flags, url]


def is_ready_title(title: str) -> bool:
    """Accepts the page title with or without Firefox's window-branding suffix."""

    return title.rsplit(" — ", 1)[0].endswith(" ready")
