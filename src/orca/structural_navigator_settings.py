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

"""Settings keys for structural navigation."""

from __future__ import annotations


class StructuralNavigationSettings:
    """The structural navigation settings keys."""

    KEY_ENABLED = "enabled"
    KEY_LARGE_OBJECT_TEXT_LENGTH = "large-object-text-length"
    KEY_SKIP_UNLABELED_IMAGES = "skip-unlabeled-images"
    KEY_TRIGGERS_FOCUS_MODE = "triggers-focus-mode"
    KEY_WRAPS = "wraps"
