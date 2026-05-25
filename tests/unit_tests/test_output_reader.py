# Unit tests for output_reader.py methods.
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
# pylint: disable=protected-access

"""Unit tests for output_reader.py methods."""

from __future__ import annotations

import json
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def _write_line(path: Path, payload: dict) -> None:
    """Appends a single JSON line to path."""

    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload) + "\n")


def test_braille_filters_out_speech() -> None:
    """braille() keeps only BrailleRecord entries."""

    from orca.output_reader import BrailleRecord, SpeechRecord, braille

    records: list[SpeechRecord | BrailleRecord] = [
        SpeechRecord(text="ignored"),
        BrailleRecord(cursor_cell=3, full="Hello.", visible="Hello."),
        BrailleRecord(cursor_cell=0, full="World.", visible="World."),
    ]
    assert braille(records) == ["Hello.", "World."]


def test_reader_parses_records_from_both_logs(tmp_path: Path) -> None:
    """OutputReader parses both files and returns records via drain()."""

    from orca.output_reader import BrailleRecord, OutputReader, SpeechRecord, braille, speech

    speech_path = tmp_path / "s.jsonl"
    braille_path = tmp_path / "b.jsonl"

    reader = OutputReader(str(speech_path), str(braille_path))
    reader.start()
    try:
        time.sleep(0.1)
        _write_line(speech_path, {"kind": "speech", "text": "hello"})
        _write_line(
            braille_path,
            {"kind": "braille", "cursor_cell": 3, "full": "Hello.", "visible": "Hello."},
        )

        records = reader.drain(quiescence_timeout=0.3)
    finally:
        reader.stop()

    speech_records = [r for r in records if isinstance(r, SpeechRecord)]
    braille_records = [r for r in records if isinstance(r, BrailleRecord)]

    assert speech(records) == ["hello"]
    assert len(speech_records) == 1
    assert braille(records) == ["Hello."]
    assert len(braille_records) == 1
    assert braille_records[0].cursor_cell == 3


def test_drain_returns_empty_when_no_output(tmp_path: Path) -> None:
    """drain() returns [] after the quiescence window elapses with no records."""

    from orca.output_reader import OutputReader

    speech_path = tmp_path / "s.jsonl"
    braille_path = tmp_path / "b.jsonl"
    speech_path.touch()
    braille_path.touch()

    reader = OutputReader(str(speech_path), str(braille_path))
    reader.start()
    try:
        assert reader.drain(quiescence_timeout=0.15) == []
    finally:
        reader.stop()


def test_reader_ignores_malformed_and_unknown_kinds(tmp_path: Path) -> None:
    """Non-JSON lines and lines with unknown 'kind' are silently dropped."""

    from orca.output_reader import OutputReader, speech

    speech_path = tmp_path / "s.jsonl"
    braille_path = tmp_path / "b.jsonl"

    reader = OutputReader(str(speech_path), str(braille_path))
    reader.start()
    try:
        time.sleep(0.1)
        with open(speech_path, "a", encoding="utf-8") as handle:
            handle.write("not-json\n")
            handle.write(json.dumps({"kind": "bogus", "text": "x"}) + "\n")
            handle.write(json.dumps({"kind": "speech", "text": "ok"}) + "\n")

        records = reader.drain(quiescence_timeout=0.3)
    finally:
        reader.stop()

    assert speech(records) == ["ok"]


def test_reader_waits_for_files_that_do_not_yet_exist(tmp_path: Path) -> None:
    """start() before files exist; reader picks them up once they appear."""

    from orca.output_reader import OutputReader, speech

    speech_path = tmp_path / "s.jsonl"
    braille_path = tmp_path / "b.jsonl"

    reader = OutputReader(str(speech_path), str(braille_path))
    reader.start()
    try:
        time.sleep(0.1)
        _write_line(speech_path, {"kind": "speech", "text": "appeared"})
        records = reader.drain(quiescence_timeout=0.3)
    finally:
        reader.stop()

    assert speech(records) == ["appeared"]


def test_parse_speech_handles_missing_text_field() -> None:
    """Missing 'text' defaults to empty string rather than crashing."""

    from orca.output_reader import OutputReader

    record = OutputReader._parse_speech(json.dumps({"kind": "speech"}))
    assert record is not None
    assert record.text == ""
    assert record.language == ""
    assert record.dialect == ""


def test_parse_speech_captures_language_and_dialect() -> None:
    """A speech record carries the synthesizer's language and dialect."""

    from orca.output_reader import OutputReader

    record = OutputReader._parse_speech(
        json.dumps({"kind": "speech", "text": "Italiano", "language": "it", "dialect": ""})
    )
    assert record is not None
    assert record.text == "Italiano"
    assert record.language == "it"
    assert record.dialect == ""


def test_parse_braille_handles_missing_fields() -> None:
    """Missing braille fields default to sensible zero/empty values."""

    from orca.output_reader import OutputReader

    record = OutputReader._parse_braille(json.dumps({"kind": "braille"}))
    assert record is not None
    assert record.cursor_cell == 0
    assert record.full == ""
    assert record.visible == ""


def test_wait_for_speech_returns_matching_record(tmp_path: Path) -> None:
    """wait_for_speech() returns the first SpeechRecord whose text contains substring."""

    from orca.output_reader import OutputReader

    speech_path = tmp_path / "s.jsonl"
    braille_path = tmp_path / "b.jsonl"

    reader = OutputReader(str(speech_path), str(braille_path))
    reader.start()
    try:
        time.sleep(0.1)
        _write_line(speech_path, {"kind": "speech", "text": "ignored"})
        _write_line(speech_path, {"kind": "speech", "text": "hello world"})
        record = reader.wait_for_speech("hello", timeout=2.0)
    finally:
        reader.stop()

    assert record.text == "hello world"


