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

from gi.repository import GLib

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
        self._say_all_source = 0

    def say_all(
        self,
        utterance_iterator: Iterator[tuple[speechserver.SayAllContext, ACSS]],
        progress_callback: Callable[[speechserver.SayAllContext, int], None],
    ) -> None:
        """Yields between utterances so browser events arrive while Say All is active."""

        self.stop()

        def advance() -> bool:
            try:
                next(utterance_iterator)
            except StopIteration:
                self._say_all_source = 0
                return GLib.SOURCE_REMOVE
            return GLib.SOURCE_CONTINUE

        self._say_all_source = GLib.idle_add(advance)

    def stop(self) -> None:
        """Cancels pending test speech when presentation is interrupted."""

        if self._say_all_source:
            GLib.source_remove(self._say_all_source)
            self._say_all_source = 0

    def shutdown(self) -> None:
        """Cancels speech when the test switches profiles or closes Orca."""

        self.stop()
