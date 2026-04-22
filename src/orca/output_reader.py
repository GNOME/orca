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

"""Reader for the speech and braille JSONL logs written by orca.output_recorder."""

import json
import os
import queue
import threading
import time
from dataclasses import dataclass
from enum import Enum


class Kind(Enum):
    """Record kinds matching the JSON records written by the presenters."""

    SPEECH = "speech"
    BRAILLE = "braille"


@dataclass
class SpeechRecord:
    """A record parsed from the speech log."""

    text: str


@dataclass
class BrailleRecord:
    """A record parsed from the braille log."""

    cursor_cell: int
    string: str


class OutputReader:
    """Reads the JSONL files written by the speech and braille presenters."""

    _POLL_INTERVAL = 0.02

    def __init__(self, speech_path: str, braille_path: str) -> None:
        self._speech_path = speech_path
        self._braille_path = braille_path
        self._queue: queue.Queue = queue.Queue()
        self._stop_event = threading.Event()
        self._threads: list[threading.Thread] = []

    def start(self) -> None:
        """Starts the reader threads."""

        self._stop_event.clear()
        self._threads = [
            threading.Thread(
                target=self._enqueue_records,
                args=(self._speech_path, self._parse_speech),
                name="orca-output-speech-reader",
                daemon=True,
            ),
            threading.Thread(
                target=self._enqueue_records,
                args=(self._braille_path, self._parse_braille),
                name="orca-output-braille-reader",
                daemon=True,
            ),
        ]
        for thread in self._threads:
            thread.start()

    def stop(self, join_timeout: float = 1.0) -> None:
        """Signals readers to stop and joins the threads."""

        self._stop_event.set()
        for thread in self._threads:
            thread.join(timeout=join_timeout)
        self._threads = []

    def drain(
        self,
        quiescence_timeout: float = 0.1,
        overall_timeout: float = 5.0,
    ) -> list[SpeechRecord | BrailleRecord]:
        """Returns records that have arrived, waiting for the stream to go quiet."""

        records: list[SpeechRecord | BrailleRecord] = []
        deadline = time.monotonic() + overall_timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return records
            try:
                record = self._queue.get(timeout=min(quiescence_timeout, remaining))
            except queue.Empty:
                return records
            records.append(record)

    def _enqueue_records(self, path: str, parser) -> None:
        """Reads lines from path as they arrive and enqueues each parsed record."""

        while not os.path.exists(path):
            if self._stop_event.wait(timeout=self._POLL_INTERVAL):
                return

        with open(path, encoding="utf-8") as handle:
            while not self._stop_event.is_set():
                if line := handle.readline():
                    if record := parser(line):
                        self._queue.put(record)
                    continue
                if self._stop_event.wait(timeout=self._POLL_INTERVAL):
                    return

    @staticmethod
    def _parse_speech(line: str) -> SpeechRecord | None:
        """Parses a line from the speech log."""

        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            return None
        if data.get("kind") != Kind.SPEECH.value:
            return None
        return SpeechRecord(text=data.get("text", ""))

    @staticmethod
    def _parse_braille(line: str) -> BrailleRecord | None:
        """Parses a line from the braille log."""

        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            return None
        if data.get("kind") != Kind.BRAILLE.value:
            return None
        return BrailleRecord(
            cursor_cell=int(data.get("cursor_cell", 0)),
            string=data.get("string", ""),
        )


def speech(records: list[SpeechRecord | BrailleRecord]) -> list[str]:
    """Returns the spoken text strings from records."""

    return [r.text for r in records if isinstance(r, SpeechRecord)]


def braille(records: list[SpeechRecord | BrailleRecord]) -> list[str]:
    """Returns the braille display strings from records."""

    return [r.string for r in records if isinstance(r, BrailleRecord)]
