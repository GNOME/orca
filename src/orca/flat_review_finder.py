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

"""Provides support for a flat review find."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2006-2008 Sun Microsystems Inc." \
                "Copyright (c) 2022 Igalia, S.L."
__license__   = "LGPL"


import copy
import re

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from . import cmdnames
from . import debug
from . import guilabels
from . import input_event
from . import keybindings
from . import messages
from . import script_manager

from .flat_review import Context


class _SearchQueryMatch:
    """Represents a SearchQuery match."""

    def __init__(self, context, pattern):
        self._line = context.lineIndex
        self._zone = context.zoneIndex
        self._word = context.wordIndex
        self._char = context.charIndex
        self._pattern = pattern
        self._line_string = context.getCurrent(Context.LINE)[0]

    def __str__(self):
        return (
            f"SEARCH QUERY MATCH: '{self._line_string}' "
            f"(line {self._line}, zone {self._zone}, word {self._word}, char {self._char}) "
            f"for '{self._pattern}'"
        )

    def __eq__(self, other):
        if not other:
            return False

        return self._line_string == other._line_string and \
               self._line == other._line and \
               self._zone == other._zone and \
               self._word == other._word and \
               self._char == other._char

class SearchQuery:
    """Represents a search that the user wants to perform."""

    def __init__(self):
        self.search_string = ""
        self.search_backwards = False
        self.case_sensitive = False
        self.match_entire_word = False
        self.window_wrap = False
        self.start_at_top = False

    def __str__(self):
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

    def __init__(self):
        self._gui = None
        self._handlers = self.get_handlers(True)
        self._desktop_bindings = keybindings.KeyBindings()
        self._laptop_bindings = keybindings.KeyBindings()
        self._last_query = None
        self._location = [0, 0, 0, 0]
        self._wrapped = False
        self._match = None

    def get_bindings(self, refresh=False, is_desktop=True):
        """Returns the flat-review-presenter keybindings."""

        if refresh:
            msg = "FLAT REVIEW FINDER: Refreshing bindings."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self._setup_bindings()
        elif is_desktop and self._desktop_bindings.is_empty():
            self._setup_bindings()
        elif not is_desktop and self._laptop_bindings.is_empty():
            self._setup_bindings()

        if is_desktop:
            return self._desktop_bindings
        return self._laptop_bindings

    def get_handlers(self, refresh=False):
        """Returns the flat-review-finder handlers."""

        if refresh:
            msg = "FLAT REVIEW FINDER: Refreshing handlers."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self._setup_handlers()

        return self._handlers

    def _setup_bindings(self):
        """Sets up the flat-review-finder key bindings."""

        self._setup_desktop_bindings()
        self._setup_laptop_bindings()

    def _setup_desktop_bindings(self):
        """Sets up the flat-review-finder desktop key bindings."""

        self._desktop_bindings = keybindings.KeyBindings()

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Delete",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("findHandler")))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Delete",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("findNextHandler")))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Delete",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_SHIFT_MODIFIER_MASK,
                self._handlers.get("findPreviousHandler")))

        msg = "FLAT REVIEW FINDER: Desktop bindings set up."
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def _setup_laptop_bindings(self):
        """Sets up the flat-review-finder laptop key bindings."""

        self._laptop_bindings = keybindings.KeyBindings()

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "bracketleft",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("findHandler")))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "bracketright",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("findNextHandler")))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "bracketright",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_CTRL_MODIFIER_MASK,
                self._handlers.get("findPreviousHandler")))

        msg = "FLAT REVIEW FINDER: Laptop bindings set up."
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def _setup_handlers(self):
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
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def _on_query(self, query):
        """Handler after a query has been made via the Find dialog."""

        self._last_query = query

    def show_dialog(self, script, event=None):
        """Shows the Find dialog."""

        self._gui = FlatReviewFinderGUI(script, self._on_query)
        self._gui.show_gui()
        return True

    def find_next(self, script, event=None):
        """Searches forward for the next instance of the string."""

        if self._last_query is None:
            self.show_dialog(script, event)
            return True

        self._last_query.search_backwards = False
        self._last_query.start_at_top = False
        self.find(script, self._last_query)
        return True

    def find_previous(self, script, event=None):
        """Searches backwards for the previous instance of the string."""

        if self._last_query is None:
            self.show_dialog(script, event)
            return True

        self._last_query.search_backwards = True
        self._last_query.start_at_top = False
        self.find(script, self._last_query)
        return True

    def find(self, script, query=None):
        """Searches for the specified query, or the most recent one."""

        query = query or self._last_query
        if query is None:
            return

        context = script.getFlatReviewContext()
        location = self._do_find(query, context)
        if not location:
            script.presentMessage(messages.STRING_NOT_FOUND)
        else:
            context.setCurrent(location.lineIndex, location.zoneIndex, \
                                location.wordIndex, location.charIndex)
            script.get_flat_review_presenter().present_item(script)
            script.targetCursorCell = script.getBrailleCursorCell()

    def _move(self, query, context, context_type):
        """Moves within the flat review context while looking for a match."""

        if context_type == Context.WORD:
            if query.search_backwards:
                return context.goPrevious(Context.WORD, Context.WRAP_LINE)
            return context.goNext(Context.WORD, Context.WRAP_LINE)

        if context_type == Context.ZONE:
            if query.search_backwards:
                moved = context.goPrevious(Context.ZONE, Context.WRAP_LINE)
                context.goEnd(Context.ZONE)
                return moved
            return context.goNext(Context.ZONE, Context.WRAP_LINE)

        if context_type == Context.LINE:
            if query.search_backwards:
                moved = context.goPrevious(Context.LINE, Context.WRAP_LINE)
                context.goEnd(Context.LINE)
            else:
                moved = context.goNext(Context.LINE, Context.WRAP_LINE)
            if moved:
                return True
            if not query.window_wrap or self._wrapped:
                return False
            self._wrapped = True
            script = script_manager.get_manager().get_active_script()
            if query.search_backwards:
                script.presentMessage(messages.WRAPPING_TO_BOTTOM)
                moved = context.goPrevious(Context.LINE, Context.WRAP_ALL)
            else:
                script.presentMessage(messages.WRAPPING_TO_TOP)
                moved = context.goNext(Context.LINE, Context.WRAP_ALL)
            return moved

        return False

    def _find_match_in(self, query, context, pattern, context_type):
        """Searches for a match of pattern in context for the given type."""

        def matches(context, pattern, context_type):
            if context_type == Context.LINE:
                type_string = "LINE"
            elif context_type == Context.ZONE:
                type_string = "ZONE"
            elif context_type == Context.WORD:
                type_string = "WORD"
            else:
                return False

            string = context.getCurrent(context_type)[0]
            match = re.search(pattern, string)
            debug_string = string.replace("\n", "\\n")
            msg = f"FLAT REVIEW FINDER: Looking in {type_string}='{debug_string}'. Match: {match}"
            debug.println(debug.LEVEL_INFO, msg, True)
            return bool(match)

        found = matches(context, pattern, context_type)
        while not found:
            if not self._move(query, context, context_type):
                break
            found = matches(context, pattern, context_type)

        return found

    def _find_match(self, query, context, pattern):
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

    def _do_find(self, query, context):
        """Performs the actual search."""

        msg = f"FLAT REVIEW FINDER: Searching for {str(query)}"
        if self._match:
            msg += f". Last match: {self._match}"
        debug.printMessage(debug.LEVEL_INFO, msg, True)

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
            context.goBegin(Context.WINDOW)

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

    def _save_location(self, context):
        """Saves the context location."""

        self._location = [context.lineIndex,
                          context.zoneIndex,
                          context.wordIndex,
                          context.charIndex]

    def _restore_location(self, context):
        """Restores the context location."""

        context.setCurrent(*self._location)
        self._location = [0, 0, 0, 0]

class FlatReviewFinderGUI:
    """The dialog containing the find options."""

    def __init__(self, script, query_handler):
        self._script = script
        self._entry = None
        self._gui = self._create_dialog()
        self._query = SearchQuery()
        self.on_apply = query_handler

    def _create_dialog(self):
        """Creates the Find dialog."""

        def _frame_with_grid(label, widgets):
            frame = Gtk.Frame()
            frame.set_shadow_type(Gtk.ShadowType.NONE)
            label = Gtk.Label(f"<b>{label}</b>")
            label.set_use_markup(True)
            frame.set_label_widget(label)
            grid = Gtk.Grid()
            for i, widget in enumerate(widgets):
                grid.attach(widget, 0, i, 1, 1)
            frame.add(grid)
            return frame

        dialog = Gtk.Dialog(
            guilabels.FIND_DIALOG_TITLE, None, Gtk.DialogFlags.MODAL,
            (Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE, Gtk.STOCK_FIND, Gtk.ResponseType.APPLY))
        dialog.set_default_response(Gtk.ResponseType.APPLY)
        grid = Gtk.Grid()
        grid.set_row_spacing(20)
        grid.set_column_spacing(20)
        grid.set_border_width(12)
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

    def on_current_location_toggled(self, widget):
        """The handler for the 'toggled' signal on the current-location radio button."""

        self._query.start_at_top = not widget.get_active()

    def on_entry_changed(self, widget):
        """The handler for the 'changed' signal on the search entry."""

        self._query.search_string = widget.get_text()

    def on_match_case_toggled(self, widget):
        """The handler for the 'toggled' signal on the match-case checkbox."""

        self._query.case_sensitive = widget.get_active()

    def on_match_entire_word_toggled(self, widget):
        """The handler for the 'toggled' signal on the match-entire-word checkbox."""

        self._query.match_entire_word = widget.get_active()

    def on_search_backwards_toggled(self, widget):
        """The handler for the 'toggled' signal on the search-backwards checkbox."""

        self._query.search_backwards = widget.get_active()

    def on_wrap_around_toggled(self, widget):
        """The handler for the 'toggled' signal on the wrap-around checkbox."""

        self._query.window_wrap = widget.get_active()

    def on_response(self, dialog, response):
        """The handler for the 'response' signal."""

        if response == Gtk.ResponseType.CLOSE:
            self._gui.hide()
            return

        if response == Gtk.ResponseType.APPLY:
            self.on_apply(copy.copy(self._query))

            # TODO - JD: Verify this.
            # Merely hiding the dialog causes the find to take place before
            # the original window has fully regained focus.
            dialog.destroy()

            self._script.run_find_command = True

    def show_gui(self):
        """Shows the notifications list dialog."""

        self._gui.show_all()
        self._gui.present_with_time(Gtk.get_current_event_time())


_finder = FlatReviewFinder()
def getFinder():
    """Returns the Flat Review Finder"""

    return _finder