def test_wait_for_braille_returns_matching_record(tmp_path: Path) -> None:
    """wait_for_braille() returns the first BrailleRecord whose full line contains substring."""

    from orca.output_reader import OutputReader

    speech_path = tmp_path / "s.jsonl"
    braille_path = tmp_path / "b.jsonl"

    reader = OutputReader(str(speech_path), str(braille_path))
    reader.start()
    try:
        time.sleep(0.1)
        _write_line(
            braille_path,
            {"kind": "braille", "cursor_cell": 1, "full": "First.", "visible": "First."},
        )
        _write_line(
            braille_path,
            {"kind": "braille", "cursor_cell": 5, "full": "Second.", "visible": "Second."},
        )
        record = reader.wait_for_braille("Second", timeout=2.0)
    finally:
        reader.stop()

    assert record.full == "Second."
    assert record.cursor_cell == 5


def test_wait_for_speech_raises_on_timeout(tmp_path: Path) -> None:
    """wait_for_speech() raises TimeoutError if no matching record arrives in time."""

    import pytest

    from orca.output_reader import OutputReader

    speech_path = tmp_path / "s.jsonl"
    braille_path = tmp_path / "b.jsonl"
    speech_path.touch()
    braille_path.touch()

    reader = OutputReader(str(speech_path), str(braille_path))
    reader.start()
    try:
        with pytest.raises(TimeoutError, match="speech containing 'never'"):
            reader.wait_for_speech("never", timeout=0.2)
    finally:
        reader.stop()


def test_wait_for_speech_does_not_consume_braille(tmp_path: Path) -> None:
    """Braille records seen during wait_for_speech remain available to wait_for_braille."""

    from orca.output_reader import OutputReader

    speech_path = tmp_path / "s.jsonl"
    braille_path = tmp_path / "b.jsonl"

    reader = OutputReader(str(speech_path), str(braille_path))
    reader.start()
    try:
        time.sleep(0.1)
        _write_line(
            braille_path,
            {"kind": "braille", "cursor_cell": 0, "full": "buffered", "visible": "buffered"},
        )
        _write_line(speech_path, {"kind": "speech", "text": "hello"})

        speech_record = reader.wait_for_speech("hello", timeout=2.0)
        braille_record = reader.wait_for_braille("buffered", timeout=2.0)
    finally:
        reader.stop()

    assert speech_record.text == "hello"
    assert braille_record.full == "buffered"


def test_reset_discards_pending_and_queued_records(tmp_path: Path) -> None:
    """reset() drops already-seen records so the next wait sees only new activity."""

    import pytest

    from orca.output_reader import OutputReader

    speech_path = tmp_path / "s.jsonl"
    braille_path = tmp_path / "b.jsonl"

    reader = OutputReader(str(speech_path), str(braille_path))
    reader.start()
    try:
        time.sleep(0.1)
        _write_line(speech_path, {"kind": "speech", "text": "old"})
        time.sleep(0.1)  # give the reader thread time to enqueue "old"
        reader.reset()
        with pytest.raises(TimeoutError):
            reader.wait_for_speech("old", timeout=0.2)
    finally:
        reader.stop()


def test_drain_returns_buffered_records_first(tmp_path: Path) -> None:
    """drain() includes records that wait_for_* previously buffered but did not consume."""

    from orca.output_reader import BrailleRecord, OutputReader

    speech_path = tmp_path / "s.jsonl"
    braille_path = tmp_path / "b.jsonl"

    reader = OutputReader(str(speech_path), str(braille_path))
    reader.start()
    try:
        time.sleep(0.1)
        _write_line(
            braille_path,
            {"kind": "braille", "cursor_cell": 0, "full": "buffered", "visible": "buffered"},
        )
        _write_line(speech_path, {"kind": "speech", "text": "hello"})

        reader.wait_for_speech("hello", timeout=2.0)
        records = reader.drain(quiescence_timeout=0.3)
    finally:
        reader.stop()

    strings = [r.full for r in records if isinstance(r, BrailleRecord)]
    assert "buffered" in strings


def test_drain_drops_records_before_an_interrupt(tmp_path: Path) -> None:
    """drain() drops speech that preceded an interrupt marker, keeping only what follows."""

    from orca.output_reader import OutputReader, speech

    speech_path = tmp_path / "s.jsonl"
    braille_path = tmp_path / "b.jsonl"

    reader = OutputReader(str(speech_path), str(braille_path))
    reader.start()
    try:
        time.sleep(0.1)
        _write_line(speech_path, {"kind": "speech", "text": "superseded"})
        _write_line(speech_path, {"kind": "interrupt"})
        _write_line(speech_path, {"kind": "speech", "text": "detailed"})
        records = reader.drain(quiescence_timeout=0.3)
    finally:
        reader.stop()

    assert speech(records) == ["detailed"]


def test_honor_interrupts_drops_speech_not_braille() -> None:
    """An interrupt drops earlier speech only; braille in the same window survives."""

    from orca.output_reader import (
        BrailleRecord,
        InterruptRecord,
        OutputReader,
        SpeechRecord,
        braille,
        speech,
    )

    kept = OutputReader._honor_interrupts(
        [
            BrailleRecord(cursor_cell=0, full="braille kept", visible="braille kept"),
            SpeechRecord(text="speech dropped"),
            InterruptRecord(),
            SpeechRecord(text="speech kept"),
        ]
    )

    assert speech(kept) == ["speech kept"]
    assert braille(kept) == ["braille kept"]
    assert not any(isinstance(record, InterruptRecord) for record in kept)
