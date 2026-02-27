# Higher-level utilities for working with accessible text.
#
# Copyright 2024-2026 Igalia, S.L.
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

"""Higher-level utilities for working with accessible text."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from . import debug
from .ax_object import AXObject
from .ax_text import AXText, AXTextAttribute
from .ax_utilities_role import AXUtilitiesRole

if TYPE_CHECKING:
    from collections.abc import Generator
    from typing import ClassVar

    import gi

    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi


class AXUtilitiesText:
    """Higher-level utilities for working with accessible text."""

    CACHED_TEXT_SELECTION: ClassVar[dict[int, tuple[str, int, int]]] = {}

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
        offset: int | None = None,
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
        offset: int | None = None,
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
        offset: int | None = None,
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
    def get_word_at_point(obj: Atspi.Accessible, x: int, y: int) -> tuple[str, int, int]:
        """Returns the (word, start, end) at the specified point."""

        offset = AXText.get_offset_at_point(obj, x, y)
        if not 0 <= offset < AXText.get_character_count(obj):
            return "", 0, 0

        return AXText.get_word_at_offset(obj, offset)

    @staticmethod
    def get_next_word(obj: Atspi.Accessible, offset: int | None = None) -> tuple[str, int, int]:
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
    def get_previous_word(obj: Atspi.Accessible, offset: int | None = None) -> tuple[str, int, int]:
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
        offset: int | None = None,
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
    def get_line_at_point(obj: Atspi.Accessible, x: int, y: int) -> tuple[str, int, int]:
        """Returns the (line, start, end) at the specified point."""

        offset = AXText.get_offset_at_point(obj, x, y)
        if not 0 <= offset < AXText.get_character_count(obj):
            return "", 0, 0

        return AXText.get_line_at_offset(obj, offset)

    @staticmethod
    def get_next_line(obj: Atspi.Accessible, offset: int | None = None) -> tuple[str, int, int]:
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
    def get_previous_line(obj: Atspi.Accessible, offset: int | None = None) -> tuple[str, int, int]:
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
        offset: int | None = None,
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
            next_line, next_start, next_end = AXUtilitiesText.get_next_line(obj, current_start)
            if not next_line or next_start <= current_start:
                break
            yield next_line, next_start, next_end
            current_start = next_start

    @staticmethod
    def has_sentence_ending(text: str) -> bool:
        """Check if text contains a sentence ending."""

        return bool(text and re.search(r"\S[.!?]+(\s|\ufffc|$)", text))

    @staticmethod
    def get_sentence_at_point(obj: Atspi.Accessible, x: int, y: int) -> tuple[str, int, int]:
        """Returns the (sentence, start, end) at the specified point."""

        offset = AXText.get_offset_at_point(obj, x, y)
        if not 0 <= offset < AXText.get_character_count(obj):
            return "", 0, 0

        return AXText.get_sentence_at_offset(obj, offset)

    @staticmethod
    def get_next_sentence(obj: Atspi.Accessible, offset: int | None = None) -> tuple[str, int, int]:
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
        offset: int | None = None,
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
        offset: int | None = None,
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
            next_sentence, next_start, next_end = AXUtilitiesText.get_next_sentence(
                obj,
                current_start,
            )
            if not next_sentence or next_start <= current_start:
                break
            yield next_sentence, next_start, next_end
            current_start = next_start

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
        offset: int | None = None,
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
        offset: int | None = None,
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
            prev_paragraph, prev_start, prev_end = AXText.get_paragraph_at_offset(
                obj,
                prev_offset,
            )
            if (prev_paragraph, prev_start, prev_end) != (current_paragraph, start, end):
                return prev_paragraph, prev_start, prev_end
            prev_offset -= 1

        return "", 0, 0

    @staticmethod
    def iter_paragraph(
        obj: Atspi.Accessible,
        offset: int | None = None,
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
    def set_caret_offset_to_start(obj: Atspi.Accessible) -> bool:
        """Returns False if we definitely failed to set the offset. True cannot be trusted."""

        return AXText.set_caret_offset(obj, 0)

    @staticmethod
    def set_caret_offset_to_end(obj: Atspi.Accessible) -> bool:
        """Returns False if we definitely failed to set the offset. True cannot be trusted."""

        return AXText.set_caret_offset(obj, AXText.get_character_count(obj))

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

        for i in range(AXText.get_n_selections(obj)):
            AXText.remove_selection(obj, i)

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
    def get_cached_selected_text(obj: Atspi.Accessible) -> tuple[str, int, int]:
        """Returns the last known selected string, start, and end for obj."""

        string, start, end = AXUtilitiesText.CACHED_TEXT_SELECTION.get(hash(obj), ("", 0, 0))
        debug_string = string.replace("\n", "\\n")
        tokens = ["AXText: Cached selection for", obj, f"is '{debug_string}' ({start}, {end})"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return string, start, end

    @staticmethod
    def update_cached_selected_text(obj: Atspi.Accessible) -> None:
        """Updates the last known selected string, start, and end for obj."""

        AXUtilitiesText.CACHED_TEXT_SELECTION[hash(obj)] = AXUtilitiesText.get_selected_text(obj)

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

        tokens = [
            "AXText: Selected text of",
            obj,
            f"'{debug_string}' ({start_offset}-{end_offset})",
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return text, start_offset, end_offset

    @staticmethod
    def set_selected_text(obj: Atspi.Accessible, start_offset: int, end_offset: int) -> bool:
        """Returns False if we definitely failed to set the selection. True cannot be trusted."""

        # TODO - JD: For now we always assume and operate on the first selection.
        # This preserves the original functionality prior to the refactor. But whether
        # that functionality is what it should be needs investigation.
        if AXText.get_n_selections(obj) > 0:
            result = AXText.update_existing_selection(obj, start_offset, end_offset)
        else:
            result = AXText.add_new_selection(obj, start_offset, end_offset)

        if result and debug.debugLevel <= debug.LEVEL_INFO:
            substring = AXText.get_substring(obj, start_offset, end_offset)
            selection = AXUtilitiesText.get_selected_text(obj)[0]
            if substring != selection:
                msg = "AXText: Substring and selected text do not match."
                debug.print_message(debug.LEVEL_INFO, msg, True)

        return result

    @staticmethod
    def get_all_text_attributes(
        obj: Atspi.Accessible,
        start_offset: int = 0,
        end_offset: int = -1,
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
    def _rect_is_fully_contained_in(rect1: Atspi.Rect, rect2: Atspi.Rect) -> bool:
        """Returns true if rect1 is fully contained in rect2"""

        return (
            rect2.x <= rect1.x
            and rect2.y <= rect1.y
            and rect2.x + rect2.width >= rect1.x + rect1.width
            and rect2.y + rect2.height >= rect1.y + rect1.height
        )

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
        clip_rect: Atspi.Rect,
    ) -> list[tuple[str, int, int]]:
        """Returns a list of (string, start, end) for lines of obj inside clip_rect."""

        tokens = ["AXText: Getting visible lines for", obj, "inside", clip_rect]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        line, start, end = AXUtilitiesText.find_first_visible_line(obj, clip_rect)
        debug_string = line.replace("\n", "\\n")
        tokens = ["AXText: First visible line in", obj, f"is: '{debug_string}' ({start}-{end})"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        result = [(line, start, end)]
        offset = end
        for line, start, end in AXUtilitiesText.iter_line(obj, offset):
            line_rect = AXText.get_range_rect(obj, start, end)
            if AXUtilitiesText._line_comparison(line_rect, clip_rect) > 0:
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
        clip_rect: Atspi.Rect,
    ) -> tuple[str, int, int]:
        """Returns the first (string, start, end) visible line of obj inside clip_rect."""

        result = "", 0, 0
        low, high = 0, AXText.get_character_count(obj)
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
            prev_result = AXText.get_line_at_offset(obj, start - 1)
            if prev_result[1] <= 0 and prev_result[2] <= 0:
                return result

            text_rect = AXText.get_range_rect(obj, start, end)
            if AXUtilitiesText._line_comparison(text_rect, clip_rect) < 0:
                low = mid + 1
                continue

            if AXUtilitiesText._line_comparison(text_rect, clip_rect) > 0:
                high = mid
                continue

            previous_rect = AXText.get_range_rect(obj, prev_result[1], prev_result[2])
            if AXUtilitiesText._line_comparison(previous_rect, clip_rect) != 0:
                return result

            result = prev_result
            high = mid

        return result

    @staticmethod
    def find_last_visible_line(
        obj: Atspi.Accessible,
        clip_rect: Atspi.Rect,
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
            next_result = AXText.get_line_at_offset(obj, end)
            if next_result[1] <= 0 and next_result[2] <= 0:
                return result

            text_rect = AXText.get_range_rect(obj, start, end)
            if AXUtilitiesText._line_comparison(text_rect, clip_rect) < 0:
                low = mid + 1
                continue

            if AXUtilitiesText._line_comparison(text_rect, clip_rect) > 0:
                high = mid
                continue

            next_rect = AXText.get_range_rect(obj, next_result[1], next_result[2])
            if AXUtilitiesText._line_comparison(next_rect, clip_rect) != 0:
                return result

            result = next_result
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
        return attributes.get("underline") in ["error", "spelling"]

    @staticmethod
    def string_has_grammar_error(obj: Atspi.Accessible, offset: int | None = None) -> bool:
        """Returns True if the text attributes indicate a grammar error."""

        attributes = AXText.get_text_attributes_at_offset(obj, offset)[0]
        if attributes.get("invalid") == "grammar":
            return True
        return attributes.get("underline") == "grammar"

    @staticmethod
    def is_eoc(character: str) -> bool:
        """Returns True if character is an embedded object character (\\ufffc)."""

        return character == "\ufffc"

    @staticmethod
    def character_at_offset_is_eoc(obj: Atspi.Accessible, offset: int) -> bool:
        """Returns True if character in obj is an embedded object character (\\ufffc)."""

        character, _start, _end = AXText.get_character_at_offset(obj, offset)
        return AXUtilitiesText.is_eoc(character)

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
