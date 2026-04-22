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

"""Writes JSONL records to a file so external observers can consume presenter output."""

from __future__ import annotations

import contextlib
import json
from typing import Any, TextIO

from . import debug


class OutputRecorder:
    """Records presenter output as JSONL to an optional file."""

    def __init__(self, label: str) -> None:
        self._label = label
        self._file: TextIO | None = None

    def set_path(self, path: str) -> bool:
        """Opens path for JSONL output; an empty string closes the current file."""

        self.close()
        if not path:
            return True
        try:
            # Line-buffered so observers see each record immediately.
            self._file = open(  # noqa: SIM115 # pylint: disable=consider-using-with
                path, "w", encoding="utf-8", buffering=1
            )
        except OSError as error:
            msg = f"OUTPUT RECORDER ({self._label}): Could not open {path!r}: {error}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return False
        return True

    def record(self, **fields: Any) -> None:
        """Writes one JSONL record with the given fields if a file is open."""

        if self._file is None:
            return
        try:
            json.dump(fields, self._file, ensure_ascii=False)
            self._file.write("\n")
        except (OSError, TypeError, ValueError) as error:
            msg = f"OUTPUT RECORDER ({self._label}): Failed to write record: {error}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)

    def close(self) -> None:
        """Closes the underlying file, if any."""

        if self._file is None:
            return
        with contextlib.suppress(OSError):
            self._file.close()
        self._file = None

    def is_open(self) -> bool:
        """Returns True if a file is currently open for recording."""

        return self._file is not None
