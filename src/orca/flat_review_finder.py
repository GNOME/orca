# Orca
#
# Copyright 2006-2008 Sun Microsystems Inc.
# Copyright 2022 Igalia, S.L.
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
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-return-statements

"""Provides support for a flat review find."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2006-2008 Sun Microsystems Inc." \
                "Copyright (c) 2022 Igalia, S.L."
__license__   = "LGPL"


import copy
import re
import time
from typing import Callable

import gi
gi.require_version("Atspi", "2.0")
gi.require_version('Gtk', '3.0')
from gi.repository import Atspi, Gtk

from . import cmdnames
from . import debug
from . import flat_review_presenter
from . import focus_manager
from . import guilabels
from . import input_event
from . import keybindings
from . import messages
from . import script_manager

from .flat_review import Context


class _SearchQueryMatch:
    """Represents a SearchQuery match."""

    def __init__(self, context: Context, pattern: re.Pattern) -> None:
        self._line, self._zone, self._word, self._char = context.get_current_location()
        self._line_string: str = context.get_current_line_string()
        self._pattern: re.Pattern = pattern

    def __str__(self) -> str:
        return (
            f"SEARCH QUERY MATCH: '{self._line_string}' "
            f"(line {self._line}, zone {self._zone}, word {self._word}, char {self._char}) "
            f"for '{self._pattern}'"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, _SearchQueryMatch):
            return False

        return self._line_string == other._line_string and \
               self._line == other._line and \
               self._zone == other._zone and \
               self._word == other._word and \
               self._char == other._char

class SearchQuery:
    """Represents a search that the user wants to perform."""

    def __init__(self) -> None:
        self.search_string: str = ""
        self.search_backwards: bool = False
        self.case_sensitive: bool = False
        self.match_entire_word: bool = False
        self.window_wrap: bool = False
        self.start_at_top: bool = False

    def __str__(self) -> str:
        string = f"'{self.search_string}'."
        options = []
        if self.search_backwards:
            options.append("search backwards")
        if self.case_sensitive:
            options.append("case sensitive")
        if self.match_entire_word:
            options.append("match entire word")
        if self.window_wrap:
            options.append("wrap")
        if self.start_at_top:
            options.append("start at top")
        if options:
            string += f" Options: {', '.join(options)}"
        return string

class FlatReviewFinder:
    """Provides tools to search the current window's flat-review contents."""

    def __init__(self) -> None:
        self._gui: FlatReviewFinderGUI | None = None
        self._handlers: dict = self.get_handlers(True)
        self._desktop_bindings: keybindings.KeyBindings = keybindings.KeyBindings()
        self._laptop_bindings: keybindings.KeyBindings = keybindings.KeyBindings()
        self._last_query: SearchQuery | None = None
        self._location: tuple[int, int, int, int] = 0, 0, 0, 0
        self._wrapped: bool = False
        self._match: _SearchQueryMatch | None = None
        self._focus: Atspi.Accessible | None = None

    def get_bindings(
        self, refresh: bool = False, is_desktop: bool = True
    ) -> keybindings.KeyBindings:
        """Returns the flat-review-presenter keybindings."""

        if refresh:
            msg = "FLAT REVIEW FINDER: Refreshing bindings."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._laptop_bindings.remove_key_grabs("FLAT REVIEW FINDER: Refreshing bindings.")
            self._desktop_bindings.remove_key_grabs("FLAT REVIEW FINDER: Refreshing bindings.")
            self._setup_bindings()
        elif is_desktop and self._desktop_bindings.is_empty():
            self._setup_bindings()
        elif not is_desktop and self._laptop_bindings.is_empty():
            self._setup_bindings()

        if is_desktop:
            return self._desktop_bindings
        return self._laptop_bindings

    def get_handlers(self, refresh: bool = False) -> dict[str, input_event.InputEventHandler]:
        """Returns the flat-review-finder handlers."""

        if refresh:
            msg = "FLAT REVIEW FINDER: Refreshing handlers."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._setup_handlers()

        return self._handlers

    def _setup_bindings(self) -> None:
        """Sets up the flat-review-finder key bindings."""

        self._setup_desktop_bindings()
        self._setup_laptop_bindings()

    def _setup_desktop_bindings(self) -> None:
        """Sets up the flat-review-finder desktop key bindings."""

        self._desktop_bindings = keybindings.KeyBindings()

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Delete",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["findHandler"]))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Delete",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers["findNextHandler"]))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Delete",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_SHIFT_MODIFIER_MASK,
                self._handlers["findPreviousHandler"]))

        msg = "FLAT REVIEW FINDER: Desktop bindings set up."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def _setup_laptop_bindings(self) -> None:
        """Sets up the flat-review-finder laptop key bindings."""

        self._laptop_bindings = keybindings.KeyBindings()

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "bracketleft",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers["findHandler"]))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "bracketright",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers["findNextHandler"]))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "bracketright",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_CTRL_MODIFIER_MASK,
                self._handlers["findPreviousHandler"]))

        msg = "FLAT REVIEW FINDER: Laptop bindings set up."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def _setup_handlers(self) -> None:
        """Sets up the flat-review-presenter input event handlers."""

        self._handlers = {}

        self._handlers["findHandler"] = \
            input_event.InputEventHandler(
                self.show_dialog,
                cmdnames.SHOW_FIND_GUI)

        self._handlers["findNextHandler"] = \
            input_event.InputEventHandler(
                self.find_next,
                cmdnames.FIND_NEXT)

        self._handlers["findPreviousHandler"] = \
            input_event.InputEventHandler(
                self.find_previous,
                cmdnames.FIND_PREVIOUS)


        msg = "FLAT REVIEW FINDER: Handlers set up."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def _on_query(self, query: SearchQuery) -> None:
        """Handler after a query has been made via the Find dialog."""

        self._last_query = query

    def show_dialog(self, script, _event=None) -> bool:
        """Shows the Find dialog."""

        self._focus = focus_manager.get_manager().get_locus_of_focus()
        self._gui = FlatReviewFinderGUI(script, self._on_query)
        self._gui.show_gui(self._focus)
        return True

    def find_next(self, script, event=None) -> bool:
        """Searches forward for the next instance of the string."""

        if self._last_query is None:
            self.show_dialog(script, event)
            return True

        self._last_query.search_backwards = False
        self._last_query.start_at_top = False
        self.find(script, self._last_query)
        return True

    def find_previous(self, script, event=None) -> bool:
        """Searches backwards for the previous instance of the string."""

        if self._last_query is None:
            self.show_dialog(script, event)
            return True

        self._last_query.search_backwards = True
        self._last_query.start_at_top = False
        self.find(script, self._last_query)
        return True

    def find(self, script, query: SearchQuery | None = None) -> None:
        """Searches for the specified query, or the most recent one."""

        query = query or self._last_query
        if query is None:
            return

        presenter = flat_review_presenter.get_presenter()
        context = presenter.get_or_create_context(script)
        location = self._do_find(query, context)
        if not location:
            script.present_message(messages.STRING_NOT_FOUND)
        else:
            context.set_current_location(location.get_current_location())
            presenter.present_item(script)

    def _move(self, query: SearchQuery, context: Context, context_type: int) -> bool:
        """Moves within the flat review context while looking for a match."""

        if context_type == Context.WORD:
            if query.search_backwards:
                return context.go_previous_word()
            return context.go_next_word()

        if context_type == Context.ZONE:
            if query.search_backwards:
                moved = context.go_previous_zone()
                context.go_to_end_of(Context.ZONE)
                return moved
            return context.go_next_zone()

        if context_type == Context.LINE:
            if query.search_backwards:
                moved = context.go_previous_line()
                context.go_to_end_of(Context.LINE)
            else:
                moved = context.go_next_line()
            if moved:
                return True
            if not query.window_wrap or self._wrapped:
                return False
            self._wrapped = True
            script = script_manager.get_manager().get_active_script()
            assert script is not None
            if query.search_backwards:
                script.present_message(messages.WRAPPING_TO_BOTTOM)
                moved = context.go_previous_line(True)
            else:
                script.present_message(messages.WRAPPING_TO_TOP)
                moved = context.go_next_line(True)
            return moved

        return False

    def _find_match_in(
        self, query: SearchQuery, context: Context, pattern: re.Pattern, context_type: int
    ) -> bool:
        """Searches for a match of pattern in context for the given type."""

        def matches(context, pattern, context_type):
            string = ""
            if context_type == Context.LINE:
                type_string = "LINE"
                string = context.get_current_line_string()
            elif context_type == Context.ZONE:
                type_string = "ZONE"
                string = context.get_current_zone_string()
            elif context_type == Context.WORD:
                type_string = "WORD"
                string = context.get_current_word_string()
            else:
                return False

            match = re.search(pattern, string)
            debug_string = string.replace("\n", "\\n")
            msg = f"FLAT REVIEW FINDER: Looking in {type_string}='{debug_string}'. Match: {match}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return bool(match)

        found = matches(context, pattern, context_type)
        while not found:
            if not self._move(query, context, context_type):
                break
            found = matches(context, pattern, context_type)

        return found

    def _find_match(self, query: SearchQuery, context: Context, pattern: re.Pattern) -> bool:
        """Searches for a match of pattern in context."""

        if not self._find_match_in(query, context, pattern, Context.LINE):
            return False

        if not self._find_match_in(query, context, pattern, Context.ZONE):
            return False

        if not self._find_match_in(query, context, pattern, Context.WORD):
            return False

        if self._match != _SearchQueryMatch(context, pattern):
            return True

        if self._move(query, context, Context.WORD) \
           and self._find_match_in(query, context, pattern, Context.WORD):
            return True

        if self._move(query, context, Context.ZONE) \
           and self._find_match_in(query, context, pattern, Context.ZONE):
            return True

        if self._move(query, context, Context.LINE):
            return self._find_match(query, context, pattern)

        return False

    def _do_find(self, query: SearchQuery, context: Context) -> Context | None:
        """Performs the actual search."""

        msg = f"FLAT REVIEW FINDER: Searching for {str(query)}"
        if self._match:
            msg += f". Last match: {self._match}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        flags = re.U
        if not query.case_sensitive:
            flags = flags | re.IGNORECASE
        if query.match_entire_word:
            regexp = "\\b" + query.search_string + "\\b"
        else:
            regexp = query.search_string
        pattern = re.compile(regexp, flags)

        self._save_location(context)
        if query.start_at_top:
            context.go_to_start_of(Context.WINDOW)

        location = None
        if self._find_match(query, context, pattern):
            self._save_location(context)
            self._match = _SearchQueryMatch(context, pattern)
            self._wrapped = False
            location = copy.copy(context)
        else:
            self._restore_location(context)
        self._last_query = copy.copy(query)
        return location

    def _save_location(self, context: Context) -> None:
        """Saves the context location."""

        self._location = context.get_current_location()

    def _restore_location(self, context: Context) -> None:
        """Restores the context location."""

        context.set_current_location(self._location)
        self._location = 0, 0, 0, 0

