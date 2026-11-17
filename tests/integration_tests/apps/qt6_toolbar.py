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

"""A toolbar with actions and an editable field."""

from . import qt6

APP_TITLE = "OrcaToolbar"


def main():
    """Shows the toolbar and runs the Qt main loop."""

    app = qt6.application(APP_TITLE)
    from PySide6 import QtCore, QtWidgets

    window = QtWidgets.QMainWindow()
    window.setFixedSize(500, 200)
    toolbar = window.addToolBar("Editing")
    actions = [toolbar.addAction(label) for label in ("New", "Open", "Save")]
    for action in actions:
        toolbar.widgetForAction(action).setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
    entry = QtWidgets.QLineEdit()
    entry.setAccessibleName("Search")
    toolbar.addWidget(entry)
    window.setCentralWidget(QtWidgets.QPushButton("After toolbar"))
    qt6.show(window, toolbar.widgetForAction(actions[0]))
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
