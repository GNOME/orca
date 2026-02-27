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

from typing import TYPE_CHECKING

from . import (
    cmdnames,
    command_manager,
    dbus_service,
    debug,
    flat_review_presenter,
    focus_manager,
    guilabels,
    input_event,
    keybindings,
    messages,
    presentation_manager,
    speech_presenter,
    spellcheck_presenter,
    text_attribute_manager,
)
from .ax_component import AXComponent
from .ax_object import AXObject
from .ax_text import AXText, AXTextAttribute
from .ax_utilities import AXUtilities

if TYPE_CHECKING:
    import gi

    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

    from .scripts import default


class WhereAmIPresenter:
    """Module for commands related to the current accessible object."""

    def __init__(self) -> None:
        self._initialized: bool = False

        msg = "WHERE AM I PRESENTER: Registering D-Bus commands."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        controller = dbus_service.get_remote_controller()
        controller.register_decorated_module("WhereAmIPresenter", self)

    # pylint: disable-next=too-many-locals
    def set_up_commands(self) -> None:
        """Sets up commands with CommandManager."""

        if self._initialized:
            return
        self._initialized = True

        manager = command_manager.get_manager()
        group_label = guilabels.KB_GROUP_WHERE_AM_I

        # Common keybindings (same for desktop and laptop)
        kb_f = keybindings.KeyBinding("f", keybindings.ORCA_MODIFIER_MASK)
        kb_e = keybindings.KeyBinding("e", keybindings.ORCA_MODIFIER_MASK)
        kb_up = keybindings.KeyBinding("Up", keybindings.ORCA_SHIFT_MODIFIER_MASK)

        # Desktop-specific keybindings
        kb_equal = keybindings.KeyBinding("equal", keybindings.ORCA_MODIFIER_MASK)
        kb_kp_enter_orca = keybindings.KeyBinding("KP_Enter", keybindings.ORCA_MODIFIER_MASK)
        kb_kp_enter_orca_2 = keybindings.KeyBinding(
            "KP_Enter",
            keybindings.ORCA_MODIFIER_MASK,
            click_count=2,
        )
        kb_kp_enter = keybindings.KeyBinding("KP_Enter", keybindings.NO_MODIFIER_MASK)
        kb_kp_enter_2 = keybindings.KeyBinding(
            "KP_Enter",
            keybindings.NO_MODIFIER_MASK,
            click_count=2,
        )

        # Laptop-specific keybindings
        kb_slash = keybindings.KeyBinding("slash", keybindings.ORCA_MODIFIER_MASK)
        kb_slash_2 = keybindings.KeyBinding("slash", keybindings.ORCA_MODIFIER_MASK, click_count=2)
        kb_return = keybindings.KeyBinding("Return", keybindings.ORCA_MODIFIER_MASK)
        kb_return_2 = keybindings.KeyBinding(
            "Return",
            keybindings.ORCA_MODIFIER_MASK,
            click_count=2,
        )

        # (name, function, description, desktop_kb, laptop_kb)
        commands_data = [
            (
                "readCharAttributesHandler",
                self.present_character_attributes,
                cmdnames.READ_CHAR_ATTRIBUTES,
                kb_f,
                kb_f,
            ),
            (
                "presentSizeAndPositionHandler",
                self.present_size_and_position,
                cmdnames.PRESENT_SIZE_AND_POSITION,
                None,
                None,
            ),
            (
                "getTitleHandler",
                self.present_title,
                cmdnames.PRESENT_TITLE,
                kb_kp_enter_orca,
                kb_slash,
            ),
            (
                "getStatusBarHandler",
                self.present_status_bar,
                cmdnames.PRESENT_STATUS_BAR,
                kb_kp_enter_orca_2,
                kb_slash_2,
            ),
            (
                "present_default_button",
                self.present_default_button,
                cmdnames.PRESENT_DEFAULT_BUTTON,
                kb_e,
                kb_e,
            ),
            (
                "present_cell_formula",
                self.present_cell_formula,
                cmdnames.PRESENT_CELL_FORMULA,
                kb_equal,
                None,
            ),
            (
                "whereAmIBasicHandler",
                self.where_am_i_basic,
                cmdnames.WHERE_AM_I_BASIC,
                kb_kp_enter,
                kb_return,
            ),
            (
                "whereAmIDetailedHandler",
                self.where_am_i_detailed,
                cmdnames.WHERE_AM_I_DETAILED,
                kb_kp_enter_2,
                kb_return_2,
            ),
            ("whereAmILinkHandler", self.present_link, cmdnames.WHERE_AM_I_LINK, None, None),
            (
                "whereAmISelectionHandler",
                self.present_selection,
                cmdnames.WHERE_AM_I_SELECTION,
                kb_up,
                kb_up,
            ),
        ]

        for name, function, description, desktop_kb, laptop_kb in commands_data:
            manager.add_command(
                command_manager.KeyboardCommand(
                    name,
                    function,
                    group_label,
                    description,
                    desktop_keybinding=desktop_kb,
                    laptop_keybinding=laptop_kb,
                ),
            )

        msg = "WHERE AM I PRESENTER: Commands set up."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def _localize_text_attribute(self, key, value):
        if value is None:
            return ""

        if key == "weight" and (value == "bold" or int(value) > 400):
            return messages.BOLD

        if key.endswith("spelling") or value == "spelling":
            return messages.MISSPELLED

        ax_text_attribute = AXTextAttribute.from_string(key)
        localized_key = ax_text_attribute.get_localized_name()
        localized_value = ax_text_attribute.get_localized_value(value)
        return f"{localized_key}: {localized_value}"

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

        focus = focus_manager.get_manager().get_locus_of_focus()
        attrs = AXText.get_text_attributes_at_offset(focus)[0]

        # Get a dictionary of text attributes that the user cares about, falling back on the
        # default presentable attributes if the user has not specified any.
        attr_list = list(
            filter(
                None,
                map(
                    AXTextAttribute.from_string,
                    text_attribute_manager.get_manager().get_attributes_to_speak(),
                ),
            ),
        )
        if not attr_list:
            attr_list = AXUtilities.get_all_supported_text_attributes()

        for ax_text_attr in attr_list:
            key = ax_text_attr.get_attribute_name()
            value = attrs.get(key)
            if not ax_text_attr.value_is_default(value):
                presentation_manager.get_manager().speak_message(
                    self._localize_text_attribute(key, value),
                )

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
        if AXComponent.is_empty_rect(rect):
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
        cell = AXObject.find_ancestor_inclusive(focus, AXUtilities.is_table_cell)
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
                script.present_object(statusbar, interrupt=True)
            else:
                full = messages.STATUS_BAR_NOT_FOUND_FULL
                brief = messages.STATUS_BAR_NOT_FOUND_BRIEF
                presentation_manager.get_manager().present_message(full, brief)

            infobar = AXUtilities.get_info_bar(frame)
            if infobar and AXUtilities.is_showing(infobar) and AXUtilities.is_visible(infobar):
                script.present_object(infobar, interrupt=statusbar is None)

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

        spreadsheet = AXObject.find_ancestor(obj, AXUtilities.is_spreadsheet_table)
        if spreadsheet is not None and script.utilities.speak_selected_cell_range(spreadsheet):
            return True

        container = script.utilities.get_selection_container(obj)
        if container is None:
            tokens = ["WHERE AM I PRESENTER: Selection container not found for", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return self.present_selected_text(script, event, obj)

        selected_count = script.utilities.selected_child_count(container)
        child_count = script.utilities.selectable_child_count(container)
        presentation_manager.get_manager().present_message(
            messages.selected_items_count(selected_count, child_count),
        )
        if not selected_count:
            return True

        selected_items = script.utilities.selected_children(container)
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

        if obj is None:
            obj = focus_manager.get_manager().get_locus_of_focus()
        if AXObject.is_dead(obj):
            obj = focus_manager.get_manager().get_active_window()

        if obj is None or AXObject.is_dead(obj):
            if notify_user:
                presentation_manager.get_manager().present_message(messages.LOCATION_NOT_FOUND_FULL)
            return True

        if basic_only:
            format_type = "basicWhereAmI"
        else:
            format_type = "detailedWhereAmI"

        def real_object(acc: Atspi.Accessible) -> Atspi.Accessible:
            if AXUtilities.is_focused(acc):
                return acc

            def pred(x):
                return AXUtilities.is_table_cell_or_header(x) or AXUtilities.is_list_item(x)

            ancestor = AXObject.find_ancestor(acc, pred)
            if ancestor is not None and not AXUtilities.is_layout_only(
                AXObject.get_parent(ancestor),
            ):
                acc = ancestor

            return acc

        script.present_object(
            real_object(obj),
            alreadyFocused=True,
            formatType=format_type,
            forceMnemonic=True,
            forceList=True,
            forceTutorial=True,
            speechOnly=True,
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


_presenter = WhereAmIPresenter()


def get_presenter() -> WhereAmIPresenter:
    """Returns the Where Am I Presenter"""

    return _presenter
