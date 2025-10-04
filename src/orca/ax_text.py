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

# pylint: disable=wrong-import-position
# pylint: disable=too-many-locals
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-branches
# pylint: disable=too-many-lines

"""Utilities for obtaining information about accessible text."""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2024 Igalia, S.L." \
                "Copyright (c) 2024 GNOME Foundation Inc."
__license__   = "LGPL"

import enum
import locale
import re
from typing import Generator

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi
from gi.repository import GLib

from . import colornames
from . import debug
from . import messages
from . import text_attribute_names
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
    def from_string(cls, string: str) -> "AXTextAttribute" | None:
        """Returns the AXTextAttribute for the specified string."""

        for attribute in cls:
            if attribute.get_attribute_name() == string:
                return attribute

        return None

    @classmethod
    def from_localized_string(cls, string: str) -> "AXTextAttribute" | None:
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

    CACHED_TEXT_SELECTION: dict[int, tuple[str, int, int]] = {}

    @staticmethod
    def get_character_at_offset(
        obj: Atspi.Accessible,
        offset: int | None = None
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

        debug_string = result.content.replace("\n", "\\n")
        tokens = [f"AXText: Character at offset {offset} in", obj,
                  f"'{debug_string}' ({result.start_offset}-{result.end_offset})"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result.content, result.start_offset, result.end_offset

    @staticmethod
    def get_character_at_point(obj: Atspi.Accessible, x: int, y: int) -> tuple[str, int, int]:
        """Returns the (character, start, end) at the specified point."""

        offset = AXText.get_offset_at_point(obj, x, y)
        if not 0 <= offset < AXText.get_character_count(obj):
            return "", 0, 0

        return AXText.get_character_at_offset(obj, offset)

    @staticmethod
    def get_next_character(
        obj: Atspi.Accessible,
        offset: int | None = None
    ) -> tuple[str, int, int]:
        """Returns the next (character, start, end) for the current or specified offset."""

        if offset is None:
            offset = AXText.get_caret_offset(obj)

        current_character, start, end = AXText.get_character_at_offset(obj, offset)
        if not current_character:
            return "", 0, 0

        length = AXText.get_character_count(obj)
        next_offset = max(end, offset + 1)

        while next_offset < length:
            next_character, next_start, next_end = AXText.get_character_at_offset(obj, next_offset)
            if (next_character, next_start, next_end) != (current_character, start, end):
                return next_character, next_start, next_end
            next_offset += 1

        return "", 0, 0

    @staticmethod
    def get_previous_character(
        obj: Atspi.Accessible,
        offset: int | None = None
    ) -> tuple[str, int, int]:
        """Returns the previous (character, start, end) for the current or specified offset."""

        if offset is None:
            offset = AXText.get_caret_offset(obj)

        current_character, start, end = AXText.get_character_at_offset(obj, offset)
        if not current_character:
            return "", 0, 0

        if start <= 0:
            return "", 0, 0

        prev_offset = start - 1

        while prev_offset >= 0:
            prev_character, prev_start, prev_end = AXText.get_character_at_offset(obj, prev_offset)
            if (prev_character, prev_start, prev_end) != (current_character, start, end):
                return prev_character, prev_start, prev_end
            prev_offset -= 1

        return "", 0, 0

    @staticmethod
    def iter_character(
        obj: Atspi.Accessible,
        offset: int | None = None
    ) -> Generator[tuple[str, int, int], None, None]:
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
    def get_word_at_offset(
        obj: Atspi.Accessible,
        offset: int | None = None
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

        tokens = [f"AXText: Word at offset {offset} in", obj,
                  f"'{result.content}' ({result.start_offset}-{result.end_offset})"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result.content, result.start_offset, result.end_offset

    @staticmethod
    def get_word_at_point(obj: Atspi.Accessible, x: int, y: int) -> tuple[str, int, int]:
        """Returns the (word, start, end) at the specified point."""

        offset = AXText.get_offset_at_point(obj, x, y)
        if not 0 <= offset < AXText.get_character_count(obj):
            return "", 0, 0

        return AXText.get_word_at_offset(obj, offset)

    @staticmethod
    def get_next_word(
        obj: Atspi.Accessible,
        offset: int | None = None
    ) -> tuple[str, int, int]:
        """Returns the next (word, start, end) for the current or specified offset."""

        if offset is None:
            offset = AXText.get_caret_offset(obj)

        current_word, start, end = AXText.get_word_at_offset(obj, offset)
        if not current_word:
            return "", 0, 0

        length = AXText.get_character_count(obj)
        next_offset = max(end, offset + 1)

        while next_offset < length:
            next_word, next_start, next_end = AXText.get_word_at_offset(obj, next_offset)
            if (next_word, next_start, next_end) != (current_word, start, end):
                return next_word, next_start, next_end
            next_offset += 1

        return "", 0, 0

    @staticmethod
    def get_previous_word(
        obj: Atspi.Accessible,
        offset: int | None = None
    ) -> tuple[str, int, int]:
        """Returns the previous (word, start, end) for the current or specified offset."""

        if offset is None:
            offset = AXText.get_caret_offset(obj)

        current_word, start, end = AXText.get_word_at_offset(obj, offset)
        if not current_word:
            return "", 0, 0

        if start <= 0:
            return "", 0, 0

        prev_offset = start - 1

        while prev_offset >= 0:
            prev_word, prev_start, prev_end = AXText.get_word_at_offset(obj, prev_offset)
            if (prev_word, prev_start, prev_end) != (current_word, start, end):
                return prev_word, prev_start, prev_end
            prev_offset -= 1

        return "", 0, 0

    @staticmethod
    def iter_word(
        obj: Atspi.Accessible,
        offset: int | None = None
    ) -> Generator[tuple[str, int, int], None, None]:
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
    def get_line_at_offset(
        obj: Atspi.Accessible,
        offset: int | None = None
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
        if not AXUtilitiesState.is_multi_line(obj) \
           and not AXUtilitiesRole.is_paragraph(obj) and not AXUtilitiesRole.is_section(obj):
            offset = min(max(0, offset), length - 1)
        else:
            offset = max(0, offset)

        try:
            result = Atspi.Text.get_string_at_offset(obj, offset, Atspi.TextGranularity.LINE)
        except GLib.GError as error:
            msg = f"AXText: Exception in get_line_at_offset: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return "", 0, 0

        # Try again, e.g. Chromium returns "", -1, -1.
        if result.start_offset == result.end_offset == -1 and offset == length:
            offset -= 1
            result = Atspi.Text.get_string_at_offset(obj, offset, Atspi.TextGranularity.LINE)

        debug_string = result.content.replace("\n", "\\n")
        tokens = [f"AXText: Line at offset {offset} in", obj,
                  f"'{debug_string}' ({result.start_offset}-{result.end_offset})"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if 0 <= offset < result.start_offset:
            offset -= 1
            msg = f"ERROR: Start offset is greater than offset. Trying with offset {offset}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            result = Atspi.Text.get_string_at_offset(obj, offset, Atspi.TextGranularity.LINE)

            debug_string = result.content.replace("\n", "\\n")
            tokens = [f"AXText: Line at offset {offset} in", obj,
                    f"'{debug_string}' ({result.start_offset}-{result.end_offset})"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        return result.content, result.start_offset, result.end_offset

    @staticmethod
    def get_line_at_point(obj: Atspi.Accessible, x: int, y: int) -> tuple[str, int, int]:
        """Returns the (line, start, end) at the specified point."""

        offset = AXText.get_offset_at_point(obj, x, y)
        if not 0 <= offset < AXText.get_character_count(obj):
            return "", 0, 0

        return AXText.get_line_at_offset(obj, offset)

    @staticmethod
    def get_next_line(
        obj: Atspi.Accessible,
        offset: int | None = None
    ) -> tuple[str, int, int]:
        """Returns the next (line, start, end) for the current or specified offset."""

        if offset is None:
            offset = AXText.get_caret_offset(obj)

        current_line, start, end = AXText.get_line_at_offset(obj, offset)
        if not current_line:
            return "", 0, 0

        length = AXText.get_character_count(obj)
        next_offset = max(end, offset + 1)

        while next_offset < length:
            next_line, next_start, next_end = AXText.get_line_at_offset(obj, next_offset)
            if (next_line, next_start, next_end) != (current_line, start, end):
                return next_line, next_start, next_end
            next_offset += 1

        return "", 0, 0

    @staticmethod
    def get_previous_line(
        obj: Atspi.Accessible,
        offset: int | None = None
    ) -> tuple[str, int, int]:
        """Returns the previous (line, start, end) for the current or specified offset."""

        if offset is None:
            offset = AXText.get_caret_offset(obj)

        current_line, start, end = AXText.get_line_at_offset(obj, offset)
        if not current_line and offset == AXText.get_character_count(obj):
            current_line, start, end = AXText.get_line_at_offset(obj, offset - 1)
            if current_line.endswith("\n"):
                start = offset - 1

        if not current_line or start <= 0:
            return "", 0, 0

        prev_offset = start - 1

        while prev_offset >= 0:
            prev_line, prev_start, prev_end = AXText.get_line_at_offset(obj, prev_offset)
            if (prev_line, prev_start, prev_end) != (current_line, start, end):
                return prev_line, prev_start, prev_end
            prev_offset -= 1

        return "", 0, 0

    @staticmethod
    def iter_line(
        obj: Atspi.Accessible,
        offset: int | None = None
    ) -> Generator[tuple[str, int, int], None, None]:
        """Generator to iterate by line in obj starting with the line at offset."""

        line, start, end = AXText.get_line_at_offset(obj, offset)
        if not line:
            return

        # If the caller provides an offset positioned at the end boundary of the
        # current line (e.g. start iteration from the previous line's end), some
        # implementations of Atspi return the same line again for that offset.
        # To avoid yielding duplicates (e.g. in get_visible_lines()), only yield
        # the current line when the offset points inside it; otherwise start with
        # the next distinct line.
        if offset is None or offset < end:
            yield line, start, end
        current_start = start

        while True:
            next_line, next_start, next_end = AXText.get_next_line(obj, current_start)
            if not next_line or next_start <= current_start:
                break
            yield next_line, next_start, next_end
            current_start = next_start

    @staticmethod
    def _find_sentence_boundaries(text: str) -> list[int]:
        """Returns the offsets in text that should be treated as sentence beginnings."""

        if not text:
            return []

        boundaries = [0]
        pattern = r"[.!?]+(?=\s|\ufffc|$)"
        for match in re.finditer(pattern, text):
            end_pos = match.end()
            # Skip whitespace and embedded objects to find start of next sentence.
            while end_pos < len(text) and (text[end_pos].isspace() or text[end_pos] == "\ufffc"):
                end_pos += 1
            # Only add boundary if we haven't reached the end and it's not a duplicate.
            if end_pos < len(text) and end_pos not in boundaries:
                boundaries.append(end_pos)

        if boundaries[-1] != len(text):
            boundaries.append(len(text))

        return boundaries

    @staticmethod
    def has_sentence_ending(text: str) -> bool:
        """Check if text contains a sentence ending."""

        return bool(text and re.search(r"\S[.!?]+(\s|\ufffc|$)", text))

    @staticmethod
    def _get_sentence_at_offset_fallback(
        obj: Atspi.Accessible,
        offset: int | None = None
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

        tokens = ["AXText: Fallback sentence in", obj,
                  f" at offset {offset}: '{fallback_text}' ({fallback_start}-{fallback_end})"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return fallback_text, fallback_start, fallback_end

    @staticmethod
    def get_sentence_at_offset(
        obj: Atspi.Accessible,
        offset: int | None = None
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

        if result.start_offset == result.end_offset == -1 or not result.content:
            return AXText._get_sentence_at_offset_fallback(obj, offset)

        if (result.start_offset == result.end_offset and
            result.start_offset in [0, -1] and not result.content):
            return AXText._get_sentence_at_offset_fallback(obj, offset)

        tokens = [f"AXText: Sentence at offset {offset} in", obj,
                  f"'{result.content}' ({result.start_offset}-{result.end_offset})"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result.content, result.start_offset, result.end_offset

    @staticmethod
    def get_sentence_at_point(obj: Atspi.Accessible, x: int, y: int) -> tuple[str, int, int]:
        """Returns the (sentence, start, end) at the specified point."""

        offset = AXText.get_offset_at_point(obj, x, y)
        if not 0 <= offset < AXText.get_character_count(obj):
            return "", 0, 0

        return AXText.get_sentence_at_offset(obj, offset)

    @staticmethod
    def get_next_sentence(
        obj: Atspi.Accessible,
        offset: int | None = None
    ) -> tuple[str, int, int]:
        """Returns the next (sentence, start, end) for the current or specified offset."""

        if offset is None:
            offset = AXText.get_caret_offset(obj)

        current_sentence, start, end = AXText.get_sentence_at_offset(obj, offset)
        if not current_sentence:
            return "", 0, 0

        length = AXText.get_character_count(obj)
        next_offset = max(end, offset + 1)

        while next_offset < length:
            next_sentence, next_start, next_end = AXText.get_sentence_at_offset(obj, next_offset)
            if (next_sentence, next_start, next_end) != (current_sentence, start, end):
                return next_sentence, next_start, next_end
            next_offset += 1

        return "", 0, 0

    @staticmethod
    def get_previous_sentence(
        obj: Atspi.Accessible,
        offset: int | None = None
    ) -> tuple[str, int, int]:
        """Returns the previous (sentence, start, end) for the current or specified offset."""

        if offset is None:
            offset = AXText.get_caret_offset(obj)

        current_sentence, start, end = AXText.get_sentence_at_offset(obj, offset)
        if not current_sentence:
            return "", 0, 0

        if start <= 0:
            return "", 0, 0

        prev_offset = start - 1

        while prev_offset >= 0:
            prev_sentence, prev_start, prev_end = AXText.get_sentence_at_offset(obj, prev_offset)
            if (prev_sentence, prev_start, prev_end) != (current_sentence, start, end):
                return prev_sentence, prev_start, prev_end
            prev_offset -= 1

        return "", 0, 0

    @staticmethod
    def iter_sentence(
        obj: Atspi.Accessible,
        offset: int | None = None
    ) -> Generator[tuple[str, int, int], None, None]:
        """Generator to iterate by sentence in obj starting with the sentence at offset."""

        sentence, start, end = AXText.get_sentence_at_offset(obj, offset)
        if not sentence:
            return

        # Avoid yielding a duplicate when the starting offset is exactly at the
        # end boundary of the current sentence. Some implementations can return
        # the same (sentence, start, end) again for that offset.
        if offset is None or offset < end:
            yield sentence, start, end
        current_start = start

        while True:
            next_sentence, next_start, next_end = AXText.get_next_sentence(obj, current_start)
            if not next_sentence or next_start <= current_start:
                break
            yield next_sentence, next_start, next_end
            current_start = next_start

    @staticmethod
    def get_paragraph_at_offset(
        obj: Atspi.Accessible,
        offset: int | None = None
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

        tokens = [f"AXText: Paragraph at offset {offset} in", obj,
                  f"'{result.content}' ({result.start_offset}-{result.end_offset})"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result.content, result.start_offset, result.end_offset

    @staticmethod
    def get_paragraph_at_point(obj: Atspi.Accessible, x: int, y: int) -> tuple[str, int, int]:
        """Returns the (paragraph, start, end) at the specified point."""

        offset = AXText.get_offset_at_point(obj, x, y)
        if not 0 <= offset < AXText.get_character_count(obj):
            return "", 0, 0

        return AXText.get_paragraph_at_offset(obj, offset)

    @staticmethod
    def get_next_paragraph(
        obj: Atspi.Accessible,
        offset: int | None = None
    ) -> tuple[str, int, int]:
        """Returns the next (paragraph, start, end) for the current or specified offset."""

        if offset is None:
            offset = AXText.get_caret_offset(obj)

        current_paragraph, start, end = AXText.get_paragraph_at_offset(obj, offset)
        if not current_paragraph:
            return "", 0, 0

        length = AXText.get_character_count(obj)
        next_offset = max(end, offset + 1)

        while next_offset < length:
            next_paragraph, next_start, next_end = AXText.get_paragraph_at_offset(obj, next_offset)
            if (next_paragraph, next_start, next_end) != (current_paragraph, start, end):
                return next_paragraph, next_start, next_end
            next_offset += 1

        return "", 0, 0

    @staticmethod
    def get_previous_paragraph(
        obj: Atspi.Accessible,
        offset: int | None = None
    ) -> tuple[str, int, int]:
        """Returns the previous (paragraph, start, end) for the current or specified offset."""

        if offset is None:
            offset = AXText.get_caret_offset(obj)

        current_paragraph, start, end = AXText.get_paragraph_at_offset(obj, offset)
        if not current_paragraph:
            return "", 0, 0

        if start <= 0:
            return "", 0, 0

        prev_offset = start - 1

        while prev_offset >= 0:
            prev_paragraph, prev_start, prev_end = AXText.get_paragraph_at_offset(obj, prev_offset)
            if (prev_paragraph, prev_start, prev_end) != (current_paragraph, start, end):
                return prev_paragraph, prev_start, prev_end
            prev_offset -= 1

        return "", 0, 0

    @staticmethod
    def iter_paragraph(
        obj: Atspi.Accessible, offset: int | None = None
    ) -> Generator[tuple[str, int, int], None, None]:
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
    def supports_paragraph_iteration(obj: Atspi.Accessible) -> bool:
        """Returns True if paragraph iteration is supported on obj."""

        if not AXObject.supports_text(obj):
            return False

        string, start, end = AXText.get_paragraph_at_offset(obj, 0)
        result = string and 0 <= start < end
        tokens = ["AXText: Paragraph iteration supported on", obj, f": {result}"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return bool(result)

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
    def set_caret_offset_to_start(obj: Atspi.Accessible) -> bool:
        """Returns False if we definitely failed to set the offset. True cannot be trusted."""

        return AXText.set_caret_offset(obj, 0)

    @staticmethod
    def set_caret_offset_to_end(obj: Atspi.Accessible) -> bool:
        """Returns False if we definitely failed to set the offset. True cannot be trusted."""

        return AXText.set_caret_offset(obj, AXText.get_character_count(obj))

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
    def _get_n_selections(obj: Atspi.Accessible) -> int:
        """Returns the number of reported selected substrings in obj."""

        if not AXObject.supports_text(obj):
            return 0

        try:
            result = Atspi.Text.get_n_selections(obj)
        except GLib.GError as error:
            msg = f"AXText: Exception in _get_n_selections: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return 0

        tokens = ["AXText:", obj, f"reports {result} selection(s)."]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def _remove_selection(obj: Atspi.Accessible, selection_number: int) -> None:
        """Attempts to remove the specified selection."""

        if not AXObject.supports_text(obj):
            return

        try:
            Atspi.Text.remove_selection(obj, selection_number)
        except GLib.GError as error:
            msg = f"AXText: Exception in _remove_selection: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

    @staticmethod
    def has_selected_text(obj: Atspi.Accessible) -> bool:
        """Returns True if obj has selected text."""

        return bool(AXText.get_selected_ranges(obj))

    @staticmethod
    def is_all_text_selected(obj: Atspi.Accessible) -> bool:
        """Returns True of all the text in obj is selected."""

        length = AXText.get_character_count(obj)
        if not length:
            return False

        ranges = AXText.get_selected_ranges(obj)
        if not ranges:
            return False

        return ranges[0][0] == 0 and ranges[-1][1] == length

    @staticmethod
    def clear_all_selected_text(obj: Atspi.Accessible) -> None:
        """Attempts to clear the selected text."""

        for i in range(AXText._get_n_selections(obj)):
            AXText._remove_selection(obj, i)

    @staticmethod
    def get_selection_start_offset(obj: Atspi.Accessible) -> int:
        """Returns the leftmost offset of the selected text."""

        ranges = AXText.get_selected_ranges(obj)
        if ranges:
            return ranges[0][0]

        return -1

    @staticmethod
    def get_selection_end_offset(obj: Atspi.Accessible) -> int:
        """Returns the rightmost offset of the selected text."""

        ranges = AXText.get_selected_ranges(obj)
        if ranges:
            return ranges[-1][1]

        return -1

    @staticmethod
    def get_selected_ranges(obj: Atspi.Accessible) -> list[tuple[int, int]]:
        """Returns a list of (start_offset, end_offset) tuples reflecting the selected text."""

        count = AXText._get_n_selections(obj)
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
    def get_cached_selected_text(obj: Atspi.Accessible) -> tuple[str, int, int]:
        """Returns the last known selected string, start, and end for obj."""

        string, start, end = AXText.CACHED_TEXT_SELECTION.get(hash(obj), ("", 0, 0))
        debug_string = string.replace("\n", "\\n")
        tokens = ["AXText: Cached selection for", obj, f"is '{debug_string}' ({start}, {end})"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return string, start, end

    @staticmethod
    def update_cached_selected_text(obj: Atspi.Accessible) -> None:
        """Updates the last known selected string, start, and end for obj."""

        AXText.CACHED_TEXT_SELECTION[hash(obj)] = AXText.get_selected_text(obj)

    @staticmethod
    def get_selected_text(obj: Atspi.Accessible) -> tuple[str, int, int]:
        """Returns the selected string, start, and end for obj."""

        selections = AXText.get_selected_ranges(obj)
        if not selections:
            return "", 0, 0

        strings = []
        start_offset = -1
        end_offset = -1
        for selection in sorted(set(selections)):
            strings.append(AXText.get_substring(obj, *selection))
            end_offset = selection[1]
            if start_offset == -1:
                start_offset = selection[0]

        text = " ".join(strings)
        words = text.split()
        if len(words) > 20:
            debug_string = f"{' '.join(words[:5])} ... {' '.join(words[-5:])}"
        else:
            debug_string = text

        tokens = ["AXText: Selected text of", obj,
                  f"'{debug_string}' ({start_offset}-{end_offset})"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return text, start_offset, end_offset

    @staticmethod
    def _add_new_selection(obj: Atspi.Accessible, start_offset: int, end_offset: int) -> bool:
        """Creates a new selection for the specified range in obj."""

        if not AXObject.supports_text(obj):
            return False

        try:
            result = Atspi.Text.add_selection(obj, start_offset, end_offset)
        except GLib.GError as error:
            msg = f"AXText: Exception in _add_selection: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        return result

    @staticmethod
    def _update_existing_selection(
        obj: Atspi.Accessible,
        start_offset: int,
        end_offset: int,
        selection_number: int = 0
    ) -> bool:
        """Modifies specified selection in obj to the specified range."""

        if not AXObject.supports_text(obj):
            return False

        try:
            result = Atspi.Text.set_selection(obj, selection_number, start_offset, end_offset)
        except GLib.GError as error:
            msg = f"AXText: Exception in set_selected_text: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        return result

    @staticmethod
    def set_selected_text(obj: Atspi.Accessible, start_offset: int, end_offset: int) -> bool:
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
                debug.print_message(debug.LEVEL_INFO, msg, True)

        return result

    # TODO - JD: This should be converted to return AXTextAttribute values.
    @staticmethod
    def get_text_attributes_at_offset(
        obj: Atspi.Accessible,
        offset: int | None = None
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
    def get_all_text_attributes(
        obj: Atspi.Accessible,
        start_offset: int = 0,
        end_offset: int = -1
    ) -> list[tuple[int, int, dict[str, str]]]:
        """Returns a list of (start, end, attrs dict) tuples for obj."""

        if not AXObject.supports_text(obj):
            return []

        if end_offset == -1:
            end_offset = AXText.get_character_count(obj)

        tokens = ["AXText: Getting attributes for", obj, f"chars: {start_offset}-{end_offset}"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        rv = []
        offset = start_offset
        while offset < end_offset:
            attrs, start, end = AXText.get_text_attributes_at_offset(obj, offset)
            if start <= end:
                rv.append((max(start, offset), end, attrs))
            else:
                # TODO - JD: We're sometimes seeing this from WebKit, e.g. in Evo gitlab messages.
                msg = f"AXText: Start offset {start} > end offset {end}"
                debug.print_message(debug.LEVEL_INFO, msg, True)
            offset = max(end, offset + 1)

        msg = f"AXText: {len(rv)} attribute ranges found."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return rv

    @staticmethod
    def get_all_supported_text_attributes() -> list[AXTextAttribute]:
        """Returns a set of all supported text attribute names."""

        return list(AXTextAttribute)

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
    def _rect_is_fully_contained_in(rect1: Atspi.Rect, rect2: Atspi.Rect) -> bool:
        """Returns true if rect1 is fully contained in rect2"""

        return rect2.x <= rect1.x and rect2.y <= rect1.y \
            and rect2.x + rect2.width >= rect1.x + rect1.width \
            and rect2.y + rect2.height >= rect1.y + rect1.height

    @staticmethod
    def _line_comparison(line_rect: Atspi.Rect, clip_rect: Atspi.Rect) -> int:
        """Returns -1 (line above), 1 (line below), or 0 (line inside) clip_rect."""

        # https://gitlab.gnome.org/GNOME/gtk/-/issues/6419
        clip_rect.y = max(0, clip_rect.y)

        if line_rect.y + line_rect.height / 2 < clip_rect.y:
            return -1

        if line_rect.y + line_rect.height / 2 > clip_rect.y + clip_rect.height:
            return 1

        return 0

    @staticmethod
    def get_visible_lines(
        obj: Atspi.Accessible,
        clip_rect: Atspi.Rect
    ) -> list[tuple[str, int, int]]:
        """Returns a list of (string, start, end) for lines of obj inside clip_rect."""

        tokens = ["AXText: Getting visible lines for", obj, "inside", clip_rect]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        line, start, end = AXText.find_first_visible_line(obj, clip_rect)
        debug_string = line.replace("\n", "\\n")
        tokens = ["AXText: First visible line in", obj, f"is: '{debug_string}' ({start}-{end})"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

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
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def find_first_visible_line(
        obj: Atspi.Accessible,
        clip_rect: Atspi.Rect
    ) -> tuple[str, int, int]:
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
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
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
    def find_last_visible_line(
        obj: Atspi.Accessible,
        clip_rect: Atspi.Rect
    ) -> tuple[str, int, int]:
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
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
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
    def string_has_spelling_error(obj: Atspi.Accessible, offset: int | None = None) -> bool:
        """Returns True if the text attributes indicate a spelling error."""

        attributes = AXText.get_text_attributes_at_offset(obj, offset)[0]
        if attributes.get("invalid") == "spelling":
            return True
        if attributes.get("invalid") == "grammar":
            return False
        if attributes.get("text-spelling") == "misspelled":
            return True
        if attributes.get("underline") in ["error", "spelling"]:
            return True
        return False

    @staticmethod
    def string_has_grammar_error(obj: Atspi.Accessible, offset: int | None = None) -> bool:
        """Returns True if the text attributes indicate a grammar error."""

        attributes = AXText.get_text_attributes_at_offset(obj, offset)[0]
        if attributes.get("invalid") == "grammar":
            return True
        if attributes.get("underline") == "grammar":
            return True
        return False

    @staticmethod
    def is_eoc(character: str) -> bool:
        """Returns True if character is an embedded object character (\ufffc)."""

        return character == "\ufffc"

    @staticmethod
    def character_at_offset_is_eoc(obj: Atspi.Accessible, offset: int) -> bool:
        """Returns True if character in obj is an embedded object character (\ufffc)."""

        character, _start, _end = AXText.get_character_at_offset(obj, offset)
        return AXText.is_eoc(character)

    @staticmethod
    def is_whitespace_or_empty(obj: Atspi.Accessible) -> bool:
        """Returns True if obj lacks text, or contains only whitespace."""

        if not AXObject.supports_text(obj):
            return True

        return not AXText.get_all_text(obj).strip()

    @staticmethod
    def has_presentable_text(obj: Atspi.Accessible) -> bool:
        """Returns True if obj has presentable text."""

        if not AXObject.supports_text(obj):
            return False

        text = AXText.get_all_text(obj).strip()
        if not text:
            return AXUtilitiesRole.is_paragraph(obj)

        return bool(re.search(r"\w+", text))

    @staticmethod
    def scroll_substring_to_point(
        obj: Atspi.Accessible,
        x: int,
        y: int,
        start_offset: int | None = None,
        end_offset: int | None = None
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
                obj, start_offset, end_offset, Atspi.CoordType.WINDOW, x, y)
        except GLib.GError as error:
            msg = f"AXText: Exception in scroll_substring_to_point: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        tokens = ["AXText: Scrolled", obj, f"substring ({start_offset}-{end_offset}) to",
                  f"{x}, {y}: {result}"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def scroll_substring_to_location(
        obj: Atspi.Accessible,
        location: Atspi.ScrollType,
        start_offset: int | None = None,
        end_offset: int | None = None
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

        tokens = ["AXText: Scrolled", obj, f"substring ({start_offset}-{end_offset}) to",
                  location, f": {result}"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result
