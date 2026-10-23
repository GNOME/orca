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

"""Terminal toolkit selection shared by the integration-test fixtures."""

TOOLKITS = {"gtk3": "2.91", "gtk4": "3.91"}
_SELECTED_TOOLKIT: str | None = None


def configure(toolkit: str | None) -> None:
    """Sets the toolkit selected by the Meson suite."""

    global _SELECTED_TOOLKIT  # noqa: PLW0603
    _SELECTED_TOOLKIT = toolkit


def selected_toolkit() -> str:
    """Returns the toolkit selected by the Meson suite."""

    if _SELECTED_TOOLKIT is None:
        raise RuntimeError("Terminal tests require the gtk3-terminal or gtk4-terminal Meson suite")
    return _SELECTED_TOOLKIT


def app_module(suffix: str = "") -> str:
    """Returns an application module name without importing its toolkit."""

    return f"{__package__}.{selected_toolkit()}_terminal{suffix}"
