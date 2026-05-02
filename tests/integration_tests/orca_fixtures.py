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

"""Session-scoped fixtures that own an Orca subprocess for integration tests."""

from __future__ import annotations

import contextlib
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING

import gi
import pytest

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi, GLib

from orca.output_reader import OutputReader

from .apps import gtk3_text_view
from .harness import sandbox
from .harness.orca_session import OrcaSession

if TYPE_CHECKING:
    from collections.abc import Iterator


@dataclass
class NativeAppSession:
    """Handle yielded by a native-app fixture: the Orca session and its output reader."""

    orca: OrcaSession
    reader: OutputReader


@pytest.fixture(scope="session", name="orca")
def _orca(tmp_path_factory: pytest.TempPathFactory) -> Iterator[OrcaSession]:
    """Launches Orca as a subprocess for the test session and quits it at the end."""

    sandbox_dir = tmp_path_factory.mktemp("orca-session")
    env = sandbox.build_sandbox_env(sandbox_dir)
    sandbox.write_sandbox_speechd_conf(sandbox_dir)

    session = OrcaSession(env)
    session.launch()
    try:
        yield session
    finally:
        session.quit()


@pytest.fixture(scope="session", name="gtk3_text_view")
def _gtk3_text_view(
    tmp_path_factory: pytest.TempPathFactory,
) -> Iterator[NativeAppSession]:
    """Launches the gtk3_text_view test app with Orca and yields a NativeAppSession."""

    yield from _run_native_app(
        tmp_path_factory,
        "tests.integration_tests.apps.gtk3_text_view",
        gtk3_text_view.APP_TITLE,
        lines=(
            "Line one.",
            "Line two has additional words to make it long enough that the text view wraps it.",
            "Line three.",
            "Line four also has extra words to push it past the wrap boundary in the view.",
            "Last line.",
        ),
    )


def _run_native_app(
    tmp_path_factory: pytest.TempPathFactory,
    app_module: str,
    app_title: str,
    *,
    lines: tuple[str, ...] = (),
) -> Iterator[NativeAppSession]:
    """Runs app_module under its own Orca subprocess and yields a NativeAppSession."""

    sandbox_dir = tmp_path_factory.mktemp("orca-native-app")
    speech_log = sandbox_dir / "speech.jsonl"
    braille_log = sandbox_dir / "braille.jsonl"
    env = sandbox.build_sandbox_env(sandbox_dir)
    sandbox.write_sandbox_speechd_conf(sandbox_dir)

    extra_args: list[str] = []
    if lines:
        content_file = sandbox_dir / "app-content.txt"
        content_file.write_text("\n".join(lines), encoding="utf-8")
        extra_args = [str(content_file)]

    with _launch_app(app_module, app_title, env, extra_args=extra_args):
        orca = OrcaSession(env)
        orca.launch()
        try:
            orca.set("SpeechPresenter", "LogFile", str(speech_log))
            orca.set("BraillePresenter", "LogFile", str(braille_log))
            reader = OutputReader(str(speech_log), str(braille_log))
            reader.start()
            try:
                yield NativeAppSession(orca=orca, reader=reader)
            finally:
                reader.stop()
        finally:
            orca.quit()


@contextlib.contextmanager
def _launch_app(
    module_path: str,
    title: str,
    env: dict[str, str],
    timeout: float = 15.0,
    poll_interval: float = 0.05,
    extra_args: list[str] | None = None,
) -> Iterator[subprocess.Popen]:
    """Launches a Python module as a subprocess, waits for AT-SPI, and cleans up on exit."""

    argv = [sys.executable, "-m", module_path, *(extra_args or [])]
    process = subprocess.Popen(argv, env=env)
    try:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if (returncode := process.poll()) is not None:
                raise RuntimeError(f"Test app {module_path!r} exited early with code {returncode}")
            if _application_is_registered(process.pid, title):
                break
            time.sleep(poll_interval)
        else:
            raise TimeoutError(
                f"Test app {module_path!r} (title={title!r}) "
                f"did not appear in AT-SPI within {timeout}s"
            )
        yield process
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=2.0)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


def _application_is_registered(pid: int, title: str) -> bool:
    """Returns True when an accessible application with this pid and name exists."""

    try:
        desktop = Atspi.get_desktop(0)
        child_count = desktop.get_child_count()
    except GLib.GError:
        return False

    for index in range(child_count):
        try:
            child = desktop.get_child_at_index(index)
            child_pid = Atspi.Accessible.get_process_id(child)
            child_name = Atspi.Accessible.get_name(child)
        except GLib.GError:
            continue
        if child_pid == pid and child_name == title:
            return True
    return False
