# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
# Copyright 2010 Orca Team.
# Copyright 2014-2025 Igalia, S.L.
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

# pylint: disable=too-many-boolean-expressions
# pylint: disable=too-many-branches
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-return-statements
# pylint: disable=too-many-statements
# pylint: disable=wrong-import-position

"""Provides support for accessing user-agent-agnostic web-content."""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc." \
                "Copyright (c) 2010 Orca Team." \
                "Copyright (c) 2014-2025 Igalia, S.L."
__license__   = "LGPL"

from typing import TYPE_CHECKING

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from orca import braille
from orca import braille_presenter
from orca import caret_navigator
from orca import cmdnames
from orca import keybindings
from orca import debug
from orca import focus_manager
from orca import guilabels
from orca import input_event
from orca import input_event_manager
from orca import label_inference
from orca import liveregions
from orca import messages
from orca import settings
from orca import settings_manager
from orca import speech
from orca import speech_and_verbosity_manager
from orca.scripts import default
from orca.ax_component import AXComponent
from orca.ax_document import AXDocument
from orca.ax_event_synthesizer import AXEventSynthesizer
from orca.ax_object import AXObject
from orca.ax_table import AXTable
from orca.ax_text import AXText
from orca.ax_utilities import AXUtilities
from orca.ax_utilities_event import TextEventReason
from orca.structural_navigator import NavigationMode

from .bookmarks import Bookmarks
from .braille_generator import BrailleGenerator
from .speech_generator import SpeechGenerator
from .script_utilities import Utilities

if TYPE_CHECKING:
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

