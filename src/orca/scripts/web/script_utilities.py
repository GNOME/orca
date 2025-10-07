# Orca
#
# Copyright 2010 Joanmarie Diggs.
# Copyright 2014-2015 Igalia, S.L.
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

# pylint: disable=too-many-lines
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-boolean-expressions
# pylint: disable=too-many-branches
# pylint: disable=too-many-locals
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-statements
# pylint: disable=too-many-return-statements
# pylint: disable=wrong-import-position

"""Utilities for providing information about objects and events in web content."""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2010 Joanmarie Diggs." \
                "Copyright (c) 2014-2015 Igalia, S.L."
__license__   = "LGPL"

import functools
import re
import time
import urllib
from typing import TYPE_CHECKING

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from orca import debug
from orca import focus_manager
from orca import input_event_manager
from orca import script_utilities
from orca import settings_manager
from orca import speech_and_verbosity_manager
from orca.ax_component import AXComponent
from orca.ax_document import AXDocument
from orca.ax_hypertext import AXHypertext
from orca.ax_object import AXObject
from orca.ax_table import AXTable
from orca.ax_text import AXText
from orca.ax_utilities import AXUtilities
from orca.ax_utilities_debugging import AXUtilitiesDebugging

if TYPE_CHECKING:
    from .script import Script

