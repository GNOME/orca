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
from .extension import Extension, get_translation

if TYPE_CHECKING:
    import gettext
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
class ExtensionLoader:  # pylint: disable=too-many-public-methods
    """Discovers, validates, and loads built-in and user extensions."""

    _SHUTDOWN_HOOK_TOTAL_TIMEOUT_SECONDS = 0.5

    def __init__(self) -> None:
        self._builtins: list[tuple[Callable[[], Extension], str]] = []
        self._user_extensions: list[Extension] = []
        self._user_extensions_by_source: dict[str, Extension] = {}
        self._speech_output_handlers: list[Extension] = []
        self._braille_output_handlers: list[Extension] = []
        self._orca_is_ready = False

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

    def reload_user_extension(self, extensions_dir: str, source_id: str) -> None:
        """Reloads one user extension while preserving unrelated instances."""

        old_extension = self._user_extensions_by_source.pop(source_id, None)
        if old_extension is not None:
            if self._orca_is_ready:
                self._run_lifecycle_hook(old_extension, old_extension.on_disabled)
            old_extension.disable()
            self._sync_user_extension_lists()

        self._remove_user_extension_modules(source_id)
        new_extension = self._load_user_extension_source(extensions_dir, source_id)
        if old_extension is None and new_extension is None:
            return

        # Re-register commands in source order so keybinding conflict winners
        # do not depend on which extension was reloaded.
        for extension in self._user_extensions_by_source.values():
            extension.reset_commands()

        if new_extension is not None:
            self._user_extensions_by_source[source_id] = new_extension
        self._sync_user_extension_lists()
        self.set_up_user_commands()
        command_manager.get_manager().activate_commands("reloaded user extension")
        if self._orca_is_ready and new_extension is not None:
            self._run_lifecycle_hook(new_extension, new_extension.on_enabled)

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
            extension = self._load_user_extension(filename, filepath, approved, disabled)
            if extension is None:
                continue

            self._user_extensions_by_source[filename] = extension

        self._sync_user_extension_lists()

    def _load_user_extension_source(
        self,
        extensions_dir: str,
        source_id: str,
    ) -> Extension | None:
        """Loads source_id if it is present, approved, and enabled."""

        if not os.path.isdir(extensions_dir):
            return None

        source = None
        for filename, filepath, _is_package in self._iter_extension_sources(extensions_dir):
            if filename == source_id:
                source = (filename, filepath)
                break
        if source is None:
            return None

        filename, filepath = source
        return self._load_user_extension(
            filename,
            filepath,
            self.get_approved_extensions(),
            self.get_disabled_extensions(),
        )

    def _load_user_extension(
        self,
        filename: str,
        filepath: str,
        approved: dict[str, str],
        disabled: list[str],
    ) -> Extension | None:
        """Loads an approved, enabled user-extension source."""

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
            return None

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
            return None

        if disabled:
            class_name = self.get_class_name(filepath)
            if class_name in disabled:
                msg = f"EXTENSION LOADER: Extension {class_name} is disabled. Skipping."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return None

        extension = self._load_from_file(filepath, filename)
        if extension is None:
            return None

        # Static metadata can differ from the subclass selected when the module is loaded.
        if extension.module_name in disabled:
            msg = f"EXTENSION LOADER: Extension {extension.module_name} is disabled. Skipping."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            extension.disable()
            self._remove_user_extension_modules(filename)
            return None

        msg = f"EXTENSION LOADER: Loaded extension {extension.module_name} from {filename}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return extension

    def _sync_user_extension_lists(self) -> None:
        """Rebuilds the user-extension and output-handler lists in source order."""

        self._user_extensions = [
            self._user_extensions_by_source[source_id]
            for source_id in sorted(self._user_extensions_by_source)
        ]
        self._speech_output_handlers = [
            extension
            for extension in self._user_extensions
            if self._extension_handles_speech_output(extension)
        ]
        self._braille_output_handlers = [
            extension
            for extension in self._user_extensions
            if self._extension_handles_braille_output(extension)
        ]

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

    def notify_user_extensions_ready(self) -> None:
        """Notifies loaded user extensions that Orca is ready."""

        if self._orca_is_ready:
            return
        self._orca_is_ready = True
        for extension in self._user_extensions:
            self._run_lifecycle_hook(extension, extension.on_ready)

    @staticmethod
    def _run_lifecycle_hook(
        extension: Extension,
        hook: Callable[[], None],
    ) -> None:
        """Runs a lifecycle hook for one user extension, logging exceptions."""

        msg = f"EXTENSION LOADER: Calling {extension.module_name}.{hook.__name__}()"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        try:
            hook()
        except Exception:  # pylint: disable=broad-exception-caught
            debug.print_exception(debug.LEVEL_WARNING)

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

        translation = get_translation(source_path)
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
                        group_label=ExtensionLoader._get_class_string_constant(
                            node, "GROUP_LABEL", translation
                        ),
                        description=ExtensionLoader._get_class_string_constant(
                            node, "DESCRIPTION", translation
                        )
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
    def _get_class_string_constant(
        node: ast.ClassDef,
        name: str,
        translation: gettext.NullTranslations | None = None,
    ) -> str | None:
        """Returns a possibly localized string assigned in a class body."""

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

            message, context = ExtensionLoader._get_translatable_literal(value)
            if message is None:
                continue
            if translation is None:
                return message
            if context is not None:
                return translation.pgettext(context, message)
            return translation.gettext(message)

        return None

    @staticmethod
    def _get_translatable_literal(value: ast.expr | None) -> tuple[str | None, str | None]:
        """Returns the literal message and optional context from an expression."""

        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            return value.value, None
        if not isinstance(value, ast.Call):
            return None, None

        function_name = getattr(value.func, "id", getattr(value.func, "attr", None))
        if function_name in ("_", "gettext") and len(value.args) == 1:
            message = value.args[0]
            if isinstance(message, ast.Constant) and isinstance(message.value, str):
                return message.value, None

        if function_name == "pgettext" and len(value.args) == 2:
            context, message = value.args
            if (
                isinstance(context, ast.Constant)
                and isinstance(context.value, str)
                and isinstance(message, ast.Constant)
                and isinstance(message.value, str)
            ):
                return message.value, context.value

        return None, None

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
    def _get_user_extension_namespace(source_id: str) -> str:
        """Returns the Python namespace for a user-extension source id."""

        if source_id.endswith(".py"):
            return os.path.splitext(source_id)[0]
        return source_id

    @staticmethod
    def _remove_user_extension_modules(source_id: str) -> None:
        """Removes a user extension and its submodules from the module cache."""

        namespace = ExtensionLoader._get_user_extension_namespace(source_id)
        module_name = f"orca_user_extension.{namespace}"
        names = [
            name
            for name in sys.modules
            if name == module_name or name.startswith(f"{module_name}.")
        ]
        for name in names:
            sys.modules.pop(name, None)

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

        namespace = ExtensionLoader._get_user_extension_namespace(filename)
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
            ExtensionLoader._remove_user_extension_modules(filename)
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
