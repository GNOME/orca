# Orca
#
# Copyright 2014 Igalia, S.L.
#
# Author: Joanmarie Diggs <jdiggs@igalia.com>
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
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-public-methods

"""Script-customizable support for application spellcheckers."""

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2014 Igalia, S.L."
__license__   = "LGPL"

import re

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from orca import debug
from orca import focus_manager
from orca import guilabels
from orca import messages
from orca import object_properties
from orca import settings_manager
from orca.ax_object import AXObject
from orca.ax_text import AXText
from orca.ax_utilities import AXUtilities


class SpellCheck:
    """Script-customizable support for application spellcheckers."""

    def __init__(self, script, has_change_to_entry=True):
        self._script = script
        self._has_change_to_entry = has_change_to_entry
        self._window = None
        self._error_widget = None
        self._change_to_entry = None
        self._suggestions_list = None
        self._activated = False
        self._document_position = None, -1

        self.spell_error_check_button = None
        self.spell_suggestion_check_button = None
        self.present_context_check_button = None

    def activate(self, window):
        """Activates spellcheck support."""

        tokens = ["SPELL CHECK: Attempting activation for", window]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        if not self.can_be_spell_check_window(window):
            tokens = ["SPELL CHECK:", window, "is not spellcheck window"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        if self._has_change_to_entry:
            self._change_to_entry = self._find_change_to_entry(window)
            if self._change_to_entry is None:
                msg = "SPELL CHECK: Change-to entry not found"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return False

        self._error_widget = self._find_error_widget(window)
        if self._error_widget is None:
            msg = "SPELL CHECK: Error widget not found"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        self._suggestions_list = self._find_suggestions_list(window)
        if self._suggestions_list is None:
            msg = "SPELL CHECK: Suggestions list not found"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        self._window = window
        self._activated = True
        msg = "SPELL CHECK: Activation complete"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    def deactivate(self):
        """Deactivates spellcheck support."""

        self._clear_state()

    def set_document_position(self, obj, offset):
        """Sets the document position as an (obj, offset) tuple."""

        self._document_position = obj, offset

    def get_error_widget(self):
        """Returns the widget which contains the misspelled word."""

        return self._error_widget

    def get_misspelled_word(self):
        """Returns the misspelled word."""

        if not self._error_widget:
            return ""

        return AXText.get_all_text(self._error_widget) or AXObject.get_name(self._error_widget)

    def get_completion_message(self):
        """Returns the string containing the app-provided message that the check is complete."""

        if not self._error_widget:
            return ""

        return AXText.get_all_text(self._error_widget) or AXObject.get_name(self._error_widget)

    def get_change_to_entry(self):
        """Returns the widget, usually an entry, that displays the suggested change-to value."""

        return self._change_to_entry

    def get_suggestions_list(self):
        """Returns the widget containing the list of suggestions."""

        return self._suggestions_list

    def is_active(self):
        """Returns True if spellcheck support is currently being used."""

        return self._activated

    def is_spell_check_window(self, window):
        """Returns True if window is the window/dialog containing the spellcheck."""

        if window and window == self._window:
            return True

        return self.activate(window)

    def is_complete(self):
        """Returns True if we have reason to conclude the check is complete."""

        if self._has_change_to_entry:
            return not AXUtilities.is_sensitive(self._change_to_entry)
        return False

    def is_autofocus_event(self, _event):
        """Returns True if event is an auto-focus event."""

        return False

    def is_suggestions_item(self, obj):
        """Returns True if obj is an item in the suggestions list."""

        if not self._suggestions_list:
            return False

        result = AXObject.is_ancestor(obj, self._suggestions_list)
        tokens = ["SPELL CHECK:", obj, "is suggestion in", self._suggestions_list, f": {result}"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    def present_context(self):
        """Presents the context/surrounding content of the misspelled word."""

        if not self.is_active():
            return False

        obj, offset = self._document_position
        if not (obj and offset >= 0):
            return False

        # This should work, but some toolkits are broken.
        string = AXText.get_sentence_at_offset(obj, offset)[0]
        if not string:
            string = AXText.get_line_at_offset(obj, offset)[0]
            sentences = re.split(r'(?:\.|\!|\?)', string)
            word = self.get_misspelled_word()
            if string.count(word) == 1:
                match = list(filter(lambda x: x.count(word), sentences))
                string = match[0]

        if not string.strip():
            return False

        msg = messages.MISSPELLED_WORD_CONTEXT % string
        voice = self._script.speech_generator.voice(string=msg)
        self._script.speakMessage(msg, voice=voice)
        return True

    def present_completion_message(self):
        """Presents the message that spellcheck is complete."""

        if not (self.is_active() and self.is_complete()):
            return False

        self._script.clearBraille()
        msg = self.get_completion_message()
        voice = self._script.speech_generator.voice(string=msg)
        self._script.presentMessage(msg, voice=voice)
        return True

    def present_error_details(self, detailed=False):
        """Presents the details of the error."""

        if self.is_complete():
            msg = "SPELL CHECK: Not presenting error details: spellcheck is complete"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if self.present_mistake(detailed):
            self.present_suggestion(detailed)
            if detailed or settings_manager.get_manager().get_setting("spellcheckPresentContext"):
                self.present_context()
            return True

        return False

    def present_mistake(self, detailed=False):
        """Presents the misspelled word."""

        if not self.is_active():
            msg = "SPELL CHECK: Not presenting mistake: spellcheck support is not active"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        word = self.get_misspelled_word()
        if not word:
            msg = "SPELL CHECK: Not presenting mistake: misspelled word not found"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        msg = messages.MISSPELLED_WORD % word
        voice = self._script.speech_generator.voice(string=msg)
        self._script.speakMessage(msg, voice=voice)
        if detailed or settings_manager.get_manager().get_setting("spellcheckSpellError"):
            self._script.spell_item(word)

        return True

    def present_suggestion(self, detailed=False):
        """Presents the suggested correction."""

        if not self._has_change_to_entry:
            return self.present_suggestion_list_item(detailed, include_label=True)

        if not self.is_active():
            msg = "SPELL CHECK: Not presenting suggestion: spellcheck support is not active"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        entry = self._change_to_entry
        if not entry:
            msg = "SPELL CHECK: Not presenting suggestion: change-to entry not found"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        label = self._script.utilities.displayedLabel(entry) or AXObject.get_name(entry)
        string = AXText.get_substring(entry, 0, -1)
        msg = f"{label} {string}"
        voice = self._script.speech_generator.voice(string=msg)
        self._script.speakMessage(msg, voice=voice)
        if detailed or settings_manager.get_manager().get_setting("spellcheckSpellSuggestion"):
            self._script.spell_item(string)

        return True

    def present_suggestion_list_item(self, detailed=False, include_label=False):
        """Presents the current item from the suggestions list."""

        if not self.is_active():
            msg = "SPELL CHECK: Not presenting suggested item: spellcheck support is not active"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        suggestions = self._suggestions_list
        if not suggestions:
            msg = "SPELL CHECK: Not presenting suggested item: suggestions list not found"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        items = self._script.utilities.selectedChildren(suggestions)
        if not len(items) == 1:
            return False

        if include_label:
            label = self._script.utilities.displayedLabel(suggestions) \
                or AXObject.get_name(suggestions)
        else:
            label = ""
        string = AXObject.get_name(items[0])

        msg = f"{label} {string}"
        voice = self._script.speech_generator.voice(string=msg)
        self._script.speakMessage(msg.strip(), voice=voice)
        if detailed or settings_manager.get_manager().get_setting("spellcheckSpellSuggestion"):
            self._script.spell_item(string)

        if settings_manager.get_manager().get_setting("enablePositionSpeaking") \
           and items[0] == focus_manager.get_manager().get_locus_of_focus():
            index, total = self._get_suggestion_index_and_position(items[0])
            msg = object_properties.GROUP_INDEX_SPEECH % {"index": index, "total": total}
            self._script.speakMessage(msg)

        return True

    def _clear_state(self):
        self._window = None
        self._error_widget = None
        self._change_to_entry = None
        self._suggestions_list = None
        self._activated = False

    def can_be_spell_check_window(self, window):
        """Returns True if the window can be the spell check window."""

        window_id = AXObject.get_accessible_id(window)
        if not window_id:
            tokens = ["SPELL CHECK:", window, "lacks an accessible ID. Will use heuristics."]
            return self._is_candidate_window(window)

        # The "SpellingDialog" accessible id is supported by the following:
        # * LO >= 25.2
        tokens = ["SPELL CHECK:", window, f"has id: '{window_id}'"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return window_id == "SpellingDialog"

    def _is_candidate_window(self, _window):
        """Returns True if window could be the spellcheck window pending other checks."""

        raise NotImplementedError("SPELL CHECK: subclasses must provide this implementation.")

    def _find_change_to_entry(self, root):
        if not self._has_change_to_entry:
            return None

        result = AXObject.find_descendant(root, AXUtilities.is_single_line_entry)
        tokens = ["SPELL CHECK: Change-to entry for:", root, "is:", result]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    def _is_error_widget(self, obj):
        if not AXUtilities.is_label(obj):
            return False

        if not AXUtilities.object_is_unrelated(obj):
            return False

        name = AXObject.get_name(obj)
        if ":" in name:
            return False

        if len(name.split()) != 1:
            return False

        return True

    def _find_error_widget(self, root):
        result = AXObject.find_descendant(root, self._is_error_widget)
        tokens = ["SPELL CHECK: Error widget for:", root, "is:", result]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    def _is_suggestions_list(self, obj):
        if not AXObject.supports_selection(obj):
            return False
        return AXUtilities.is_list(obj) or AXUtilities.is_list_box(obj) \
            or AXUtilities.is_table(obj) or AXUtilities.is_tree_table(obj)

    def _find_suggestions_list(self, root):
        result = AXObject.find_descendant(root, self._is_suggestions_list)
        tokens = ["SPELL CHECK: Suggestions list for:", root, "is:", result]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    def _get_suggestion_index_and_position(self, suggestion):
        return AXUtilities.get_position_in_set(suggestion) + 1, AXUtilities.get_set_size(suggestion)

    def get_app_preferences_gui(self):
        """Returns the preferences GUI for spellcheck support."""

        frame = Gtk.Frame()
        label = Gtk.Label(label=f"<b>{guilabels.SPELL_CHECK}</b>")
        label.set_use_markup(True)
        frame.set_label_widget(label)

        alignment = Gtk.Alignment.new(0.5, 0.5, 1, 1)
        alignment.set_padding(0, 0, 12, 0)
        frame.add(alignment)

        grid = Gtk.Grid()
        alignment.add(grid)

        label = guilabels.SPELL_CHECK_SPELL_ERROR
        value = settings_manager.get_manager().get_setting('spellcheckSpellError')
        self.spell_error_check_button = Gtk.CheckButton.new_with_mnemonic(label)
        self.spell_error_check_button.set_active(value)
        grid.attach(self.spell_error_check_button, 0, 0, 1, 1)

        label = guilabels.SPELL_CHECK_SPELL_SUGGESTION
        value = settings_manager.get_manager().get_setting('spellcheckSpellSuggestion')
        self.spell_suggestion_check_button = Gtk.CheckButton.new_with_mnemonic(label)
        self.spell_suggestion_check_button.set_active(value)
        grid.attach(self.spell_suggestion_check_button, 0, 1, 1, 1)

        label = guilabels.SPELL_CHECK_PRESENT_CONTEXT
        value = settings_manager.get_manager().get_setting('spellcheckPresentContext')
        self.present_context_check_button = Gtk.CheckButton.new_with_mnemonic(label)
        self.present_context_check_button.set_active(value)
        grid.attach(self.present_context_check_button, 0, 2, 1, 1)

        return frame

    def get_preferences_from_gui(self):
        """Returns a dictionary with the app-specific preferences."""

        return {
            "spellcheckSpellError": self.spell_error_check_button.get_active(),
            "spellcheckSpellSuggestion": self.spell_suggestion_check_button.get_active(),
            "spellcheckPresentContext": self.present_context_check_button.get_active()
        }
