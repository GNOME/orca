# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
# Copyright 2016-2025 Igalia, S.L.
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
# pylint: disable=too-many-lines
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-instance-attributes

"""Provides the default implementation for flat review for Orca."""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc." \
                "Copyright (c) 2016-2025 Igalia, S.L."
__license__   = "LGPL"

import re

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from . import braille
from . import braille_presenter
from . import debug
from . import focus_manager
from . import script_manager
from . import speech_and_verbosity_manager
from .ax_component import AXComponent
from .ax_object import AXObject
from .ax_text import AXText
from .ax_utilities import AXUtilities

class Char:
    """A character's worth of presentable information."""

    def __init__(self, word: "Word", start_offset: int, string: str):
        """Creates a new char.

        Arguments:
        - word: the Word instance this belongs to
        - start_offset: the start offset with respect to the accessible object
        - string: the char string
        """

        self._word: "Word" = word
        self._start_offset: int = start_offset
        self._string: str = string
        self._rect: Atspi.Rect | None = None

    def __str__(self) -> str:
        text = self._string.replace("\n", "\\n")
        rect = self.get_rect()
        rect_string = f"({rect.x}, {rect.y}, {rect.width}, {rect.height})"
        return (
            f"CHAR: '{text}' ({self._start_offset}-{self._start_offset + 1}) "
            f"rect: {rect_string}"
        )

    def get_string(self) -> str:
        """Returns the string being displayed for this Char."""

        return self._string

    def get_start_offset(self) -> int:
        """Returns the start offset of this Char with respect to the accessible object."""

        return self._start_offset

    def get_rect(self) -> Atspi.Rect:
        """Returns the Atspi.Rect instance representing the extents of this Char."""

        if self._rect is None:
            obj = self._word.get_object()
            self._rect = AXText.get_character_rect(obj, self._start_offset)

        return self._rect

class Word:
    """A single chunk (word or object) of presentable information."""

    def __init__(self, zone: "Zone", start_offset: int, string: str):
        """Creates a new Word.

        Arguments:
        - zone: the Zone instance this belongs to
        - start_offset: the start offset with respect to the accessible object
        - string: the word string
        """

        self._zone: "Zone" = zone
        self._start_offset: int = start_offset
        self._string: str = string
        self._rect: Atspi.Rect | None = None
        self._characters: dict[int, Char] = {}

    def __str__(self) -> str:
        text = self._string.replace("\n", "\\n")
        rect = self.get_rect()
        rect_string = f"({rect.x}, {rect.y}, {rect.width}, {rect.height})"
        return (
            f"WORD: '{text}' ({self._start_offset}-{self._start_offset + len(self._string)}) "
            f"rect: {rect_string}"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Word):
            return False

        if self._zone != other._zone or self._start_offset != other._start_offset or \
           self._string != other._string:
            return False

        this_rect = self.get_rect()
        other_rect = other.get_rect()
        return this_rect.x == other_rect.x and this_rect.y == other_rect.y and \
               this_rect.width == other_rect.width and this_rect.height == other_rect.height

    def get_characters(self) -> list[Char]:
        """Returns a list of Char instances for this Word."""

        for i, char_str in enumerate(self._string):
            if i not in self._characters:
                start = i + self._start_offset
                self._characters[i] = Char(self, start, char_str)

        return [self._characters[i] for i in range(len(self._string))]

    def get_character_at_index(self, index: int) -> Char | None:
        """Returns the Char at the specified index with respect to this Word."""

        if not 0 <= index < len(self._string):
            return None

        if index not in self._characters:
            char_str = self._string[index]
            start = index + self._start_offset
            self._characters[index] = Char(self, start, char_str)

        return self._characters[index]

    def get_start_offset(self) -> int:
        """Returns the start offset of this Word with respect to the accessible object."""

        return self._start_offset

    def get_relative_offset(self, offset: int) -> int:
        """Returns the char offset with respect to this word or -1."""

        if self._start_offset <= offset < self._start_offset + len(self._string):
            return offset - self._start_offset

        return -1

    def get_string(self) -> str:
        """Returns the string being displayed for this Word."""

        return self._string

    def get_rect(self) -> Atspi.Rect:
        """Returns the Atspi.Rect instance representing the extents of this Word."""

        if self._rect is None:
            self._rect = self._zone.get_word_rect(self._start_offset, self._string)
        return self._rect

    def get_object(self) -> Atspi.Accessible:
        """Returns the accessible object associated with this Word's zone."""

        return self._zone.get_object()

