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

# pylint: disable=too-many-lines
# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals
# pylint: disable=too-many-positional-arguments
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-return-statements

"""The default Script for presenting information to the user."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from orca import (
    action_presenter,
    braille,
    braille_presenter,
    bypass_mode_manager,
    caret_navigator,
    chat_presenter,
    clipboard,
    cmdnames,
    command_manager,
    debug,
    debugging_tools_manager,
    document_presenter,
    event_manager,
    extension_loader,
    flat_review_finder,
    flat_review_presenter,
    focus_manager,
    guilabels,
    input_event_manager,
    learn_mode_presenter,
    live_region_presenter,
    math_navigator,
    messages,
    mouse_presenter,
    notification_presenter,
    object_navigator,
    orca,
    preferences_presenter,
    presentation_manager,
    profile_manager,
    say_all_presenter,
    script,
    script_manager,
    sleep_mode_manager,
    speech_manager,
    speech_presenter,
    spellcheck_presenter,
    structural_navigator,
    system_information_presenter,
    table_navigator,
    typing_echo_presenter,
    where_am_i_presenter,
)
from orca.ax_object import AXObject
from orca.ax_selection import AXSelection
from orca.ax_text import AXText
from orca.ax_utilities import AXUtilities
from orca.ax_utilities_event import TextEventReason
from orca.ax_utilities_text import CaretSetReason, TextUnit
from orca.command import KeyboardCommand
from orca.generator import PresentationReason

if TYPE_CHECKING:
    import gi

    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi


class Script(script.Script):
    """The default Script for presenting information to the user."""

    _commands_initialized: bool = False

    def _register_builtin_extensions(self) -> None:
        """Registers built-in extensions with the extension loader."""

        loader = extension_loader.get_loader()
        builtins = [
            (braille_presenter.get_presenter, guilabels.BRAILLE),
            (notification_presenter.get_presenter, guilabels.KB_GROUP_NOTIFICATIONS),
            (clipboard.get_presenter, guilabels.KB_GROUP_CLIPBOARD),
            (say_all_presenter.get_presenter, guilabels.GENERAL_SAY_ALL),
            (typing_echo_presenter.get_presenter, guilabels.ECHO),
            (speech_manager.get_manager, guilabels.KB_GROUP_SPEECH_VERBOSITY),
            (speech_presenter.get_presenter, guilabels.KB_GROUP_SPEECH_VERBOSITY),
            (bypass_mode_manager.get_manager, guilabels.KB_GROUP_BYPASS_MODE),
            (sleep_mode_manager.get_manager, guilabels.KB_GROUP_SLEEP_MODE),
            (system_information_presenter.get_presenter, guilabels.KB_GROUP_SYSTEM_INFORMATION),
            (object_navigator.get_navigator, guilabels.KB_GROUP_OBJECT_NAVIGATION),
            (caret_navigator.get_navigator, guilabels.KB_GROUP_CARET_NAVIGATION),
            (structural_navigator.get_navigator, guilabels.KB_GROUP_STRUCTURAL_NAVIGATION),
            (table_navigator.get_navigator, guilabels.KB_GROUP_TABLE_NAVIGATION),
            (math_navigator.get_navigator, guilabels.KB_GROUP_MATH_NAVIGATION),
            (document_presenter.get_presenter, guilabels.KB_GROUP_DOCUMENTS),
            (live_region_presenter.get_presenter, guilabels.KB_GROUP_LIVE_REGIONS),
            (learn_mode_presenter.get_presenter, guilabels.KB_GROUP_LEARN_MODE),
            (mouse_presenter.get_presenter, guilabels.KB_GROUP_MOUSE),
            (action_presenter.get_presenter, guilabels.KB_GROUP_ACTIONS),
            (flat_review_presenter.get_presenter, guilabels.KB_GROUP_FLAT_REVIEW),
            (flat_review_finder.get_finder, guilabels.KB_GROUP_FIND),
            (where_am_i_presenter.get_presenter, guilabels.KB_GROUP_WHERE_AM_I),
            (debugging_tools_manager.get_manager, guilabels.KB_GROUP_DEBUGGING_TOOLS),
            (chat_presenter.get_presenter, guilabels.KB_GROUP_CHAT),
            (profile_manager.get_manager, guilabels.GENERAL_PROFILES),
            (preferences_presenter.get_presenter, guilabels.KB_GROUP_SCREEN_READER_MANAGEMENT),
        ]
        for getter, group_label in builtins:
            loader.register_builtin(getter, group_label)

    def set_up_commands(self) -> None:
        """Sets up commands with CommandManager."""

        tokens = ["DEFAULT: Setting up commands for", self.app]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if Script._commands_initialized:
            msg = "DEFAULT: Commands already initialized."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        Script._commands_initialized = True

        manager = command_manager.get_manager()
        manager.set_up_commands()
        manager.add_command(
            KeyboardCommand(
                "shutdownHandler",
                orca.quit_orca,
                guilabels.KB_GROUP_SCREEN_READER_MANAGEMENT,
                cmdnames.QUIT_ORCA,
            )
        )

        self._register_builtin_extensions()
        extension_loader.get_loader().set_up_all_commands()

        all_braille_keys: set[int] = set()
        for cmd in manager.get_all_braille_commands():
            all_braille_keys.update(cmd.get_braille_bindings())
        braille.setup_key_ranges(all_braille_keys)

        cmd_count = len(command_manager.get_manager().get_all_keyboard_commands())
        msg = f"DEFAULT: Commands set up: {cmd_count} keyboard commands"
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def register_event_listeners(self) -> None:
        """Registers for listeners needed by this script."""

        event_manager.get_manager().register_script_listeners(self)

    def deregister_event_listeners(self) -> None:
        """De-registers the listeners needed by this script."""

        event_manager.get_manager().deregister_script_listeners(self)

    def _get_queued_event(
        self,
        event_type: str,
        detail1: int | None = None,
        detail2: int | None = None,
        any_data=None,
    ) -> Atspi.Event | None:
        cached_event = self.get_queued_event(event_type)
        if not cached_event:
            tokens = ["SCRIPT: No queued event of type", event_type]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return None

        if detail1 is not None and detail1 != cached_event.detail1:
            tokens = [
                "SCRIPT: Queued event's detail1 (",
                str(cached_event.detail1),
                ") doesn't match",
                str(detail1),
            ]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return None

        if detail2 is not None and detail2 != cached_event.detail2:
            tokens = [
                "SCRIPT: Queued event's detail2 (",
                str(cached_event.detail2),
                ") doesn't match",
                str(detail2),
            ]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return None

        if any_data is not None and any_data != cached_event.any_data:
            tokens = [
                "SCRIPT: Queued event's any_data (",
                cached_event.any_data,
                ") doesn't match",
                any_data,
            ]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return None

        tokens = ["SCRIPT: Found matching queued event:", cached_event]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return cached_event

    def locus_of_focus_changed(self, event, old_focus, new_focus):
        """Called when the visual object with focus changes."""

        presentation_manager.get_manager().present_command_announcement()

        if not new_focus:
            return True

        if AXUtilities.is_defunct(new_focus):
            return True

        is_name_change = event and event.type.endswith("accessible-name")
        if old_focus == new_focus and not is_name_change:
            msg = "DEFAULT: old focus == new focus"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if self.run_find_command_on:
            if self.run_find_command_on == new_focus:
                self.run_find_command_on = None
                flat_review_finder.get_finder().find(self)
            return True

        if learn_mode_presenter.get_presenter().is_active():
            learn_mode_presenter.get_presenter().quit()

        document_presenter.get_presenter().update_mode_if_needed(self, old_focus, new_focus)

        active_window = self.utilities.top_level_object(new_focus)
        focus_manager.get_manager().set_active_window(active_window)
        if old_focus is None:
            old_focus = active_window

        manager = presentation_manager.get_manager()
        manager.interrupt_if_needed_for_focus_change(old_focus, new_focus, event)

        if input_event_manager.get_manager().last_event_was_caret_selection():
            handled = False
            if AXObject.supports_text(old_focus):
                handled = self.utilities.handle_text_selection_change(old_focus) or handled
            if AXObject.supports_text(new_focus):
                handled = self.utilities.handle_text_selection_change(new_focus) or handled
            if handled:
                self.update_braille(new_focus)
                return True

        # A name change on the focused object usually means only its value changed (e.g.
        # arrowing a combo box); keep old_focus as prior_obj so we don't re-speak the
        # ancestor context. Reused table rows (e.g. Thunderbird message deletion) are the
        # exception: present those in full.
        prior = old_focus
        if is_name_change and old_focus == new_focus and AXUtilities.is_table_row(new_focus):
            prior = None
        manager.present_object(self, new_focus, prior_obj=prior)
        return True

    def activate(self) -> None:
        """Called when this script is activated."""

        tokens = ["DEFAULT: Activating script for", self.app]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if not focus_manager.get_manager().is_in_preferences_window():
            speech_manager.get_manager().update_punctuation_level()
            speech_manager.get_manager().update_capitalization_style()
            speech_manager.get_manager().update_synthesizer()

        presenter = document_presenter.get_presenter()
        if presenter.has_state_for_app(self.app):
            presenter.restore_mode_for_script(self)
        else:
            reason = "script activation, no prior state"
            presenter.suspend_navigators(self, False, reason)
            structural_navigator.get_navigator().set_mode(self, self._default_sn_mode)
            caret_navigator.get_navigator().set_enabled_for_script(
                self,
                self._default_caret_navigation_enabled,
            )

        table_navigator.get_navigator().refresh_enabled_state()
        command_manager.get_manager().activate_commands(f"activated {self.name}")

    def deactivate(self) -> None:
        """Called when this script is deactivated."""

        if bypass_mode_manager.get_manager().is_active():
            bypass_mode_manager.get_manager().toggle_enabled(self)

    def update_braille(
        self,
        obj: Atspi.Accessible,
        offset: int | None = None,
    ) -> None:
        """Updates the braille display to show obj."""

        if not obj:
            return
        braille_presenter.get_presenter().present_generated_braille(
            self,
            obj,
            offset=offset,
        )

    def handle_braille_pan_at_edge(
        self,
        _direction: braille_presenter.PanDirection,
    ) -> bool | None:
        """Handles braille panning when the presenter reaches the edge of a line."""

        return None

    ########################################################################
    #                                                                      #
    # AT-SPI OBJECT EVENT HANDLERS                                         #
    #                                                                      #
    # Event handlers return bool:                                          #
    # - True: Event was fully handled, no further processing needed        #
    # - False: Event wasn't handled, should be passed to parent handlers   #
    # Default return value is True (event handled by default script)       #
    #                                                                      #
    ########################################################################

    def _on_active_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:active accessibility events."""

        window = event.source
        if AXUtilities.is_dialog_or_alert(window) or AXUtilities.is_frame(window):
            if event.detail1 and not AXUtilities.can_be_active_window(window):
                return True

            source_is_active_window = window == focus_manager.get_manager().get_active_window()
            if source_is_active_window and not event.detail1:
                focus = focus_manager.get_manager().get_locus_of_focus()
                if AXUtilities.is_menu_descendant(focus, inclusive=True):
                    msg = "DEFAULT: Ignoring event. In menu."
                    debug.print_message(debug.LEVEL_INFO, msg, True)
                    return True

                msg = "DEFAULT: Event is for active window. Clearing state."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                focus_manager.get_manager().set_active_window(None)
                return True

            if not source_is_active_window and event.detail1:
                msg = "DEFAULT: Updating active window."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                focus_manager.get_manager().set_active_window(
                    window,
                    set_window_as_focus=True,
                    notify_script=True,
                )

        return True

    def _on_active_descendant_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:active-descendant-changed accessibility events."""

        if AXUtilities.is_presentable_active_descendant_change(event):
            focus_manager.get_manager().set_locus_of_focus(event, event.any_data)

        return True

    def _on_checked_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:checked accessibility events."""

        if AXUtilities.is_presentable_checked_change(event):
            presentation_manager.get_manager().interrupt_if_needed_for_object_presentation()
            self.present_object(event.source, reason=PresentationReason.STATE_CHANGE)

        return True

    def _on_children_added(self, event: Atspi.Event) -> bool:
        """Callback for object:children-changed:add accessibility events."""

        AXUtilities.clear_all_cache_now(event.source, "children-changed event.")
        return True

    def _on_children_removed(self, event: Atspi.Event) -> bool:
        """Callback for object:children-changed:remove accessibility events."""

        AXUtilities.clear_all_cache_now(event.source, "children-changed event.")
        return True

    # pylint: disable-next=too-many-return-statements
    def _on_caret_moved(self, event: Atspi.Event) -> bool:
        """Callback for object:text-caret-moved accessibility events."""

        reason = AXUtilities.get_text_event_reason(event)
        if reason == TextEventReason.SEARCH_PRESENTABLE:
            msg = "DEFAULT: Presenting line for search result change"
            contents = self.utilities.get_line_contents_at_offset(event.source, event.detail1)
            presentation_manager.get_manager().speak_contents(contents)
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if reason == TextEventReason.AUTO_INSERTION_UNPRESENTABLE:
            msg = "DEFAULT: Ignoring caret-moved event believed to be irrelevant auto insertion"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        manager = focus_manager.get_manager()
        focus = manager.get_locus_of_focus()
        if focus != event.source:
            if reason == TextEventReason.FOCUS_CHANGE:
                msg = "DEFAULT: Caret moved due to focus change (focus event missing)"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                manager.set_locus_of_focus(event, event.source)
                return True

            if not AXUtilities.is_focused(event.source):
                msg = "DEFAULT: Change is from unfocused source that is not the locus of focus"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return True
            # TODO - JD: See if this can be removed. If it's still needed document why.
            manager.set_locus_of_focus(event, event.source, False)

        obj, offset = manager.get_last_cursor_position()
        if offset == event.detail1 and obj == event.source:
            navigation_reasons = {
                TextEventReason.NAVIGATION_BY_WORD,
                TextEventReason.NAVIGATION_BY_CHARACTER,
                TextEventReason.NAVIGATION_BY_LINE,
            }
            if reason not in navigation_reasons:
                msg = "DEFAULT: Event is for last saved cursor position"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return True
            msg = "DEFAULT: Position matches but proceeding due to navigation reason"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            presentation_manager.get_manager().interrupt_presentation()

        offset = AXText.get_caret_offset(event.source)

        # TODO - JD: These need to be harmonized / unified / simplified.
        manager.set_last_cursor_position(event.source, offset)
        self.utilities.set_caret_context(event.source, offset)

        # The text-changed and text-selection-changed handlers already refreshed braille
        # and presented speech for these reasons. Letting caret-moved also run would
        # re-emit the same braille line a second time for the same logical operation.
        ignore = [
            TextEventReason.BACKSPACE,
            TextEventReason.CUT,
            TextEventReason.DELETE,
            TextEventReason.PASTE,
            TextEventReason.REDO,
            TextEventReason.SPIN_BUTTON_VALUE_CHANGE,
            TextEventReason.UNDO,
        ]
        if reason in ignore:
            msg = f"DEFAULT: Ignoring event due to reason ({reason})"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            AXUtilities.update_cached_selected_text(event.source)
            return True

        if AXUtilities.has_selected_text(event.source):
            msg = "DEFAULT: Event source has text selections"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self.utilities.handle_text_selection_change(event.source)
            return True

        text, _start, _end = AXUtilities.get_cached_selected_text(obj)
        if text and self.utilities.handle_text_selection_change(obj):
            msg = "DEFAULT: Event handled as text selection change"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        msg = "DEFAULT: Presenting text at new caret position"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self._present_caret_moved_event(event, reason=reason)
        return True

    def _on_description_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:property-change:accessible-description events."""

        if AXUtilities.is_presentable_description_change(event):
            presentation_manager.get_manager().present_message(event.any_data)
        return True

    def _on_document_page_changed(self, event: Atspi.Event) -> bool:
        """Callback for document:page-changed accessibility events."""

        if event.detail1 < 0:
            return True

        presentation_manager.get_manager().present_message(messages.PAGE_NUMBER % event.detail1)
        return True

    def _on_expanded_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:expanded accessibility events."""

        AXUtilities.clear_all_cache_now(event.source, "expanded-changed event.")
        if not AXUtilities.is_presentable_expanded_change(event):
            return True

        presentation_manager.get_manager().interrupt_if_needed_for_object_presentation()
        self.present_object(event.source, reason=PresentationReason.STATE_CHANGE)
        details = AXUtilities.get_details_content(event.source)
        for detail in details:
            presentation_manager.get_manager().speak_message(detail)

        return True

    def _on_indeterminate_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:indeterminate accessibility events."""

        if AXUtilities.is_presentable_indeterminate_change(event):
            presentation_manager.get_manager().interrupt_if_needed_for_object_presentation()
            self.present_object(event.source, reason=PresentationReason.STATE_CHANGE)

        return True

    def _on_invalid_entry_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:invalid-entry accessibility events."""

        if not AXUtilities.is_presentable_invalid_entry_change(event):
            return True

        if event.detail1:
            msg = self.get_speech_generator().get_error_message(event.source)
        else:
            msg = messages.INVALID_ENTRY_FIXED
        presentation_manager.get_manager().speak_message(msg)
        self.update_braille(event.source)
        return True

    def _on_mouse_button(self, event: Atspi.Event) -> bool:
        """Callback for mouse:button events."""

        input_event_manager.get_manager().process_mouse_button_event(event)
        return True

    def _on_announcement(self, event: Atspi.Event) -> bool:
        """Callback for object:announcement events."""

        if isinstance(event.any_data, str):
            presentation_manager.get_manager().present_message(event.any_data)

        return True

    def _on_name_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:property-change:accessible-name events."""

        if not AXUtilities.is_presentable_name_change(event):
            return True

        manager = focus_manager.get_manager()
        if event.source == manager.get_locus_of_focus():
            # Force the update so that braille is refreshed.
            manager.set_locus_of_focus(event, event.source, True, True)
            return True

        presentation_manager.get_manager().present_message(event.any_data)
        return True

    def _on_object_attributes_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:attributes-changed accessibility events."""

        AXUtilities.clear_all_cache_now(event.source, "object-attributes-changed event.")
        return True

    def _on_pressed_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:pressed accessibility events."""

        if AXUtilities.is_presentable_pressed_change(event):
            presentation_manager.get_manager().interrupt_if_needed_for_object_presentation()
            self.present_object(event.source, reason=PresentationReason.STATE_CHANGE)

        return True

    def _on_selected_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:selected accessibility events."""

        if not AXUtilities.is_presentable_selected_change(event):
            return True

        if speech_presenter.get_presenter().get_only_speak_displayed_text():
            return True

        announce_state = False
        manager = input_event_manager.get_manager()
        if manager.last_event_was_space():
            announce_state = True
        elif (
            manager.last_event_was_up() or manager.last_event_was_down()
        ) and AXUtilities.is_table_cell(event.source):
            announce_state = AXUtilities.is_selected(event.source)

        if not announce_state:
            return True

        # TODO - JD: Unlike the other state-changed callbacks, it seems unwise
        # to call generate_speech() here because that also will present the
        # expandable state if appropriate for the object type. The generators
        # need to gain some smarts w.r.t. state changes.

        if event.detail1:
            presentation_manager.get_manager().speak_message(messages.TEXT_SELECTED)
        else:
            presentation_manager.get_manager().speak_message(messages.TEXT_UNSELECTED)

        return True

    def _on_selection_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:selection-changed accessibility events."""

        if not AXUtilities.is_presentable_selection_change(event):
            return True

        presentation_manager.get_manager().present_command_announcement()

        if self.utilities.handle_container_selection_change(event.source):
            return True

        focus = focus_manager.get_manager().get_locus_of_focus()
        mouse_item = mouse_presenter.get_presenter().get_current_item()
        child = AXUtilities.get_selected_child_for_focus(
            event.source,
            focus,
            lambda c: c == mouse_item or AXUtilities.is_layout_only(c),
        )
        if child is not None:
            if AXUtilities.is_page_tab(child) and not AXUtilities.is_focused(child):
                self.present_object(child, generate_braille=False)
            else:
                focus_manager.get_manager().set_locus_of_focus(event, child)

        return True

    def _on_focused_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:focused accessibility events."""

        if not event.detail1:
            return True

        if not AXUtilities.is_focused(event.source):
            tokens = ["DEFAULT:", event.source, "lacks focused state. Clearing cache."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            AXObject.clear_cache(event.source, reason="Event detail1 does not match state.")
            if not AXUtilities.is_focused(event.source):
                msg = "DEFAULT: Clearing cache did not update state."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return True

        obj = event.source
        window, dialog = self.utilities.frame_and_dialog(obj)
        if window and not AXUtilities.can_be_active_window(window) and not dialog:
            return True

        if AXObject.get_child_count(obj) and not AXUtilities.is_combo_box(obj):
            selected_children = AXUtilities.selected_children(obj)
            if selected_children:
                obj = selected_children[0]

        focus_manager.get_manager().set_locus_of_focus(event, obj)
        return True

    def _on_showing_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:showing accessibility events."""

        obj = event.source
        if AXUtilities.is_notification(obj):
            if not event.detail1:
                return True

            presentation_manager.get_manager().speak_message(
                self.get_speech_generator().get_localized_role_name(obj),
            )
            msg = self.utilities.get_notification_content(obj)
            presenter = presentation_manager.get_manager()
            presenter.speak_accessible_text(obj, msg)
            presenter.present_braille_message(msg)
            notification_presenter.get_presenter().save_notification(msg)
            return True

        if AXUtilities.is_tool_tip(obj):
            was_f1 = input_event_manager.get_manager().last_event_was_f1()
            if not was_f1 and not mouse_presenter.get_presenter().get_present_tooltips():
                return True
            if event.detail1:
                presentation_manager.get_manager().interrupt_if_needed_for_object_presentation()
                self.present_object(obj)
                return True

            focus = focus_manager.get_manager().get_locus_of_focus()
            if focus and was_f1:
                obj = focus
                presentation_manager.get_manager().interrupt_if_needed_for_object_presentation()
                self.present_object(obj, prior_obj=event.source)
                return True

        return True

    def _on_text_attributes_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:text-attributes-changed accessibility events."""

        if not AXUtilities.is_presentable_text_attributes_change(event):
            return True

        changes = AXUtilities.get_text_attribute_changes(event.source)

        word, start, _end = AXText.get_word_at_offset(event.source)
        if not word.strip():
            word, start, _end = AXText.get_word_at_offset(event.source, start - 1)

        speech_pres = speech_presenter.get_presenter()
        if error := speech_pres.get_error_description(event.source, start):
            presentation_manager.get_manager().speak_message(error)

        for attr, _old_value, new_value in changes:
            presentation_manager.get_manager().speak_message(attr.get_change_description(new_value))

        return True

    def _on_text_deleted(self, event: Atspi.Event) -> bool:
        """Callback for object:text-changed:delete accessibility events."""

        if not AXUtilities.is_presentable_text_deletion(event):
            return True

        reason = AXUtilities.get_text_event_reason(event)
        if reason == TextEventReason.AUTO_DELETION_UNPRESENTABLE:
            msg = "DEFAULT: Ignoring event believed to be irrelevant auto deletion"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if reason == TextEventReason.SPIN_BUTTON_VALUE_CHANGE:
            msg = "DEFAULT: Ignoring deletion; spin button value is presented via value-changed"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        presentation_manager.get_manager().present_command_announcement()
        self.update_braille(event.source)

        if reason == TextEventReason.SELECTED_TEXT_DELETION:
            msg = "DEFAULT: Deletion is believed to be due to deleting selected text"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            presentation_manager.get_manager().present_message(messages.SELECTION_DELETED)
            AXUtilities.update_cached_selected_text(event.source)
            return True

        text = self.utilities.deleted_text(event)
        selected_text, _start, _end = AXUtilities.get_cached_selected_text(event.source)
        if reason == TextEventReason.DELETE:
            msg = "DEFAULT: Deletion is believed to be due to Delete command"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            text = AXText.get_character_at_offset(event.source)[0]
        elif reason == TextEventReason.BACKSPACE and text != selected_text:
            msg = "DEFAULT: Deletion is believed to be due to BackSpace command"
            debug.print_message(debug.LEVEL_INFO, msg, True)
        else:
            msg = "DEFAULT: Event is not being presented due to lack of cause"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if len(text) == 1:
            presentation_manager.get_manager().speak_character(text)
        else:
            presentation_manager.get_manager().speak_accessible_text(event.source, text)

        return True

    def _on_text_inserted(self, event: Atspi.Event) -> bool:
        """Callback for object:text-changed:insert accessibility events."""

        if not AXUtilities.is_presentable_text_insertion(event):
            return True

        reason = AXUtilities.get_text_event_reason(event)
        if reason == TextEventReason.AUTO_INSERTION_UNPRESENTABLE:
            msg = "DEFAULT: Ignoring event believed to be irrelevant auto insertion"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if reason == TextEventReason.SPIN_BUTTON_VALUE_CHANGE:
            msg = "DEFAULT: Ignoring insertion; spin button value is presented via value-changed"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        presentation_manager.get_manager().present_command_announcement()
        self.update_braille(event.source)

        if reason == TextEventReason.SELECTED_TEXT_RESTORATION:
            msg = "DEFAULT: Insertion is believed to be due to restoring selected text"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            presentation_manager.get_manager().present_message(messages.SELECTION_RESTORED)
            AXUtilities.update_cached_selected_text(event.source)
            return True

        if reason == TextEventReason.LIVE_REGION_UPDATE:
            msg = "DEFAULT: Event is from live region"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            live_region_presenter.get_presenter().handle_event(self, event)
            return True

        reason_messages: dict[TextEventReason, str] = {
            TextEventReason.PAGE_SWITCH: "due to page switch",
            TextEventReason.PASTE: "due to paste",
            TextEventReason.UNSPECIFIED_COMMAND: "due to command",
            TextEventReason.MOUSE_MIDDLE_BUTTON: "due to middle mouse button",
            TextEventReason.TYPING_ECHOABLE: "echoable",
            TextEventReason.AUTO_INSERTION_PRESENTABLE: "presentable auto text event",
            TextEventReason.SELECTED_TEXT_INSERTION: "also selected",
        }
        silent_reasons = {TextEventReason.PAGE_SWITCH, TextEventReason.PASTE}
        description = reason_messages.get(reason)
        if description is not None:
            msg = f"DEFAULT: Insertion is believed to be {description}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            speak_string = reason not in silent_reasons
        else:
            msg = "DEFAULT: Not speaking inserted string due to lack of cause"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            speak_string = False

        # Because some implementations are broken.
        text = self.utilities.inserted_text(event)
        if speak_string:
            if len(text) == 1:
                presentation_manager.get_manager().speak_character(text)
            else:
                presentation_manager.get_manager().speak_accessible_text(event.source, text)

        if len(text) != 1 or reason not in [
            TextEventReason.TYPING,
            TextEventReason.TYPING_ECHOABLE,
        ]:
            return True

        if AXText.get_selected_ranges(event.source):
            return True

        presenter = typing_echo_presenter.get_presenter()
        if presenter.echo_previous_sentence(event.source):
            return True

        presenter.echo_previous_word(event.source)
        return True

    def _on_text_selection_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:text-selection-changed accessibility events."""

        if AXUtilities.is_focusable(event.source) and not AXUtilities.is_focused(event.source):
            msg = "DEFAULT: Ignoring event from focusable but unfocused source"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        # We won't handle undo here as it can lead to double-presentation.
        # If there is an application for which text-changed events are
        # missing upon undo, handle them in an app or toolkit script.

        reason = AXUtilities.get_text_event_reason(event)
        if reason == TextEventReason.UNKNOWN:
            msg = "DEFAULT: Ignoring event because reason for change is unknown"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            AXUtilities.update_cached_selected_text(event.source)
            return True
        if reason == TextEventReason.SPIN_BUTTON_VALUE_CHANGE:
            msg = "DEFAULT: Ignoring selection; spin button value is presented via value-changed"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            AXUtilities.update_cached_selected_text(event.source)
            return True
        if reason == TextEventReason.SEARCH_PRESENTABLE:
            msg = "DEFAULT: Presenting line believed to be search match"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self.say_line(event.source, AXText.get_caret_offset(event.source))
            AXUtilities.update_cached_selected_text(event.source)
            return True
        if reason == TextEventReason.SEARCH_UNPRESENTABLE:
            msg = "DEFAULT: Ignoring event believed to be unpresentable search results change"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            AXUtilities.update_cached_selected_text(event.source)
            return True
        if reason in [TextEventReason.CUT, TextEventReason.BACKSPACE, TextEventReason.DELETE]:
            msg = "DEFAULT: Ignoring event believed to be text removal"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            AXUtilities.update_cached_selected_text(event.source)
            return True
        if reason == TextEventReason.AUTO_SELECTION:
            msg = "DEFAULT: Ignoring auto-selection believed to be side effect of typing"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            AXUtilities.update_cached_selected_text(event.source)
            return True
        if reason == TextEventReason.AUTO_UNSELECTION:
            msg = "DEFAULT: Ignoring auto-unselection believed to be side effect of typing"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            AXUtilities.update_cached_selected_text(event.source)
            return True

        self.utilities.handle_text_selection_change(event.source)
        self.update_braille(event.source)
        return True

    def _on_column_reordered(self, event: Atspi.Event) -> bool:
        """Callback for object:column-reordered accessibility events."""

        AXUtilities.clear_all_cache_now(event.source, "column-reordered event.")
        if not input_event_manager.get_manager().last_event_was_table_sort():
            return True

        if event.source != AXUtilities.get_table(focus_manager.get_manager().get_locus_of_focus()):
            return True

        presentation_manager.get_manager().present_message(messages.TABLE_REORDERED_COLUMNS)
        return True

    def _on_row_reordered(self, event: Atspi.Event) -> bool:
        """Callback for object:row-reordered accessibility events."""

        AXUtilities.clear_all_cache_now(event.source, "row-reordered event.")
        if not input_event_manager.get_manager().last_event_was_table_sort():
            return True

        if event.source != AXUtilities.get_table(focus_manager.get_manager().get_locus_of_focus()):
            return True

        presentation_manager.get_manager().present_message(messages.TABLE_REORDERED_ROWS)
        return True

    def _on_value_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:property-change:accessible-value accessibility events."""

        if not AXUtilities.is_presentable_value_change(event):
            return True

        manager = focus_manager.get_manager()
        if (
            not AXUtilities.is_progress_bar(event.source)
            and event.source != manager.get_locus_of_focus()
        ):
            msg = "DEFAULT: Source != locusOfFocus"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if AXUtilities.is_spin_button(event.source):
            manager.set_last_cursor_position(event.source, AXText.get_caret_offset(event.source))

        is_progress_bar = AXUtilities.is_progress_bar(event.source)
        if not is_progress_bar:
            presentation_manager.get_manager().interrupt_presentation()

        presentation_manager.get_manager().present_object(
            self,
            event.source,
            generate_sound=True,
            reason=(
                PresentationReason.PROGRESS_BAR_UPDATE
                if is_progress_bar
                else PresentationReason.STATE_CHANGE
            ),
        )
        return True

    def _on_window_activated(self, event: Atspi.Event) -> bool:
        """Callback for window:activate accessibility events."""

        if not AXUtilities.can_be_active_window(event.source):
            return True

        manager = focus_manager.get_manager()
        active_window = manager.get_active_window()
        if event.source == active_window:
            msg = "DEFAULT: Event is for active window."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            spellcheck_presenter.get_presenter().handle_window_event(event, self)
            return True

        manager.set_active_window(event.source)
        if AXUtilities.is_combo_box_popup(active_window):
            return True

        if AXObject.get_child_count(event.source) == 1:
            child = AXObject.get_child(event.source, 0)
            # Popup menus in Chromium live in a menu bar whose first child is a panel.
            if AXUtilities.is_menu_bar(child):
                child = AXUtilities.get_menu(child)
            if AXUtilities.is_menu(child):
                selected_item = AXSelection.get_selected_child(child, 0)
                if AXUtilities.is_selected(selected_item):
                    child = selected_item
                manager.set_locus_of_focus(event, child)
                return True

        if not spellcheck_presenter.get_presenter().handle_window_event(event, self):
            manager.set_locus_of_focus(event, event.source)
        return True

    def _on_window_deactivated(self, event: Atspi.Event) -> bool:
        """Callback for window:deactivate accessibility events."""

        manager = focus_manager.get_manager()
        focus = manager.get_locus_of_focus()
        if AXUtilities.is_menu_descendant(focus, inclusive=True):
            msg = "DEFAULT: Ignoring event. In menu."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if event.source != manager.get_active_window():
            msg = "DEFAULT: Ignoring event. Not for active window"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if AXUtilities.is_combo_box(focus) and AXUtilities.is_combo_box_popup(
            AXUtilities.find_active_window()
        ):
            msg = "DEFAULT: Ignoring event. Combo box popup is the new active window."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if AXUtilities.is_combo_box_popup(event.source):
            msg = "DEFAULT: Ignoring event. Combo box popup."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if learn_mode_presenter.get_presenter().is_active():
            learn_mode_presenter.get_presenter().quit()

        focus_manager.get_manager().clear_state("Window deactivated")
        script_manager.get_manager().set_active_script(None, "Window deactivated")
        return True

    ########################################################################
    #                                                                      #
    # Methods for presenting content                                       #
    #                                                                      #
    ########################################################################

    def _update_braille_caret_position(self, obj: Atspi.Accessible) -> None:
        """Try to reposition the cursor without having to do a full update."""

        if not braille_presenter.get_presenter().use_braille():
            return

        if braille.try_reposition_cursor(obj):
            return

        self.update_braille(obj)

    def _present_caret_moved_event(
        self,
        event: Atspi.Event,
        obj: Atspi.Accessible | None = None,
        reason: TextEventReason = TextEventReason.UNKNOWN,
    ) -> bool:
        """Presents text at the new position, based on heuristics. Returns True if handled."""

        obj = obj or event.source
        self._update_braille_caret_position(obj)

        # TODO - JD: Make this a TextEventReason. Also handle structural navigation
        # and table navigation here. Technically that's not been necessary because
        # it won't match anything below. But it would be cleaner to cover each cause
        # explicitly.
        if caret_navigator.get_navigator().last_input_event_was_navigation_command():
            msg = "DEFAULT: Event ignored: Last command was caret nav"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if reason == TextEventReason.SAY_ALL:
            msg = "DEFAULT: Not presenting text because SayAll is active"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        line_reasons = (
            TextEventReason.NAVIGATION_BY_LINE,
            TextEventReason.NAVIGATION_BY_PAGE,
            TextEventReason.NAVIGATION_TO_FILE_BOUNDARY,
        )
        if reason in line_reasons:
            self.say_line(obj, event.detail1)
            return True

        if reason == TextEventReason.NAVIGATION_BY_WORD:
            self.say_word(obj, event.detail1)
            return True

        character_reasons = (
            TextEventReason.NAVIGATION_BY_CHARACTER,
            TextEventReason.NAVIGATION_TO_LINE_BOUNDARY,
        )
        if reason in character_reasons:
            self.say_character(obj, event.detail1)
            return True

        if reason == TextEventReason.MOUSE_PRIMARY_BUTTON:
            text, _start, _end = AXUtilities.get_cached_selected_text(event.source)
            if not text:
                self.say_line(obj, event.detail1)
                return True
        return False

    def say_character(self, obj: Atspi.Accessible, offset: int) -> None:
        """Speak the character at the specified offset."""

        if input_event_manager.get_manager().last_event_was_forward_caret_selection():
            offset -= 1

        character, start_offset, end_offset = AXText.get_character_at_offset(obj, offset)
        focus_manager.get_manager().emit_region_changed(
            obj,
            start_offset,
            end_offset,
            focus_manager.CARET_TRACKING,
        )

        presentation_manager.get_manager().speak_character_at_offset(obj, offset, character)
        AXUtilities.set_last_text_unit_spoken(TextUnit.CHAR)

    def say_line(self, obj: Atspi.Accessible, offset: int) -> None:
        """Speaks the line at the specified offset."""

        line, start_offset = AXText.get_line_at_offset(obj, offset)[0:2]
        if line and line != "\n":
            end_offset = start_offset + len(line)
            focus_manager.get_manager().emit_region_changed(
                obj,
                start_offset,
                end_offset,
                focus_manager.CARET_TRACKING,
            )

        speech_presenter.get_presenter().speak_line(
            self,
            obj,
            start_offset,
            start_offset + len(line),
            line,
        )

        AXUtilities.set_last_text_unit_spoken(TextUnit.LINE)

    def say_phrase(self, obj: Atspi.Accessible, start_offset: int, end_offset: int) -> None:
        """Speaks the substring between start and end offset."""

        phrase = self.utilities.expand_eocs(obj, start_offset, end_offset)
        if not phrase:
            return

        if len(phrase) > 1 or phrase.isalnum():
            focus_manager.get_manager().emit_region_changed(
                obj,
                start_offset,
                end_offset,
                focus_manager.CARET_TRACKING,
            )

        speech_presenter.get_presenter().speak_phrase(self, obj, start_offset, end_offset, phrase)
        AXUtilities.set_last_text_unit_spoken(TextUnit.PHRASE)

    def say_word(self, obj: Atspi.Accessible, offset: int) -> None:
        """Speaks the word at the specified offset, taking into account the previous position."""

        word, start_offset, end_offset = self.utilities.get_word_at_offset_adjusted_for_navigation(
            obj,
            offset,
        )

        speech_pres = speech_presenter.get_presenter()
        if "\n" in word:
            # Announce when we cross a hard line boundary, based on whether or not indentation
            # should be spoken. This was done to avoid yet another setting in response to some
            # users saying this announcement was too chatty. The idea of using this setting for
            # the decision is that if the user wants indentation announced, they are interested
            # in explicit whitespace information.
            if speech_pres.get_speak_indentation():
                presentation_manager.get_manager().speak_character("\n")
            if word.startswith("\n"):
                start_offset += 1
            elif word.endswith("\n"):
                end_offset -= 1
            word = AXText.get_substring(obj, start_offset, end_offset)

        # say_phrase is useful because it handles punctuation verbalization, but we don't want
        # to trigger its whitespace presentation.
        matches = list(re.finditer(r"\S+", word))
        if matches:
            start_offset += matches[0].start()
            end_offset -= len(word) - matches[-1].end()
            word = AXText.get_substring(obj, start_offset, end_offset)

        text = word.replace("\n", "\\n")
        msg = f"DEFAULT: Final word at offset {offset} is '{text}' ({start_offset}-{end_offset})"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        speech_presenter.get_presenter().present_text_attribute_state(obj, start_offset)
        self.say_phrase(obj, start_offset, end_offset)
        AXUtilities.set_last_text_unit_spoken(TextUnit.WORD)

    def present_object(
        self,
        obj: Atspi.Accessible,
        offset: int | None = None,
        prior_obj: Atspi.Accessible | None = None,
        generate_speech: bool = True,
        generate_braille: bool = True,
        reason: PresentationReason | None = None,
    ) -> None:
        """Presents the current object."""

        tokens = ["DEFAULT: Presenting object", obj]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if offset is not None:
            AXUtilities.set_caret_offset_with_reason(
                obj, offset, CaretSetReason.OBJECT_PRESENTATION
            )

        presentation_manager.get_manager().present_object(
            self,
            obj,
            generate_speech=generate_speech,
            generate_braille=generate_braille,
            prior_obj=prior_obj,
            reason=reason,
        )
