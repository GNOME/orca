# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
# Copyright 2013 Igalia, S.L.
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

"""Custom script for Evolution."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc." \
                "Copyright (c) 2013 Igalia, S.L."
__license__   = "LGPL"


from orca import debug
from orca import focus_manager
from orca import settings_manager
from orca.ax_object import AXObject
from orca.ax_utilities import AXUtilities
from orca.scripts.toolkits import gtk
from orca.scripts.toolkits import WebKitGtk
from .braille_generator import BrailleGenerator
from .speech_generator import SpeechGenerator
from .script_utilities import Utilities


class Script(WebKitGtk.Script, gtk.Script):

    def __init__(self, app):
        """Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """

        if settings_manager.get_manager().get_setting('sayAllOnLoad') is None:
            settings_manager.get_manager().set_setting('sayAllOnLoad', False)

        super().__init__(app)
        self.present_if_inactive = False

    def get_braille_generator(self):
        return BrailleGenerator(self)

    def get_speech_generator(self):
        return SpeechGenerator(self)

    def get_utilities(self):
        return Utilities(self)

    def is_activatable_event(self, event):
        """Returns True if event should cause this script to become active."""

        if event.type.startswith("focus:") and AXUtilities.is_menu(event.source):
            return True

        window = self.utilities.topLevelObject(event.source)
        if not AXUtilities.is_active(window):
            return False

        return True

    def stopSpeechOnActiveDescendantChanged(self, event):
        """Whether or not speech should be stopped prior to setting the
        locusOfFocus in on_active_descendant_changed.

        Arguments:
        - event: the Event

        Returns True if speech should be stopped; False otherwise.
        """

        return False

    ########################################################################
    #                                                                      #
    # AT-SPI OBJECT EVENT HANDLERS                                         #
    #                                                                      #
    ########################################################################

    def on_active_descendant_changed(self, event):
        """Callback for object:active-descendant-changed accessibility events."""

        if not event.any_data:
            msg = "EVOLUTION: Ignoring event. No any_data."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return

        if self.utilities.isComposeAutocomplete(event.source):
            if AXUtilities.is_selected(event.any_data):
                msg = "EVOLUTION: Source is compose autocomplete with selected child."
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                focus_manager.get_manager().set_locus_of_focus(event, event.any_data)
            else:
                msg = "EVOLUTION: Source is compose autocomplete without selected child."
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                focus_manager.get_manager().set_locus_of_focus(event, event.source)
            return

        focus = focus_manager.get_manager().get_locus_of_focus()
        if AXUtilities.is_table_cell(focus):
            table = AXObject.find_ancestor(focus, AXUtilities.is_tree_or_tree_table)
            if table is not None and table != event.source:
                msg = "EVOLUTION: Event is from a different tree or tree table."
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                return

        child = AXObject.get_active_descendant_checked(event.source, event.any_data)
        if child is not None and child != event.any_data:
            tokens = ["EVOLUTION: Bogus any_data suspected. Setting focus to", child]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            focus_manager.get_manager().set_locus_of_focus(event, child)
            return

        msg = "EVOLUTION: Passing event to super class for processing."
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        super().on_active_descendant_changed(event)

    def on_busy_changed(self, event):
        """Callback for object:state-changed:busy accessibility events."""
        pass

    def on_focus(self, event):
        """Callback for focus: accessibility events."""

        if self.utilities.isWebKitGtk(event.source):
            return

        # This is some mystery child of the 'Messages' panel which fails to show
        # up in the hierarchy or emit object:state-changed:focused events.
        if AXUtilities.is_layered_pane(event.source):
            obj = self.utilities.realActiveDescendant(event.source)
            focus_manager.get_manager().set_locus_of_focus(event, obj)
            return

        gtk.Script.on_focus(self, event)

    def on_name_changed(self, event):
        """Callback for object:property-change:accessible-name events."""

        if self.utilities.isWebKitGtk(event.source):
            return

        gtk.Script.on_name_changed(self, event)

    def on_selection_changed(self, event):
        """Callback for object:selection-changed accessibility events."""

        if AXUtilities.is_combo_box(event.source) \
           and not AXUtilities.is_focused(event.source):
            return

        gtk.Script.on_selection_changed(self, event)
