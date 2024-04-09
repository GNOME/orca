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
from orca.ax_object import AXObject
from orca.ax_utilities import AXUtilities
from orca.scripts.toolkits import gtk
from orca.scripts.toolkits import WebKitGTK
from .braille_generator import BrailleGenerator
from .speech_generator import SpeechGenerator
from .script_utilities import Utilities


class Script(WebKitGTK.Script, gtk.Script):

    def get_braille_generator(self):
        """Returns the braille generator for this script."""

        return BrailleGenerator(self)

    def get_speech_generator(self):
        """Returns the speech generator for this script."""

        return SpeechGenerator(self)

    def get_utilities(self):
        """Returns the utilities for this script."""

        return Utilities(self)

    def stopSpeechOnActiveDescendantChanged(self, event):
        return False

    def on_active_descendant_changed(self, event):
        """Callback for object:active-descendant-changed accessibility events."""

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
