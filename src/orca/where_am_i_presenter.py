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

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc." \
                "Copyright (c) 2016-2023 Igalia, S.L."
__license__   = "LGPL"

from typing import TYPE_CHECKING

from . import cmdnames
from . import dbus_service
from . import debug
from . import focus_manager
from . import input_event
from . import keybindings
from . import messages
from . import settings_manager
from . import speech_and_verbosity_manager
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
        self._handlers: dict[str, input_event.InputEventHandler] = self.get_handlers(True)
        self._desktop_bindings: keybindings.KeyBindings = keybindings.KeyBindings()
        self._laptop_bindings: keybindings.KeyBindings = keybindings.KeyBindings()

        msg = "WhereAmIPresenter: Registering D-Bus commands."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        controller = dbus_service.get_remote_controller()
        controller.register_decorated_module("WhereAmIPresenter", self)

    def get_bindings(
        self, refresh: bool = False, is_desktop: bool = True
    ) -> keybindings.KeyBindings:
        """Returns the where-am-i-presenter keybindings."""

        if refresh:
            msg = "WHERE AM I PRESENTER: Refreshing bindings."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._desktop_bindings.remove_key_grabs("WHERE AM I PRESENTER: Refreshing bindings.")
            self._laptop_bindings.remove_key_grabs("WHERE AM I PRESENTER: Refreshing bindings.")
            self._setup_bindings()
        elif is_desktop and self._desktop_bindings.is_empty():
            self._setup_bindings()
        elif not is_desktop and self._laptop_bindings.is_empty():
            self._setup_bindings()

        if is_desktop:
            return self._desktop_bindings
        return self._laptop_bindings

    def get_handlers(self, refresh: bool = False) -> dict[str, input_event.InputEventHandler]:
        """Returns the where-am-i-presenter handlers."""

        if refresh:
            msg = "WHERE AM I PRESENTER: Refreshing handlers."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._setup_handlers()

        return self._handlers

    def _setup_bindings(self) -> None:
        """Sets up the where-am-i-presenter key bindings."""

        self._setup_desktop_bindings()
        self._setup_laptop_bindings()

    def _setup_handlers(self) -> None:
        """Sets up the where-am-i-presenter input event handlers."""

        self._handlers = {}

        self._handlers["readCharAttributesHandler"] = \
            input_event.InputEventHandler(
                self.present_character_attributes,
                cmdnames.READ_CHAR_ATTRIBUTES)

        self._handlers["presentSizeAndPositionHandler"] = \
            input_event.InputEventHandler(
                self.present_size_and_position,
                cmdnames.PRESENT_SIZE_AND_POSITION)

        self._handlers["getTitleHandler"] = \
            input_event.InputEventHandler(
                self.present_title,
                cmdnames.PRESENT_TITLE)

        self._handlers["getStatusBarHandler"] = \
            input_event.InputEventHandler(
                self.present_status_bar,
                cmdnames.PRESENT_STATUS_BAR)

        self._handlers["present_default_button"] = \
            input_event.InputEventHandler(
                self.present_default_button,
                cmdnames.PRESENT_DEFAULT_BUTTON)

        self._handlers["whereAmIBasicHandler"] = \
            input_event.InputEventHandler(
                self.where_am_i_basic,
                cmdnames.WHERE_AM_I_BASIC)

        self._handlers["whereAmIDetailedHandler"] = \
            input_event.InputEventHandler(
                self.where_am_i_detailed,
                cmdnames.WHERE_AM_I_DETAILED)

        self._handlers["whereAmILinkHandler"] = \
            input_event.InputEventHandler(
                self.present_link,
                cmdnames.WHERE_AM_I_LINK)

        self._handlers["whereAmISelectionHandler"] = \
            input_event.InputEventHandler(
                self.present_selection,
                cmdnames.WHERE_AM_I_SELECTION)

        msg = "WHERE AM I PRESENTER: Handlers set up."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def _setup_desktop_bindings(self) -> None:
        """Sets up the where-am-i-presenter desktop key bindings."""

        self._desktop_bindings = keybindings.KeyBindings()

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "f",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers["readCharAttributesHandler"]))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "e",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers["present_default_button"]))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["presentSizeAndPositionHandler"]))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Enter",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers["getTitleHandler"],
                1))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Enter",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers["getStatusBarHandler"],
                2))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Enter",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["whereAmIBasicHandler"],
                1))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Enter",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["whereAmIDetailedHandler"],
                2))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["whereAmILinkHandler"]))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "Up",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_SHIFT_MODIFIER_MASK,
                self._handlers["whereAmISelectionHandler"]))

        msg = "WHERE AM I PRESENTER: Desktop bindings set up."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def _setup_laptop_bindings(self) -> None:
        """Sets up the where-am-i-presenter laptop key bindings."""

        self._laptop_bindings = keybindings.KeyBindings()

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "f",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers["readCharAttributesHandler"]))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "e",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers["present_default_button"]))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["presentSizeAndPositionHandler"]))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "slash",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers["getTitleHandler"],
                1))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "slash",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers["getStatusBarHandler"],
                2))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "Return",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers["whereAmIBasicHandler"],
                1))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "Return",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers["whereAmIDetailedHandler"],
                2))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["whereAmILinkHandler"]))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "Up",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_SHIFT_MODIFIER_MASK,
                self._handlers["whereAmISelectionHandler"]))

        msg = "WHERE AM I PRESENTER: Laptop bindings set up."
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
        notify_user: bool = True
    ) -> bool:
        """Presents the font and formatting details for the current character."""

        tokens = ["WHERE AM I PRESENTER: present_character_attributes. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        focus = focus_manager.get_manager().get_locus_of_focus()
        attrs = AXText.get_text_attributes_at_offset(focus)[0]

        # Get a dictionary of text attributes that the user cares about, falling back on the
        # default presentable attributes if the user has not specified any.
        attr_list = list(filter(None, map(
            AXTextAttribute.from_string,
            settings_manager.get_manager().get_setting("textAttributesToSpeak"))))
        if not attr_list:
            attr_list = AXText.get_all_supported_text_attributes()

        for ax_text_attr in attr_list:
            key = ax_text_attr.get_attribute_name()
            value = attrs.get(key)
            if not ax_text_attr.value_is_default(value):
                script.speak_message(self._localize_text_attribute(key, value))

        return True

    @dbus_service.command
    def present_size_and_position(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Presents the size and position of the current object."""

        tokens = ["WHERE AM I PRESENTER: present_size_and_position. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if script.get_flat_review_presenter().is_active():
            obj = script.get_flat_review_presenter().get_current_object(script, event)
        else:
            obj = focus_manager.get_manager().get_locus_of_focus()

        rect = AXComponent.get_rect(obj)
        if AXComponent.is_empty_rect(rect):
            full = messages.LOCATION_NOT_FOUND_FULL
            brief = messages.LOCATION_NOT_FOUND_BRIEF
            script.present_message(full, brief)
            return True

        full = messages.SIZE_AND_POSITION_FULL % (rect.width, rect.height, rect.x, rect.y)
        brief = messages.SIZE_AND_POSITION_BRIEF % (rect.width, rect.height, rect.x, rect.y)
        script.present_message(full, brief)
        return True

    @dbus_service.command
    def present_title(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Presents the title of the current window."""

        tokens = ["WHERE AM I PRESENTER: present_title. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        obj = focus_manager.get_manager().get_locus_of_focus()
        if AXObject.is_dead(obj):
            obj = focus_manager.get_manager().get_active_window()

        if obj is None or AXObject.is_dead(obj):
            script.present_message(messages.LOCATION_NOT_FOUND_FULL)
            return True

        title = script.speech_generator.generate_window_title(obj)
        for (string, voice) in title:
            script.present_message(string, voice=voice)
        return True

    @dbus_service.command
    def present_default_button(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        dialog: Atspi.Accessible | None = None,
        notify_user: bool = True
    ) -> bool:
        """Presents the default button of the current dialog."""

        tokens = ["WHERE AM I PRESENTER: present_default_button. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        obj = focus_manager.get_manager().get_locus_of_focus()
        if dialog is None:
            _frame, dialog = script.utilities.frame_and_dialog(obj)
        if dialog is None:
            if notify_user:
                script.present_message(messages.DIALOG_NOT_IN_A)
            return True

        button = AXUtilities.get_default_button(dialog)
        if button is None:
            if notify_user:
                script.present_message(messages.DEFAULT_BUTTON_NOT_FOUND)
            return True

        name = AXObject.get_name(button)
        if not AXUtilities.is_sensitive(button):
            script.present_message(messages.DEFAULT_BUTTON_IS_GRAYED % name)
            return True

        script.present_message(messages.DEFAULT_BUTTON_IS % name)
        return True

    @dbus_service.command
    def present_status_bar(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Presents the status bar and info bar of the current window."""

        tokens = ["WHERE AM I PRESENTER: present_status_bar. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
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
                script.present_message(full, brief)

            infobar = AXUtilities.get_info_bar(frame)
            if infobar and AXUtilities.is_showing(infobar) and AXUtilities.is_visible(infobar):
                script.present_object(infobar, interrupt=statusbar is None)

        return True

    @dbus_service.command
    def present_link(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Presents details about the current link."""

        tokens = ["WHERE AM I PRESENTER: present_link. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        link = focus_manager.get_manager().get_locus_of_focus()
        if not script.utilities.is_link(link):
            if notify_user:
                script.present_message(messages.NOT_ON_A_LINK)
            return True

        return self._do_where_am_i(script, True, link)

    def _get_all_selected_text(self, script: default.Script, obj: Atspi.Accessible) -> str:
        """Returns the selected text of obj plus any adjacent text objects."""

        string = AXText.get_selected_text(obj)[0]
        if script.utilities.is_spreadsheet_cell(obj):
            return string

        prev_obj = script.utilities.find_previous_object(obj)
        while prev_obj:
            selection = AXText.get_selected_text(prev_obj)[0]
            if not selection:
                break
            string = f"{selection} {string}"
            prev_obj = script.utilities.find_previous_object(prev_obj)

        next_obj = script.utilities.find_next_object(obj)
        while next_obj:
            selection = AXText.get_selected_text(next_obj)[0]
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
        notify_user: bool = True
    ) -> bool:
        """Presents the selected text."""

        tokens = ["WHERE AM I PRESENTER: present_selected_text. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        obj = focus_manager.get_manager().get_locus_of_focus()
        if obj is None:
            script.speak_message(messages.LOCATION_NOT_FOUND_FULL)
            return True

        text = self._get_all_selected_text(script, obj)
        if not text:
            script.speak_message(messages.NO_SELECTED_TEXT)
            return True

        manager = speech_and_verbosity_manager.get_manager()
        indentation = manager.get_indentation_description(text, only_if_changed=False)
        text = manager.adjust_for_presentation(obj, text)
        msg = messages.SELECTED_TEXT_IS % f"{indentation} {text}"
        script.speak_message(msg)
        return True

    @dbus_service.command
    def present_selection(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Presents the selected text or selected objects."""

        tokens = ["WHERE AM I PRESENTER: present_selection. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        obj = focus_manager.get_manager().get_locus_of_focus()
        if obj is None:
            if not script.utilities.is_link(obj):
                script.speak_message(messages.LOCATION_NOT_FOUND_FULL)
            return True

        tokens = ["WHERE AM I PRESENTER: presenting selection for", obj]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        spreadsheet = AXObject.find_ancestor(obj, script.utilities.is_spreadsheet_table)
        if spreadsheet is not None and script.utilities.speak_selected_cell_range(spreadsheet):
            return True

        container = script.utilities.get_selection_container(obj)
        if container is None:
            tokens = ["WHERE AM I PRESENTER: Selection container not found for", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return self.present_selected_text(script, event, obj)

        selected_count = script.utilities.selected_child_count(container)
        child_count = script.utilities.selectable_child_count(container)
        script.present_message(messages.selected_items_count(selected_count, child_count))
        if not selected_count:
            return True

        selected_items = script.utilities.selected_children(container)
        item_names = ",".join(map(AXObject.get_name, selected_items))
        script.speak_message(item_names)
        return True

    def _do_where_am_i(
        self,
        script: default.Script,
        basic_only: bool = True,
        obj: Atspi.Accessible | None = None,
        notify_user: bool = True
    ) -> bool:
        """Presents details about the current location at the specified level."""

        if script.spellcheck and script.spellcheck.is_active():
            script.spellcheck.present_error_details(not basic_only)

        if obj is None:
            obj = focus_manager.get_manager().get_locus_of_focus()
        if AXObject.is_dead(obj):
            obj = focus_manager.get_manager().get_active_window()

        if obj is None or AXObject.is_dead(obj):
            if notify_user:
                script.present_message(messages.LOCATION_NOT_FOUND_FULL)
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
            if ancestor is not None \
              and not AXUtilities.is_layout_only(AXObject.get_parent(ancestor)):
                acc = ancestor

            return acc

        script.present_object(
            real_object(obj),
            alreadyFocused=True,
            formatType=format_type,
            forceMnemonic=True,
            forceList=True,
            forceTutorial=True,
            speechOnly=True)

        return True

    @dbus_service.command
    def where_am_i_basic(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Presents basic information about the current location."""

        tokens = ["WHERE AM I PRESENTER: where_am_i_basic. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return self._do_where_am_i(script, notify_user=notify_user)

    @dbus_service.command
    def where_am_i_detailed(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Presents detailed information about the current location."""

        tokens = ["WHERE AM I PRESENTER: where_am_i_detailed. Script:", script,
                  "Event:", event, "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        # TODO - JD: For some reason, we are starting the basic where am I
        # in response to the first click. Then we do the detailed one in
        # response to the second click. Until that's fixed, interrupt the
        # first one.
        script.interrupt_presentation()
        return self._do_where_am_i(script, False, notify_user=notify_user)

_presenter = WhereAmIPresenter()
def get_presenter() -> WhereAmIPresenter:
    """Returns the Where Am I Presenter"""

    return _presenter
