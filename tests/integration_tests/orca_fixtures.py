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
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import gi
import pytest

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi, GLib

from orca.output_reader import OutputReader

from .apps import (
    chromium_browser,
    gtk3_terminal,
    gtk3_text_view,
    gtk3_toolbar,
    gtk3_tree_view,
    gtk3_two_entries,
    gtk3_two_windows,
    gtk3_widget_notebook,
)
from .harness import sandbox
from .harness.orca_session import OrcaSession

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator
    from types import ModuleType
    from typing import Literal

_WEB_PAGES_DIR = Path(__file__).parent / "web_pages"

_DUMMY_SPEECH_SERVER_MODULE = f"{__name__.rsplit('.', 1)[0]}.harness.dummy_speech_server"


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


def _make_native_app_fixture(
    app: ModuleType,
    lines: tuple[str, ...] = (),
    scope: Literal["session", "function"] = "session",
) -> Callable[..., Iterator[NativeAppSession]]:
    @pytest.fixture(scope=scope, name=app.__name__.rsplit(".", 1)[-1])
    def fixture(tmp_path_factory: pytest.TempPathFactory) -> Iterator[NativeAppSession]:
        yield from _run_native_app(
            tmp_path_factory,
            app.__name__,
            ready_predicate=_name_equals(app.APP_TITLE),
            lines=lines,
        )

    return fixture


_gtk3_text_view = _make_native_app_fixture(
    gtk3_text_view,
    lines=(
        "Line one.",
        "Line two has additional words to make it long enough that the text view wraps it.",
        "Line three.",
        "Line four also has extra words to push it past the wrap boundary in the view.",
        "Last line.",
    ),
)
_gtk3_tree_view = _make_native_app_fixture(gtk3_tree_view, scope="function")
_gtk3_two_entries = _make_native_app_fixture(gtk3_two_entries, scope="function")
_gtk3_two_windows = _make_native_app_fixture(gtk3_two_windows, scope="function")
_gtk3_widget_notebook = _make_native_app_fixture(gtk3_widget_notebook)
_gtk3_toolbar = _make_native_app_fixture(gtk3_toolbar, scope="function")

_PAGER_DOC = "\n".join(f"line {n:02d}" for n in range(1, 21)) + "\n"


def _make_terminal_fixture(
    name: str,
    *,
    binary_names: tuple[str, ...],
    args: tuple[str, ...] = (),
    files: dict[str, str] | None = None,
) -> Callable[..., Iterator[NativeAppSession]]:
    @pytest.fixture(scope="function", name=name)
    def fixture(tmp_path_factory: pytest.TempPathFactory) -> Iterator[NativeAppSession]:
        yield from _run_terminal_app(
            tmp_path_factory, binary_names=binary_names, args=args, files=files
        )

    return fixture


_gtk3_terminal_shell = _make_terminal_fixture(
    "gtk3_terminal_shell", binary_names=("bash",), args=("--norc", "--noprofile")
)
_gtk3_terminal_flatrev = _make_terminal_fixture(
    "gtk3_terminal_flatrev",
    binary_names=("bash",),
    args=("--norc", "--noprofile"),
    files={"t.sh": "printf c1; sleep 3; printf '\\rc2'; echo\n"},
)
_gtk3_terminal_pager = _make_terminal_fixture(
    "gtk3_terminal_pager", binary_names=("less",), args=("doc.txt",), files={"doc.txt": _PAGER_DOC}
)

_WIDE_PAGER_DOC = "top\nthis line is wider than the display now\nbottom\n"
_gtk3_terminal_wide_pager = _make_terminal_fixture(
    "gtk3_terminal_wide_pager",
    binary_names=("less",),
    args=("doc.txt",),
    files={"doc.txt": _WIDE_PAGER_DOC},
)
_gtk3_terminal_vim = _make_terminal_fixture(
    "gtk3_terminal_vim",
    binary_names=("vim",),
    args=("-u", "NONE", "-i", "NONE", "-n", "-c", "set ruler", "doc.txt"),
    files={"doc.txt": "hello\n"},
)


def _run_native_app(
    tmp_path_factory: pytest.TempPathFactory,
    app_module: str,
    *,
    ready_predicate: Callable[[Atspi.Accessible], bool],
    lines: tuple[str, ...] = (),
) -> Iterator[NativeAppSession]:
    """Runs app_module under its own Orca subprocess and yields a NativeAppSession."""

    sandbox_dir = tmp_path_factory.mktemp("orca-native-app")
    extra_args: list[str] = []
    if lines:
        content_file = sandbox_dir / "app-content.txt"
        content_file.write_text("\n".join(lines), encoding="utf-8")
        extra_args = [str(content_file)]
    argv = [sys.executable, "-m", app_module, *extra_args]
    yield from _run_app_with_orca(sandbox_dir, argv=argv, ready_predicate=ready_predicate)


