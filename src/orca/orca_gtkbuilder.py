# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
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

"""Displays a GUI for the user to quit Orca."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import gettext
import gtk

class GtkBuilderWrapper:
    """
    Superclass for GtkBuilder based applications. Just derive from this
    and your subclass should create methods whose names correspond to
    the signal handlers defined in the GtkBuilder file. Any other attributes
    in your class will be safely ignored.

    This class will give you the ability to do:
        subclass_instance.GtkWindow.method(...)
        subclass_instance.widget_name...
    """

    def __init__(self, fileName, windowName):
        # Load GtkBuilder file.
        self.builder = gtk.Builder()
        self.builder.set_translation_domain(gettext.textdomain())
        self.builder.add_from_file(fileName)
        self.gtkWindow = getattr(self, windowName)

        # Set default application icon.
        self.set_orca_icon()

        instance_attributes = {}
        for attribute in dir(self.__class__):
            instance_attributes[attribute] = getattr(self, attribute)
        self.builder.connect_signals(instance_attributes)

    def set_orca_icon(self):
        """Get the icon in all sizes from the current theme and set them as
        default for all application windows.
        """

        icon_theme = gtk.icon_theme_get_default()
        try:
            icon16 = icon_theme.load_icon("orca", 16, 0)
            icon22 = icon_theme.load_icon("orca", 22, 0)
            icon24 = icon_theme.load_icon("orca", 24, 0)
            icon32 = icon_theme.load_icon("orca", 32, 0)
            icon48 = icon_theme.load_icon("orca", 48, 0)
        except:
            return
        else:
            gtk.window_set_default_icon_list(icon16,
                                             icon22,
                                             icon24,
                                             icon32,
                                             icon48)

    def get_widget(self, attribute):
        """Return the requested widget. This routine has been introduced
        (and calls to it made by the Orca GtkBuilder sub-classes), to prevent
        "No class attribute" pychecker errors caused when using __getattr__.

        Arguments:
        - attribute: name of the widget to return.
        """

        widget = self.builder.get_object(attribute)
        if widget is None:
            raise AttributeError("Widget [" + attribute + "] not found")

        return widget

    def __getattr__(self, attribute):   # Called when no attribute in __dict__
        widget = self.builder.get_object(attribute)
        if widget is None:
            raise AttributeError("Widget [" + attribute + "] not found")
        self.__dict__[attribute] = widget   # Add reference to cache.

        return widget
