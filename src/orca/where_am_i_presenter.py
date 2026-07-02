# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
# Copyright 2016-2023 Igalia, S.L.
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

"""Module for commands related to the current accessible object."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, Gtk  # pylint: disable=no-name-in-module

from . import (
    dbus_service,
    debug,
    flat_review_presenter,
    focus_manager,
    guilabels,
    input_event,
    math_navigator,
    math_presenter,
    messages,
    presentation_manager,
    speech_presenter,
    spellcheck_presenter,
    text_attribute_manager,
    where_am_i_presenter_command_definitions,
)
from .ax_component import AXComponent
from .ax_object import AXObject
from .ax_text import AXText, AXTextAttribute
from .ax_utilities import AXUtilities
from .extension import Extension
from .generator import PresentationReason

if TYPE_CHECKING:
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

    from .command import Command
    from .scripts import default


class WhereAmIPresenter(Extension):
    """Module for commands related to the current accessible object."""

    GROUP_LABEL = guilabels.KB_GROUP_WHERE_AM_I

    def __init__(self) -> None:
        super().__init__()
        self._char_attributes_gui: CharacterAttributesGUI | None = None

    def _get_commands(self) -> list[Command]:
        return where_am_i_presenter_command_definitions.get_commands(self)

    def _get_current_character_info(self, script: default.Script) -> tuple[dict[str, str], str]:
        """Returns the text attributes and string for the current character."""

        reviewer = flat_review_presenter.get_presenter()
        if reviewer.is_active():
            context = reviewer.get_or_create_context(script)
            obj = context.get_current_object()
            offset = context.get_current_text_offset()
        else:
            obj = focus_manager.get_manager().get_locus_of_focus()
            offset = None

        attrs = AXText.get_text_attributes_at_offset(obj, offset)[0]
        char = AXText.get_character_at_offset(obj, offset)[0]
        return attrs, char

    def _localize_text_attribute(self, key: str, value: str | None) -> str:
        """Returns a localized description of the text attribute for Orca+F readout."""

        if value is None:
            return ""

        if key == "weight" and (value == "bold" or int(value) > 400):
            return messages.BOLD

        if key.endswith("spelling") or value == "spelling":
            return messages.MISSPELLED

        ax_text_attribute = AXTextAttribute.from_string(key)
        if ax_text_attribute is None:
            return ""

        localized_key = ax_text_attribute.get_localized_name()
        localized_value = ax_text_attribute.get_localized_value(value)
        return f"{localized_key}: {localized_value}"

    def _get_all_available_text_attributes(self, attrs: dict[str, str]) -> list[str]:
        """Returns localized descriptions of all available text attributes."""

        result = []
        seen = set()
        for key, value in attrs.items():
            ax_text_attribute = AXTextAttribute.from_string(key)
            sort_key = ax_text_attribute.get_localized_name() if ax_text_attribute else key
            canonical_key = ax_text_attribute.get_attribute_name() if ax_text_attribute else key

            if canonical_key in seen or value is None:
                continue

            if ax_text_attribute is not None:
                localized_key = ax_text_attribute.get_localized_name()
                localized_value = ax_text_attribute.get_localized_value(value)
                description = f"{localized_key}: {localized_value}"
            else:
                description = f"{key}: {value}"

            result.append((sort_key.casefold(), description))
            seen.add(canonical_key)

        return [description for _sort_key, description in sorted(result)]

    def _get_character_formatting_text(self, attrs: dict[str, str]) -> str:
        """Returns text for the character-formatting window."""

        return "\n".join(self._get_all_available_text_attributes(attrs))

    @dbus_service.command
    def present_character_attributes(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Presents the font and formatting details for the current character."""

        tokens = [
            "WHERE AM I PRESENTER: present_character_attributes. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        attrs, _char = self._get_current_character_info(script)
        attr_list = text_attribute_manager.get_manager().get_resolved_attributes_to_speak()
        presented = False

        for ax_text_attr in attr_list:
            key = ax_text_attr.get_attribute_name()
            value = ax_text_attr.get_value_from_attrs(attrs)
            if not ax_text_attr.value_is_default(value):
                presentation_manager.get_manager().present_message(
                    self._localize_text_attribute(key, value),
                )
                presented = True

        if not presented:
            msg = (
                messages.CHARACTER_FORMATTING_DEFAULT
                if attrs
                else messages.CHARACTER_FORMATTING_NOT_AVAILABLE
            )
            presentation_manager.get_manager().present_message(
                msg,
            )

        return True

    @dbus_service.command
    def show_character_attributes(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Shows the font and formatting details for the current character."""

        tokens = [
            "WHERE AM I PRESENTER: show_character_attributes. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        attrs, char = self._get_current_character_info(script)
        descriptions = self._get_all_available_text_attributes(attrs)
        if not descriptions:
            presentation_manager.get_manager().present_message(
                messages.CHARACTER_FORMATTING_NOT_AVAILABLE,
            )
            return True

        title = guilabels.CHARACTER_FORMATTING
        if char:
            title = guilabels.CHARACTER_FORMATTING_FOR % char
        text = self._get_character_formatting_text(attrs)
        self._char_attributes_gui = CharacterAttributesGUI(title, text)
        self._char_attributes_gui.show_gui()

        return True

    @dbus_service.command
    def present_size_and_position(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Presents the size and position of the current object."""

        tokens = [
            "WHERE AM I PRESENTER: present_size_and_position. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if flat_review_presenter.get_presenter().is_active():
            obj = flat_review_presenter.get_presenter().get_current_object(script, event)
        else:
            obj = focus_manager.get_manager().get_locus_of_focus()

        rect = AXComponent.get_rect(obj)
        if AXUtilities.is_empty_rect(rect):
            full = messages.LOCATION_NOT_FOUND_FULL
            brief = messages.LOCATION_NOT_FOUND_BRIEF
            presentation_manager.get_manager().present_message(full, brief)
            return True

        full = messages.SIZE_AND_POSITION_FULL % (rect.width, rect.height, rect.x, rect.y)
        brief = messages.SIZE_AND_POSITION_BRIEF % (rect.width, rect.height, rect.x, rect.y)
        presentation_manager.get_manager().present_message(full, brief)
        return True

    @dbus_service.command
    def present_title(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Presents the title of the current window."""

        tokens = [
            "WHERE AM I PRESENTER: present_title. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        obj = focus_manager.get_manager().get_locus_of_focus()
        if AXObject.is_dead(obj):
            obj = focus_manager.get_manager().get_active_window()

        if obj is None or AXObject.is_dead(obj):
            presentation_manager.get_manager().present_message(messages.LOCATION_NOT_FOUND_FULL)
            return True

        presentation_manager.get_manager().present_window_title(script, obj)
        return True

    @dbus_service.command
    def present_default_button(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        dialog: Atspi.Accessible | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Presents the default button of the current dialog."""

        tokens = [
            "WHERE AM I PRESENTER: present_default_button. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        obj = focus_manager.get_manager().get_locus_of_focus()
        if dialog is None:
            _frame, dialog = script.utilities.frame_and_dialog(obj)
        if dialog is None:
            if notify_user:
                presentation_manager.get_manager().present_message(messages.DIALOG_NOT_IN_A)
            return True

        button = AXUtilities.get_default_button(dialog)
        if button is None:
            if notify_user:
                presentation_manager.get_manager().present_message(
                    messages.DEFAULT_BUTTON_NOT_FOUND,
                )
            return True

        name = AXObject.get_name(button)
        if not AXUtilities.is_sensitive(button):
            presentation_manager.get_manager().present_message(
                messages.DEFAULT_BUTTON_IS_GRAYED % name,
            )
            return True

        presentation_manager.get_manager().present_message(messages.DEFAULT_BUTTON_IS % name)
        return True

    @dbus_service.command
    def present_cell_formula(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Presents the formula associated with the current spreadsheet cell."""

        tokens = [
            "WHERE AM I PRESENTER: present_cell_formula. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        focus = focus_manager.get_manager().get_locus_of_focus()
        cell = AXUtilities.find_ancestor_inclusive(focus, AXUtilities.is_table_cell)
        if cell is None:
            if notify_user:
                presentation_manager.get_manager().present_message(messages.TABLE_NOT_IN_A)
            return True

        text = AXUtilities.get_cell_formula(cell)
        if not text:
            text = AXText.get_all_text(cell) or AXText.get_all_text(focus) or messages.EMPTY
        if notify_user:
            presentation_manager.get_manager().present_message(text)

        return True

    @dbus_service.command
    def present_status_bar(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Presents the status bar and info bar of the current window."""

        tokens = [
            "WHERE AM I PRESENTER: present_status_bar. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        obj = focus_manager.get_manager().get_locus_of_focus()
        frame, _dialog = script.utilities.frame_and_dialog(obj)
        if frame:
            statusbar = AXUtilities.get_status_bar(frame)
            if statusbar:
                presentation_manager.get_manager().interrupt_if_needed_for_object_presentation()
                script.present_object(statusbar)
            else:
                full = messages.STATUS_BAR_NOT_FOUND_FULL
                brief = messages.STATUS_BAR_NOT_FOUND_BRIEF
                presentation_manager.get_manager().present_message(full, brief)

            infobar = AXUtilities.get_info_bar(frame)
            if infobar and AXUtilities.is_showing_and_visible(infobar):
                script.present_object(infobar)

        return True

    @dbus_service.command
    def present_link(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Presents details about the current link."""

        tokens = [
            "WHERE AM I PRESENTER: present_link. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        link = focus_manager.get_manager().get_locus_of_focus()
        if not script.utilities.is_link(link):
            if notify_user:
                presentation_manager.get_manager().present_message(messages.NOT_ON_A_LINK)
            return True

        return self._do_where_am_i(script, True, link)

    def _get_all_selected_text(self, script: default.Script, obj: Atspi.Accessible) -> str:
        """Returns the selected text of obj plus any adjacent text objects."""

        string = AXUtilities.get_selected_text(obj)[0]
        if AXUtilities.is_spreadsheet_cell(obj):
            return string

        prev_obj = script.utilities.find_previous_object(obj)
        while prev_obj:
            selection = AXUtilities.get_selected_text(prev_obj)[0]
            if not selection:
                break
            string = f"{selection} {string}"
            prev_obj = script.utilities.find_previous_object(prev_obj)

        next_obj = script.utilities.find_next_object(obj)
        while next_obj:
            selection = AXUtilities.get_selected_text(next_obj)[0]
            if not selection:
                break
            string = f"{string} {selection}"
            next_obj = script.utilities.find_next_object(next_obj)

        return string

    @dbus_service.command
    def present_selected_text(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Presents the selected text."""

        tokens = [
            "WHERE AM I PRESENTER: present_selected_text. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        obj = focus_manager.get_manager().get_locus_of_focus()
        if obj is None:
            presentation_manager.get_manager().speak_message(messages.LOCATION_NOT_FOUND_FULL)
            return True

        text = self._get_all_selected_text(script, obj)
        if not text:
            presentation_manager.get_manager().speak_message(messages.NO_SELECTED_TEXT)
            return True

        manager = speech_presenter.get_presenter()
        indentation = manager.get_indentation_description(text, only_if_changed=False)
        text = manager.adjust_for_presentation(obj, text)
        msg = messages.SELECTED_TEXT_IS % f"{indentation} {text}"
        presentation_manager.get_manager().speak_message(msg)
        return True

    @dbus_service.command
    def present_selection(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Presents the selected text or selected objects."""

        tokens = [
            "WHERE AM I PRESENTER: present_selection. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        obj = focus_manager.get_manager().get_locus_of_focus()
        if obj is None:
            if not script.utilities.is_link(obj):
                presentation_manager.get_manager().speak_message(messages.LOCATION_NOT_FOUND_FULL)
            return True

        tokens = ["WHERE AM I PRESENTER: presenting selection for", obj]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        spreadsheet = AXUtilities.find_ancestor(obj, AXUtilities.is_spreadsheet_table)
        if spreadsheet is not None and script.utilities.speak_selected_cell_range(spreadsheet):
            return True

        container = AXUtilities.get_selection_container(obj)
        if container is None:
            tokens = ["WHERE AM I PRESENTER: Selection container not found for", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return self.present_selected_text(script, event, obj)

        selected_count = AXUtilities.selected_child_count(container)
        child_count = AXUtilities.selectable_child_count(container)
        presentation_manager.get_manager().present_message(
            messages.selected_items_count(selected_count, child_count),
        )
        if not selected_count:
            return True

        selected_items = AXUtilities.selected_children(container)
        item_names = ",".join(map(AXObject.get_name, selected_items))
        presentation_manager.get_manager().speak_message(item_names)
        return True

    def _do_where_am_i(
        self,
        script: default.Script,
        basic_only: bool = True,
        obj: Atspi.Accessible | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Presents details about the current location at the specified level."""

        presenter = spellcheck_presenter.get_presenter()
        if presenter.is_active():
            presenter.present_error_details(not basic_only, script)

        if math_navigator.get_navigator().is_active():
            if basic_only:
                speech = math_presenter.get_presenter().get_where_am_i()
            else:
                speech = math_presenter.get_presenter().get_where_am_i_all()
            if speech:
                presentation_manager.get_manager().present_message(speech)
            return True

        if obj is None:
            obj = focus_manager.get_manager().get_locus_of_focus()
        if AXObject.is_dead(obj):
            obj = focus_manager.get_manager().get_active_window()

        if obj is None or AXObject.is_dead(obj):
            if notify_user:
                presentation_manager.get_manager().present_message(messages.LOCATION_NOT_FOUND_FULL)
            return True

        if basic_only:
            reason = PresentationReason.WHERE_AM_I_BASIC
        else:
            reason = PresentationReason.WHERE_AM_I_DETAILED

        def real_object(acc: Atspi.Accessible) -> Atspi.Accessible:
            if AXUtilities.is_focused(acc):
                return acc

            def pred(x):
                return AXUtilities.is_table_cell_or_header(x) or AXUtilities.is_list_item(x)

            ancestor = AXUtilities.find_ancestor(acc, pred)
            if ancestor is not None and not AXUtilities.is_layout_only(
                AXObject.get_parent(ancestor),
            ):
                acc = ancestor

            return acc

        script.present_object(
            real_object(obj),
            reason=reason,
        )

        return True

    @dbus_service.command
    def where_am_i_basic(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Presents basic information about the current location."""

        tokens = [
            "WHERE AM I PRESENTER: where_am_i_basic. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return self._do_where_am_i(script, notify_user=notify_user)

    @dbus_service.command
    def where_am_i_detailed(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Presents detailed information about the current location."""

        tokens = [
            "WHERE AM I PRESENTER: where_am_i_detailed. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        # TODO - JD: For some reason, we are starting the basic where am I
        # in response to the first click. Then we do the detailed one in
        # response to the second click. Until that's fixed, interrupt the
        # first one.
        presentation_manager.get_manager().interrupt_presentation()
        return self._do_where_am_i(script, False, notify_user=notify_user)


class CharacterAttributesGUI:
    """Presents character attributes in a text view."""

    def __init__(self, title: str, text: str) -> None:
        self._gui: Gtk.Dialog = self._create_dialog(title, text)

    def _create_dialog(self, title: str, text: str) -> Gtk.Dialog:
        """Creates the dialog."""

        dialog = Gtk.Dialog(
            title,
            None,
            Gtk.DialogFlags.MODAL,
            (Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE),
        )
        dialog.set_default_size(600, 400)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)

        textbuffer = Gtk.TextBuffer()
        textbuffer.set_text(text)
        textbuffer.place_cursor(textbuffer.get_start_iter())

        textview = Gtk.TextView(buffer=textbuffer)
        textview.set_editable(False)
        textview.set_cursor_visible(True)
        textview.set_wrap_mode(Gtk.WrapMode.WORD)
        scrolled_window.add(textview)  # pylint: disable=no-member
        dialog.get_content_area().pack_start(scrolled_window, True, True, 0)
        dialog.set_focus(textview)
        dialog.connect("response", self.on_response)
        dialog.connect("key-press-event", self.on_key_press)
        return dialog

    def on_response(self, _dialog: Gtk.Dialog, response: Gtk.ResponseType) -> None:
        """Handler for the 'response' signal of the dialog."""

        if response == Gtk.ResponseType.CLOSE:
            self._gui.destroy()

    def on_key_press(self, _dialog: Gtk.Dialog, event: Gdk.EventKey) -> bool:
        """Handler for the 'key-press-event' signal of the dialog."""

        if event.keyval == Gdk.KEY_Escape:
            self._gui.destroy()
            return True
        return False

    def show_gui(self) -> None:
        """Shows the dialog."""

        self._gui.show_all()  # pylint: disable=no-member
        self._gui.present_with_time(time.time())


_presenter = WhereAmIPresenter()


def get_presenter() -> WhereAmIPresenter:
    """Returns the Where Am I Presenter"""

    return _presenter
