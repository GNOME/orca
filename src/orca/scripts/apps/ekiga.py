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

"""Custom script for Ekiga."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi

import orca.default as default
import orca.orca as orca
import orca.orca_state as orca_state
import orca.speech as speech

########################################################################
#                                                                      #
# The Ekiga script class.                                              #
#                                                                      #
########################################################################

class Script(default.Script):

    def __init__(self, app):
        """Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """

        default.Script.__init__(self, app)

    def onActiveDescendantChanged(self, event):
        """Called when an object who manages its own descendants detects a
        change in one of its children.

        Arguments:
        - event: the Event
        """

        # The tree table on the left side of Ekiga's Preferences dialog
        # has STATE_FOCUSABLE, but not STATE_FOCUSED. The default script
        # will ignore these events as a result. See bug 574221.
        #
        window = self.getTopLevel(event.source)
        if not window or window.getRole() != pyatspi.ROLE_DIALOG:
            return default.Script.onActiveDescendantChanged(self, event)

        # There can be cases when the object that fires an
        # active-descendant-changed event has no children. In this case,
        # use the object that fired the event, otherwise, use the child.
        #
        child = event.any_data
        if child:
            speech.stop()
            orca.setLocusOfFocus(event, child)
        else:
            orca.setLocusOfFocus(event, event.source)

        # We'll tuck away the activeDescendant information for future
        # reference since the AT-SPI gives us little help in finding
        # this.
        #
        if orca_state.locusOfFocus \
           and (orca_state.locusOfFocus != event.source):
            self.pointOfReference['activeDescendantInfo'] = \
                [orca_state.locusOfFocus.parent,
                 orca_state.locusOfFocus.getIndexInParent()]

    def onFocus(self, event):
        """Called whenever an object gets focus.

        Arguments:
        - event: the Event
        """

        # Selecting items in Ekiga's Preferences dialog causes objects
        # of ROLE_PAGE_TAB to issue focus: events. These page tabs are
        # not showing or visible, but they claim to be both. As a result
        # Orca attempts to present them. Because these page tabs lack a
        # name as well as STATE_SENSTIVE, this causes us to present
        # "page grayed." We just want to ignore this creative use of a
        # Gtk+ widget. See bug 574221.
        #
        if event.source.getRole() == pyatspi.ROLE_PAGE_TAB \
           and not event.source.getState().contains(pyatspi.STATE_SENSITIVE) \
           and not event.source.name:
            return

        default.Script.onFocus(self, event)
