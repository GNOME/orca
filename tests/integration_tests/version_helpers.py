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

import functools
import re
import subprocess

import gi
import pytest

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from .apps import chromium_browser

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


def chromium_version() -> Version | None:
    """Returns the version of the Chromium executable selected for the tests."""

    binary = chromium_browser.resolve_binary()
    return command_version((binary, "--version")) if binary is not None else None


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