class Utilities(script_utilities.Utilities):
    """Utilities for providing information about objects and events in web content."""

    def __init__(self, script: Script) -> None:
        super().__init__(script)
        self._cached_caret_contexts: dict[int, tuple[Atspi.Accessible, int]] = {}
        self._cached_prior_contexts: dict[int, tuple[Atspi.Accessible, int]] = {}
        self._cached_can_have_caret_context_decision: dict[int, bool] = {}
        self._cached_context_paths_roles_and_names: dict[int, tuple] = {}
        self._cached_paths: dict[int, list] = {}
        self._cached_in_document_content: dict[int, bool] = {}
        self._cached_in_top_level_web_app: dict[int, bool] = {}
        self._cached_is_text_block_element: dict[int, bool] = {}
        self._cached_is_content_editable_with_embedded_objects: dict[int, bool] = {}
        self._cached_has_grid_descendant: dict[int, bool] = {}
        self._cached_is_off_screen_label: dict[int, bool] = {}
        self._cached_element_lines_are_single_chars: dict[int, bool] = {}
        self._cached_element_lines_are_single_words: dict[int, bool] = {}
        self._cached_is_clickable_element: dict[int, bool] = {}
        self._cached_is_link: dict[int, bool] = {}
        self._cached_is_custom_image: dict[int, bool] = {}
        self._cached_is_useless_image: dict[int, bool] = {}
        self._cached_is_redundant_svg: dict[int, bool] = {}
        self._cached_is_useless_empty_element: dict[int, bool] = {}
        self._cached_has_name_and_action_and_no_useful_children: dict[int, bool] = {}
        self._cached_inferred_labels: dict[int, tuple[str, list[Atspi.Accessible]]] = {}
        self._cached_should_filter: dict[int, bool] = {}
        self._cached_should_infer_label_for: dict[int, bool] = {}
        self._cached_treat_as_text_object: dict[int, bool] = {}
        self._cached_treat_as_div: dict[int, bool] = {}
        self._cached_object_contents: list[tuple[Atspi.Accessible, int, int, str]] | None = None
        self._cached_sentence_contents: list[tuple[Atspi.Accessible, int, int, str]] | None = None
        self._cached_line_contents: list[tuple[Atspi.Accessible, int, int, str]] | None = None
        self._cached_word_contents: list[tuple[Atspi.Accessible, int, int, str]] | None = None
        self._cached_character_contents: list[tuple[Atspi.Accessible, int, int, str]] | None = None
        self._cached_find_container: Atspi.Accessible | None = None
        self._valid_child_roles: dict[Atspi.Role, list[Atspi.Role]] = \
            {Atspi.Role.LIST: [Atspi.Role.LIST_ITEM]}
        self._find_container: Atspi.Accessible | None = None

    def _cleanup_contexts(self) -> None:
        to_remove = []
        for key, [obj, _offset] in self._cached_caret_contexts.items():
            if not AXObject.is_valid(obj):
                to_remove.append(key)

        for key in to_remove:
            self._cached_caret_contexts.pop(key, None)

    def dump_cache(
        self,
        document: Atspi.Accessible | None = None,
        preserve_context: bool = False
    ) -> None:
        """Dumps all cached information about objects, and by default the caret context."""

        if not AXObject.is_valid(document):
            document = self.active_document()

        document_parent = AXObject.get_parent(document)
        context = self._cached_caret_contexts.get(hash(document_parent))
        tokens = ["WEB: Clearing all cached info for", document,
                  "Preserving context:", preserve_context, "Context:", context]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self.clear_caret_context(document)
        self.clear_cached_objects()

        if preserve_context and context:
            tokens = ["WEB: Preserving context of", context[0], ",", context[1]]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            self._cached_caret_contexts[hash(document_parent)] = context

    def clear_cached_objects(self) -> None:
        """Clears cached object details."""

        # TODO - JD: Should callers instead call dump_cache with preserve_context=True?

        debug.print_message(debug.LEVEL_INFO, "WEB: cleaning up cached objects", True)
        self._cached_in_document_content = {}
        self._cached_in_top_level_web_app = {}
        self._cached_is_text_block_element = {}
        self._cached_is_content_editable_with_embedded_objects = {}
        self._cached_has_grid_descendant = {}
        self._cached_is_off_screen_label = {}
        self._cached_element_lines_are_single_chars= {}
        self._cached_element_lines_are_single_words= {}
        self._cached_is_clickable_element = {}
        self._cached_is_link = {}
        self._cached_is_custom_image = {}
        self._cached_is_useless_image = {}
        self._cached_is_redundant_svg = {}
        self._cached_is_useless_empty_element = {}
        self._cached_has_name_and_action_and_no_useful_children = {}
        self._cached_inferred_labels = {}
        self._cached_should_filter = {}
        self._cached_should_infer_label_for = {}
        self._cached_treat_as_text_object = {}
        self._cached_treat_as_div = {}
        self._cached_paths = {}
        self._cached_context_paths_roles_and_names = {}
        self._cached_can_have_caret_context_decision = {}
        self._cleanup_contexts()
        self._cached_prior_contexts = {}
        self._cached_find_container = None

    def clear_content_cache(self) -> None:
        """Clears the cached line, word, object, character contents."""

        self._cached_object_contents = None
        self._cached_sentence_contents = None
        self._cached_line_contents = None
        self._cached_word_contents = None
        self._cached_character_contents = None

    def is_document(self, obj: Atspi.Accessible, exclude_document_frame: bool = True) -> bool:
        """Returns True if obj is a document."""

        if AXUtilities.is_document_web(obj) or AXUtilities.is_embedded(obj):
            return True

        if not exclude_document_frame:
            return AXUtilities.is_document_frame(obj)

        return False

    def in_document_content(self, obj: Atspi.Accessible | None = None) -> bool:
        if not obj:
            obj = focus_manager.get_manager().get_locus_of_focus()


        if self.is_document(obj):
            return True

        rv = self._cached_in_document_content.get(hash(obj))
        if rv is not None:
            return rv

        document = self.get_document_for_object(obj)
        rv = document is not None
        self._cached_in_document_content[hash(obj)] = rv
        return rv

    def grab_focus_when_setting_caret(self, obj: Atspi.Accessible) -> bool:
        """Returns true if we should grab focus when setting the caret."""

        # To avoid triggering popup lists.
        if AXUtilities.is_entry(obj):
            return False

        if AXUtilities.is_image(obj):
            return AXObject.find_ancestor(obj, AXUtilities.is_link) is not None

        if AXUtilities.is_heading(obj) and AXObject.get_child_count(obj) == 1:
            return self.is_link(AXObject.get_child(obj, 0))

        return AXUtilities.is_focusable(obj)

    def set_caret_position(
        self,
        obj: Atspi.Accessible,
        offset: int,
        document: Atspi.Accessible | None = None
    ) -> None:
        if self._script.get_flat_review_presenter().is_active():
            self._script.get_flat_review_presenter().quit()
        grab_focus = self.grab_focus_when_setting_caret(obj)

        obj, offset = self.first_context(obj, offset)
        self.set_caret_context(obj, offset, document)
        if self._script.focus_mode_is_sticky():
            return

        old_focus = focus_manager.get_manager().get_locus_of_focus()
        AXText.clear_all_selected_text(old_focus)
        focus_manager.get_manager().set_locus_of_focus(None, obj, notify_script=False)
        if grab_focus:
            AXObject.grab_focus(obj)

        AXText.set_caret_offset(obj, offset)
        if self._script.use_focus_mode(obj, old_focus) != self._script.in_focus_mode():
            self._script.toggle_presentation_mode(None)

        # TODO - JD: Can we remove this?
        if obj:
            AXObject.clear_cache(obj, False, "Set caret in object.")

    def in_find_container(self, obj: Atspi.Accessible | None = None) -> bool:
        if not obj:
            obj = focus_manager.get_manager().get_locus_of_focus()

        if self.in_document_content(obj):
            return False

        return super().in_find_container(obj)

    def set_caret_offset(self, obj: Atspi.Accessible, offset: int) -> None:
        """Sets the caret offset via AtspiText."""

        # TODO - JD: Audit callers and see if this can be merged into the default logic.

        self.set_caret_position(obj, offset)
        self._script.update_braille(obj)

    def next_context(
        self,
        obj: Atspi.Accessible | None = None,
        offset: int = -1,
        skip_space: bool = False,
        restrict_to: Atspi.Accessible | None = None # pylint: disable=unused-argument
    ) -> tuple[Atspi.Accessible | None, int]:
        """Returns the next viable/valid caret context given obj and offset."""

        if obj is None:
            obj, offset = self.get_caret_context()

        next_obj, next_offset = self.find_next_caret_in_order(obj, offset)
        if skip_space:
            while AXText.get_character_at_offset(next_obj, next_offset)[0].isspace():
                next_obj, next_offset = self.find_next_caret_in_order(next_obj, next_offset)

        return next_obj, next_offset

    def previous_context(
        self,
        obj: Atspi.Accessible | None = None,
        offset: int = -1,
        skip_space: bool = False,
        restrict_to: Atspi.Accessible | None = None # pylint: disable=unused-argument
    ) -> tuple[Atspi.Accessible | None, int]:
        """Returns the previous viable/valid caret context given obj and offset."""

        if obj is None:
            obj, offset = self.get_caret_context()

        prev_obj, prev_offset = self.find_previous_caret_in_order(obj, offset)
        if skip_space:
            while AXText.get_character_at_offset(prev_obj, prev_offset)[0].isspace():
                prev_obj, prev_offset = self.find_previous_caret_in_order(prev_obj, prev_offset)

        return prev_obj, prev_offset

    def last_context(self, root: Atspi.Accessible) -> tuple[Atspi.Accessible, int]:
        """Returns the last viable/valid caret context in root."""

        offset = 0
        if self.treat_as_text_object(root):
            offset = AXText.get_character_count(root) - 1

        def _is_in_root(o: Atspi.Accessible) -> bool:
            return o == root or AXObject.find_ancestor(o, lambda x: x == root) is not None

        obj = root
        while obj:
            last_obj, last_offset = self.next_context(obj, offset)
            if not (last_obj and _is_in_root(last_obj)):
                break
            obj, offset = last_obj, last_offset

        return obj, offset

    def contexts_are_on_same_line(
        self,
        a: tuple[Atspi.Accessible, int],
        b: tuple[Atspi.Accessible, int]
    ) -> bool:
        """Returns true if a and b are on the same line."""

        if a == b:
            return True

        a_obj, a_offset = a
        b_obj, b_offset = b
        a_extents = self._get_extents(a_obj, a_offset, a_offset + 1)
        b_extents = self._get_extents(b_obj, b_offset, b_offset + 1)
        return self._extents_are_on_same_line(a_extents, b_extents)

    @staticmethod
    def _extents_are_on_same_line(
        a: tuple[int, int, int, int],
        b: tuple[int, int, int, int],
        pixel_delta: int = 5
    ) -> bool:
        ### TODO - JD: Replace this with an AXComponent utility.
        if a == b:
            return True

        _a_x, a_y, a_width, a_height = a
        _b_x, b_y, b_width, b_height = b

        if a_width == 0 and a_height == 0:
            return b_y <= a_y <= b_y + b_height
        if b_width == 0 and b_height == 0:
            return a_y <= b_y <= a_y + a_height

        highest_bottom = min(a_y + a_height, b_y + b_height)
        lowest_top = max(a_y, b_y)
        if lowest_top >= highest_bottom:
            return False

        a_middle = a_y + a_height / 2
        b_middle = b_y + b_height / 2
        if abs(a_middle - b_middle) > pixel_delta:
            return False

        return True

    def _get_extents(
        self,
        obj: Atspi.Accessible | None,
        start_offset: int,
        end_offset: int
    ) -> tuple[int, int, int, int]:
        ### TODO - JD: Replace this with an AXComponent utility.
        if not obj:
            return (0, 0, 0, 0)

        result = (0, 0, 0, 0)
        if self.treat_as_text_object(obj) and 0 <= start_offset < end_offset:
            rect = AXText.get_range_rect(obj, start_offset, end_offset)
            result = (rect.x, rect.y, rect.width, rect.height)
            if not (result[0] and result[1] and result[2] == 0 and result[3] == 0 \
               and AXText.get_substring(obj, start_offset, end_offset).strip()):
                return result

            tokens = ["WEB: Suspected bogus range extents for",
                      obj, "(chars:", start_offset, ",", end_offset, "):", result]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        parent = AXObject.get_parent(obj)
        if (AXUtilities.is_menu(obj) or AXUtilities.is_list_item(obj)) \
            and (AXUtilities.is_combo_box(parent) or AXUtilities.is_list_box(parent)):
            ext = AXComponent.get_rect(parent)
        else:
            ext = AXComponent.get_rect(obj)

        return (ext.x, ext.y, ext.width, ext.height)

    def expand_eocs(
        self,
        obj: Atspi.Accessible,
        start_offset: int = 0,
        end_offset: int = -1
    ) -> str:
        """Expands the current object replacing embedded object characters with their text."""

        if not self.in_document_content(obj):
            return super().expand_eocs(obj, start_offset, end_offset)

        if self._has_grid_descendant(obj):
            tokens = ["WEB: not expanding EOCs:", obj, "has grid descendant"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return ""

        if not self.treat_as_text_object(obj):
            return ""

        if AXUtilities.is_math(obj) and AXObject.get_child_count(obj):
            utterances = self._script.speech_generator.generate_speech(obj)
            return self._script.speech_generator.utterances_to_string(utterances)

        return super().expand_eocs(obj, start_offset, end_offset)

    def _adjust_contents_for_language(
        self,
        contents: list[tuple[Atspi.Accessible, int, int, str]]
    ) -> list[tuple[Atspi.Accessible, int, int, str]]:
        rv = []
        for content in contents:
            split = self.split_substring_by_language(*content[0:3])
            for start, end, string, _language, _dialect in split:
                rv.append((content[0], start, end, string))

        return rv

    def get_language_and_dialect_from_text_attributes(
        self,
        obj: Atspi.Accessible | None,
        start_offset: int = 0,
        end_offset: int = -1
    ) -> list[tuple[int, int, str, str]]:
        rv = super().get_language_and_dialect_from_text_attributes(obj, start_offset, end_offset)
        if rv or obj is None:
            return rv

        # Embedded objects such as images and certain widgets won't implement the text interface
        # and thus won't expose text attributes. Therefore try to get the info from the parent.
        parent = AXObject.get_parent(obj)
        if parent is None or not self.in_document_content(parent):
            return rv

        start = AXHypertext.get_link_start_offset(obj)
        end = AXHypertext.get_link_end_offset(obj)
        language, dialect = self.get_language_and_dialect_for_substring(parent, start, end)
        rv.append((0, 1, language, dialect))

        return rv

    def find_object_in_contents(
        self,
        obj: Atspi.Accessible | None,
        offset: int,
        contents: list[tuple[Atspi.Accessible, int, int, str]],
        use_cache: bool = False
    ) -> int:
        """Returns the index of obj + offset in contents."""

        if not obj or not contents:
            return -1

        offset = max(0, offset)
        matches = [x for x in contents if x[0] == obj]
        match = [x for x in matches if x[1] <= offset < x[2]]
        if match and match[0] and match[0] in contents:
            return contents.index(match[0])
        if not use_cache:
            match = [x for x in matches if offset == x[2]]
            if match and match[0] and match[0] in contents:
                return contents.index(match[0])

        if not self.is_text_block_element(obj):
            return -1

        child = AXHypertext.find_child_at_offset(obj, offset)
        if child and not self.is_text_block_element(child):
            matches = [x for x in contents if x[0] == child]
            if len(matches) == 1:
                return contents.index(matches[0])

        return -1

    def treat_as_text_object(self, obj: Atspi.Accessible | None) -> bool:
        """Returns True if obj should be treated as a text object."""

        if not obj or AXObject.is_dead(obj):
            return False

        rv = self._cached_treat_as_text_object.get(hash(obj))
        if rv is not None:
            return rv

        if not AXObject.supports_text(obj):
            return False

        if not self.in_document_content(obj) or self._script.browse_mode_is_sticky():
            return True

        rv = AXText.get_character_count(obj) > 0 or AXUtilities.is_editable(obj)
        if rv and self._treat_object_as_whole(obj, -1) and AXObject.get_name(obj) \
           and not self._is_cell_with_name_from_header(obj):
            tokens = ["WEB: Treating", obj, "as non-text: named object treated as whole."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            rv = False

        elif rv and not AXUtilities.is_live_region(obj):
            not_text_roles = [Atspi.Role.LIST_BOX, Atspi.Role.TABLE, Atspi.Role.TABLE_ROW]
            role = AXObject.get_role(obj)
            if rv and role in not_text_roles:
                tokens = ["WEB: Treating", obj, "as non-text due to role."]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                rv = False
            if rv and (AXUtilities.is_hidden(obj) or self._is_off_screen_label(obj)):
                tokens = ["WEB: Treating", obj, "as non-text: is hidden or off-screen label."]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                rv = False
            if rv and self._is_non_navigable_embedded_document(obj):
                tokens = ["WEB: Treating", obj, "as non-text: is non-navigable embedded document."]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                rv = False
            if rv and self._is_fake_placeholder_for_entry(obj):
                tokens = ["WEB: Treating", obj, "as non-text: is fake placeholder for entry."]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                rv = False

        self._cached_treat_as_text_object[hash(obj)] = rv
        return rv

    def _has_name_and_action_and_no_useful_children(self, obj: Atspi.Accessible) -> bool:
        if not (obj and self.in_document_content(obj)):
            return False

        rv = self._cached_has_name_and_action_and_no_useful_children.get(hash(obj))
        if rv is not None:
            return rv

        rv = False
        if AXUtilities.has_explicit_name(obj) and AXObject.supports_action(obj):
            for child in AXObject.iter_children(obj):
                if not self._is_useless_empty_element(child) or self._is_useless_image(child):
                    break
            else:
                rv = True

        if rv:
            tokens = ["WEB:", obj, "has name and action and no useful children"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._cached_has_name_and_action_and_no_useful_children[hash(obj)] = rv
        return rv

    def _treat_object_as_whole(self, obj: Atspi.Accessible, offset: int | None = None) -> bool:
        always = [Atspi.Role.BUTTON,
                  Atspi.Role.CHECK_BOX,
                  Atspi.Role.CHECK_MENU_ITEM,
                  Atspi.Role.LIST_BOX,
                  Atspi.Role.MENU_ITEM,
                  Atspi.Role.PAGE_TAB,
                  Atspi.Role.RADIO_MENU_ITEM,
                  Atspi.Role.RADIO_BUTTON,
                  Atspi.Role.TOGGLE_BUTTON]

        descendable = [Atspi.Role.MENU,
                       Atspi.Role.MENU_BAR,
                       Atspi.Role.TOOL_BAR,
                       Atspi.Role.TREE_ITEM]

        role = AXObject.get_role(obj)
        if role in always:
            return True

        if role in descendable:
            if self._script.in_focus_mode():
                return True

            # This should cause us to initially stop at the large containers before
            # allowing the user to drill down into them in browse mode.
            return offset == -1

        if role == Atspi.Role.ENTRY:
            if AXObject.get_child_count(obj) == 1 \
              and self._is_fake_placeholder_for_entry(AXObject.get_child(obj, 0)):
                return True
            return False

        if AXUtilities.is_editable(obj):
            return False

        if role == Atspi.Role.TABLE_CELL:
            if self.is_focus_mode_widget(obj):
                return not self._script.browse_mode_is_sticky()
            if self._has_name_and_action_and_no_useful_children(obj):
                return True

        if role in [Atspi.Role.COLUMN_HEADER, Atspi.Role.ROW_HEADER] \
           and AXUtilities.has_explicit_name(obj):
            return True

        if role == Atspi.Role.COMBO_BOX:
            return True

        if role in [Atspi.Role.EMBEDDED, Atspi.Role.TREE, Atspi.Role.TREE_TABLE]:
            return not self._script.browse_mode_is_sticky()

        if role == Atspi.Role.LINK:
            return AXUtilities.has_explicit_name(obj) or self.has_useless_canvas_descendant(obj)

        if self._is_non_navigable_embedded_document(obj):
            return True

        if self._is_fake_placeholder_for_entry(obj):
            return True

        if self.is_custom_image(obj):
            return True

        # Example: Some StackExchange instances have a focusable "note"/comment role
        # with a name (e.g. "Accepted"), and a single child div which is empty.
        if role in self._text_block_element_roles() and AXUtilities.is_focusable(obj) \
           and AXUtilities.has_explicit_name(obj):
            for child in AXObject.iter_children(obj):
                if not self._is_useless_empty_element(child):
                    return False
            return True

        return False

    def _get_text_at_offset(
        self,
        obj: Atspi.Accessible,
        offset: int,
        granularity: Atspi.TextGranularity
    ) -> tuple[str, int, int]:
        def string_for_debug(x):
            return x.replace("\ufffc", "[OBJ]").replace("\n", "\\n")

        if not obj:
            tokens = ["WEB:", granularity, f"at offset {offset} for", obj, ":",
                      "'', Start: 0, End: 0. (obj is None)"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return '', 0, 0

        if not self.treat_as_text_object(obj):
            tokens = ["WEB:", granularity, f"at offset {offset} for", obj, ":",
                      "'', Start: 0, End: 1. (treat_as_text_object() returned False)"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return '', 0, 1

        all_text = AXText.get_all_text(obj)
        if granularity is None:
            string, start, end = all_text, 0, len(all_text)
            s = string_for_debug(string)
            tokens = ["WEB:", granularity, f"at offset {offset} for", obj, ":",
                      f"'{s}', Start: {start}, End: {end}."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return string, start, end

        if granularity == Atspi.TextGranularity.SENTENCE and not AXUtilities.is_editable(obj):
            if AXObject.get_role(obj) in [Atspi.Role.LIST_ITEM, Atspi.Role.HEADING] \
               or not (re.search(r"\w", all_text) and self.is_text_block_element(obj)):
                string, start, end = all_text, 0, len(all_text)
                s = string_for_debug(string)
                tokens = ["WEB:", granularity, f"at offset {offset} for", obj, ":",
                          f"'{s}', Start: {start}, End: {end}."]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                return string, start, end

        if granularity == Atspi.TextGranularity.LINE and self.treat_as_end_of_line(obj, offset):
            offset -= 1
            tokens = ["WEB: Line sought for", obj, "at end of text. Adjusting offset to",
                      offset, "."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        offset = max(0, offset)
        if granularity == Atspi.TextGranularity.LINE:
            string, start, end = AXText.get_line_at_offset(obj, offset)
        elif granularity == Atspi.TextGranularity.SENTENCE:
            string, start, end = AXText.get_sentence_at_offset(obj, offset)
        elif granularity == Atspi.TextGranularity.WORD:
            string, start, end = AXText.get_word_at_offset(obj, offset)
        elif granularity == Atspi.TextGranularity.CHAR:
            string, start, end = AXText.get_character_at_offset(obj, offset)
        else:
            string, start, end = AXText.get_line_at_offset(obj, offset)

        s = string_for_debug(string)
        tokens = ["WEB:", granularity, f"at offset {offset} for", obj, ":",
                  f"'{s}', Start: {start}, End: {end}."]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return string, start, end

    def _get_contents_for_obj(
        self,
        obj: Atspi.Accessible,
        offset: int,
        granularity: Atspi.TextGranularity
    ) -> list[tuple[Atspi.Accessible, int, int, str]]:
        tokens = ["WEB: Attempting to get contents for", obj, granularity]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        if not obj:
            return []

        if granularity == Atspi.TextGranularity.SENTENCE and AXUtilities.is_time(obj):
            string = AXText.get_all_text(obj)
            if string:
                return [(obj, 0, len(string), string)]

        if granularity == Atspi.TextGranularity.LINE:
            if AXUtilities.is_math_related(obj):
                math = AXObject.find_ancestor_inclusive(obj, AXUtilities.is_math)
                return [(math, 0, 1, '')]

            treat_as_text = self.treat_as_text_object(obj)
            if self._element_lines_are_single_chars(obj):
                if AXObject.get_name(obj) and treat_as_text:
                    tokens = ["WEB: Returning name as contents for", obj, "(single-char lines)"]
                    debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                    return [(obj, 0, AXText.get_character_count(obj), AXObject.get_name(obj))]

                tokens = ["WEB: Returning all text as contents for", obj, "(single-char lines)"]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                granularity = None

            if self._element_lines_are_single_words(obj):
                if AXObject.get_name(obj) and treat_as_text:
                    tokens = ["WEB: Returning name as contents for", obj, "(single-word lines)"]
                    debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                    return [(obj, 0, AXText.get_character_count(obj), AXObject.get_name(obj))]

                tokens = ["WEB: Returning all text as contents for", obj, "(single-word lines)"]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                granularity = None

        if AXUtilities.is_internal_frame(obj) and AXObject.get_child_count(obj) == 1:
            return self._get_contents_for_obj(AXObject.get_child(obj, 0), 0, granularity)

        string, start, end = self._get_text_at_offset(obj, offset, granularity)
        if not string:
            return [(obj, start, end, string)]

        string_offset = max(0, offset - start)
        try:
            char = string[string_offset]
        except IndexError:
            msg = f"WEB: Could not get char {string_offset} for '{string}'"
            debug.print_message(debug.LEVEL_INFO, msg, True)
        else:
            if char == "\ufffc":
                if child := AXHypertext.find_child_at_offset(obj, offset):
                    return self._get_contents_for_obj(child, 0, granularity)

        ranges = [m.span() for m in re.finditer("[^\ufffc]+", string)]
        strings = list(filter(lambda x: x[0] <= string_offset <= x[1], ranges))
        if len(strings) == 1:
            range_start, range_end = strings[0]
            start += range_start
            string = string[range_start:range_end]
            end = start + len(string)

        if granularity in [Atspi.TextGranularity.WORD, Atspi.TextGranularity.CHAR]:
            return [(obj, start, end, string)]

        return self._adjust_contents_for_language([(obj, start, end, string)])

    def get_sentence_contents_at_offset(
        self,
        obj: Atspi.Accessible,
        offset: int,
        use_cache: bool = True
    ) -> list[tuple[Atspi.Accessible, int, int, str]]:
        """Returns the sentence contents for the specified offset."""

        self._cached_can_have_caret_context_decision = {}
        rv = self._get_sentence_contents_at_offset_internal(obj, offset, use_cache)
        self._cached_can_have_caret_context_decision = {}
        return rv

    def _get_sentence_contents_at_offset_internal(
        self,
        obj: Atspi.Accessible,
        offset: int,
        use_cache: bool = True
    ) -> list[tuple[Atspi.Accessible, int, int, str]]:
        if not obj:
            return []

        offset = max(0, offset)

        if use_cache and self._cached_sentence_contents:
            if self.find_object_in_contents(
                    obj, offset, self._cached_sentence_contents, use_cache=True) != -1:
                return self._cached_sentence_contents or []

        granularity = Atspi.TextGranularity.SENTENCE
        objects = self._get_contents_for_obj(obj, offset, granularity)
        if AXUtilities.is_editable(obj):
            if AXUtilities.is_focused(obj):
                return objects
            if self.is_content_editable_with_embedded_objects(obj):
                return objects

        def _treat_as_sentence_end(x):
            x_obj, x_start, x_end, x_string = x
            if not self.is_text_block_element(x_obj):
                return False

            if self.treat_as_text_object(x_obj) and 0 < AXText.get_character_count(x_obj) <= x_end:
                return True

            if 0 <= x_start <= 5:
                x_string = " ".join(x_string.split()[1:])

            return AXText.has_sentence_ending(x_string)

        # Check for things in the same sentence before this object.
        first_obj, first_start, _first_end, first_string = objects[0]
        while first_obj and first_string:
            if self.is_text_block_element(first_obj):
                if first_start == 0:
                    break
            elif self.is_text_block_element(AXObject.get_parent(first_obj)):
                if AXHypertext.get_character_offset_in_parent(first_obj) == 0:
                    break

            prev_object, prev_offset = self.find_previous_caret_in_order(first_obj, first_start)
            on_left = self._get_contents_for_obj(prev_object, prev_offset, granularity)
            on_left = list(filter(lambda x: x not in objects, on_left))
            ends_on_left = list(filter(_treat_as_sentence_end, on_left))
            if ends_on_left:
                i = on_left.index(ends_on_left[-1])
                on_left = on_left[i+1:]

            if not on_left:
                break

            objects[0:0] = on_left
            first_obj, first_start, _first_end, first_string = objects[0]

        # Check for things in the same sentence after this object.
        while not _treat_as_sentence_end(objects[-1]):
            last_obj, _last_start, last_end, _last_string = objects[-1]
            next_obj, next_offset = self.find_next_caret_in_order(last_obj, last_end - 1)
            on_right = self._get_contents_for_obj(next_obj, next_offset, granularity)
            on_right = list(filter(lambda x: x not in objects, on_right))
            if not on_right:
                break

            objects.extend(on_right)

        if use_cache:
            self._cached_sentence_contents = objects

        return objects

    def get_character_contents_at_offset(
        self,
        obj: Atspi.Accessible,
        offset: int,
        use_cache: bool = True
    ) -> list[tuple[Atspi.Accessible, int, int, str]]:
        """Returns the character contents for obj at the specified offset."""

        self._cached_can_have_caret_context_decision = {}
        rv = self._get_character_contents_at_offset_internal(obj, offset, use_cache)
        self._cached_can_have_caret_context_decision = {}
        return rv

    def _get_character_contents_at_offset_internal(
        self,
        obj: Atspi.Accessible,
        offset: int,
        use_cache: bool = True
    ) -> list[tuple[Atspi.Accessible, int, int, str]]:
        if not obj:
            return []

        offset = max(0, offset)

        if use_cache and self._cached_character_contents:
            if self.find_object_in_contents(
                    obj, offset, self._cached_character_contents, use_cache=True) != -1:
                return self._cached_character_contents or []

        granularity = Atspi.TextGranularity.CHAR
        objects = self._get_contents_for_obj(obj, offset, granularity)
        if use_cache:
            self._cached_character_contents = objects

        return objects

    def get_word_contents_at_offset(
        self,
        obj: Atspi.Accessible,
        offset: int = 0,
        use_cache: bool = True
    ) -> list[tuple[Atspi.Accessible, int, int, str]]:
        """Returns a list of (obj, start, end, string) tuples for the word at offset."""

        self._cached_can_have_caret_context_decision = {}
        rv = self._get_word_contents_at_offset(obj, offset, use_cache)
        self._cached_can_have_caret_context_decision = {}
        return rv

    def _get_word_contents_at_offset(
        self,
        obj: Atspi.Accessible,
        offset: int,
        use_cache: bool = True
    ) -> list[tuple[Atspi.Accessible, int, int, str]]:
        if not obj:
            return []

        offset = max(0, offset)

        if use_cache and self._cached_word_contents:
            if self.find_object_in_contents(
                    obj, offset, self._cached_word_contents, use_cache=True) != -1:
                self._debug_contents_info(
                    obj, offset, self._cached_word_contents, "Word (cached)")
                return self._cached_word_contents or []

        granularity = Atspi.TextGranularity.WORD
        objects = self._get_contents_for_obj(obj, offset, granularity)
        extents = self._get_extents(obj, offset, offset + 1)

        def _include(x):
            if x in objects:
                return False

            if AXUtilities.is_text_input(obj):
                return False

            x_obj, x_start, x_end, x_string = x
            if x_start == x_end or not x_string:
                return False

            if AXUtilities.is_table_cell_or_header(obj) \
               and AXUtilities.is_table_cell_or_header(x_obj) and obj != x_obj:
                return False

            x_extents = self._get_extents(x_obj, x_start, x_start + 1)
            return self._extents_are_on_same_line(extents, x_extents)

        # Check for things in the same word to the left of this object.
        first_obj, first_start, _first_end, first_string = objects[0]
        prev_obj, prev_offset = self.find_previous_caret_in_order(first_obj, first_start)
        while prev_obj and first_string and prev_obj != first_obj:
            char = AXText.get_character_at_offset(prev_obj, prev_offset)[0]
            if not char or char.isspace():
                break

            on_left = self._get_contents_for_obj(prev_obj, prev_offset, granularity)
            on_left = list(filter(_include, on_left))
            if not on_left:
                break

            if self._content_is_subset_of(objects[0], on_left[-1]):
                objects.pop(0)

            objects[0:0] = on_left
            first_obj, first_start, _first_end, first_string = objects[0]
            prev_obj, prev_offset = self.find_previous_caret_in_order(first_obj, first_start)

        # Check for things in the same word to the right of this object.
        last_obj, _last_start, last_end, last_string = objects[-1]
        while last_obj and last_string and not last_string[-1].isspace():
            next_obj, next_offset = self.find_next_caret_in_order(last_obj, last_end - 1)
            if next_obj == last_obj:
                break

            on_right = self._get_contents_for_obj(next_obj, next_offset, granularity)
            if on_right and self._content_is_subset_of(objects[0], on_right[-1]):
                on_right = on_right[0:-1]

            on_right = list(filter(_include, on_right))
            if not on_right:
                break

            objects.extend(on_right)
            last_obj, _last_start, last_end, last_string = objects[-1]

        # We want to treat the list item marker as its own word.
        first_obj, first_start, _first_end, first_string = objects[0]
        if first_start == 0 and AXUtilities.is_list_item(first_obj):
            objects = [objects[0]]

        if use_cache:
            self._cached_word_contents = objects

        self._debug_contents_info(obj, offset, objects, "Word (not cached)")
        return objects

    def get_object_contents_at_offset(
        self,
        obj: Atspi.Accessible,
        offset: int = 0,
        use_cache: bool = True
    ) -> list[tuple[Atspi.Accessible, int, int, str]]:
        """Returns a list of (obj, start, end, string) tuples for the object at offset."""

        self._cached_can_have_caret_context_decision = {}
        rv = self._get_object_contents_at_offset(obj, offset, use_cache)
        self._cached_can_have_caret_context_decision = {}
        return rv

    def _get_object_contents_at_offset(
        self,
        obj: Atspi.Accessible,
        offset: int = 0,
        use_cache: bool = True
    ) -> list[tuple[Atspi.Accessible, int, int, str]]:

        if obj is None:
            return []

        if AXObject.is_dead(obj):
            msg = "ERROR: Cannot get object contents at offset for dead object."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return []

        offset = max(0, offset)

        if use_cache and self._cached_object_contents:
            if self.find_object_in_contents(
                    obj, offset, self._cached_object_contents, use_cache=True) != -1:
                self._debug_contents_info(
                    obj, offset, self._cached_object_contents, "Object (cached)")
                return self._cached_object_contents or []

        obj_is_landmark = AXUtilities.is_landmark(obj)

        def _is_in_object(x):
            if not x:
                return False
            if x == obj:
                return True
            return _is_in_object(AXObject.get_parent(x))

        def _include(x):
            if x in objects:
                return False

            x_obj, x_start, x_end, _x_string = x
            if x_start == x_end:
                return False

            if obj_is_landmark and AXUtilities.is_landmark(x_obj) and obj != x_obj:
                return False

            return _is_in_object(x_obj)

        objects = self._get_contents_for_obj(obj, offset, None)
        if not objects:
            tokens = ["ERROR: Cannot get object contents for", obj, f"at offset {offset}"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return []

        last_obj, _last_start, last_end, _last_string = objects[-1]
        next_obj, next_offset = self.find_next_caret_in_order(last_obj, last_end - 1)
        while next_obj:
            on_right = self._get_contents_for_obj(next_obj, next_offset, None)
            on_right = list(filter(_include, on_right))
            if not on_right:
                break

            objects.extend(on_right)
            last_obj, last_end = objects[-1][0], objects[-1][2]
            next_obj, next_offset = self.find_next_caret_in_order(last_obj, last_end - 1)

        if use_cache:
            self._cached_object_contents = objects

        self._debug_contents_info(obj, offset, objects, "Object (not cached)")
        return objects

    def _content_is_subset_of(
        self,
        content_a: tuple[Atspi.Accessible, int, int, str],
        content_b: tuple[Atspi.Accessible, int, int, str]
    ) -> bool:
        obj_a, start_a, end_a, _string_a = content_a
        obj_b, start_b, end_b, _string_b = content_b
        if obj_a == obj_b:
            set_a = set(range(start_a, end_a))
            set_b = set(range(start_b, end_b))
            return set_a.issubset(set_b)

        return False

    def _debug_contents_info(
        self,
        obj: Atspi.Accessible,
        offset: int,
        contents: list[tuple[Atspi.Accessible, int, int, str]],
        contents_msg: str = ""
    ) -> None:
        if debug.LEVEL_INFO < debug.debugLevel:
            return

        tokens = ["WEB: ", contents_msg, "for", obj, "at offset", offset, ":"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        indent = " " * 8
        for i, (acc, start, end, string) in enumerate(contents):
            extents = self._get_extents(acc, start, end)
            msg = f"     {i}. chars: {start}-{end}: '{string}' extents={extents}\n"
            msg += AXUtilitiesDebugging.object_details_as_string(acc, indent, False)
            debug.print_message(debug.LEVEL_INFO, msg, True)

    def treat_as_end_of_line(self, obj: Atspi.Accessible, offset: int) -> bool:
        """Returns true if the offset in obj should be treated as the end of the line."""

        if not self.is_content_editable_with_embedded_objects(obj):
            return False

        if not AXObject.supports_text(obj):
            return False

        if self.is_document(obj):
            return False

        if offset == AXText.get_character_count(obj):
            tokens = ["WEB: ", obj, "offset", offset, "is end of line: offset is characterCount"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        # Do not treat a literal newline char as the end of line. When there is an
        # actual newline character present, user agents should give us the right value
        # for the line at that offset. Here we are trying to figure out where asking
        # for the line at offset will give us the next line rather than the line where
        # the cursor is physically blinking.
        char = AXText.get_character_at_offset(obj, offset)[0]
        if char == "\ufffc":
            prev_extents = self._get_extents(obj, offset - 1, offset)
            this_extents = self._get_extents(obj, offset, offset + 1)
            same_line = self._extents_are_on_same_line(prev_extents, this_extents)
            tokens = ["WEB: ", obj, "offset", offset, "is [obj]. Same line: ",
                      same_line, "Is end of line: ", not same_line]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return not same_line

        return False

    def get_line_contents_at_offset(
        self,
        obj: Atspi.Accessible,
        offset: int,
        layout_mode: bool | None = None,
        use_cache: bool = True
    ) -> list[tuple[Atspi.Accessible, int, int, str]]:
        self._cached_can_have_caret_context_decision = {}
        rv = self._get_line_contents_at_offset(obj, offset, layout_mode, use_cache)
        self._cached_can_have_caret_context_decision = {}
        return rv

    def _get_line_contents_at_offset(
        self,
        obj: Atspi.Accessible,
        offset: int,
        layout_mode: bool | None = None,
        use_cache: bool = True
    ) -> list[tuple[Atspi.Accessible, int, int, str]]:
        start_time = time.time()
        if not obj:
            return []

        if AXObject.is_dead(obj):
            msg = "ERROR: Cannot get line contents at offset for dead object."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return []

        offset = max(0, offset)
        if (AXUtilities.is_tool_bar(obj) or AXUtilities.is_menu_bar(obj)) \
                and not self._treat_object_as_whole(obj):
            child = AXHypertext.find_child_at_offset(obj, offset)
            if child:
                obj = child
                offset = 0

        if use_cache and self._cached_line_contents:
            if self.find_object_in_contents(
                    obj, offset, self._cached_line_contents, use_cache=True) != -1:
                self._debug_contents_info(
                    obj, offset, self._cached_line_contents, "Line (cached)")
                return self._cached_line_contents or []

        if layout_mode is None:
            layout_mode = settings_manager.get_manager().get_setting("layoutMode") \
                or self._script.in_focus_mode()

        objects = []
        if offset > 0 and self.treat_as_end_of_line(obj, offset):
            extents = self._get_extents(obj, offset - 1, offset)
        else:
            extents = self._get_extents(obj, offset, offset + 1)

        if AXObject.find_ancestor_inclusive(obj, AXUtilities.is_inline_list_item) is not None:
            container = AXObject.find_ancestor(obj, AXUtilities.is_list)
            if container:
                extents = self._get_extents(container, 0, 1)

        obj_banner = AXObject.find_ancestor(obj, AXUtilities.is_landmark_banner)
        obj_row = AXObject.find_ancestor_inclusive(obj, AXUtilities.is_table_row)

        def _include(x):
            if x in objects:
                return False

            x_obj, x_start, x_end, _x_string = x
            if x_start == x_end:
                return False

            x_extents = self._get_extents(x_obj, x_start, x_start + 1)

            if obj != x_obj:
                if AXUtilities.is_landmark(obj) and AXUtilities.is_landmark(x_obj):
                    return False
                if self.is_link(obj) and self.is_link(x_obj):
                    x_obj_banner = AXObject.find_ancestor(x_obj, AXUtilities.is_landmark_banner)
                    if (obj_banner or x_obj_banner) and obj_banner != x_obj_banner:
                        return False
                    if abs(extents[0] - x_extents[0]) <= 1 and abs(extents[1] - x_extents[1]) <= 1:
                        # This happens with dynamic skip links such as found on Wikipedia.
                        return False
                elif self._is_block_list_descendant(obj) != self._is_block_list_descendant(x_obj):
                    return False
                elif AXUtilities.is_tree_related(obj) and AXUtilities.is_tree_related(x_obj):
                    return False
                elif AXUtilities.is_heading(obj) and AXComponent.has_no_size(obj):
                    return False
                elif AXUtilities.is_heading(x_obj) and AXComponent.has_no_size(x_obj):
                    return False

            if AXUtilities.is_math(x_obj) or AXUtilities.is_math_related(obj):
                on_same_line = self._extents_are_on_same_line(extents, x_extents, extents[3])
            elif AXObject.find_ancestor_inclusive(
                    x_obj, AXUtilities.is_subscript_or_superscript_text):
                on_same_line = self._extents_are_on_same_line(extents, x_extents, x_extents[3])
            else:
                on_same_line = self._extents_are_on_same_line(extents, x_extents)
            return on_same_line

        granularity = Atspi.TextGranularity.LINE
        objects = self._get_contents_for_obj(obj, offset, granularity)
        if not layout_mode:
            if use_cache:
                self._cached_line_contents = objects

            self._debug_contents_info(obj, offset, objects, "Line (not layout mode)")
            return objects

        if not (objects and objects[0]):
            tokens = ["WEB: Error. No objects found for", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return []

        first_obj, first_start, first_end, first_string = objects[0]
        if (extents[2] == 0 and extents[3] == 0) or AXUtilities.is_math_related(first_obj):
            extents = self._get_extents(first_obj, first_start, first_end)

        last_obj, _last_start, last_end, _last_string = objects[-1]
        if AXUtilities.is_math(last_obj):
            last_obj, last_end = self.last_context(last_obj)
            last_end += 1

        document = self.get_document_for_object(obj)
        prev_obj, prev_offset = self.find_previous_caret_in_order(first_obj, first_start)
        next_obj, next_offset = self.find_next_caret_in_order(last_obj, last_end - 1)

        # Check for things on the same line to the left of this object.
        prev_start_time = time.time()
        while prev_obj and self.get_document_for_object(prev_obj) == document:
            char = AXText.get_character_at_offset(prev_obj, prev_offset)[0]
            if char.isspace():
                prev_obj, prev_offset = self.find_previous_caret_in_order(prev_obj, prev_offset)

            char = AXText.get_character_at_offset(prev_obj, prev_offset)[0]
            if char == "\n" and first_obj == prev_obj:
                break

            if obj_row != AXObject.find_ancestor_inclusive(prev_obj, AXUtilities.is_table_row):
                break

            on_left = self._get_contents_for_obj(prev_obj, prev_offset, granularity)
            on_left = list(filter(_include, on_left))
            if not on_left:
                break

            if self._content_is_subset_of(objects[0], on_left[-1]):
                objects.pop(0)

            objects[0:0] = on_left
            first_obj, first_start = objects[0][0], objects[0][1]
            prev_obj, prev_offset = self.find_previous_caret_in_order(first_obj, first_start)

        prev_end_time = time.time()
        msg = f"INFO: Time to get line contents on left: {prev_end_time - prev_start_time:.4f}s"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        # Check for things on the same line to the right of this object.
        next_start_time = time.time()
        while next_obj and self.get_document_for_object(next_obj) == document:
            char = AXText.get_character_at_offset(next_obj, next_offset)[0]
            if char.isspace():
                next_obj, next_offset = self.find_next_caret_in_order(next_obj, next_offset)

            char = AXText.get_character_at_offset(next_obj, next_offset)[0]
            if char == "\n" and last_obj == next_obj:
                break

            if obj_row != AXObject.find_ancestor_inclusive(next_obj, AXUtilities.is_table_row):
                break

            on_right = self._get_contents_for_obj(next_obj, next_offset, granularity)
            if on_right and self._content_is_subset_of(objects[0], on_right[-1]):
                on_right = on_right[0:-1]

            on_right = list(filter(_include, on_right))
            if not on_right:
                break

            objects.extend(on_right)
            last_obj, last_end = objects[-1][0], objects[-1][2]
            if AXUtilities.is_math(last_obj):
                last_obj, last_end = self.last_context(last_obj)
                last_end += 1

            next_obj, next_offset = self.find_next_caret_in_order(last_obj, last_end - 1)

        next_end_time = time.time()
        msg = f"INFO: Time to get line contents on right: {next_end_time - next_start_time:.4f}s"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        first_obj, first_start, first_end, first_string = objects[0]
        if first_string == "\n" and len(objects) > 1:
            objects.pop(0)

        if use_cache:
            self._cached_line_contents = objects

        msg = f"INFO: Time to get line contents: {time.time() - start_time:.4f}s"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        self._debug_contents_info(obj, offset, objects, "Line (layout mode)")

        self._cached_can_have_caret_context_decision = {}
        return objects

    def get_previous_line_contents(
        self,
        obj: Atspi.Accessible | None = None,
        offset: int = -1,
        layout_mode: bool | None = None,
        use_cache: bool = True
    ) -> list[tuple[Atspi.Accessible, int, int, str]]:
        """Returns a list of (obj, start, end, string) tuples for the previous line."""

        if obj is None:
            obj, offset = self.get_caret_context()

        tokens = ["WEB: Current context is: ", obj, ", ", offset]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if not AXObject.is_valid(obj):
            tokens = ["WEB: Current context obj", obj, "is not valid. Clearing cache."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            self.clear_cached_objects()

            obj, offset = self.get_caret_context()
            tokens = ["WEB: Now Current context is: ", obj, ", ", offset]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        line = self.get_line_contents_at_offset(obj, offset, layout_mode, use_cache)
        if not (line and line[0]):
            return []

        first_obj, first_offset = line[0][0], line[0][1]
        tokens = ["WEB: First context on line is: ", first_obj, ", ", first_offset]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        skip_space = not speech_and_verbosity_manager.get_manager().get_speak_blank_lines()
        obj, offset = self.previous_context(first_obj, first_offset, skip_space)
        if not obj and first_obj:
            tokens = ["WEB: Previous context is: ", obj, ", ", offset, ". Trying again."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            self.clear_cached_objects()
            obj, offset = self.previous_context(first_obj, first_offset, skip_space)

        tokens = ["WEB: Previous context is: ", obj, ", ", offset]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        contents = self.get_line_contents_at_offset(obj, offset, layout_mode, use_cache)
        if not contents:
            tokens = ["WEB: Could not get line contents for ", obj, ", ", offset]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return []

        if line == contents:
            obj, offset = self.previous_context(obj, offset, True)
            tokens = ["WEB: Got same line. Trying again with ", obj, ", ", offset]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            contents = self.get_line_contents_at_offset(obj, offset, layout_mode, use_cache)

        if line == contents:
            start = AXHypertext.get_link_start_offset(obj)
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            if start >= 0:
                parent = AXObject.get_parent(obj)
                obj, offset = self.previous_context(parent, start, True)
                tokens = ["WEB: Trying again with", obj, ", ", offset]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                contents = self.get_line_contents_at_offset(obj, offset, layout_mode, use_cache)

        return contents

    def get_next_line_contents(
        self,
        obj: Atspi.Accessible | None = None,
        offset: int = -1,
        layout_mode: bool | None = None,
        use_cache: bool = True
    ) -> list[tuple[Atspi.Accessible, int, int, str]]:
        """Returns a list of (obj, start, end, string) tuples for the next line."""

        if obj is None:
            obj, offset = self.get_caret_context()

        tokens = ["WEB: Current context is: ", obj, ", ", offset]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if not AXObject.is_valid(obj):
            tokens = ["WEB: Current context obj", obj, "is not valid. Clearing cache."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            self.clear_cached_objects()

            obj, offset = self.get_caret_context()
            tokens = ["WEB: Now Current context is: ", obj, ", ", offset]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        line = self.get_line_contents_at_offset(obj, offset, layout_mode, use_cache)
        if not (line and line[0]):
            return []

        last_obj, last_offset = line[-1][0], line[-1][2] - 1
        math = AXObject.find_ancestor_inclusive(last_obj, AXUtilities.is_math)
        if math:
            last_obj, last_offset = self.last_context(math)

        tokens = ["WEB: Last context on line is: ", last_obj, ", ", last_offset]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        skip_space = not speech_and_verbosity_manager.get_manager().get_speak_blank_lines()
        obj, offset = self.next_context(last_obj, last_offset, skip_space)
        if not obj and last_obj:
            tokens = ["WEB: Next context is: ", obj, ", ", offset, ". Trying again."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            self.clear_cached_objects()
            obj, offset = self.next_context(last_obj, last_offset, skip_space)

        tokens = ["WEB: Next context is: ", obj, ", ", offset]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        contents = self.get_line_contents_at_offset(obj, offset, layout_mode, use_cache)
        if line == contents:
            obj, offset = self.next_context(obj, offset, True)
            tokens = ["WEB: Got same line. Trying again with ", obj, ", ", offset]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            contents = self.get_line_contents_at_offset(obj, offset, layout_mode, use_cache)

        if line == contents:
            end = AXHypertext.get_link_end_offset(obj)
            if end >= 0:
                parent = AXObject.get_parent(obj)
                obj, offset = self.next_context(parent, end, True)
                tokens = ["WEB: Trying again with", obj, ", ", offset]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                contents = self.get_line_contents_at_offset(obj, offset, layout_mode, use_cache)

        if not contents:
            tokens = ["WEB: Could not get line contents for ", obj, ", ", offset]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return []

        return contents

    def _find_selection_boundary_object(
        self,
        root: Atspi.Accessible,
        find_start: bool = True
    ) -> Atspi.Accessible | None:
        string = AXText.get_selected_text(root)[0]
        if not string:
            return None

        if find_start and not string.startswith("\ufffc"):
            return root

        if not find_start and not string.endswith("\ufffc"):
            return root

        indices = list(range(AXObject.get_child_count(root)))
        if not find_start:
            indices.reverse()

        for i in indices:
            result = self._find_selection_boundary_object(AXObject.get_child(root, i), find_start)
            if result:
                return result

        return None

    def _get_selection_anchor_and_focus(
        self,
        root: Atspi.Accessible
    ) -> tuple[Atspi.Accessible | None, Atspi.Accessible | None]:
        obj1 = self._find_selection_boundary_object(root, True)
        obj2 = self._find_selection_boundary_object(root, False)
        return obj1, obj2

    def _get_subtree(
        self,
        start_obj: Atspi.Accessible,
        end_obj: Atspi.Accessible
    ) -> list[Atspi.Accessible]:
        if not (start_obj and end_obj):
            return []

        if AXObject.is_dead(start_obj):
            msg = "INFO: Cannot get subtree: Start object is dead."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return []

        def _include(x):
            return x is not None

        def _exclude(x):
            return not AXUtilities.is_web_element(x)

        subtree = []
        start_obj_parent = AXObject.get_parent(start_obj)
        for i in range(AXObject.get_index_in_parent(start_obj),
                        AXObject.get_child_count(start_obj_parent)):
            child = AXObject.get_child(start_obj_parent, i)
            if not AXUtilities.is_web_element(child):
                continue
            subtree.append(child)
            subtree.extend(self._find_all_descendants(child, _include, _exclude))
            if end_obj in subtree:
                break

        if end_obj == start_obj:
            return subtree

        if end_obj not in subtree:
            subtree.append(end_obj)
            subtree.extend(self._find_all_descendants(end_obj, _include, _exclude))

        end_obj_parent = AXObject.get_parent(end_obj)
        end_obj_index = AXObject.get_index_in_parent(end_obj)
        last_obj = AXObject.get_child(end_obj_parent, end_obj_index + 1) or end_obj

        try:
            end_index = subtree.index(last_obj)
        except ValueError:
            pass
        else:
            if last_obj == end_obj:
                end_index += 1
            subtree = subtree[:end_index]

        return subtree

    def handle_text_selection_change(
        self,
        obj: Atspi.Accessible,
        speak_message: bool = True
    ) -> bool:
        """Handles a change in the selected text."""

        if not self.in_document_content(obj) or self._script.in_focus_mode():
            return super().handle_text_selection_change(obj)

        old_start, old_end = \
            self._script.point_of_reference.get("selectionAnchorAndFocus", (None, None))
        start, end = self._get_selection_anchor_and_focus(obj)
        self._script.point_of_reference["selectionAnchorAndFocus"] = (start, end)

        def _cmp(obj1, obj2):
            return self.path_comparison(AXObject.get_path(obj1), AXObject.get_path(obj2))

        old_subtree = self._get_subtree(old_start, old_end)
        if start == old_start and end == old_end:
            descendants = old_subtree
        else:
            new_subtree = self._get_subtree(start, end)
            descendants = sorted(
                set(old_subtree).union(new_subtree), key=functools.cmp_to_key(_cmp))

        if not descendants:
            return False

        for descendant in descendants:
            if descendant not in (old_start, old_end, start, end) \
               and AXObject.find_ancestor(descendant, lambda x: x in descendants):
                AXText.update_cached_selected_text(descendant)
            else:
                super().handle_text_selection_change(descendant, speak_message)

        return True

    def in_top_level_web_app(self, obj: Atspi.Accessible | None = None) -> bool:
        """Returns True if the object is in a top-level web application."""

        if obj is None:
            obj = focus_manager.get_manager().get_locus_of_focus()

        rv = self._cached_in_top_level_web_app.get(hash(obj))
        if rv is not None:
            return rv

        document = self.get_document_for_object(obj)
        if not document and self.is_document(obj):
            document = obj

        rv = self.is_top_level_web_app(document)
        self._cached_in_top_level_web_app[hash(obj)] = rv
        return rv

    def is_top_level_web_app(self, obj: Atspi.Accessible) -> bool:
        """Returns True if the object is a top-level web application."""

        if AXUtilities.is_embedded(obj) \
           and not self.get_document_for_object(AXObject.get_parent(obj)):
            uri = AXDocument.get_uri(obj)
            rv = bool(uri and uri.startswith("http"))
            tokens = ["WEB:", obj, "is top-level web application:", rv, "(URI:", uri, ")"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return rv

        return False

    def force_browse_mode_for_web_app_descendant(self, obj: Atspi.Accessible) -> bool:
        """Returns true if we should force browse mode for web-app descendant obj."""

        if not AXObject.find_ancestor(obj, AXUtilities.is_embedded):
            return False

        if AXUtilities.is_tool_tip(obj):
            return AXUtilities.is_focused(obj)

        if AXUtilities.is_document_web(obj):
            return not self.is_focus_mode_widget(obj)

        return False

    def is_focus_mode_widget(self, obj: Atspi.Accessible) -> bool:
        """Returns true if obj should be treated as a focus-mode widget."""

        if AXUtilities.is_editable(obj):
            tokens = ["WEB:", obj, "is focus mode widget because it's editable"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        if AXUtilities.is_expandable(obj) and AXUtilities.is_focusable(obj) \
           and not AXUtilities.is_link(obj):
            tokens = ["WEB:", obj, "is focus mode widget because it's expandable and focusable"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        always_focus_mode_roles = [Atspi.Role.COMBO_BOX,
                                   Atspi.Role.ENTRY,
                                   Atspi.Role.LIST_BOX,
                                   Atspi.Role.MENU,
                                   Atspi.Role.MENU_ITEM,
                                   Atspi.Role.CHECK_MENU_ITEM,
                                   Atspi.Role.RADIO_MENU_ITEM,
                                   Atspi.Role.PAGE_TAB,
                                   Atspi.Role.PASSWORD_TEXT,
                                   Atspi.Role.PROGRESS_BAR,
                                   Atspi.Role.SLIDER,
                                   Atspi.Role.SPIN_BUTTON,
                                   Atspi.Role.TOOL_BAR,
                                   Atspi.Role.TREE_ITEM,
                                   Atspi.Role.TREE_TABLE,
                                   Atspi.Role.TREE]

        role = AXObject.get_role(obj)
        if role in always_focus_mode_roles:
            tokens = ["WEB:", obj, "is focus mode widget due to its role"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        if role in [Atspi.Role.TABLE_CELL, Atspi.Role.TABLE] \
           and AXTable.is_layout_table(AXTable.get_table(obj)):
            tokens = ["WEB:", obj, "is not focus mode widget because it's layout only"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        if AXUtilities.is_list_box_item(obj, role):
            tokens = ["WEB:", obj, "is focus mode widget because it's a listbox item"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        if AXUtilities.is_button_with_popup(obj, role):
            tokens = ["WEB:", obj, "is focus mode widget because it's a button with popup"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        focus_mode_roles = [Atspi.Role.EMBEDDED,
                            Atspi.Role.TABLE_CELL,
                            Atspi.Role.TABLE]

        if role in focus_mode_roles \
           and not self.is_text_block_element(obj) \
           and not self._has_name_and_action_and_no_useful_children(obj) \
           and not AXDocument.is_pdf(self.get_document_for_object(obj)):
            tokens = ["WEB:", obj, "is focus mode widget based on presumed functionality"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        if AXObject.find_ancestor(obj, AXUtilities.is_grid) is not None:
            tokens = ["WEB:", obj, "is focus mode widget because it's a grid descendant"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        if AXObject.find_ancestor(obj, AXUtilities.is_menu) is not None:
            tokens = ["WEB:", obj, "is focus mode widget because it's a menu descendant"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if AXObject.find_ancestor(obj, AXUtilities.is_tool_bar) is not None:
            tokens = ["WEB:", obj, "is focus mode widget because it's a toolbar descendant"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        if self.is_content_editable_with_embedded_objects(obj):
            tokens = ["WEB:", obj, "is focus mode widget because it's content editable"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        return False

    def _text_block_element_roles(self) -> list[Atspi.Role]:
        # TODO - JD: Move to AXUtilities.
        roles = [Atspi.Role.ARTICLE,
                 Atspi.Role.CAPTION,
                 Atspi.Role.COLUMN_HEADER,
                 Atspi.Role.COMMENT,
                 Atspi.Role.CONTENT_DELETION,
                 Atspi.Role.CONTENT_INSERTION,
                 Atspi.Role.DEFINITION,
                 Atspi.Role.DESCRIPTION_LIST,
                 Atspi.Role.DESCRIPTION_TERM,
                 Atspi.Role.DESCRIPTION_VALUE,
                 Atspi.Role.DOCUMENT_FRAME,
                 Atspi.Role.DOCUMENT_WEB,
                 Atspi.Role.FOOTER,
                 Atspi.Role.FORM,
                 Atspi.Role.HEADING,
                 Atspi.Role.LIST,
                 Atspi.Role.LIST_ITEM,
                 Atspi.Role.MARK,
                 Atspi.Role.PARAGRAPH,
                 Atspi.Role.ROW_HEADER,
                 Atspi.Role.SECTION,
                 Atspi.Role.STATIC,
                 Atspi.Role.SUGGESTION,
                 Atspi.Role.TEXT,
                 Atspi.Role.TABLE_CELL]

        return roles

    def unrelated_labels(
        self,
        root: Atspi.Accessible | None = None,
        only_showing: bool = True,
        minimum_words: int = 3
    ) -> list[Atspi.Accessible]:
        """Returns a list of labels in root that lack a relationship."""

        if not (root and self.in_document_content(root)):
            return super().unrelated_labels(root, only_showing, minimum_words)
        return []

    def is_focusable_with_math_child(self, obj: Atspi.Accessible) -> bool:
        """Returns true if obj is focusable, not a document, and has a math child."""

        # TODO - JD: This could go in the AXUtilities.
        if not (obj and self.in_document_content(obj)):
            return False

        return AXUtilities.is_focusable(obj) and not self.is_document(obj) \
             and any(AXObject.iter_children(obj, AXUtilities.is_math))

    def is_focused_with_math_child(self, obj: Atspi.Accessible) -> bool:
        """Returns true if obj is focused, not a document, and has a math child."""

        # TODO - JD: This could go in the AXUtilities.
        if not self.is_focusable_with_math_child(obj):
            return False
        return AXUtilities.is_focused(obj)

    def is_text_block_element(self, obj: Atspi.Accessible) -> bool:
        """Returns true if obj is a text block element."""

        if not (obj and self.in_document_content(obj)):
            return False

        rv = self._cached_is_text_block_element.get(hash(obj))
        if rv is not None:
            return rv

        if AXObject.get_role(obj) not in self._text_block_element_roles():
            rv = False
        elif not AXObject.supports_text(obj):
            rv = False
        elif AXUtilities.is_editable(obj):
            rv = False
        elif AXUtilities.is_grid_cell(obj):
            rv = False
        elif AXUtilities.is_document(obj):
            rv = True
        elif self.is_custom_image(obj):
            rv = False
        elif not AXUtilities.is_focusable(obj):
            rv = not self._has_name_and_action_and_no_useful_children(obj)
        else:
            rv = False

        self._cached_is_text_block_element[hash(obj)] = rv
        return rv

    def _advance_caret_in_empty_object(self, obj: Atspi.Accessible) -> bool:
        if AXUtilities.is_table_cell(obj) and not self.treat_as_text_object(obj):
            return not self._script.get_caret_navigator().last_input_event_was_navigation_command()

        return True

    def treat_as_div(self, obj: Atspi.Accessible, offset: int | None = None) -> bool:
        """Returns True if the object should be treated as a div."""

        if not (obj and self.in_document_content(obj)):
            return False

        if AXUtilities.is_description_list(obj):
            return False

        if AXUtilities.is_list(obj) and offset is not None:
            string = AXText.get_substring(obj, offset, offset + 1)
            if string and string != "\ufffc":
                return True

        child_count = AXObject.get_child_count(obj)
        if AXUtilities.is_panel(obj) and not child_count:
            return True

        rv = self._cached_treat_as_div.get(hash(obj))
        if rv is not None:
            return rv

        rv = False

        valid_roles = self._valid_child_roles.get(AXObject.get_role(obj))
        if valid_roles:
            if not child_count:
                rv = True
            else:
                def pred1(x):
                    return x is not None and AXObject.get_role(x) not in valid_roles

                rv = bool(list(AXObject.iter_children(obj, pred1)))

        if not rv:
            parent = AXObject.get_parent(obj)
            valid_roles = self._valid_child_roles.get(parent)
            if valid_roles:
                def pred2(x):
                    return x is not None and AXObject.get_role(x) not in valid_roles
                rv = bool(list(AXObject.iter_children(parent, pred2)))

        self._cached_treat_as_div[hash(obj)] = rv
        return rv

    def filter_contents_for_presentation(
        self,
        contents: list[tuple[Atspi.Accessible, int, int, str]],
        infer_labels: bool = False
    ) -> list[tuple[Atspi.Accessible, int, int, str]]:
        """Filters contents for presentation, removing objects that should not be included."""

        # TODO - JD: Is this still needed?

        def _include(x):
            obj, _start, _end, string = x
            if not obj or AXObject.is_dead(obj):
                return False

            rv = self._cached_should_filter.get(hash(obj))
            if rv is not None:
                return rv

            text = string or AXObject.get_name(obj)
            rv = True
            # TODO - JD: Audit this to see if they are now redundant.
            if ((self.is_text_block_element(obj) or self.is_link(obj)) and not text) \
               or (self.is_content_editable_with_embedded_objects(obj) and not string.strip()) \
               or self._is_empty_anchor(obj) \
               or (AXComponent.has_no_size(obj) and not text) \
               or AXUtilities.is_hidden(obj) \
               or self._is_off_screen_label(obj) \
               or self._is_useless_image(obj) \
               or self.is_link_ancestor_of_image_in_contents(obj, contents) \
               or self.is_error_for_contents(obj, contents) \
               or self._is_labelling_contents(obj, contents):
                rv = False
            elif AXUtilities.is_table_row(obj):
                rv = AXUtilities.has_explicit_name(obj)
            else:
                widget = self.is_inferred_label_for_contents(x, contents)
                always_filter = [Atspi.Role.RADIO_BUTTON, Atspi.Role.CHECK_BOX]
                if widget and (infer_labels or AXObject.get_role(widget) in always_filter):
                    rv = False

            self._cached_should_filter[hash(obj)] = rv
            return rv

        if len(contents) == 1:
            return contents

        rv = list(filter(_include, contents))
        self._cached_should_filter = {}
        return rv

    def _has_grid_descendant(self, obj: Atspi.Accessible) -> bool:
        if not obj:
            return False

        rv = self._cached_has_grid_descendant.get(hash(obj))
        if rv is not None:
            return rv

        if not AXObject.get_child_count(obj):
            rv = False
        else:
            document = self.active_document()
            if obj != document:
                document_has_grids = self._has_grid_descendant(document)
                if not document_has_grids:
                    rv = False

        if rv is None:
            grids = AXUtilities.find_all_grids(obj)
            rv = bool(grids)

        self._cached_has_grid_descendant[hash(obj)] = rv
        return rv

    def _is_cell_with_name_from_header(self, obj: Atspi.Accessible) -> bool:
        # TODO - JD: Move into one of the AX* classes.
        if not AXUtilities.is_table_cell(obj):
            return False

        name = AXObject.get_name(obj)
        if not name:
            return False

        headers = AXTable.get_column_headers(obj)
        for header in headers:
            if AXObject.get_name(header) == name:
                return True

        headers = AXTable.get_row_headers(obj)
        for header in headers:
            if AXObject.get_name(header) == name:
                return True

        return False

    def should_read_full_row(
        self,
        obj: Atspi.Accessible,
        previous_object: Atspi.Accessible | None = None
    ) -> bool:
        if not (obj and self.in_document_content(obj)):
            return super().should_read_full_row(obj, previous_object)

        if not super().should_read_full_row(obj, previous_object):
            return False

        if AXObject.find_ancestor(obj, AXUtilities.is_grid) is not None:
            return not self._script.in_focus_mode()

        if input_event_manager.get_manager().last_event_was_line_navigation():
            return False

        if input_event_manager.get_manager().last_event_was_mouse_button():
            return False

        return True

    def _element_lines_are_single_words(self, obj: Atspi.Accessible) -> bool:
        if not (obj and self.in_document_content(obj)):
            return False

        if AXUtilities.is_code(obj):
            return False

        rv = self._cached_element_lines_are_single_words.get(hash(obj))
        if rv is not None:
            return rv

        n_chars = AXText.get_character_count(obj)
        if not n_chars:
            return False

        if not self.treat_as_text_object(obj):
            return False

        # If we have a series of embedded object characters, there's a reasonable chance
        # they'll look like the one-word-per-line CSSified text we're trying to detect.
        # We don't want that false positive. By the same token, the one-word-per-line
        # CSSified text we're trying to detect can have embedded object characters. So
        # if we have more than 30% EOCs, don't use this workaround. (The 30% is based on
        # testing with problematic text.)
        string = AXText.get_all_text(obj)
        eocs = re.findall("\ufffc", string)
        if len(eocs)/n_chars > 0.3:
            return False

        # TODO - JD: Can we remove this?
        AXObject.clear_cache(obj, False, "Checking if element lines are single words.")
        tokens = list(filter(lambda x: x, re.split(r"[\s\ufffc]", string)))

        # Note: We cannot check for the editable-text interface, because Gecko
        # seems to be exposing that for non-editable things. Thanks Gecko.
        rv = len(tokens) > 1 \
            and not (AXUtilities.is_editable(obj) or AXUtilities.is_text_input(obj))
        if rv:
            i = 0
            while i < n_chars:
                string, _start, end = AXText.get_line_at_offset(obj, i)
                if len(string.split()) != 1:
                    rv = False
                    break
                i = max(i+1, end)

        self._cached_element_lines_are_single_words[hash(obj)] = rv
        return rv

    def _element_lines_are_single_chars(self, obj: Atspi.Accessible) -> bool:
        if not (obj and self.in_document_content(obj)):
            return False

        rv = self._cached_element_lines_are_single_chars.get(hash(obj))
        if rv is not None:
            return rv

        n_chars = AXText.get_character_count(obj)
        if not n_chars:
            return False

        if not self.treat_as_text_object(obj):
            return False

        # If we have a series of embedded object characters, there's a reasonable chance
        # they'll look like the one-char-per-line CSSified text we're trying to detect.
        # We don't want that false positive. By the same token, the one-char-per-line
        # CSSified text we're trying to detect can have embedded object characters. So
        # if we have more than 30% EOCs, don't use this workaround. (The 30% is based on
        # testing with problematic text.)
        string = AXText.get_all_text(obj)
        eocs = re.findall("\ufffc", string)
        if len(eocs)/n_chars > 0.3:
            return False

        # TODO - JD: Can we remove this?
        AXObject.clear_cache(obj, False, "Checking if element lines are single chars.")

        # Note: We cannot check for the editable-text interface, because Gecko
        # seems to be exposing that for non-editable things. Thanks Gecko.
        rv = not (AXUtilities.is_editable(obj) or AXUtilities.is_text_input(obj))
        if rv:
            for i in range(n_chars):
                char = AXText.get_character_at_offset(obj, i)[0]
                if char.isspace() or char in ["\ufffc", "\ufffd"]:
                    continue

                string = AXText.get_line_at_offset(obj, i)[0]
                if len(string.strip()) > 1:
                    rv = False
                    break

        self._cached_element_lines_are_single_chars[hash(obj)] = rv
        return rv

    def _label_is_ancestor_of_labelled(self, label: Atspi.Accessible) -> bool:
        # TODO - JD: Move into AXUtilities.
        for labelled in AXUtilities.get_is_label_for(label):
            if AXObject.is_ancestor(labelled, label):
                return True
        return False

    def _is_off_screen_label(self, obj: Atspi.Accessible) -> bool:
        if not (obj and self.in_document_content(obj)):
            return False

        rv = self._cached_is_off_screen_label.get(hash(obj))
        if rv is not None:
            return rv

        if self._label_is_ancestor_of_labelled(obj):
            return False

        rv = False
        if AXUtilities.get_is_label_for(obj):
            end = max(1, AXText.get_character_count(obj))
            rect = AXText.get_range_rect(obj, 0, end)
            if rect.x < 0 or rect.y < 0:
                rv = True

        self._cached_is_off_screen_label[hash(obj)] = rv
        return rv

    def _is_detached_document(self, obj: Atspi.Accessible) -> bool:
        if AXUtilities.is_document(obj) and not AXObject.is_valid(AXObject.get_parent(obj)):
            tokens = ["WEB:", obj, "is a detached document"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        return False

    def _iframe_for_detached_document(
        self,
        obj: Atspi.Accessible,
        root: Atspi.Accessible | None = None
    ) -> Atspi.Accessible | None:
        root = root or self.active_document()
        for iframe in AXUtilities.find_all_internal_frames(root):
            if AXObject.get_parent(obj) == iframe:
                tokens = ["WEB: Returning", iframe, "as iframe parent of detached", obj]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                return iframe

        return None

    def is_link_ancestor_of_image_in_contents(
        self,
        link: Atspi.Accessible,
        contents: list[tuple[Atspi.Accessible, int, int, str]]
    ) -> bool:
        """Returns true if link is an ancestor of an image in contents."""

        if not self.is_link(link):
            return False

        for obj, _start, _end, _string in contents:
            if not AXUtilities.is_image(obj):
                continue
            if AXObject.find_ancestor(obj, lambda x: x == link):
                return True

        return False

    def is_inferred_label_for_contents(
        self,
        content: tuple[Atspi.Accessible, int, int, str],
        contents: list[tuple[Atspi.Accessible, int, int, str]]
    ) -> bool:
        """Returns true if content is an inferred label for contents."""

        obj, _start, _end, string = content
        objs = list(filter(self._should_infer_label_for, [x[0] for x in contents]))
        if not objs:
            return False

        for o in objs:
            label, sources = self.infer_label_for(o)
            if obj in sources and label and label.strip() == string.strip():
                return True

        return False

    def _is_labelling_contents(
        self,
        obj: Atspi.Accessible,
        contents: list[tuple[Atspi.Accessible, int, int, str]] | None = None
    ) -> bool:
        if self.is_focus_mode_widget(obj):
            return False

        targets = AXUtilities.get_is_label_for(obj)
        if not contents:
            if targets:
                return True
            return AXObject.find_ancestor(obj, AXUtilities.is_label_or_caption) is not None

        for acc, _start, _end, _string in contents:
            if acc in targets:
                return True

        if not self.is_text_block_element(obj):
            return False

        if AXObject.find_ancestor(obj, AXUtilities.is_label_or_caption) is None:
            return False

        for acc, _start, _end, _string in contents:
            if AXObject.find_ancestor(acc, AXUtilities.is_label_or_caption) is None:
                continue
            if self.is_text_block_element(acc):
                continue

            if AXUtilities.is_label_or_caption(AXObject.get_common_ancestor(acc, obj)):
                return True

        return False

    def _is_empty_anchor(self, obj: Atspi.Accessible) -> bool:
        return self.is_anchor(obj) and not self.treat_as_text_object(obj)

    def _is_empty_tool_tip(self, obj: Atspi.Accessible) -> bool:
        return AXUtilities.is_tool_tip(obj) and not self.treat_as_text_object(obj)

    def is_browser_ui_alert(self, obj: Atspi.Accessible) -> bool:
        """Returns true if obj is an alert outside of document content."""

        if not AXUtilities.is_alert(obj):
            return False

        if self.in_document_content(obj):
            return False

        return True

    def is_clickable_element(self, obj: Atspi.Accessible) -> bool:
        if not (obj and self.in_document_content(obj)):
            return False

        rv = self._cached_is_clickable_element.get(hash(obj))
        if rv is not None:
            return rv

        if self._label_is_ancestor_of_labelled(obj):
            return False

        if self._has_grid_descendant(obj):
            tokens = ["WEB:", obj, "is not clickable: has grid descendant"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        rv = False
        if not self.is_focus_mode_widget(obj):
            if not AXUtilities.is_focusable(obj):
                rv = AXObject.has_action(obj, "click")
            else:
                rv = AXObject.has_action(obj, "click-ancestor")

        if rv and not AXObject.get_name(obj) and AXObject.supports_text(obj):
            text = AXText.get_all_text(obj)
            if not text.replace("\ufffc", ""):
                tokens = ["WEB:", obj, "is not clickable: its text is just EOCs"]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                rv = False
            elif not text.strip():
                rv = not (AXUtilities.is_static(obj) or AXUtilities.is_link(obj))

        self._cached_is_clickable_element[hash(obj)] = rv
        return rv

    def is_item_for_editable_combo_box(
        self,
        item: Atspi.Accessible,
        combobox: Atspi.Accessible
    ) -> bool:
        """Returns true if item is an item for editable combobox combobox."""

        # TODO - JD: Move into AXUtilities.
        if not (AXUtilities.is_list_item(item) or AXUtilities.is_menu_item(item)):
            return False
        if not AXUtilities.is_editable_combo_box(combobox):
            return False
        if AXObject.is_ancestor(item, combobox):
            return True

        container = AXObject.find_ancestor(
            item, lambda x: AXUtilities.is_list_box(x) or AXUtilities.is_combo_box(x))
        targets = AXUtilities.get_is_controlled_by(container)
        return combobox in targets

    def _is_fake_placeholder_for_entry(self, obj: Atspi.Accessible) -> bool:
        if not (obj and self.in_document_content(obj) and AXObject.get_parent(obj)):
            return False

        if AXUtilities.is_editable(obj):
            return False

        entry_name = AXObject.get_name(AXObject.find_ancestor(obj, AXUtilities.is_entry))
        if not entry_name:
            return False

        def _is_match(x):
            string = AXText.get_all_text(x).strip()
            if entry_name != string:
                return False
            return AXUtilities.is_section(x) or AXUtilities.is_static(x)

        if _is_match(obj):
            return True

        return AXObject.find_descendant(obj, _is_match) is not None

    def _is_block_list_descendant(self, obj: Atspi.Accessible) -> bool:
        # TODO - JD: Move into AXUtilities.
        if AXObject.find_ancestor(obj, AXUtilities.is_list) is None:
            return False

        return AXObject.find_ancestor_inclusive(obj, AXUtilities.is_inline_list_item) is None

    def is_link(self, obj: Atspi.Accessible) -> bool:
        if not obj:
            return False

        rv = self._cached_is_link.get(hash(obj))
        if rv is not None:
            return rv

        if AXUtilities.is_link(obj) and not self.is_anchor(obj):
            rv = True
        elif AXUtilities.is_static(obj) and AXUtilities.is_link(AXObject.get_parent(obj)) \
           and AXObject.has_same_non_empty_name(obj, AXObject.get_parent(obj)):
            rv = True
        else:
            rv = False

        self._cached_is_link[hash(obj)] = rv
        return rv

    def has_useless_canvas_descendant(self, obj: Atspi.Accessible) -> bool:
        """Returns true if obj has a canvas descendant which lacks fallback content."""

        return len(AXUtilities.find_all_canvases(obj, self._is_useless_image)) > 0

    def _is_non_navigable_embedded_document(self, obj: Atspi.Accessible) -> bool:
        if self.is_document(obj) and self.get_document_for_object(obj):
            return "doubleclick" in AXObject.get_name(obj)
        return False

    def _is_redundant_svg(self, obj: Atspi.Accessible) -> bool:
        if not AXUtilities.is_svg(obj) or AXObject.get_child_count(AXObject.get_parent(obj)) == 1:
            return False

        rv = self._cached_is_redundant_svg.get(hash(obj))
        if rv is not None:
            return rv

        rv = False
        parent = AXObject.get_parent(obj)
        children = list(AXObject.iter_children(parent, AXUtilities.is_svg))
        if len(children) == AXObject.get_child_count(parent):
            sorted_children = AXComponent.sort_objects_by_size(children)
            if obj != sorted_children[-1]:
                obj_extents = AXComponent.get_rect(obj)
                largest_extents = AXComponent.get_rect(sorted_children[-1])
                intersection = AXComponent.get_rect_intersection(obj_extents, largest_extents)
                rv = intersection == obj_extents

        rv = bool(rv)
        self._cached_is_redundant_svg[hash(obj)] = rv
        return rv

    def is_custom_image(self, obj: Atspi.Accessible) -> bool:
        """Returns true if obj is a custom image."""

        # TODO - JD: Move into the AXUtilities.

        if not (obj and self.in_document_content(obj)):
            return False

        rv = self._cached_is_custom_image.get(hash(obj))
        if rv is not None:
            return rv

        rv = False
        if AXUtilities.is_web_element_custom(obj) and AXUtilities.has_explicit_name(obj) \
           and AXUtilities.is_section(obj) \
           and AXObject.supports_text(obj) \
           and not re.search(r"[^\s\ufffc]", AXText.get_all_text(obj)):
            for child in AXObject.iter_children(obj):
                if not (AXUtilities.is_image_or_canvas(child) or AXUtilities.is_svg(child)):
                    break
            else:
                rv = True

        self._cached_is_custom_image[hash(obj)] = rv
        return rv

    def _is_useless_image(self, obj: Atspi.Accessible) -> bool:
        if not (obj and self.in_document_content(obj)):
            return False

        rv = self._cached_is_useless_image.get(hash(obj))
        if rv is not None:
            return rv

        rv = True
        has_explicit_name = AXUtilities.has_explicit_name(obj)
        if not (AXUtilities.is_image_or_canvas(obj) or AXUtilities.is_svg(obj)):
            rv = False
        if rv and (AXObject.get_name(obj) \
                   or AXObject.get_description(obj) \
                   or self.has_long_desc(obj)):
            rv = False
        if rv and self.is_clickable_element(obj) and not has_explicit_name:
            rv = False
        if rv and AXUtilities.is_focusable(obj):
            rv = False
        if rv and AXUtilities.is_link(AXObject.get_parent(obj)) and not has_explicit_name:
            uri = AXHypertext.get_link_uri(AXObject.get_parent(obj))
            if uri and not uri.startswith("javascript"):
                rv = False
        if rv and AXObject.supports_image(obj):
            if AXObject.get_image_description(obj):
                rv = False
            elif not has_explicit_name and not self._is_redundant_svg(obj):
                width, height = AXObject.get_image_size(obj)
                if width > 25 and height > 25:
                    rv = False
        if rv and AXObject.supports_text(obj):
            rv = not self.treat_as_text_object(obj)
        if rv and AXObject.get_child_count(obj):
            for i in range(min(AXObject.get_child_count(obj), 50)):
                if not self._is_useless_image(AXObject.get_child(obj, i)):
                    rv = False
                    break

        self._cached_is_useless_image[hash(obj)] = rv
        return rv

    def has_valid_name(self, obj: Atspi.Accessible) -> bool:
        """Returns true if obj has a valid name."""

        name = AXObject.get_name(obj)
        if not name:
            return False

        if len(name.split()) > 1:
            return True

        parsed = urllib.parse.parse_qs(name)
        if len(parsed) > 2:
            tokens = ["WEB: name of", obj, "is suspected query string"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        if len(name) == 1 and ord(name) in range(0xe000, 0xf8ff):
            tokens = ["WEB: name of", obj, "is in unicode private use area"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        return True

    def _is_useless_empty_element(self, obj: Atspi.Accessible) -> bool:
        if not (obj and self.in_document_content(obj)):
            return False

        rv = self._cached_is_useless_empty_element.get(hash(obj))
        if rv is not None:
            return rv

        roles = [Atspi.Role.PARAGRAPH,
                 Atspi.Role.SECTION,
                 Atspi.Role.STATIC,
                 Atspi.Role.TABLE_ROW]
        role = AXObject.get_role(obj)
        if role not in roles and not AXUtilities.is_aria_alert(obj):
            rv = False
        elif AXUtilities.is_focusable(obj):
            rv = False
        elif AXUtilities.is_editable(obj):
            rv = False
        elif self.has_valid_name(obj) \
                or AXObject.get_description(obj) or AXObject.get_child_count(obj):
            rv = False
        elif AXText.get_character_count(obj) and AXText.get_all_text(obj) != AXObject.get_name(obj):
            rv = False
        elif AXObject.supports_action(obj):
            names = AXObject.get_action_names(obj)
            ignore = ["click-ancestor", "show-context-menu", "do-default"]
            names = list(filter(lambda x: x not in ignore, names))
            rv = not names
        else:
            rv = True

        self._cached_is_useless_empty_element[hash(obj)] = rv
        return rv

    def has_long_desc(self, obj: Atspi.Accessible) -> bool:
        """Returns true if obj has a long description."""

        if not (obj and self.in_document_content(obj)):
            return False
        return AXObject.has_action(obj, "showlongdesc")

    def infer_label_for(self, obj: Atspi.Accessible) -> tuple[str | None, list[Atspi.Accessible]]:
        """Attempts to infer the text serving as the functional label for obj."""

        if not self._should_infer_label_for(obj):
            return None, []

        rv = self._cached_inferred_labels.get(hash(obj))
        if rv is not None:
            return rv

        rv = self._script.label_inference.infer(obj, False)
        self._cached_inferred_labels[hash(obj)] = rv
        return rv

    def _should_infer_label_for(self, obj: Atspi.Accessible) -> bool:
        if not self.in_document_content() or AXObject.find_ancestor(obj, AXUtilities.is_embedded):
            return False

        rv = self._cached_should_infer_label_for.get(hash(obj))
        if rv and not self._script.get_caret_navigator().last_input_event_was_navigation_command():
            return not focus_manager.get_manager().in_say_all()
        if rv is False:
            return rv

        role = AXObject.get_role(obj)
        if AXObject.get_name(obj):
            rv = False
        elif AXUtilities.has_role_from_aria(obj):
            rv = False
        elif not rv:
            roles = [Atspi.Role.CHECK_BOX,
                     Atspi.Role.COMBO_BOX,
                     Atspi.Role.ENTRY,
                     Atspi.Role.LIST_BOX,
                     Atspi.Role.PASSWORD_TEXT,
                     Atspi.Role.RADIO_BUTTON]
            rv = role in roles and not AXUtilities.get_displayed_label(obj)

        self._cached_should_infer_label_for[hash(obj)] = rv
        if self._script.get_caret_navigator().last_input_event_was_navigation_command() \
           and role not in [Atspi.Role.RADIO_BUTTON, Atspi.Role.CHECK_BOX]:
            return False

        return rv

    def _is_spinner_entry(self, obj: Atspi.Accessible) -> bool:
        # TODO - JD: This should be in AXUtilities.
        if not self.in_document_content(obj):
            return False

        if not AXUtilities.is_editable(obj):
            return False

        if AXUtilities.is_spin_button(obj) or AXUtilities.is_spin_button(AXObject.get_parent(obj)):
            return True

        return False

    def event_is_spinner_noise_deprecated(self, event: Atspi.Event) -> bool:
        """Returns true if event is believed to be spinner noise."""

        # TODO - JD: This should be in AXEventUtilities.
        if not self._is_spinner_entry(event.source):
            return False

        return event.type.startswith("object:text-selection-changed") \
            and input_event_manager.get_manager().last_event_was_up_or_down()

    def treat_event_as_spinner_value_change_deprecated(self, event: Atspi.Event) -> bool:
        """Returns true if event should be treated as a spinner value change."""
        # TODO - JD: This should be in AXEventUtilities.

        if event.type.startswith("object:text-caret-moved") \
           and self._is_spinner_entry(event.source):
            if input_event_manager.get_manager().last_event_was_up_or_down():
                obj = self.get_caret_context()[0]
                return event.source == obj

        return False

    def event_is_browser_ui_noise_deprecated(self, event: Atspi.Event) -> bool:
        """Returns true if event is believed to be browser UI noise."""

        # TODO - JD: This is pretty generic and belongs in AXEventUtilities.
        if self.in_document_content(event.source):
            return False

        if event.type.endswith("accessible-name"):
            return AXUtilities.is_status_bar(event.source) or AXUtilities.is_label(event.source) \
                or AXUtilities.is_frame(event.source)
        if event.type.startswith("object:children-changed"):
            return True

        return False

    def event_is_autocomplete_noise_deprecated(self, event, document=None):
        """Returns true if event is believed to be autocomplete noise."""

        # TODO - JD: This should be in AXEventUtilities. And also fixed.

        in_content = document is not None or self.in_document_content(event.source)
        if not in_content:
            return False

        def is_list_box_item(x):
            return AXUtilities.is_list_box(AXObject.get_parent(x))

        def is_menu_item(x):
            return AXUtilities.is_menu(AXObject.get_parent(x))

        def is_combo_box_item(x):
            return AXUtilities.is_combo_box(AXObject.get_parent(x))

        if AXUtilities.is_editable(event.source) \
           and event.type.startswith("object:text-"):
            obj, _offset = self.get_caret_context(document)
            if is_list_box_item(obj) or is_menu_item(obj):
                return True

            if obj == event.source and is_combo_box_item(obj) \
               and input_event_manager.get_manager().last_event_was_up_or_down():
                return True

        return False

    def event_is_browser_ui_autocomplete_noise_deprecated(self, event: Atspi.Event) -> bool:
        """Returns true if event is browser ui autocomplete noise."""

        # TODO - JD: This should be in AXEventUtilities.
        if self.in_document_content(event.source):
            return False

        if self._event_is_browser_ui_autocomplete_text_noise(event):
            return True

        return self._event_is_browser_ui_autocomplete_selection_noise(event)

    def _event_is_browser_ui_autocomplete_selection_noise(self, event):
        # TODO - JD: This should be in AXEventUtilities.
        selection = ["object:selection-changed", "object:state-changed:selected"]
        if event.type not in selection:
            return False

        if not AXUtilities.is_menu_related(event.source):
            return False

        focus = focus_manager.get_manager().get_locus_of_focus()
        if AXUtilities.is_entry(focus) and AXUtilities.is_focused(focus):
            if not input_event_manager.get_manager().last_event_was_up_or_down():
                return True

        return False

    def _event_is_browser_ui_autocomplete_text_noise(self, event: Atspi.Event) -> bool:
        # TODO - JD: This should be in AXEventUtilities.

        if not event.type.startswith("object:text-") \
           or not AXUtilities.is_single_line_autocomplete_entry(event.source):
            return False

        focus = focus_manager.get_manager().get_locus_of_focus()
        if not AXUtilities.is_selectable(focus):
            return False

        if AXUtilities.is_menu_item_of_any_kind(focus) or AXUtilities.is_list_item(focus):
            return input_event_manager.get_manager().last_event_was_up_or_down()

        return False

    def event_is_browser_ui_page_switch(self, event: Atspi.Event) -> bool:
        """Returns true if event is a browser UI page switch event."""

        # TODO - JD: Move into AXUtilities.

        selection = ["object:selection-changed", "object:state-changed:selected"]
        if event.type not in selection:
            return False

        if not AXUtilities.is_page_tab_list_related(event.source):
            return False

        if self.in_document_content(event.source):
            return False

        if not self.in_document_content(focus_manager.get_manager().get_locus_of_focus()):
            return False

        return True

    def event_is_from_locus_of_focus_document(self, event: Atspi.Event) -> bool:
        """Returns true if event comes from the document of the locus of focus."""

        if focus_manager.get_manager().focus_is_active_window():
            focus = self.active_document()
            source = self.get_top_level_document_for_object(event.source)
        else:
            focus = self.get_document_for_object(focus_manager.get_manager().get_locus_of_focus())
            source = self.get_document_for_object(event.source)

        tokens = ["WEB: Event doc:", source, ". Focus doc:", focus, "."]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if not (source and focus):
            return False

        if source == focus:
            return True

        if not AXObject.is_valid(focus) and AXObject.is_valid(source):
            if self.active_document() == source:
                msg = "WEB: Treating active doc as locusOfFocus doc"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return True

        return False

    def event_is_irrelevant_selection_changed_event(self, event: Atspi.Event) -> bool:
        """Returns true if event is an irrelevant selection changed event."""

        # TODO - JD: This should be in AXEventUtilities.
        if event.type != "object:selection-changed":
            return False

        focus = focus_manager.get_manager().get_locus_of_focus()
        if not focus:
            msg = "WEB: Selection changed event is relevant (no locusOfFocus)"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False
        if event.source == focus:
            msg = "WEB: Selection changed event is relevant (is locusOfFocus)"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False
        if AXObject.find_ancestor(focus, lambda x: x == event.source):
            msg = "WEB: Selection changed event is relevant (ancestor of locusOfFocus)"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        # There may be other roles where we need to do this. For now, solve the known one.
        if AXUtilities.is_page_tab_list(event.source):
            tokens = ["WEB: Selection changed event is irrelevant (unrelated",
                      AXObject.get_role_name(event.source), ")"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        msg = "WEB: Selection changed event is relevant (no reason found to ignore it)"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return False

    def event_is_for_non_navigable_text_object(self, event):
        """Returns true if event is for an object we're treating as a whole."""

        if not event.type.startswith("object:text-"):
            return False
        return self._treat_object_as_whole(event.source)

    def caret_moved_outside_active_grid(self, event, old_focus=None):
        """Returns true if caret moved outside the active grid."""

        # TODO - JD: This is one of those "noise" functions.
        if not (event and event.type.startswith("object:text-caret-moved")):
            return False

        old_focus = old_focus or focus_manager.get_manager().get_locus_of_focus()
        if AXObject.find_ancestor(old_focus, AXUtilities.is_grid) is None:
            return False

        return AXObject.find_ancestor(event.source, AXUtilities.is_grid) is None

    def caret_moved_to_same_page_fragment(self, event, old_focus=None):
        """Returns true if the caret moved to a same-page fragment."""

        if not (event and event.type.startswith("object:text-caret-moved")):
            return False

        if AXUtilities.is_editable(event.source):
            return False

        document = self.active_document()
        fragment = AXDocument.get_document_uri_fragment(document)
        if not fragment:
            return False

        source_id = AXObject.get_attribute(event.source, "id")
        if source_id and fragment == source_id:
            return True

        old_focus = old_focus or focus_manager.get_manager().get_locus_of_focus()
        if self.is_link(old_focus):
            link = old_focus
        else:
            link = AXObject.find_ancestor(old_focus, self.is_link)

        return link and AXHypertext.get_link_uri(link) == AXDocument.get_uri(document)

    def is_child_of_current_fragment(self, obj: Atspi.Accessible) -> bool:
        """Returns true if obj is a child of the current document fragment."""

        fragment = AXDocument.get_document_uri_fragment(self.active_document())
        if not fragment:
            return False

        def is_same_fragment(x):
            return AXObject.get_attribute(x, "id") == fragment

        return AXObject.find_ancestor(obj, is_same_fragment) is not None

    def is_content_editable_with_embedded_objects(self, obj: Atspi.Accessible) -> bool:
        """Returns true if obj is content editable with embedded objects."""

        # TODO - JD: Revisit all the cases this function is used and white editablility is not
        # enough of a check.
        if not (obj and self.in_document_content(obj)):
            return False

        rv = self._cached_is_content_editable_with_embedded_objects.get(hash(obj))
        if rv is not None:
            return rv

        rv = False
        def has_text_block_role(x):
            return AXObject.get_role(x) in self._text_block_element_roles() \
                and not self._is_fake_placeholder_for_entry(x) and AXUtilities.is_web_element(x)

        if AXUtilities.is_text_input(obj):
            rv = False
        elif AXUtilities.is_multi_line_entry(obj):
            rv = AXObject.find_descendant(obj, has_text_block_role) is not None
        elif AXUtilities.is_editable(obj):
            rv = has_text_block_role(obj) or self.is_link(obj)
        elif not self.is_document(obj):
            document = self.get_document_for_object(obj)
            if document:
                rv = self.is_content_editable_with_embedded_objects(document)

        self._cached_is_content_editable_with_embedded_objects[hash(obj)] = rv
        return rv

    def _range_in_parent_with_length(self, obj: Atspi.Accessible) -> tuple[int, int, int]:
        # TODO - JD: Is this still needed?
        parent = AXObject.get_parent(obj)
        if not self.treat_as_text_object(parent):
            return -1, -1, 0

        start = AXHypertext.get_link_start_offset(obj)
        end = AXHypertext.get_link_end_offset(obj)
        return start, end, AXText.get_character_count(parent)

    def _can_have_caret_context(self, obj: Atspi.Accessible) -> bool:
        rv = self._cached_can_have_caret_context_decision.get(hash(obj))
        if rv is not None:
            return rv

        if obj is None:
            return False
        if AXObject.is_dead(obj):
            msg = "WEB: Dead object cannot have caret context"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False
        if not AXObject.is_valid(obj):
            tokens = ["WEB: Invalid object cannot have caret context", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False
        if not AXUtilities.is_web_element(obj):
            tokens = ["WEB: Non-element cannot have caret context", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        start_time = time.time()
        rv = None
        if AXUtilities.is_focusable(obj):
            tokens = ["WEB: Focusable object can have caret context", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            rv = True
        elif AXUtilities.is_editable(obj):
            tokens = ["WEB: Editable object can have caret context", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            rv = True
        elif AXUtilities.is_landmark(obj):
            tokens = ["WEB: Landmark can have caret context", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            rv = True
        elif AXUtilities.is_table_related(obj, True):
            tokens = ["WEB: Table-related object can have caret context", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            rv = True
        elif AXUtilities.is_tool_tip(obj):
            tokens = ["WEB: Non-focusable tooltip cannot have caret context", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            rv = False
        elif self._is_useless_empty_element(obj):
            tokens = ["WEB: Useless empty element cannot have caret context", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            rv = False
        elif self._is_off_screen_label(obj):
            tokens = ["WEB: Off-screen label cannot have caret context", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            rv = False
        elif self._is_useless_image(obj):
            tokens = ["WEB: Useless image cannot have caret context", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            rv = False
        elif self._is_empty_anchor(obj):
            tokens = ["WEB: Empty anchor cannot have caret context", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            rv = False
        elif self._is_empty_tool_tip(obj):
            tokens = ["WEB: Empty tool tip cannot have caret context", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            rv = False
        elif self._is_fake_placeholder_for_entry(obj):
            tokens = ["WEB: Fake placeholder for entry cannot have caret context", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            rv = False
        elif AXObject.find_ancestor(obj, AXUtilities.children_are_presentational):
            tokens = ["WEB: Presentational child cannot have caret context", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            rv = False
        elif AXUtilities.is_hidden(obj):
            # We try to do this check only if needed because getting object attributes is
            # not as performant, and we cannot use the cached attribute because aria-hidden
            # can change frequently depending on the app.
            tokens = ["WEB: Hidden object cannot have caret context", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            rv = False
        elif AXComponent.has_no_size(obj):
            tokens = ["WEB: Allowing sizeless object to have caret context", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            rv = True
        else:
            tokens = ["WEB: ", obj, f"can have caret context. ({time.time() - start_time:.4f}s)"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            rv = True

        self._cached_can_have_caret_context_decision[hash(obj)] = rv
        msg = f"INFO: _canHaveCaretContext took {time.time() - start_time:.4f}s"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return rv

    def search_for_caret_context(self, obj: Atspi.Accessible) -> tuple[Atspi.Accessible, int]:
        """Searches inside obj for the caret context."""

        tokens = ["WEB: Searching for caret context in", obj]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        container = obj
        context_obj, context_offset = None, -1
        while obj:
            offset = AXText.get_caret_offset(obj)
            if offset < 0:
                obj = None
            else:
                context_obj, context_offset = obj, offset
                child = AXHypertext.find_child_at_offset(obj, offset)
                if child:
                    obj = child
                else:
                    break

        if context_obj and not AXUtilities.is_hidden(context_obj):
            return self.find_next_caret_in_order(context_obj, max(-1, context_offset - 1))

        if self.is_document(container):
            return container, 0

        return None, -1

    def get_caret_context(
        self,
        document: Atspi.Accessible | None = None,
        get_replicant: bool = False,
        search_if_needed: bool = True
    ) -> tuple[Atspi.Accessible, int]:
        """Returns an (obj, offset) tuple representing the current location."""

        tokens = ["WEB: Getting caret context for", document]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if not AXObject.is_valid(document):
            document = self.active_document()
            tokens = ["WEB: Now getting caret context for", document]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if not document:
            if not search_if_needed:
                msg = "WEB: Returning None, -1: No document and no search requested."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return None, -1

            obj, offset = focus_manager.get_manager().get_locus_of_focus(), 0
            if AXObject.supports_text(obj):
                offset = AXText.get_caret_offset(obj)

            tokens = ["WEB: Returning", obj, ", ", offset, "(from locusOfFocus)"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return obj, offset

        context = self._cached_caret_contexts.get(hash(AXObject.get_parent(document)))
        if context is not None:
            tokens = ["WEB: Cached context of", document, "is", context[0], ", ", context[1]]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        else:
            tokens = ["WEB: No cached context for", document, "."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            obj, offset = None, -1

        if not context or not self.is_top_level_document(document):
            if not search_if_needed:
                msg = "WEB: Returning None, -1: No top-level document with context " \
                      "and no search requested."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return None, -1
            obj, offset = self.search_for_caret_context(document)
        elif not get_replicant:
            obj, offset = context
        elif not AXObject.is_valid(context[0]):
            msg = "WEB: Context is not valid. Searching for replicant."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            obj, offset = self._find_context_replicant_deprecated()
            if obj:
                caret_obj, caret_offset = self.search_for_caret_context(AXObject.get_parent(obj))
                if caret_obj and AXObject.is_valid(caret_obj):
                    obj, offset = caret_obj, caret_offset
        else:
            obj, offset = context

        tokens = ["WEB: Result context of", document, "is", obj, ", ", offset, "."]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        self.set_caret_context(obj, offset, document)
        return obj, offset

    def _get_caret_context_path_role_and_name(
        self,
        document: Atspi.Accessible | None = None
    ) -> tuple[list[int], Atspi.Role | None, str | None]:
        document = document or self.active_document()
        if not document:
            return [-1], None, None

        rv = self._cached_context_paths_roles_and_names.get(
            hash(AXObject.get_parent(document)))
        if not rv:
            return [-1], None, None

        return rv

    def clear_caret_context(self, document: Atspi.Accessible | None = None) -> None:
        """Clears the caret context."""

        # TODO - JD: All the clearing stuff should be unified.
        self.clear_content_cache()
        document = document or self.active_document()
        if not document:
            return

        parent = AXObject.get_parent(document)
        self._cached_caret_contexts.pop(hash(parent), None)
        self._cached_prior_contexts.pop(hash(parent), None)

    def handle_event_from_context_replicant(self, event, replicant):
        """Attempts to clean up when we can an event from a replacement of the focused object."""

        if AXObject.is_dead(replicant):
            msg = "WEB: Context replicant is dead."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if not focus_manager.get_manager().focus_is_dead():
            msg = "WEB: Not event from context replicant, locus of focus is not dead."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        path, role, name = self._get_caret_context_path_role_and_name()
        replicant_path = AXObject.get_path(replicant)
        if path != replicant_path:
            tokens = ["WEB: Not event from context replicant. Path", path,
                      " != replicant path", replicant_path]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        replicant_role = AXObject.get_role(replicant)
        if role != replicant_role:
            tokens = ["WEB: Not event from context replicant. Role", role,
                      " != replicant role", replicant_role]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        notify = AXObject.get_name(replicant) != name
        document = self.active_document()
        _obj, offset = self._cached_caret_contexts.get(hash(AXObject.get_parent(document)))

        tokens = ["WEB: Is event from context replicant. Notify:", notify]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        focus_manager.get_manager().set_locus_of_focus(event, replicant, notify)
        self.set_caret_context(replicant, offset, document)
        return True

    def _handle_event_for_removed_selectable_child(self, event):
        container = None
        if AXUtilities.is_list_box(event.source):
            container = event.source
        elif AXUtilities.is_tree(event.source):
            container = event.source
        else:
            container = AXObject.find_ancestor(event.source, AXUtilities.is_list_box) \
                or AXObject.find_ancestor(event.source, AXUtilities.is_tree)
        if container is None:
            msg = "WEB: Could not find listbox or tree to recover from removed child."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        tokens = ["WEB: Checking", container, "for focused child."]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        # TODO - JD: Can we remove this? If it's needed, should it be recursive?
        AXObject.clear_cache(container, False, "Handling event for removed selectable child.")
        item = AXUtilities.get_focused_object(container)
        if not (AXUtilities.is_list_item(item) or AXUtilities.is_tree_item):
            msg = "WEB: Could not find focused item to recover from removed child."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        names = self._script.point_of_reference.get('names', {})
        old_name = names.get(hash(focus_manager.get_manager().get_locus_of_focus()))
        notify = AXObject.get_name(item) != old_name

        tokens = ["WEB: Recovered from removed child. New focus is: ", item, "0"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        focus_manager.get_manager().set_locus_of_focus(event, item, notify)
        self.set_caret_context(item, 0)
        return True

    def handle_event_for_removed_child(self, event):
        """Attempts to recover when the current object has been removed from the document."""

        focus = focus_manager.get_manager().get_locus_of_focus()
        if event.any_data == focus:
            msg = "WEB: Removed child is locus of focus."
            debug.print_message(debug.LEVEL_INFO, msg, True)
        elif AXObject.find_ancestor(focus, lambda x: x == event.any_data):
            msg = "WEB: Removed child is ancestor of locus of focus."
            debug.print_message(debug.LEVEL_INFO, msg, True)
        else:
            msg = "WEB: Removed child is not locus of focus nor ancestor of locus of focus."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if event.detail1 == -1:
            msg = "WEB: Event detail1 is useless."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if self._handle_event_for_removed_selectable_child(event):
            return True

        obj, offset = None, -1
        notify = True
        child_count = AXObject.get_child_count(event.source)
        if input_event_manager.get_manager().last_event_was_up():
            if event.detail1 >= child_count:
                msg = "WEB: Last child removed. Getting new location from end of parent."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                obj, offset = self.previous_context(event.source, -1)
            elif 0 <= event.detail1 - 1 < child_count:
                child = AXObject.get_child(event.source, event.detail1 - 1)
                tokens = ["WEB: Getting new location from end of previous child", child, "."]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                obj, offset = self.previous_context(child, -1)
            else:
                prev_obj = self.find_previous_object(event.source)
                tokens = ["WEB: Getting new location from end of source's previous object",
                          prev_obj, "."]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                obj, offset = self.previous_context(prev_obj, -1)

        elif input_event_manager.get_manager().last_event_was_down():
            if event.detail1 == 0:
                msg = "WEB: First child removed. Getting new location from start of parent."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                obj, offset = self.next_context(event.source, -1)
            elif 0 < event.detail1 < child_count:
                child = AXObject.get_child(event.source, event.detail1)
                tokens = ["WEB: Getting new location from start of child", event.detail1,
                          child, "."]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                obj, offset = self.next_context(child, -1)
            else:
                next_obj = self.find_next_object(event.source)
                tokens = ["WEB: Getting new location from start of source's next object",
                          next_obj, "."]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                obj, offset = self.next_context(next_obj, -1)

        else:
            notify = False
            # TODO - JD: Can we remove this? Even if it is needed, we now also clear the
            # cache in _handleEventForRemovedSelectableChild. Also, if it is needed, should
            # it be recursive?
            AXObject.clear_cache(event.source, False, "Handling event for removed child.")
            obj, offset = self.search_for_caret_context(event.source)
            if obj is None:
                obj = AXUtilities.get_focused_object(event.source)

            # Risk "chattiness" if the locusOfFocus is dead and the object we've found is
            # focused and has a different name than the last known focused object.
            if obj and focus_manager.get_manager().focus_is_dead() and AXUtilities.is_focused(obj):
                names = self._script.point_of_reference.get('names', {})
                old_name = names.get(hash(focus_manager.get_manager().get_locus_of_focus()))
                notify = AXObject.get_name(obj) != old_name

        if obj:
            msg = f"WEB: Setting locusOfFocus and context to: {obj}, {offset}"
            focus_manager.get_manager().set_locus_of_focus(event, obj, notify)
            self.set_caret_context(obj, offset)
            return True

        tokens = ["WEB: Unable to find context for child removed from", event.source]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return False

    def _find_context_replicant_deprecated(
        self,
        document: Atspi.Accessible | None = None,
        match_role: bool = True,
        match_name: bool = True
    ) -> tuple[Atspi.Accessible | None, int]:
        path, old_role, old_name = self._get_caret_context_path_role_and_name(document)
        obj = self._get_object_from_path(path)
        if obj and match_role:
            if AXObject.get_role(obj) != old_role:
                obj = None
        if obj and match_name:
            if AXObject.get_name(obj) != old_name:
                obj = None
        if not obj:
            return None, -1

        obj, offset = self.first_context(obj, 0)
        tokens = ["WEB: Context replicant is", obj, ", ", offset]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return obj, offset

    def get_prior_context(
        self,
        document: Atspi.Accessible | None = None
    ) -> tuple[Atspi.Accessible, int] | None:
        """Returns the previously-stored caret context for the given document."""

        if not AXObject.is_valid(document):
            document = self.active_document()

        if document:
            context = self._cached_prior_contexts.get(hash(AXObject.get_parent(document)))
            if context:
                return context

        return None, -1

    def _get_path(self, obj: Atspi.Accessible) -> list[int]:
        rv = self._cached_paths.get(hash(obj))
        if rv is not None:
            return rv

        rv = AXObject.get_path(obj) or [-1]
        self._cached_paths[hash(obj)] = rv
        return rv

    def set_caret_context(
        self,
        obj: Atspi.Accessible | None = None,
        offset: int = -1,
        document: Atspi.Accessible | None = None
    ) -> None:
        """Sets the caret context in document to (obj, offset)."""

        document = document or self.active_document()
        if not document:
            return

        parent = AXObject.get_parent(document)
        old_obj, old_offset = self._cached_caret_contexts.get(hash(parent), (obj, offset))
        self._cached_prior_contexts[hash(parent)] = old_obj, old_offset
        self._cached_caret_contexts[hash(parent)] = obj, offset

        path = self._get_path(obj)
        role = AXObject.get_role(obj)
        name = AXObject.get_name(obj)
        self._cached_context_paths_roles_and_names[hash(parent)] = path, role, name

    def first_context(self, obj: Atspi.Accessible, offset: int) -> tuple[Atspi.Accessible, int]:
        """Returns the first viable/valid caret context given obj and offset."""

        self._cached_can_have_caret_context_decision = {}
        rv = self._first_context(obj, offset)
        self._cached_can_have_caret_context_decision = {}
        return rv

    def _first_context(self, obj, offset):
        tokens = ["WEB: Looking for first caret context for", obj, ", ", offset]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        role = AXObject.get_role(obj)
        look_in_child = [Atspi.Role.LIST,
                         Atspi.Role.INTERNAL_FRAME,
                         Atspi.Role.TABLE,
                         Atspi.Role.TABLE_ROW]
        if role in look_in_child \
           and AXObject.get_child_count(obj) and not self.treat_as_div(obj, offset):
            first_child = AXObject.get_child(obj, 0)
            tokens = ["WEB: Will look in child", first_child, "for first caret context"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return self._first_context(first_child, 0)

        treat_as_text = self.treat_as_text_object(obj)
        if not treat_as_text and self._can_have_caret_context(obj):
            tokens = ["WEB: First caret context for non-text context is", obj, "0"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return obj, 0

        length = AXText.get_character_count(obj)
        if treat_as_text and offset >= length:
            if self.is_content_editable_with_embedded_objects(obj) \
               and input_event_manager.get_manager().last_event_was_character_navigation():
                next_obj, next_offset = self.next_context(obj, length)
                if not next_obj:
                    tokens = ["WEB: No next object found at end of contenteditable", obj]
                    debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                elif not self.is_content_editable_with_embedded_objects(next_obj):
                    tokens = ["WEB: Next object", next_obj,
                              "found at end of contenteditable", obj, "is not editable"]
                    debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                else:
                    tokens = ["WEB: First caret context at end of contenteditable", obj,
                              "is next context", next_obj, ", ", next_offset]
                    debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                    return next_obj, next_offset

            tokens = ["WEB: First caret context at end of", obj, ", ", offset, "is",
                      obj, ", ", length]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return obj, length

        offset = max(0, offset)
        if treat_as_text:
            all_text = AXText.get_all_text(obj)
            if (all_text and all_text[offset] != "\ufffc") or role == Atspi.Role.ENTRY:
                msg = "WEB: First caret context is unchanged"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return obj, offset

            # Descending an element that we're treating as whole can lead to looping/getting stuck.
            if self._element_lines_are_single_chars(obj):
                msg = "WEB: EOC in single-char-lines element. Returning context unchanged."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return obj, offset

        child = AXHypertext.find_child_at_offset(obj, offset)
        if not child:
            msg = "WEB: Child at offset is null. Returning context unchanged."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return obj, offset

        if self.is_document(obj):
            while self._is_useless_empty_element(child):
                tokens = ["WEB: Child", child, "of", obj, "at offset", offset, "cannot be context."]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                offset += 1
                child = AXHypertext.find_child_at_offset(obj, offset)

        if self._is_empty_anchor(child):
            next_obj, next_offset = self.next_context(obj, offset)
            if next_obj:
                tokens = ["WEB: First caret context at end of empty anchor", obj,
                          "is next context", next_obj, ", ", next_offset]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                return next_obj, next_offset

        if not self._can_have_caret_context(child):
            tokens = ["WEB: Child", child, "cannot be context. Returning", obj, ", ", offset]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return obj, offset

        tokens = ["WEB: Looking in child", child, "for first caret context for", obj, ", ", offset]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return self._first_context(child, 0)

    def find_next_caret_in_order(
        self,
        obj: Atspi.Accessible | None = None,
        offset: int = -1
    ) -> tuple[Atspi.Accessible, int]:
        """Returns the next (obj, offset) to the specified one."""

        start_time = time.time()
        rv = self._find_next_caret_in_order_internal(obj, offset)
        tokens = ["WEB: Next caret in order for", obj, ", ", offset, ":",
                  rv[0], ", ", rv[1], f"({time.time() - start_time:.4f}s)"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return rv

    def _find_next_caret_in_order_internal(
        self,
        obj: Atspi.Accessible | None = None,
        offset: int = -1
    ) -> tuple[Atspi.Accessible, int]:
        if not obj:
            obj, offset = self.get_caret_context()

        if not obj or not self.in_document_content(obj):
            return None, -1

        if self._can_have_caret_context(obj):
            if self.treat_as_text_object(obj) and AXText.get_character_count(obj):
                all_text = AXText.get_all_text(obj)
                for i in range(offset + 1, len(all_text)):
                    child = AXHypertext.find_child_at_offset(obj, i)
                    if child and all_text[i] != "\ufffc":
                        tokens = ["ERROR: Child", child, "found at offset with char '",
                                  all_text[i].replace("\n", "\\n"), "'"]
                        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                        if offset == AXHypertext.get_character_offset_in_parent(child):
                            tokens = ["WEB: Handling error by returning", obj, i]
                            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                            return obj, i
                    if self._can_have_caret_context(child):
                        if self._treat_object_as_whole(child, -1):
                            return child, 0
                        return self._find_next_caret_in_order_internal(child, -1)
                    if all_text[i] not in (
                            "\ufffc", self.ZERO_WIDTH_NO_BREAK_SPACE):
                        return obj, i
            elif AXObject.get_child_count(obj) and not self._treat_object_as_whole(obj, offset):
                return self._find_next_caret_in_order_internal(AXObject.get_child(obj, 0), -1)
            elif offset < 0 and not self.is_text_block_element(obj):
                return obj, 0

        # If we're here, start looking up the tree, up to the document.
        if self.is_top_level_document(obj):
            return None, -1

        while obj and (parent := AXObject.get_parent(obj)):
            # TODO - JD: Is this detached document logic still needed?
            if self._is_detached_document(parent):
                obj = self._iframe_for_detached_document(parent)
                continue

            if not AXObject.is_valid(parent):
                msg = "WEB: Finding next caret in order. Parent is not valid."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                if AXObject.get_parent(parent):
                    obj = parent
                    continue
                break

            start, end, length = self._range_in_parent_with_length(obj)
            if start + 1 == end and 0 <= start < end <= length:
                return self._find_next_caret_in_order_internal(parent, start)

            child = AXObject.get_next_sibling(obj)
            if child:
                return self._find_next_caret_in_order_internal(child, -1)
            obj = parent

        return None, -1

    def find_previous_caret_in_order(
        self,
        obj: Atspi.Accessible | None = None,
        offset: int = -1
    ) -> tuple[Atspi.Accessible, int]:
        """Returns the previous (obj, offset) to the specified one."""

        start_time = time.time()
        rv = self._find_previous_caret_in_order_internal(obj, offset)
        tokens = ["WEB: Previous caret in order for", obj, ", ", offset, ":",
                  rv[0], ", ", rv[1], f"({time.time() - start_time:.4f}s)"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return rv

    def _find_previous_caret_in_order_internal(
        self,
        obj: Atspi.Accessible | None = None,
        offset: int = -1
    ) -> tuple[Atspi.Accessible, int]:
        if not obj:
            obj, offset = self.get_caret_context()

        if not obj or not self.in_document_content(obj):
            return None, -1

        if self._can_have_caret_context(obj):
            if self.treat_as_text_object(obj) and AXText.get_character_count(obj):
                all_text = AXText.get_all_text(obj)
                if offset == -1 or offset > len(all_text):
                    offset = len(all_text)
                for i in range(offset - 1, -1, -1):
                    child = AXHypertext.find_child_at_offset(obj, i)
                    if child and all_text[i] != "\ufffc":
                        tokens = ["ERROR: Child", child, "found at offset with char '",
                                  all_text[i].replace("\n", "\\n"), "'"]
                        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                    if self._can_have_caret_context(child):
                        if self._treat_object_as_whole(child, -1):
                            return child, 0
                        return self._find_previous_caret_in_order_internal(child, -1)
                    if all_text[i] not in ("\ufffc", self.ZERO_WIDTH_NO_BREAK_SPACE):
                        return obj, i
            elif AXObject.get_child_count(obj) and not self._treat_object_as_whole(obj, offset):
                return self._find_previous_caret_in_order_internal(
                    AXObject.get_child(obj, AXObject.get_child_count(obj) - 1), -1)
            elif offset < 0 and not self.is_text_block_element(obj):
                return obj, 0

        # If we're here, start looking up the tree, up to the document.
        if self.is_top_level_document(obj):
            return None, -1

        while obj and (parent := AXObject.get_parent(obj)):
            # TODO - JD: Is this detached document logic still needed?
            if self._is_detached_document(parent):
                obj = self._iframe_for_detached_document(parent)
                continue

            if not AXObject.is_valid(parent):
                msg = "WEB: Finding previous caret in order. Parent is not valid."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                if AXObject.get_parent(parent):
                    obj = parent
                    continue
                break

            start, end, length = self._range_in_parent_with_length(obj)
            if start + 1 == end and 0 <= start < end <= length:
                return self._find_previous_caret_in_order_internal(parent, start)

            child = AXObject.get_previous_sibling(obj)
            if child:
                return self._find_previous_caret_in_order_internal(child, -1)
            obj = parent

        return None, -1

    def handle_as_live_region(self, event: Atspi.Event) -> bool:
        """Returns true if event should be handled as a live region."""

        if not settings_manager.get_manager().get_setting("inferLiveRegions"):
            return False

        if not AXUtilities.is_live_region(event.source):
            return False

        if not settings_manager.get_manager().get_setting("presentLiveRegionFromInactiveTab") \
           and self.get_top_level_document_for_object(event.source) != self.active_document():
            msg = "WEB: Live region source is not in active tab."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        alert = AXObject.find_ancestor(event.source, AXUtilities.is_aria_alert)
        if alert and AXUtilities.get_focused_object(alert) == event.source:
            msg = "WEB: Focused source will be presented as part of alert"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        return True
