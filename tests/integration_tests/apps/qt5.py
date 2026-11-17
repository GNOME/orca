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

"""Application setup for Qt5 widget fixtures."""

import os
import sys


def application(title):
    """Creates an accessible Qt application with a consistent style and font."""

    os.environ["QT_QPA_PLATFORM"] = "xcb"
    os.environ["QT_LINUX_ACCESSIBILITY_ALWAYS_ON"] = "1"
    os.environ["QT_STYLE_OVERRIDE"] = "Fusion"
    from PyQt5 import QtGui, QtWidgets

    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName(title)
    app.setFont(QtGui.QFont("DejaVu Sans", 10))
    return app


def show(window, focus):
    """Shows the fixture window and focuses its first control."""

    from PyQt5 import QtCore, QtWidgets

    if not window.windowTitle():
        window.setWindowTitle(QtWidgets.QApplication.applicationName())
    window.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
    window.show()
    window.activateWindow()
    focus.setFocus()
