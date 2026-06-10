# Unit tests for label_inference.py methods.
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

"""Unit tests for label_inference.py methods."""

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
class TestLabelInferenceCache:
    """Tests the manager-backed label inference cache."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Set up mocks for label inference dependencies."""

        return test_context.setup_shared_dependencies(
            [
                "orca.ax_component",
                "orca.ax_hypertext",
                "orca.ax_table",
                "orca.ax_text",
                "orca.ax_utilities",
            ]
        )

    def test_values_are_manager_backed(self, test_context: OrcaTestContext) -> None:
        """Test label-inference storage uses the manager."""

        self._setup_dependencies(test_context)
        from orca import ax_cache_manager
        from orca.label_inference import _LabelInferenceCache

        cache = _LabelInferenceCache()
        obj = test_context.Mock(spec=Atspi.Accessible)
        contents = [(obj, 0, 4, "Name")]
        extents = (0, 0, 0, 0)

        cache.set_line_contents(hash(obj), contents)
        cache.set_text_extents(obj, 0, -1, extents)
        cache.set_is_widget(obj, False)

        assert cache.get_line_contents(obj) == contents
        assert cache.get_text_extents(obj, 0, -1) == extents
        assert cache.get_is_widget(obj) is False

        ax_cache_manager.get_manager().clear_cache_now("test reason")

        assert cache.get_line_contents(obj) == contents
        assert cache.get_text_extents(obj, 0, -1) == extents
        assert cache.get_is_widget(obj) is False

        cache.clear("test reason")

        assert cache.get_line_contents(obj) is None
        assert cache.get_text_extents(obj, 0, -1) is None
        assert cache.get_is_widget(obj) is None
