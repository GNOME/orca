# Unit tests for ax_device_manager.py methods.
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

"""Unit tests for ax_device_manager.py methods."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from .orca_test_context import OrcaTestContext


@pytest.mark.unit
class TestAXDeviceManager:
    """Test AXDeviceManager class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Returns dependencies for ax_device_manager module testing."""

        essential_modules = test_context.setup_shared_dependencies(["gi.repository"])

        debug_mock = essential_modules["orca.debug"]
        debug_mock.LEVEL_INFO = 800
        debug_mock.LEVEL_WARNING = 2
        debug_mock.print_message = test_context.Mock()

        return essential_modules

    def test_grab_keyboard_refuses_call_from_outside_orca(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test code outside Orca cannot grab the whole keyboard."""

        self._setup_dependencies(test_context)
        from orca import ax_device_manager
        from orca.ax_device_manager import AXDeviceManager

        frame = test_context.Mock()
        frame.filename = "/home/test/.local/share/orca/extensions/demo.py"
        test_context.patch_object(
            ax_device_manager.inspect,
            "stack",
            return_value=[frame, frame, frame],
        )

        manager = AXDeviceManager()
        manager._device = test_context.Mock()
        manager.grab_keyboard("Test grab")

        manager._device.grab_keyboard.assert_not_called()

    def test_grab_keyboard_allows_orca_call(self, test_context: OrcaTestContext) -> None:
        """Test Orca code can grab the whole keyboard."""

        self._setup_dependencies(test_context)
        from orca import ax_device_manager
        from orca.ax_device_manager import AXDeviceManager

        frame = test_context.Mock()
        orca_dir = ax_device_manager.os.path.dirname(
            ax_device_manager.os.path.realpath(ax_device_manager.__file__)
        )
        frame.filename = f"{orca_dir}/learn_mode_presenter.py"
        test_context.patch_object(
            ax_device_manager.inspect,
            "stack",
            return_value=[frame, frame, frame],
        )

        manager = AXDeviceManager()
        manager._device = test_context.Mock()
        manager.grab_keyboard("Test grab")

        manager._device.grab_keyboard.assert_called_once_with()

    def test_add_key_grab_refuses_call_from_outside_orca(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test code outside Orca cannot add raw key grabs."""

        self._setup_dependencies(test_context)
        from orca import ax_device_manager
        from orca.ax_device_manager import AXDeviceManager

        frame = test_context.Mock()
        frame.filename = "/home/test/.local/share/orca/extensions/demo.py"
        test_context.patch_object(
            ax_device_manager.inspect,
            "stack",
            return_value=[frame, frame, frame],
        )

        manager = AXDeviceManager()
        manager._device = test_context.Mock()

        assert manager.add_key_grab(test_context.Mock()) == 0
        manager._device.add_key_grab.assert_not_called()
