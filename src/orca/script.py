# Orca
#
# Copyright 2004-2009 Sun Microsystems Inc.
# Copyright 2011-2026 Igalia, S.L.
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

# pylint:disable=too-many-instance-attributes
# pylint:disable=unused-argument

"""The base Script class."""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import (
    braille_generator,
    chat_presenter,
    debug,
    script_utilities,
    sound_generator,
    speech_generator,
    structural_navigator,
)
from .ax_object import AXObject

if TYPE_CHECKING:
    from collections.abc import Callable

    import gi

    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

    from . import label_inference


class Script:
    """The base Script class."""

    def __init__(self, app: Atspi.Accessible) -> None:
        self.app = app
        self.app_name: str | None = AXObject.get_name(self.app) or None
        self.name = f"{self.app_name or 'default'} (module={self.__module__})"
        self.present_if_inactive: bool = True
        self.run_find_command_on: Atspi.Accessible | None = None
        self.point_of_reference: dict = {}
        self.event_cache: dict = {}

        self.listeners = self.get_listeners()
        self.utilities = self.get_utilities()

        self._braille_generator = self._create_braille_generator()
        self._sound_generator = self._create_sound_generator()
        self._speech_generator = self._create_speech_generator()

        # pylint:disable=assignment-from-none
        self.label_inference = self.get_label_inference()
        self.chat = self.get_chat()
        # pylint:enable=assignment-from-none

        self.set_up_commands()

        self._default_sn_mode: structural_navigator.NavigationMode = (
            structural_navigator.NavigationMode.OFF
        )
        self._default_caret_navigation_enabled: bool = False

        msg = f"SCRIPT: {self.name} initialized"
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def __str__(self) -> str:
        return f"{self.name}"

    def get_listeners(self) -> dict[str, Callable]:
        """Returns a dictionary of the event listeners for this script."""

        return {
            "document:attributes-changed": self._on_document_attributes_changed,
            "document:load-complete": self._on_document_load_complete,
            "document:load-stopped": self._on_document_load_stopped,
            "document:page-changed": self._on_document_page_changed,
            "document:reload": self._on_document_reload,
            "mouse:button": self._on_mouse_button,
            "object:active-descendant-changed": self._on_active_descendant_changed,
            "object:announcement": self._on_announcement,
            "object:attributes-changed": self._on_object_attributes_changed,
            "object:children-changed:add": self._on_children_added,
            "object:children-changed:remove": self._on_children_removed,
            "object:column-reordered": self._on_column_reordered,
            "object:property-change:accessible-description": self._on_description_changed,
            "object:property-change:accessible-name": self._on_name_changed,
            "object:property-change:accessible-value": self._on_value_changed,
            "object:row-reordered": self._on_row_reordered,
            "object:selection-changed": self._on_selection_changed,
            "object:state-changed:active": self._on_active_changed,
            "object:state-changed:busy": self._on_busy_changed,
            "object:state-changed:checked": self._on_checked_changed,
            "object:state-changed:expanded": self._on_expanded_changed,
            "object:state-changed:focused": self._on_focused_changed,
            "object:state-changed:indeterminate": self._on_indeterminate_changed,
            "object:state-changed:invalid-entry": self._on_invalid_entry_changed,
            "object:state-changed:pressed": self._on_pressed_changed,
            "object:state-changed:selected": self._on_selected_changed,
            "object:state-changed:sensitive": self._on_sensitive_changed,
            "object:state-changed:showing": self._on_showing_changed,
            "object:text-attributes-changed": self._on_text_attributes_changed,
            "object:text-caret-moved": self._on_caret_moved,
            "object:text-changed:delete": self._on_text_deleted,
            "object:text-changed:insert": self._on_text_inserted,
            "object:text-selection-changed": self._on_text_selection_changed,
            "object:value-changed": self._on_value_changed,
            "window:activate": self._on_window_activated,
            "window:create": self._on_window_created,
            "window:deactivate": self._on_window_deactivated,
            "window:destroy": self._on_window_destroyed,
        }

    def set_up_commands(self) -> None:
        """Sets up commands with CommandManager."""

    def _create_braille_generator(self) -> braille_generator.BrailleGenerator:
        """Creates and returns the braille generator for this script."""

        return braille_generator.BrailleGenerator(self)

    def _create_sound_generator(self) -> sound_generator.SoundGenerator:
        """Creates and returns the sound generator for this script."""

        return sound_generator.SoundGenerator(self)

    def _create_speech_generator(self) -> speech_generator.SpeechGenerator:
        """Creates and returns the speech generator for this script."""

        return speech_generator.SpeechGenerator(self)

    def get_braille_generator(self) -> braille_generator.BrailleGenerator:
        """Returns the braille generator for this script."""

        return self._braille_generator

    def get_sound_generator(self) -> sound_generator.SoundGenerator:
        """Returns the sound generator for this script."""

        return self._sound_generator

    def get_speech_generator(self) -> speech_generator.SpeechGenerator:
        """Returns the speech generator for this script."""

        return self._speech_generator

    def get_chat(self) -> chat_presenter.Chat:
        """Returns the Chat object for this script."""

        # In practice, self will always be an instance/subclass of default.Script.
        return chat_presenter.Chat(self)  # type: ignore[arg-type]

    def get_utilities(self) -> script_utilities.Utilities:
        """Returns the utilities for this script."""

        return script_utilities.Utilities(self)

    def get_label_inference(self) -> label_inference.LabelInference | None:
        """Returns the label inference functionality for this script."""

        return None

    def locus_of_focus_changed(
        self,
        event: Atspi.Event | None,
        old_focus: Atspi.Accessible | None,
        new_focus: Atspi.Accessible | None,
    ) -> bool:
        """Handles changes of focus of interest. Returns True if this script did all needed work."""

        return True

    def is_activatable_event(self, event: Atspi.Event) -> bool:
        """Returns True if event should cause this script to become active."""

        return True

    def force_script_activation(self, event: Atspi.Event) -> bool:
        """Allows scripts to insist that they should become active."""

        return False

    def activate(self) -> None:
        """Called when this script is activated."""

    def deactivate(self) -> None:
        """Called when this script is deactivated."""

    def _on_active_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:active accessibility events."""
        return True

    def _on_active_descendant_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:active-descendant-changed accessibility events."""
        return True

    def _on_announcement(self, event: Atspi.Event) -> bool:
        """Callback for object:announcement events."""
        return True

    def _on_busy_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:busy accessibility events."""
        return True

    def _on_caret_moved(self, event: Atspi.Event) -> bool:
        """Callback for object:text-caret-moved accessibility events."""
        return True

    def _on_checked_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:checked accessibility events."""
        return True

    def _on_children_added(self, event: Atspi.Event) -> bool:
        """Callback for object:children-changed:add accessibility events."""
        return True

    def _on_children_removed(self, event: Atspi.Event) -> bool:
        """Callback for object:children-changed:remove accessibility events."""
        return True

    def _on_column_reordered(self, event: Atspi.Event) -> bool:
        """Callback for object:column-reordered accessibility events."""
        return True

    def _on_description_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:property-change:accessible-description events."""
        return True

    def _on_document_attributes_changed(self, event: Atspi.Event) -> bool:
        """Callback for document:attributes-changed accessibility events."""
        return True

    def _on_document_load_complete(self, event: Atspi.Event) -> bool:
        """Callback for document:load-complete accessibility events."""
        return True

    def _on_document_load_stopped(self, event: Atspi.Event) -> bool:
        """Callback for document:load-stopped accessibility events."""
        return True

    def _on_document_page_changed(self, event: Atspi.Event) -> bool:
        """Callback for document:page-changed accessibility events."""
        return True

    def _on_document_reload(self, event: Atspi.Event) -> bool:
        """Callback for document:reload accessibility events."""
        return True

    def _on_expanded_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:expanded accessibility events."""
        return True

    def _on_focused_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:focused accessibility events."""
        return True

    def _on_indeterminate_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:indeterminate accessibility events."""
        return True

    def _on_invalid_entry_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:invalid-entry accessibility events."""
        return True

    def _on_mouse_button(self, event: Atspi.Event) -> bool:
        """Callback for mouse:button events."""
        return True

    def _on_name_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:property-change:accessible-name events."""
        return True

    def _on_object_attributes_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:attributes-changed accessibility events."""
        return True

    def _on_pressed_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:pressed accessibility events."""
        return True

    def _on_row_reordered(self, event: Atspi.Event) -> bool:
        """Callback for object:row-reordered accessibility events."""
        return True

    def _on_selected_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:selected accessibility events."""
        return True

    def _on_selection_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:selection-changed accessibility events."""
        return True

    def _on_sensitive_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:sensitive accessibility events."""
        return True

    def _on_showing_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:showing accessibility events."""
        return True

    def _on_text_attributes_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:text-attributes-changed accessibility events."""
        return True

    def _on_text_deleted(self, event: Atspi.Event) -> bool:
        """Callback for object:text-changed:delete accessibility events."""
        return True

    def _on_text_inserted(self, event: Atspi.Event) -> bool:
        """Callback for object:text-changed:insert accessibility events."""
        return True

    def _on_text_selection_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:text-selection-changed accessibility events."""
        return True

    def _on_value_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:property-change:accessible-value accessibility events."""
        return True

    def _on_window_activated(self, event: Atspi.Event) -> bool:
        """Callback for window:activate accessibility events."""
        return True

    def _on_window_created(self, event: Atspi.Event) -> bool:
        """Callback for window:create accessibility events."""
        return True

    def _on_window_deactivated(self, event: Atspi.Event) -> bool:
        """Callback for window:deactivate accessibility events."""
        return True

    def _on_window_destroyed(self, event: Atspi.Event) -> bool:
        """Callback for window:destroy accessibility events."""
        return True

    def present_object(self, obj: Atspi.Accessible, **args) -> None:
        """Presents the current object."""

    def update_braille(self, obj: Atspi.Accessible, **args) -> None:
        """Updates the braille display to show obj."""
