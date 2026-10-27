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

"""Version discovery and requirements for integration-test applications and libraries."""

from __future__ import annotations

import configparser
import functools
import re
import shutil
import subprocess
import sys
from pathlib import Path

import gi
import pytest

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from .apps import browser

Version = tuple[int, ...]


@functools.cache
def command_version(command: tuple[str, ...]) -> Version | None:
    """Returns the dotted version printed by command, or None if it cannot be read."""

    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=30, check=True)
    except (OSError, subprocess.SubprocessError):
        return None
    match = re.search(r"\d+(?:\.\d+)+", result.stdout)
    return tuple(int(part) for part in match[0].split(".")) if match else None


def requires_browser_version(name: str, *minimum: int, when: bool = True) -> pytest.MarkDecorator:
    """Applies a version requirement only to the named browser, when selected."""

    if name not in browser.BROWSERS:
        raise ValueError(f"Unknown browser version requirement: {name!r}")
    applies = when and browser.selected_browser() == name
    binary = browser.resolve_binary(name) if applies else None
    actual = command_version((binary, "--version")) if binary is not None else None
    return requires_version(name, actual, *minimum, when=applies)


def requires_atril_version(*minimum: int) -> pytest.MarkDecorator:
    """Skips tests which require fixes in a newer Atril release."""

    return requires_version("Atril", command_version(("atril", "--version")), *minimum)


def gtk_version(api_version: str) -> Version | None:
    """Returns the GTK version, querying separately from the GTK3 driver."""

    command = (
        sys.executable,
        "-c",
        (
            f"import gi; gi.require_version('Gtk', {api_version!r}); "
            "from gi.repository import Gtk; "
            "print(f'{Gtk.get_major_version()}.{Gtk.get_minor_version()}.{Gtk.get_micro_version()}')"
        ),
    )
    return command_version(command)


def requires_gtk_version(
    api_version: str, *minimum: int, when: bool = True
) -> pytest.MarkDecorator:
    """Skips tests requiring newer GTK; query separately from the GTK3 driver."""

    actual = gtk_version(api_version) if when else None
    return requires_version("GTK", actual, *minimum, when=when)


def requires_vte_version(
    api_version: str, *minimum: int, when: bool = True
) -> pytest.MarkDecorator:
    """Skips tests requiring a newer VTE; query GTK4 separately from the GTK3 driver."""

    command = (
        sys.executable,
        "-c",
        (
            f"import gi; gi.require_version('Vte', {api_version!r}); "
            "from gi.repository import Vte; "
            "print(f'{Vte.get_major_version()}.{Vte.get_minor_version()}.{Vte.get_micro_version()}')"
        ),
    )
    actual = command_version(command) if when else None
    return requires_version(f"VTE {api_version}", actual, *minimum, when=when)


@functools.cache
def _firefox_build_info() -> tuple[int, int, bool] | None:
    """Returns Firefox's major version, build ID, and whether it is a Nightly build."""

    if browser.selected_browser() != "firefox":
        return None
    binary = browser.resolve_binary("firefox")
    if binary is None:
        return None
    pattern = r"(\d+)(?:\.\d+)+([ab]\d+|esr)?\s+(\d{14})(?:\s|$)"
    config = configparser.ConfigParser(interpolation=None)
    try:
        executable = Path(shutil.which(binary) or binary).resolve()
        config.read(executable.with_name("application.ini"), encoding="utf-8")
        match = re.fullmatch(
            pattern,
            f"{config.get('App', 'Version', fallback='')} "
            f"{config.get('App', 'BuildID', fallback='')}",
        )
    except (OSError, configparser.Error, UnicodeError):
        match = None
    if match is None:
        try:
            result = subprocess.run(
                [binary, "--full-version"], capture_output=True, text=True, timeout=30, check=True
            )
        except (OSError, subprocess.SubprocessError):
            return None
        match = re.search(pattern, result.stdout)
    if match is None:
        return None
    return int(match[1]), int(match[3]), (match[2] or "").startswith("a")


def firefox_is_older_than_build(major: int, build_id: int) -> bool:
    """Returns whether Firefox is selected and predates the build, or cannot be identified."""

    if browser.selected_browser() != "firefox":
        return False
    info = _firefox_build_info()
    return info is None or info[:2] < (major, build_id)


def firefox_is_nightly() -> bool:
    """Returns whether the selected Firefox executable reports a Nightly version."""

    info = _firefox_build_info()
    return info is not None and info[2]


def atspi_version() -> Version:
    """Returns the version of the AT-SPI library used by the tests."""

    return tuple(Atspi.get_version())  # pylint: disable=no-value-for-parameter


def has_typelib(namespace: str, version: str) -> bool:
    """Returns whether a GI namespace's API version is installed, without loading it."""

    return version in gi.Repository.get_default().enumerate_versions(namespace)


def version_at_least(actual: Version | None, *minimum: int) -> bool:
    """Compares versions, treating an unknown version as insufficient and missing parts as zero."""

    if actual is None:
        return False
    length = max(len(actual), len(minimum))
    return actual + (0,) * (length - len(actual)) >= minimum + (0,) * (length - len(minimum))


def requires_version(
    name: str, actual: Version | None, *minimum: int, when: bool = True
) -> pytest.MarkDecorator:
    """Skips a test if an applicable application or library version requirement is unmet."""

    needed = ".".join(map(str, minimum))
    detected = ".".join(map(str, actual)) if actual is not None else "unknown"
    return pytest.mark.skipif(
        when and not version_at_least(actual, *minimum),
        reason=f"needs {name} {needed} or later; this is {detected}",
    )