def _vte_available() -> bool:
    """Returns True if the VTE 2.91 (GTK3) typelib is installed."""

    return "2.91" in gi.Repository.get_default().enumerate_versions("Vte")


def _run_terminal_app(
    tmp_path_factory: pytest.TempPathFactory,
    *,
    binary_names: tuple[str, ...],
    args: tuple[str, ...] = (),
    files: dict[str, str] | None = None,
) -> Iterator[NativeAppSession]:
    """Runs a program inside a VTE terminal under its own Orca subprocess."""

    if not _vte_available():
        pytest.skip("VTE 2.91 (GTK3) typelib is not available")
    binary = _resolve_binary(binary_names)
    if binary is None:
        pytest.skip(f"no terminal program found among {binary_names!r}")

    sandbox_dir = tmp_path_factory.mktemp("orca-terminal")
    work_dir = sandbox_dir / "work"
    work_dir.mkdir()
    for filename, content in (files or {}).items():
        (work_dir / filename).write_text(content, encoding="utf-8")

    argv = [sys.executable, "-m", gtk3_terminal.__name__, str(work_dir), binary, *args]
    yield from _run_app_with_orca(
        sandbox_dir, argv=argv, ready_predicate=_name_equals(gtk3_terminal.APP_TITLE)
    )


def _run_app_with_orca(
    sandbox_dir: Path,
    *,
    argv: list[str],
    ready_predicate: Callable[[Atspi.Accessible], bool] | None = None,
) -> Iterator[NativeAppSession]:
    """Runs argv with Orca attached, yielding a NativeAppSession until teardown."""

    speech_log = sandbox_dir / "speech.jsonl"
    braille_log = sandbox_dir / "braille.jsonl"
    env = sandbox.build_sandbox_env(sandbox_dir)
    env["ORCA_TEST_SPEECH_SERVER_FACTORY"] = _DUMMY_SPEECH_SERVER_MODULE
    sandbox.write_sandbox_speechd_conf(sandbox_dir)

    with _launch_subprocess(argv, env) as (_process, app_accessible):
        if ready_predicate is not None:
            _wait_until_ready(app_accessible, ready_predicate)
        orca = OrcaSession(env)
        orca.launch()
        try:
            orca.set("SpeechPresenter", "LogFile", str(speech_log))
            orca.set("BraillePresenter", "LogFile", str(braille_log))
            reader = OutputReader(str(speech_log), str(braille_log))
            reader.set_idle_check(orca.is_idle)
            reader.start()
            try:
                yield NativeAppSession(orca=orca, reader=reader)
            finally:
                reader.stop()
        finally:
            orca.quit()


@contextlib.contextmanager
def _launch_subprocess(
    argv: list[str],
    env: dict[str, str],
    *,
    timeout: float = 30.0,
    poll_interval: float = 0.05,
) -> Iterator[tuple[subprocess.Popen, Atspi.Accessible]]:
    """Spawns argv, waits for its pid to appear in AT-SPI, yields (process, app_accessible)."""

    process = subprocess.Popen(argv, env=env)
    try:
        deadline = time.monotonic() + timeout
        app_accessible: Atspi.Accessible | None = None
        while time.monotonic() < deadline:
            if (returncode := process.poll()) is not None:
                raise RuntimeError(f"Test app {argv!r} exited early with code {returncode}")
            app_accessible = _find_registered_application(process.pid)
            if app_accessible is not None:
                break
            time.sleep(poll_interval)
        if app_accessible is None:
            raise TimeoutError(f"Test app {argv!r} did not appear in AT-SPI within {timeout}s")
        yield process, app_accessible
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=2.0)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


def _find_registered_application(pid: int) -> Atspi.Accessible | None:
    """Returns an accessible application with this pid, or None."""

    try:
        desktop = Atspi.get_desktop(0)
        child_count = desktop.get_child_count()
    except GLib.GError:
        return None

    for index in range(child_count):
        try:
            child = desktop.get_child_at_index(index)
            child_pid = Atspi.Accessible.get_process_id(child)
        except GLib.GError:
            continue
        if child_pid == pid:
            return child
    return None


def _wait_until_ready(
    app_accessible: Atspi.Accessible,
    predicate: Callable[[Atspi.Accessible], bool],
    timeout: float = 10.0,
    poll_interval: float = 0.1,
) -> None:
    """Polls predicate(app_accessible) until True or raises TimeoutError."""

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            if predicate(app_accessible):
                return
        except GLib.GError:
            pass
        time.sleep(poll_interval)
    raise TimeoutError(f"App {app_accessible!r} did not become ready within {timeout}s")


