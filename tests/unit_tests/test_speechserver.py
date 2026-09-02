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

# pylint: disable=protected-access

"""Unit tests for speechserver.py methods."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext


@pytest.mark.unit
def test_build_voice_families_prepends_default_family(
    test_context: OrcaTestContext,
) -> None:
    """_build_voice_families() puts the speech server's default family first."""

    i18n = test_context.Mock()
    i18n._ = lambda value: value
    i18n.C_ = lambda _context, value: value
    i18n.ngettext = lambda singular, plural, count: singular if count == 1 else plural
    test_context.patch_module("orca.orca_i18n", i18n)

    from orca.speechserver import SpeechServer, VoiceFamily

    server = SpeechServer("test")
    server._default_voice_name = "Default Voice"
    voices = (
        ("Alice", "en-US", None),
        ("Bob", "en-GB", "variant"),
    )

    families = server._build_voice_families(voices)

    assert [family[VoiceFamily.NAME] for family in families] == [
        "Default Voice",
        "Alice",
        "Bob",
    ]
