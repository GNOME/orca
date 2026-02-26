# Unit tests for keybindings.py methods.
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

# pylint: disable=import-outside-toplevel
# pylint: disable=protected-access

"""Unit tests for keybindings.py methods."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext


def _setup_keybindings_dependencies(test_context: OrcaTestContext) -> None:
    """Mock only the dependencies keybindings.py needs, not keybindings itself."""

    i18n_mock = test_context.Mock()
    i18n_mock._ = lambda x: x
    i18n_mock.C_ = lambda c, x: x
    test_context.patch_module("orca.orca_i18n", i18n_mock)

    input_event_manager_mock = test_context.Mock()
    input_event_manager_mock.get_manager = test_context.Mock(
        return_value=test_context.Mock(),
    )
    test_context.patch_module("orca.input_event_manager", input_event_manager_mock)


@pytest.mark.unit
class TestAltGrModifierSupport:
    """Test AltGr (ISO_Level3_Shift) modifier support in keybindings."""

    @staticmethod
    def _create_binding(
        keysymstring: str,
        modifiers: int,
        keyval: int = 0,
        keycode: int = 0,
    ):
        """Creates a KeyBinding with pre-populated keyval/keycode to avoid Gdk.Keymap."""

        from orca.keybindings import KeyBinding

        kb = KeyBinding(keysymstring, modifiers)
        kb.keyval = keyval
        kb.keycode = keycode
        return kb

    def test_extra_altgr_prevents_match(self, test_context: OrcaTestContext) -> None:
        """Test that AltGr in event modifiers prevents matching a non-AltGr binding."""

        _setup_keybindings_dependencies(test_context)
        from orca.keybindings import ALTGR_MODIFIER_MASK, ORCA_MODIFIER_MASK

        kb = self._create_binding("z", ORCA_MODIFIER_MASK, keyval=122, keycode=52)
        assert kb.matches(122, 52, ORCA_MODIFIER_MASK | ALTGR_MODIFIER_MASK) is False

    def test_altgr_keycode_fallback(self, test_context: OrcaTestContext) -> None:
        """Test keycode fallback when AltGr changes the keyval."""

        _setup_keybindings_dependencies(test_context)
        from orca.keybindings import ALTGR_MODIFIER_MASK, ORCA_MODIFIER_MASK

        orca_altgr = ORCA_MODIFIER_MASK | ALTGR_MODIFIER_MASK
        kb = self._create_binding("period", orca_altgr, keyval=46, keycode=60)
        assert kb.matches(183, 60, orca_altgr) is True

    def test_orca_modifier_enables_keycode_fallback(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test that Orca modifier enables keycode fallback for AZERTY-like layouts."""

        _setup_keybindings_dependencies(test_context)
        from orca.keybindings import ORCA_MODIFIER_MASK

        kb = self._create_binding("9", ORCA_MODIFIER_MASK, keyval=57, keycode=18)
        assert kb.matches(231, 18, ORCA_MODIFIER_MASK) is True
