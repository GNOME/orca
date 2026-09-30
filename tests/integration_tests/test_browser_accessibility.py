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

"""Checks browser accessibility, retrying with an environment override if needed."""

from __future__ import annotations

import contextlib
import os
import shutil
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from orca.output_reader import OutputReader

from .apps import browser, chromium_browser
from .harness import keyboard, sandbox
from .harness.orca_session import OrcaSession
from .orca_fixtures import BrowserSession

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

    BrowserLaunch = Callable[[bool], contextlib.AbstractContextManager[BrowserSession]]

_ACCESSIBILITY_VARIABLES = {"chromium": "ACCESSIBILITY_ENABLED", "firefox": "GNOME_ACCESSIBILITY"}


@pytest.fixture(params=("chromium", "firefox"))
def browser_accessibility(
    request: pytest.FixtureRequest, tmp_path: Path
) -> tuple[str, BrowserLaunch]:
    """Selects a system browser and provides fresh sessions for each attempt."""

    name = request.param
    app = browser.BROWSERS[name]
    binary = next(
        (path for candidate in app.BINARY_NAMES if (path := shutil.which(candidate))), None
    )
    if name == browser.selected_browser() and (
        os.environ.get("ORCA_TEST_BROWSER_BINARY")
        or (name == "chromium" and os.environ.get("ORCA_TEST_CHROMIUM_BINARY"))
    ):
        binary = browser.resolve_binary(name)
    if binary is None:
        pytest.skip(f"{name} is not installed; tried {app.BINARY_NAMES!r}")
    print(f"Browser accessibility smoke test: {name}, executable: {binary}")

    def launch(enabled: bool) -> contextlib.AbstractContextManager[BrowserSession]:
        attempt_dir = tmp_path / ("enabled" if enabled else "automatic")
        attempt_dir.mkdir()
        return _browser_session(name, binary, attempt_dir, enabled)

    return name, launch


@contextlib.contextmanager
def _browser_session(
    name: str, binary: str, tmp_path: Path, enabled: bool
) -> Iterator[BrowserSession]:
    """Starts Orca before the browser and closes both before another attempt."""

    app = browser.BROWSERS[name]
    profile = tmp_path / "profile"
    profile.mkdir()
    page = Path(__file__).parent / "web_pages" / "browser_accessibility.html"
    flags = app.prepare_launch(profile)
    if name == "chromium":
        argv = chromium_browser.build_argv(
            page.as_uri(), profile, binary, extra_flags=flags, force_accessibility=False
        )
    else:
        argv = app.build_argv(page.as_uri(), profile, binary, extra_flags=flags)

    env = sandbox.build_sandbox_env(tmp_path)
    for variable in (*_ACCESSIBILITY_VARIABLES.values(), "QT_ACCESSIBILITY"):
        env.pop(variable, None)
    if enabled:
        env[_ACCESSIBILITY_VARIABLES[name]] = "1"
    env["ORCA_TEST_SPEECH_SERVER_FACTORY"] = "tests.integration_tests.harness.dummy_speech_server"
    sandbox.write_sandbox_speechd_conf(tmp_path)
    orca = OrcaSession(env)
    try:
        orca.launch()
        orca.set("DocumentPresenter", "SayAllOnLoad", False)
        speech_log = tmp_path / "speech.jsonl"
        braille_log = tmp_path / "braille.jsonl"
        orca.set_log_file("SpeechPresenter", str(speech_log))
        orca.set_log_file("BraillePresenter", str(braille_log))
        reader = OutputReader(str(speech_log), str(braille_log))
        reader.set_idle_check(orca.is_idle)
        reader.start()
        try:
            # Let Orca discover the document; querying its tree here could activate accessibility.
            process = subprocess.Popen(argv, env=env)
            try:
                yield BrowserSession(orca=orca, reader=reader, browser=name)
            finally:
                if process.poll() is None:
                    process.terminate()
                    try:
                        process.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()
        finally:
            reader.stop()
    finally:
        orca.quit()


def _check_presentation(session: BrowserSession) -> None:
    """Checks presentation of a focused control and heading navigation."""

    reader = session.reader
    timeout = 20 * float(os.environ.get("ORCA_TEST_TIMEOUT_SCALE") or 1.0)
    reader.wait_for_speech("Check connection", timeout=timeout)
    reader.wait_for_braille("Check connection", timeout=timeout)
    reader.drain()

    keyboard.tap_key(keyboard.KEYSYM_H)
    reader.wait_for_speech("Browser connection ready", timeout=timeout)
    reader.wait_for_braille("Browser connection ready", timeout=timeout)


@pytest.mark.native_app
def test_browser_accessibility(
    browser_accessibility: tuple[str, BrowserLaunch], capsys: pytest.CaptureFixture[str]
) -> None:
    """Checks browser accessibility with an optional environment override."""

    name, launch = browser_accessibility
    variable = _ACCESSIBILITY_VARIABLES[name]
    failures = []
    for enabled in (False, True):
        try:
            with launch(enabled) as session:
                _check_presentation(session)
        except TimeoutError as error:
            failures.append(str(error))
            continue
        if enabled:
            with capsys.disabled():
                print(
                    f"\n{name}: passed on retry with {variable}=1. "
                    "This environment may need that setting for browser accessibility.",
                    flush=True,
                )
        return

    pytest.fail(
        f"{name} accessibility smoke test failed.\n"
        f"Without accessibility variables: {failures[0]}\n"
        f"With {variable}=1: {failures[1]}\n"
        "Check browser startup errors, accessibility support, and AT-SPI dependencies. "
        "Do not file an Orca bug for this environment check. See tests/README.md.",
        pytrace=False,
    )
