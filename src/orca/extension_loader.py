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

import ast
import hashlib
import importlib.util
import os
import sys
import threading
import time
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

from . import command_manager, debug, gsettings_registry
from .extension import Extension

if TYPE_CHECKING:
    from collections.abc import Callable

_SCHEMA = "extensions"
_KEY_DISABLED = "disabled-extensions"
_KEY_APPROVED = "approved-user-extensions"
_KEY_SETTINGS = "settings"


class UserExtensionStatus(Enum):
    """Status of a discovered user extension file."""

    INVALID = "invalid"
    UNAPPROVED = "unapproved"
    APPROVED = "approved"
    MODIFIED = "modified"
    DISABLED = "disabled"


@dataclass(frozen=True)
class UserExtensionMetadata:
    """Metadata parsed from a user extension without executing it."""

    class_name: str | None = None
    group_label: str | None = None
    description: str = ""
    version: str = ""
    author: str = ""
    organization: str = ""
    copyright: str = ""
    website: str = ""


@dataclass(frozen=True)
class UserExtensionInfo:
    """Non-executing metadata for a user extension file."""

    filename: str
    filepath: str
    is_package: bool
    class_name: str | None
    group_label: str | None
    description: str
    version: str
    author: str
    organization: str
    copyright: str
    website: str
    file_hash: str
    approved_hash: str | None
    status: UserExtensionStatus

    @property
    def is_approved(self) -> bool:
        """Returns True if the current file hash is approved."""

        return self.approved_hash == self.file_hash


