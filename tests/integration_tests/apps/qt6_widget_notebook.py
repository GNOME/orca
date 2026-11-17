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

"""A notebook with common controls, menus, lists, and labels."""

from . import qt6

APP_TITLE = "OrcaWidgetNotebook"


def main():
    """Shows the controls and runs the Qt main loop."""

    app = qt6.application(APP_TITLE)
    from PySide6 import QtCore, QtGui, QtWidgets

    window = QtWidgets.QMainWindow()
    window.setFixedSize(500, 600)
    menu = window.menuBar().addMenu("&File")
    menu.addAction("&New")
    menu.addAction("&Open")
    recent = menu.addMenu("&Recent")
    recent.addAction("&Report")
    recent.addAction("&Summary")
    menu.addAction("&Quit")
    tabs = QtWidgets.QTabWidget()
    window.setCentralWidget(tabs)
    widgets = QtWidgets.QWidget()
    box = QtWidgets.QVBoxLayout(widgets)
    save = QtWidgets.QPushButton("Save")
    bold = QtWidgets.QPushButton("Bold")
    bold.setCheckable(True)
    enabled = QtWidgets.QCheckBox("Enabled")
    quantity = QtWidgets.QSpinBox()
    quantity.setRange(0, 100)
    quantity.setAccessibleName("Quantity")
    color = QtWidgets.QComboBox()
    color_label = QtWidgets.QLabel("Color")
    color_label.setBuddy(color)
    color.addItems(["Red", "Green", "Blue"])
    city = QtWidgets.QLineEdit("Madrid")
    city.setAccessibleName("City")
    radios = [QtWidgets.QRadioButton(label) for label in ("Small", "Medium", "Large")]
    level = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
    level.setAccessibleName("Level")
    level.setRange(0, 10)
    bump = QtWidgets.QPushButton("Bump Quantity in 1000 ms")
    bump.clicked.connect(lambda: QtCore.QTimer.singleShot(1000, quantity.stepUp))
    readonly = QtWidgets.QSpinBox()
    readonly.setAccessibleName("Readonly")
    readonly.setValue(25)
    readonly.setReadOnly(True)
    mixed = QtWidgets.QCheckBox("Include archived")
    mixed.setTristate(True)
    for control in (
        save,
        bold,
        enabled,
        quantity,
        color_label,
        color,
        city,
        *radios,
        level,
        bump,
        readonly,
        mixed,
    ):
        box.addWidget(control)
    tabs.addTab(widgets, "Widgets")

    messages = QtWidgets.QWidget()
    box = QtWidgets.QVBoxLayout(messages)
    entry = QtWidgets.QLineEdit()
    entry.setAccessibleName("Filter")
    entry.setAccessibleDescription("3 matches found")
    box.addWidget(entry)
    options = QtWidgets.QGroupBox("Options")
    options.setAccessibleDescription("Review before saving")
    options_box = QtWidgets.QVBoxLayout(options)
    options_box.addWidget(QtWidgets.QCheckBox("Agree"))
    box.addWidget(options)
    tabs.addTab(messages, "Messages")

    labels = QtWidgets.QWidget()
    box = QtWidgets.QVBoxLayout(labels)
    box.addWidget(QtWidgets.QLabel("Disk almost full"))
    label = QtWidgets.QLabel("&Volume")
    volume = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
    volume.setRange(0, 10)
    label.setBuddy(volume)
    box.addWidget(label)
    box.addWidget(volume)
    tabs.addTab(labels, "Labels")

    files = QtWidgets.QListWidget()
    files.addItems(["report.pdf shared", "notes.txt private", "Budget 2 MB"])
    tabs.addTab(files, "Files")

    available = QtWidgets.QListWidget()
    available.addItems(["Unavailable first", "Available", "Unavailable last"])
    for index in (0, 2):
        item = available.item(index)
        item.setFlags(item.flags() & ~QtCore.Qt.ItemFlag.ItemIsEnabled)
    tabs.addTab(available, "Availability")
    window.statusBar().showMessage("Ready. 3 items.")

    def reset():
        tabs.setCurrentIndex(0)
        bold.setChecked(False)
        enabled.setChecked(False)
        quantity.setValue(75)
        color.setCurrentIndex(0)
        city.setText("Madrid")
        radios[0].setChecked(True)
        level.setValue(3)
        mixed.setCheckState(QtCore.Qt.CheckState.Unchecked)
        save.setFocus()

    reset_key = QtGui.QShortcut(QtGui.QKeySequence("F12"), window)
    reset_key.activated.connect(reset)
    qt6.show(window, save)
    reset()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
