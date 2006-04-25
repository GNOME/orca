# Orca
#
# Copyright 2006 Sun Microsystems Inc.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

"""Displays a GUI for the user to set Orca preferences."""

import os
import sys
import gettext
import gtk
import gtk.glade
import locale

import platform

OS = None

speechSystemsModel = None
speechServersModel = None
voicesModel = None

class GladeWrapper:
    """
    Superclass for glade based applications. Just derive from this
    and your subclass should create methods whose names correspond to
    the signal handlers defined in the glade file. Any other attributes
    in your class will be safely ignored.

    This class will give you the ability to do:
        subclass_instance.GtkWindow.method(...)
        subclass_instance.widget_name...
    """

    def __init__(self, Filename, WindowName):
        # Load glade file.
        self.widgets = gtk.glade.XML(Filename, WindowName, gettext.textdomain())
        self.GtkWindow = getattr(self, WindowName)

        instance_attributes = {}
        for attribute in dir(self.__class__):
            instance_attributes[attribute] = getattr(self, attribute)
        self.widgets.signal_autoconnect(instance_attributes)

    def __getattr__(self, attribute):   # Called when no attribute in __dict__
        widget = self.widgets.get_widget(attribute)
        if widget is None:
            raise AttributeError("Widget [" + attribute + "] not found")
        self.__dict__[attribute] = widget   # Add reference to cache.

        return widget

class orcaSetupGUI(GladeWrapper):

    def _init(self):
        global speechSystemsModel, speechServersModel, voicesModel

        speechSystemsModel = self.initList(self.speechSystems)
        selection = self.speechSystems.get_selection()
        selection.connect("changed", self.systemsSelectionChanged)

        speechServersModel = self.initList(self.speechServers)
        selection = self.speechServers.get_selection()
        selection.connect("changed", self.serversSelectionChanged)

        voicesModel = self.initList(self.voices)
        selection = self.voices.get_selection()
        selection.connect("changed", self.voicesSelectionChanged)

        self.setKeyEchoItems()

    def showGUI(self):
        self.orcaSetupWindow.show()

    def initList(self, list):
        model = gtk.ListStore(str)
        list.set_model(model)
        column = gtk.TreeViewColumn("", gtk.CellRendererText(), text=0)
        list.append_column(column)

        return model

    def setKeyEchoItems(self):
        if self.keyEchoCheckbutton.get_active():
            enable = True
        else:
            enable = False
        self.alphaPunctCheckbutton.set_sensitive(enable)
        self.modifierCheckbutton.set_sensitive(enable)
        self.lockingCheckbutton.set_sensitive(enable)
        self.functionCheckbutton.set_sensitive(enable)
        self.actionCheckbutton.set_sensitive(enable)

    def systemsSelectionChanged(self, selection):
        print "systemsSelectionChanged called."

    def serversSelectionChanged(self, selection):
        print "serversSelectionChanged called."

    def voicesSelectionChanged(self, selection):
        print "voicesSelectionChanged called."

    def brailleSupportChecked(self, widget):
        print "brailleSupportChecked called."

    def brailleMonitorChecked(self, widget):
        print "brailleMonitorChecked called."

    def keyEchoChecked(self, widget):
        print "keyEchoChecked called."

    def printableKeysChecked(self, widget):
        print "printableKeysChecked called."

    def modifierKeysChecked(self, widget):
        print "modifierKeysChecked called."

    def lockingKeysChecked(self, widget):
        print "lockingKeysChecked called."

    def functionKeysChecked(self, widget):
        print "functionKeysChecked called."

    def actionKeysChecked(self, widget):
        print "actionKeysChecked called."

    def echoByWordChecked(self, widget):
        print "echoByWordChecked called."

    def helpButtonClicked(self, widget):
        print "helpButtonClicked called."

    def cancelButtonClicked(self, widget):
        print "cancelButtonClicked called."
        self.orcaSetupWindow.hide()

    def applyButtonClicked(self, widget):
        print "applyButtonClicked called."
        self.orcaSetupWindow.hide()

    def quit(self, *args):
        gtk.main_quit()

    def windowDestroyed(self, widget):
        self.quit()

def showPreferencesUI():
    global OS

    if not OS:
        gladeFile = os.path.join(platform.prefix,
                                 platform.datadirname,
                                 platform.package,
                                 "glade",
                                 "orca-setup.glade")
        OS = orcaSetupGUI(gladeFile, "orcaSetupWindow")
        OS._init()
    else:
        OS.showGUI()

def main():
    locale.setlocale(locale.LC_ALL, '')

    showPreferencesUI()

    gtk.main()
    sys.exit(0)

if __name__ == "__main__":
    main()
