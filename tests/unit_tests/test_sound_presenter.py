# Unit tests for sound_presenter.py methods.
#
# Copyright 2025 Igalia, S.L.
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

"""Unit tests for sound_presenter.py methods."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext
    from unittest.mock import MagicMock


@pytest.mark.unit
class TestSoundPresenter:
    """Test SoundPresenter class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Set up mocks for sound_presenter dependencies."""

        essential_modules = test_context.setup_shared_dependencies([])

        debug_mock = essential_modules["orca.debug"]
        debug_mock.print_message = test_context.Mock()
        debug_mock.LEVEL_INFO = 800

        dbus_service_mock = essential_modules["orca.dbus_service"]
        controller_mock = test_context.Mock()
        controller_mock.register_decorated_module = test_context.Mock()
        dbus_service_mock.get_remote_controller = test_context.Mock(return_value=controller_mock)
        dbus_service_mock.getter = lambda func: func
        dbus_service_mock.setter = lambda func: func

        settings_mock = essential_modules["orca.settings"]
        settings_mock.PROGRESS_BAR_ALL = 0
        settings_mock.PROGRESS_BAR_APPLICATION = 1
        settings_mock.PROGRESS_BAR_WINDOW = 2
        settings_mock.enableSound = True
        settings_mock.soundVolume = 0.5
        settings_mock.beepProgressBarUpdates = False
        settings_mock.progressBarBeepInterval = 5
        settings_mock.progressBarBeepVerbosity = 1

        essential_modules["controller"] = controller_mock

        from orca import gsettings_registry

        gsettings_registry.get_registry().set_enabled(False)

        return essential_modules

    def test_initialization_registers_dbus_module(self, test_context: OrcaTestContext) -> None:
        """Test that SoundPresenter registers itself with D-Bus on initialization."""

        mocks = self._setup_dependencies(test_context)

        from orca import sound_presenter

        presenter = sound_presenter.SoundPresenter()
        mocks["controller"].register_decorated_module.assert_called_with(
            "SoundPresenter", presenter
        )

    def test_get_sound_is_enabled_returns_setting(self, test_context: OrcaTestContext) -> None:
        """Test get_sound_is_enabled returns the enableSound setting."""

        mocks = self._setup_dependencies(test_context)
        mocks["orca.settings"].enableSound = True

        from orca.sound_presenter import SoundPresenter

        presenter = SoundPresenter()
        assert presenter.get_sound_is_enabled() is True

        mocks["orca.settings"].enableSound = False
        assert presenter.get_sound_is_enabled() is False

    def test_set_sound_is_enabled_updates_setting(self, test_context: OrcaTestContext) -> None:
        """Test set_sound_is_enabled updates the enableSound setting."""

        mocks = self._setup_dependencies(test_context)
        mocks["orca.settings"].enableSound = True

        from orca.sound_presenter import SoundPresenter

        presenter = SoundPresenter()
        result = presenter.set_sound_is_enabled(False)

        assert result is True
        assert presenter.get_sound_is_enabled() is False

    def test_get_sound_volume_returns_setting(self, test_context: OrcaTestContext) -> None:
        """Test get_sound_volume returns the soundVolume setting."""

        mocks = self._setup_dependencies(test_context)
        mocks["orca.settings"].soundVolume = 0.75

        from orca.sound_presenter import SoundPresenter

        presenter = SoundPresenter()
        assert presenter.get_sound_volume() == 0.75

    def test_set_sound_volume_updates_setting(self, test_context: OrcaTestContext) -> None:
        """Test set_sound_volume updates the soundVolume setting."""

        mocks = self._setup_dependencies(test_context)
        mocks["orca.settings"].soundVolume = 0.5

        from orca.sound_presenter import SoundPresenter

        presenter = SoundPresenter()
        result = presenter.set_sound_volume(0.8)

        assert result is True
        assert presenter.get_sound_volume() == 0.8

    def test_get_beep_progress_bar_updates_returns_setting(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test get_beep_progress_bar_updates returns the beepProgressBarUpdates setting."""

        mocks = self._setup_dependencies(test_context)
        mocks["orca.settings"].beepProgressBarUpdates = True

        from orca.sound_presenter import SoundPresenter

        presenter = SoundPresenter()
        assert presenter.get_beep_progress_bar_updates() is True

        mocks["orca.settings"].beepProgressBarUpdates = False
        assert presenter.get_beep_progress_bar_updates() is False

    def test_set_beep_progress_bar_updates_updates_setting(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test set_beep_progress_bar_updates updates the beepProgressBarUpdates setting."""

        mocks = self._setup_dependencies(test_context)
        mocks["orca.settings"].beepProgressBarUpdates = False

        from orca.sound_presenter import SoundPresenter

        presenter = SoundPresenter()
        result = presenter.set_beep_progress_bar_updates(True)

        assert result is True
        assert presenter.get_beep_progress_bar_updates() is True

    def test_get_progress_bar_beep_interval_returns_setting(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test get_progress_bar_beep_interval returns the progressBarBeepInterval setting."""

        mocks = self._setup_dependencies(test_context)
        mocks["orca.settings"].progressBarBeepInterval = 10

        from orca.sound_presenter import SoundPresenter

        presenter = SoundPresenter()
        assert presenter.get_progress_bar_beep_interval() == 10

    def test_set_progress_bar_beep_interval_updates_setting(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test set_progress_bar_beep_interval updates the progressBarBeepInterval setting."""

        mocks = self._setup_dependencies(test_context)
        mocks["orca.settings"].progressBarBeepInterval = 5

        from orca.sound_presenter import SoundPresenter

        presenter = SoundPresenter()
        result = presenter.set_progress_bar_beep_interval(15)

        assert result is True
        assert presenter.get_progress_bar_beep_interval() == 15

    def test_get_progress_bar_beep_verbosity_returns_setting(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test get_progress_bar_beep_verbosity returns the progressBarBeepVerbosity setting."""

        mocks = self._setup_dependencies(test_context)
        mocks["orca.settings"].progressBarBeepVerbosity = 2

        from orca.sound_presenter import SoundPresenter

        presenter = SoundPresenter()
        assert presenter.get_progress_bar_beep_verbosity() == 2

    def test_set_progress_bar_beep_verbosity_updates_setting(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test set_progress_bar_beep_verbosity updates the progressBarBeepVerbosity setting."""

        mocks = self._setup_dependencies(test_context)
        mocks["orca.settings"].progressBarBeepVerbosity = 1

        from orca.sound_presenter import SoundPresenter

        presenter = SoundPresenter()
        result = presenter.set_progress_bar_beep_verbosity(2)

        assert result is True
        assert presenter.get_progress_bar_beep_verbosity() == 2

    def test_get_presenter_returns_singleton(self, test_context: OrcaTestContext) -> None:
        """Test get_presenter returns the module-level presenter instance."""

        self._setup_dependencies(test_context)

        from orca import sound_presenter

        presenter1 = sound_presenter.get_presenter()
        presenter2 = sound_presenter.get_presenter()

        assert presenter1 is presenter2
        assert isinstance(presenter1, sound_presenter.SoundPresenter)
