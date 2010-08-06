# Orca
#
# Copyright 2005-2010 Sun Microsystems Inc.
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
# Free Software Foundation, Inc., Franklin Street, Fifth Floor,
# Boston MA  02110-1301 USA.

"""Displays a GUI for the Orca main window."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import os
import sys
import gtk
import locale

import orca
import orca_gtkbuilder
import orca_platform

from orca_i18n import _           # for gettext support

OS = None

class OrcaMainGUI(orca_gtkbuilder.GtkBuilderWrapper):

    def __init__(self, fileName, windowName):
        orca_gtkbuilder.GtkBuilderWrapper.__init__(self, fileName, windowName)
        self.aboutDialog = None

    def init(self):
        pass

    def showGUI(self):
        """Show the Orca main window GUI. This assumes that the GUI has 
        already been created.
        """

        mainWindow = self.get_widget("mainWindow")

        accelGroup = gtk.AccelGroup()
        mainWindow.add_accel_group(accelGroup)
        helpButton = self.get_widget("helpButton")
        (keyVal, modifierMask) = gtk.accelerator_parse("F1")
        helpButton.add_accelerator("clicked",
                                   accelGroup,
                                   keyVal,
                                   modifierMask,
                                   0)

        mainWindow.show()

    def hideGUI(self):
        """Hide the Orca main window GUI. This assumes that the GUI has
        already been created.
        """

        self.get_widget("mainWindow").hide()

    def aboutButtonClicked(self, widget):
        """Signal handler for the "clicked" signal for the aboutButton
        GtkButton widget. The user has clicked the About button.
        Call the method to bring up the About dialog.

        Arguments:
        - widget: the component that generated the signal.
        """

        if self.aboutDialog:
            return

        authors = ["Marc Mulcahy",
                   "Willie Walker <william.walker@sun.com>",
                   "Mike Pedersen <michael.pedersen@sun.com>",
                   "Rich Burridge <rich.burridge@sun.com>",
                   "Joanmarie Diggs <joanmarie.diggs@gmail.com>"]
        # Translators: This is used in the Orca About dialog.
        #
        documenters = [_("The Orca Team")]
        # Translators: This text is used in the Orca About dialog.
        #
        comments = _("A free, open source scriptable screen reader, which " \
                     "provides access to applications and toolkits that " \
                     "support AT-SPI (e.g., the GNOME desktop).")
        # Translators: This text is used in the Orca About dialog.
        #
        copyrights = _("Copyright (c) 2005-2010 Sun Microsystems Inc. \n" \
                       "Copyright (c) 2005-2008 Google Inc. \n" \
                       "Copyright (c) 2008, 2009 Eitan Isaacson \n" \
                       "Copyright (c) 2006-2009 Brailcom, o.p.s. \n" \
                       "Copyright (c) 2001, 2002 BAUM Retec, A.G.")
        # Translators: This text is used in the Orca About dialog. Please
        # translate it to contain your name. And thank you for your work!
        #
        translatorCredits = _("translator-credits")
        # Translators: This text is used in the Orca About dialog. Orca is
        # licensed under GPL2+.
        #
        licenseText = \
            _("Orca is free software; you can redistribute it and/or\n" \
              "modify it under the terms of the GNU Library General\n" \
              "Public License as published by the Free Software Foundation;\n" \
              "either version 2 of the License, or (at your option) any\n" \
              "later version.\n" \
              "\n" \
              "Orca is distributed in the hope that it will be useful, but\n" \
              "WITHOUT ANY WARRANTY; without even the implied warranty of\n" \
              "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See\n" \
              "the GNU Library General Public License for more details.\n" \
              "\n" \
              "You should have received a copy of the GNU Library General\n" \
              "Public License along with Orca; if not, write to the\n" \
              "Free Software Foundation, Inc., Franklin Street, Fifth Floor," \
              "\nBoston MA  02110-1301 USA.")
        url = "http://live.gnome.org/Orca"

        self.aboutDialog = gtk.AboutDialog()
        self.aboutDialog.set_authors(authors)
        self.aboutDialog.set_documenters(documenters)
        self.aboutDialog.set_translator_credits(translatorCredits)
        self.aboutDialog.set_comments(comments)
        self.aboutDialog.set_copyright(copyrights)
        self.aboutDialog.set_license(licenseText)
        self.aboutDialog.set_logo_icon_name('orca')
        self.aboutDialog.set_name(_('Orca'))
        self.aboutDialog.set_version(orca_platform.version)
        self.aboutDialog.set_website(url)
        self.aboutDialog.connect('response', self.aboutDialogOnResponse)
        self.aboutDialog.show()

    def aboutDialogOnResponse(self, dialog, responseID):
        """Signal handler for the About Dialog's "response" signal."""

        dialog.destroy()
        self.aboutDialog = None

    def helpButtonClicked(self, widget):
        """Signal handler for the "clicked" signal for the helpButton
           GtkButton widget. The user has clicked the Help button.
           Call the method to bring up the Orca help window.

        Arguments:
        - widget: the component that generated the signal.
        """

        orca.helpForOrca()

    def quitButtonClicked(self, widget):
        """Signal handler for the "clicked" signal for the quitButton
           GtkButton widget. The user has clicked the Quit button.
           Call the method to bring up the Quit dialog.

        Arguments:
        - widget: the component that generated the signal.
        """

        orca.quitOrca()

    def preferencesButtonClicked(self, widget):
        """Signal handler for the "clicked" signal for the preferencesButton
           GtkButton widget. The user has clicked the Preferences button.
           Call the method to bring up the Preferences dialog.

        Arguments:
        - widget: the component that generated the signal.
        """

        orca.showPreferencesGUI()

    def mainWindowDestroyed(self, widget):
        """Signal handler for the "destroyed" signal for the mainWindow
           GtkWindow widget. Reset OS to None, then call the method to 
           bring up the quit dialog.

        Arguments:
        - widget: the component that generated the signal.
        """

        global OS

        OS = None
        orca.quitOrca()

def showMainUI():
    global OS

    if not OS:
        uiFile = os.path.join(orca_platform.prefix,
                              orca_platform.datadirname,
                              orca_platform.package,
                              "ui",
                              "orca-mainwin.ui")
        OS = OrcaMainGUI(uiFile, "mainWindow")
        OS.init()

    OS.showGUI()

def hideMainUI():
    if OS:
        OS.hideGUI()

def main():
    locale.setlocale(locale.LC_ALL, '')

    showMainUI()

    gtk.main()
    sys.exit(0)

if __name__ == "__main__":
    main()
