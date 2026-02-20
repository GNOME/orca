# Orca
#
# Copyright 2010 Consorcio Fernando de los Rios.
# Author: Javier Hernandez Antunez <jhernandez@emergya.es>
# Author: Alejandro Leiva <aleiva@emergya.es>
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

# pylint: disable=too-few-public-methods

"""Settings manager."""

from __future__ import annotations

import importlib
import importlib.util
import os
import sys
from types import ModuleType

from gi.repository import GLib

from . import debug
from . import speech_manager


DEFAULT_PROFILE: list[str] = ["Default", "default"]


# TODO - JD: Remove _DeprecatedSettingsStub in Orca v51.
class _DeprecatedSettingsStub(ModuleType):
    """Stub for the removed orca.settings module."""

    _has_warned: bool = False

    def __setattr__(self, name: str, value: object) -> None:
        if not name.startswith("_") and not _DeprecatedSettingsStub._has_warned:
            _DeprecatedSettingsStub._has_warned = True
            msg = (
                "WARNING: orca.settings has been removed. "
                "Please update your orca-customizations.py to remove references to it."
            )
            debug.print_message(debug.LEVEL_SEVERE, msg, True)
        super().__setattr__(name, value)


class SettingsManager:
    """Settings manager"""

    def __init__(self) -> None:
        debug.print_message(debug.LEVEL_INFO, "SETTINGS MANAGER: Initializing", True)

        self._prefs_dir: str = ""
        self._customized_settings: dict | None = None
        self._configuring: bool = False

        debug.print_message(debug.LEVEL_INFO, "SETTINGS MANAGER: Initialized", True)

    def activate(self) -> None:
        """Activates this manager."""

        debug.print_message(debug.LEVEL_INFO, "SETTINGS MANAGER: Activating", True)

        self._prefs_dir = os.path.join(GLib.get_user_data_dir(), "orca")  # pylint: disable=no-value-for-parameter

        self._load_customizations()

        def _create_dir(dir_name: str) -> None:
            if not os.path.isdir(dir_name):
                os.makedirs(dir_name)

        orca_dir = self._prefs_dir
        _create_dir(orca_dir)
        init_file = os.path.join(orca_dir, "__init__.py")
        if not os.path.exists(init_file):
            os.close(os.open(init_file, os.O_CREAT, 0o700))

        orca_script_dir = os.path.join(orca_dir, "orca-scripts")
        _create_dir(orca_script_dir)
        init_file = os.path.join(orca_script_dir, "__init__.py")
        if not os.path.exists(init_file):
            os.close(os.open(init_file, os.O_CREAT, 0o700))

        sounds_dir = os.path.join(orca_dir, "sounds")
        _create_dir(sounds_dir)

        customizations_file = os.path.join(orca_dir, "orca-customizations.py")
        if not os.path.exists(customizations_file):
            os.close(os.open(customizations_file, os.O_CREAT, 0o700))

        debug.print_message(debug.LEVEL_INFO, "SETTINGS MANAGER: Activated", True)

    def _load_customizations(self) -> None:
        """Load user's orca-customizations.py."""

        if self._customized_settings is not None:
            return

        self._customized_settings = {}
        module_path = os.path.join(self._prefs_dir, "orca-customizations.py")
        tokens = ["SETTINGS MANAGER: Attempt to load orca-customizations"]

        try:
            spec = importlib.util.spec_from_file_location("orca-customizations", module_path)
            if spec is not None and spec.loader is not None:
                if "orca.settings" not in sys.modules:
                    settings_stub = _DeprecatedSettingsStub("orca.settings")
                    sys.modules["orca.settings"] = settings_stub
                    sys.modules["orca"].settings = settings_stub  # type: ignore[attr-defined]
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                tokens.extend(["from", module_path, "succeeded."])
            else:
                tokens.extend(["from", module_path, "failed. Spec not found."])
        except FileNotFoundError:
            tokens.extend(["from", module_path, "failed. File not found."])
        except Exception as error:  # pylint: disable=broad-exception-caught
            tokens.extend(["failed due to:", str(error), ". Not loading customizations."])

        debug.print_tokens(debug.LEVEL_ALL, tokens, True)

    def get_prefs_dir(self) -> str:
        """Returns the preferences directory."""

        return self._prefs_dir

    def set_configuring(self, configuring: bool) -> None:
        """Set whether preferences are currently being configured."""

        self._configuring = configuring
        msg = f"SETTINGS MANAGER: Configuring mode set to {configuring}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def is_configuring(self) -> bool:
        """Return whether preferences are currently being configured."""

        return self._configuring

    def get_speech_server_factories(self) -> list[ModuleType]:
        """Imports all known SpeechServer factory modules."""

        factories: list[ModuleType] = []
        for module_name in speech_manager.SPEECH_FACTORY_MODULES:
            try:
                module = importlib.import_module(f"orca.{module_name}")
                factories.append(module)
                tokens = ["SETTINGS MANAGER: Valid speech server factory:", module_name]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            except ImportError:
                tokens = ["SETTINGS MANAGER: Invalid speech server factory:", module_name]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        return factories


_manager: SettingsManager = SettingsManager()


def get_manager() -> SettingsManager:
    """Returns the Settings Manager singleton."""

    return _manager
