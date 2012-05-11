# Orca
#
# Copyright 2005-2010 Sun Microsystems Inc.
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

"""Displays a GUI for the Orca main window."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import locale
import sys
from gi.repository import Gtk

from . import orca
from . import orca_platform
from . import orca_state

from .orca_i18n import _

OS = None

class OrcaMainGUI(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self)
        self.set_title(_('Orca Screen Reader'))
        self.set_has_resize_grip(False)

        grid = Gtk.Grid()
        grid.set_border_width(5)
        self.add(grid)

        preferencesButton = Gtk.Button.new_from_stock('gtk-preferences')
        preferencesButton.connect('clicked', orca.showPreferencesGUI)
        grid.attach(preferencesButton, 0, 0, 1, 1)

        quitButton = Gtk.Button.new_from_stock('gtk-quit')
        quitButton.connect('clicked', orca.quitOrca)
        grid.attach(quitButton, 1, 0, 1, 1)

        self.aboutDialog = None
        aboutButton = Gtk.Button.new_from_stock('gtk-about')
        aboutButton.connect('clicked', self.aboutButtonClicked)
        grid.attach(aboutButton, 2, 0, 1, 1)

        helpButton = Gtk.Button.new_from_stock('gtk-help')
        helpButton.connect('clicked', orca.helpForOrca)
        grid.attach(helpButton, 3, 0, 1, 1)

        accelGroup = Gtk.AccelGroup()
        (keyVal, modMask) = Gtk.accelerator_parse('F1')
        helpButton.add_accelerator('clicked', accelGroup, keyVal, modMask, 0)
        self.add_accel_group(accelGroup)

        self.connect('destroy', self.onDestroy)

    def init(self):
        pass

    def showGUI(self):
        """Show the Orca main window GUI."""

        self.show_all()
        ts = orca_state.lastInputEventTimestamp
        if ts == 0:
            ts = Gtk.get_current_event_time()
        self.present_with_time(ts)

    def hideGUI(self):
        """Hide the Orca main window GUI."""

        self.hide()

    def aboutButtonClicked(self, widget):
        """Handler for the 'clicked' signal of the aboutButton GtkButton."""

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
        copyrights = _("Copyright (c) 2010-2011 The Orca Team \n" \
                       "Copyright (c) 2010-2011 Igalia, S.L. \n" \
                       "Copyright (c) 2010 Consorcio Fernando de los Rios \n" \
                       "Copyright (c) 2010 Informal Informatica LTDA. \n" \
                       "Copyright (c) 2005-2010 Sun Microsystems Inc. \n" \
                       "Copyright (c) 2005-2008 Google Inc. \n" \
                       "Copyright (c) 2008, 2009 Eitan Isaacson \n" \
                       "Copyright (c) 2006-2009 Brailcom, o.p.s. \n" \
                       "Copyright (c) 2001, 2002 BAUM Retec, A.G.")
        # Translators: This text is used in the Orca About dialog. Please
        # translate it to contain your name. And thank you for your work!
        #
        translatorCredits = _("translator-credits")
        # Translators: This text is used in the Orca About dialog. Orca is
        # licensed under LGPL2.1+.
        #
        licenseText = \
            _("Orca is free software; you can redistribute it and/or\n" \
              "modify it under the terms of the GNU Lesser General\n" \
              "Public License as published by the Free Software Foundation;\n" \
              "either version 2.1 of the License, or (at your option) any\n" \
              "later version.\n" \
              "\n" \
              "Orca is distributed in the hope that it will be useful, but\n" \
              "WITHOUT ANY WARRANTY; without even the implied warranty of\n" \
              "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See\n" \
              "the GNU Lesser General Public License for more details.\n" \
              "\n" \
              "You should have received a copy of the GNU Lesser General\n" \
              "Public License along with Orca; if not, write to the\n" \
              "Free Software Foundation, Inc., Franklin Street, Fifth Floor," \
              "\nBoston MA  02110-1301 USA.")
        url = "http://live.gnome.org/Orca"

        self.aboutDialog = Gtk.AboutDialog()
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
        """Signal handler for the About Dialog's 'response' signal."""

        dialog.destroy()
        self.aboutDialog = None

    def onDestroy(self, widget):
        """Signal handler for the 'destroy' signal for this window."""

        global OS

        OS = None
        orca.quitOrca()

def showMainUI():
    global OS

    if not OS:
        OS = OrcaMainGUI()
        OS.init()

    OS.showGUI()

def hideMainUI():
    if OS:
        OS.hideGUI()

def main():
    locale.setlocale(locale.LC_ALL, '')

    showMainUI()

    Gtk.main()
    sys.exit(0)

if __name__ == "__main__":
    main()
