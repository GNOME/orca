# Orca
#
# Copyright 2026 Igalia, S.L.
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

"""Presents changes in text selection."""

from __future__ import annotations

import functools
from typing import TYPE_CHECKING

from . import (
    ax_cache_manager,
    debug,
    document_presenter,
    input_event_manager,
    messages,
    presentation_manager,
    speech_presenter,
)
from .ax_object import AXObject
from .ax_text import AXText
from .ax_utilities import AXUtilities

if TYPE_CHECKING:
    import gi

    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

    from .scripts import default


class TextSelectionPresenter:
    """Presents changes in text selection."""

    DOCUMENT_SELECTION_BOUNDARIES = "TextSelectionPresenter.document-selection-boundaries"

    def __init__(self) -> None:
        self._manager = ax_cache_manager.get_manager()
        self._manager.register_cache(
            self,
            self.DOCUMENT_SELECTION_BOUNDARIES,
            lifetime=ax_cache_manager.Lifetime.OWNER,
            clear_on_demand=ax_cache_manager.ClearPolicy.PRESERVE,
            clear_interval_seconds=None,
        )
        self._document_selection_boundaries = self._manager.get_cache(
            self,
            self.DOCUMENT_SELECTION_BOUNDARIES,
        )

    def _get_cached_document_selection_boundaries(
        self,
        script: default.Script,
    ) -> tuple[Atspi.Accessible | None, Atspi.Accessible | None]:
        if self._document_selection_boundaries is None:
            return None, None
        return self._document_selection_boundaries.get(
            ax_cache_manager.get_object_key(script),
            (None, None),
        )

    def _set_cached_document_selection_boundaries(
        self,
        script: default.Script,
        boundaries: tuple[Atspi.Accessible | None, Atspi.Accessible | None],
    ) -> None:
        if self._document_selection_boundaries is not None:
            self._document_selection_boundaries.put(
                ax_cache_manager.get_object_key(script),
                boundaries,
            )

    def _compute_changes(
        self,
        script: default.Script,
        obj: Atspi.Accessible,
        old_string: str,
        old_start: int,
        old_end: int,
        new_string: str,
        new_start: int,
        new_end: int,
    ) -> tuple[list[list], bool]:
        """Returns the changes and whether a preceding child change was presented."""

        old_chars = set(range(old_start, old_end))
        new_chars = set(range(new_start, new_end))
        if not old_chars.union(new_chars):
            return [], False

        if old_chars and new_chars and not old_chars.intersection(new_chars):
            return (
                [
                    [old_start, old_end, messages.TEXT_UNSELECTED],
                    [new_start, new_end, messages.TEXT_SELECTED],
                ],
                False,
            )

        change = sorted(old_chars.symmetric_difference(new_chars))
        if not change:
            return [], False

        changes = []
        preceding_child_change_presented = False
        change_start, change_end = change[0], change[-1] + 1
        if old_chars < new_chars:
            changes.append([change_start, change_end, messages.TEXT_SELECTED])
            if old_string.endswith("\ufffc") and old_end == change_start:
                child = AXUtilities.find_child_at_offset(obj, old_end - 1)
                preceding_child_change_presented = self._handle_basic_change(
                    script,
                    child,
                    False,
                )
        else:
            changes.append([change_start, change_end, messages.TEXT_UNSELECTED])
            if new_string.endswith("\ufffc"):
                child = AXUtilities.find_child_at_offset(obj, new_end - 1)
                preceding_child_change_presented = self._handle_basic_change(
                    script,
                    child,
                    False,
                )
        return changes, preceding_child_change_presented

    def _present_changes(
        self,
        script: default.Script,
        obj: Atspi.Accessible,
        changes: list[list],
        speak_message: bool,
        preceding_child_change_presented: bool,
    ) -> None:
        """Presents the supplied selection changes."""

        speak_message = (
            speak_message and not speech_presenter.get_presenter().get_only_speak_displayed_text()
        )
        for start, end, message in changes:
            string = AXText.get_substring(obj, start, end)
            ends_with_child = string.endswith("\ufffc")
            effective_end = end - 1 if ends_with_child else end
            message_presented = False
            tokens = [
                "TEXT SELECTION PRESENTER: Presenting change in",
                obj,
                f"range {start}-{end}",
                f"message='{message}'",
                f"ends with child: {ends_with_child}",
            ]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

            if len(string) > 5000 and speak_message:
                if message == messages.TEXT_SELECTED:
                    presentation_manager.get_manager().speak_message(
                        messages.selected_character_count(len(string)),
                    )
                else:
                    presentation_manager.get_manager().speak_message(
                        messages.unselected_character_count(len(string)),
                    )
                message_presented = True
            else:
                script.say_phrase(obj, start, effective_end)
                if speak_message and not ends_with_child:
                    presentation_manager.get_manager().speak_message(message)
                    message_presented = True

            destination_child_change_presented = False
            if ends_with_child:
                child = AXUtilities.find_child_at_offset(obj, effective_end)
                destination_child_change_presented = self._handle_basic_change(
                    script,
                    child,
                    speak_message,
                )

            if (
                speak_message
                and preceding_child_change_presented
                and not message_presented
                and not destination_child_change_presented
            ):
                presentation_manager.get_manager().speak_message(message)
            preceding_child_change_presented = False

    def _handle_basic_change(
        self,
        script: default.Script,
        obj: Atspi.Accessible,
        speak_message: bool,
    ) -> bool:
        """Handles a selection change in obj."""

        if (
            not AXObject.supports_text(obj)
            or input_event_manager.get_manager().last_event_was_cut()
        ):
            tokens = ["TEXT SELECTION PRESENTER: Ignoring basic change for", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        old_string, old_start, old_end = AXUtilities.get_cached_selected_text(obj)
        AXUtilities.update_cached_selected_text(obj)
        new_string, new_start, new_end = AXUtilities.get_cached_selected_text(obj)
        tokens = [
            "TEXT SELECTION PRESENTER: Selection in",
            obj,
            f"changed from {old_start}-{old_end} ({len(old_string)} chars)",
            f"to {new_start}-{new_end} ({len(new_string)} chars)",
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if input_event_manager.get_manager().last_event_was_select_all() and new_string:
            if new_string != old_string:
                presentation_manager.get_manager().speak_message(messages.DOCUMENT_SELECTED_ALL)
            return True

        if (
            not input_event_manager.get_manager().last_event_was_caret_selection()
            and old_string
            and not new_string
        ):
            presentation_manager.get_manager().speak_message(messages.SELECTION_REMOVED)
            return False

        changes, preceding_child_change_presented = self._compute_changes(
            script,
            obj,
            old_string,
            old_start,
            old_end,
            new_string,
            new_start,
            new_end,
        )
        tokens = ["TEXT SELECTION PRESENTER: Computed changes for", obj, changes]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        if not changes:
            return False

        self._present_changes(
            script,
            obj,
            changes,
            speak_message,
            preceding_child_change_presented,
        )
        return True

    def _find_document_selection_boundary(
        self,
        root: Atspi.Accessible,
        find_start: bool,
    ) -> Atspi.Accessible | None:
        string = AXUtilities.get_selected_text(root)[0]
        if not string:
            return None
        if find_start and not string.startswith("\ufffc"):
            return root
        if not find_start and not string.endswith("\ufffc"):
            return root

        indices = list(range(AXObject.get_child_count(root)))
        if not find_start:
            indices.reverse()
        for index in indices:
            result = self._find_document_selection_boundary(
                AXObject.get_child(root, index),
                find_start,
            )
            if result is not None:
                return result
        return None

    def _get_document_selection_boundaries(
        self,
        root: Atspi.Accessible,
    ) -> tuple[Atspi.Accessible | None, Atspi.Accessible | None]:
        return (
            self._find_document_selection_boundary(root, True),
            self._find_document_selection_boundary(root, False),
        )

    @staticmethod
    def _get_document_selection_elements(
        start_obj: Atspi.Accessible | None,
        end_obj: Atspi.Accessible | None,
    ) -> list[Atspi.Accessible]:
        if not (start_obj and end_obj):
            return []
        if AXObject.is_dead(start_obj):
            msg = "TEXT SELECTION PRESENTER: Cannot get elements: Start object is dead."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return []

        def _include(x):
            return x is not None

        def _exclude(x):
            return not AXUtilities.is_web_element(x)

        elements = []
        start_parent = AXObject.get_parent(start_obj)
        for index in range(
            AXObject.get_index_in_parent(start_obj),
            AXObject.get_child_count(start_parent),
        ):
            child = AXObject.get_child(start_parent, index)
            if not AXUtilities.is_web_element(child):
                continue
            elements.append(child)
            if not AXUtilities.is_code(child):
                elements.extend(AXUtilities.find_all_descendants(child, _include, _exclude))
            if end_obj in elements:
                break

        if end_obj == start_obj:
            return elements
        if end_obj not in elements:
            elements.append(end_obj)
            if not AXUtilities.is_code(end_obj):
                elements.extend(AXUtilities.find_all_descendants(end_obj, _include, _exclude))

        end_parent = AXObject.get_parent(end_obj)
        end_index = AXObject.get_index_in_parent(end_obj)
        last_obj = AXObject.get_child(end_parent, end_index + 1) or end_obj
        try:
            elements_end = elements.index(last_obj)
        except ValueError:
            pass
        else:
            if last_obj == end_obj:
                elements_end += 1
            elements = elements[:elements_end]
        return elements

    def _handle_document_change(
        self,
        script: default.Script,
        obj: Atspi.Accessible,
        speak_message: bool,
    ) -> bool:
        old_start, old_end = self._get_cached_document_selection_boundaries(script)
        start, end = self._get_document_selection_boundaries(obj)
        self._set_cached_document_selection_boundaries(script, (start, end))
        tokens = [
            "TEXT SELECTION PRESENTER: Document selection event from",
            obj,
            "Old boundaries:",
            old_start,
            old_end,
            "New boundaries:",
            start,
            end,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        old_elements = self._get_document_selection_elements(old_start, old_end)
        if start == old_start and end == old_end:
            elements = old_elements
        else:
            new_elements = self._get_document_selection_elements(start, end)

            def _compare(obj1, obj2):
                return AXUtilities.path_comparison(AXObject.get_path(obj1), AXObject.get_path(obj2))

            elements = sorted(
                set(old_elements).union(new_elements),
                key=functools.cmp_to_key(_compare),
            )

        tokens = [
            "TEXT SELECTION PRESENTER: Document selection element count:",
            len(elements),
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if not elements:
            return False

        elements_set = set(elements)
        for element in elements:
            if element not in (old_start, old_end, start, end) and AXUtilities.find_ancestor(
                element,
                lambda x: x in elements_set,
            ):
                tokens = ["TEXT SELECTION PRESENTER: Updating nested selection cache for", element]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                AXUtilities.update_cached_selected_text(element)
            else:
                tokens = ["TEXT SELECTION PRESENTER: Presenting selection change for", element]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                self._handle_basic_change(script, element, speak_message)
        return True

    def handle_text_selection_change(
        self,
        script: default.Script,
        obj: Atspi.Accessible,
        speak_message: bool = True,
    ) -> bool:
        """Handles and presents a change in selected text."""

        is_document = bool(
            AXUtilities.is_web_element(obj)
            and script.utilities.in_document_content(obj)
            and not document_presenter.get_presenter().in_focus_mode(script.app)
        )
        tokens = [
            "TEXT SELECTION PRESENTER: Handling change for",
            obj,
            "Script:",
            script,
            f"speak message: {speak_message}",
            f"is document selection: {is_document}",
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        if is_document:
            return self._handle_document_change(script, obj, speak_message)
        return self._handle_basic_change(script, obj, speak_message)


_presenter: TextSelectionPresenter = TextSelectionPresenter()


def get_presenter() -> TextSelectionPresenter:
    """Returns the text selection presenter."""

    return _presenter