class Script(default.Script):
    """Provides support for accessing user-agent-agnostic web-content."""

    # Type annotations to override the base class types
    utilities: Utilities
    caret_navigator: caret_navigator.CaretNavigator
    live_region_manager: liveregions.LiveRegionManager
    bookmarks: Bookmarks

    def __init__(self, app: Atspi.Accessible) -> None:
        super().__init__(app)

        self._default_sn_mode = NavigationMode.DOCUMENT
        self._default_caret_navigation_enabled: bool = True

        self._loading_content = False
        self._made_find_announcement = False
        self._last_mouse_button_context = None, -1
        self._in_focus_mode = False
        self._focus_mode_is_sticky = False
        self._browse_mode_is_sticky = False

        if settings_manager.get_manager().get_setting("sayAllOnLoad") is None:
            settings_manager.get_manager().set_setting("sayAllOnLoad", True)
        if settings_manager.get_manager().get_setting("pageSummaryOnLoad") is None:
            settings_manager.get_manager().set_setting("pageSummaryOnLoad", True)

        self._changed_lines_only_check_button: Gtk.CheckButton | None = None
        self._control_caret_navigation_check_button: Gtk.CheckButton | None = None
        self._minimum_find_length_adjustment: Gtk.Adjustment | None = None
        self._minimum_find_length_label: Gtk.Label | None = None
        self._minimum_find_length_spin_button: Gtk.SpinButton | None = None
        self._page_summary_on_load_check_button: Gtk.CheckButton | None = None
        self._say_all_on_load_check_button: Gtk.CheckButton | None = None
        self._skip_blank_cells_check_button: Gtk.CheckButton | None = None
        self._speak_cell_coordinates_check_button: Gtk.CheckButton | None = None
        self._speak_cell_headers_check_button: Gtk.CheckButton | None = None
        self._speak_cell_span_check_button: Gtk.CheckButton | None = None
        self._speak_results_during_find_check_button: Gtk.CheckButton | None = None
        self._structural_navigation_check_button: Gtk.CheckButton | None = None
        self._auto_focus_mode_struct_nav_check_button: Gtk.CheckButton | None = None
        self._auto_focus_mode_caret_nav_check_button: Gtk.CheckButton | None = None
        self._auto_focus_mode_native_nav_check_button: Gtk.CheckButton | None = None
        self._layout_mode_check_button: Gtk.CheckButton | None = None

    def activate(self) -> None:
        """Called when this script is activated."""

        tokens = ["WEB: Activating script for", self.app]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        focus = focus_manager.get_manager().get_locus_of_focus()
        in_app = AXUtilities.get_application(focus) == self.app
        in_doc = self.utilities.in_document_content(focus)
        suspend = not (in_doc and in_app)
        reason = f"script activation, not in document content in this app: {suspend}"
        self.get_caret_navigator().suspend_commands(self, suspend, reason)
        self.get_structural_navigator().suspend_commands(self, suspend, reason)
        self.live_region_manager.suspend_commands(self, suspend, reason)
        self.get_table_navigator().suspend_commands(self, suspend, reason)
        super().activate()

    def deactivate(self) -> None:
        """Called when this script is deactivated."""

        self._loading_content = False
        self._made_find_announcement = False
        self._last_mouse_button_context = None, -1
        self.utilities.clear_cached_objects()
        reason = "script deactivation"
        self.get_caret_navigator().suspend_commands(self, False, reason)
        self.get_structural_navigator().suspend_commands(self, False, reason)
        self.live_region_manager.suspend_commands(self, False, reason)
        self.get_table_navigator().suspend_commands(self, False, reason)
        super().deactivate()

    def get_app_key_bindings(self) -> keybindings.KeyBindings:
        """Returns the application-specific keybindings for this script."""

        key_bindings = keybindings.KeyBindings()

        layout = settings_manager.get_manager().get_setting("keyboardLayout")
        is_desktop = layout == settings.GENERAL_KEYBOARD_LAYOUT_DESKTOP

        live_region_bindings = self.live_region_manager.get_bindings(
            refresh=True, is_desktop=is_desktop)
        for key_binding in live_region_bindings.key_bindings:
            key_bindings.add(key_binding)

        key_bindings.add(
            keybindings.KeyBinding(
                "a",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self.input_event_handlers["togglePresentationModeHandler"]))

        key_bindings.add(
            keybindings.KeyBinding(
                "a",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self.input_event_handlers["enableStickyFocusModeHandler"],
                2))

        key_bindings.add(
            keybindings.KeyBinding(
                "a",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self.input_event_handlers["enableStickyBrowseModeHandler"],
                3))

        key_bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self.input_event_handlers["toggleLayoutModeHandler"]))

        return key_bindings

    def setup_input_event_handlers(self) -> None:
        """Defines the input event handlers for this script."""

        super().setup_input_event_handlers()
        self.input_event_handlers.update(self.live_region_manager.get_handlers(True))

        self.input_event_handlers["panBrailleLeftHandler"] = \
            input_event.InputEventHandler(
                Script.pan_braille_left,
                cmdnames.PAN_BRAILLE_LEFT,
                False) # Do not enable learn mode for this action

        self.input_event_handlers["panBrailleRightHandler"] = \
            input_event.InputEventHandler(
                Script.pan_braille_right,
                cmdnames.PAN_BRAILLE_RIGHT,
                False) # Do not enable learn mode for this action

        self.input_event_handlers["togglePresentationModeHandler"] = \
            input_event.InputEventHandler(
                Script.toggle_presentation_mode,
                cmdnames.TOGGLE_PRESENTATION_MODE)

        self.input_event_handlers["enableStickyFocusModeHandler"] = \
            input_event.InputEventHandler(
                Script.enable_sticky_focus_mode,
                cmdnames.SET_FOCUS_MODE_STICKY)

        self.input_event_handlers["enableStickyBrowseModeHandler"] = \
            input_event.InputEventHandler(
                Script.enable_sticky_browse_mode,
                cmdnames.SET_BROWSE_MODE_STICKY)

        self.input_event_handlers["toggleLayoutModeHandler"] = \
            input_event.InputEventHandler(
                Script.toggle_layout_mode,
                cmdnames.TOGGLE_LAYOUT_MODE)

    def get_bookmarks(self) -> Bookmarks:
        """Returns the "bookmarks" class for this script."""

        try:
            return self.bookmarks
        except AttributeError:
            self.bookmarks = Bookmarks(self)
            return self.bookmarks

    def get_braille_generator(self) -> BrailleGenerator:
        """Returns the braille generator for this script."""

        return BrailleGenerator(self)

    def get_label_inference(self) -> label_inference.LabelInference | None:
        """Returns the label inference functionality for this script."""

        return label_inference.LabelInference(self)

    def get_live_region_manager(self) -> liveregions.LiveRegionManager:
        """Returns the live region support for this script."""

        return liveregions.LiveRegionManager(self)

    def get_speech_generator(self) -> SpeechGenerator:
        """Returns the speech generator for this script."""

        return SpeechGenerator(self)

    def get_utilities(self) -> Utilities:
        """Returns the utilities for this script."""

        return Utilities(self)

    def get_app_preferences_gui(self) -> Gtk.Grid:
        """Return a GtkGrid containing app-unique configuration items."""

        grid = Gtk.Grid()
        grid.set_border_width(12)

        general_frame = Gtk.Frame()
        grid.attach(general_frame, 0, 0, 1, 1)

        label = Gtk.Label(label=f"<b>{guilabels.PAGE_NAVIGATION}</b>")
        label.set_use_markup(True)
        general_frame.set_label_widget(label)

        general_alignment = Gtk.Alignment.new(0.5, 0.5, 1, 1)
        general_alignment.set_padding(0, 0, 12, 0)
        general_frame.add(general_alignment)
        general_grid = Gtk.Grid()
        general_alignment.add(general_grid)

        label = guilabels.USE_CARET_NAVIGATION
        value = self.get_caret_navigator().get_is_enabled()
        self._control_caret_navigation_check_button = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self._control_caret_navigation_check_button.set_active(value)
        general_grid.attach(self._control_caret_navigation_check_button, 0, 0, 1, 1)

        label = guilabels.AUTO_FOCUS_MODE_CARET_NAV
        value = self.get_caret_navigator().get_triggers_focus_mode()
        self._auto_focus_mode_caret_nav_check_button = Gtk.CheckButton.new_with_mnemonic(label)
        self._auto_focus_mode_caret_nav_check_button.set_active(value)
        general_grid.attach(self._auto_focus_mode_caret_nav_check_button, 0, 1, 1, 1)

        label = guilabels.USE_STRUCTURAL_NAVIGATION
        value = self.get_structural_navigator().get_is_enabled()
        self._structural_navigation_check_button = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self._structural_navigation_check_button.set_active(value)
        general_grid.attach(self._structural_navigation_check_button, 0, 2, 1, 1)

        label = guilabels.AUTO_FOCUS_MODE_STRUCT_NAV
        value = self.get_structural_navigator().get_triggers_focus_mode()
        self._auto_focus_mode_struct_nav_check_button = Gtk.CheckButton.new_with_mnemonic(label)
        self._auto_focus_mode_struct_nav_check_button.set_active(value)
        general_grid.attach(self._auto_focus_mode_struct_nav_check_button, 0, 3, 1, 1)

        label = guilabels.AUTO_FOCUS_MODE_NATIVE_NAV
        value = settings_manager.get_manager().get_setting("nativeNavTriggersFocusMode")
        self._auto_focus_mode_native_nav_check_button = Gtk.CheckButton.new_with_mnemonic(label)
        self._auto_focus_mode_native_nav_check_button.set_active(value)
        general_grid.attach(self._auto_focus_mode_native_nav_check_button, 0, 4, 1, 1)

        label = guilabels.READ_PAGE_UPON_LOAD
        value = settings_manager.get_manager().get_setting("sayAllOnLoad")
        self._say_all_on_load_check_button = Gtk.CheckButton.new_with_mnemonic(label)
        self._say_all_on_load_check_button.set_active(value)
        general_grid.attach(self._say_all_on_load_check_button, 0, 5, 1, 1)

        label = guilabels.PAGE_SUMMARY_UPON_LOAD
        value = settings_manager.get_manager().get_setting("pageSummaryOnLoad")
        self._page_summary_on_load_check_button = Gtk.CheckButton.new_with_mnemonic(label)
        self._page_summary_on_load_check_button.set_active(value)
        general_grid.attach(self._page_summary_on_load_check_button, 0, 6, 1, 1)

        label = guilabels.CONTENT_LAYOUT_MODE
        value = settings_manager.get_manager().get_setting("layoutMode")
        self._layout_mode_check_button = Gtk.CheckButton.new_with_mnemonic(label)
        self._layout_mode_check_button.set_active(value)
        general_grid.attach(self._layout_mode_check_button, 0, 7, 1, 1)

        table_frame = Gtk.Frame()
        grid.attach(table_frame, 0, 1, 1, 1)

        # TODO - JD: All table settings belong in a non-app dialog page.
        speech_manager = speech_and_verbosity_manager.get_manager()

        label = Gtk.Label(label=f"<b>{guilabels.TABLE_NAVIGATION}</b>")
        label.set_use_markup(True)
        table_frame.set_label_widget(label)

        table_alignment = Gtk.Alignment.new(0.5, 0.5, 1, 1)
        table_alignment.set_padding(0, 0, 12, 0)
        table_frame.add(table_alignment)
        table_grid = Gtk.Grid()
        table_alignment.add(table_grid)

        label = guilabels.TABLE_SPEAK_CELL_COORDINATES
        value = speech_manager.get_announce_cell_coordinates()
        self._speak_cell_coordinates_check_button = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self._speak_cell_coordinates_check_button.set_active(value)
        table_grid.attach(self._speak_cell_coordinates_check_button, 0, 0, 1, 1)

        label = guilabels.TABLE_SPEAK_CELL_SPANS
        value = speech_manager.get_announce_cell_span()
        self._speak_cell_span_check_button = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self._speak_cell_span_check_button.set_active(value)
        table_grid.attach(self._speak_cell_span_check_button, 0, 1, 1, 1)

        label = guilabels.TABLE_ANNOUNCE_CELL_HEADER
        value = speech_manager.get_announce_cell_headers()
        self._speak_cell_headers_check_button = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self._speak_cell_headers_check_button.set_active(value)
        table_grid.attach(self._speak_cell_headers_check_button, 0, 2, 1, 1)

        label = guilabels.TABLE_SKIP_BLANK_CELLS
        value = self.get_table_navigator().get_skip_blank_cells()
        self._skip_blank_cells_check_button = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self._skip_blank_cells_check_button.set_active(value)
        table_grid.attach(self._skip_blank_cells_check_button, 0, 3, 1, 1)

        find_frame = Gtk.Frame()
        grid.attach(find_frame, 0, 2, 1, 1)

        label = Gtk.Label(label=f"<b>{guilabels.FIND_OPTIONS}</b>")
        label.set_use_markup(True)
        find_frame.set_label_widget(label)

        find_alignment = Gtk.Alignment.new(0.5, 0.5, 1, 1)
        find_alignment.set_padding(0, 0, 12, 0)
        find_frame.add(find_alignment)
        find_grid = Gtk.Grid()
        find_alignment.add(find_grid)

        verbosity = settings_manager.get_manager().get_setting("findResultsVerbosity")

        label = guilabels.FIND_SPEAK_RESULTS
        value = verbosity != settings.FIND_SPEAK_NONE
        self._speak_results_during_find_check_button = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self._speak_results_during_find_check_button.set_active(value)
        find_grid.attach(self._speak_results_during_find_check_button, 0, 0, 1, 1)

        label = guilabels.FIND_ONLY_SPEAK_CHANGED_LINES
        value = verbosity == settings.FIND_SPEAK_IF_LINE_CHANGED
        self._changed_lines_only_check_button = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self._changed_lines_only_check_button.set_active(value)
        find_grid.attach(self._changed_lines_only_check_button, 0, 1, 1, 1)

        hgrid = Gtk.Grid()
        find_grid.attach(hgrid, 0, 2, 1, 1)

        self._minimum_find_length_label = \
              Gtk.Label(label=guilabels.FIND_MINIMUM_MATCH_LENGTH)
        self._minimum_find_length_label.set_alignment(0, 0.5)
        hgrid.attach(self._minimum_find_length_label, 0, 0, 1, 1)

        self._minimum_find_length_adjustment = \
            Gtk.Adjustment(settings_manager.get_manager().get_setting(
                "findResultsMinimumLength"), 0, 20, 1)
        self._minimum_find_length_spin_button = Gtk.SpinButton()
        self._minimum_find_length_spin_button.set_adjustment(
            self._minimum_find_length_adjustment)
        hgrid.attach(self._minimum_find_length_spin_button, 1, 0, 1, 1)
        self._minimum_find_length_label.set_mnemonic_widget(
            self._minimum_find_length_spin_button)

        grid.show_all()
        return grid

    def get_preferences_from_gui(self) -> dict[str, bool | int]:
        """Returns a dictionary with the app-specific preferences."""

        assert self._speak_results_during_find_check_button is not None
        assert self._changed_lines_only_check_button is not None
        assert self._minimum_find_length_spin_button is not None
        assert self._say_all_on_load_check_button is not None
        assert self._page_summary_on_load_check_button is not None
        assert self._structural_navigation_check_button is not None
        assert self._auto_focus_mode_struct_nav_check_button is not None
        assert self._control_caret_navigation_check_button is not None
        assert self._auto_focus_mode_caret_nav_check_button is not None
        assert self._auto_focus_mode_native_nav_check_button is not None
        assert self._speak_cell_coordinates_check_button is not None
        assert self._layout_mode_check_button is not None
        assert self._speak_cell_span_check_button is not None
        assert self._speak_cell_headers_check_button is not None
        assert self._skip_blank_cells_check_button is not None

        if not self._speak_results_during_find_check_button.get_active():
            verbosity = settings.FIND_SPEAK_NONE
        elif self._changed_lines_only_check_button.get_active():
            verbosity = settings.FIND_SPEAK_IF_LINE_CHANGED
        else:
            verbosity = settings.FIND_SPEAK_ALL

        return {
            "findResultsVerbosity": verbosity,
            "findResultsMinimumLength":
                self._minimum_find_length_spin_button.get_value(),
            "sayAllOnLoad":
                self._say_all_on_load_check_button.get_active(),
            "pageSummaryOnLoad":
                self._page_summary_on_load_check_button.get_active(),
            "structuralNavigationEnabled":
                self._structural_navigation_check_button.get_active(),
            "structNavTriggersFocusMode":
                self._auto_focus_mode_struct_nav_check_button.get_active(),
            "caretNavigationEnabled":
                self._control_caret_navigation_check_button.get_active(),
            "caretNavTriggersFocusMode":
                self._auto_focus_mode_caret_nav_check_button.get_active(),
            "nativeNavTriggersFocusMode":
                self._auto_focus_mode_native_nav_check_button.get_active(),
            "speakCellCoordinates":
                self._speak_cell_coordinates_check_button.get_active(),
            "layoutMode":
                self._layout_mode_check_button.get_active(),
            "speakCellSpan":
                self._speak_cell_span_check_button.get_active(),
            "speakCellHeaders":
                self._speak_cell_headers_check_button.get_active(),
            "skipBlankCells":
                self._skip_blank_cells_check_button.get_active()
        }

    def _present_find_results(self, obj: Atspi.Accessible, offset: int) -> None:
        """Updates the context and presents the find results if appropriate."""

        document = self.utilities.get_document_for_object(obj)
        if not document:
            return

        start = AXText.get_selection_start_offset(obj)
        if start < 0:
            return

        offset = max(offset, start)
        context = self.utilities.get_caret_context(document)
        self.utilities.set_caret_context(obj, offset, document=document)

        end = AXText.get_selection_end_offset(obj)
        if end - start < settings_manager.get_manager().get_setting("findResultsMinimumLength"):
            return

        verbosity = settings_manager.get_manager().get_setting("findResultsVerbosity")
        if verbosity == settings.FIND_SPEAK_NONE:
            return

        if self._made_find_announcement \
           and verbosity == settings.FIND_SPEAK_IF_LINE_CHANGED \
           and self.utilities.contexts_are_on_same_line(context, (obj, offset)):
            return

        contents = self.utilities.get_line_contents_at_offset(obj, offset)
        self.speak_contents(contents)
        self.update_braille(obj)

        results_count = self.utilities.get_find_results_count()
        if results_count:
            self.present_message(results_count)

        self._made_find_announcement = True

    def in_layout_mode(self) -> bool:
        """ Returns True if we're in layout mode."""

        return settings_manager.get_manager().get_setting("layoutMode")

    def in_focus_mode(self) -> bool:
        """ Returns True if we're in focus mode."""

        return self._in_focus_mode

    def focus_mode_is_sticky(self) -> bool:
        """Returns True if we're in 'sticky' focus mode."""

        return self._focus_mode_is_sticky

    def browse_mode_is_sticky(self) -> bool:
        """Returns True if we're in 'sticky' browse mode."""

        return self._browse_mode_is_sticky

    def use_focus_mode(
        self,
        obj: Atspi.Accessible,
        prev_obj: Atspi.Accessible | None = None
    ) -> bool:
        """Returns True if we should use focus mode in obj."""

        if self._focus_mode_is_sticky:
            msg = "WEB: Using focus mode because focus mode is sticky"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if self._browse_mode_is_sticky:
            msg = "WEB: Not using focus mode because browse mode is sticky"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if focus_manager.get_manager().in_say_all():
            msg = "WEB: Not using focus mode because we're in SayAll."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if self.get_structural_navigator().last_command_prevents_focus_mode():
            msg = "WEB: Not using focus mode due to struct nav settings"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if self.get_table_navigator().last_input_event_was_navigation_command():
            msg = "WEB: Not using focus mode because last command was table navigation"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if prev_obj and AXObject.is_dead(prev_obj):
            prev_obj = None

        if self.get_caret_navigator().last_command_prevents_focus_mode() \
           and AXObject.find_ancestor_inclusive(prev_obj, AXUtilities.is_tool_tip) is None:
            msg = "WEB: Not using focus mode due to caret nav settings"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if not settings_manager.get_manager().get_setting("nativeNavTriggersFocusMode"):
            struct_nav = self.get_structural_navigator().last_input_event_was_navigation_command()
            caret_nav = self.get_caret_navigator().last_input_event_was_navigation_command()
            if not (struct_nav or caret_nav):
                msg = "WEB: Not changing focus/browse mode due to native nav settings"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return self._in_focus_mode

        if self.utilities.is_focus_mode_widget(obj):
            tokens = ["WEB: Using focus mode because", obj, "is a focus mode widget"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        do_not_toggle = AXUtilities.is_link(obj) or AXUtilities.is_radio_button(obj)
        if self._in_focus_mode and do_not_toggle \
           and input_event_manager.get_manager().last_event_was_unmodified_arrow():
            tokens = ["WEB: Staying in focus mode due to arrowing in role of", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        was_in_app = AXObject.find_ancestor(prev_obj, AXUtilities.is_embedded)
        is_in_app = AXObject.find_ancestor(obj, AXUtilities.is_embedded)
        if not was_in_app and is_in_app:
            msg = "WEB: Using focus mode because we just entered a web application"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if self._in_focus_mode and is_in_app:
            if self.utilities.force_browse_mode_for_web_app_descendant(obj):
                tokens = ["WEB: Forcing browse mode for web app descendant", obj]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                return False

            msg = "WEB: Staying in focus mode because we're inside a web application"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        tokens = ["WEB: Not using focus mode for", obj, "due to lack of cause"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return False

    def say_character(self, obj: Atspi.Accessible) -> None:
        """Speaks the character at the current caret position."""

        tokens = ["WEB: Say character for", obj]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        if not self.utilities.in_document_content(obj):
            msg = "WEB: Object is not in document content."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            super().say_character(obj)
            return

        document = self.utilities.get_top_level_document_for_object(obj)
        obj, offset = self.utilities.get_caret_context(document=document)
        tokens = ["WEB: Adjusted object and offset for say character to", obj, offset]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if not obj:
            return

        contents: list[tuple[Atspi.Accessible, int, int, str]] | None = None
        if self.utilities.treat_as_end_of_line(obj, offset) and AXObject.supports_text(obj):
            char = AXText.get_character_at_offset(obj, offset)[0]
            if char == "\ufffc":
                char = ""
            contents = [(obj, offset, offset + 1, char)]
        else:
            contents = self.utilities.get_character_contents_at_offset(obj, offset)

        if not contents:
            return

        obj, start, _end, string = contents[0]
        if start > 0 and string == "\n":
            if speech_and_verbosity_manager.get_manager().get_speak_blank_lines():
                self.speak_message(messages.BLANK, interrupt=False)
                return

        if string:
            self.speak_misspelled_indicator(obj, start)
            self.speak_character(string)
        else:
            self.speak_contents(contents)

        self.point_of_reference["lastTextUnitSpoken"] = "char"

    def say_word(self, obj: Atspi.Accessible) -> None:
        """Speaks the word at the current caret position."""

        tokens = ["WEB: Say word for", obj]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        if not self.utilities.in_document_content(obj):
            msg = "WEB: Object is not in document content."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            super().say_word(obj)
            return

        document = self.utilities.get_top_level_document_for_object(obj)
        obj, offset = self.utilities.get_caret_context(document=document)
        if input_event_manager.get_manager().last_event_was_right():
            offset -= 1

        tokens = ["WEB: Adjusted object and offset for say word to", obj, offset]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        word_contents = self.utilities.get_word_contents_at_offset(obj, offset, use_cache=True)
        text_obj, start_offset, _end_offset, _word = word_contents[0]
        self.speak_misspelled_indicator(text_obj, start_offset)
        # TODO - JD: Clean up the focused + alreadyFocused mess which by side effect is causing
        # the content of some objects (e.g. table cells) to not be generated.
        self.speak_contents(word_contents, alreadyFocused=AXUtilities.is_text_input(text_obj))
        self.point_of_reference["lastTextUnitSpoken"] = "word"

    def say_line(self, obj: Atspi.Accessible, offset: int | None = None) -> None:
        """Speaks the line at the current caret position."""

        tokens = ["WEB: Say line for", obj]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        if not self.utilities.in_document_content(obj):
            msg = "WEB: Object is not in document content."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            super().say_line(obj)
            return

        # TODO - JD: We're making an exception here because the default script's say_line()
        # handles verbalized punctuation, indentation, repeats, etc. That adjustment belongs
        # in the generators, but that's another potentially non-trivial change.
        if AXUtilities.is_editable(obj) and "\ufffc" not in AXText.get_line_at_offset(obj)[0]:
            msg = "WEB: Object is editable and line has no EOCs."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            if not self._in_focus_mode:
                self.utilities.set_caret_position(obj, 0)
            super().say_line(obj)
            return

        document = self.utilities.get_top_level_document_for_object(obj)
        prior_context = self.utilities.get_prior_context(document=document)
        if prior_context is not None:
            prior_obj, _prior_offset = prior_context
        else:
            prior_obj = None

        if offset is None:
            obj, offset = self.utilities.get_caret_context(document)
            tokens = ["WEB: Adjusted object and offset for say line to", obj, offset]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        contents = self.utilities.get_line_contents_at_offset(obj, offset, use_cache=True)
        if contents and contents[0] and not self._in_focus_mode:
            self.utilities.set_caret_position(contents[0][0], contents[0][1])

        self.speak_contents(contents, priorObj=prior_obj)
        self.point_of_reference["lastTextUnitSpoken"] = "line"

    def present_object(self, obj: Atspi.Accessible, **args) -> None:
        if obj is None:
            return

        if not self.utilities.in_document_content(obj) or AXUtilities.is_document(obj):
            super().present_object(obj, **args)
            return

        mode, _obj = focus_manager.get_manager().get_active_mode_and_object_of_interest()
        if mode in [focus_manager.OBJECT_NAVIGATOR, focus_manager.MOUSE_REVIEW]:
            super().present_object(obj, **args)
            return

        if AXUtilities.is_status_bar(obj) or AXUtilities.is_alert(obj):
            if not self._in_focus_mode:
                self.utilities.set_caret_position(obj, 0)
            super().present_object(obj, **args)
            return

        prior_obj = args.get("priorObj")
        if self.get_caret_navigator().last_input_event_was_navigation_command() \
           or self.get_structural_navigator().last_input_event_was_navigation_command() \
           or self.get_table_navigator().last_input_event_was_navigation_command() \
           or args.get("includeContext") or AXTable.get_table(obj):
            prior_context = self.utilities.get_prior_context()
            if prior_context is not None:
                prior_obj, _prior_offset = prior_context
                args["priorObj"] = prior_obj

        # Objects might be destroyed as a consequence of scrolling, such as in an infinite scroll
        # list. Therefore, store its name and role beforehand. Objects in the process of being
        # destroyed typically lose their name even if they lack the defunct state. If the name of
        # the object is different after scrolling, we'll try to find a child with the same name and
        # role.
        document = self.utilities.get_document_for_object(obj)
        name = AXObject.get_name(obj)
        role = AXObject.get_role(obj)
        AXEventSynthesizer.scroll_to_center(obj, start_offset=0)
        if (name and AXObject.get_name(obj) != name) or AXObject.get_index_in_parent(obj) < 0:
            tokens = ["WEB:", obj, "believed to be destroyed after scroll."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            replicant = AXObject.find_descendant(
                document, lambda x: AXObject.get_name(x) == name and AXObject.get_role(obj) == role)
            if replicant:
                obj = replicant
                tokens = ["WEB: Replacing destroyed object with", obj]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        # Reasons we don't want to dive deep into the object include:
        # 1. Editors like VSCode use the entry role for the code editor.
        # 2. Giant nested lists.
        if AXUtilities.is_entry(obj) or AXUtilities.is_list_item(obj):
            if not self._in_focus_mode:
                self.utilities.set_caret_position(obj, 0)
            super().present_object(obj, **args)
            return

        interrupt = args.get("interrupt", False)
        tokens = ["WEB: Presenting object", obj, ". Interrupt:", interrupt]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        # We shouldn't use cache in this method, because if the last thing we presented
        # included this object and offset (e.g. a Say All or Mouse Review), we're in
        # danger of presented irrelevant context.
        offset = args.get("offset", 0)
        contents = self.utilities.get_object_contents_at_offset(obj, offset, use_cache=False)
        if contents and contents[0] and not self._in_focus_mode:
            self.utilities.set_caret_position(contents[0][0], contents[0][1])
        self.display_contents(contents)
        self.speak_contents(contents, **args)

    def _update_braille_caret_position(self, obj: Atspi.Accessible) -> None:
        """Try to reposition the cursor without having to do a full update."""

        if "\ufffc" in AXText.get_all_text(obj):
            self.update_braille(obj)
            return

        super()._update_braille_caret_position(obj)

    def update_braille(self, obj: Atspi.Accessible, **args) -> None:
        """Updates the braille display to show the given object."""

        tokens = ["WEB: updating braille for", obj, args]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True, True)

        if not braille_presenter.get_presenter().use_braille():
            return

        if self._in_focus_mode and "\ufffc" not in AXText.get_all_text(obj):
            tokens = ["WEB: updating braille in focus mode", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            super().update_braille(obj, **args)
            return

        document = args.get("documentFrame", self.utilities.get_top_level_document_for_object(obj))
        if not document:
            tokens = ["WEB: updating braille for non-document object", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            super().update_braille(obj, **args)
            return

        is_content_editable = self.utilities.is_content_editable_with_embedded_objects(obj)

        if not self.get_caret_navigator().last_input_event_was_navigation_command() \
           and not self.get_structural_navigator().last_input_event_was_navigation_command() \
           and not self.get_table_navigator().last_input_event_was_navigation_command() \
           and not is_content_editable \
           and not AXDocument.is_plain_text(document) \
           and not input_event_manager.get_manager().last_event_was_caret_selection():
            tokens = ["WEB: updating braille for unhandled navigation type", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            super().update_braille(obj, **args)
            return

        # TODO - JD: Getting the caret context can, by side effect, update it. This in turn
        # can prevent us from presenting table column headers when braille is enabled because
        # we think they are not "new." Commit bd877203f0 addressed that, but we need to stop
        # such side effects from happening in the first place.
        offset = args.get("offset")
        if offset is None:
            obj, offset = self.utilities.get_caret_context(
                document, get_replicant=True)
        if offset > 0 and is_content_editable \
           and self.utilities.treat_as_text_object(obj):
            offset = min(offset, AXText.get_character_count(obj))

        contents = self.utilities.get_line_contents_at_offset(obj, offset)
        self.display_contents(contents, documentFrame=document)

    def pan_braille_left(
        self,
        event: input_event.InputEvent | None = None,
        pan_amount: int = 0
    ) -> bool:
        """Pans braille to the left."""

        if self.get_flat_review_presenter().is_active() \
           or not self.utilities.in_document_content() or not braille.beginningIsShowing:
            return super().pan_braille_left(event, pan_amount)

        contents = self.utilities.get_previous_line_contents()
        if not contents:
            return False

        obj, start, _end, _string = contents[0]
        self.utilities.set_caret_position(obj, start)
        self.update_braille(obj)

        # Hack: When panning to the left in a document, we want to start at
        # the right/bottom of each new object. For now, we'll pan there.
        # When time permits, we'll give our braille code some smarts.
        while braille.panRight(0):
            pass

        braille.refresh(False)
        return True

    def pan_braille_right(
        self,
        event: input_event.InputEvent | None = None,
        pan_amount: int = 0
    ) -> bool:
        """Pans braille to the right."""

        if self.get_flat_review_presenter().is_active() \
           or not self.utilities.in_document_content() or not braille.endIsShowing:
            return super().pan_braille_right(event, pan_amount)

        contents = self.utilities.get_next_line_contents()
        if not contents:
            return False

        obj, start, _end, _string = contents[0]
        self.utilities.set_caret_position(obj, start)
        self.update_braille(obj)

        # Hack: When panning to the right in a document, we want to start at
        # the left/top of each new object. For now, we'll pan there. When time
        # permits, we'll give our braille code some smarts.
        while braille.panLeft(0):
            pass

        braille.refresh(False)
        return True

    def enable_sticky_browse_mode(
        self,
        _event: input_event.InputEvent | None = None,
        force_message: bool = False
    ) -> bool:
        """Enables sticky browse mode."""

        if not self._browse_mode_is_sticky or force_message:
            self.present_message(messages.MODE_BROWSE_IS_STICKY)

        self._in_focus_mode = False
        self._focus_mode_is_sticky = False
        self._browse_mode_is_sticky = True
        reason = "enable sticky browse mode"
        self.get_caret_navigator().suspend_commands(self, self._in_focus_mode, reason)
        self.get_structural_navigator().suspend_commands(self, self._in_focus_mode, reason)
        self.live_region_manager.suspend_commands(self, self._in_focus_mode, reason)
        self.get_table_navigator().suspend_commands(self, self._in_focus_mode, reason)
        return True

    def enable_sticky_focus_mode(
        self,
        _event: input_event.InputEvent | None = None,
        force_message: bool = False
    ) -> bool:
        """Enables sticky focus mode."""

        if not self._focus_mode_is_sticky or force_message:
            self.present_message(messages.MODE_FOCUS_IS_STICKY)

        self._in_focus_mode = True
        self._focus_mode_is_sticky = True
        self._browse_mode_is_sticky = False
        reason = "enable sticky focus mode"
        self.get_caret_navigator().suspend_commands(self, self._in_focus_mode, reason)
        self.get_structural_navigator().suspend_commands(self, self._in_focus_mode, reason)
        self.live_region_manager.suspend_commands(self, self._in_focus_mode, reason)
        self.get_table_navigator().suspend_commands(self, self._in_focus_mode, reason)
        return True

    def toggle_layout_mode(
        self,
        _event: input_event.InputEvent | None = None,
        notify_user: bool = True
    ) -> bool:
        """Switches between object mode and layout mode for line presentation."""

        layout_mode = not settings_manager.get_manager().get_setting("layoutMode")
        if notify_user:
            if layout_mode:
                self.present_message(messages.MODE_LAYOUT)
            else:
                self.present_message(messages.MODE_OBJECT)
        settings_manager.get_manager().set_setting("layoutMode", layout_mode)
        return True

    def toggle_presentation_mode(
        self,
        event: input_event.InputEvent | None = None,
        document: Atspi.Accessible | None = None,
        notify_user: bool = True
    ) -> bool:
        """Switches between browse mode and focus mode."""

        obj, _offset = self.utilities.get_caret_context(document)
        if self._in_focus_mode:
            parent = AXObject.get_parent(obj)
            if AXUtilities.is_list_box(parent):
                self.utilities.set_caret_context(parent, -1)
            elif AXUtilities.is_menu(parent):
                self.utilities.set_caret_context(AXObject.get_parent(parent), -1)
            if notify_user and not self._loading_content:
                self.present_message(messages.MODE_BROWSE)
        else:
            if not self.utilities.grab_focus_when_setting_caret(obj) \
               and (self.get_caret_navigator().last_input_event_was_navigation_command() \
                    or self.get_structural_navigator().last_input_event_was_navigation_command() \
                    or self.get_table_navigator().last_input_event_was_navigation_command() \
                    or event):
                AXObject.grab_focus(obj)

            if notify_user:
                self.present_message(messages.MODE_FOCUS)
        self._in_focus_mode = not self._in_focus_mode
        self._focus_mode_is_sticky = False
        self._browse_mode_is_sticky = False

        reason = "toggling focus/browse mode"
        self.get_caret_navigator().suspend_commands(self, self._in_focus_mode, reason)
        self.get_structural_navigator().suspend_commands(self, self._in_focus_mode, reason)
        self.live_region_manager.suspend_commands(self, self._in_focus_mode, reason)
        self.get_table_navigator().suspend_commands(self, self._in_focus_mode, reason)
        return True

    def locus_of_focus_changed(
        self,
        event: Atspi.Event | None,
        old_focus: Atspi.Accessible | None,
        new_focus: Atspi.Accessible | None
    ) -> bool:
        """Handles changes of focus of interest. Returns True if this script did all needed work."""

        tokens = ["WEB: Focus changing from", old_focus, "to", new_focus]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if new_focus and not AXObject.is_valid(new_focus):
            return True

        if new_focus and AXObject.is_dead(new_focus):
            return True

        document = self.utilities.get_top_level_document_for_object(new_focus)
        if not document and self.utilities.is_document(new_focus):
            document = new_focus

        sn_navigator = self.get_structural_navigator()
        last_command_was_struct_nav = sn_navigator.last_input_event_was_navigation_command()

        if not document:
            msg = "WEB: Locus of focus changed to non-document obj"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._made_find_announcement = False
            self._in_focus_mode = False

            old_document = self.utilities.get_top_level_document_for_object(old_focus)
            if not document and self.utilities.is_document(old_focus):
                old_document = old_focus

            if old_focus and not old_document:
                msg = "WEB: Not refreshing grabs because we weren't in a document before"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return False

            if last_command_was_struct_nav and sn_navigator.get_mode(self) == NavigationMode.GUI:
                msg = "WEB: Not refreshing grabs: Last command was GUI structural navigation"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return False

            tokens = ["WEB: Refreshing grabs because we left document", old_document]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

            reason = "locus of focus no longer in document"
            self.get_caret_navigator().suspend_commands(self, True, reason)
            assert self.live_region_manager is not None
            self.live_region_manager.suspend_commands(self, True, reason)
            self.get_structural_navigator().suspend_commands(self, True, reason)
            self.get_table_navigator().suspend_commands(self, True, reason)
            return False

        if self.get_flat_review_presenter().is_active():
            self.get_flat_review_presenter().quit()

        caret_offset = 0
        if self.utilities.in_find_container(old_focus) \
           or (self.utilities.is_document(new_focus) \
               and old_focus == focus_manager.get_manager().get_active_window()):
            context_obj, context_offset = self.utilities.get_caret_context(document)
            if context_obj and AXObject.is_valid(context_obj):
                new_focus, caret_offset = context_obj, context_offset

        if AXUtilities.is_unknown_or_redundant(new_focus):
            msg = "WEB: Event source has bogus role. Likely browser bug."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            new_focus, _offset = self.utilities.first_context(new_focus, 0)

        if self.utilities.treat_as_text_object(new_focus):
            text_offset = AXText.get_caret_offset(new_focus)
            if 0 <= text_offset <= AXText.get_character_count(new_focus):
                caret_offset = text_offset

        self.utilities.set_caret_context(new_focus, caret_offset, document)
        self.update_braille(new_focus, documentFrame=document)

        contents = None
        args = {}
        last_command_was_caret_nav = \
            self.get_caret_navigator().last_input_event_was_navigation_command()
        last_command_was_struct_nav = last_command_was_struct_nav \
            or self.get_table_navigator().last_input_event_was_navigation_command()
        manager = input_event_manager.get_manager()
        last_command_was_line_nav = manager.last_event_was_line_navigation() \
            and not last_command_was_caret_nav

        args["priorObj"] = old_focus
        if manager.last_event_was_mouse_button() and event \
             and event.type.startswith("object:text-caret-moved"):
            msg = "WEB: Last input event was mouse button. Generating line."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            contents = self.utilities.get_line_contents_at_offset(new_focus, caret_offset)
        elif self.utilities.is_content_editable_with_embedded_objects(new_focus) \
           and (last_command_was_caret_nav \
                or last_command_was_struct_nav or last_command_was_line_nav) \
           and not (AXUtilities.is_table_cell(new_focus) and AXObject.get_name(new_focus)):
            tokens = ["WEB: New focus", new_focus, "content editable. Generating line."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            contents = self.utilities.get_line_contents_at_offset(new_focus, caret_offset)
        elif self.utilities.is_anchor(new_focus):
            tokens = ["WEB: New focus", new_focus, "is anchor. Generating line."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            contents = self.utilities.get_line_contents_at_offset(new_focus, 0)
        elif input_event_manager.get_manager().last_event_was_page_navigation() \
             and not AXTable.get_table(new_focus) \
             and not AXUtilities.is_feed_article(new_focus):
            tokens = ["WEB: New focus", new_focus, "was scrolled to. Generating line."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            contents = self.utilities.get_line_contents_at_offset(new_focus, caret_offset)
        elif self.utilities.is_focused_with_math_child(new_focus):
            tokens = ["WEB: New focus", new_focus, "has math child. Generating line."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            contents = self.utilities.get_line_contents_at_offset(new_focus, caret_offset)
        elif AXUtilities.is_heading(new_focus):
            tokens = ["WEB: New focus", new_focus, "is heading. Generating object."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            contents = self.utilities.get_object_contents_at_offset(new_focus, 0)
        elif self.utilities.caret_moved_to_same_page_fragment(event, old_focus):
            assert event is not None
            tokens = ["WEB: Source", event.source, "is same page fragment. Generating line."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            contents = self.utilities.get_line_contents_at_offset(new_focus, 0)
        elif event and event.type.startswith("object:children-changed:remove") \
             and self.utilities.is_focus_mode_widget(new_focus):
            tokens = ["WEB: New focus", new_focus,
                      "is recovery from removed child. Generating speech."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        elif last_command_was_line_nav and not AXObject.is_valid(old_focus):
            msg = "WEB: Last input event was line nav; old_focus is invalid. Generating line."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            contents = self.utilities.get_line_contents_at_offset(new_focus, caret_offset)
        elif last_command_was_line_nav and event \
             and event.type.startswith("object:children-changed"):
            msg = "WEB: Last input event was line nav and children changed. Generating line."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            contents = self.utilities.get_line_contents_at_offset(new_focus, caret_offset)
        else:
            tokens = ["WEB: New focus", new_focus, "is not a special case. Generating speech."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if new_focus and AXObject.is_dead(new_focus):
            msg = "WEB: New focus has since died"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            if self._get_queued_event("object:state-changed:focused", True):
                msg = "WEB: Have matching focused event. Not speaking contents"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return True

        if self.utilities.should_interrupt_for_locus_of_focus_change(old_focus, new_focus, event):
            self.interrupt_presentation()

        if contents:
            self.speak_contents(contents, **args)
        else:
            utterances = self.speech_generator.generate_speech(new_focus, **args)
            speech.speak(utterances)

        if self.utilities.in_top_level_web_app(new_focus) and not self._browse_mode_is_sticky:
            announce = not self.utilities.in_document_content(old_focus)
            self.enable_sticky_focus_mode(None, announce)
            return True

        if not self._focus_mode_is_sticky \
           and not self._browse_mode_is_sticky \
           and self.use_focus_mode(new_focus, old_focus) != self._in_focus_mode:
            dummy_event = input_event.InputEvent("synthetic")
            self.toggle_presentation_mode(dummy_event, document)

        if not self.utilities.in_document_content(old_focus):
            if self._focus_mode_is_sticky:
                self.present_message(messages.MODE_FOCUS_IS_STICKY)
                return True

            sn_navigator.set_mode(self, NavigationMode.DOCUMENT)
            reason = "locus of focus now in document"
            self.get_caret_navigator().suspend_commands(self, self._in_focus_mode, reason)
            sn_navigator.suspend_commands(self, self._in_focus_mode, reason)
            self.live_region_manager.suspend_commands(self, self._in_focus_mode, reason)
            self.get_table_navigator().suspend_commands(self, self._in_focus_mode, reason)

        return True

    def on_active_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:active accessibility events."""

        if not self.utilities.in_document_content(event.source):
            msg = "WEB: Event source is not in document content"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if not event.detail1:
            msg = "WEB: Ignoring because event source is now inactive"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if AXUtilities.is_dialog_or_alert(event.source):
            msg = "WEB: Event handled: Setting locusOfFocus to event source"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            focus_manager.get_manager().set_locus_of_focus(event, event.source)
            return True

        return False

    def on_busy_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:busy accessibility events."""

        if AXComponent.has_no_size(event.source):
            msg = "WEB: Ignoring event from page with no size."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if not AXDocument.get_uri(event.source):
            msg = "WEB: Ignoring event from page with no URI."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        AXUtilities.clear_all_cache_now(event.source, "busy-changed event.")

        if event.detail1 and self._loading_content:
            msg = "WEB: Ignoring: Already loading document content"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if not self.utilities.in_document_content(event.source):
            msg = "WEB: Event source is not in document content"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        active_document = self.utilities.active_document()
        if active_document and active_document != event.source:
            msg = "WEB: Ignoring: Event source is not active document"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        focus = focus_manager.get_manager().get_locus_of_focus()
        if not AXUtilities.is_document_web(event.source) \
           and not AXObject.is_ancestor(focus, event.source, True):
            msg = "WEB: Ignoring: Not document and not something we're in"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.get_document_for_object(AXObject.get_parent(event.source)):
            msg = "WEB: Ignoring: Event source is nested document"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        obj, offset = self.utilities.get_caret_context()
        if not AXObject.is_valid(obj):
            self.utilities.clear_caret_context()

        should_present = True
        mgr = speech_and_verbosity_manager.get_manager()
        if mgr.get_only_speak_displayed_text():
            should_present = False
            msg = "WEB: Not presenting due to settings"
            debug.print_message(debug.LEVEL_INFO, msg, True)
        elif not (AXUtilities.is_showing(event.source) or AXUtilities.is_visible(event.source)):
            should_present = False
            msg = "WEB: Not presenting because source is not showing or visible"
            debug.print_message(debug.LEVEL_INFO, msg, True)
        elif not AXDocument.get_uri(event.source):
            should_present = False
            msg = "WEB: Not presenting because source lacks URI"
            debug.print_message(debug.LEVEL_INFO, msg, True)
        elif not event.detail1 and self._in_focus_mode and AXObject.is_valid(obj):
            should_present = False
            tokens = ["WEB: Not presenting due to focus mode for", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        elif not mgr.use_verbose_speech():
            should_present = not event.detail1
            tokens = ["WEB: Brief verbosity set. Should present", obj, f": {should_present}"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if should_present and AXDocument.get_uri(event.source).startswith("http"):
            if event.detail1:
                self.present_message(messages.PAGE_LOADING_START)
            elif AXObject.get_name(event.source):
                if not mgr.use_verbose_speech():
                    msg = AXObject.get_name(event.source)
                else:
                    msg = messages.PAGE_LOADING_END_NAMED % AXObject.get_name(event.source)
                self.present_message(msg, reset_styles=False)
            else:
                self.present_message(messages.PAGE_LOADING_END)

        self._loading_content = event.detail1
        if event.detail1:
            return True

        self.utilities.clear_cached_objects()
        if AXObject.is_dead(obj):
            obj = None

        if not focus_manager.get_manager().focus_is_dead() \
           and not self.utilities.in_document_content(focus) \
           and AXUtilities.is_focused(focus):
            msg = "WEB: Not presenting content, focus is outside of document"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if settings_manager.get_manager().get_setting("pageSummaryOnLoad") and should_present:
            tokens = ["WEB: Getting page summary for", event.source]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            summary = AXDocument.get_document_summary(event.source)
            if summary:
                self.present_message(summary)

        obj, offset = self.utilities.get_caret_context()
        if not AXUtilities.is_busy(event.source) \
           and self.utilities.is_top_level_web_app(event.source):
            tokens = ["WEB: Setting locusOfFocus to", obj, "with sticky focus mode"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            focus_manager.get_manager().set_locus_of_focus(event, obj)
            dummy_event = input_event.InputEvent("synthetic")
            self.enable_sticky_focus_mode(dummy_event, True)
            return True

        if self.use_focus_mode(obj) != self._in_focus_mode:
            dummy_event = input_event.InputEvent("synthetic")
            self.toggle_presentation_mode(dummy_event)

        if not obj:
            msg = "WEB: Could not get caret context"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.is_focus_mode_widget(obj):
            tokens = ["WEB: Setting locus of focus to focusModeWidget", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            focus_manager.get_manager().set_locus_of_focus(event, obj)
            return True

        if self.utilities.is_link(obj) and AXUtilities.is_focused(obj):
            tokens = ["WEB: Setting locus of focus to focused link", obj, ". No SayAll."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            focus_manager.get_manager().set_locus_of_focus(event, obj)
            return True

        if offset > 0:
            tokens = ["WEB: Setting locus of focus to context obj", obj, ". No SayAll"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            focus_manager.get_manager().set_locus_of_focus(event, obj)
            return True

        if not AXUtilities.is_focused(focus_manager.get_manager().get_locus_of_focus()):
            tokens = ["WEB: Setting locus of focus to context obj", obj, "(no notification)"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            focus_manager.get_manager().set_locus_of_focus(event, obj, False)

        self.update_braille(obj)
        if AXDocument.get_document_uri_fragment(event.source):
            msg = "WEB: Not doing SayAll due to page fragment"
            debug.print_message(debug.LEVEL_INFO, msg, True)
        elif not settings_manager.get_manager().get_setting("sayAllOnLoad"):
            msg = "WEB: Not doing SayAll due to sayAllOnLoad being False"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self.speak_contents(self.utilities.get_line_contents_at_offset(obj, offset))
        elif speech_and_verbosity_manager.get_manager().get_speech_is_enabled_and_not_muted():
            msg = "WEB: Doing SayAll"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self.get_say_all_presenter().say_all(self, None)
        else:
            msg = "WEB: Not doing SayAll due to speech being disabled or muted"
            debug.print_message(debug.LEVEL_INFO, msg, True)

        return True

    def on_caret_moved(self, event: Atspi.Event) -> bool:
        """Callback for object:text-caret-moved accessibility events."""

        reason = AXUtilities.get_text_event_reason(event)
        document = self.utilities.get_top_level_document_for_object(event.source)
        if not document:
            if self.utilities.event_is_browser_ui_noise_deprecated(event):
                msg = "WEB: Ignoring event believed to be browser UI noise"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return True

            if self.utilities.event_is_browser_ui_autocomplete_noise_deprecated(event):
                msg = "WEB: Ignoring event believed to be browser UI autocomplete noise"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return True

            msg = "WEB: Event source is not in document content"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        obj, offset = self.utilities.get_caret_context(document, False, False)
        tokens = ["WEB: Context: ", obj, ", ", offset]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        # TODO - JD: Make this a TextEventReason.
        if self.get_caret_navigator().last_input_event_was_navigation_command():
            msg = "WEB: Event ignored: Last command was caret nav"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        # TODO - JD: Make this a TextEventReason.
        if self.get_structural_navigator().last_input_event_was_navigation_command():
            msg = "WEB: Event ignored: Last command was struct nav"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        # TODO - JD: Make this a TextEventReason.
        if self.get_table_navigator().last_input_event_was_navigation_command():
            msg = "WEB: Event ignored: Last command was table nav"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if reason == TextEventReason.SAY_ALL:
            msg = "WEB: Event handled: SayAll triggered"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if reason == TextEventReason.MOUSE_PRIMARY_BUTTON:
            if (event.source, event.detail1) == (obj, offset):
                msg = "WEB: Event is for current caret context."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return True

            if (event.source, event.detail1) == self._last_mouse_button_context:
                msg = "WEB: Event is for last mouse button context."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return True

            self._last_mouse_button_context = event.source, event.detail1

            msg = "WEB: Event handled: Last command was mouse button"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self.utilities.set_caret_context(event.source, event.detail1)
            notify = AXObject.find_ancestor_inclusive(obj, AXUtilities.is_entry) is None
            focus_manager.get_manager().set_locus_of_focus(event, event.source, notify, True)
            return True

        if reason == TextEventReason.FOCUS_CHANGE:
            msg = "WEB: Event ignored: Caret moved due to focus change."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.in_find_container():
            msg = "WEB: Event handled: Presenting find results"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._present_find_results(event.source, event.detail1)
            return True

        if not self.utilities.event_is_from_locus_of_focus_document(event):
            msg = "WEB: Event ignored: Not from locus of focus document"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if reason == TextEventReason.UI_UPDATE:
            msg = "WEB: Event ignored: Caret moved due to UI update."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if reason in [TextEventReason.TYPING, TextEventReason.TYPING_ECHOABLE]:
            msg = "WEB: Event handled: Updating position due to insertion"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            focus_manager.get_manager().set_last_cursor_position(event.source, event.detail1)
            return True

        if reason in (TextEventReason.DELETE, TextEventReason.BACKSPACE):
            msg = "WEB: Event handled: Updating position due to deletion"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            focus_manager.get_manager().set_last_cursor_position(event.source, event.detail1)
            return True

        focus = focus_manager.get_manager().get_locus_of_focus()
        i_e_manager = input_event_manager.get_manager()
        if self.utilities.is_item_for_editable_combo_box(focus, event.source) \
           and not i_e_manager.last_event_was_character_navigation() \
           and not i_e_manager.last_event_was_line_boundary_navigation():
            msg = "WEB: Event ignored: Editable combobox noise"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.event_is_autocomplete_noise_deprecated(event, document):
            msg = "WEB: Event ignored: Autocomplete noise"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if self._in_focus_mode and self.utilities.caret_moved_outside_active_grid(event):
            msg = "WEB: Event ignored: Caret moved outside active grid during focus mode"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.treat_event_as_spinner_value_change_deprecated(event):
            msg = "WEB: Event handled as the value-change event we wish we'd get"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self.update_braille(event.source)
            self._present_caret_moved_event(event)
            return True

        if not self.utilities.treat_as_text_object(event.source) \
           and not AXUtilities.is_editable(event.source):
            msg = "WEB: Event ignored: Was for non-editable object we're treating as textless"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        notify = force = handled = False
        AXObject.clear_cache(event.source, False, "Updating state for caret moved event.")

        if self._in_focus_mode:
            obj, offset = event.source, event.detail1
        else:
            obj, offset = self.utilities.first_context(event.source, event.detail1)

        if reason == TextEventReason.NAVIGATION_BY_PAGE:
            msg = "WEB: Caret moved due to scrolling."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            notify = force = handled = True

        elif self.utilities.caret_moved_to_same_page_fragment(event):
            msg = "WEB: Caret moved to fragment."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            notify = force = handled = True

        elif event.source != focus and AXUtilities.is_editable(event.source) and \
             (AXUtilities.is_focused(event.source) or not AXUtilities.is_focusable(event.source)):
            msg = "WEB: Editable object is not (yet) the locus of focus."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            notify = force = handled = \
                i_e_manager.last_event_was_line_navigation() or \
                i_e_manager.last_event_was_return()

        elif i_e_manager.last_event_was_caret_navigation():
            msg = "WEB: Caret moved due to native caret navigation."
            debug.print_message(debug.LEVEL_INFO, msg, True)

        tokens = ["WEB: Setting context and focus to: ", obj, ", ", offset, f", notify: {notify}"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        self.utilities.set_caret_context(obj, offset, document)
        focus_manager.get_manager().set_locus_of_focus(event, obj, notify, force)
        return handled

    def on_checked_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:checked accessibility events."""

        msg = "WEB: This event is is handled by the toolkit or default script."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return False

    def on_children_added(self, event: Atspi.Event) -> bool:
        """Callback for object:children-changed:add accessibility events."""

        AXUtilities.clear_all_cache_now(event.source, "children-changed event.")

        if self.utilities.event_is_browser_ui_noise_deprecated(event):
            msg = "WEB: Ignoring event believed to be browser UI noise"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        is_live_region = AXUtilities.is_live_region(event.source)
        document = self.utilities.get_top_level_document_for_object(event.source)
        if document and not is_live_region:
            focus = focus_manager.get_manager().get_locus_of_focus()
            if event.source == focus:
                msg = "WEB: Dumping cache: source is focus"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                self.utilities.dump_cache(document, preserve_context=True)
            elif focus_manager.get_manager().focus_is_dead():
                msg = "WEB: Dumping cache: dead focus"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                self.utilities.dump_cache(document, preserve_context=True)
            elif AXObject.find_ancestor(focus, lambda x: x == event.source):
                msg = "WEB: Dumping cache: source is ancestor of focus"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                self.utilities.dump_cache(document, preserve_context=True)
            else:
                msg = "WEB: Not dumping full cache"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                self.utilities.clear_cached_objects()
        elif is_live_region:
            msg = "WEB: Ignoring event from live region."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True
        else:
            msg = "WEB: Could not get document for event source"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if self._loading_content:
            msg = "WEB: Ignoring because document content is being loaded."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if not AXObject.is_valid(document):
            tokens = ["WEB: Ignoring because", document, "is not valid."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        if AXUtilities.is_busy(document):
            tokens = ["WEB: Ignoring because", document, "is busy."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        if self.utilities.handle_event_from_context_replicant(event, event.any_data):
            msg = "WEB: Event handled by updating locusOfFocus and context to child."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if AXUtilities.is_alert(event.any_data):
            msg = "WEB: Presenting event.any_data"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self.present_object(event.any_data, interrupt=True)

            focused = AXUtilities.get_focused_object(event.any_data)
            if focused:
                notify = not self.utilities.treat_as_text_object(focused)
                tokens = ["WEB: Setting locusOfFocus and caret context to", focused]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                focus_manager.get_manager().set_locus_of_focus(event, focused, notify)
                self.utilities.set_caret_context(focused, 0)
            return True

        return False

    def on_children_removed(self, event: Atspi.Event) -> bool:
        """Callback for object:children-changed:removed accessibility events."""

        AXUtilities.clear_all_cache_now(event.source, "children-changed event.")

        if not self.utilities.in_document_content(event.source):
            msg = "WEB: Event source is not in document content."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if self._loading_content:
            msg = "WEB: Ignoring because document content is being loaded."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if AXUtilities.is_live_region(event.source):
            if self.utilities.handle_event_for_removed_child(event):
                msg = "WEB: Event handled for removed live-region child."
                debug.print_message(debug.LEVEL_INFO, msg, True)
            else:
                msg = "WEB: Ignoring removal from live region."
                debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        document = self.utilities.get_top_level_document_for_object(event.source)
        if document:
            focus = focus_manager.get_manager().get_locus_of_focus()
            if event.source == focus:
                msg = "WEB: Dumping cache: source is focus"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                self.utilities.dump_cache(document, preserve_context=True)
            elif focus_manager.get_manager().focus_is_dead():
                msg = "WEB: Dumping cache: dead focus"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                self.utilities.dump_cache(document, preserve_context=True)
            elif AXObject.find_ancestor(focus, lambda x: x == event.source):
                msg = "WEB: Dumping cache: source is ancestor of focus"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                self.utilities.dump_cache(document, preserve_context=True)
            else:
                msg = "WEB: Not dumping full cache"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                self.utilities.clear_cached_objects()

        if self.utilities.handle_event_for_removed_child(event):
            msg = "WEB: Event handled for removed child."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        return False

    def on_column_reordered(self, event: Atspi.Event) -> bool:
        """Callback for object:column-reordered accessibility events."""

        if not self.utilities.in_document_content(event.source):
            msg = "WEB: Event source is not in document content"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        focus = focus_manager.get_manager().get_locus_of_focus()
        if event.source != AXTable.get_table(focus):
            msg = "WEB: focus is not in this table"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        self.present_message(messages.TABLE_REORDERED_COLUMNS)
        header = AXObject.find_ancestor_inclusive(focus, AXUtilities.is_table_header)
        msg = AXTable.get_presentable_sort_order_from_header(header, True)
        if msg:
            self.present_message(msg)
        return True

    def on_document_load_complete(self, event: Atspi.Event) -> bool:
        """Callback for document:load-complete accessibility events."""

        if AXComponent.has_no_size(event.source):
            msg = "WEB: Ignoring event from page with no size."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        uri = AXDocument.get_uri(event.source)
        if not uri:
            msg = "WEB: Ignoring event from page with no URI."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if uri.startswith("moz-extension"):
            msg = f"WEB: Ignoring event from page with URI: {uri}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        AXUtilities.clear_all_cache_now(event.source, "load-complete event.")
        if self.utilities.get_document_for_object(AXObject.get_parent(event.source)):
            msg = "WEB: Ignoring: Event source is nested document"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        msg = "WEB: Updating loading state and resetting live regions"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self._loading_content = False
        self.live_region_manager.reset()
        return True

    def on_document_load_stopped(self, event: Atspi.Event) -> bool:
        """Callback for document:load-stopped accessibility events."""

        if self.utilities.get_document_for_object(AXObject.get_parent(event.source)):
            msg = "WEB: Ignoring: Event source is nested document"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        msg = "WEB: Updating loading state"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self._loading_content = False
        return True

    def on_document_reload(self, event: Atspi.Event) -> bool:
        """Callback for document:reload accessibility events."""

        if self.utilities.get_document_for_object(AXObject.get_parent(event.source)):
            msg = "WEB: Ignoring: Event source is nested document"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        msg = "WEB: Updating loading state"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self._loading_content = True
        return True

    def on_expanded_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:expanded accessibility events."""

        if not self.utilities.in_document_content(event.source):
            msg = "WEB: Event source is not in document content"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        focus = focus_manager.get_manager().get_locus_of_focus()
        obj, offset = self.utilities.get_caret_context(search_if_needed=False)
        tokens = ["WEB: Caret context is", obj, ", ", offset]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        if not AXObject.is_valid(obj) and event.source == focus:
            msg = "WEB: Setting caret context to event source"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self.utilities.set_caret_context(event.source, 0)

        return False

    def on_focused_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:focused accessibility events."""

        if not event.detail1:
            msg = "WEB: Ignoring because event source lost focus"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        document = self.utilities.get_document_for_object(event.source)
        if not document:
            msg = "WEB: Could not get document for event source"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if focus_manager.get_manager().in_say_all():
            msg = "WEB: Ignoring focus change during say all"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        focus = focus_manager.get_manager().get_locus_of_focus()
        prev_document = self.utilities.get_document_for_object(focus)
        if prev_document != document:
            tokens = ["WEB: document changed from", prev_document, "to", document]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if AXUtilities.is_link(event.source) and AXObject.is_ancestor(focus, event.source):
            msg = "WEB: Ignoring focus change on link ancestor of focus"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if AXObject.find_ancestor(event.source, AXUtilities.is_embedded):
            if self._browse_mode_is_sticky:
                msg = "WEB: Embedded descendant claimed focus, but browse mode is sticky"
                debug.print_message(debug.LEVEL_INFO, msg, True)
            elif AXUtilities.is_tool_tip(event.source) \
              and AXObject.find_ancestor(focus, lambda x: x == event.source):
                msg = "WEB: Event believed to be side effect of tooltip navigation."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return True
            else:
                msg = "WEB: Event handled: Setting locusOfFocus to embedded descendant"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                if self.utilities.should_interrupt_for_locus_of_focus_change(
                        focus, event.source, event):
                    self.interrupt_presentation()

                focus_manager.get_manager().set_locus_of_focus(event, event.source)
                return True

        if AXUtilities.is_editable(event.source):
            msg = "WEB: Event source is editable"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if AXUtilities.is_dialog_or_alert(event.source):
            if AXObject.is_ancestor(focus, event.source, True):
                msg = "WEB: Ignoring event from ancestor of focus"
                debug.print_message(debug.LEVEL_INFO, msg, True)
            else:
                msg = "WEB: Event handled: Setting locusOfFocus to event source"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                focus_manager.get_manager().set_locus_of_focus(event, event.source)
            return True

        if self.utilities.handle_event_from_context_replicant(event, event.source):
            msg = "WEB: Event handled by updating locusOfFocus and context to source."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        obj, offset = self.utilities.get_caret_context()
        tokens = ["WEB: Caret context is", obj, ", ", offset]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if not AXObject.is_valid(obj) or prev_document != document:
            tokens = ["WEB: Clearing context - obj", obj, "is not valid or document changed"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            self.utilities.clear_caret_context()

            obj, offset = self.utilities.search_for_caret_context(event.source)
            if obj:
                notify = self.utilities.in_find_container(focus)
                tokens = ["WEB: Updating focus and context to", obj, ", ", offset]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                focus_manager.get_manager().set_locus_of_focus(event, obj, notify)
                if not notify and prev_document is None:
                    reason = "updating locus of focus without notification"
                    self.get_caret_navigator().suspend_commands(self, self._in_focus_mode, reason)
                    self.get_structural_navigator().suspend_commands(
                        self, self._in_focus_mode, reason)
                    self.live_region_manager.suspend_commands(self, self._in_focus_mode, reason)
                    self.get_table_navigator().suspend_commands(self, self._in_focus_mode, reason)
                self.utilities.set_caret_context(obj, offset)
            else:
                msg = "WEB: Search for caret context failed"
                debug.print_message(debug.LEVEL_INFO, msg, True)

        if self.get_caret_navigator().last_input_event_was_navigation_command():
            msg = "WEB: Event ignored: Last command was caret nav"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if self.get_structural_navigator().last_input_event_was_navigation_command():
            msg = "WEB: Event ignored: Last command was struct nav"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if self.get_table_navigator().last_input_event_was_navigation_command():
            msg = "WEB: Event ignored: Last command was table nav"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if not (AXUtilities.is_focusable(event.source) and AXUtilities.is_focused(event.source)):
            msg = "WEB: Event ignored: Source is not focusable or focused"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if not AXUtilities.is_document(event.source):
            msg = "WEB: Deferring to other scripts for handling non-document source"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if not obj:
            msg = "WEB: Unable to get valid context object"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if input_event_manager.get_manager().last_event_was_page_navigation():
            msg = "WEB: Event handled: Focus changed due to scrolling"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            focus_manager.get_manager().set_locus_of_focus(event, obj)
            self.utilities.set_caret_context(obj, offset)
            return True

        # TODO - JD: Can this logic be removed?
        was_focused = AXUtilities.is_focused(obj)
        AXObject.clear_cache(obj, False, "Sanity-checking focused state.")
        is_focused = AXUtilities.is_focused(obj)
        if was_focused != is_focused:
            tokens = ["WEB: Focused state of", obj, "changed to", is_focused]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        if self.utilities.is_anchor(obj):
            cause = "Context is anchor"
        elif not (self.utilities.is_link(obj) and not is_focused):
            cause = "Context is not a non-focused link"
        elif self.utilities.is_child_of_current_fragment(obj):
            cause = "Context is child of current fragment"
        elif document == event.source and AXDocument.get_document_uri_fragment(event.source):
            cause = "Document URI is fragment"
        else:
            return False

        tokens = ["WEB: Event handled: Setting locusOfFocus to", obj, "(", cause, ")"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        focus_manager.get_manager().set_locus_of_focus(event, obj)
        return True

    def on_mouse_button(self, event: Atspi.Event) -> bool:
        """Callback for mouse:button accessibility events."""

        return False

    def on_name_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:property-change:accessible-name events."""

        if self.utilities.event_is_browser_ui_noise_deprecated(event):
            msg = "WEB: Ignoring event believed to be browser UI noise"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        return False

    def on_row_reordered(self, event: Atspi.Event) -> bool:
        """Callback for object:row-reordered accessibility events."""

        if not self.utilities.in_document_content(event.source):
            msg = "WEB: Event source is not in document content"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        focus = focus_manager.get_manager().get_locus_of_focus()
        if event.source != AXTable.get_table(focus):
            msg = "WEB: focus is not in this table"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        self.present_message(messages.TABLE_REORDERED_ROWS)
        header = AXObject.find_ancestor_inclusive(focus, AXUtilities.is_table_header)
        msg = AXTable.get_presentable_sort_order_from_header(header, True)
        if msg:
            self.present_message(msg)
        return True

    def on_selected_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:selected accessibility events."""

        if self.utilities.event_is_browser_ui_autocomplete_noise_deprecated(event):
            msg = "WEB: Ignoring event believed to be browser UI autocomplete noise"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        focus = focus_manager.get_manager().get_locus_of_focus()
        if self.utilities.event_is_browser_ui_page_switch(event):
            msg = "WEB: Event believed to be browser UI page switch"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            if event.detail1:
                # https://bugzilla.mozilla.org/show_bug.cgi?id=1867044
                AXObject.clear_cache(event.source, False, "Work around Gecko bug.")
                AXUtilities.clear_all_cache_now(reason=msg)
                self.present_object(event.source, priorObj=focus, interrupt=True)
            return True

        if not self.utilities.in_document_content(event.source):
            msg = "WEB: Event source is not in document content"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if focus != event.source:
            msg = "WEB: Ignoring because event source is not locusOfFocus"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        return False

    def on_selection_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:selection-changed accessibility events."""

        if self.utilities.event_is_browser_ui_autocomplete_noise_deprecated(event):
            msg = "WEB: Ignoring event believed to be browser UI autocomplete noise"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.event_is_browser_ui_page_switch(event):
            msg = "WEB: Ignoring event believed to be browser UI page switch"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if not self.utilities.in_document_content(event.source):
            msg = "WEB: Event source is not in document content"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if not self.utilities.in_document_content(focus_manager.get_manager().get_locus_of_focus()):
            msg = "WEB: Event ignored: locusOfFocus is not in document content"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if not self.utilities.event_is_from_locus_of_focus_document(event):
            msg = "WEB: Event ignored: Not from locus of focus document"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if AXObject.find_ancestor(event.source, AXUtilities.is_embedded):
            if self._in_focus_mode:
                # Because we cannot count on the app firing the right state-changed events
                # for descendants.
                AXObject.clear_cache(event.source,
                                     True,
                                     "Workaround for missing events on descendants.")
                msg = "WEB: Event source is embedded descendant and we're in focus mode"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return False

            msg = "WEB: Event source is embedded descendant and we're in browse mode"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.event_is_irrelevant_selection_changed_event(event):
            msg = "WEB: Event ignored: Irrelevant"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        obj, _offset = self.utilities.get_caret_context()
        ancestor = AXObject.get_common_ancestor(obj, event.source)
        if ancestor and self.utilities.is_text_block_element(ancestor):
            msg = "WEB: Ignoring: Common ancestor of context and event source is text block"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        return False

    def on_showing_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:showing accessibility events."""

        if event.detail1 and self.utilities.is_browser_ui_alert(event.source):
            msg = "WEB: Event handled: Presenting event source"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self.present_object(event.source, interrupt=True)
            return True

        if not self.utilities.in_document_content(event.source):
            msg = "WEB: Event source is not in document content"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        return True

    def on_text_attributes_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:text-attributes-changed accessibility events."""

        msg = "WEB: This event is is handled by the toolkit or default script."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return False

    def on_text_deleted(self, event: Atspi.Event) -> bool:
        """Callback for object:text-changed:delete accessibility events."""

        reason = AXUtilities.get_text_event_reason(event)
        if reason == TextEventReason.PAGE_SWITCH:
            msg = "WEB: Deletion is believed to be due to page switch"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if AXUtilities.is_live_region(event.source):
            msg = "WEB: Ignoring deletion from live region"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if not self.utilities.in_document_content(event.source):
            msg = "WEB: Event source is not in document content"
            debug.print_message(debug.LEVEL_INFO, msg, True)

            if reason == TextEventReason.UI_UPDATE:
                msg = "WEB: Ignoring event believed to be browser UI update"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return True

            return False

        if reason == TextEventReason.SPIN_BUTTON_VALUE_CHANGE:
            msg = "WEB: Ignoring: Event believed to be spin button value change"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if reason == TextEventReason.AUTO_DELETION:
            msg = "WEB: Ignoring event believed to be auto deletion"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        msg = "WEB: Clearing content cache due to text deletion"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self.utilities.clear_content_cache()

        if reason in (TextEventReason.DELETE, TextEventReason.BACKSPACE):
            msg = "WEB: Event believed to be due to editable text deletion"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if reason in [TextEventReason.TYPING, TextEventReason.TYPING_ECHOABLE]:
            msg = "WEB: Ignoring event believed to be due to text insertion"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        obj, _offset = self.utilities.get_caret_context(get_replicant=False)
        if obj and obj != event.source \
           and not AXObject.find_ancestor(obj, lambda x: x == event.source):
            tokens = ["WEB: Ignoring event because it isn't", obj, "or its ancestor"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        if not AXObject.is_valid(obj):
            if self.utilities.is_link(obj):
                msg = "WEB: Focused link deleted. Taking no further action."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return True

            obj, _offset = self.utilities.get_caret_context(get_replicant=True)
            if obj:
                focus_manager.get_manager().set_locus_of_focus(event, obj, notify_script=False)

        if not AXObject.is_valid(obj):
            msg = "WEB: Unable to get valid context object"
            debug.print_message(debug.LEVEL_INFO, msg, True)

        if not AXUtilities.is_editable(event.source) \
           and not self.utilities.is_content_editable_with_embedded_objects(event.source):
            msg = "WEB: Done processing non-editable source"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        return False

    def on_text_inserted(self, event: Atspi.Event) -> bool:
        """Callback for object:text-changed:insert accessibility events."""

        reason = AXUtilities.get_text_event_reason(event)
        if reason == TextEventReason.PAGE_SWITCH:
            msg = "WEB: Insertion is believed to be due to page switch"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if AXUtilities.is_live_region(event.source):
            if self.utilities.handle_as_live_region(event):
                msg = "WEB: Event to be handled as live region"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                self.live_region_manager.handleEvent(event)
                return True
            msg = "WEB: Ignoring because live region event not to be handled."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if reason == TextEventReason.CHILDREN_CHANGE:
            msg = "WEB: Ignoring: Event believed to be due to children change"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if not self.utilities.in_document_content(event.source):
            msg = "WEB: Event source is not in document content"
            debug.print_message(debug.LEVEL_INFO, msg, True)

            if reason == TextEventReason.UI_UPDATE:
                msg = "WEB: Ignoring event believed to be browser UI update"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return True

            return False

        if reason == TextEventReason.SPIN_BUTTON_VALUE_CHANGE:
            msg = "WEB: Ignoring: Event believed to be spin button value change"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if reason == TextEventReason.AUTO_INSERTION_PRESENTABLE:
            msg = "WEB: Ignoring: Event believed to be auto insertion"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        msg = "WEB: Clearing content cache due to text insertion"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self.utilities.clear_content_cache()

        document = self.utilities.get_top_level_document_for_object(event.source)
        if focus_manager.get_manager().focus_is_dead():
            msg = "WEB: Dumping cache: dead focus"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self.utilities.dump_cache(document, preserve_context=True)

            if AXUtilities.is_focused(event.source):
                msg = "WEB: Event handled: Setting locusOfFocus to event source"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                focus_manager.get_manager().set_locus_of_focus(None, event.source, force=True)
                return True

        if not self.utilities.treat_as_text_object(event.source):
            msg = "WEB: Ignoring: Event source is not a text object"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        source_is_focus = event.source == focus_manager.get_manager().get_locus_of_focus()
        if not AXUtilities.is_editable(event.source):
            if not source_is_focus:
                msg = "WEB: Done processing non-editable, non-locusOfFocus source"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return True

            if self.utilities.is_clickable_element(event.source):
                msg = "WEB: Event handled: Re-setting locusOfFocus to changed clickable"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                focus_manager.get_manager().set_locus_of_focus(None, event.source, force=True)
                return True

        if not source_is_focus and AXUtilities.is_text_input(event.source) \
           and AXUtilities.is_focused(event.source):
            msg = "WEB: Focused entry is not the locus of focus. Waiting for focus event."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        return False

    def on_text_selection_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:text-selection-changed accessibility events."""

        _reason = AXUtilities.get_text_event_reason(event)
        if self.utilities.event_is_browser_ui_noise_deprecated(event):
            msg = "WEB: Ignoring event believed to be browser UI noise"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if not self.utilities.in_document_content(event.source):
            msg = "WEB: Event source is not in document content"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        focus = focus_manager.get_manager().get_locus_of_focus()
        if not self.utilities.in_document_content(focus):
            msg = "WEB: Locus of focus is not in document content"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.event_is_autocomplete_noise_deprecated(event):
            msg = "WEB: Ignoring: Event believed to be autocomplete noise"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.event_is_spinner_noise_deprecated(event):
            msg = "WEB: Ignoring: Event believed to be spinner noise"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.event_is_for_non_navigable_text_object(event):
            msg = "WEB: Ignoring event for non-navigable text object"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if not self.utilities.treat_as_text_object(event.source):
            msg = "WEB: Ignoring: Event source is not a text object"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if event.source != focus and AXUtilities.is_text_input(event.source) \
           and AXUtilities.is_focused(event.source):
            msg = "WEB: Focused entry is not the locus of focus. Waiting for focus event."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.is_content_editable_with_embedded_objects(event.source):
            msg = "WEB: In content editable with embedded objects"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if self.get_structural_navigator().last_input_event_was_navigation_command():
            msg = "WEB: Ignoring: Last input event was structural navigation command."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        if self.get_table_navigator().last_input_event_was_navigation_command():
            msg = "WEB: Ignoring: Last input event was table navigation command."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        char = AXText.get_character_at_offset(event.source)[0]
        manager = input_event_manager.get_manager()
        if char == "\ufffc" and not manager.last_event_was_caret_selection() \
           and not manager.last_event_was_command():
            msg = "WEB: Ignoring: Not selecting and event offset is at embedded object"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        return False

    def on_window_activated(self, event: Atspi.Event) -> bool:
        """Callback for window:activate accessibility events."""

        msg = "WEB: Deferring to app/toolkit script"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return False

    def on_window_deactivated(self, event: Atspi.Event) -> bool:
        """Callback for window:deactivate accessibility events."""

        msg = "WEB: Clearing command state"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self._last_mouse_button_context = None, -1
        return False