class Zone:
    """Represents text that is a portion of a single horizontal line."""

    WORDS_RE = re.compile(r"(\S+\s*)")

    def __init__(self, obj: Atspi.Accessible, string: str, rect: Atspi.Rect) -> None:
        """Creates a new Zone.

        Arguments:
        - obj: the Accessible associated with this Zone
        - string: the string being displayed for this Zone
        - rect: an Atspi.Rect instance representing the extents of this Zone
        """

        self._obj: Atspi.Accessible = obj
        self._start_offset: int = 0
        self._string: str = string
        self._rect: Atspi.Rect = rect
        self._words: list[Word] = []
        self.line: 'Line' | None = None
        self._braille_region: braille.Region | None = None
        self._word_rect_cache: dict[tuple[int, int], Atspi.Rect] = {}
        self._word_index_map: dict[tuple[int, str], int] = {}  # (start_offset, string) -> index

    def __str__(self) -> str:
        text = self._string.replace("\n", "\\n")
        return f"ZONE: '{text}' {AXObject.get_role_name(self._obj)}"

    def _can_cache_braille_region(self) -> bool:
        """Returns True if we can cache the braille region for this Zone."""

        if AXUtilities.is_editable(self._obj):
            return False

        if AXObject.supports_value(self._obj):
            return False

        return True

    def get_braille_region(self) -> braille.Region | None:
        """Returns the braille region for this Zone."""

        if self._braille_region is not None:
            return self._braille_region

        region = braille.ReviewComponent(self._obj, self._string, 0, self)
        if self._can_cache_braille_region():
            self._braille_region = region
        return region

    def get_string(self) -> str:
        """Returns the string being displayed for this Zone."""

        return self._string

    def get_words(self) -> list[Word]:
        """Returns the list of Words in this Zone."""

        if self._words:
            return self._words

        # TODO - JD: For now, don't fake character and word extents.
        # The main goal is to improve reviewability.
        for i, word in enumerate(re.finditer(self.WORDS_RE, self._string)):
            word_obj = Word(self, word.start(), word.group())
            self._words.append(word_obj)
            key = (word_obj.get_start_offset(), word_obj.get_string())
            self._word_index_map[key] = i

        return self._words

    def get_word_at_index(self, index: int) -> Word | None:
        """Returns the Word at the specified index with respect to this Zone."""

        words = self.get_words()
        if 0 <= index < len(words):
            return words[index]

        return None

    def get_index_of_word(self, word: Word) -> int:
        """Returns the index of the specified Word with respect to this Zone."""

        # Ensure words are initialized
        self.get_words()
        key = (word.get_start_offset(), word.get_string())
        return self._word_index_map.get(key, -1)

    def get_object(self) -> Atspi.Accessible:
        """Returns the accessible object associated with this Zone."""

        return self._obj

    def get_rect(self) -> Atspi.Rect:
        """Returns the Atspi.Rect instance representing the extents of this Zone."""

        return self._rect

    def get_word_rect(self, start_offset: int, string: str) -> Atspi.Rect:
        """Returns the rectangle for a word within this zone."""

        cache_key = (start_offset, len(string))
        if cache_key in self._word_rect_cache:
            return self._word_rect_cache[cache_key]

        # TODO - JD: For now, don't fake character and word extents.
        # The main goal is to improve reviewability.
        rect = self._rect
        self._word_rect_cache[cache_key] = rect
        return rect

    def on_same_line(self, zone: "Zone", pixel_delta: int = 5) -> bool:
        """Returns True if we treat this Zone and zone as being on one line."""

        if AXUtilities.is_scroll_bar(self._obj) or AXUtilities.is_scroll_bar(zone.get_object()):
            return self._obj == zone.get_object()

        this_parent = AXObject.get_parent(self._obj)
        zone_parent = AXObject.get_parent(zone.get_object())
        if AXUtilities.is_menu(this_parent) or AXUtilities.is_menu(zone_parent):
            return this_parent == zone_parent

        this_rect = self._rect
        zone_rect = zone.get_rect()
        if this_rect.width == 0 and this_rect.height == 0:
            return zone_rect.y <= this_rect.y <= zone_rect.y + zone_rect.height

        if zone_rect.width == 0 and zone_rect.height == 0:
            return this_rect.y <= zone_rect.y <= this_rect.y + this_rect.height

        highest_bottom = min(this_rect.y + this_rect.height, zone_rect.y + zone_rect.height)
        lowest_top = max(this_rect.y, zone_rect.y)
        if lowest_top >= highest_bottom:
            return False

        this_middle = this_rect.y + this_rect.height / 2
        zone_middle = zone_rect.y + zone_rect.height / 2
        return abs(this_middle - zone_middle) <= pixel_delta

    def get_start_offset(self) -> int:
        """Returns the start offset of this Zone with respect to the accessible object."""

        return self._start_offset

    def get_word_at_offset(self, char_offset: int) -> tuple[Word | None, int]:
        """Returns the Word at the specified offset with respect to the accessible object."""

        msg = f"FLAT REVIEW: Searching for word at offset {char_offset}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        words = self.get_words()
        for word in words:
            tokens = ["FLAT REVIEW: Checking", word]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

            offset = word.get_relative_offset(char_offset)
            if offset >= 0:
                return word, offset

        if len(self._string) == char_offset and words:
            last_word = words[-1]
            return last_word, len(last_word.get_string())

        return None, -1

    def has_caret(self) -> bool:
        """Returns True if this Zone contains the caret."""

        return False

    def word_with_caret(self) -> tuple[Word | None, int]:
        """Returns the Word and relative offset with the caret."""

        return None, -1

