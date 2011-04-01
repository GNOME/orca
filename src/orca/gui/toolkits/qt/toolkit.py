# Orca
#
# Copyright 2011 The Orca Team.
# Author: Alejandro Leiva <aleiva@emergya.es>
# Author: Joanmarie Diggs <joanmarie.diggs@gmail.com>
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

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2011 The Orca Team."
__license__   = "LGPL"

from PyQt4 import QtGui, QtCore

from orca.gui import toolkit

# TODO - Maybe the localization stuff needs to be part of the gui
# toolkit??
from orca.orca_i18n import _

from box import HBox, VBox
from checkbox import Checkbox
from entry import Entry
from frame import Frame
from label import Label
from message_dialog import MessageDialog
from push_button import PushButton
from radio_button import RadioButton
from slider import HSlider, VSlider
from spinner import Spinner
from status_bar import StatusBar
from tabbed_widget import TabbedWidget
from table import Table
from text_combo_box import TextComboBox
from tree import Tree
from tree_model import TreeModel
from window import Window

TYPE_BOOLEAN = QtCore.QVariant
TYPE_CHAR    = QtCore.QVariant
TYPE_DOUBLE  = QtCore.QVariant
TYPE_FLOAT   = QtCore.QVariant
TYPE_INT     = QtCore.QVariant
TYPE_LONG    = QtCore.QVariant
TYPE_NONE    = QtCore.QVariant
TYPE_STRING  = QtCore.QVariant
TYPE_UCHAR   = QtCore.QVariant
TYPE_UINT    = QtCore.QVariant
TYPE_ULONG   = QtCore.QVariant
TYPE_UNICHAR = QtCore.QVariant

STOCK_ABOUT       = (QtGui.QIcon.fromTheme('help-about'), _('_About'))
STOCK_APPLY       = (QtGui.QIcon.fromTheme('apply'), '')
STOCK_CANCEL      = (QtGui.QIcon.fromTheme('cancel'), '')
STOCK_CLOSE       = (QtGui.QIcon.fromTheme('window-close'), '')
STOCK_FIND        = (QtGui.QIcon.fromTheme('edit-find'), '')
STOCK_HELP        = (QtGui.QIcon.fromTheme('help'), _('_Help'))
STOCK_NO          = (QtGui.QIcon.fromTheme('no'), '')
STOCK_OK          = (QtGui.QIcon.fromTheme('ok'), _('_OK'))
STOCK_OPEN        = (QtGui.QIcon.fromTheme('document-open'), '')
STOCK_PREFERENCES = (QtGui.QIcon.fromTheme('preferences-desktop'), _('_Preferences'))
STOCK_QUIT        = (QtGui.QIcon.fromTheme('application-exit'), _('_Quit'))
STOCK_SAVE        = (QtGui.QIcon.fromTheme('document-save'), '')
STOCK_SAVE_AS     = (QtGui.QIcon.fromTheme('document-save-as'), '')
STOCK_YES         = (QtGui.QIcon.fromTheme('yes'), '')

app = QtGui.QApplication([''])

def main():
    return app.exec_()

def timeoutAdd(time, function):
    pass

class Toolkit(toolkit.Toolkit):

    def __init__(self):
        super(Toolkit, self).__init__()
