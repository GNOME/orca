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

"""A wrapping text editor."""

import sys
from pathlib import Path

from . import qt6

APP_TITLE = "OrcaTextView"
FONT_FAMILY = "DejaVu Sans Mono"


def main(*, plain=False):
    """Shows the text and runs the Qt main loop."""

    app = qt6.application(APP_TITLE)
    from PySide6 import QtGui, QtWidgets

    window = QtWidgets.QMainWindow()
    content = QtWidgets.QWidget()
    window.setCentralWidget(content)
    window.setFixedSize(600, 300)
    layout = QtWidgets.QVBoxLayout(content)
    layout.setContentsMargins(0, 0, 0, 0)
    text = QtWidgets.QPlainTextEdit() if plain else QtWidgets.QTextEdit()
    text.setFont(QtGui.QFont(FONT_FAMILY, 12))
    text.setPlainText(Path(sys.argv[1]).read_text(encoding="utf-8"))
    text.moveCursor(QtGui.QTextCursor.MoveOperation.Start)
    layout.addWidget(text)
    qt6.show(window, text)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
