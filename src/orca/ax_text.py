# Orca
#
# Copyright 2024 Igalia, S.L.
# Copyright 2024 GNOME Foundation Inc.
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

# pylint: disable=broad-exception-caught
# pylint: disable=wrong-import-position
# pylint: disable=too-many-locals
# pylint: disable=too-many-public-methods

"""
Utilities for obtaining information about accessible text.
These utilities are app-type- and toolkit-agnostic. Utilities that might have
different implementations or results depending on the type of app (e.g. terminal,
chat, web) or toolkit (e.g. Qt, Gtk) should be in script_utilities.py file(s).

N.B. There are currently utilities that should never have custom implementations
that live in script_utilities.py files. These will be moved over time.
"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2024 Igalia, S.L." \
                "Copyright (c) 2024 GNOME Foundation Inc."
__license__   = "LGPL"

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from . import debug
from .ax_object import AXObject
from .ax_utilities_state import AXUtilitiesState

class AXText:
    """Utilities for obtaining information about accessible text."""

    @staticmethod
    def get_text_for_debugging(obj):
        """Returns the text content of obj for debugging."""

        try:
            result = Atspi.Text.get_text(obj, 0, Atspi.Text.get_character_count(obj))
        except Exception:
            return ""

        words = result.split()
        if len(words) > 10:
            debug_string = f"{' '.join(words[:5])} ... {' '.join(words[-5:])}"
        else:
            debug_string = result

        return debug_string.replace("\n", "\\n")

    @staticmethod
    def get_character_at_offset(obj, offset=None):
        """Returns the character, start, and end for the current or specified offset."""

        length = AXText.get_character_count(obj)
        if not length:
            return "", 0, 0

        if offset is None:
            offset = AXText.get_caret_offset(obj)

        if not 0 <= offset <= length:
            msg = f"WARNING: Offset {offset} is not valid. No character can be provided."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return "", 0, 0

        try:
            result = Atspi.Text.get_string_at_offset(obj, offset, Atspi.TextGranularity.CHAR)
        except Exception as error:
            try:
                result = Atspi.Text.get_text_at_offset(obj, offset, Atspi.TextBoundaryType.CHAR)
            except Exception as error2:
                msg = f"AXText: Exception in get_character_at_offset: {error2}"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                return "", 0, 0

            # https://gitlab.gnome.org/GNOME/at-spi2-core/-/issues/161
            msg = f"WARNING: String at offset failed; text at offset succeeded: {error}"
            debug.printMessage(debug.LEVEL_INFO, msg, True)

        debug_string = result.content.replace("\n", "\\n")
        tokens = [f"AXText: Character at offset {offset} in", obj,
                  f"'{debug_string}' ({result.start_offset}-{result.end_offset})"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return result.content, result.start_offset, result.end_offset

    @staticmethod
    def get_character_at_point(obj, x, y):
        """Returns the character, start, and end at the specified point."""

        offset = AXText.get_offset_at_point(obj, x, y)
        if not 0 <= offset < AXText.get_character_count(obj):
            return "", 0, 0

        return AXText.get_character_at_offset(obj, offset)

    @staticmethod
    def iter_character(obj, offset=None):
        """Generator to iterate by character in obj starting with the character at offset."""

        if offset is None:
            offset = AXText.get_caret_offset(obj)

        last_result = None
        length = AXText.get_character_count(obj)
        while offset < length:
            character, start, end = AXText.get_character_at_offset(obj, offset)
            if last_result is None and not character:
                return
            if character and (character, start, end) != last_result:
                yield character, start, end
            offset = max(end, offset + 1)
            last_result = character, start, end

    @staticmethod
    def get_word_at_offset(obj, offset=None):
        """Returns the word, start, and end for the current or specified offset."""

        length = AXText.get_character_count(obj)
        if not length:
            return "", 0, 0

        if offset is None:
            offset = AXText.get_caret_offset(obj)

        offset = min(max(0, offset), length - 1)
        try:
            result = Atspi.Text.get_string_at_offset(obj, offset, Atspi.TextGranularity.WORD)
        except Exception as error:
            try:
                result = Atspi.Text.get_text_at_offset(
                    obj, offset, Atspi.TextBoundaryType.WORD_START)
            except Exception as error2:
                msg = f"AXText: Exception in get_word_at_offset: {error2}"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                return "", 0, 0

            # https://gitlab.gnome.org/GNOME/at-spi2-core/-/issues/161
            msg = f"WARNING: String at offset failed; text at offset succeeded: {error}"
            debug.printMessage(debug.LEVEL_INFO, msg, True)

        tokens = [f"AXText: Word at offset {offset} in", obj,
                  f"'{result.content}' ({result.start_offset}-{result.end_offset})"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return result.content, result.start_offset, result.end_offset

    @staticmethod
    def get_word_at_point(obj, x, y):
        """Returns the word, start, and end at the specified point."""

        offset = AXText.get_offset_at_point(obj, x, y)
        if not 0 <= offset < AXText.get_character_count(obj):
            return "", 0, 0

        return AXText.get_word_at_offset(obj, offset)

    @staticmethod
    def iter_word(obj, offset=None):
        """Generator to iterate by word in obj starting with the word at offset."""

        if offset is None:
            offset = AXText.get_caret_offset(obj)

        last_result = None
        length = AXText.get_character_count(obj)
        while offset < length:
            word, start, end = AXText.get_word_at_offset(obj, offset)
            if last_result is None and not word:
                return
            if word and (word, start, end) != last_result:
                yield word, start, end
            offset = max(end, offset + 1)
            last_result = word, start, end

    @staticmethod
    def get_line_at_offset(obj, offset=None):
        """Returns the line, start, and end for the current or specified offset."""

        length = AXText.get_character_count(obj)
        if not length:
            return "", 0, 0

        if offset is None:
            offset = AXText.get_caret_offset(obj)

        # Don't adjust the length in multiline text because we want to say "blank" at the end.
        if not AXUtilitiesState.is_multi_line(obj):
            offset = min(max(0, offset), length - 1)
        else:
            offset = max(0, offset)
        try:
            result = Atspi.Text.get_string_at_offset(obj, offset, Atspi.TextGranularity.LINE)
        except Exception as error:
            try:
                result = Atspi.Text.get_text_at_offset(
                    obj, offset, Atspi.TextBoundaryType.LINE_START)
            except Exception as error2:
                msg = f"AXText: Exception in get_line_at_offset: {error2}"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                return "", 0, 0

            # https://gitlab.gnome.org/GNOME/at-spi2-core/-/issues/161
            msg = f"WARNING: String at offset failed; text at offset succeeded: {error}"
            debug.printMessage(debug.LEVEL_INFO, msg, True)

        debug_string = result.content.replace("\n", "\\n")
        tokens = [f"AXText: Line at offset {offset} in", obj,
                  f"'{debug_string}' ({result.start_offset}-{result.end_offset})"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return result.content, result.start_offset, result.end_offset

    @staticmethod
    def get_line_at_point(obj, x, y):
        """Returns the line, start, and end at the specified point."""

        offset = AXText.get_offset_at_point(obj, x, y)
        if not 0 <= offset < AXText.get_character_count(obj):
            return "", 0, 0

        return AXText.get_line_at_offset(obj, offset)

    @staticmethod
    def iter_line(obj, offset=None):
        """Generator to iterate by line in obj starting with the line at offset."""

        if offset is None:
            offset = AXText.get_caret_offset(obj)

        last_result = None
        length = AXText.get_character_count(obj)
        while offset < length:
            line, start, end = AXText.get_line_at_offset(obj, offset)
            if last_result is None and not line:
                return
            if line and (line, start, end) != last_result:
                yield line, start, end
            offset = max(end, offset + 1)
            last_result = line, start, end

    @staticmethod
    def get_sentence_at_offset(obj, offset=None):
        """Returns the sentence, start, and end for the current or specified offset."""

        length = AXText.get_character_count(obj)
        if not length:
            return "", 0, 0

        if offset is None:
            offset = AXText.get_caret_offset(obj)

        offset = min(max(0, offset), length - 1)
        try:
            result = Atspi.Text.get_string_at_offset(obj, offset, Atspi.TextGranularity.SENTENCE)
        except Exception as error:
            try:
                result = Atspi.Text.get_text_at_offset(
                    obj, offset, Atspi.TextBoundaryType.SENTENCE_START)
            except Exception as error2:
                msg = f"AXText: Exception in get_sentence_at_offset: {error2}"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                return "", 0, 0

            # https://gitlab.gnome.org/GNOME/at-spi2-core/-/issues/161
            msg = f"WARNING: String at offset failed; text at offset succeeded: {error}"
            debug.printMessage(debug.LEVEL_INFO, msg, True)

        tokens = [f"AXText: Sentence at offset {offset} in", obj,
                  f"'{result.content}' ({result.start_offset}-{result.end_offset})"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return result.content, result.start_offset, result.end_offset

    @staticmethod
    def get_sentence_at_point(obj, x, y):
        """Returns the sentence, start, and end at the specified point."""

        offset = AXText.get_offset_at_point(obj, x, y)
        if not 0 <= offset < AXText.get_character_count(obj):
            return "", 0, 0

        return AXText.get_sentence_at_offset(obj, offset)

    @staticmethod
    def iter_sentence(obj, offset=None):
        """Generator to iterate by sentence in obj starting with the sentence at offset."""

        if offset is None:
            offset = AXText.get_caret_offset(obj)

        last_result = None
        length = AXText.get_character_count(obj)
        while offset < length:
            sentence, start, end = AXText.get_sentence_at_offset(obj, offset)
            if last_result is None and not sentence:
                return
            if sentence and (sentence, start, end) != last_result:
                yield sentence, start, end
            offset = max(end, offset + 1)
            last_result = sentence, start, end

    @staticmethod
    def supports_sentence_iteration(obj):
        """Returns True if sentence iteration is supported on obj."""

        if not AXObject.supports_text(obj):
            return False

        string, start, end = AXText.get_sentence_at_offset(obj, 0)
        result = string and 0 <= start < end
        tokens = ["AXText: Sentence iteration supported on", obj, f": {result}"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def get_paragraph_at_offset(obj, offset=None):
        """Returns the paragraph, start, and end for the current or specified offset."""

        length = AXText.get_character_count(obj)
        if not length:
            return "", 0, 0

        if offset is None:
            offset = AXText.get_caret_offset(obj)

        offset = min(max(0, offset), length - 1)
        try:
            result = Atspi.Text.get_string_at_offset(obj, offset, Atspi.TextGranularity.PARAGRAPH)
        except Exception as error:
            msg = f"AXText: Exception in get_paragraph_at_offset: {error}"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return "", 0, 0

        tokens = [f"AXText: Paragraph at offset {offset} in", obj,
                  f"'{result.content}' ({result.start_offset}-{result.end_offset})"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return result.content, result.start_offset, result.end_offset

    @staticmethod
    def get_paragraph_at_point(obj, x, y):
        """Returns the paragraph, start, and end at the specified point."""

        offset = AXText.get_offset_at_point(obj, x, y)
        if not 0 <= offset < AXText.get_character_count(obj):
            return "", 0, 0

        return AXText.get_paragraph_at_offset(obj, offset)

    @staticmethod
    def iter_paragraph(obj, offset=None):
        """Generator to iterate by paragraph in obj starting with the paragraph at offset."""

        if offset is None:
            offset = AXText.get_caret_offset(obj)

        last_result = None
        length = AXText.get_character_count(obj)
        while offset < length:
            paragraph, start, end = AXText.get_paragraph_at_offset(obj, offset)
            if last_result is None and not paragraph:
                return
            if paragraph and (paragraph, start, end) != last_result:
                yield paragraph, start, end
            offset = max(end, offset + 1)
            last_result = paragraph, start, end

    @staticmethod
    def supports_paragraph_iteration(obj):
        """Returns True if paragraph iteration is supported on obj."""

        if not AXObject.supports_text(obj):
            return False

        string, start, end = AXText.get_paragraph_at_offset(obj, 0)
        result = string and 0 <= start < end
        tokens = ["AXText: Paragraph iteration supported on", obj, f": {result}"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def get_character_count(obj):
        """Returns the character count of obj."""

        if not AXObject.supports_text(obj):
            return 0

        try:
            count = Atspi.Text.get_character_count(obj)
        except Exception as error:
            msg = f"AXText: Exception in get_character_count: {error}"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return 0

        tokens = ["AXText:", obj, f"reports {count} characters."]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return count

    @staticmethod
    def get_caret_offset(obj):
        """Returns the caret offset of obj."""

        if not AXObject.supports_text(obj):
            return -1

        try:
            offset = Atspi.Text.get_caret_offset(obj)
        except Exception as error:
            msg = f"AXText: Exception in get_caret_offset: {error}"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return -1

        tokens = ["AXText:", obj, f"reports caret offset of {offset}."]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return offset

    @staticmethod
    def set_caret_offset(obj, offset):
        """Returns False if we definitely failed to set the offset. True cannot be trusted."""

        if not AXObject.supports_text(obj):
            return False

        try:
            result = Atspi.Text.set_caret_offset(obj, offset)
        except Exception as error:
            msg = f"AXText: Exception in set_caret_offset: {error}"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        tokens = [f"AXText: Reported result of setting offset to {offset} in", obj, f": {result}"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def set_caret_offset_to_start(obj):
        """Returns False if we definitely failed to set the offset. True cannot be trusted."""

        return AXText.set_caret_offset(obj, 0)

    @staticmethod
    def set_caret_offset_to_end(obj):
        """Returns False if we definitely failed to set the offset. True cannot be trusted."""

        return AXText.set_caret_offset(obj, AXText.get_character_count(obj))

    @staticmethod
    def get_substring(obj, start_offset, end_offset):
        """Returns the text of obj within the specified offsets."""

        if not AXObject.supports_text(obj):
            return ""

        if end_offset == -1:
            end_offset = AXText.get_character_count(obj)

        try:
            result = Atspi.Text.get_text(obj, start_offset, end_offset)
        except Exception as error:
            msg = f"AXText: Exception in get_substring: {error}"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return ""

        debug_string = result.replace("\n", "\\n")
        tokens = ["AXText: Text of", obj, f"({start_offset}-{end_offset}): '{debug_string}'"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def get_all_text(obj):
        """Returns the text content of obj."""

        length = AXText.get_character_count(obj)
        if not length:
            return ""

        try:
            result = Atspi.Text.get_text(obj, 0, length)
        except Exception as error:
            msg = f"AXText: Exception in get_all_text: {error}"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return ""

        words = result.split()
        if len(words) > 10:
            debug_string = f"{' '.join(words[:5])} ... {' '.join(words[-5:])}"
        else:
            debug_string = result

        debug_string = debug_string.replace("\n", "\\n")
        tokens = ["AXText: Text of", obj, f"'{debug_string}'"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def _get_n_selections(obj):
        """Returns the number of reported selected substrings in obj."""

        if not AXObject.supports_text(obj):
            return 0

        try:
            result = Atspi.Text.get_n_selections(obj)
        except Exception as error:
            msg = f"AXText: Exception in _get_n_selections: {error}"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return 0

        tokens = ["AXText:", obj, f"reports {result} selection(s)."]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def _remove_selection(obj, selection_number):
        """Attempts to remove the specified selection."""

        if not AXObject.supports_text(obj):
            return

        try:
            Atspi.Text.remove_selection(obj, selection_number)
        except Exception as error:
            msg = f"AXText: Exception in _remove_selection: {error}"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return

    @staticmethod
    def has_selected_text(obj):
        """Returns True if obj has selected text."""

        return bool(AXText.get_selected_ranges(obj))

    @staticmethod
    def is_all_text_selected(obj):
        """Returns True of all the text in obj is selected."""

        length = AXText.get_character_count(obj)
        if not length:
            return False

        ranges = AXText.get_selected_ranges(obj)
        if not ranges:
            return False

        return ranges[0][0] == 0 and ranges[-1][1] == length

    @staticmethod
    def clear_all_selected_text(obj):
        """Attempts to clear the selected text."""

        for i in range(AXText._get_n_selections(obj)):
            AXText._remove_selection(obj, i)

    @staticmethod
    def get_selection_start_offset(obj):
        """Returns the leftmost offset of the selected text."""

        ranges = AXText.get_selected_ranges(obj)
        if ranges:
            return ranges[0][0]

        return -1

    @staticmethod
    def get_selection_end_offset(obj):
        """Returns the rightmost offset of the selected text."""

        ranges = AXText.get_selected_ranges(obj)
        if ranges:
            return ranges[-1][1]

        return -1

    @staticmethod
    def get_selected_ranges(obj):
        """Returns a list of (start_offset, end_offset) tuples reflecting the selected text."""

        count = AXText._get_n_selections(obj)
        if not count:
            return []

        selections = []
        for i in range(count):
            try:
                result = Atspi.Text.get_selection(obj, i)
            except Exception as error:
                msg = f"AXText: Exception in get_selected_ranges: {error}"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                break
            if 0 <= result.start_offset < result.end_offset:
                selections.append((result.start_offset, result.end_offset))

        tokens = ["AXText:", obj, f"reports selected ranges: {selections}"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return selections

    @staticmethod
    def get_selected_text(obj):
        """Returns the selected string, start, and end for obj."""

        selections = AXText.get_selected_ranges(obj)
        if not selections:
            return "", 0, 0

        strings = []
        start_offset = None
        end_offset = None
        for selection in sorted(set(selections)):
            strings.append(AXText.get_substring(obj, *selection))
            end_offset = selection[1]
            if start_offset is None:
                start_offset = selection[0]

        text = " ".join(strings)
        words = text.split()
        if len(text) > 10:
            debug_string = f"{' '.join(words[:5])} ... {' '.join(words[-5:])}"
        else:
            debug_string = text

        tokens = ["AXText: Selected text of", obj,
                  f"'{debug_string}' ({start_offset}-{end_offset})"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return text, start_offset, end_offset

    @staticmethod
    def _add_new_selection(obj, start_offset, end_offset):
        """Creates a new selection for the specified range in obj."""

        if not AXObject.supports_text(obj):
            return False

        try:
            result = Atspi.Text.add_selection(obj, start_offset, end_offset)
        except Exception as error:
            msg = f"AXText: Exception in _add_selection: {error}"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        return result

    @staticmethod
    def _update_existing_selection(obj, start_offset, end_offset, selection_number=0):
        """Modifies specified selection in obj to the specified range."""

        if not AXObject.supports_text(obj):
            return False

        try:
            result = Atspi.Text.set_selection(obj, selection_number, start_offset, end_offset)
        except Exception as error:
            msg = f"AXText: Exception in set_selected_text: {error}"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        return result

    @staticmethod
    def set_selected_text(obj, start_offset, end_offset):
        """Returns False if we definitely failed to set the selection. True cannot be trusted."""

        # TODO - JD: For now we always assume and operate on the first selection.
        # This preserves the original functionality prior to the refactor. But whether
        # that functionality is what it should be needs investigation.
        if AXText._get_n_selections(obj) > 0:
            result = AXText._update_existing_selection(obj, start_offset, end_offset)
        else:
            result = AXText._add_new_selection(obj, start_offset, end_offset)

        if result and debug.LEVEL_INFO >= debug.debugLevel:
            substring = AXText.get_substring(obj, start_offset, end_offset)
            selection = AXText.get_selected_text(obj)[0]
            if substring != selection:
                msg = "AXText: Substring and selected text do not match."
                debug.printMessage(debug.LEVEL_INFO, msg, True)

        return result

    @staticmethod
    def get_text_attributes_at_offset(obj, offset=None):
        """Returns a (dict, start, end) tuple for attributes at offset in obj."""

        if not AXObject.supports_text(obj):
            return {}, 0, 0

        if offset is None:
            offset = AXText.get_caret_offset(obj)

        try:
            result = Atspi.Text.get_attribute_run(obj, offset, include_defaults=True)
        except Exception as error:
            msg = f"AXText: Exception in get_text_attributes_at_offset: {error}"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return {}, 0, AXText.get_character_count(obj)

        tokens = ["AXText: Attributes for", obj, f"at offset {offset} : {result}"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return result[0] or {}, result[1] or 0, result[2] or AXText.get_character_count(obj)

    @staticmethod
    def get_all_text_attributes(obj, start_offset=0, end_offset=-1):
        """Returns a list of (start, end, attrs dict) tuples for obj."""

        if not AXObject.supports_text(obj):
            return []

        if end_offset == -1:
            end_offset = AXText.get_character_count(obj)

        tokens = ["AXText: Getting attributes for", obj, f"chars: {start_offset}-{end_offset}"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        rv = []
        offset = start_offset
        while offset < end_offset:
            attrs, start, end = AXText.get_text_attributes_at_offset(obj, offset)
            if start <= end:
                rv.append((max(start, offset), end, attrs))
            else:
                # TODO - JD: We're sometimes seeing this from WebKit, e.g. in Evo gitlab messages.
                msg = f"AXText: Start offset {start} > end offset {end}"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
            offset = max(end, offset + 1)

        msg = f"AXText: {len(rv)} attribute ranges found."
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        return rv

    @staticmethod
    def get_offset_at_point(obj, x, y):
        """Returns the character offset in obj at the specified point."""

        if not AXObject.supports_text(obj):
            return -1

        try:
            offset = Atspi.Text.get_offset_at_point(obj, x, y, Atspi.CoordType.WINDOW)
        except Exception as error:
            msg = f"AXText: Exception in get_offset_at_point: {error}"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return -1

        tokens = ["AXText: Offset in", obj, f"at {x}, {y} is {offset}"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return offset

    @staticmethod
    def get_character_rect(obj, offset=None):
        """Returns the Atspi rect of the character at the specified offset in obj."""

        if not AXObject.supports_text(obj):
            return Atspi.Rect()

        if offset is None:
            offset = AXText.get_caret_offset(obj)

        try:
            rect = Atspi.Text.get_character_extents(obj, offset, Atspi.CoordType.WINDOW)
        except Exception as error:
            msg = f"AXText: Exception in get_character_rect: {error}"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return Atspi.Rect()

        tokens = [f"AXText: Offset {offset} in", obj, "has rect", rect]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return rect

    @staticmethod
    def get_range_rect(obj, start, end):
        """Returns the Atspi rect of the string at the specified range in obj."""

        if not AXObject.supports_text(obj):
            return Atspi.Rect()

        try:
            rect = Atspi.Text.get_range_extents(obj, start, end, Atspi.CoordType.WINDOW)
        except Exception as error:
            tokens = ["AXText: Exception in get_range_rect for", obj, f":{ error}"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return Atspi.Rect()

        tokens = [f"AXText: Range {start}-{end} in", obj, "has rect", rect]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return rect

    @staticmethod
    def _rect_is_fully_contained_in(rect1, rect2):
        """Returns true if rect1 is fully contained in rect2"""

        return rect2.x <= rect1.x and rect2.y <= rect1.y \
            and rect2.x + rect2.width >= rect1.x + rect1.width \
            and rect2.y + rect2.height >= rect1.y + rect1.height

    @staticmethod
    def _line_comparison(line_rect, clip_rect):
        """Returns -1 (line above), 1 (line below), or 0 (line inside) clip_rect."""

        # https://gitlab.gnome.org/GNOME/gtk/-/issues/6419
        clip_rect.y = max(0, clip_rect.y)

        if line_rect.y + line_rect.height / 2 < clip_rect.y:
            return -1

        if line_rect.y + line_rect.height / 2 > clip_rect.y + clip_rect.height:
            return 1

        return 0

    @staticmethod
    def get_visible_lines(obj, clip_rect):
        """Returns a list of (string, start, end) for lines of obj inside clip_rect."""

        tokens = ["AXText: Getting visible lines for", obj, "inside", clip_rect]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        line, start, end = AXText.find_first_visible_line(obj, clip_rect)
        debug_string = line.replace("\n", "\\n")
        tokens = ["AXText: First visible line in", obj, f"is: '{debug_string}' ({start}-{end})"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        result = [(line, start, end)]
        offset = end
        for line, start, end in AXText.iter_line(obj, offset):
            line_rect = AXText.get_range_rect(obj, start, end)
            if AXText._line_comparison(line_rect, clip_rect) > 0:
                break
            result.append((line, start, end))

        line, start, end = result[-1]
        debug_string = line.replace("\n", "\\n")
        tokens = ["AXText: Last visible line in", obj, f"is: '{debug_string}' ({start}-{end})"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def find_first_visible_line(obj, clip_rect):
        """Returns the first (string, start, end) visible line of obj inside clip_rect."""

        result = "", 0, 0
        length = AXText.get_character_count(obj)
        low, high = 0, length
        while low < high:
            mid = (low + high) // 2
            line, start, end = AXText.get_line_at_offset(obj, mid)
            if start == 0:
                return line, start, end

            if start < 0:
                tokens = ["AXText: Treating invalid offset as above", clip_rect]
                debug.printTokens(debug.LEVEL_INFO, tokens, True)
                low = mid + 1
                continue

            result = line, start, end
            previous_line, previous_start, previous_end = AXText.get_line_at_offset(obj, start - 1)
            if previous_start <= 0 and previous_end <= 0:
                return result

            text_rect = AXText.get_range_rect(obj, start, end)
            if AXText._line_comparison(text_rect, clip_rect) < 0:
                low = mid + 1
                continue

            if AXText._line_comparison(text_rect, clip_rect) > 0:
                high = mid
                continue

            previous_rect = AXText.get_range_rect(obj, previous_start, previous_end)
            if AXText._line_comparison(previous_rect, clip_rect) != 0:
                return result

            result = previous_line, previous_start, previous_end
            high = mid

        return result

    @staticmethod
    def find_last_visible_line(obj, clip_rect):
        """Returns the last (string, start, end) visible line of obj inside clip_rect."""

        result = "", 0, 0
        length = AXText.get_character_count(obj)
        low, high = 0, length
        while low < high:
            mid = (low + high) // 2
            line, start, end = AXText.get_line_at_offset(obj, mid)
            if end >= length:
                return line, start, end

            if end <= 0:
                tokens = ["AXText: Treating invalid offset as below", clip_rect]
                debug.printTokens(debug.LEVEL_INFO, tokens, True)
                high = mid
                continue

            result = line, start, end
            next_line, next_start, next_end = AXText.get_line_at_offset(obj, end)
            if next_start <= 0 and next_end <= 0:
                return result

            text_rect = AXText.get_range_rect(obj, start, end)
            if AXText._line_comparison(text_rect, clip_rect) < 0:
                low = mid + 1
                continue

            if AXText._line_comparison(text_rect, clip_rect) > 0:
                high = mid
                continue

            next_rect = AXText.get_range_rect(obj, next_start, next_end)
            if AXText._line_comparison(next_rect, clip_rect) != 0:
                return result

            result = next_line, next_start, next_end
            low = mid + 1

        return result

    @staticmethod
    def is_word_misspelled(obj, offset=None):
        """Returns True if the text attributes indicate a spelling error."""

        attributes = AXText.get_text_attributes_at_offset(obj, offset)[0]
        if attributes.get("invalid") == "spelling":
            return True
        if attributes.get("text-spelling") == "misspelled":
            return True
        if attributes.get("underline") in ["error", "spelling"]:
            return True
        return False

    @staticmethod
    def is_eoc(character):
        """Returns True if character is an embedded object character (\ufffc)."""

        return character == "\ufffc"

    @staticmethod
    def character_at_offset_is_eoc(obj, offset):
        """Returns True if character in obj is an embedded object character (\ufffc)."""

        return AXText.is_eoc(AXText.get_character_at_offset(obj, offset))

    @staticmethod
    def is_whitespace_or_empty(obj):
        """Returns True if obj lacks text, or contains only whitespace."""

        if not AXObject.supports_text(obj):
            return True

        return not AXText.get_all_text(obj).strip()

    @staticmethod
    def scroll_substring_to_point(obj, x, y, start_offset, end_offset):
        """Attempts to scroll obj to the specified point."""

        length = AXText.get_character_count(obj)
        if not length:
            return False

        if start_offset is None:
            start_offset = 0
        if end_offset is None:
            end_offset = length - 1

        try:
            result = Atspi.Text.scroll_substring_to_point(
                obj, start_offset, end_offset, Atspi.CoordType.WINDOW, x, y)
        except Exception as error:
            msg = f"AXText: Exception in scroll_substring_to_point: {error}"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        tokens = ["AXText: Scrolled", obj, f"substring ({start_offset}-{end_offset}) to",
                  f"{x}, {y}: {result}"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def scroll_substring_to_location(obj, location, start_offset, end_offset):
        """Attempts to scroll the substring to the specified Atspi.ScrollType location."""

        length = AXText.get_character_count(obj)
        if not length:
            return False

        if start_offset is None:
            start_offset = 0
        if end_offset is None:
            end_offset = length - 1

        try:
            result = Atspi.Text.scroll_substring_to(obj, start_offset, end_offset, location)
        except Exception as error:
            msg = f"AXText: Exception in scroll_substring_to_location: {error}"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        tokens = ["AXText: Scrolled", obj, f"substring ({start_offset}-{end_offset}) to",
                  location, f": {result}"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return result
