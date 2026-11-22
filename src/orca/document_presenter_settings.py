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

"""Settings keys for documents."""

from __future__ import annotations


class DocumentSettings:
    """The document settings keys."""

    KEY_AUTO_STICKY_FOCUS_MODE = "auto-sticky-focus-mode"
    KEY_FIND_RESULTS_MINIMUM_LENGTH = "find-results-minimum-length"
    KEY_FIND_RESULTS_VERBOSITY = "find-results-verbosity"
    KEY_NATIVE_NAV_TRIGGERS_FOCUS_MODE = "native-nav-triggers-focus-mode"
    KEY_PAGE_SUMMARY_ON_LOAD = "page-summary-on-load"
    KEY_SAY_ALL_ON_LOAD = "say-all-on-load"
