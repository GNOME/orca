# Orca
#
# Copyright 2011 The Orca Team.
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

import gobject
import gtk

from orca.gui import toolkit

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

TYPE_BOOLEAN = "gboolean"
TYPE_CHAR    = "gchar"
TYPE_DOUBLE  = "gdouble"
TYPE_FLOAT   = "gfloat"
TYPE_INT     = "gint"
TYPE_LONG    = "glong"
TYPE_NONE    = "void"
TYPE_STRING  = "gchararray"
TYPE_UCHAR   = "guchar"
TYPE_UINT    = "guint"
TYPE_ULONG   = "gulong"
TYPE_UNICHAR = "guint"

STOCK_ABOUT       = gtk.STOCK_ABOUT
STOCK_APPLY       = gtk.STOCK_APPLY
STOCK_CANCEL      = gtk.STOCK_CANCEL
STOCK_CLOSE       = gtk.STOCK_CLOSE
STOCK_FIND        = gtk.STOCK_FIND
STOCK_HELP        = gtk.STOCK_HELP
STOCK_NO          = gtk.STOCK_NO
STOCK_OK          = gtk.STOCK_OK
STOCK_OPEN        = gtk.STOCK_OPEN
STOCK_PREFERENCES = gtk.STOCK_PREFERENCES
STOCK_QUIT        = gtk.STOCK_QUIT
STOCK_SAVE        = gtk.STOCK_SAVE
STOCK_SAVE_AS     = gtk.STOCK_SAVE_AS
STOCK_YES         = gtk.STOCK_YES

def main():
    return gtk.main()

def timeoutAdd(time, function):
    gobject.timeout_add(time, function)

class Toolkit(toolkit.Toolkit):

    def __init__(self):
        super(Toolkit, self).__init__()
