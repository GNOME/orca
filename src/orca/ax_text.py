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

# pylint: disable=too-many-public-methods
# pylint: disable=too-many-lines

"""Utilities for obtaining information about accessible text."""

from __future__ import annotations

import enum
import locale
import re

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi, GLib

from . import colornames, debug, messages, text_attribute_names
from .ax_object import AXObject
from .ax_utilities_role import AXUtilitiesRole
from .ax_utilities_state import AXUtilitiesState


class AXTextAttribute(enum.Enum):
    """Enum representing an accessible text attribute."""

    # Note: Anything added here should also have an entry in text_attribute_names.py.
    # The tuple is (non-localized name, enable by default).
    BG_COLOR = ("bg-color", True)
    BG_FULL_HEIGHT = ("bg-full-height", False)
    BG_STIPPLE = ("bg-stipple", False)
    DIRECTION = ("direction", False)
    EDITABLE = ("editable", False)
    FAMILY_NAME = ("family-name", True)
    FG_COLOR = ("fg-color", True)
    FG_STIPPLE = ("fg-stipple", False)
    FONT_EFFECT = ("font-effect", True)
    INDENT = ("indent", True)
    INVALID = ("invalid", True)
    INVISIBLE = ("invisible", False)
    JUSTIFICATION = ("justification", True)
    LANGUAGE = ("language", False)
    LEFT_MARGIN = ("left-margin", False)
    LINE_HEIGHT = ("line-height", False)
    MARK = ("mark", True)
    PARAGRAPH_STYLE = ("paragraph-style", True)
    PIXELS_ABOVE_LINES = ("pixels-above-lines", False)
    PIXELS_BELOW_LINES = ("pixels-below-lines", False)
    PIXELS_INSIDE_WRAP = ("pixels-inside-wrap", False)
    RIGHT_MARGIN = ("right-margin", False)
    RISE = ("rise", False)
    SCALE = ("scale", False)
    SIZE = ("size", True)
    STRETCH = ("stretch", False)
    STRIKETHROUGH = ("strikethrough", True)
    STYLE = ("style", True)
    TEXT_DECORATION = ("text-decoration", True)
    TEXT_POSITION = ("text-position", False)
    TEXT_ROTATION = ("text-rotation", True)
    TEXT_SHADOW = ("text-shadow", False)
    UNDERLINE = ("underline", True)
    VARIANT = ("variant", False)
    VERTICAL_ALIGN = ("vertical-align", False)
    WEIGHT = ("weight", True)
    WRAP_MODE = ("wrap-mode", False)
    WRITING_MODE = ("writing-mode", False)

    @classmethod
    def from_string(cls, string: str) -> AXTextAttribute | None:
        """Returns the AXTextAttribute for the specified string."""

        for attribute in cls:
            if attribute.get_attribute_name() == string:
                return attribute

        return None

    @classmethod
    def from_localized_string(cls, string: str) -> AXTextAttribute | None:
        """Returns the AXTextAttribute for the specified localized string."""

        for attribute in cls:
            if attribute.get_localized_name() == string:
                return attribute

        return None

    def get_attribute_name(self) -> str:
        """Returns the non-localized name of the attribute."""

        return self.value[0]

    def get_localized_name(self) -> str:
        """Returns the localized name of the attribute."""

        name = self.value[0]
        return text_attribute_names.attribute_names.get(name, name)

    def get_localized_value(self, value) -> str:
        """Returns the localized value of the attribute."""

        if value is None:
            return ""

        if value.endswith("px"):
            value = value.split("px")[0]
            if locale.localeconv()["decimal_point"] in value:
                return messages.pixel_count(float(value))
            return messages.pixel_count(int(value))

        if self in [AXTextAttribute.BG_COLOR, AXTextAttribute.FG_COLOR]:
            return colornames.get_presentable_color_name(value)

        # TODO - JD: Is this still needed?
        value = value.replace("-moz", "")

        # TODO - JD: Are these still needed?
        if self == AXTextAttribute.JUSTIFICATION:
            value = value.replace("justify", "fill")
        elif self == AXTextAttribute.FAMILY_NAME:
            value = value.split(",")[0].strip().strip('"')

        return text_attribute_names.attribute_values.get(value, value)

    def should_present_by_default(self) -> bool:
        """Returns True if the attribute should be presented by default."""

        return self.value[1]

    def value_is_default(self, value) -> bool:
        """Returns True if value should be treated as the default value for this attribute."""

        null_values = ["0", "0mm", "0px", "none", "false", "normal", "", None]
        if value in null_values:
            return True

        if self == AXTextAttribute.SCALE:
            return float(value) == 1.0
        if self == AXTextAttribute.TEXT_POSITION:
            return value == "baseline"
        if self == AXTextAttribute.WEIGHT:
            return value == "400"
        if self == AXTextAttribute.LANGUAGE:
            loc = locale.getlocale()[0] or ""
            return value == loc[:2]

        return False


