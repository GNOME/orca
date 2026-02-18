# Unit tests for spellcheck_presenter.py methods.
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
# pylint: disable=no-member

"""Unit tests for spellcheck_presenter.py methods."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext
    from unittest.mock import MagicMock


@pytest.mark.unit
class TestSpellCheckPresenter:
    """Test SpellCheckPresenter class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Returns dependencies for spellcheck_presenter module testing."""

        additional_modules: list[str] = [
            "orca.ax_utilities",
            "orca.ax_text",
            "orca.ax_object",
            "orca.braille",
            "orca.focus_manager",
            "orca.input_event_manager",
            "orca.messages",
            "orca.object_properties",
            "orca.preferences_grid_base",
            "orca.presentation_manager",
            "orca.speech_presenter",
        ]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        debug_mock = essential_modules["orca.debug"]
        debug_mock.print_message = test_context.Mock()
        debug_mock.LEVEL_INFO = 800

        from orca import gsettings_registry

        gsettings_registry.get_registry().set_enabled(False)
        gsettings_registry.get_registry().clear_runtime_values()

        return essential_modules

    def test_get_presenter(self, test_context: OrcaTestContext) -> None:
        """Test get_presenter returns a SpellCheckPresenter instance."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.spellcheck_presenter import get_presenter, SpellCheckPresenter

        presenter = get_presenter()
        assert presenter is not None
        assert isinstance(presenter, SpellCheckPresenter)

        dbus_service_mock = essential_modules["orca.dbus_service"]
        controller = dbus_service_mock.get_remote_controller.return_value
        controller.register_decorated_module.assert_called_with("SpellCheckPresenter", presenter)

    def test_get_spell_error_true(self, test_context: OrcaTestContext) -> None:
        """Test get_spell_error returns True when setting is True."""

        self._setup_dependencies(test_context)
        from orca.spellcheck_presenter import SpellCheckPresenter

        presenter = SpellCheckPresenter()
        result = presenter.get_spell_error()
        assert result is True

    def test_get_spell_error_false(self, test_context: OrcaTestContext) -> None:
        """Test get_spell_error returns False when setting is False."""

        self._setup_dependencies(test_context)

        from orca import gsettings_registry
        from orca.spellcheck_presenter import SpellCheckPresenter

        presenter = SpellCheckPresenter()
        gsettings_registry.get_registry().set_runtime_value("spellcheck", "spell-error", False)
        result = presenter.get_spell_error()
        assert result is False

    def test_set_spell_error(self, test_context: OrcaTestContext) -> None:
        """Test set_spell_error updates settings."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.spellcheck_presenter import SpellCheckPresenter

        presenter = SpellCheckPresenter()
        result = presenter.set_spell_error(False)

        assert result is True
        assert presenter.get_spell_error() is False
        essential_modules["orca.debug"].print_message.assert_called()

    def test_set_spell_error_same_value(self, test_context: OrcaTestContext) -> None:
        """Test set_spell_error returns early when value unchanged."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.spellcheck_presenter import SpellCheckPresenter

        presenter = SpellCheckPresenter()
        essential_modules["orca.debug"].print_message.reset_mock()

        result = presenter.set_spell_error(True)
        assert result is True
        # Debug message for setting change should NOT be called
        calls = essential_modules["orca.debug"].print_message.call_args_list
        setting_calls = [c for c in calls if "Setting spell error" in str(c)]
        assert len(setting_calls) == 0

    def test_get_spell_suggestion_true(self, test_context: OrcaTestContext) -> None:
        """Test get_spell_suggestion returns True when setting is True."""

        self._setup_dependencies(test_context)
        from orca.spellcheck_presenter import SpellCheckPresenter

        presenter = SpellCheckPresenter()
        result = presenter.get_spell_suggestion()
        assert result is True

    def test_get_spell_suggestion_false(self, test_context: OrcaTestContext) -> None:
        """Test get_spell_suggestion returns False when setting is False."""

        self._setup_dependencies(test_context)

        from orca import gsettings_registry
        from orca.spellcheck_presenter import SpellCheckPresenter

        presenter = SpellCheckPresenter()
        gsettings_registry.get_registry().set_runtime_value("spellcheck", "spell-suggestion", False)
        result = presenter.get_spell_suggestion()
        assert result is False

    def test_set_spell_suggestion(self, test_context: OrcaTestContext) -> None:
        """Test set_spell_suggestion updates settings."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.spellcheck_presenter import SpellCheckPresenter

        presenter = SpellCheckPresenter()
        result = presenter.set_spell_suggestion(False)

        assert result is True
        assert presenter.get_spell_suggestion() is False
        essential_modules["orca.debug"].print_message.assert_called()

    def test_set_spell_suggestion_same_value(self, test_context: OrcaTestContext) -> None:
        """Test set_spell_suggestion returns early when value unchanged."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.spellcheck_presenter import SpellCheckPresenter

        presenter = SpellCheckPresenter()
        essential_modules["orca.debug"].print_message.reset_mock()

        result = presenter.set_spell_suggestion(True)
        assert result is True
        # Debug message for setting change should NOT be called
        calls = essential_modules["orca.debug"].print_message.call_args_list
        setting_calls = [c for c in calls if "Setting spell suggestion" in str(c)]
        assert len(setting_calls) == 0

    def test_get_present_context_true(self, test_context: OrcaTestContext) -> None:
        """Test get_present_context returns True when setting is True."""

        self._setup_dependencies(test_context)
        from orca.spellcheck_presenter import SpellCheckPresenter

        presenter = SpellCheckPresenter()
        result = presenter.get_present_context()
        assert result is True

    def test_get_present_context_false(self, test_context: OrcaTestContext) -> None:
        """Test get_present_context returns False when setting is False."""

        self._setup_dependencies(test_context)

        from orca import gsettings_registry
        from orca.spellcheck_presenter import SpellCheckPresenter

        presenter = SpellCheckPresenter()
        gsettings_registry.get_registry().set_runtime_value("spellcheck", "present-context", False)
        result = presenter.get_present_context()
        assert result is False

    def test_set_present_context(self, test_context: OrcaTestContext) -> None:
        """Test set_present_context updates settings."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.spellcheck_presenter import SpellCheckPresenter

        presenter = SpellCheckPresenter()
        result = presenter.set_present_context(False)

        assert result is True
        assert presenter.get_present_context() is False
        essential_modules["orca.debug"].print_message.assert_called()

    def test_set_present_context_same_value(self, test_context: OrcaTestContext) -> None:
        """Test set_present_context returns early when value unchanged."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.spellcheck_presenter import SpellCheckPresenter

        presenter = SpellCheckPresenter()
        essential_modules["orca.debug"].print_message.reset_mock()

        result = presenter.set_present_context(True)
        assert result is True
        # Debug message for setting change should NOT be called
        calls = essential_modules["orca.debug"].print_message.call_args_list
        setting_calls = [c for c in calls if "Setting present context" in str(c)]
        assert len(setting_calls) == 0
