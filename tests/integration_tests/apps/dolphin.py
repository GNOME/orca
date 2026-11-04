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

"""Launches Dolphin for integration tests."""

import os
import sys
from pathlib import Path


def main() -> None:
    """Configures the requested view and launches Dolphin."""

    binary, folder, view = sys.argv[1:]
    os.environ["QT_QPA_PLATFORM"] = "xcb"
    os.environ["QT_LINUX_ACCESSIBILITY_ALWAYS_ON"] = "1"
    os.environ["QT_STYLE_OVERRIDE"] = "Fusion"
    config = Path(os.environ["XDG_CONFIG_HOME"])
    (config / "dolphinrc").write_text(
        "[General]\nGlobalViewProps=true\nRememberOpenedTabs=false\nDynamicView=false\n"
        "[IconsMode]\nIconSize=48\nUseSystemFont=false\nViewFont=DejaVu Sans,10\n"
        "[DetailsMode]\nIconSize=16\nUseSystemFont=false\nViewFont=DejaVu Sans,10\n"
        "ExpandableFolders=true\n",
        encoding="utf-8",
    )
    properties = Path(os.environ["XDG_DATA_HOME"]) / "dolphin/view_properties/global"
    properties.mkdir(parents=True)
    mode = 0 if view == "icon" else 1
    (properties / ".directory").write_text(
        f"[Dolphin]\nVersion=4\nViewMode={mode}\nPreviewsShown=false\n"
        "SortRole=text\nSortOrder=0\nSortFoldersFirst=true\nGroupedSorting=false\n"
        "VisibleRoles=Details_text,CustomizedDetails\n"
        "[Settings]\nHiddenFilesShown=false\n",
        encoding="utf-8",
    )
    os.execv(binary, [binary, "--new-window", folder])  # noqa: S606


if __name__ == "__main__":
    main()
