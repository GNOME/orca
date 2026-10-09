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

from typing import TYPE_CHECKING, Any

from . import (
    ax_cache_manager,
    debug,
    document_presenter,
    input_event_manager,
    messages,
    presentation_manager,
    speech_presenter,
    text_selection_manager,
)
from .ax_object import AXObject
from .ax_text import AXText
from .ax_utilities import AXUtilities

if TYPE_CHECKING:
    from collections.abc import Hashable

    import gi

    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

    from .input_event import InputEvent
    from .scripts import default

    DocumentTextChange = tuple[
        tuple[Atspi.Accessible, int],
        tuple[Atspi.Accessible, int],
        bool,
        bool,
        str,
    ]


class TextSelectionPresenter:
    """Presents changes in text selection."""

    def __init__(self) -> None:
        self._last_selection_removal: tuple[Hashable, InputEvent] | None = None

    def present_selected_text(
        self,
        script: default.Script,
        obj: Atspi.Accessible,
    ) -> bool:
        """Presents all text in the logical selection containing obj."""

        text = text_selection_manager.get_manager().get_all_selected_text(script, obj)
        if not text:
            presentation_manager.get_manager().speak_message(messages.NO_SELECTED_TEXT)
            return True

        manager = speech_presenter.get_presenter()
        indentation = manager.get_indentation_description(text, only_if_changed=False)
        text = manager.adjust_for_presentation(obj, text)
        message = messages.SELECTED_TEXT_IS % f"{indentation} {text}"
        presentation_manager.get_manager().speak_message(message)
        return True

    def present_selection_removed(self, obj: Atspi.Accessible | None = None) -> None:
        """Presents that the current text selection was removed."""

        event = input_event_manager.get_manager().get_last_input_event()
        self._last_selection_removal = (
            (ax_cache_manager.get_object_key(obj), event)
            if obj is not None and event is not None
            else None
        )
        presentation_manager.get_manager().speak_message(messages.SELECTION_REMOVED)

    def selection_removal_was_presented(self, obj: Atspi.Accessible) -> bool:
        """Returns whether selection removal in obj was presented for the current input."""

        if self._last_selection_removal is None:
            return False
        obj_key, event = self._last_selection_removal
        if obj_key != ax_cache_manager.get_object_key(obj):
            return False
        return input_event_manager.get_manager().last_event_equals_or_is_release_for_event(event)

    @staticmethod
    def _present_pending_page_change(obj: Atspi.Accessible) -> bool:
        """Presents a page change associated with obj's selection command."""

        page_number = text_selection_manager.get_manager().take_deferred_page_change_for_selection(
            obj
        )
        if page_number is None:
            return False
        presentation_manager.get_manager().present_message(messages.PAGE_NUMBER % page_number)
        return True

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
            child = (
                AXUtilities.find_child_at_offset(obj, effective_end) if ends_with_child else None
            )
            tokens = [
                "TEXT SELECTION PRESENTER: Presenting change in",
                obj,
                "range",
                start,
                "-",
                end,
                "message='",
                message,
                "'",
                "ends with child:",
                ends_with_child,
            ]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

            child_processed = False
            message_presented = False
            destination_child_change_presented = False
            if child is not None and string[:-1].isspace() and AXObject.supports_text(child):
                child_processed = True
                destination_child_change_presented = self._handle_basic_change(
                    script,
                    child,
                    speak_message,
                )
                if destination_child_change_presented:
                    tokens = [
                        "TEXT SELECTION PRESENTER: Suppressing whitespace before changed child",
                        child,
                    ]
                    debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                    continue

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
                script.say_phrase(obj, start, effective_end, include_whole_objects=True)
                if speak_message and (not ends_with_child or child_processed):
                    presentation_manager.get_manager().speak_message(message)
                    message_presented = True

            if ends_with_child:
                if child is None:
                    continue
                if AXObject.supports_text(child) and not child_processed:
                    destination_child_change_presented = self._handle_basic_change(
                        script,
                        child,
                        speak_message,
                    )
                else:
                    presentation_manager.get_manager().present_object(
                        script,
                        child,
                        generate_braille=False,
                    )
                    if speak_message:
                        presentation_manager.get_manager().speak_message(message)
                        message_presented = True

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
            "changed from",
            old_start,
            "-",
            old_end,
            "(",
            len(old_string),
            "chars)",
            "to",
            new_start,
            "-",
            new_end,
            "(",
            len(new_string),
            "chars)",
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if input_event_manager.get_manager().last_event_was_select_all() and new_string:
            if new_string != old_string:
                presentation_manager.get_manager().speak_message(messages.DOCUMENT_SELECTED_ALL)
            return True

        if (
            not text_selection_manager.get_manager().is_selection_change_from_selection_command(obj)
            and old_string
            and not new_string
        ):
            if speak_message:
                self.present_selection_removed(obj)
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

        self._present_pending_page_change(obj)
        self._present_changes(
            script,
            obj,
            changes,
            speak_message,
            preceding_child_change_presented,
        )
        return True

    def _get_document_text_change(
        self,
        old_start: tuple[Atspi.Accessible | None, int],
        old_end: tuple[Atspi.Accessible | None, int],
        start: tuple[Atspi.Accessible | None, int],
        end: tuple[Atspi.Accessible | None, int],
    ) -> DocumentTextChange | None:
        """Returns the changed document range and its selection state."""

        old_start_obj, _old_start_offset = old_start
        old_end_obj, _old_end_offset = old_end
        start_obj, _start_offset = start
        end_obj, _end_offset = end
        if old_start_obj is None and old_end_obj is None:
            if start_obj is not None and end_obj is not None:
                return start, end, True, False, messages.TEXT_SELECTED
            return None
        if start_obj is None and end_obj is None:
            if old_start_obj is not None and old_end_obj is not None:
                return old_start, old_end, True, False, messages.TEXT_UNSELECTED
            return None

        if None in (old_start_obj, old_end_obj, start_obj, end_obj):
            return None
        starts_are_same = AXUtilities.compare_text_positions(*start, *old_start) == 0
        ends_are_same = AXUtilities.compare_text_positions(*end, *old_end) == 0
        if starts_are_same and not ends_are_same:
            comparison = AXUtilities.compare_text_positions(*old_end, *end)
            if comparison < 0:
                return old_end, end, True, False, messages.TEXT_SELECTED
            if comparison > 0:
                return end, old_end, True, False, messages.TEXT_UNSELECTED
        if ends_are_same and not starts_are_same:
            comparison = AXUtilities.compare_text_positions(*old_start, *start)
            if comparison > 0:
                return start, old_start, True, False, messages.TEXT_SELECTED
            if comparison < 0:
                return old_start, start, True, False, messages.TEXT_UNSELECTED
        return None

    def _present_document_text_change(
        self,
        script: default.Script,
        old_start: tuple[Atspi.Accessible | None, int],
        old_end: tuple[Atspi.Accessible | None, int],
        start: tuple[Atspi.Accessible | None, int],
        end: tuple[Atspi.Accessible | None, int],
        speak_message: bool,
        *,
        change: DocumentTextChange | None = None,
    ) -> bool:
        """Presents a document text selection change as a single phrase."""

        if change is None:
            change = self._get_document_text_change(old_start, old_end, start, end)
        if change is None:
            msg = "TEXT SELECTION PRESENTER: Could not identify changed document text range."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        range_start, range_end, include_start, include_end, message = change
        selection_obj = start[0] or old_start[0]
        if not text_selection_manager.get_manager().is_selection_change_from_selection_command(
            selection_obj
        ):
            selection_was_removed = start[0] is None and end[0] is None
            if not selection_was_removed:
                msg = "TEXT SELECTION PRESENTER: Change is not from a selection command."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return False

            msg = "TEXT SELECTION PRESENTER: Presenting selection removal."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            if speak_message:
                self.present_selection_removed(selection_obj)
            return True

        start_obj, start_offset = range_start
        end_obj, end_offset = range_end
        unexpanded_objects: list[Atspi.Accessible] = []
        string = AXUtilities.expand_eocs_in_range(
            start_obj,
            start_offset,
            end_obj,
            end_offset,
            include_start=include_start,
            include_end=include_end,
            unexpanded_objects=unexpanded_objects,
        )
        tokens: list[Any] = [
            "TEXT SELECTION PRESENTER: Expanded changed document text range",
            range_start,
            range_end,
            "with endpoint inclusion",
            include_start,
            ",",
            include_end,
            "to '",
            string,
            "'",
            "message='",
            message,
            "'",
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        speak_message = (
            speak_message and not speech_presenter.get_presenter().get_only_speak_displayed_text()
        )
        if not string:
            if any(not AXUtilities.is_image_or_canvas(obj) for obj in unexpanded_objects):
                return False
            self._present_pending_page_change(selection_obj)
            for image in unexpanded_objects:
                presentation_manager.get_manager().present_object(
                    script,
                    image,
                    generate_braille=False,
                )
                if speak_message:
                    presentation_manager.get_manager().speak_message(message)
            # An empty boundary is handled, even when there is nothing to announce.
            return True

        self._present_pending_page_change(selection_obj)
        spoken_string = string.strip() or string
        if len(string) > 5000 and speak_message:
            if message == messages.TEXT_SELECTED:
                presentation_manager.get_manager().speak_message(
                    messages.selected_character_count(len(string)),
                )
            else:
                presentation_manager.get_manager().speak_message(
                    messages.unselected_character_count(len(string)),
                )
            return True

        speech_presenter.get_presenter().speak_phrase(
            script,
            start_obj,
            start_offset,
            end_offset if start_obj == end_obj else start_offset + 1,
            spoken_string,
        )
        if speak_message:
            presentation_manager.get_manager().speak_message(message)
        return True

    def _handle_document_change(
        self,
        script: default.Script,
        obj: Atspi.Accessible,
        speak_message: bool,
    ) -> bool:
        state, old_selection, selection = (
            text_selection_manager.get_manager().update_selection_state(obj)
        )
        if state == text_selection_manager.SelectionChangeState.UNPRESENTABLE:
            msg = "TEXT SELECTION PRESENTER: Ignoring unpresentable document selection state."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        old_start, old_end = old_selection
        start, end = selection
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

        old_start_obj, _old_start_offset = old_start
        old_end_obj, _old_end_offset = old_end
        start_obj, _start_offset = start
        end_obj, _end_offset = end
        if start_obj is not None and start == old_start and end == old_end:
            msg = "TEXT SELECTION PRESENTER: Ignoring duplicate document selection boundaries."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        change = self._get_document_text_change(old_start, old_end, start, end)
        if change is not None and self._present_document_text_change(
            script, old_start, old_end, start, end, speak_message, change=change
        ):
            range_start, range_end, _include_start, _include_end, _message = change
            elements = dict.fromkeys(
                AXUtilities.get_text_selection_elements(range_start[0], range_end[0])
            )
            visited = set()
            for endpoint in (range_start[0], range_end[0]):
                ancestor = endpoint
                while ancestor is not None and ancestor not in visited:
                    visited.add(ancestor)
                    if AXUtilities.is_document(ancestor):
                        break
                    elements[ancestor] = None
                    ancestor = AXObject.get_parent(ancestor)
            for element in elements:
                AXUtilities.update_cached_selected_text(element)
            return True

        old_elements = AXUtilities.get_text_selection_elements(old_start_obj, old_end_obj)
        new_elements = (
            old_elements
            if start_obj == old_start_obj and end_obj == old_end_obj
            else AXUtilities.get_text_selection_elements(start_obj, end_obj)
        )
        if not old_elements and not new_elements:
            manager = text_selection_manager.get_manager()
            if not manager.is_selection_change_from_selection_command(obj):
                return False
            command = manager.get_current_selection_command(obj)
            if command is not None and obj == command.get_selection_container():
                presented = False
                for selection_obj in command.get_objects():
                    presented = (
                        self._handle_basic_change(script, selection_obj, speak_message) or presented
                    )
                return presented
            msg = "TEXT SELECTION PRESENTER: Falling back to event source selection change."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return self._handle_basic_change(script, obj, speak_message)

        elements = dict.fromkeys(old_elements + new_elements)

        tokens = [
            "TEXT SELECTION PRESENTER: Document selection element count:",
            len(elements),
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if not elements:
            return False

        boundary_objects = (old_start_obj, old_end_obj, start_obj, end_obj)
        for element in elements:
            if element not in boundary_objects and AXUtilities.find_ancestor(
                element,
                lambda x: x in elements,
            ):
                tokens = ["TEXT SELECTION PRESENTER: Updating nested selection cache for", element]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                AXUtilities.update_cached_selected_text(element)
            else:
                tokens = ["TEXT SELECTION PRESENTER: Presenting selection change for", element]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                self._handle_basic_change(script, element, speak_message)
        return True

    def present_text_selection_change(
        self,
        script: default.Script,
        obj: Atspi.Accessible,
        speak_message: bool = True,
    ) -> bool:
        """Presents a change in selected text."""

        selection_manager = text_selection_manager.get_manager()
        managed_document = None
        if selection_manager.get_current_selection_command() is not None:
            active_document = script.utilities.active_document()
            if (
                active_document is not None
                and selection_manager.get_current_selection_command(active_document) is not None
            ):
                managed_document = active_document
        is_document = bool(
            obj is not None and (AXUtilities.is_web_element(obj) or managed_document is not None)
        )
        tokens = [
            "TEXT SELECTION PRESENTER: Presenting change for",
            obj,
            "Script:",
            script,
            "speak message:",
            speak_message,
            "is document selection:",
            is_document,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        if (
            is_document
            and script.utilities.in_document_content(obj)
            and not document_presenter.get_presenter().in_focus_mode(script.app)
        ):
            return self._handle_document_change(script, obj, speak_message)
        return self._handle_basic_change(script, obj, speak_message)


_presenter: TextSelectionPresenter = TextSelectionPresenter()


def get_presenter() -> TextSelectionPresenter:
    """Returns the text selection presenter."""

    return _presenter