class AXText:
    """Utilities for obtaining information about accessible text."""

    @staticmethod
    def get_character_at_offset(
        obj: Atspi.Accessible,
        offset: int | None = None,
    ) -> tuple[str, int, int]:
        """Returns the (character, start, end) for the current or specified offset."""

        length = AXText.get_character_count(obj)
        if not length:
            return "", 0, 0

        if offset is None:
            offset = AXText.get_caret_offset(obj)

        if not 0 <= offset <= length:
            msg = f"WARNING: Offset {offset} is not valid. No character can be provided."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return "", 0, 0

        try:
            result = Atspi.Text.get_string_at_offset(obj, offset, Atspi.TextGranularity.CHAR)
        except GLib.GError as error:
            msg = f"AXText: Exception in get_character_at_offset: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return "", 0, 0

        if result is None:
            tokens = ["AXText: get_string_at_offset (char) failed for", obj, f"at {offset}."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return "", 0, 0

        debug_string = result.content.replace("\n", "\\n")
        tokens = [
            f"AXText: Character at offset {offset} in",
            obj,
            f"'{debug_string}' ({result.start_offset}-{result.end_offset})",
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result.content, result.start_offset, result.end_offset

    @staticmethod
    def get_word_at_offset(
        obj: Atspi.Accessible,
        offset: int | None = None,
    ) -> tuple[str, int, int]:
        """Returns the (word, start, end) for the current or specified offset."""

        length = AXText.get_character_count(obj)
        if not length:
            return "", 0, 0

        if offset is None:
            offset = AXText.get_caret_offset(obj)

        offset = min(max(0, offset), length - 1)
        try:
            result = Atspi.Text.get_string_at_offset(obj, offset, Atspi.TextGranularity.WORD)
        except GLib.GError as error:
            msg = f"AXText: Exception in get_word_at_offset: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return "", 0, 0

        if result is None:
            tokens = ["AXText: get_string_at_offset (word) failed for", obj, f"at {offset}."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return "", 0, 0

        tokens = [
            f"AXText: Word at offset {offset} in",
            obj,
            f"'{result.content}' ({result.start_offset}-{result.end_offset})",
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result.content, result.start_offset, result.end_offset

    @staticmethod
    def get_line_at_offset(
        obj: Atspi.Accessible,
        offset: int | None = None,
    ) -> tuple[str, int, int]:
        """Returns the (line, start, end) for the current or specified offset."""

        length = AXText.get_character_count(obj)
        if not length:
            return "", 0, 0

        if offset is None:
            offset = AXText.get_caret_offset(obj)

        # Don't adjust the length in multiline text because we want to say "blank" at the end.
        # This may or may not be sufficient. GTK3 seems to give us the correct, empty line. But
        # (at least) Chromium does not. See comment below.
        if (
            not AXUtilitiesState.is_multi_line(obj)
            and not AXUtilitiesRole.is_paragraph(obj)
            and not AXUtilitiesRole.is_section(obj)
        ):
            offset = min(max(0, offset), length - 1)
        else:
            offset = max(0, offset)

        try:
            result = Atspi.Text.get_string_at_offset(obj, offset, Atspi.TextGranularity.LINE)
        except GLib.GError as error:
            msg = f"AXText: Exception in get_line_at_offset: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return "", 0, 0

        if result is None:
            tokens = ["AXText: get_string_at_offset (line) failed for", obj, f"at {offset}."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return "", 0, 0

        # Try again, e.g. Chromium returns "", -1, -1.
        if result.start_offset == result.end_offset == -1 and offset == length:
            offset -= 1
            result = Atspi.Text.get_string_at_offset(obj, offset, Atspi.TextGranularity.LINE)

        debug_string = result.content.replace("\n", "\\n")
        tokens = [
            f"AXText: Line at offset {offset} in",
            obj,
            f"'{debug_string}' ({result.start_offset}-{result.end_offset})",
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if 0 <= offset < result.start_offset:
            offset -= 1
            msg = f"ERROR: Start offset is greater than offset. Trying with offset {offset}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            result = Atspi.Text.get_string_at_offset(obj, offset, Atspi.TextGranularity.LINE)

            debug_string = result.content.replace("\n", "\\n")
            tokens = [
                f"AXText: Line at offset {offset} in",
                obj,
                f"'{debug_string}' ({result.start_offset}-{result.end_offset})",
            ]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        return result.content, result.start_offset, result.end_offset

    @staticmethod
    def _find_sentence_boundaries(text: str) -> list[int]:
        """Returns the offsets in text that should be treated as sentence beginnings."""

        if not text:
            return []

        boundaries = [0]
        pattern = r"[.!?]+(?=\s|\ufffc|$)"
        for match in re.finditer(pattern, text):
            end_pos = match.end()
            # Skip whitespace to find start of next sentence. Do not skip embedded object
            # characters since they represent child objects that must be traversed.
            while end_pos < len(text) and text[end_pos].isspace():
                end_pos += 1
            # Only add boundary if we haven't reached the end and it's not a duplicate.
            if end_pos < len(text) and end_pos not in boundaries:
                boundaries.append(end_pos)

        if boundaries[-1] != len(text):
            boundaries.append(len(text))

        return boundaries

    @staticmethod
    def _get_sentence_at_offset_fallback(
        obj: Atspi.Accessible,
        offset: int | None = None,
    ) -> tuple[str, int, int]:
        """Fallback sentence detection for broken implementations."""

        if offset is None:
            offset = AXText.get_caret_offset(obj)

        text = AXText.get_all_text(obj)
        if not text or offset < 0 or offset >= len(text):
            return "", 0, 0

        fallback_text, fallback_start, fallback_end = text, 0, len(text)
        boundaries = AXText._find_sentence_boundaries(text)
        for i in range(len(boundaries) - 1):
            start, end = boundaries[i], boundaries[i + 1]
            if start <= offset < end:
                fallback_text, fallback_start, fallback_end = text[start:end], start, end
                break

        tokens = [
            "AXText: Fallback sentence in",
            obj,
            f" at offset {offset}: '{fallback_text}' ({fallback_start}-{fallback_end})",
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return fallback_text, fallback_start, fallback_end

    @staticmethod
    def get_sentence_at_offset(
        obj: Atspi.Accessible,
        offset: int | None = None,
    ) -> tuple[str, int, int]:
        """Returns the (sentence, start, end) for the current or specified offset."""

        length = AXText.get_character_count(obj)
        if not length:
            return "", 0, 0

        if offset is None:
            offset = AXText.get_caret_offset(obj)

        offset = min(max(0, offset), length - 1)
        try:
            result = Atspi.Text.get_string_at_offset(obj, offset, Atspi.TextGranularity.SENTENCE)
        except GLib.GError as error:
            msg = f"AXText: Exception in get_sentence_at_offset: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return AXText._get_sentence_at_offset_fallback(obj, offset)

        if result is None:
            tokens = ["AXText: get_string_at_offset (sentence) failed for", obj, f"at {offset}."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return "", 0, 0

        if result.start_offset == result.end_offset == -1 or not result.content:
            return AXText._get_sentence_at_offset_fallback(obj, offset)

        if (
            result.start_offset == result.end_offset
            and result.start_offset in [0, -1]
            and not result.content
        ):
            return AXText._get_sentence_at_offset_fallback(obj, offset)

        tokens = [
            f"AXText: Sentence at offset {offset} in",
            obj,
            f"'{result.content}' ({result.start_offset}-{result.end_offset})",
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result.content, result.start_offset, result.end_offset

    @staticmethod
    def get_paragraph_at_offset(
        obj: Atspi.Accessible,
        offset: int | None = None,
    ) -> tuple[str, int, int]:
        """Returns the (paragraph, start, end) for the current or specified offset."""

        length = AXText.get_character_count(obj)
        if not length:
            return "", 0, 0

        if offset is None:
            offset = AXText.get_caret_offset(obj)

        offset = min(max(0, offset), length - 1)
        try:
            result = Atspi.Text.get_string_at_offset(obj, offset, Atspi.TextGranularity.PARAGRAPH)
        except GLib.GError as error:
            msg = f"AXText: Exception in get_paragraph_at_offset: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return "", 0, 0

        if result is None:
            tokens = ["AXText: get_string_at_offset (paragraph) failed for", obj, f"at {offset}."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return "", 0, 0

        tokens = [
            f"AXText: Paragraph at offset {offset} in",
            obj,
            f"'{result.content}' ({result.start_offset}-{result.end_offset})",
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result.content, result.start_offset, result.end_offset

    @staticmethod
    def get_character_count(obj: Atspi.Accessible) -> int:
        """Returns the character count of obj."""

        if not AXObject.supports_text(obj):
            return 0

        try:
            count = Atspi.Text.get_character_count(obj)
        except GLib.GError as error:
            msg = f"AXText: Exception in get_character_count: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return 0

        tokens = ["AXText:", obj, f"reports {count} characters."]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return count

    @staticmethod
    def get_caret_offset(obj: Atspi.Accessible) -> int:
        """Returns the caret offset of obj."""

        if not AXObject.supports_text(obj):
            return -1

        try:
            offset = Atspi.Text.get_caret_offset(obj)
        except GLib.GError as error:
            msg = f"AXText: Exception in get_caret_offset: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return -1

        tokens = ["AXText:", obj, f"reports caret offset of {offset}."]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return offset

    @staticmethod
    def set_caret_offset(obj: Atspi.Accessible, offset: int) -> bool:
        """Returns False if we definitely failed to set the offset. True cannot be trusted."""

        if not AXObject.supports_text(obj):
            return False

        try:
            result = Atspi.Text.set_caret_offset(obj, offset)
        except GLib.GError as error:
            msg = f"AXText: Exception in set_caret_offset: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        tokens = [f"AXText: Reported result of setting offset to {offset} in", obj, f": {result}"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def get_substring(obj: Atspi.Accessible, start_offset: int, end_offset: int) -> str:
        """Returns the text of obj within the specified offsets."""

        if not AXObject.supports_text(obj):
            return ""

        if end_offset == -1:
            end_offset = AXText.get_character_count(obj)

        try:
            result = Atspi.Text.get_text(obj, start_offset, end_offset)
        except GLib.GError as error:
            msg = f"AXText: Exception in get_substring: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return ""

        debug_string = result.replace("\n", "\\n")
        tokens = ["AXText: Text of", obj, f"({start_offset}-{end_offset}): '{debug_string}'"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def get_all_text(obj: Atspi.Accessible) -> str:
        """Returns the text content of obj."""

        length = AXText.get_character_count(obj)
        if not length:
            return ""

        try:
            result = Atspi.Text.get_text(obj, 0, length)
        except GLib.GError as error:
            msg = f"AXText: Exception in get_all_text: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return ""

        words = result.split()
        if len(words) > 20:
            debug_string = f"{' '.join(words[:5])} ... {' '.join(words[-5:])}"
        else:
            debug_string = result

        debug_string = debug_string.replace("\n", "\\n")
        tokens = ["AXText: Text of", obj, f"'{debug_string}'"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def get_n_selections(obj: Atspi.Accessible) -> int:
        """Returns the number of reported selected substrings in obj."""

        if not AXObject.supports_text(obj):
            return 0

        try:
            result = Atspi.Text.get_n_selections(obj)
        except GLib.GError as error:
            msg = f"AXText: Exception in get_n_selections: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return 0

        tokens = ["AXText:", obj, f"reports {result} selection(s)."]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def remove_selection(obj: Atspi.Accessible, selection_number: int) -> None:
        """Attempts to remove the specified selection."""

        if not AXObject.supports_text(obj):
            return

        try:
            Atspi.Text.remove_selection(obj, selection_number)
        except GLib.GError as error:
            msg = f"AXText: Exception in remove_selection: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

    @staticmethod
    def get_selected_ranges(obj: Atspi.Accessible) -> list[tuple[int, int]]:
        """Returns a list of (start_offset, end_offset) tuples reflecting the selected text."""

        count = AXText.get_n_selections(obj)
        if not count:
            return []

        selections = []
        for i in range(count):
            try:
                result = Atspi.Text.get_selection(obj, i)
            except GLib.GError as error:
                msg = f"AXText: Exception in get_selected_ranges: {error}"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                break
            if 0 <= result.start_offset < result.end_offset:
                selections.append((result.start_offset, result.end_offset))

        tokens = ["AXText:", obj, f"reports selected ranges: {selections}"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return selections

    @staticmethod
    def add_new_selection(obj: Atspi.Accessible, start_offset: int, end_offset: int) -> bool:
        """Creates a new selection for the specified range in obj."""

        if not AXObject.supports_text(obj):
            return False

        try:
            result = Atspi.Text.add_selection(obj, start_offset, end_offset)
        except GLib.GError as error:
            msg = f"AXText: Exception in add_new_selection: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        return result

    @staticmethod
    def update_existing_selection(
        obj: Atspi.Accessible,
        start_offset: int,
        end_offset: int,
        selection_number: int = 0,
    ) -> bool:
        """Modifies specified selection in obj to the specified range."""

        if not AXObject.supports_text(obj):
            return False

        try:
            result = Atspi.Text.set_selection(obj, selection_number, start_offset, end_offset)
        except GLib.GError as error:
            msg = f"AXText: Exception in update_existing_selection: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        return result

    # TODO - JD: This should be converted to return AXTextAttribute values.
    @staticmethod
    def get_text_attributes_at_offset(
        obj: Atspi.Accessible,
        offset: int | None = None,
    ) -> tuple[dict[str, str], int, int]:
        """Returns a (dict, start, end) tuple for attributes at offset in obj."""

        if not AXObject.supports_text(obj):
            return {}, 0, 0

        if offset is None:
            offset = AXText.get_caret_offset(obj)

        try:
            result = Atspi.Text.get_attribute_run(obj, offset, include_defaults=True)
        except GLib.GError as error:
            msg = f"AXText: Exception in get_text_attributes_at_offset: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return {}, 0, AXText.get_character_count(obj)

        if result is None:
            tokens = ["AXText: get_attribute_run failed for", obj, f"at offset {offset}."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return {}, 0, AXText.get_character_count(obj)

        tokens = ["AXText: Attributes for", obj, f"at offset {offset} : {result}"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        # Adjust for web browsers that report indentation and justification at object attributes
        # rather than text attributes.
        obj_attributes = AXObject.get_attributes_dict(obj, False)
        if not result[0].get("justification"):
            alternative = obj_attributes.get("text-align")
            if alternative:
                result[0]["justification"] = alternative
        if not result[0].get("indent"):
            alternative = obj_attributes.get("text-indent")
            if alternative:
                result[0]["indent"] = alternative

        return result[0] or {}, result[1] or 0, result[2] or AXText.get_character_count(obj)

    @staticmethod
    def get_offset_at_point(obj: Atspi.Accessible, x: int, y: int) -> int:
        """Returns the character offset in obj at the specified point."""

        if not AXObject.supports_text(obj):
            return -1

        try:
            offset = Atspi.Text.get_offset_at_point(obj, x, y, Atspi.CoordType.WINDOW)
        except GLib.GError as error:
            msg = f"AXText: Exception in get_offset_at_point: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return -1

        tokens = ["AXText: Offset in", obj, f"at {x}, {y} is {offset}"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return offset

    @staticmethod
    def get_character_rect(obj: Atspi.Accessible, offset: int | None = None) -> Atspi.Rect:
        """Returns the Atspi rect of the character at the specified offset in obj."""

        if not AXObject.supports_text(obj):
            return Atspi.Rect()

        if offset is None:
            offset = AXText.get_caret_offset(obj)

        try:
            rect = Atspi.Text.get_character_extents(obj, offset, Atspi.CoordType.WINDOW)
        except GLib.GError as error:
            msg = f"AXText: Exception in get_character_rect: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return Atspi.Rect()

        tokens = [f"AXText: Offset {offset} in", obj, "has rect", rect]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return rect

    @staticmethod
    def get_range_rect(obj: Atspi.Accessible, start: int, end: int) -> Atspi.Rect:
        """Returns the Atspi rect of the string at the specified range in obj."""

        if not AXObject.supports_text(obj):
            return Atspi.Rect()

        if end <= 0:
            end = AXText.get_character_count(obj)

        try:
            rect = Atspi.Text.get_range_extents(obj, start, end, Atspi.CoordType.WINDOW)
        except GLib.GError as error:
            msg = f"AXText: Exception in get_range_rect: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return Atspi.Rect()

        tokens = [f"AXText: Range {start}-{end} in", obj, "has rect", rect]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return rect

    @staticmethod
    def scroll_substring_to_point(
        obj: Atspi.Accessible,
        x: int,
        y: int,
        start_offset: int | None = None,
        end_offset: int | None = None,
    ) -> bool:
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
                obj,
                start_offset,
                end_offset,
                Atspi.CoordType.WINDOW,
                x,
                y,
            )
        except GLib.GError as error:
            msg = f"AXText: Exception in scroll_substring_to_point: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        tokens = [
            "AXText: Scrolled",
            obj,
            f"substring ({start_offset}-{end_offset}) to",
            f"{x}, {y}: {result}",
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def scroll_substring_to_location(
        obj: Atspi.Accessible,
        location: Atspi.ScrollType,
        start_offset: int | None = None,
        end_offset: int | None = None,
    ) -> bool:
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
        except GLib.GError as error:
            msg = f"AXText: Exception in scroll_substring_to_location: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        tokens = [
            "AXText: Scrolled",
            obj,
            f"substring ({start_offset}-{end_offset}) to",
            location,
            f": {result}",
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result
