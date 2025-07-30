# Orca
#
# Copyright 2004-2008 Sun Microsystems Inc.
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

# pylint: disable=wrong-import-position

"""Custom script for gedit."""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

from typing import TYPE_CHECKING

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from orca import focus_manager
from orca.ax_object import AXObject
from orca.ax_text import AXText
from orca.ax_utilities import AXUtilities
from orca.scripts.toolkits import gtk
from .spellcheck import SpellCheck

if TYPE_CHECKING:
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi


class Script(gtk.Script):
    """Custom script for gedit."""

    # Override the base class type annotation since this script always has spellcheck
    spellcheck: SpellCheck

    def get_spellcheck(self) -> SpellCheck:
        """Returns the spellcheck for this script."""

        return SpellCheck(self)

    def get_app_preferences_gui(self) -> Gtk.Grid:
        """Returns a GtkGrid containing the application unique configuration
        GUI items for the current application."""

        grid = Gtk.Grid()
        grid.set_border_width(12)
        grid.attach(self.spellcheck.get_app_preferences_gui(), 0, 0, 1, 1)
        grid.show_all()

        return grid

    def get_preferences_from_gui(self) -> dict[str, bool]:
        """Returns a dictionary with the app-specific preferences."""

        return self.spellcheck.get_preferences_from_gui()

    def locus_of_focus_changed(
        self,
        event: Atspi.Event | None,
        old_focus: Atspi.Accessible | None,
        new_focus: Atspi.Accessible | None
    ) -> bool:
        """Handles changes of focus of interest. Returns True if this script did all needed work."""

        if self.spellcheck.is_suggestions_item(new_focus):
            include_label = not self.spellcheck.is_suggestions_item(old_focus)
            self.update_braille(new_focus)
            self.spellcheck.present_suggestion_list_item(include_label=include_label)
            return True

        return super().locus_of_focus_changed(event, old_focus, new_focus)

    def on_active_descendant_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:active-descendant-changed accessibility events."""

        if event.source == self.spellcheck.get_suggestions_list():
            return True

        return super().on_active_descendant_changed(event)

    def on_caret_moved(self, event: Atspi.Event) -> bool:
        """Callback for object:text-caret-moved accessibility events."""

        if AXUtilities.is_multi_line(event.source):
            self.spellcheck.set_document_position(event.source, event.detail1)

        return super().on_caret_moved(event)

    def on_name_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:property-change:accessible-name events."""

        if not self.spellcheck.is_active():
            return super().on_name_changed(event)

        name = AXObject.get_name(event.source)
        if name == self.spellcheck.get_misspelled_word():
            self.spellcheck.present_error_details()
            return True

        parent = AXObject.get_parent(event.source)
        if parent != self.spellcheck.get_suggestions_list() or not AXUtilities.is_focused(parent):
            return True

        entry = self.spellcheck.get_change_to_entry()
        if name != AXText.get_all_text(entry):
            return True

        # If we're here, the locusOfFocus was in the selection list when
        # that list got destroyed and repopulated. Focus is still there.
        focus_manager.get_manager().set_locus_of_focus(event, event.source, False)
        self.update_braille(event.source)
        return True

    def on_sensitive_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:sensitive accessibility events."""

        if event.source == self.spellcheck.get_change_to_entry() \
           and self.spellcheck.present_completion_message():
            return True

        return super().on_sensitive_changed(event)

    def on_window_activated(self, event: Atspi.Event) -> bool:
        """Callback for window:activate accessibility events."""

        super().on_window_activated(event)
        if not self.spellcheck.is_spell_check_window(event.source):
            self.spellcheck.deactivate()
            return True

        self.spellcheck.present_error_details()
        entry = self.spellcheck.get_change_to_entry()
        focus_manager.get_manager().set_locus_of_focus(None, entry, False)
        self.update_braille(entry)
        return True

    def on_window_deactivated(self, event: Atspi.Event) -> bool:
        """Callback for window:deactivate accessibility events."""

        super().on_window_deactivated(event)
        self.spellcheck.deactivate()
        return True
