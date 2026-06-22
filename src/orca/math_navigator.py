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

from functools import wraps
from typing import TYPE_CHECKING

from . import (
    braille,
    clipboard,
    command_manager,
    dbus_service,
    debug,
    document_presenter,
    focus_manager,
    guilabels,
    input_event,
    math_navigator_command_definitions,
    math_presenter,
    messages,
    presentation_manager,
    script_manager,
)
from .ax_utilities_math import AXUtilitiesMath
from .ax_utilities_text import CaretSetReason
from .extension import Extension

try:
    from . import libmathcat_py  # type: ignore[attr-defined]
except ImportError:
    libmathcat_py = None  # type: ignore[assignment]

if TYPE_CHECKING:
    import gi

    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

    from .scripts import default


class MathNavigator(Extension):
    """Provides interactive exploration of math expressions via MathCAT."""

    GROUP_LABEL = guilabels.KB_GROUP_MATH_NAVIGATION

    def __init__(self) -> None:
        self._active: bool = False
        self._math_object: Atspi.Accessible | None = None
        self._last_command: str = ""
        self._last_nav_id: tuple[str, int] = ("", 0)
        self._suspended: bool = True
        super().__init__()

    @staticmethod
    def navigation_command(func):
        """Decorator that logs the command, then dispatches to it."""

        @wraps(func)
        def wrapper(self, script, event=None, notify_user=True) -> bool:
            tokens = [
                "MATH NAVIGATOR:",
                func,
                "\nScript:",
                script,
                "\nEvent:",
                event,
                "\nnotify_user:",
                notify_user,
            ]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return func(self, script, notify_user)

        return wrapper

    @dbus_service.getter
    def is_active(self) -> bool:
        """Returns True if currently navigating a math expression."""

        return self._active

    @dbus_service.getter
    def get_supported_commands(self) -> list[str]:
        """Returns the MathCAT navigation commands supported by this navigator."""

        return math_navigator_command_definitions.get_supported_commands()

    def _register_commands(self) -> None:
        if libmathcat_py is None:
            msg = f"EXTENSION: {self.module_name} MathCAT not available. Skipping command setup."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        manager = command_manager.get_manager()
        for command in math_navigator_command_definitions.get_commands(self):
            manager.add_command(command)
        manager.set_group_suspended(self.GROUP_LABEL, True)

        msg = f"EXTENSION: {self.module_name} Commands set up."
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
    @navigation_command
    def enter_math_mode_command(self, script: default.Script, notify_user: bool = True) -> bool:
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
    @navigation_command
    def exit_math_mode(self, script: default.Script, notify_user: bool = True) -> bool:
        """Exits math navigation mode."""

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

        tokens = [
            "MATH NAVIGATOR: copy_to_clipboard. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

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
            script.utilities.set_caret_position(math_obj, 0, reason=CaretSetReason.MATH_NAVIGATION)

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