class TextZone(Zone):
    """A Zone whose purpose is to display text of an object."""

    def __init__(
        self,
        obj: Atspi.Accessible,
        start_offset: int,
        string: str,
        rect: Atspi.Rect
    ) -> None:
        """Creates a new TextZone.

        Arguments:
        - obj: the Accessible associated with this Zone
        - string: the string being displayed for this Zone
        - rect: an Atspi.Rect instance representing the extents of this Zone
        """

        super().__init__(obj, string, rect)
        self._start_offset: int = start_offset
        self._word_rect_cache: dict[tuple[int, int], Atspi.Rect] = {}

    def __str__(self) -> str:
        text = self._string.replace("\n", "\\n")
        return f"TEXT ZONE: '{text}' {AXObject.get_role_name(self._obj)}"

    def _can_cache_braille_region(self) -> bool:
        """Returns True if we can cache the braille region for this Zone."""

        if AXUtilities.is_editable(self._obj) or AXUtilities.is_terminal(self._obj):
            return False

        if AXUtilities.is_label(self._obj):
            return False

        return True

    def get_braille_region(self) -> braille.Region | None:
        """Returns the braille region for this Zone."""

        if self._braille_region is not None:
            return self._braille_region

        region = braille.ReviewText(self._obj, self._string, self._start_offset, self)
        if self._can_cache_braille_region():
            self._braille_region = region

        return region

    def get_string(self) -> str:
        """Returns the string being displayed for this Zone."""

        end_offset = self._start_offset + len(self._string)
        self._string = AXText.get_substring(self._obj, self._start_offset, end_offset)
        return self._string

    def get_words(self) -> list[Word]:
        """Returns the list of Words in this Zone."""

        words = []
        self._word_index_map.clear()  # Clear any existing mapping
        for i, word in enumerate(re.finditer(self.WORDS_RE, self.get_string())):
            start = word.start() + self._start_offset
            word_obj = Word(self, start, word.group())
            words.append(word_obj)
            key = (word_obj.get_start_offset(), word_obj.get_string())
            self._word_index_map[key] = i

        self._words = words
        return self._words

    def get_word_rect(self, start_offset: int, string: str) -> Atspi.Rect:
        """Returns the precise rectangle for a word within this TextZone."""

        cache_key = (start_offset, len(string))
        if cache_key in self._word_rect_cache:
            return self._word_rect_cache[cache_key]

        end_offset = start_offset + len(string)
        rect = AXText.get_range_rect(self._obj, start_offset, end_offset)
        self._word_rect_cache[cache_key] = rect
        return rect

    def has_caret(self) -> bool:
        """Returns True if this Zone contains the caret."""

        end_offset = self._start_offset + len(self._string)
        if self._start_offset <= AXText.get_caret_offset(self._obj) < end_offset:
            return True

        return end_offset == AXText.get_character_count(self._obj)

    def word_with_caret(self) -> tuple[Word | None, int]:
        """Returns the Word and relative offset with the caret."""

        if not self.has_caret():
            return None, -1

        return self.get_word_at_offset(AXText.get_caret_offset(self._obj))


