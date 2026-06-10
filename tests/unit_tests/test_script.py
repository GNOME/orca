# Unit tests for script.py methods.
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

# pylint: disable=wrong-import-position
# pylint: disable=import-outside-toplevel
# pylint: disable=protected-access

"""Unit tests for script.py methods."""

from __future__ import annotations

from typing import TYPE_CHECKING

import gi
import pytest

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from .orca_test_context import OrcaTestContext


@pytest.mark.unit
class TestScriptCache:
    """Tests the manager-backed base script cache."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Set up mocks for script module dependencies."""

        return test_context.setup_shared_dependencies(
            [
                "orca.braille_generator",
                "orca.chat_presenter",
                "orca.script_utilities",
                "orca.sound_generator",
                "orca.speech_generator",
                "orca.structural_navigator",
            ]
        )

    def test_queued_events_survive_on_demand_clear(self, test_context: OrcaTestContext) -> None:
        """Test queued events are stored and survive an on-demand cache clear."""

        self._setup_dependencies(test_context)
        from orca import ax_cache_manager
        from orca.script import _ScriptCache

        cache = _ScriptCache()
        event = test_context.Mock(spec=Atspi.Event)
        event.type = "object:state-changed:focused"

        assert cache.get_queued_event(event.type) is None

        cache.record_queued_event(event)

        assert cache.get_queued_event(event.type) is event

        # Queued events use a PRESERVE policy, so the on-demand clear must not evict them.
        ax_cache_manager.get_manager().clear_cache_now("test reason")

        assert cache.get_queued_event(event.type) is event
