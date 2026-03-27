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

"""Provides interactive math navigation via MathCAT."""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

from . import (
    braille,
    clipboard,
    cmdnames,
    command_manager,
    dbus_service,
    debug,
    document_presenter,
    focus_manager,
    guilabels,
    input_event,
    keybindings,
    math_presenter,
    messages,
    presentation_manager,
    script_manager,
)
from .ax_utilities_math import AXUtilitiesMath

try:
    from . import libmathcat_py  # type: ignore[attr-defined]
except ImportError:
    libmathcat_py = None  # type: ignore[assignment]

if TYPE_CHECKING:
    import gi

    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

    from .scripts import default


class MathNavigator:
    """Provides interactive exploration of math expressions via MathCAT."""

    _PLACE_MARKER_PREFIXES = ("MoveTo", "SetPlacemarker", "Read", "Describe")

    def __init__(self) -> None:
        self._active: bool = False
        self._math_object: Atspi.Accessible | None = None
        self._last_command: str = ""
        self._last_nav_id: tuple[str, int] = ("", 0)
        self._initialized: bool = False
        self._suspended: bool = True

        msg = "MATH NAVIGATOR: Registering D-Bus commands."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        controller = dbus_service.get_remote_controller()
        controller.register_decorated_module("MathNavigator", self)

    @dbus_service.getter
    def is_active(self) -> bool:
        """Returns True if currently navigating a math expression."""

        return self._active

    @dbus_service.getter
    def get_supported_commands(self) -> list[str]:
        """Returns the MathCAT navigation commands supported by this navigator."""

        commands = [mathcat_cmd for _name, mathcat_cmd, _desc, _kb in self._get_commands_data()]
        for digit in range(10):
            commands.extend(f"{prefix}{digit}" for prefix in self._PLACE_MARKER_PREFIXES)
        return commands

    @staticmethod
    def _get_commands_data() -> list[tuple[str, str, str, keybindings.KeyBinding | None]]:
        """Returns (command_name, mathcat_command, description, binding) for each command."""

        no_mod = keybindings.NO_MODIFIER_MASK
        ctrl = keybindings.CTRL_MODIFIER_MASK
        shift = keybindings.SHIFT_MODIFIER_MASK
        control_shift = keybindings.CTRL_SHIFT_MODIFIER_MASK
        kb = keybindings.KeyBinding

        return [
            ("math_move_next", "MoveNext", cmdnames.MATH_NAV_MOVE_NEXT, kb("Right", no_mod)),
            (
                "math_move_previous",
                "MovePrevious",
                cmdnames.MATH_NAV_MOVE_PREVIOUS,
                kb("Left", no_mod),
            ),
            ("math_zoom_in", "ZoomIn", cmdnames.MATH_NAV_ZOOM_IN, kb("Down", no_mod)),
            ("math_zoom_out", "ZoomOut", cmdnames.MATH_NAV_ZOOM_OUT, kb("Up", no_mod)),
            (
                "math_zoom_in_all",
                "ZoomInAll",
                cmdnames.MATH_NAV_ZOOM_IN_ALL,
                kb("Down", control_shift),
            ),
            (
                "math_zoom_out_all",
                "ZoomOutAll",
                cmdnames.MATH_NAV_ZOOM_OUT_ALL,
                kb("Up", control_shift),
            ),
            ("math_move_start", "MoveStart", cmdnames.MATH_NAV_MOVE_START, kb("Home", no_mod)),
            ("math_move_end", "MoveEnd", cmdnames.MATH_NAV_MOVE_END, kb("End", no_mod)),
            (
                "math_move_line_start",
                "MoveLineStart",
                cmdnames.MATH_NAV_MOVE_LINE_START,
                kb("Home", ctrl),
            ),
            ("math_move_line_end", "MoveLineEnd", cmdnames.MATH_NAV_MOVE_LINE_END, kb("End", ctrl)),
            (
                "math_move_column_start",
                "MoveColumnStart",
                cmdnames.MATH_NAV_MOVE_COLUMN_START,
                kb("Home", shift),
            ),
            (
                "math_move_column_end",
                "MoveColumnEnd",
                cmdnames.MATH_NAV_MOVE_COLUMN_END,
                kb("End", shift),
            ),
            (
                "math_move_cell_previous",
                "MoveCellPrevious",
                cmdnames.MATH_NAV_MOVE_CELL_PREVIOUS,
                kb("Left", ctrl),
            ),
            (
                "math_move_cell_next",
                "MoveCellNext",
                cmdnames.MATH_NAV_MOVE_CELL_NEXT,
                kb("Right", ctrl),
            ),
            ("math_move_cell_up", "MoveCellUp", cmdnames.MATH_NAV_MOVE_CELL_UP, kb("Up", ctrl)),
            (
                "math_move_cell_down",
                "MoveCellDown",
                cmdnames.MATH_NAV_MOVE_CELL_DOWN,
                kb("Down", ctrl),
            ),
            (
                "math_move_last_location",
                "MoveLastLocation",
                cmdnames.MATH_NAV_MOVE_LAST_LOCATION,
                kb("BackSpace", no_mod),
            ),
            (
                "math_toggle_zoom_lock_up",
                "ToggleZoomLockUp",
                cmdnames.MATH_NAV_TOGGLE_ZOOM_LOCK_UP,
                kb("Up", shift),
            ),
            (
                "math_toggle_zoom_lock_down",
                "ToggleZoomLockDown",
                cmdnames.MATH_NAV_TOGGLE_ZOOM_LOCK_DOWN,
                kb("Down", shift),
            ),
            (
                "math_toggle_speech_mode",
                "ToggleSpeakMode",
                cmdnames.MATH_NAV_TOGGLE_SPEECH_MODE,
                kb("space", shift),
            ),
            (
                "math_read_previous",
                "ReadPrevious",
                cmdnames.MATH_NAV_READ_PREVIOUS,
                kb("Left", shift),
            ),
            ("math_read_next", "ReadNext", cmdnames.MATH_NAV_READ_NEXT, kb("Right", shift)),
            (
                "math_read_current",
                "ReadCurrent",
                cmdnames.MATH_NAV_READ_CURRENT,
                kb("space", no_mod),
            ),
            (
                "math_read_cell_current",
                "ReadCellCurrent",
                cmdnames.MATH_NAV_READ_CELL_CURRENT,
                kb("space", ctrl),
            ),
            (
                "math_describe_previous",
                "DescribePrevious",
                cmdnames.MATH_NAV_DESCRIBE_PREVIOUS,
                kb("Left", control_shift),
            ),
            (
                "math_describe_next",
                "DescribeNext",
                cmdnames.MATH_NAV_DESCRIBE_NEXT,
                kb("Right", control_shift),
            ),
            (
                "math_describe_current",
                "DescribeCurrent",
                cmdnames.MATH_NAV_DESCRIBE_CURRENT,
                kb("space", control_shift),
            ),
            ("math_where_am_i", "WhereAmI", cmdnames.MATH_NAV_WHERE_AM_I, None),
            ("math_where_am_i_all", "WhereAmIAll", cmdnames.MATH_NAV_WHERE_AM_I_ALL, None),
            ("math_exit", "Exit", cmdnames.MATH_NAV_EXIT, kb("Escape", no_mod)),
            ("math_copy", "Copy", cmdnames.MATH_NAV_COPY, None),
        ]

    # pylint: disable-next=too-many-locals
    def set_up_commands(self) -> None:
        """Sets up the math navigation commands with CommandManager."""

        if self._initialized:
            return
        self._initialized = True

        manager = command_manager.get_manager()
        group_label = guilabels.KB_GROUP_MATH_NAVIGATION

        for name, mathcat_cmd, description, binding in self._get_commands_data():
            if mathcat_cmd == "Exit":
                handler = self.exit_math_mode
            elif mathcat_cmd == "Copy":
                handler = self.copy_to_clipboard
            else:
                handler = partial(self._execute_command, mathcat_cmd)
            manager.add_command(
                command_manager.KeyboardCommand(
                    name,
                    handler,
                    group_label,
                    description,
                    desktop_keybinding=binding,
                    laptop_keybinding=binding,
                ),
            )

        no_mod = keybindings.NO_MODIFIER_MASK
        ctrl = keybindings.CTRL_MODIFIER_MASK
        shift = keybindings.SHIFT_MODIFIER_MASK
        control_shift = keybindings.CTRL_SHIFT_MODIFIER_MASK
        marker_types = [
            (no_mod, self._PLACE_MARKER_PREFIXES[0], cmdnames.MATH_NAV_GOTO_PLACE_MARKER),
            (ctrl, self._PLACE_MARKER_PREFIXES[1], cmdnames.MATH_NAV_SET_PLACE_MARKER),
            (shift, self._PLACE_MARKER_PREFIXES[2], cmdnames.MATH_NAV_READ_PLACE_MARKER),
            (
                control_shift,
                self._PLACE_MARKER_PREFIXES[3],
                cmdnames.MATH_NAV_DESCRIBE_PLACE_MARKER,
            ),
        ]

        for digit in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]:
            for modifier_mask, cmd_prefix, description in marker_types:
                cmd_name = f"math_{cmd_prefix.lower()}_{digit}"
                manager.add_command(
                    command_manager.KeyboardCommand(
                        cmd_name,
                        partial(self._execute_command, f"{cmd_prefix}{digit}"),
                        group_label,
                        description,
                        desktop_keybinding=keybindings.KeyBinding(digit, modifier_mask),
                        laptop_keybinding=keybindings.KeyBinding(digit, modifier_mask),
                    ),
                )

        command_manager.get_manager().set_group_suspended(
            guilabels.KB_GROUP_MATH_NAVIGATION,
            True,
        )

        manager.add_command(
            command_manager.KeyboardCommand(
                "math_enter",
                self.enter_math_mode_command,
                group_label,
                cmdnames.MATH_NAV_ENTER,
                is_group_toggle=True,
            ),
        )

        msg = "MATH NAVIGATOR: Commands set up."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def _is_active_script(self, script):
        active_script = script_manager.get_manager().get_active_script()
        if active_script == script:
            return True

        tokens = ["MATH NAVIGATOR:", script, "is not the active script", active_script]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return False

    def suspend_commands(
        self,
        script: default.Script,
        suspended: bool,
        reason: str = "",
    ) -> None:
        """Suspends math navigation independent of the enabled setting."""

        if not (script and self._is_active_script(script)):
            return

        msg = f"MATH NAVIGATOR: Commands suspended: {suspended}"
        if reason:
            msg += f": {reason}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        self._suspended = suspended
        command_manager.get_manager().set_group_suspended(
            guilabels.KB_GROUP_MATH_NAVIGATION,
            suspended,
        )

    def enter_math_mode(self, obj: Atspi.Accessible) -> bool:
        """Enters math navigation mode for the expression containing obj."""

        already_active = self._active
        if not already_active and not self._enter(obj):
            return False

        if not already_active:
            presentation_manager.get_manager().present_message(
                messages.MATH_NAVIGATION_ENTERED,
            )

        math_obj = self._math_object or obj
        speech = math_presenter.get_presenter().get_speech_for_math(math_obj)
        if speech:
            presentation_manager.get_manager().speak_accessible_text(math_obj, speech)

        return True

    @dbus_service.command
    def enter_math_mode_command(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Enters math navigation mode if the current focus is on math."""

        obj = focus_manager.get_manager().get_locus_of_focus()
        if not (math_root := AXUtilitiesMath.find_math_root(obj)):
            if notify_user:
                presentation_manager.get_manager().present_message(
                    messages.MATH_NAVIGATION_NOT_IN_MATH,
                )
            return True

        document_presenter.get_presenter().enter_math_navigation(script, math_root)
        return True

    @dbus_service.command
    def exit_math_mode(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Exits math navigation mode."""

        tokens = [
            "MATH NAVIGATOR: exit_math_mode. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if not self._active:
            return False

        self._do_command("Exit")
        self.reset(script)
        document_presenter.get_presenter().exit_math_navigation(script)

        if notify_user:
            presentation_manager.get_manager().present_message(
                messages.MATH_NAVIGATION_EXITED,
            )
        return True

    @dbus_service.command
    def copy_to_clipboard(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Copies the current math navigation node to the clipboard."""

        if not self._active:
            return False

        content = math_presenter.get_presenter().get_navigation_content_for_copy()
        if not content:
            return False

        clipboard.get_presenter().set_text(content)
        return True

    @dbus_service.parameterized_command
    def execute_mathcat_command(
        self,
        mathcat_command: str,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Executes a MathCAT navigation command. Use get_supported_commands for valid values."""

        if script is None:
            return False
        return self._execute_command(mathcat_command, script, event, notify_user)

    def _execute_command(
        self,
        mathcat_command: str,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Executes a MathCAT navigation command and presents the result."""

        tokens = [
            f"MATH NAVIGATOR: _execute_command: {mathcat_command}. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if not self._active:
            return False

        at_boundary = (
            mathcat_command in self._MOVEMENT_COMMANDS
            and mathcat_command == self._last_command
            and self._last_nav_id == self._get_nav_location()
        )

        speech = self._do_command(mathcat_command)
        self._last_command = mathcat_command
        self._last_nav_id = self._get_nav_location()

        if notify_user:
            self._present(speech, mathcat_command)
            if at_boundary:
                presentation_manager.get_manager().present_message(
                    messages.MATH_NAVIGATION_ESCAPE_HINT,
                )
        return True

    def _enter(self, math_root: Atspi.Accessible) -> bool:
        """Enters math navigation for the given math root element."""

        mathml = AXUtilitiesMath.get_mathml(math_root)
        if not mathml:
            return False

        if not math_presenter.get_presenter().is_available():
            return False

        try:
            libmathcat_py.SetMathML(mathml)
        except OSError as err:
            msg = f"MATH NAVIGATOR: SetMathML failed: {err}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        self._math_object = math_root
        self._active = True
        self._last_command = ""
        self._last_nav_id = ("", 0)

        focus_manager.get_manager().emit_region_changed(
            math_root,
            mode=focus_manager.MATH_NAVIGATOR,
        )

        msg = "MATH NAVIGATOR: Entered math navigation."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    def reset(self, script: default.Script) -> None:
        """Resets navigator state and positions the caret on the math object."""

        math_obj = self._math_object
        self._active = False
        self._math_object = None
        self._last_command = ""
        self._last_nav_id = ("", 0)

        if math_obj is not None:
            script.utilities.set_caret_position(math_obj, 0)

        msg = "MATH NAVIGATOR: Exited math navigation."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def _get_nav_location(self) -> tuple[str, int]:
        """Returns the current navigation location as (id, offset)."""

        try:
            return libmathcat_py.GetNavigationMathMLId()
        except OSError:
            return ("", 0)

    def _do_command(self, command: str) -> str:
        """Sends a navigation command to MathCAT and returns the speech result."""

        try:
            speech = libmathcat_py.DoNavigateCommand(command)
        except OSError as err:
            msg = f"MATH NAVIGATOR: DoNavigateCommand({command}) failed: {err}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return ""

        msg = f"MATH NAVIGATOR: {command} -> {speech}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return speech

    _MOVEMENT_COMMANDS = frozenset(
        (
            "MoveNext",
            "MovePrevious",
            "MoveStart",
            "MoveEnd",
            "MoveLineStart",
            "MoveLineEnd",
            "MoveColumnStart",
            "MoveColumnEnd",
            "MoveCellPrevious",
            "MoveCellNext",
            "MoveCellUp",
            "MoveCellDown",
            "MoveLastLocation",
            "ZoomIn",
            "ZoomOut",
            "ZoomInAll",
            "ZoomOutAll",
        )
    )

    _INFORMATIONAL_COMMANDS = frozenset(
        (
            "WhereAmI",
            "WhereAmIAll",
            "ToggleZoomLockUp",
            "ToggleZoomLockDown",
            "ToggleSpeakMode",
        )
    )

    def _present(self, speech: str, command: str = "") -> None:
        """Presents the navigation result via speech and braille."""

        if speech:
            if command in self._INFORMATIONAL_COMMANDS:
                presentation_manager.get_manager().present_message(speech)
            else:
                presentation_manager.get_manager().speak_accessible_text(
                    self._math_object,
                    speech,
                )

        try:
            braille_string = libmathcat_py.GetNavigationBraille()
        except OSError:
            braille_string = ""

        if braille_string and self._math_object is not None:
            region = braille.Component(
                self._math_object,
                braille_string,
                contracted=False,
            )
            line = braille.Line(region)
            braille.display_line(line, region)


_navigator: MathNavigator = MathNavigator()


def get_navigator() -> MathNavigator:
    """Returns the Math Navigator"""

    return _navigator