class StateZone(Zone):
    """A Zone whose purpose is to display the state of an object."""

    def __init__(self, obj: Atspi.Accessible, rect: Atspi.Rect) -> None:
        super().__init__(obj, "", rect)

    def __str__(self) -> str:
        text = self.get_string().replace("\n", "\\n")
        return f"STATE ZONE: '{text}' {AXObject.get_role_name(self._obj)}"

    def _can_cache_braille_region(self) -> bool:
        """Returns True if we can cache the braille region for this Zone."""

        return False

    def get_braille_region(self) -> braille.Region | None:
        """Returns the braille region for this Zone."""

        script = script_manager.get_manager().get_active_script()
        if script is None:
            return None

        result = script.braille_generator.get_state_indicator(self._obj)
        if result and result[0]:
            if isinstance(result[0], str):
                return braille.ReviewComponent(self._obj, result[0], 0, self)
            return result[0]
        return None

    def get_string(self) -> str:
        """Returns the string being displayed for this Zone."""

        script = script_manager.get_manager().get_active_script()
        if script is None:
            return ""

        result = script.speech_generator.get_state_indicator(self._obj)
        return " ".join([r for r in result if isinstance(r, str)])
class ValueZone(Zone):
    """A Zone whose purpose is to display the value of an object."""

    def __init__(self, obj: Atspi.Accessible, rect: Atspi.Rect) -> None:
        super().__init__(obj, "", rect)

    def __str__(self) -> str:
        text = self.get_string().replace("\n", "\\n")
        return f"VALUE ZONE: '{text}' {AXObject.get_role_name(self._obj)}"

    def _can_cache_braille_region(self) -> bool:
        """Returns True if we can cache the braille region for this Zone."""

        return False

    def get_braille_region(self) -> braille.Region | None:
        """Returns the braille region for this Zone."""

        script = script_manager.get_manager().get_active_script()
        if script is None:
            return None

        rolename = script.braille_generator.get_localized_role_name(self._obj)
        value = script.braille_generator.get_value(self._obj)
        if rolename and value:
            result = f"{rolename} {value[0]}"
            return braille.ReviewComponent(self._obj, result, 0, self)
        return None

    def get_string(self) -> str:
        """Returns the string being displayed for this Zone."""

        script = script_manager.get_manager().get_active_script()
        if script is None:
            return ""

        rolename = script.speech_generator.get_localized_role_name(self._obj)
        value = script.speech_generator.get_value(self._obj)
        result = ""
        if rolename and value:
            result = f"{rolename} {value[0]}"
        return result


class Line:
    """A Line is a single line across a window and is composed of Zones."""

    def __init__(self, line_number: int, zones: list[Zone]) -> None:
        """Creates a new Line, which is a horizontal region of text.

        Arguments:
        - line_number: the line number of this Line in the window
        - zones: the Zones that make up this line
        """

        self._line_number: int = line_number
        self._zones: list[Zone] = zones
        self._zone_index_map: dict[Zone, int] = {zone: i for i, zone in enumerate(zones)}

    def get_line_number(self) -> int:
        """Returns the index of this Line in the window."""

        return self._line_number

    def get_zones(self) -> list[Zone]:
        """Returns the list of Zones in this Line."""

        return self._zones

    def get_zone_at_index(self, index: int) -> Zone | None:
        """Returns the Zone at the specified index with respect to this Line."""

        if 0 <= index < len(self._zones):
            return self._zones[index]

        return None

    def get_index_of_zone(self, zone: Zone) -> int:
        """Returns the index of the specified Zone with respect to this Line."""

        return self._zone_index_map.get(zone, -1)

    def get_string(self) -> str:
        """Returns the string of this Line, which is the concatenation of all Zones."""

        return " ".join([zone.get_string() for zone in self._zones])

    def get_braille_regions(self) -> list[braille.Region]:
        """Returns a list of braille regions for this Line."""

        regions: list[braille.Region] = []
        for zone in self._zones:
            region = zone.get_braille_region()
            if region is not None:
                if regions:
                    regions.append(braille.Region(" "))
                regions.append(region)

        if braille_presenter.get_presenter().get_end_of_line_indicator_is_enabled():
            if regions:
                regions.append(braille.Region(" "))
            regions.append(braille.Region("$l"))

        return regions

