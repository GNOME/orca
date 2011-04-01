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

class Toolkit(object):

    def __init__(self, toolkitName='gtk2'):
        super(Toolkit, self).__init__()
        self._baseToolkit = None
        self._baseToolkitName = toolkitName
        self._getBaseToolkit(toolkitName)

        self.TYPE_BOOLEAN = self._baseToolkit.TYPE_BOOLEAN
        self.TYPE_CHAR    = self._baseToolkit.TYPE_CHAR
        self.TYPE_DOUBLE  = self._baseToolkit.TYPE_DOUBLE
        self.TYPE_FLOAT   = self._baseToolkit.TYPE_FLOAT
        self.TYPE_INT     = self._baseToolkit.TYPE_INT
        self.TYPE_LONG    = self._baseToolkit.TYPE_LONG
        self.TYPE_NONE    = self._baseToolkit.TYPE_NONE
        self.TYPE_STRING  = self._baseToolkit.TYPE_STRING
        self.TYPE_UCHAR   = self._baseToolkit.TYPE_UCHAR
        self.TYPE_UINT    = self._baseToolkit.TYPE_UINT
        self.TYPE_ULONG   = self._baseToolkit.TYPE_ULONG
        self.TYPE_UNICHAR = self._baseToolkit.TYPE_UNICHAR

        self.STOCK_ABOUT       = self._baseToolkit.STOCK_ABOUT
        self.STOCK_APPLY       = self._baseToolkit.STOCK_APPLY
        self.STOCK_CANCEL      = self._baseToolkit.STOCK_CANCEL
        self.STOCK_CLOSE       = self._baseToolkit.STOCK_CLOSE
        self.STOCK_FIND        = self._baseToolkit.STOCK_FIND
        self.STOCK_HELP        = self._baseToolkit.STOCK_HELP
        self.STOCK_NO          = self._baseToolkit.STOCK_NO
        self.STOCK_OK          = self._baseToolkit.STOCK_OK
        self.STOCK_OPEN        = self._baseToolkit.STOCK_OPEN
        self.STOCK_PREFERENCES = self._baseToolkit.STOCK_PREFERENCES
        self.STOCK_QUIT        = self._baseToolkit.STOCK_QUIT
        self.STOCK_SAVE        = self._baseToolkit.STOCK_SAVE
        self.STOCK_SAVE_AS     = self._baseToolkit.STOCK_SAVE_AS
        self.STOCK_YES         = self._baseToolkit.STOCK_YES

    def _getBaseToolkit(self, toolkitName):
        toolkit = 'orca.gui.toolkits.%s.toolkit' % toolkitName
        try:
            module = __import__(toolkit, globals(), locals(), [''])
            self._baseToolkit = module
        except:
            raise Exception('toolkit._getBaseToolkit failure: %s' % toolkit)

    def createHBox(self):
        return self._baseToolkit.HBox()

    def createVBox(self):
        return self._baseToolkit.VBox()

    def createCheckbox(self, label='', state=False):
        return self._baseToolkit.Checkbox(label, state)

    def createEntry(self, text='', isPasswordText=False):
        return self._baseToolkit.Entry(text, isPasswordText)

    def createFrame(self, labelText=''):
        return self._baseToolkit.Frame(labelText)

    def createLabel(self, text=''):
        return self._baseToolkit.Label(text)

    def createMessageDialog(self):
        return self._baseToolkit.MessageDialog()

    def createPushButton(self, label='', stock=None):
        return self._baseToolkit.PushButton(label, stock)

    def createRadioButton(self, label='', firstInGroup=None, state=False):
        return self._baseToolkit.RadioButton(label, firstInGroup, state)

    def createHSlider(self):
        return self._baseToolkit.HSlider()

    def createVSlider(self):
        return self._baseToolkit.VSlider()

    def createSpinner(self):
        return self._baseToolkit.Spinner()

    def createStatusBar(self, numberOfAreas=1):
        return self._baseToolkit.StatusBar(numberOfAreas)

    def createTabbedWidget(self):
        return self._baseToolkit.TabbedWidget()

    def createTable(self, nRows=1, nColumns=1):
        return self._baseToolkit.Table(nRows, nColumns)

    def createTextComboBox(self, isEditable=False):
        return self._baseToolkit.TextComboBox(isEditable)

    def createTree(self, *args):
        return self._baseToolkit.Tree(*args)

    def createTreeModel(self, *args):
        return self._baseToolkit.TreeModel(*args)

    def createWindow(self, title=''):
        return self._baseToolkit.Window(title)

    def main(self):
        self._baseToolkit.main()

    def timeoutAdd(self, time, function):
        self._baseToolkit.timeoutAdd(time, function)