def _name_equals(target: str) -> Callable[[Atspi.Accessible], bool]:
    """Predicate: app accessible's name equals target."""

    def predicate(accessible: Atspi.Accessible) -> bool:
        return Atspi.Accessible.get_name(accessible) == target

    return predicate


def _name_suffix(suffix: str) -> Callable[[Atspi.Accessible], bool]:
    """Predicate: app accessible or any direct child has a name ending with suffix."""

    def predicate(accessible: Atspi.Accessible) -> bool:
        if (name := Atspi.Accessible.get_name(accessible)) and name.endswith(suffix):
            return True
        for index in range(accessible.get_child_count()):
            child_name = Atspi.Accessible.get_name(accessible.get_child_at_index(index))
            if child_name and child_name.endswith(suffix):
                return True
        return False

    return predicate


def _resolve_binary(names: tuple[str, ...]) -> str | None:
    """Returns the first of names that resolves on PATH, or None."""

    for name in names:
        if path := shutil.which(name):
            return path
    return None


def _run_browser_session(
    tmp_path_factory: pytest.TempPathFactory,
    *,
    app: ModuleType,
    page: str,
    caret_browsing: bool = False,
) -> Iterator[NativeAppSession]:
    """Launches app loading web_pages/<page> under its own Orca subprocess."""

    binary = _resolve_binary(app.BINARY_NAMES)
    if binary is None:
        pytest.skip(f"{app.__name__}: no binary found among {app.BINARY_NAMES!r}")

    source_page = _WEB_PAGES_DIR / page
    if not source_page.is_file():
        raise FileNotFoundError(f"Test page not found: {source_page}")

    sandbox_dir = tmp_path_factory.mktemp("orca-browser")
    page_path = sandbox_dir / page
    page_path.write_bytes(source_page.read_bytes())
    profile_dir = sandbox_dir / "browser-profile"
    profile_dir.mkdir()
    argv = [
        sys.executable,
        "-m",
        app.__name__,
        f"file://{page_path}",
        str(profile_dir),
        binary,
    ]
    if caret_browsing:
        argv.append("--enable-caret-browsing")
    yield from _run_app_with_orca(
        sandbox_dir,
        argv=argv,
        ready_predicate=_name_suffix(app.READY_SUFFIX),
    )


_BROWSER_APPS: dict[str, ModuleType] = {"chromium": chromium_browser}


def _make_web_fixture(
    page: str, *, caret_browsing: bool = False
) -> Callable[..., Iterator[NativeAppSession]]:
    @pytest.fixture(scope="session", name=Path(page).stem, params=["chromium"])
    def fixture(
        request: pytest.FixtureRequest,
        tmp_path_factory: pytest.TempPathFactory,
    ) -> Iterator[NativeAppSession]:
        yield from _run_browser_session(
            tmp_path_factory,
            app=_BROWSER_APPS[request.param],
            page=page,
            caret_browsing=caret_browsing,
        )

    return fixture


_web_basic = _make_web_fixture("web_basic.html")
_web_languages = _make_web_fixture("web_languages.html")
_web_tables = _make_web_fixture("web_tables.html")
_web_form_fields = _make_web_fixture("web_form_fields.html")
_web_landmarks = _make_web_fixture("web_landmarks.html")
_web_inline_landmarks = _make_web_fixture("web_inline_landmarks.html")
_web_inline_list = _make_web_fixture("web_inline_list.html")
_web_nested_headings = _make_web_fixture("web_nested_headings.html")
_web_label_inference = _make_web_fixture("web_label_inference.html")
_web_structural_navigation = _make_web_fixture("web_structural_navigation.html")
_web_headings = _make_web_fixture("web_headings.html")
_web_field_states = _make_web_fixture("web_field_states.html")
_web_wrapping_text = _make_web_fixture("web_wrapping_text.html")
_web_lists = _make_web_fixture("web_lists.html")
_web_sliders = _make_web_fixture("web_sliders.html")
_web_text_attributes = _make_web_fixture("web_text_attributes.html")
_web_tree = _make_web_fixture("web_tree.html")
_web_live_regions = _make_web_fixture("web_live_regions.html")
_web_dialogs = _make_web_fixture("web_dialogs.html")
_web_aria_spinbutton = _make_web_fixture("web_aria_spinbutton.html")
_web_autocomplete = _make_web_fixture("web_autocomplete.html")
_web_dynamic_content = _make_web_fixture("web_dynamic_content.html")
_web_editing = _make_web_fixture("web_editing.html")
_web_long_line = _make_web_fixture("web_long_line.html")
_web_contracted_braille = _make_web_fixture("web_contracted_braille.html", caret_browsing=True)
_web_attribute_mask = _make_web_fixture("web_attribute_mask.html", caret_browsing=True)
