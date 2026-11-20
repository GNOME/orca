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

"""Lists and tables for keyboard navigation and selection."""

from . import qt6

APP_TITLE = "OrcaItemViews"


def main():
    """Shows the item views and runs the Qt main loop."""

    app = qt6.application(APP_TITLE)
    from PySide6 import QtCore, QtGui, QtWidgets

    window = QtWidgets.QMainWindow()
    content = QtWidgets.QWidget()
    window.setCentralWidget(content)
    window.setFixedSize(600, 500)
    box = QtWidgets.QVBoxLayout(content)
    toppings = QtWidgets.QListWidget()
    toppings.setAccessibleName("Toppings")
    toppings.addItems(["Cheese", "Olives", "Mushrooms", "Onions"])
    toppings.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
    box.addWidget(toppings)
    table = QtWidgets.QTableWidget(3, 4)
    table.setAccessibleName("People")
    table.setHorizontalHeaderLabels(["Name", "Role", "Office", "Done"])
    table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
    table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
    table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
    for row, values in enumerate(
        (
            ("Ada", "Engineer", "London"),
            ("Grace", "Admiral", "Boston"),
            ("Alan", "Analyst", "Manchester"),
        )
    ):
        for col, text in enumerate(values):
            table.setItem(row, col, QtWidgets.QTableWidgetItem(text))
        done = QtWidgets.QTableWidgetItem()
        done.setCheckState(
            QtCore.Qt.CheckState.Checked if row == 1 else QtCore.Qt.CheckState.Unchecked
        )
        table.setItem(row, 3, done)
    table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
    box.addWidget(table)
    for names in (("Readme.txt",), ("Readme.txt", "Notes.txt")):
        downloads = QtWidgets.QTreeView()
        downloads.setAccessibleName("Downloads")
        downloads.setRootIsDecorated(False)
        downloads.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        model = QtGui.QStandardItemModel(downloads)
        model.setHorizontalHeaderLabels(["Name", "Status"])
        for name in names:
            model.appendRow([QtGui.QStandardItem(name), QtGui.QStandardItem("Complete")])
        downloads.setModel(model)
        box.addWidget(downloads)
    tree = QtWidgets.QTreeWidget()
    tree.setHeaderLabel("Projects")
    for name, children in (("Work", ("Report", "Notes")), ("Home", ("Garden", "Kitchen"))):
        parent = QtWidgets.QTreeWidgetItem(tree, [name])
        for child in children:
            QtWidgets.QTreeWidgetItem(parent, [child])
    box.addWidget(tree)
    box.addWidget(QtWidgets.QPushButton("After"))

    def reset():
        toppings.clearSelection()
        toppings.setCurrentRow(0)
        table.clearSelection()
        table.setCurrentCell(0, 0)
        tree.collapseAll()
        tree.setCurrentItem(tree.topLevelItem(0))
        tree.topLevelItem(1).setCheckState(0, QtCore.Qt.CheckState.Checked)
        toppings.setFocus()

    shortcut = QtGui.QShortcut(QtGui.QKeySequence("F12"), window)
    shortcut.activated.connect(reset)
    qt6.show(window, toppings)
    reset()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
