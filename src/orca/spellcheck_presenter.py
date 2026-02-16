# Orca
#
# Copyright 2014-2026 Igalia, S.L.
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

"""Script-customizable support for application spellcheckers."""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations


import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from orca import dbus_service
from orca import debug
from orca import gsettings_registry
from orca import focus_manager
from orca import guilabels
from orca import messages
from orca import object_properties
from orca import preferences_grid_base
from orca import presentation_manager
from orca import settings
from orca import speech_presenter
from orca.ax_object import AXObject
from orca.ax_selection import AXSelection
from orca.ax_text import AXText
from orca.ax_utilities import AXUtilities

if TYPE_CHECKING:
    from .scripts import default


@dataclass
class _SpellCheckWidgets:
    """Widget references for an active spellcheck session."""

    window: Atspi.Accessible
    error_widget: Atspi.Accessible
    suggestions_list: Atspi.Accessible
    change_to_entry: Atspi.Accessible | None
    document: Atspi.Accessible | None


@dataclass
class _PresentationState:
    """Tracking state to avoid duplicate presentations."""

    last_presented_suggestion: Atspi.Accessible | None = None
    error_widget_text: str = ""
    context_line: tuple[str, int, int] = field(default_factory=lambda: ("", -1, -1))
    completion_announced: bool = False

    def reset(self) -> None:
        """Reset presentation state for a new spellcheck session."""
        self.last_presented_suggestion = None
        self.error_widget_text = ""
        self.context_line = ("", -1, -1)
        self.completion_announced = False


