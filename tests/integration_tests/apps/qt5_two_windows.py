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

"""Two windows for testing focus and flat review."""

from . import qt5

APP_TITLE = "OrcaTwoWindows"


def main():
    """Shows the first window and runs the Qt main loop."""

    app = qt5.application(APP_TITLE)
    from PyQt5 import QtCore, QtGui, QtWidgets

    first = QtWidgets.QMainWindow()
    first_content = QtWidgets.QWidget()
    first.setCentralWidget(first_content)
    first.setWindowTitle("First")
    first.setFixedSize(400, 180)
    text = QtWidgets.QTextEdit("First line.\nSecond line.\nThird line.")
    QtWidgets.QVBoxLayout(first_content).addWidget(text)
    second = QtWidgets.QMainWindow()
    second_content = QtWidgets.QWidget()
    second.setCentralWidget(second_content)
    second.setWindowTitle("Second")
    second.setFixedSize(400, 120)
    entry = QtWidgets.QLineEdit("Second window entry")
    QtWidgets.QVBoxLayout(second_content).addWidget(entry)
    shortcuts = []
    for window in (first, second):
        window.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
        for key, target, focus in (("F2", second, entry), ("F3", first, text)):
            shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(key), window)
            shortcut.activated.connect(lambda target=target, focus=focus: qt5.show(target, focus))
            shortcuts.append(shortcut)
    qt5.show(first, text)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
