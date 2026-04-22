# Unit tests for output_recorder.py methods.
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

"""Unit tests for output_recorder.py methods."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path


def _read_records(path: Path) -> list[dict]:
    """Returns the JSON records written to path, one per line."""

    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


@pytest.mark.unit
class TestOutputRecorder:
    """Tests for the OutputRecorder class."""

    def test_records_before_set_path_are_dropped(self, tmp_path: Path) -> None:
        """A recorder with no open file silently drops records."""

        from orca.output_recorder import OutputRecorder

        recorder = OutputRecorder("test")
        recorder.record(kind="speech", text="ignored")
        assert recorder.is_open() is False
        assert list(tmp_path.iterdir()) == []

    def test_set_path_writes_jsonl(self, tmp_path: Path) -> None:
        """Records are written as one JSON object per line."""

        from orca.output_recorder import OutputRecorder

        log = tmp_path / "out.jsonl"
        recorder = OutputRecorder("test")
        assert recorder.set_path(str(log)) is True
        assert recorder.is_open() is True

        recorder.record(kind="speech", text="hello")
        recorder.record(kind="braille", cursor_cell=3, string="hi")

        assert _read_records(log) == [
            {"kind": "speech", "text": "hello"},
            {"kind": "braille", "cursor_cell": 3, "string": "hi"},
        ]

    def test_set_path_with_empty_string_closes_file(self, tmp_path: Path) -> None:
        """An empty path closes the current file and stops recording."""

        from orca.output_recorder import OutputRecorder

        log = tmp_path / "out.jsonl"
        recorder = OutputRecorder("test")
        recorder.set_path(str(log))
        recorder.record(kind="speech", text="kept")

        assert recorder.set_path("") is True
        assert recorder.is_open() is False

        recorder.record(kind="speech", text="dropped")
        assert _read_records(log) == [{"kind": "speech", "text": "kept"}]

    def test_set_path_replaces_previous_file(self, tmp_path: Path) -> None:
        """A second set_path closes the first file and opens the new one."""

        from orca.output_recorder import OutputRecorder

        first = tmp_path / "first.jsonl"
        second = tmp_path / "second.jsonl"
        recorder = OutputRecorder("test")
        recorder.set_path(str(first))
        recorder.record(kind="speech", text="first-only")
        recorder.set_path(str(second))
        recorder.record(kind="speech", text="second-only")

        assert _read_records(first) == [{"kind": "speech", "text": "first-only"}]
        assert _read_records(second) == [{"kind": "speech", "text": "second-only"}]

    def test_set_path_unwritable_returns_false(self, tmp_path: Path) -> None:
        """Failing to open the log path returns False and leaves the recorder closed."""

        from orca.output_recorder import OutputRecorder

        bad = tmp_path / "missing-dir" / "out.jsonl"
        recorder = OutputRecorder("test")
        assert recorder.set_path(str(bad)) is False
        assert recorder.is_open() is False

    def test_close_is_idempotent(self, tmp_path: Path) -> None:
        """Calling close() on an already-closed recorder is a no-op."""

        from orca.output_recorder import OutputRecorder

        recorder = OutputRecorder("test")
        recorder.set_path(str(tmp_path / "out.jsonl"))
        recorder.close()
        recorder.close()
        assert recorder.is_open() is False

    def test_unicode_round_trip(self, tmp_path: Path) -> None:
        """Non-ASCII text is written and read back unchanged."""

        from orca.output_recorder import OutputRecorder

        log = tmp_path / "out.jsonl"
        recorder = OutputRecorder("test")
        recorder.set_path(str(log))
        recorder.record(kind="speech", text="héllo ⠁⠃⠉")
        assert _read_records(log) == [{"kind": "speech", "text": "héllo ⠁⠃⠉"}]
