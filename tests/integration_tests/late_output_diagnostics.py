"""Collects late output after an empty-capture assertion fails in the CI comparison."""

from __future__ import annotations

import queue
import time
from typing import TYPE_CHECKING

import pytest

from .orca_fixtures import NativeAppSession

if TYPE_CHECKING:
    from collections.abc import Iterator

    from orca.output_reader import OutputReader


class LateOutputDiagnostics:
    """Observes failed captures without changing their result or Orca's debug level."""

    def __init__(self) -> None:
        self._reader: OutputReader | None = None

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_call(self, item: pytest.Item) -> Iterator[None]:
        """Makes the current session's reader available only during the test call."""

        self._reader = next(
            (
                value.reader
                for value in item.funcargs.values()
                if isinstance(value, NativeAppSession)
            ),
            None,
        )
        try:
            yield
        finally:
            self._reader = None

    def pytest_assertrepr_compare(self, op: str, left: object) -> None:
        """Collects raw output for two seconds after an empty speech/braille mismatch."""

        if self._reader is None or op != "==" or not isinstance(left, tuple) or len(left) != 2:
            return
        if any(not isinstance(part, list) or part for part in left):
            return

        started = time.monotonic()
        records = []
        while (remaining := 2.0 - (time.monotonic() - started)) > 0:
            try:
                record = self._reader._queue.get(timeout=remaining)
            except queue.Empty:
                break
            records.append((time.monotonic() - started, record))

        print("[late-output] Empty capture failed; original assertion remains failed.")
        for elapsed, record in records:
            print(f"[late-output] +{elapsed:.3f}s: {record!r}")
        if not records:
            print("[late-output] No output arrived within two additional seconds.")


def pytest_configure(config: pytest.Config) -> None:
    """Registers diagnostics when this plugin is explicitly loaded."""

    config.pluginmanager.register(LateOutputDiagnostics())
