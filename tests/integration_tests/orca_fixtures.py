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

"""Session-scoped fixture that owns an Orca subprocess for integration tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .harness import sandbox
from .harness.orca_session import OrcaSession

if TYPE_CHECKING:
    from collections.abc import Iterator


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