class Context:
    """Contains the flat review regions for the current top-level object."""

    CHAR   = 0
    WORD   = 1
    ZONE   = 2
    LINE   = 3
    WINDOW = 4

    def __init__(self, script, root: Atspi.Accessible | None = None) -> None:
        """Create a new Context for script."""

        self._script = script
        self._zones: list[Zone] = []
        self._lines: list[Line] = []
        self._line_index: int = 0
        self._zone_index: int = 0
        self._word_index: int = 0
        self._char_index: int = 0
        self._focus_zone: Zone | None = None
        self._container: Atspi.Accessible | None = None
        self._object_to_zone_map: dict[Atspi.Accessible, list[Zone]] = {}
        self._focus_obj: Atspi.Accessible | None = \
            focus_manager.get_manager().get_locus_of_focus()
        self._top_level: Atspi.Accessible | None = None
        self._rect: Atspi.Rect = Atspi.Rect()

        frame, dialog = script.utilities.frame_and_dialog(self._focus_obj)
        if root is not None:
            self._top_level = root
            tokens = ["FLAT REVIEW: Restricting flat review to", root]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        else:
            self._top_level = dialog or frame
        tokens = ["FLAT REVIEW: Frame:", frame, "Dialog:", dialog, ". Top level:", self._top_level]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        self._rect = AXComponent.get_rect(self._top_level)

        container = AXObject.find_ancestor_inclusive(self._focus_obj, AXUtilities.is_menu)
        self._container = container or self._top_level

        self._zones = self._get_showing_zones(self._container)
        for zone in self._zones:
            obj = zone.get_object()
            if obj not in self._object_to_zone_map:
                self._object_to_zone_map[obj] = []
            self._object_to_zone_map[obj].append(zone)
        self._focus_zone = self._find_zone_with_object(self._focus_obj)

        self._lines = self._cluster_zones_by_line(self._zones)
        if not (self._lines and self._focus_zone):
            return

        for i, line in enumerate(self._lines):
            index = line.get_index_of_zone(self._focus_zone)
            if index < 0:
                continue

            self._line_index = i
            self._zone_index = index
            word, offset = self._focus_zone.word_with_caret()
            if word:
                self._word_index = self._focus_zone.get_index_of_word(word)
                self._char_index = offset
            break

        msg = (
            f"FLAT REVIEW: On line {self._line_index}, zone {self._zone_index} "
            f"word {self._word_index}, char {self._char_index}"
        )
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def _split_text_into_zones(
        self,
        obj: Atspi.Accessible,
        string: str,
        start_offset: int,
        cliprect: Atspi.Rect
    ) -> list[TextZone]:
        """Returns a list of TextZones with embedded object characters removed."""

        zones: list[TextZone] = []
        ranges = [(*m.span(), m.group(0)) for m in re.finditer(r"[^\ufffc]+", string)]
        ranges = list(map(lambda x: (x[0] + start_offset, x[1] + start_offset, x[2]), ranges))
        for (start, end, substring) in ranges:
            rect = AXText.get_range_rect(obj, start, end)
            intersection = AXComponent.get_rect_intersection(rect, cliprect)
            if not AXComponent.is_empty_rect(intersection):
                zones.append(TextZone(obj, start, substring, intersection))

        return zones

    def _get_zones_from_text(self, obj: Atspi.Accessible, cliprect: Atspi.Rect) -> list[TextZone]:
        """Returns a list of TextZones for the given object."""

        if not AXText.has_presentable_text(obj):
            return []

        zones: list[TextZone] = []

        def _is_container(x: Atspi.Accessible) -> bool:
            return AXUtilities.is_scroll_pane(x) or AXUtilities.is_document(x)

        container = AXObject.find_ancestor(obj, _is_container)
        if container:
            rect = AXComponent.get_rect(container)
            intersection = AXComponent.get_rect_intersection(rect, cliprect)
            if AXComponent.is_same_rect(rect, intersection):
                tokens = ["FLAT REVIEW: Cliprect", cliprect, "->", rect, "from", container]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                cliprect = rect

        if AXObject.supports_editable_text(obj) and AXUtilities.is_single_line(obj):
            rect = AXComponent.get_rect(obj)
            return [TextZone(obj, 0, AXText.get_all_text(obj), rect)]

        tokens = ["FLAT REVIEW: Getting lines for", obj]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        lines = AXText.get_visible_lines(obj, cliprect)
        # Optionally skip whitespace-only lines based on user preference.
        if not speech_and_verbosity_manager.get_manager().get_speak_blank_lines():
            lines = [t for t in lines if t[0] and t[0].strip()]
        tokens = ["FLAT REVIEW:", len(lines), "lines found for", obj]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        for string, start_offset, _end_offset in lines:
            zones.extend(self._split_text_into_zones(obj, string, start_offset, cliprect))

        return zones

    def _get_zones_from_object(self, obj: Atspi.Accessible, cliprect: Atspi.Rect) -> list[Zone]:
        """Returns a list of Zones for the given object."""

        rect = AXComponent.get_rect(obj)
        zones: list[Zone] = list(self._get_zones_from_text(obj, cliprect))
        if not zones:
            if AXObject.supports_value(obj):
                zones.append(ValueZone(obj, rect))
            else:
                string = ""
                if not AXUtilities.is_table_row(obj):
                    string = self._script.speech_generator.get_name(obj, inFlatReview=True)
                if not string:
                    string = self._script.speech_generator.get_role_name(obj)
                if string:
                    zones.append(Zone(obj, string, rect))

        zone = StateZone(obj, rect)
        if zone.get_string():
            zones.insert(0, zone)

        return zones

    def set_current_to_zone_with_object(self, obj: Atspi.Accessible) -> bool:
        """Attempts to set the current zone to obj, if obj is in the current context."""

        tokens = ["FLAT REVIEW: Current", self.get_current_object(),
                  f"line: {self._line_index}, zone: {self._zone_index},",
                  f"word: {self._word_index}, char: {self._char_index})"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        zone = self._find_zone_with_object(obj)
        tokens = ["FLAT REVIEW: Zone with", obj, "is", zone]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        if zone is None:
            return False

        for i, line in enumerate(self._lines):
            index = line.get_index_of_zone(zone)
            if index < 0:
                continue

            self._line_index = i
            self._zone_index = index
            word, offset = zone.word_with_caret()
            if word:
                self._word_index = zone.get_index_of_word(word)
                self._char_index = offset
            msg = "FLAT REVIEW: Updated current zone."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            break
        else:
            msg = "FLAT REVIEW: Failed to update current zone."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        tokens = ["FLAT REVIEW: Updated", self.get_current_object(),
                  f"line: {self._line_index}, zone: {self._zone_index},",
                  f"word: {self._word_index}, char: {self._char_index})"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return True

    def _find_zone_with_object(self, obj: Atspi.Accessible | None) -> Zone | None:
        """Returns the existing zone which contains obj."""

        if obj is None:
            return None

        if matching_zones := self._object_to_zone_map.get(obj, []):
            for zone in matching_zones:
                if zone.has_caret():
                    return zone
            return matching_zones[0]

        # Items can be pruned from the flat review context. When this happens, usually the parent
        # or one of its children will still be in the context.
        if parent := AXObject.get_parent(obj):
            if parent_zones := self._object_to_zone_map.get(parent, []):
                return parent_zones[0]

        for child in AXObject.iter_children(obj):
            if child_zones := self._object_to_zone_map.get(child, []):
                return child_zones[0]

        return None

    def _get_showing_zones(
        self,
        root: Atspi.Accessible,
        boundingbox: Atspi.Rect | None = None
    ) -> list[Zone]:
        """Returns an unsorted list of all the zones under root."""

        if boundingbox is None:
            boundingbox = self._rect

        objs = AXUtilities.get_on_screen_objects(root, boundingbox)
        tokens = ["FLAT REVIEW:", len(objs), "on-screen objects found for", root]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        all_zones: list[Zone] = []
        obj_set = set(objs)
        for o in objs:
            if obj_set.intersection(AXUtilities.get_is_label_for(o)):
                continue

            zones = self._get_zones_from_object(o, boundingbox)
            if not zones:
                descendant = self._script.utilities.active_descendant(o)
                if descendant:
                    zones = self._get_zones_from_object(descendant, boundingbox)
            all_zones.extend(zones)

        tokens = ["FLAT REVIEW:", len(all_zones), "zones found for", root]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return all_zones

    def _cluster_zones_by_line(self, zones: list[Zone]) -> list[Line]:
        """Returns a sorted list of Line clusters containing sorted Zones."""

        if not zones:
            return []

        zones.sort(key=lambda zone: zone.get_rect().y)
        line_clusters: list[list[Zone]] = []
        current_cluster = [zones[0]]
        for zone in zones[1:]:
            if zone.on_same_line(current_cluster[-1]):
                current_cluster.append(zone)
            else:
                current_cluster.sort(key=lambda z: z.get_rect().x)
                line_clusters.append(current_cluster)
                current_cluster = [zone]

        if current_cluster:
            current_cluster.sort(key=lambda z: z.get_rect().x)
            line_clusters.append(current_cluster)

        lines: list[Line] = []
        for line_index, zones_in_line in enumerate(line_clusters):
            line = Line(line_index, zones_in_line)
            lines.append(line)
            for zone in zones_in_line:
                zone.line = line

        tokens = ["FLAT REVIEW: Zones clustered into", len(lines), "lines"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return lines

    def get_current_line_string(self) -> str:
        """Returns the string of the current line."""

        if zone := self._get_current_zone():
            if zone.line:
                return zone.line.get_string()
        return ""

    def get_current_zone_string(self) -> str:
        """Returns the string of the current zone."""

        if zone := self._get_current_zone():
            return zone.get_string()
        return ""

    def get_current_word_string(self) -> str:
        """Returns the string of the current word."""

        zone = self._get_current_zone()
        if not zone:
            return ""

        if words := zone.get_words():
            return words[self._word_index].get_string()

        return zone.get_string()

    def get_current_character_string(self) -> str:
        """Returns the string of the current character."""

        zone = self._get_current_zone()
        if not zone:
            return ""

        words = zone.get_words()
        if not words:
            return ""

        word = words[self._word_index]
        if char := word.get_character_at_index(self._char_index):
            return char.get_string()
        return ""

    def _get_current_character_rect(self) -> Atspi.Rect:
        """Returns the extents of the current character."""

        zone = self._get_current_zone()
        if not zone:
            return Atspi.Rect()

        words = zone.get_words()
        if not words:
            return Atspi.Rect()

        word = words[self._word_index]
        if char := word.get_character_at_index(self._char_index):
            return char.get_rect()

        return Atspi.Rect()

    def get_current_location(self) -> tuple[int, int, int, int]:
        """Returns the location as a (lineIndex, zoneIndex, wordIndex, charIndex) tuple."""

        return self._line_index, self._zone_index, self._word_index, self._char_index

    def set_current_location(self, location: tuple[int, int, int, int]) -> None:
        """Sets the location to the specified (lineIndex, zoneIndex, wordIndex, charIndex)."""

        self._line_index, self._zone_index, self._word_index, self._char_index = location

    def set_current_zone(self, zone: Zone, offset_in_zone: int = 0) -> None:
        """Sets zone as the current zone."""

        if zone is None or zone.line is None:
            return

        self._line_index = zone.line.get_line_number()
        self._zone_index = self._lines[self._line_index].get_index_of_zone(zone)
        self._word_index = 0
        self._char_index = 0

        text_offset = zone.get_start_offset()
        word, character_offset = zone.get_word_at_offset(text_offset + offset_in_zone)
        if word:
            self._word_index = zone.get_index_of_word(word)
            self._char_index = character_offset

    def _get_current_zone(self) -> Zone | None:
        """Returns the current Zone."""

        if not (self._lines and 0 <= self._line_index < len(self._lines)):
            return None

        line = self._lines[self._line_index]
        zones = line.get_zones()
        if not (line and 0 <= self._zone_index < len(zones)):
            return None

        return zones[self._zone_index]

    def get_current_text_offset(self) -> int:
        """Returns the current text offset in the current object."""

        zone = self._get_current_zone()
        if zone is None:
            return -1
        words = zone.get_words()
        if not words:
            return -1
        word = words[self._word_index]
        if char := word.get_character_at_index(self._char_index):
            return char.get_start_offset()
        return -1

    def get_current_object(self) -> Atspi.Accessible | None:
        """Returns the current object."""

        zone = self._get_current_zone()
        if not zone:
            return None

        return zone.get_object()

    def get_current_braille_regions(self) -> tuple[list[braille.Region], braille.Region | None]:
        """Returns a (regions, focused-region) tuple."""

        if not self._lines:
            return [], None

        focused_region = None
        line = self._lines[self._line_index]
        regions = line.get_braille_regions()

        zone = self._get_current_zone()
        if zone is None:
            return regions, None

        focused_region = zone.get_braille_region()
        if focused_region is None:
            return regions, None

        focused_region.cursor_offset = 0
        if words := zone.get_words():
            focused_region.cursor_offset += words[0].get_start_offset() - zone.get_start_offset()
            for word_index in range(self._word_index):
                focused_region.cursor_offset += len(words[word_index].get_string())
        focused_region.cursor_offset += self._char_index
        # This is related to contracted braille.
        focused_region.reposition_cursor()
        return regions, focused_region

    def go_to_start_of(self, review_type: int = WINDOW) -> bool:
        """Returns True if moving to the start of the specified type succeeded."""

        before = [self._line_index, self._zone_index, self._word_index, self._char_index]
        self._char_index = 0
        self._word_index = 0
        if review_type == Context.WINDOW:
            self._zone_index = 0
            self._line_index = 0
        elif review_type == Context.LINE:
            self._zone_index = 0

        return before != [self._line_index, self._zone_index, self._word_index, self._char_index]

    def go_to_end_of(self, review_type: int = WINDOW) -> bool:
        """Returns True if moving to the end of the specified type succeeded."""

        if not self._lines:
            return False

        before = [self._line_index, self._zone_index, self._word_index, self._char_index]
        if review_type == Context.WINDOW:
            self._line_index = len(self._lines) - 1
        elif review_type == Context.LINE:
            self._zone_index = len(self._lines[self._line_index].get_zones()) - 1

        zone = self._get_current_zone()
        if zone is None:
            return False
        if words := zone.get_words():
            self._word_index = len(words) - 1
            word = words[self._word_index]
            chars = word.get_characters()
            self._char_index = max(len(chars) - 1, 0)
        else:
            self._word_index = 0
            self._char_index = 0

        return before != [self._line_index, self._zone_index, self._word_index, self._char_index]

    def go_previous_line(self, wrap: bool = False) -> bool:
        """Returns True if moving to the previous line succeeded."""

        if self._line_index > 0:
            self._line_index -= 1
            self._zone_index = 0
            self._word_index = 0
            self._char_index = 0
            return True

        if not wrap:
            return False

        self._line_index = max(0, len(self._lines) - 1)
        self._zone_index = 0
        self._word_index = 0
        self._char_index = 0
        return True

    def go_next_line(self, wrap: bool = False) -> bool:
        """Returns True if moving to the next line succeeded."""

        if self._line_index < (len(self._lines) - 1):
            self._line_index += 1
            self._zone_index = 0
            self._word_index = 0
            self._char_index = 0
            return True

        if not wrap:
            return False

        self._line_index = 0
        self._zone_index = 0
        self._word_index = 0
        self._char_index = 0
        return True

    def go_previous_zone(self) -> bool:
        """Returns True if moving to the previous zone succeeded."""

        if self._zone_index > 0:
            self._zone_index -= 1
            self._word_index = 0
            self._char_index = 0
            return True

        if not self.go_previous_line():
            return False

        zones = self._lines[self._line_index].get_zones()
        self._zone_index = max(len(zones) - 1, 0)
        self._word_index = 0
        self._char_index = 0
        return True

    def go_next_zone(self) -> bool:
        """Returns True if moving to the next zone succeeded."""

        zones = self._lines[self._line_index].get_zones()
        if self._zone_index < len(zones) - 1:
            self._zone_index += 1
            self._word_index = 0
            self._char_index = 0
            return True

        return self.go_next_line()

    def go_previous_word(self) -> bool:
        """Returns True if moving to the previous word succeeded."""

        if self._word_index > 0:
            self._word_index -= 1
            self._char_index = 0
            return True

        if not self.go_previous_zone():
            return False

        self.go_to_end_of(Context.ZONE)
        return True

    def go_next_word(self) -> bool:
        """Returns True if moving to the next word succeeded."""

        zone = self._get_current_zone()
        if zone is None:
            return False
        words = zone.get_words()
        if self._word_index < len(words) - 1:
            self._word_index += 1
            self._char_index = 0
            return True

        return self.go_next_zone()

    def go_previous_character(self) -> bool:
        """Returns True if moving to the previous character succeeded."""

        if self._char_index > 0:
            self._char_index -= 1
            return True

        if not self.go_previous_word():
            return False

        zone = self._get_current_zone()
        if zone is None:
            return False
        if words := zone.get_words():
            chars = words[self._word_index].get_characters()
            self._char_index = max(len(chars) - 1, 0)
        else:
            self._char_index = 0
        return True

    def go_next_character(self) -> bool:
        """Returns True if moving to the next character succeeded."""

        zone = self._get_current_zone()
        if zone is None:
            return False
        if words := zone.get_words():
            chars = words[self._word_index].get_characters()
            if self._char_index < (len(chars) - 1):
                self._char_index += 1
                return True

        return self.go_next_word()

    def go_up(self) -> bool:
        """Returns True if moving up succeeded."""

        rect = self._get_current_character_rect()
        target_x = rect.x + (rect.width / 2)
        if not self.go_previous_line():
            return False

        rect = self._get_current_character_rect()
        if rect.x + rect.width >= target_x:
            return True

        while self.go_next_character():
            rect = self._get_current_character_rect()
            if rect.x + rect.width >= target_x:
                break

        return True

    def go_down(self) -> bool:
        """Returns True if moving down succeeded."""

        rect = self._get_current_character_rect()
        target_x = rect.x + (rect.width / 2)
        if not self.go_next_line():
            return False

        rect = self._get_current_character_rect()
        if rect.x + rect.width >= target_x:
            return True

        while self.go_next_character():
            rect= self._get_current_character_rect()
            if rect.x + rect.width >= target_x:
                break

        return True
