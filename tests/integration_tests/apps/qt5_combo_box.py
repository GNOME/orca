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

"""Editable and non-editable combo boxes with programmatic selection changes."""

from . import qt5

APP_TITLE = "OrcaComboBox"


def main():
    """Shows the combo boxes and runs the Qt main loop."""

    app = qt5.application(APP_TITLE)
    from PyQt5 import QtGui, QtWidgets

    window = QtWidgets.QMainWindow()
    content = QtWidgets.QWidget()
    window.setCentralWidget(content)
    window.setFixedSize(400, 180)
    box = QtWidgets.QVBoxLayout(content)
    start = QtWidgets.QPushButton("Start")
    color = QtWidgets.QComboBox()
    color_label = QtWidgets.QLabel("Color")
    color_label.setBuddy(color)
    color.addItems(["Red", "Green", "Blue"])
    city = QtWidgets.QComboBox()
    city.setAccessibleName("City")
    city.setEditable(True)
    city.addItems(["Madrid", "Paris", "Rome"])
    for widget in (start, color_label, color, city):
        box.addWidget(widget)
    color_key = QtWidgets.QShortcut(QtGui.QKeySequence("F5"), window)
    color_key.activated.connect(lambda: color.setCurrentIndex((color.currentIndex() + 1) % 3))
    city_key = QtWidgets.QShortcut(QtGui.QKeySequence("Shift+F5"), window)
    city_key.activated.connect(lambda: city.setCurrentIndex((city.currentIndex() + 1) % 3))
    qt5.show(window, start)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
