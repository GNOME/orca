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

"""Discovers, validates, and loads built-in and user extensions."""

from __future__ import annotations

import hashlib
import importlib.util
import os
from typing import TYPE_CHECKING

from . import debug, gsettings_registry
from .extension import Extension

if TYPE_CHECKING:
    from collections.abc import Callable

_SCHEMA = "extensions"
_KEY_DISABLED = "disabled-extensions"
_KEY_APPROVED = "approved-user-extensions"


@gsettings_registry.get_registry().gsettings_schema("org.gnome.Orca.Extensions", name="extensions")
class ExtensionLoader:
    """Discovers, validates, and loads built-in and user extensions."""

    def __init__(self) -> None:
        self._builtins: list[tuple[Callable[[], Extension], str]] = []
        self._user_extensions: list[Extension] = []

    @gsettings_registry.get_registry().gsetting(
        key="disabled-extensions",
        schema="extensions",
        gtype="as",
        default=[],
        summary="Extensions disabled by the user (by MODULE_NAME)",
    )
    def get_disabled_extensions(self) -> list[str]:
        """Returns the list of disabled extension MODULE_NAMEs."""

        return gsettings_registry.get_registry().layered_lookup(
            _SCHEMA,
            _KEY_DISABLED,
            "as",
            default=[],
        )

    def set_disabled_extensions(self, value: list[str]) -> bool:
        """Sets the list of disabled extension MODULE_NAMEs."""

        gsettings_registry.get_registry().set_runtime_value(_SCHEMA, _KEY_DISABLED, value)
        return True

    @gsettings_registry.get_registry().gsetting(
        key="approved-user-extensions",
        schema="extensions",
        gtype="a{ss}",
        default={},
        summary="Approved user extensions (filename to SHA256 hash)",
    )
    def get_approved_extensions(self) -> dict[str, str]:
        """Returns the dict of approved extensions (filename -> sha256)."""

        return gsettings_registry.get_registry().layered_lookup(
            _SCHEMA,
            _KEY_APPROVED,
            "a{ss}",
            default={},
        )

    def set_approved_extensions(self, value: dict[str, str]) -> bool:
        """Sets the dict of approved extensions."""

        gsettings_registry.get_registry().set_runtime_value(_SCHEMA, _KEY_APPROVED, value)
        return True

    def approve_extension(self, filename: str, sha256_hash: str) -> None:
        """Approves an extension by recording its filename and hash."""

        approved = dict(self.get_approved_extensions())
        approved[filename] = sha256_hash
        self.set_approved_extensions(approved)

    def revoke_extension(self, filename: str) -> None:
        """Revokes approval for an extension."""

        approved = dict(self.get_approved_extensions())
        approved.pop(filename, None)
        self.set_approved_extensions(approved)

    def register_builtin(self, getter: Callable[[], Extension], group_label: str) -> None:
        """Registers a built-in extension with the loader."""

        self._builtins.append((getter, group_label))

    def discover_and_load(self, extensions_dir: str) -> None:
        """Scans the extensions directory and loads approved user extensions."""

        if not os.path.isdir(extensions_dir):
            msg = f"EXTENSION LOADER: Extensions directory not found: {extensions_dir}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        approved = self.get_approved_extensions()
        disabled = self.get_disabled_extensions()

        for filename in sorted(os.listdir(extensions_dir)):
            if not filename.endswith(".py") or filename.startswith("_"):
                continue

            filepath = os.path.join(extensions_dir, filename)
            if not os.path.isfile(filepath):
                continue

            file_hash = self._compute_hash(filepath)
            approved_hash = approved.get(filename)

            if approved_hash is None:
                msg = (
                    f"EXTENSION LOADER: New extension found: {filename}. "
                    f"Not approved. Hash: {file_hash}"
                )
                debug.print_message(debug.LEVEL_INFO, msg, True)
                profile = gsettings_registry.get_registry().get_active_profile()
                msg = (
                    f"EXTENSION LOADER: To approve, run: dconf write "
                    f"/org/gnome/orca/{profile}/extensions/"
                    f"approved-user-extensions "
                    f"\"{{'{filename}': '{file_hash}'}}\""
                )
                debug.print_message(debug.LEVEL_INFO, msg, True)
                continue

            if approved_hash != file_hash:
                msg = (
                    f"EXTENSION LOADER: Extension modified: {filename}. "
                    f"Approved hash: {approved_hash} "
                    f"Current hash: {file_hash}. "
                    "Not loading until re-approved."
                )
                debug.print_message(debug.LEVEL_WARNING, msg, True)
                profile = gsettings_registry.get_registry().get_active_profile()
                msg = (
                    f"EXTENSION LOADER: To re-approve, run: dconf write "
                    f"/org/gnome/orca/{profile}/extensions/"
                    f"approved-user-extensions "
                    f"\"{{'{filename}': '{file_hash}'}}\""
                )
                debug.print_message(debug.LEVEL_INFO, msg, True)
                continue

            extension = self._load_from_file(filepath, filename)
            if extension is None:
                continue

            if extension.module_name in disabled:
                msg = f"EXTENSION LOADER: Extension {extension.module_name} is disabled. Skipping."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                continue

            self._user_extensions.append(extension)
            msg = f"EXTENSION LOADER: Loaded extension {extension.module_name} from {filename}"
            debug.print_message(debug.LEVEL_INFO, msg, True)

    def set_up_all_commands(self) -> None:
        """Calls set_up_commands on all enabled extensions (built-in and user)."""

        disabled = self.get_disabled_extensions()

        for getter, _group_label in self._builtins:
            ext = getter()
            if ext.module_name in disabled:
                msg = f"EXTENSION LOADER: {ext.module_name} is disabled. Skipping."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                continue
            msg = f"EXTENSION LOADER: Loading built-in extension {ext.module_name}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            ext.set_up_commands()

        for ext in self._user_extensions:
            if ext.module_name in disabled:
                msg = f"EXTENSION LOADER: {ext.module_name} is disabled. Skipping."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                continue
            msg = f"EXTENSION LOADER: Loading user extension {ext.module_name}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            ext.set_up_commands()

    @staticmethod
    def _compute_hash(filepath: str) -> str:
        """Returns the SHA256 hex digest of the file at filepath."""

        sha256 = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    @staticmethod
    def _load_from_file(filepath: str, filename: str) -> Extension | None:
        """Loads an Extension subclass from a Python file."""

        module_name = f"orca_user_extension.{filename[:-3]}"
        try:
            spec = importlib.util.spec_from_file_location(module_name, filepath)
            if spec is None or spec.loader is None:
                msg = f"EXTENSION LOADER: Could not create spec for {filepath}"
                debug.print_message(debug.LEVEL_WARNING, msg, True)
                return None

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except Exception as error:  # pylint: disable=broad-exception-caught
            msg = f"EXTENSION LOADER: Failed to load {filepath}: {error}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return None

        for attr_name in dir(module):
            obj = module.__dict__.get(attr_name)
            if isinstance(obj, type) and issubclass(obj, Extension) and obj is not Extension:
                try:
                    instance = obj()
                    instance.mark_as_user_extension()
                    return instance
                except Exception as error:  # pylint: disable=broad-exception-caught
                    msg = (
                        f"EXTENSION LOADER: Failed to instantiate "
                        f"{attr_name} from {filepath}: {error}"
                    )
                    debug.print_message(debug.LEVEL_WARNING, msg, True)
                    return None

        msg = f"EXTENSION LOADER: No Extension subclass found in {filepath}"
        debug.print_message(debug.LEVEL_WARNING, msg, True)
        return None


_loader: ExtensionLoader = ExtensionLoader()


def get_loader() -> ExtensionLoader:
    """Returns the ExtensionLoader singleton."""

    return _loader
