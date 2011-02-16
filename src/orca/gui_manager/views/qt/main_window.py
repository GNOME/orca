# Orca
#
# Copyright 2010 Consorcio Fernando de los Rios.
# Author: J. Ignacio Alvarez <jialvarez@emergya.es>
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

"""A hello world example written in QT."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2010 Consorcio Fernando de los Rios."
__license__   = "LGPL"

try:
    import qt
except ImportError:
    print "Error in the QT libraries import"

class HelloWindow:

    def __init__(self):
        self.app = qt.QApplication(["Orca"])
        self.button = qt.QPushButton("Hello Orca!", None)
        self.button.resize(300, 30);

        self.app.setMainWidget(self.button)
        self.button.show()

    def runExample(self):
        self.app.exec_loop()
