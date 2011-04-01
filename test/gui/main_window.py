#!/usr/bin/python

import sys

import orca.orca as orca
from orca.gui.toolkit import Toolkit
from orca.orca_i18n import _

def onClicked(widget, function=None):
    print "'%s' clicked" % widget.getDisplayedText()
    if function:
        function()

def onWindowCloseEvent(widget, event):
    print "Close event for window: %s" % widget.getTitle()
    widget.destroy()
    quit()

def runTest(toolkitName):
    toolkit = Toolkit(toolkitName)

    window = toolkit.createWindow(_("Orca Screen Reader / Magnifier"))
    window.bind(window.SIGNAL_CLOSE_EVENT, onWindowCloseEvent)
    window.setDefaultSize(300, 40)
    window.setResizable(False)

    table = toolkit.createTable(1, 5)
    table.setContentsMargins(0, 0, 0, 0)
    window.add(table)

    button = toolkit.createPushButton(stock=toolkit.STOCK_PREFERENCES)
    button.bind(button.SIGNAL_CLICKED, onClicked)
    table.add(button, 0, 1)
    table.setPadding(button, 5, 5)
    table.setOptions(button, 0, 0)

    button = toolkit.createPushButton(stock=toolkit.STOCK_QUIT)
    button.bind(button.SIGNAL_CLICKED, onClicked)
    table.add(button, 0, 2)
    table.setPadding(button, 0, 5)
    table.setOptions(button, 0, 0)

    spacer = toolkit.createLabel()
    table.add(spacer, 0, 3)
    table.setPadding(spacer, 5, 0)
    table.setOptions(spacer, 1, 0)

    button = toolkit.createPushButton(stock=toolkit.STOCK_ABOUT)
    button.bind(button.SIGNAL_CLICKED, onClicked)
    table.add(button, 0, 4)
    table.setPadding(button, 0, 5)
    table.setOptions(button, 0, 0)

    # At the moment, this button is the only one connected to a handler
    # that actually does something other than print the signal.
    button = toolkit.createPushButton(stock=toolkit.STOCK_HELP)
    button.bind(button.SIGNAL_CLICKED, onClicked, orca.helpForOrca)
    table.add(button, 0, 5)
    table.setPadding(button, 5, 5)
    table.setOptions(button, 0, 0)

    window.display()
    toolkit.main()

def main():
    try:
       toolkit = sys.argv[1]
    except IndexError:
        toolkit = 'gtk2'

    runTest(toolkit)

    return 0

if __name__ == "__main__":
    sys.exit(main())
