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

"""A no-audio speech server used by integration tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

from orca import speechserver

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

    from orca.acss import ACSS


class SpeechServer(speechserver.SpeechServer):
    """A speech server that produces no audio, for integration tests."""

    @staticmethod
    def get_factory_name() -> str:
        """Returns a name describing this factory."""

        return "Test (no audio)"

    def __init__(self, server_id: str = speechserver.SpeechServer.DEFAULT_SERVER_ID) -> None:
        super().__init__(server_id)
        speechserver.SpeechServer._active_servers[server_id] = self

    def say_all(
        self,
        utterance_iterator: Iterator[tuple[speechserver.SayAllContext, ACSS]],
        progress_callback: Callable[[speechserver.SayAllContext, int], None],
    ) -> None:
        """Drains the iterator synchronously so every intended utterance is recorded."""

        for _context, _voice in utterance_iterator:
            pass
