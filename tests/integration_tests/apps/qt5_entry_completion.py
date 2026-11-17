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

"""An entry with city-name completion."""

from . import qt5

APP_TITLE = "OrcaEntryCompletion"


def main():
    """Shows the entry and runs the Qt main loop."""

    app = qt5.application(APP_TITLE)
    from PyQt5 import QtCore, QtWidgets

    window = QtWidgets.QMainWindow()
    content = QtWidgets.QWidget()
    window.setCentralWidget(content)
    window.setFixedSize(400, 240)
    box = QtWidgets.QVBoxLayout(content)
    start = QtWidgets.QPushButton("Start")
    entry = QtWidgets.QLineEdit()
    label = QtWidgets.QLabel("&City")
    label.setBuddy(entry)
    completion = QtWidgets.QCompleter(["London", "Los Angeles", "Lodz", "Paris"], entry)
    completion.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
    entry.setCompleter(completion)
    for widget in (start, label, entry, QtWidgets.QPushButton("After")):
        box.addWidget(widget)
    qt5.show(window, start)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