@gsettings_registry.get_registry().gsettings_schema("org.gnome.Orca.Spellcheck", name="spellcheck")
class SpellCheckPresenter:
    """Singleton presenter for spell check support and preferences."""

    _SCHEMA = "spellcheck"

    def _get_setting(self, key: str, fallback: bool) -> bool:
        """Returns the dconf value for key, or fallback if not in dconf."""

        return gsettings_registry.get_registry().layered_lookup(
            self._SCHEMA, key, "b", fallback=fallback
        )

    def __init__(self) -> None:
        self._script: default.Script | None = None
        self._widgets: _SpellCheckWidgets | None = None
        self._state: _PresentationState = _PresentationState()
        self._listener: Atspi.EventListener = Atspi.EventListener.new(self._on_event)

        msg = "SPELLCHECK PRESENTER: Registering D-Bus commands."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        controller = dbus_service.get_remote_controller()
        controller.register_decorated_module("SpellCheckPresenter", self)

    @gsettings_registry.get_registry().gsetting(
        key="spell-error",
        schema="spellcheck",
        gtype="b",
        default=True,
        summary="Spell misspelled word",
        settings_key="spellcheckSpellError",
    )
    @dbus_service.getter
    def get_spell_error(self) -> bool:
        """Returns whether misspelled word should be spelled."""

        return self._get_setting("spell-error", settings.spellcheckSpellError)

    @dbus_service.setter
    def set_spell_error(self, value: bool) -> bool:
        """Sets whether misspelled word should be spelled."""

        if self.get_spell_error() == value:
            return True

        msg = f"SPELLCHECK PRESENTER: Setting spell error to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(self._SCHEMA, "spell-error", value)
        return True

    @gsettings_registry.get_registry().gsetting(
        key="spell-suggestion",
        schema="spellcheck",
        gtype="b",
        default=True,
        summary="Spell suggested correction",
        settings_key="spellcheckSpellSuggestion",
    )
    @dbus_service.getter
    def get_spell_suggestion(self) -> bool:
        """Returns whether the suggested correction should be spelled."""

        return self._get_setting("spell-suggestion", settings.spellcheckSpellSuggestion)

    @dbus_service.setter
    def set_spell_suggestion(self, value: bool) -> bool:
        """Sets whether the suggested correction should be spelled."""

        if self.get_spell_suggestion() == value:
            return True

        msg = f"SPELLCHECK PRESENTER: Setting spell suggestion to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(self._SCHEMA, "spell-suggestion", value)
        return True

    @gsettings_registry.get_registry().gsetting(
        key="present-context",
        schema="spellcheck",
        gtype="b",
        default=True,
        summary="Present context/surrounding sentence",
        settings_key="spellcheckPresentContext",
    )
    @dbus_service.getter
    def get_present_context(self) -> bool:
        """Returns whether to present the context/surrounding sentence."""

        return self._get_setting("present-context", settings.spellcheckPresentContext)

    @dbus_service.setter
    def set_present_context(self, value: bool) -> bool:
        """Sets whether to present the context/surrounding sentence."""

        if self.get_present_context() == value:
            return True

        msg = f"SPELLCHECK PRESENTER: Setting present context to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(self._SCHEMA, "present-context", value)
        return True

    def create_preferences_grid(self) -> "SpellCheckPreferencesGrid":
        """Create and return the spell check preferences grid."""

        return SpellCheckPreferencesGrid(self)

    # pylint: disable-next=too-many-branches, too-many-return-statements
    def _on_event(self, event: Atspi.Event) -> None:
        """Listener for spellcheck-related events."""

        if self._widgets is None:
            return

        if AXObject.is_dead(self._widgets.window):
            self.deactivate()
            return

        if AXUtilities.get_application(event.source) != AXUtilities.get_application(
            self._widgets.window
        ):
            return

        debug.print_message(debug.LEVEL_INFO, "\nvvvvv PROCESS SPELL CHECK EVENT vvvvv")
        tokens = ["SPELL CHECK PRESENTER: Event:", event]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if not AXObject.is_ancestor(event.source, self._widgets.window, inclusive=True):
            debug.print_message(debug.LEVEL_INFO, "^^^^^ PROCESS SPELL CHECK EVENT ^^^^^\n")
            return

        if event.type.startswith("object:property-change:accessible-name"):
            self._handle_name_changed(event)
        elif (
            event.type.startswith("object:state-changed:sensitive")
            and self._widgets.change_to_entry
        ):
            self._handle_change_to_entry_sensitive_changed(event)
        elif event.type.startswith("object:selection-changed"):
            self._handle_suggestions_list_change(event)
        elif event.type.startswith("object:active-descendant-changed"):
            self._handle_suggestions_list_change(event)
        debug.print_message(debug.LEVEL_INFO, "^^^^^ PROCESS SPELL CHECK EVENT ^^^^^\n")

    def activate(self, window: Atspi.Accessible) -> bool:
        """Activates spellcheck support."""

        tokens = ["SPELL CHECK PRESENTER: Attempting activation for", window]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        error_widget, suggestions_list, change_to_entry = self._find_spellcheck_widgets(window)
        if error_widget is None or suggestions_list is None:
            tokens = ["SPELL CHECK PRESENTER:", window, "is not spellcheck window"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        document = self._get_document_from_cursor_history(window)
        tokens = ["SPELL CHECK PRESENTER: Document:", document]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._widgets = _SpellCheckWidgets(
            window=window,
            error_widget=error_widget,
            suggestions_list=suggestions_list,
            change_to_entry=change_to_entry,
            document=document,
        )
        self._state.reset()

        msg = "SPELL CHECK PRESENTER: Registering event listeners"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self._listener.register("object:property-change:accessible-name")
        self._listener.register("object:state-changed:sensitive")
        self._listener.register("object:selection-changed")
        self._listener.register("object:active-descendant-changed")

        # Silently set locus of focus to the deepest focused child in the dialog
        # to prevent focus claims from document objects from interrupting presentation.
        focused = AXUtilities.get_focused_object(window)
        while focused is not None:
            child = AXUtilities.get_focused_object(focused)
            if child is None or child == focused:
                break
            focused = child
        if focused is not None:
            tokens = ["SPELL CHECK PRESENTER: Setting locus of focus to", focused]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            focus_manager.get_manager().set_locus_of_focus(None, focused, notify_script=False)

        msg = "SPELL CHECK PRESENTER: Activation complete"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    def deactivate(self) -> None:
        """Deactivates spellcheck support."""

        if self._widgets is None:
            return

        msg = "SPELL CHECK PRESENTER: Deregistering event listeners"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self._listener.deregister("object:property-change:accessible-name")
        self._listener.deregister("object:state-changed:sensitive")
        self._listener.deregister("object:selection-changed")
        self._listener.deregister("object:active-descendant-changed")

        self._clear_state()

    def _get_document_from_cursor_history(
        self, window: Atspi.Accessible
    ) -> Atspi.Accessible | None:
        """Gets the document object from the focus manager's cursor history."""

        manager = focus_manager.get_manager()

        def is_valid_document(obj: Atspi.Accessible | None) -> bool:
            if obj is None or AXObject.is_dead(obj):
                return False
            if obj == window or AXObject.is_ancestor(obj, window):
                return False
            if not AXObject.supports_text(obj):
                return False
            if not AXUtilities.is_editable(obj) and not AXObject.find_ancestor(
                obj, AXUtilities.is_editable
            ):
                return False
            return True

        last_obj, _ = manager.get_last_cursor_position()
        if is_valid_document(last_obj):
            return last_obj

        penult_obj, _ = manager.get_penultimate_cursor_position()
        if is_valid_document(penult_obj):
            return penult_obj

        return None

    def _get_misspelled_word(self) -> str:
        """Returns the misspelled word."""

        if self._widgets is None:
            return ""

        text = AXText.get_all_text(self._widgets.error_widget) or AXObject.get_name(
            self._widgets.error_widget
        )
        if not text:
            return ""

        # For most apps, the error widget text/name contains only the misspelled word.
        if len(text.split()) == 1:
            return text

        # For soffice, the error widget contains the full sentence with the misspelled word
        # highlighted in red.
        app = AXUtilities.get_application(self._widgets.window)
        app_name = AXObject.get_name(app).lower().split(".")[-1]
        if app_name == "soffice":
            word = self._find_red_text(self._widgets.error_widget)
            if word and not word.isspace():
                return word.strip(".,;:!?")

        return text

    def _find_red_text(self, obj: Atspi.Accessible) -> str:
        """Finds text with red foreground color (misspelled word indicator in soffice)."""

        length = AXText.get_character_count(obj)
        if length <= 0:
            return ""

        offset = 0
        while offset < length:
            attrs, start, end = AXText.get_text_attributes_at_offset(obj, offset)
            if attrs.get("fg-color") == "255,0,0":
                word = AXText.get_substring(obj, start, end)
                tokens = ["SPELL CHECK PRESENTER: Found red text:", word]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                return word
            offset = max(end, offset + 1)

        return ""

    def is_active(self) -> bool:
        """Returns True if spellcheck support is currently being used."""

        return self._widgets is not None

    def is_spell_check_window(self, window: Atspi.Accessible) -> bool:
        """Returns True if window is the window/dialog containing the spellcheck."""

        return self._widgets is not None and window == self._widgets.window

    def _is_complete(self) -> bool:
        """Returns True if we have reason to conclude the check is complete."""

        if self._widgets is None or AXObject.is_dead(self._widgets.window):
            msg = "SPELL CHECK PRESENTER: Window is gone; spellcheck complete"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        AXObject.clear_cache(self._widgets.suggestions_list)
        if not AXUtilities.is_sensitive(self._widgets.suggestions_list):
            msg = "SPELL CHECK PRESENTER: Suggestions list is insensitive; spellcheck complete"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        return False

    def handle_window_event(self, event: Atspi.Event, script: default.Script) -> bool:
        """Handles window activate/deactivate events. Returns True if spellcheck-related."""

        self._script = script
        if event.type.startswith("window:activate"):
            return self._handle_window_activated(event)

        return False

    def _handle_change_to_entry_sensitive_changed(self, event: Atspi.Event) -> bool:
        """Handles sensitive state change on the change-to entry."""

        tokens = [
            "SPELL CHECK PRESENTER: Handling change-to entry sensitive change for",
            event.source,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if self._widgets is None or event.source != self._widgets.change_to_entry:
            tokens = ["SPELL CHECK PRESENTER:", event.source, "is not the change-to entry"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        msg = "SPELL CHECK PRESENTER: Change-to entry sensitivity changed. Checking for completion."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return self._present_completion_message()

    def _handle_name_changed(self, event: Atspi.Event) -> bool:
        """Handles name-changed events that might indicate a new misspelled word."""

        tokens = ["SPELL CHECK PRESENTER: Handling name change for", event.source]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if self._widgets is None:
            msg = "SPELL CHECK PRESENTER: Spellcheck is not active."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if not AXObject.is_ancestor(event.source, self._widgets.window, inclusive=True):
            tokens = ["SPELL CHECK PRESENTER:", event.source, "is not in the spellcheck window"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        msg = "SPELL CHECK PRESENTER: Name changed in spellcheck window; checking for error change"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return self._check_and_present_if_error_changed()

    def _handle_suggestions_list_change(self, event: Atspi.Event) -> bool:
        """Handles selection-changed and active-descendant-changed events for suggestions list."""

        tokens = [
            "SPELL CHECK PRESENTER: Handling suggestions list change for",
            event.source,
            "Event type:",
            event.type,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if self._widgets is None or event.source != self._widgets.suggestions_list:
            tokens = ["SPELL CHECK PRESENTER:", event.source, "is not the suggestions list"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        items = AXSelection.get_selected_children(event.source)
        selected_item = items[0] if len(items) == 1 else None

        if AXUtilities.is_focused(event.source):
            if selected_item is not None:
                assert self._script is not None
                msg = "SPELL CHECK PRESENTER: List is focused; presenting selected suggestion"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                # If focus is newly entering the list, clear last_presented_suggestion
                # so we announce the item even if it was presented during error details.
                current_focus = focus_manager.get_manager().get_locus_of_focus()
                if not AXObject.is_ancestor(current_focus, self._widgets.suggestions_list):
                    self._state.last_presented_suggestion = None
                focus_manager.get_manager().set_locus_of_focus(
                    None, selected_item, notify_script=False
                )
                self._script.update_braille(selected_item)
                self._present_suggestion_list_item()
            return True

        if selected_item == self._state.last_presented_suggestion:
            tokens = [
                "SPELL CHECK PRESENTER: Selection unchanged since last presentation:",
                selected_item,
            ]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        msg = "SPELL CHECK PRESENTER: List is not focused; checking for error change"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        # If we have no document, reset last error text to force presentation.
        if self._widgets.document is None:
            self._state.error_widget_text = ""

        self._check_and_present_if_error_changed()
        return True

    # pylint: disable-next=too-many-return-statements
    def _check_and_present_if_error_changed(self) -> bool:
        """Checks if the misspelled word changed and presents if so."""

        if self._widgets is None:
            msg = "SPELL CHECK PRESENTER: Not active; not checking for error change"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if self._state.completion_announced:
            msg = "SPELL CHECK PRESENTER: Completion already announced; ignoring"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if self._is_complete():
            msg = "SPELL CHECK PRESENTER: Spellcheck is complete; presenting completion"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return self._present_completion_message()

        # Check full error widget text first - if it changed, we have a new error
        error_widget_text = AXText.get_all_text(self._widgets.error_widget) or AXObject.get_name(
            self._widgets.error_widget
        )
        error_text_changed = error_widget_text != self._state.error_widget_text

        current_word = self._get_misspelled_word()
        if not current_word:
            msg = "SPELL CHECK PRESENTER: No current error word"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        # Multi-word content in non-editable widget is not a misspelled word (may be completion msg)
        if len(current_word.split()) > 1 and not AXUtilities.is_editable(
            self._widgets.error_widget
        ):
            return self._present_completion_message()

        # Check if context line changed (detects same word at different position)
        current_context_line: tuple[str, int, int] = ("", -1, -1)
        if self._widgets.document is not None:
            current_context_line = AXText.get_line_at_offset(self._widgets.document)
        context_changed = current_context_line != self._state.context_line

        msg = (
            f"SPELL CHECK PRESENTER: error_text_changed={error_text_changed} "
            f"context_changed={context_changed}"
        )
        debug.print_message(debug.LEVEL_INFO, msg, True)

        if not error_text_changed and not context_changed:
            msg = "SPELL CHECK PRESENTER: Error text and context unchanged; not presenting"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        msg = "SPELL CHECK PRESENTER: Error changed; presenting"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self._state.last_presented_suggestion = None
        self.present_error_details()
        self._state.error_widget_text = error_widget_text
        self._state.context_line = current_context_line
        return True

    def _handle_window_activated(self, event: Atspi.Event) -> bool:
        """Handles window activation."""

        tokens = ["SPELL CHECK PRESENTER: Handling window:activate for", event.source]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if not (self.is_spell_check_window(event.source) or self.activate(event.source)):
            msg = "SPELL CHECK PRESENTER: Not a spellcheck window. Deactivating."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self.deactivate()
            return False

        msg = "SPELL CHECK PRESENTER: Window activated; checking for error to present"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self._state.error_widget_text = ""  # Reset to force presentation
        self._state.context_line = ("", -1, -1)
        self._check_and_present_if_error_changed()
        if self._widgets is not None and self._widgets.change_to_entry is not None:
            assert self._script is not None
            focus_manager.get_manager().set_locus_of_focus(
                None, self._widgets.change_to_entry, False
            )
            self._script.update_braille(self._widgets.change_to_entry)
        return True

    def _present_context(self) -> bool:
        """Presents the context/surrounding content of the misspelled word."""

        if self._widgets is None:
            return False

        word = self._get_misspelled_word()
        if not word:
            return False

        if self._script is None:
            return False

        string = self._get_context_string(word)
        if not string:
            return False

        msg = messages.MISSPELLED_WORD_CONTEXT % string.strip()
        voice = self._script.speech_generator.voice(string=msg)
        presentation_manager.get_manager().speak_message(msg, voice=voice)
        return True

    def _get_context_string(self, word: str) -> str:
        """Returns the context string containing the misspelled word."""

        if self._widgets is None:
            return ""

        error_text = AXText.get_all_text(self._widgets.error_widget)
        if error_text and word in error_text and len(error_text.split()) > 1:
            tokens = ["SPELL CHECK PRESENTER: Using error widget text as context"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return error_text

        if self._widgets.document is None:
            return ""

        string, start, end = AXText.get_line_at_offset(self._widgets.document)
        msg = f"SPELL CHECK PRESENTER: Line at offset {start}-{end}: {string}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        if not string or word not in string:
            return ""

        if len(string) > 80:
            sentences = re.split(r"(?:\.|\!|\?)", string)
            if string.count(word) == 1:
                match = list(filter(lambda x: word in x, sentences))
                if match:
                    return match[0].strip()

        return string

    def _present_completion_message(self) -> bool:
        """Presents the message that spellcheck is complete."""

        if self._widgets is None or not self._is_complete():
            return False

        if self._state.completion_announced:
            msg = "SPELL CHECK PRESENTER: Completion already announced"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if self._script is None:
            return False

        msg = AXText.get_all_text(self._widgets.error_widget) or AXObject.get_name(
            self._widgets.error_widget
        )
        manager = presentation_manager.get_manager()
        manager.speak_message(msg)

        # Don't restore previous braille content to prevent accidental clicks on old elements.
        manager.present_braille_message(msg, restore_previous=False)
        self._state.completion_announced = True
        return True

    def present_error_details(
        self, detailed: bool = False, script: default.Script | None = None
    ) -> bool:
        """Presents the details of the error."""

        if script is not None:
            self._script = script

        if self._is_complete():
            msg = "SPELL CHECK PRESENTER: Not presenting error details: spellcheck is complete"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if self._present_mistake(detailed):
            self._present_suggestion(detailed)
            if detailed or self.get_present_context():
                self._present_context()
            return True

        return False

    def _present_mistake(self, detailed: bool = False) -> bool:
        """Presents the misspelled word."""

        if self._widgets is None:
            msg = "SPELL CHECK PRESENTER: Not presenting mistake: spellcheck is not active"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if self._script is None:
            return False

        word = self._get_misspelled_word()
        if not word:
            msg = "SPELL CHECK PRESENTER: Not presenting mistake: misspelled word not found"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        msg = messages.MISSPELLED_WORD % word
        voice = self._script.speech_generator.voice(string=msg)
        presentation_manager.get_manager().speak_message(msg, voice=voice)
        if detailed or self.get_spell_error():
            presentation_manager.get_manager().spell_item(word)

        return True

    def _present_suggestion(self, detailed: bool = False) -> bool:
        """Presents the suggested correction."""

        if self._widgets is None:
            msg = "SPELL CHECK PRESENTER: Not presenting suggestion: spellcheck is not active"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if not self._widgets.change_to_entry:
            return self._present_suggestion_list_item(detailed, include_label=True)

        if self._script is None:
            return False

        label = AXUtilities.get_displayed_label(self._widgets.change_to_entry) or AXObject.get_name(
            self._widgets.change_to_entry
        )
        string = AXText.get_substring(self._widgets.change_to_entry, 0, -1)
        msg = f"{label} {string}"
        voice = self._script.speech_generator.voice(string=msg)
        presentation_manager.get_manager().speak_message(msg, voice=voice)
        if detailed or self.get_spell_suggestion():
            presentation_manager.get_manager().spell_item(string)

        items = AXSelection.get_selected_children(self._widgets.suggestions_list)
        if len(items) == 1:
            self._state.last_presented_suggestion = items[0]

        return True

    def _present_suggestion_list_item(
        self, detailed: bool = False, include_label: bool = False
    ) -> bool:
        """Presents the current item from the suggestions list."""

        if self._widgets is None:
            msg = "SPELL CHECK PRESENTER: Not presenting suggested item: spellcheck is not active"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if self._script is None:
            return False

        items = AXSelection.get_selected_children(self._widgets.suggestions_list)
        if len(items) != 1:
            return False

        if items[0] == self._state.last_presented_suggestion:
            return False
        self._state.last_presented_suggestion = items[0]

        if include_label:
            label = AXUtilities.get_displayed_label(
                self._widgets.suggestions_list
            ) or AXObject.get_name(self._widgets.suggestions_list)
        else:
            label = ""
        string = AXObject.get_name(items[0])

        msg = f"{label} {string}"
        voice = self._script.speech_generator.voice(string=msg)
        presentation_manager.get_manager().speak_message(msg.strip(), voice=voice)
        if detailed or self.get_spell_suggestion():
            presentation_manager.get_manager().spell_item(string)

        if (
            speech_presenter.get_presenter().get_speak_position_in_set()
            and items[0] == focus_manager.get_manager().get_locus_of_focus()
        ):
            index = AXUtilities.get_position_in_set(items[0]) + 1
            total = AXUtilities.get_set_size(items[0])
            msg = object_properties.GROUP_INDEX_SPEECH % {"index": index, "total": total}
            presentation_manager.get_manager().speak_message(msg)

        return True

    def _clear_state(self) -> None:
        """Clears all session state."""
        self._script = None
        self._widgets = None
        self._state.reset()

    def _has_id(self, obj: Atspi.Accessible, target_id: str) -> bool:
        """Returns True if obj has target_id as accessible ID or object attribute 'id'."""

        if AXObject.get_accessible_id(obj) == target_id:
            return True
        if AXObject.get_attribute(obj, "id") == target_id:
            return True
        return False

    def _could_be_spellcheck_window(self, window: Atspi.Accessible, app_name: str) -> bool:
        """Returns True if window could be the spellcheck window."""

        # What we want. LibreOffice uses this.
        if self._has_id(window, "SpellingDialog"):
            return True

        # Fallback: thunderbird uses frame with tag=body; no ID.
        # Unfortunately, thunderbird does this for the main window with tons of descendants.
        if app_name == "thunderbird":
            if AXObject.get_attribute(window, "tag") != "body":
                return False
            return AXObject.find_descendant(window, AXUtilities.is_menu) is None

        # Fallback: gedit/pluma uses a modal dialog (gedit) or frame (pluma); no ID.
        if app_name in ("gedit", "pluma"):
            return AXUtilities.is_modal(window)

        return False

    def _could_be_error_widget(self, obj: Atspi.Accessible, app_name: str) -> bool:
        """Returns True if obj could be the error widget."""

        # What we want. Thunderbird uses this.
        if self._has_id(obj, "MisspelledWord"):
            return True

        # Fallback: soffice uses "errorsentence".
        if app_name == "soffice":
            return AXObject.get_accessible_id(obj) == "errorsentence"

        # Fallback: gedit/pluma uses label with single word, no colon.
        if app_name in ("gedit", "pluma") and AXUtilities.is_label(obj):
            name_tokens = AXObject.get_name(obj).split()
            return len(name_tokens) == 1 and ":" not in name_tokens[0]

        return False

    def _could_be_suggestions_list(self, obj: Atspi.Accessible, app_name: str) -> bool:
        """Returns True if obj could be the suggestions list."""

        # What we want. Thunderbird uses "SuggestedList", but the "SuggestionsList" seems nicer,
        # given the label is typically "Suggestions:". But we'll happily accept either.
        if self._has_id(obj, "SuggestedList") or self._has_id(obj, "SuggestionsList"):
            return True

        # Fallback: soffice uses "suggestionslb".
        if app_name == "soffice":
            return AXObject.get_accessible_id(obj) == "suggestionslb"

        # Fallback: gedit/pluma uses a table which manages descendants.
        if app_name in ("gedit", "pluma"):
            return AXUtilities.is_table(obj) and AXUtilities.manages_descendants(obj)

        return False

    def _could_be_change_to_entry(self, obj: Atspi.Accessible, app_name: str) -> bool:
        """Returns True if obj could be the change-to entry."""

        # TODO - JD: What we want (need to try to find consensus).

        # soffice lacks a change-to entry.
        if app_name == "soffice":
            return False

        # Fallback: Thunderbird uses this.
        if self._has_id(obj, "ReplaceWordInput"):
            return True

        # Fallback: gedit/pluma uses labelled single-line editable
        if app_name in ("gedit", "pluma"):
            return AXUtilities.is_single_line_entry(obj)

        return False

    def _find_spellcheck_widgets(
        self, window: Atspi.Accessible
    ) -> tuple[Atspi.Accessible | None, Atspi.Accessible | None, Atspi.Accessible | None]:
        """Finds spellcheck widgets. Returns (error_widget, suggestions_list, change_to_entry)."""

        app = AXUtilities.get_application(window)
        app_name = AXObject.get_name(app).lower().split(".")[-1]

        if not self._could_be_spellcheck_window(window, app_name):
            return None, None, None

        error_widget = AXObject.find_descendant(
            window, lambda obj: self._could_be_error_widget(obj, app_name)
        )
        suggestions_list = AXObject.find_descendant(
            window, lambda obj: self._could_be_suggestions_list(obj, app_name)
        )
        change_to_entry = (
            None
            if app_name == "soffice"
            else AXObject.find_descendant(
                window, lambda obj: self._could_be_change_to_entry(obj, app_name)
            )
        )

        # soffice: errorsentence ID is on panel; get text child if needed
        if error_widget is not None and not AXObject.supports_text(error_widget):
            if text_child := AXObject.find_descendant(error_widget, AXObject.supports_text):
                error_widget = text_child

        tokens = [
            "SPELL CHECK PRESENTER: Error widget:",
            error_widget,
            "Suggestions list:",
            suggestions_list,
            "Change-to entry:",
            change_to_entry,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return error_widget, suggestions_list, change_to_entry


class SpellCheckPreferencesGrid(preferences_grid_base.AutoPreferencesGrid):
    """GtkGrid containing the Spell Check preferences page."""

    _gsettings_schema = "spellcheck"

    def __init__(self, presenter: SpellCheckPresenter) -> None:
        controls = [
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.SPELL_CHECK_SPELL_ERROR,
                getter=presenter.get_spell_error,
                setter=presenter.set_spell_error,
                prefs_key="spellcheckSpellError",
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.SPELL_CHECK_SPELL_SUGGESTION,
                getter=presenter.get_spell_suggestion,
                setter=presenter.set_spell_suggestion,
                prefs_key="spellcheckSpellSuggestion",
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.SPELL_CHECK_PRESENT_CONTEXT,
                getter=presenter.get_present_context,
                setter=presenter.set_present_context,
                prefs_key="spellcheckPresentContext",
            ),
        ]

        super().__init__(
            guilabels.SPELL_CHECK, controls, info_message=guilabels.SPELL_CHECK_DESCRIPTION
        )


_presenter: SpellCheckPresenter = SpellCheckPresenter()


def get_presenter() -> SpellCheckPresenter:
    """Returns the Spell Check Presenter"""

    return _presenter
