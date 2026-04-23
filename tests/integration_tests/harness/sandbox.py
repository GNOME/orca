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

"""Shared helpers for building the isolated environment Orca-launching fixtures use."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def build_sandbox_env(sandbox: Path) -> dict[str, str]:
    """Builds an isolated environment for Orca; points Orca's XDG dirs into the sandbox."""

    env = os.environ.copy()
    # XDG_RUNTIME_DIR is owned by the wrapper (it hosts the AT-SPI sockets);
    # only the Orca-specific XDG dirs are sandboxed here.
    for subdir, key in (
        ("data", "XDG_DATA_HOME"),
        ("config", "XDG_CONFIG_HOME"),
        ("cache", "XDG_CACHE_HOME"),
        ("state", "XDG_STATE_HOME"),
    ):
        path = sandbox / subdir
        path.mkdir(exist_ok=True)
        env[key] = str(path)

    env["HOME"] = str(sandbox)
    env["GSETTINGS_BACKEND"] = "memory"
    env["LANG"] = "en_US.UTF-8"
    env["LC_ALL"] = "en_US.UTF-8"
    env["GDK_BACKEND"] = "x11"
    return env


def write_sandbox_speechd_conf(sandbox: Path) -> None:
    """Pins the sandbox speech-dispatcher to the dummy output module."""

    # The sandbox's fresh XDG_RUNTIME_DIR makes speech-dispatcher auto-spawn a
    # new instance instead of reusing the user's; without audio access its
    # default espeak-ng module crashes on some utterances, so point it at
    # sd_dummy which never touches audio.
    conf_dir = sandbox / "config" / "speech-dispatcher"
    conf_dir.mkdir(parents=True, exist_ok=True)
    (conf_dir / "speechd.conf").write_text(
        'DefaultModule dummy\nAddModule "dummy" "sd_dummy" ""\n',
        encoding="utf-8",
    )