@gsettings_registry.get_registry().gsettings_schema("org.gnome.Orca.Extensions", name="extensions")
class ExtensionLoader:
    """Discovers, validates, and loads built-in and user extensions."""

    _SHUTDOWN_HOOK_TOTAL_TIMEOUT_SECONDS = 0.5

    def __init__(self) -> None:
        self._builtins: list[tuple[Callable[[], Extension], str]] = []
        self._user_extensions: list[Extension] = []
        self._speech_output_handlers: list[Extension] = []
        self._braille_output_handlers: list[Extension] = []

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
        """Sets the list of disabled extension class names."""

        return gsettings_registry.get_registry().set_strv(
            _SCHEMA,
            _KEY_DISABLED,
            value,
        )

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

        return gsettings_registry.get_registry().set_dict(
            _SCHEMA,
            _KEY_APPROVED,
            "a{ss}",
            value,
        )

    @gsettings_registry.get_registry().gsetting(
        key="settings",
        schema="extensions",
        gtype="a{sv}",
        default={},
        summary="Settings for a user extension",
    )
    def get_user_extension_settings(self) -> dict:
        """Returns settings for the extensions root path."""

        return gsettings_registry.get_registry().layered_lookup(
            _SCHEMA,
            _KEY_SETTINGS,
            "a{sv}",
            default={},
        )

    def approve_extension(self, filename: str, sha256_hash: str) -> None:
        """Approves an extension by recording its filename and hash."""

        approved = dict(self.get_approved_extensions())
        approved[filename] = sha256_hash
        self.set_approved_extensions(approved)

    def approve_extension_file(self, filepath: str) -> str:
        """Computes the hash and approves the extension. Returns the hash."""

        filename = self._get_source_id(filepath)
        file_hash = self._compute_hash(filepath)
        self.approve_extension(filename, file_hash)
        return file_hash

    def revoke_extension(self, filename: str) -> None:
        """Revokes approval for an extension."""

        approved = dict(self.get_approved_extensions())
        approved.pop(filename, None)
        self.set_approved_extensions(approved)

    def discover_user_extensions(self, extensions_dir: str) -> list[UserExtensionInfo]:
        """Returns metadata for user extension files without executing them."""

        if not os.path.isdir(extensions_dir):
            return []

        approved = self.get_approved_extensions()
        disabled = self.get_disabled_extensions()
        result: list[UserExtensionInfo] = []

        for filename, filepath, is_package in self._iter_extension_sources(extensions_dir):
            metadata = self.get_metadata(filepath)
            file_hash = self._compute_hash(filepath)
            approved_hash = approved.get(filename)
            status = self._get_user_extension_status(
                metadata.class_name,
                file_hash,
                approved_hash,
                disabled,
            )
            result.append(
                UserExtensionInfo(
                    filename=filename,
                    filepath=filepath,
                    is_package=is_package,
                    class_name=metadata.class_name,
                    group_label=metadata.group_label,
                    description=metadata.description,
                    version=metadata.version,
                    author=metadata.author,
                    organization=metadata.organization,
                    copyright=metadata.copyright,
                    website=metadata.website,
                    file_hash=file_hash,
                    approved_hash=approved_hash,
                    status=status,
                )
            )

        return result

    def reload_user_extensions(self, extensions_dir: str) -> None:
        """Reloads approved user extensions and their Orca-owned integration points."""

        for extension in self._user_extensions:
            extension.disable()
        self._user_extensions.clear()
        self._speech_output_handlers.clear()
        self._braille_output_handlers.clear()
        self.discover_and_load(extensions_dir)
        self.set_up_user_commands()
        command_manager.get_manager().activate_commands("reloaded user extensions")

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

        for filename, filepath, _is_package in self._iter_extension_sources(extensions_dir):
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
            if self._extension_handles_speech_output(extension):
                self._speech_output_handlers.append(extension)
            if self._extension_handles_braille_output(extension):
                self._braille_output_handlers.append(extension)
            msg = f"EXTENSION LOADER: Loaded extension {extension.module_name} from {filename}"
            debug.print_message(debug.LEVEL_INFO, msg, True)

    def set_up_all_commands(self) -> None:
        """Calls set_up_commands on all enabled extensions (built-in and user)."""

        disabled = self.get_disabled_extensions()

        for getter, _group_label in self._builtins:
            ext = getter()
            if ext.module_name in disabled:
                ext.disable()
                continue
            msg = f"EXTENSION LOADER: Loading built-in extension {ext.module_name}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            ext.set_up_commands()

        self.set_up_user_commands()

    def set_up_user_commands(self) -> None:
        """Calls set_up_commands on all enabled user extensions."""

        disabled = self.get_disabled_extensions()

        for ext in self._user_extensions:
            if ext.module_name in disabled:
                ext.disable()
                continue
            msg = f"EXTENSION LOADER: Loading user extension {ext.module_name}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            ext.set_up_commands()

    def shutdown_user_extensions(self) -> None:
        """Notifies loaded user extensions that Orca is shutting down."""

        threads: list[tuple[Extension, threading.Thread]] = []
        for ext in self._user_extensions:
            msg = f"EXTENSION LOADER: Shutting down user extension {ext.module_name}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            thread = threading.Thread(target=self._run_shutdown_hook, args=(ext,), daemon=True)
            thread.start()
            threads.append((ext, thread))

        deadline = time.monotonic() + self._SHUTDOWN_HOOK_TOTAL_TIMEOUT_SECONDS
        for _ext, thread in threads:
            timeout = deadline - time.monotonic()
            if timeout <= 0:
                break
            thread.join(timeout)

        timed_out = [ext.module_name for ext, thread in threads if thread.is_alive()]
        if timed_out:
            names = ", ".join(timed_out)
            msg = f"EXTENSION LOADER: Shutdown hook timed out for: {names}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)

    @staticmethod
    def _run_shutdown_hook(extension: Extension) -> None:
        """Runs an extension shutdown hook, logging exceptions."""

        try:
            extension.on_shutdown()
        except Exception:  # pylint: disable=broad-exception-caught
            debug.print_exception(debug.LEVEL_WARNING)

    def iter_speech_output_handlers(self) -> list[Extension]:
        """Returns enabled user extensions that can handle outgoing speech."""

        if not self._speech_output_handlers:
            return []

        disabled = self.get_disabled_extensions()

        return [ext for ext in self._speech_output_handlers if ext.module_name not in disabled]

    def iter_braille_output_handlers(self) -> list[Extension]:
        """Returns enabled user extensions that can handle outgoing braille."""

        if not self._braille_output_handlers:
            return []

        disabled = self.get_disabled_extensions()

        return [ext for ext in self._braille_output_handlers if ext.module_name not in disabled]

    def get_loaded_user_extension(self, class_name: str) -> Extension | None:
        """Returns the loaded user extension with class_name."""

        return next(
            (ext for ext in self._user_extensions if ext.module_name == class_name),
            None,
        )

    @staticmethod
    def _extension_handles_speech_output(extension: Extension) -> bool:
        """Returns True if extension overrides the speech-output hook."""

        return type(extension).on_speech_output is not Extension.on_speech_output

    @staticmethod
    def _extension_handles_braille_output(extension: Extension) -> bool:
        """Returns True if extension overrides the braille-output hook."""

        return type(extension).on_braille_output is not Extension.on_braille_output

    @staticmethod
    def _get_user_extension_status(
        class_name: str | None,
        file_hash: str,
        approved_hash: str | None,
        disabled: list[str],
    ) -> UserExtensionStatus:
        """Returns the status for a discovered user extension file."""

        if class_name is None:
            return UserExtensionStatus.INVALID
        if approved_hash is None:
            return UserExtensionStatus.UNAPPROVED
        if approved_hash != file_hash:
            return UserExtensionStatus.MODIFIED
        if class_name in disabled:
            return UserExtensionStatus.DISABLED
        return UserExtensionStatus.APPROVED

    @staticmethod
    def get_class_name(filepath: str) -> str | None:
        """Returns the Extension subclass name from a file without executing it."""

        return ExtensionLoader.get_metadata(filepath).class_name

    @staticmethod
    def get_metadata(filepath: str) -> UserExtensionMetadata:
        """Returns metadata from an Extension subclass without executing it."""

        result = UserExtensionMetadata()
        source_path = ExtensionLoader._get_source_file(filepath)
        if source_path is None:
            return result

        try:
            with open(source_path, encoding="utf-8") as f:
                tree = ast.parse(f.read())
        except (OSError, SyntaxError):
            return result

        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            for base in node.bases:
                if isinstance(base, ast.Attribute):
                    name = base.attr
                elif isinstance(base, ast.Name):
                    name = base.id
                else:
                    continue
                if name == "Extension":
                    return UserExtensionMetadata(
                        class_name=node.name,
                        group_label=ExtensionLoader._get_class_string_constant(node, "GROUP_LABEL"),
                        description=ExtensionLoader._get_class_string_constant(node, "DESCRIPTION")
                        or "",
                        version=ExtensionLoader._get_class_string_constant(node, "VERSION") or "",
                        author=ExtensionLoader._get_class_string_constant(node, "AUTHOR") or "",
                        organization=ExtensionLoader._get_class_string_constant(
                            node, "ORGANIZATION"
                        )
                        or "",
                        copyright=ExtensionLoader._get_class_string_constant(node, "COPYRIGHT")
                        or "",
                        website=ExtensionLoader._get_class_string_constant(node, "WEBSITE") or "",
                    )

        return result

    @staticmethod
    def _get_class_string_constant(node: ast.ClassDef, name: str) -> str | None:
        """Returns a string constant assigned in a class body."""

        for child in node.body:
            value: ast.expr | None = None
            if isinstance(child, ast.Assign):
                if not any(
                    isinstance(target, ast.Name) and target.id == name for target in child.targets
                ):
                    continue
                value = child.value
            elif isinstance(child, ast.AnnAssign):
                if not isinstance(child.target, ast.Name) or child.target.id != name:
                    continue
                value = child.value

            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                return value.value

        return None

    @staticmethod
    def _compute_hash(filepath: str) -> str:
        """Returns the SHA256 hex digest of an extension file or package."""

        if os.path.isdir(filepath):
            return ExtensionLoader._compute_package_hash(filepath)

        sha256 = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    @staticmethod
    def _compute_package_hash(dirpath: str) -> str:
        """Returns a deterministic SHA256 digest for a package extension."""

        sha256 = hashlib.sha256()
        for root, dirs, files in os.walk(dirpath):
            dirs[:] = sorted(
                dirname
                for dirname in dirs
                if dirname != "__pycache__" and not dirname.startswith(".")
            )
            for basename in sorted(files):
                if ExtensionLoader._should_ignore_package_file(basename):
                    continue
                path = os.path.join(root, basename)
                relpath = os.path.relpath(path, dirpath).replace(os.sep, "/")
                sha256.update(relpath.encode("utf-8"))
                sha256.update(b"\0")
                with open(path, "rb") as f:
                    for chunk in iter(lambda: f.read(8192), b""):
                        sha256.update(chunk)
                sha256.update(b"\0")
        return sha256.hexdigest()

    @staticmethod
    def _should_ignore_package_file(filename: str) -> bool:
        """Returns True if filename should not affect package approval."""

        return filename.startswith(".") or filename.endswith((".pyc", ".pyo", "~"))

    @staticmethod
    def _iter_extension_sources(extensions_dir: str) -> list[tuple[str, str, bool]]:
        """Returns extension source ids, paths, and package flags."""

        sources: list[tuple[str, str, bool]] = []
        for filename in sorted(os.listdir(extensions_dir)):
            if filename.startswith("_"):
                continue

            filepath = os.path.join(extensions_dir, filename)
            if os.path.isfile(filepath) and filename.endswith(".py"):
                sources.append((filename, filepath, False))
            elif os.path.isdir(filepath):
                init_path = os.path.join(filepath, "__init__.py")
                if os.path.isfile(init_path):
                    sources.append((filename, filepath, True))
        return sources

    @staticmethod
    def _get_source_id(filepath: str) -> str:
        """Returns the approval id for an extension source."""

        return os.path.basename(filepath)

    @staticmethod
    def _get_source_file(filepath: str) -> str | None:
        """Returns the Python file that defines extension metadata."""

        if os.path.isdir(filepath):
            init_path = os.path.join(filepath, "__init__.py")
            if os.path.isfile(init_path):
                return init_path
            return None
        if os.path.isfile(filepath):
            return filepath
        return None

    @staticmethod
    def _load_from_file(filepath: str, filename: str) -> Extension | None:
        """Loads an Extension subclass from a Python file or package."""

        source_file = ExtensionLoader._get_source_file(filepath)
        if source_file is None:
            msg = f"EXTENSION LOADER: No loadable source found for {filepath}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return None

        namespace = os.path.splitext(filename)[0] if filename.endswith(".py") else filename
        module_name = f"orca_user_extension.{namespace}"
        try:
            if os.path.isdir(filepath):
                spec = importlib.util.spec_from_file_location(
                    module_name,
                    source_file,
                    submodule_search_locations=[filepath],
                )
            else:
                spec = importlib.util.spec_from_file_location(module_name, source_file)
            if spec is None or spec.loader is None:
                msg = f"EXTENSION LOADER: Could not create spec for {filepath}"
                debug.print_message(debug.LEVEL_WARNING, msg, True)
                return None

            module = importlib.util.module_from_spec(spec)
            # The module must be in sys.modules before exec_module so that code run during
            # class creation (e.g. @dataclass) can look itself up via sys.modules[__name__].
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
        except Exception as error:  # pylint: disable=broad-exception-caught
            sys.modules.pop(module_name, None)
            msg = f"EXTENSION LOADER: Failed to load {filepath}: {error}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return None

        for attr_name in dir(module):
            obj = module.__dict__.get(attr_name)
            if isinstance(obj, type) and issubclass(obj, Extension) and obj is not Extension:
                try:
                    instance = obj()
                    instance.mark_as_user_extension(namespace)
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