class FlatReviewFinderGUI:
    """The dialog containing the find options."""

    def __init__(self, script, query_handler: Callable[[SearchQuery], None]) -> None:
        self._script = script
        self._entry: Gtk.Entry | None = None
        self._gui: Gtk.Dialog = self._create_dialog()
        self._query: SearchQuery = SearchQuery()
        self.on_apply: Callable[[SearchQuery], None] = query_handler
        self._focus: Atspi.Accessible | None = None

    def _create_dialog(self) -> Gtk.Dialog:
        """Creates the Find dialog."""

        def _frame_with_grid(label, widgets):
            frame = Gtk.Frame()
            frame.set_shadow_type(Gtk.ShadowType.NONE) # pylint: disable=no-member
            label = Gtk.Label(f"<b>{label}</b>")
            label.set_use_markup(True)
            frame.set_label_widget(label)
            grid = Gtk.Grid()
            for i, widget in enumerate(widgets):
                grid.attach(widget, 0, i, 1, 1)
            frame.add(grid) # pylint: disable=no-member
            return frame

        dialog = Gtk.Dialog(
            guilabels.FIND_DIALOG_TITLE, None, Gtk.DialogFlags.MODAL,
            (Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE, Gtk.STOCK_FIND, Gtk.ResponseType.APPLY))
        dialog.set_default_response(Gtk.ResponseType.APPLY)
        grid = Gtk.Grid()
        grid.set_row_spacing(20)
        grid.set_column_spacing(20)
        grid.set_border_width(12) # pylint: disable=no-member
        dialog.get_content_area().add(grid)

        entry_grid = Gtk.Grid()
        entry_grid.set_hexpand(True)
        entry_grid.set_column_spacing(20)
        self._entry = Gtk.Entry()
        self._entry.set_hexpand(True)
        self._entry.set_activates_default(True)
        self._entry.connect("changed", self.on_entry_changed)
        label = Gtk.Label(guilabels.FIND_SEARCH_FOR)
        label.set_use_markup(True)
        label.set_use_underline(True)
        label.set_mnemonic_widget(self._entry)
        entry_grid.attach(label, 0, 0, 1, 1)
        entry_grid.attach(self._entry, 1, 0, 2, 1)
        grid.attach(entry_grid, 0, 0, 3, 1)

        rb1 = Gtk.RadioButton.new_with_mnemonic_from_widget(
            None, guilabels.FIND_START_AT_CURRENT_LOCATION)
        rb1.connect("toggled", self.on_current_location_toggled)
        rb2 = Gtk.RadioButton.new_with_mnemonic_from_widget(
            rb1, guilabels.FIND_START_AT_TOP_OF_WINDOW)
        grid.attach(_frame_with_grid(guilabels.FIND_START_FROM, (rb1, rb2)), 0, 1, 1, 1)

        cb1 = Gtk.CheckButton.new_with_mnemonic(guilabels.FIND_SEARCH_BACKWARDS)
        cb1.connect("toggled", self.on_search_backwards_toggled)
        cb2 = Gtk.CheckButton.new_with_mnemonic(guilabels.FIND_WRAP_AROUND)
        cb2.connect("toggled", self.on_wrap_around_toggled)
        grid.attach(_frame_with_grid(guilabels.FIND_SEARCH_DIRECTION, (cb1, cb2)), 1, 1, 1, 1)

        cb3 = Gtk.CheckButton.new_with_mnemonic(guilabels.FIND_MATCH_CASE)
        cb3.connect("toggled", self.on_match_case_toggled)
        cb4 = Gtk.CheckButton.new_with_mnemonic(guilabels.FIND_MATCH_ENTIRE_WORD)
        cb4.connect("toggled", self.on_match_entire_word_toggled)
        grid.attach(_frame_with_grid(guilabels.FIND_MATCH_OPTIONS, (cb3, cb4)), 2, 1, 1, 1)

        dialog.connect("response", self.on_response)
        return dialog

    def on_current_location_toggled(self, widget: Gtk.Widget) -> None:
        """The handler for the 'toggled' signal on the current-location radio button."""

        self._query.start_at_top = not widget.get_active()

    def on_entry_changed(self, widget: Gtk.Entry) -> None:
        """The handler for the 'changed' signal on the search entry."""

        self._query.search_string = widget.get_text()

    def on_match_case_toggled(self, widget: Gtk.CheckButton) -> None:
        """The handler for the 'toggled' signal on the match-case checkbox."""

        self._query.case_sensitive = widget.get_active()

    def on_match_entire_word_toggled(self, widget: Gtk.CheckButton) -> None:
        """The handler for the 'toggled' signal on the match-entire-word checkbox."""

        self._query.match_entire_word = widget.get_active()

    def on_search_backwards_toggled(self, widget: Gtk.CheckButton) -> None:
        """The handler for the 'toggled' signal on the search-backwards checkbox."""

        self._query.search_backwards = widget.get_active()

    def on_wrap_around_toggled(self, widget: Gtk.CheckButton) -> None:
        """The handler for the 'toggled' signal on the wrap-around checkbox."""

        self._query.window_wrap = widget.get_active()

    def on_response(self, dialog: Gtk.Dialog, response: int) -> None:
        """The handler for the 'response' signal."""

        if response == Gtk.ResponseType.CLOSE:
            self._gui.hide()
            return

        if response == Gtk.ResponseType.APPLY:
            self.on_apply(copy.copy(self._query))
            dialog.destroy()
            self._script.run_find_command_on = self._focus

    def show_gui(self, focus: Atspi.Accessible) -> None:
        """Shows the find dialog."""

        self._focus = focus
        self._gui.show_all() # pylint: disable=no-member
        self._gui.present_with_time(time.time())


_finder: FlatReviewFinder = FlatReviewFinder()
def get_finder() -> FlatReviewFinder:
    """Returns the Flat Review Finder"""

    return _finder
