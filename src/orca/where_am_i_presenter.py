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

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc." \
                "Copyright (c) 2016-2023 Igalia, S.L."
__license__   = "LGPL"

from . import cmdnames
from . import debug
from . import focus_manager
from . import input_event
from . import keybindings
from . import messages
from . import settings_manager
from .ax_component import AXComponent
from .ax_object import AXObject
from .ax_utilities import AXUtilities


class WhereAmIPresenter:
    """Module for commands related to the current accessible object."""

    def __init__(self):
        self._handlers = self.get_handlers(True)
        self._desktop_bindings = keybindings.KeyBindings()
        self._laptop_bindings = keybindings.KeyBindings()

    def get_bindings(self, refresh=False, is_desktop=True):
        """Returns the where-am-i-presenter keybindings."""

        if refresh:
            msg = "WHERE AM I PRESENTER: Refreshing bindings."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self._setup_bindings()
        elif is_desktop and self._desktop_bindings.isEmpty():
            self._setup_bindings()
        elif not is_desktop and self._laptop_bindings.isEmpty():
            self._setup_bindings()

        if is_desktop:
            return self._desktop_bindings
        return self._laptop_bindings

    def get_handlers(self, refresh=False):
        """Returns the where-am-i-presenter handlers."""

        if refresh:
            msg = "WHERE AM I PRESENTER: Refreshing handlers."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self._setup_handlers()

        return self._handlers

    def _setup_bindings(self):
        """Sets up the where-am-i-presenter key bindings."""

        self._setup_desktop_bindings()
        self._setup_laptop_bindings()

    def _setup_handlers(self):
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
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def _setup_desktop_bindings(self):
        """Sets up the where-am-i-presenter desktop key bindings."""

        self._desktop_bindings = keybindings.KeyBindings()

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "f",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("readCharAttributesHandler")))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "e",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("present_default_button")))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("presentSizeAndPositionHandler")))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Enter",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("getTitleHandler"),
                1))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Enter",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("getStatusBarHandler"),
                2))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Enter",
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("whereAmIBasicHandler"),
                1))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Enter",
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("whereAmIDetailedHandler"),
                2))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("whereAmILinkHandler")))

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "Up",
                keybindings.defaultModifierMask,
                keybindings.ORCA_SHIFT_MODIFIER_MASK,
                self._handlers.get("whereAmISelectionHandler")))

        msg = "WHERE AM I PRESENTER: Desktop bindings set up."
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def _setup_laptop_bindings(self):
        """Sets up the where-am-i-presenter laptop key bindings."""

        self._laptop_bindings = keybindings.KeyBindings()

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "f",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("readCharAttributesHandler")))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "e",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("present_default_button")))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("presentSizeAndPositionHandler")))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "slash",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("getTitleHandler"),
                1))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "slash",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("getStatusBarHandler"),
                2))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "Return",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("whereAmIBasicHandler"),
                1))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "Return",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("whereAmIDetailedHandler"),
                2))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("whereAmILinkHandler")))

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "Up",
                keybindings.defaultModifierMask,
                keybindings.ORCA_SHIFT_MODIFIER_MASK,
                self._handlers.get("whereAmISelectionHandler")))

        msg = "WHERE AM I PRESENTER: Laptop bindings set up."
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def present_character_attributes(self, script, event=None):
        """Presents the font and formatting details for the current character."""

        focus = focus_manager.getManager().get_locus_of_focus()
        attrs = script.utilities.textAttributes(focus, None, True)[0]

        # Get a dictionary of text attributes that the user cares about.
        [user_attr_list, user_attr_dict] = script.utilities.stringToKeysAndDict(
            settings_manager.getManager().getSetting('enabledSpokenTextAttributes'))

        null_values = ['0', '0mm', 'none', 'false']
        for key in user_attr_list:
            # Convert the standard key into the non-standard implementor variant.
            app_key = script.utilities.getAppNameForAttribute(key)
            value = attrs.get(app_key)
            ignore_if_value = user_attr_dict.get(key)
            if value in null_values and ignore_if_value in null_values:
                continue

            if value and value != ignore_if_value:
                script.speakMessage(script.utilities.localizeTextAttribute(key, value))

        return True

    def present_size_and_position(self, script, event=None):
        """Presents the size and position of the current object."""

        if script.flatReviewPresenter.is_active():
            obj = script.flatReviewPresenter.get_current_object(script, event)
        else:
            obj = focus_manager.getManager().get_locus_of_focus()

        rect = AXComponent.get_rect(obj)
        if AXComponent.is_empty_rect(rect):
            full = messages.LOCATION_NOT_FOUND_FULL
            brief = messages.LOCATION_NOT_FOUND_BRIEF
            script.presentMessage(full, brief)
            return True

        full = messages.SIZE_AND_POSITION_FULL % (rect.width, rect.height, rect.x, rect.y)
        brief = messages.SIZE_AND_POSITION_BRIEF % (rect.width, rect.height, rect.x, rect.y)
        script.presentMessage(full, brief)
        return True

    def present_title(self, script, event=None):
        """Presents the title of the current window."""

        obj = focus_manager.getManager().get_locus_of_focus()
        if AXObject.is_dead(obj):
            obj = focus_manager.getManager().get_active_window()

        if obj is None or AXObject.is_dead(obj):
            script.presentMessage(messages.LOCATION_NOT_FOUND_FULL)
            return True

        title = script.speechGenerator.generateTitle(obj)
        for (string, voice) in title:
            script.presentMessage(string, voice=voice)
        return True

    def _present_default_button(self, script, event=None, dialog=None, error_messages=True):
        """Presents the default button of the current dialog."""

        obj = focus_manager.getManager().get_locus_of_focus()
        frame, dialog = script.utilities.frameAndDialog(obj)
        if dialog is None:
            if error_messages:
                script.presentMessage(messages.DIALOG_NOT_IN_A)
            return True

        button = AXUtilities.get_default_button(dialog)
        if button is None:
            if error_messages:
                script.presentMessage(messages.DEFAULT_BUTTON_NOT_FOUND)
            return True

        name = AXObject.get_name(button)
        if not AXUtilities.is_sensitive(button):
            script.presentMessage(messages.DEFAULT_BUTTON_IS_GRAYED % name)
            return True

        script.presentMessage(messages.DEFAULT_BUTTON_IS % name)
        return True

    def present_status_bar(self, script, event=None):
        """Presents the status bar of the current window."""

        obj = focus_manager.getManager().get_locus_of_focus()
        frame, dialog = script.utilities.frameAndDialog(obj)
        if frame:
            statusbar = AXUtilities.get_status_bar(frame)
            if statusbar:
                script.pointOfReference['statusBarItems'] = None
                script.presentObject(statusbar, interrupt=True)
                script.pointOfReference['statusBarItems'] = None
            else:
                full = messages.STATUS_BAR_NOT_FOUND_FULL
                brief = messages.STATUS_BAR_NOT_FOUND_BRIEF
                script.presentMessage(full, brief)

            infobar = script.utilities.infoBar(frame)
            if infobar:
                script.presentObject(infobar, interrupt=statusbar is None)

        # TODO - JD: Pending user feedback, this should be removed.
        if dialog:
            self._present_default_button(script, event, dialog, False)

        return True

    def present_default_button(self, script, event=None):
        """Presents the default button of the current window."""

        return self._present_default_button(script, event)

    def present_link(self, script, event=None, link=None):
        """Presents details about the current link."""

        link = link or focus_manager.getManager().get_locus_of_focus()
        if not script.utilities.isLink(link):
            script.presentMessage(messages.NOT_ON_A_LINK)
            return True

        return self._do_where_am_i(script, event, True, link)

    def present_selected_text(self, script, event=None, obj=None):
        """Presents the selected text."""

        obj = obj or focus_manager.getManager().get_locus_of_focus()
        if obj is None:
            script.speakMessage(messages.LOCATION_NOT_FOUND_FULL)
            return True

        text = script.utilities.allSelectedText(obj)[0]
        if not text:
            script.speakMessage(messages.NO_SELECTED_TEXT)
            return True

        if script.utilities.shouldVerbalizeAllPunctuation(obj):
            text = script.utilities.verbalizeAllPunctuation(text)

        msg = messages.SELECTED_TEXT_IS % text
        script.speakMessage(msg)
        return True

    def present_selection(self, script, event=None, obj=None):
        """Presents the selected text or selected objects."""

        obj = obj or focus_manager.getManager().get_locus_of_focus()
        if obj is None:
            script.speakMessage(messages.LOCATION_NOT_FOUND_FULL)
            return True

        tokens = ["WHERE AM I PRESENTER: presenting selection for", obj]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        spreadsheet = AXObject.find_ancestor(obj, script.utilities.isSpreadSheetTable)
        if spreadsheet is not None and script.utilities.speakSelectedCellRange(spreadsheet):
            return True

        container = script.utilities.getSelectionContainer(obj)
        if container is None:
            tokens = ["WHERE AM I PRESENTER: Selection container not found for", obj]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return self.present_selected_text(script, event, obj)

        selected_count = script.utilities.selectedChildCount(container)
        child_count = script.utilities.selectableChildCount(container)
        script.presentMessage(messages.selectedItemsCount(selected_count, child_count))
        if not selected_count:
            return True

        selected_items = script.utilities.selectedChildren(container)
        item_names = ",".join(map(AXObject.get_name, selected_items))
        script.speakMessage(item_names)
        return True

    def _do_where_am_i(self, script, event=None, basic_only=True, obj=None):
        """Presents details about the current location at the specified level."""

        if script.spellcheck and script.spellcheck.isActive():
            script.spellcheck.presentErrorDetails(not basic_only)

        if obj is None:
            obj = focus_manager.getManager().get_locus_of_focus()
        if AXObject.is_dead(obj):
            obj = focus_manager.getManager().get_active_window()

        if obj is None or AXObject.is_dead(obj):
            script.presentMessage(messages.LOCATION_NOT_FOUND_FULL)
            return True

        if basic_only:
            format_type = 'basicWhereAmI'
        else:
            format_type = 'detailedWhereAmI'

        script.presentObject(
            script.utilities.realActiveAncestor(obj),
            alreadyFocused=True,
            formatType=format_type,
            forceMnemonic=True,
            forceList=True,
            forceTutorial=True,
            speechOnly=True)

        return True

    def where_am_i_basic(self, script, event=None):
        """Presents basic information about the current location."""

        return self._do_where_am_i(script, event)

    def where_am_i_detailed(self, script, event=None):
        """Presents detailed information about the current location."""

        # TODO - JD: For some reason, we are starting the basic where am I
        # in response to the first click. Then we do the detailed one in
        # response to the second click. Until that's fixed, interrupt the
        # first one.
        script.presentationInterrupt()
        return self._do_where_am_i(script, event, False)

_presenter = WhereAmIPresenter()
def getPresenter():
    """Returns the Where Am I Presenter"""

    return _presenter
