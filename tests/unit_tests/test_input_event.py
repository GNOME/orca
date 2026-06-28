# Unit tests for input_event.py methods.
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

"""Unit tests for input_event.py methods."""

from __future__ import annotations

import importlib
import os
import sys
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext


@pytest.mark.unit
class TestKeyboardEvent:
    """Test KeyboardEvent methods."""

    @staticmethod
    def _setup_dependencies(test_context: OrcaTestContext) -> None:
        """Set up generated modules needed to import input_event."""

        i18n = test_context.Mock()
        i18n._ = lambda string: string
        i18n.C_ = lambda _context, string: string
        i18n.ngettext = lambda singular, plural, number: singular if number == 1 else plural

        ax_utilities = test_context.Mock()
        ax_utilities.AXUtilities = test_context.Mock()
        test_context.patch_modules(
            {
                "orca.ax_utilities": ax_utilities,
                "orca.command_manager": test_context.Mock(),
                "orca.debug": test_context.Mock(),
                "orca.focus_manager": test_context.Mock(),
                "orca.keybindings": test_context.Mock(),
                "orca.keynames": test_context.Mock(),
                "orca.messages": test_context.Mock(),
                "orca.orca_i18n": i18n,
                "orca.orca_modifier_manager": test_context.Mock(),
                "orca.presentation_manager": test_context.Mock(),
                "orca.script_manager": test_context.Mock(),
            }
        )
        sys.modules.pop("orca.input_event", None)

    @staticmethod
    def _frame(test_context: OrcaTestContext, filename: str):
        """Return a lightweight frame mock for caller checks."""

        return test_context.Mock(
            f_code=test_context.Mock(co_filename=filename),
        )

    def test_set_object_refuses_call_from_outside_input_event(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test code outside Orca cannot set raw event object."""

        self._setup_dependencies(test_context)
        input_event = importlib.import_module("orca.input_event")

        frame = self._frame(test_context, "/home/test/.local/share/orca/extensions/demo.py")
        test_context.patch_object(input_event.sys, "_getframe", return_value=frame)

        event = input_event.KeyboardEvent.__new__(input_event.KeyboardEvent)
        event._obj = None
        with pytest.raises(PermissionError):
            event.set_object(test_context.Mock())

    def test_set_object_refuses_extension_named_like_input_event(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test extension filenames cannot bypass the setter guard."""

        self._setup_dependencies(test_context)
        input_event = importlib.import_module("orca.input_event")

        frame = self._frame(
            test_context,
            "/home/test/.local/share/orca/extensions/input_event_demo.py",
        )
        test_context.patch_object(input_event.sys, "_getframe", return_value=frame)

        event = input_event.KeyboardEvent.__new__(input_event.KeyboardEvent)
        event._obj = None
        with pytest.raises(PermissionError):
            event.set_object(test_context.Mock())

    def test_set_object_refuses_non_input_event_orca_module(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test non-input-event Orca modules cannot set raw event object."""

        self._setup_dependencies(test_context)
        input_event = importlib.import_module("orca.input_event")

        assert input_event.__file__ is not None
        orca_dir = os.path.dirname(os.path.realpath(input_event.__file__))
        frame = self._frame(test_context, f"{orca_dir}/focus_manager.py")
        test_context.patch_object(input_event.sys, "_getframe", return_value=frame)

        event = input_event.KeyboardEvent.__new__(input_event.KeyboardEvent)
        event._obj = None
        with pytest.raises(PermissionError):
            event.set_object(test_context.Mock())

    def test_set_object_allows_input_event_manager_call(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test input event manager can set raw event object."""

        self._setup_dependencies(test_context)
        input_event = importlib.import_module("orca.input_event")

        assert input_event.__file__ is not None
        orca_dir = os.path.dirname(os.path.realpath(input_event.__file__))
        frame = self._frame(test_context, f"{orca_dir}/input_event_manager.py")
        test_context.patch_object(input_event.sys, "_getframe", return_value=frame)

        event = input_event.KeyboardEvent.__new__(input_event.KeyboardEvent)
        obj = test_context.Mock()
        event._obj = None
        event.set_object(obj)

        assert event.get_object() is obj
