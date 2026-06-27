# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
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

# pylint: disable=too-many-public-methods
# pylint: disable=too-many-lines

"""Provides braille presentation support."""

from __future__ import annotations

import os
import time
from enum import Enum
from typing import TYPE_CHECKING, Any

from . import (
    braille,
    braille_monitor,
    braille_presenter_command_definitions,
    brltablenames,
    clipboard,
    dbus_service,
    debug,
    document_presenter,
    flat_review_presenter,
    focus_manager,
    gsettings_registry,
    guilabels,
    input_event,
    input_event_manager,
    messages,
    output_recorder,
    presentation_manager,
)
from .ax_text import AXText
from .ax_utilities import AXUtilities
from .ax_utilities_text import CaretSetReason
from .braille_generator import BrailleGeneratorContext
from .extension import Extension
from .generator import PresentationReason
from .orca_platform import tablesdir  # pylint: disable=import-error

if TYPE_CHECKING:
    from collections.abc import Callable

    import gi

    from .dbus_service import UInt32

    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

    from .braille_presenter_preferences_grid import BraillePreferencesGrid
    from .command import Command
    from .scripts import default


@gsettings_registry.get_registry().gsettings_enum(
    "org.gnome.Orca.VerbosityLevel",
    values={"brief": 0, "verbose": 1},
)
class VerbosityLevel(Enum):
    """Verbosity level enumeration."""

    BRIEF = 0
    VERBOSE = 1

    @property
    def string_name(self) -> str:
        """Returns the lowercase string name for this enum value."""

        return self.name.lower()


@gsettings_registry.get_registry().gsettings_enum(
    "org.gnome.Orca.BrailleIndicator",
    values={"none": 0, "dot7": 64, "dot8": 128, "dots78": 192},
)
class BrailleIndicator(Enum):
    """Braille indicator enumeration."""

    NONE = 0x00
    DOT7 = 0x40
    DOT8 = 0x80
    DOTS78 = 0xC0

    @property
    def string_name(self) -> str:
        """Returns the lowercase string name for this enum value."""

        return self.name.lower()


@gsettings_registry.get_registry().gsettings_enum(
    "org.gnome.Orca.ProgressBarVerbosity",
    values={"all": 0, "application": 1, "window": 2},
)
class ProgressBarVerbosity(Enum):
    """Progress bar verbosity level enumeration."""

    ALL = 0
    APPLICATION = 1
    WINDOW = 2


class PanDirection(Enum):
    """Braille panning direction."""

    LEFT = "left"
    RIGHT = "right"


@gsettings_registry.get_registry().gsettings_schema("org.gnome.Orca.Braille", name="braille")
class BraillePresenter(Extension):
    """Provides braille presentation support."""

    GROUP_LABEL = guilabels.BRAILLE

    _SCHEMA = "braille"

    KEY_ENABLED = "enabled"
    KEY_VERBOSITY_LEVEL = "verbosity-level"
    KEY_ROLENAME_STYLE = "rolename-style"
    KEY_PRESENT_MNEMONICS = "present-mnemonics"
    KEY_DISPLAY_ANCESTORS = "display-ancestors"
    KEY_BRAILLE_PROGRESS_BAR_UPDATES = "braille-progress-bar-updates"
    KEY_PROGRESS_BAR_BRAILLE_INTERVAL = "progress-bar-braille-interval"
    KEY_PROGRESS_BAR_BRAILLE_VERBOSITY = "progress-bar-braille-verbosity"
    KEY_CONTRACTED_BRAILLE = "contracted-braille"
    KEY_COMPUTER_BRAILLE_AT_CURSOR = "computer-braille-at-cursor"
    KEY_CONTRACTION_TABLE = "contraction-table"
    KEY_END_OF_LINE_INDICATOR = "end-of-line-indicator"
    KEY_WORD_WRAP = "word-wrap"
    KEY_FLASH_MESSAGES = "flash-messages"
    KEY_FLASH_MESSAGE_DURATION = "flash-message-duration"
    KEY_FLASH_MESSAGES_PERSISTENT = "flash-messages-persistent"
    KEY_FLASH_MESSAGES_DETAILED = "flash-messages-detailed"
    KEY_SELECTOR_INDICATOR = "selector-indicator"
    KEY_LINK_INDICATOR = "link-indicator"
    KEY_TEXT_ATTRIBUTES_INDICATOR = "text-attributes-indicator"
    KEY_MONITOR_CELL_COUNT = "monitor-cell-count"
    KEY_MONITOR_SHOW_DOTS = "monitor-show-dots"
    KEY_MONITOR_FOREGROUND = "monitor-foreground"
    KEY_MONITOR_BACKGROUND = "monitor-background"

    def _get_setting(self, key: str, gtype: str, default: Any) -> Any:
        """Returns the dconf value for key, or default if not in dconf."""

        return gsettings_registry.get_registry().layered_lookup(
            self._SCHEMA,
            key,
            gtype,
            default=default,
        )

    def __init__(self) -> None:
        self._command_names: dict[int, str] | None = None
        self._monitor: braille_monitor.BrailleMonitor | None = None
        self._monitor_enabled_override: bool | None = None
        self._progress_bar_cache: dict = {}
        self._output_recorder = output_recorder.OutputRecorder("braille")
        super().__init__()

    def _get_commands(self) -> list[Command]:
        """Returns commands for registration."""

        return braille_presenter_command_definitions.get_commands(self)

    def pan_braille_left(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
    ) -> bool:
        """Pans the braille display to the left."""

        return self._pan_braille(PanDirection.LEFT, script, event)

    def pan_braille_right(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
    ) -> bool:
        """Pans the braille display to the right."""

        return self._pan_braille(PanDirection.RIGHT, script, event)

    def _pan_braille(
        self,
        direction: PanDirection,
        script: default.Script | None,
        event: input_event.InputEvent | None = None,
    ) -> bool:
        """Pans braille in direction, asking the script only when at an edge."""

        if isinstance(event, input_event.KeyboardEvent) and not self.use_braille():
            msg = f"BRAILLE PRESENTER: panBraille{direction.name.title()} command requires braille"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        flat_review_result = self._pan_flat_review_braille(direction, script, event)
        if flat_review_result is not None:
            return flat_review_result

        did_pan = self.pan_left() if direction == PanDirection.LEFT else self.pan_right()
        if did_pan:
            return True

        if script is not None:
            script_result = script.handle_braille_pan_at_edge(direction)
            if script_result is not None:
                return script_result

        return self._handle_braille_pan_at_edge(direction, script, event)

    @staticmethod
    def _pan_flat_review_braille(
        direction: PanDirection,
        script: default.Script | None,
        event: input_event.InputEvent | None = None,
    ) -> bool | None:
        """Pans flat review braille if flat review is active."""

        flat_review = flat_review_presenter.get_presenter()
        if not flat_review.is_active():
            return None
        if script is None:
            return True
        if direction == PanDirection.LEFT:
            return flat_review.pan_braille_left(script, event)
        return flat_review.pan_braille_right(script, event)

    def _handle_braille_pan_at_edge(
        self,
        direction: PanDirection,
        script: default.Script | None,
        event: input_event.InputEvent | None = None,
    ) -> bool:
        """Handles braille panning when no more cells are available in the current line."""

        focus = focus_manager.get_manager().get_locus_of_focus()
        is_text_area = AXUtilities.is_editable(focus) or AXUtilities.is_terminal(focus)
        if not is_text_area:
            return True

        if direction == PanDirection.LEFT:
            start_offset = AXText.get_line_at_offset(focus)[1]
            moved_caret = False
            if start_offset > 0:
                moved_caret = AXUtilities.set_caret_offset_with_reason(
                    focus, start_offset - 1, CaretSetReason.BRAILLE_PANNING
                )

            # If we didn't move the caret and we're in a terminal, jump into flat review to
            # review the text. See http://bugzilla.gnome.org/show_bug.cgi?id=482294.
            if not moved_caret and script is not None and AXUtilities.is_terminal(focus):
                flat_review = flat_review_presenter.get_presenter()
                flat_review.go_start_of_line(script, event)
                flat_review.go_previous_character(script, event)
            return True

        end_offset = AXText.get_line_at_offset(focus)[2]
        if end_offset < AXText.get_character_count(focus):
            AXUtilities.set_caret_offset_with_reason(
                focus, end_offset, CaretSetReason.BRAILLE_PANNING
            )

        return True

    def go_home(
        self,
        _script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
    ) -> bool:
        """Returns to the component with focus."""

        if flat_review_presenter.get_presenter().is_active():
            flat_review_presenter.get_presenter().quit()
            return True

        presentation_manager.get_manager().interrupt_presentation()
        return braille.return_to_region_with_focus(event)

    def toggle_contracted_braille(
        self,
        _script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
    ) -> bool:
        """Toggles contracted braille."""

        braille.toggle_contracted_braille(event)
        return True

    def process_routing_key(
        self,
        _script: default.Script | None = None,
        event: input_event.BrailleEvent | None = None,
    ) -> bool:
        """Processes a cursor routing key."""

        # Don't kill flash here because it will restore the previous contents and
        # then process the routing key. If the contents accept a click action, this
        # would result in clicking on the link instead of clearing the flash message.
        presentation_manager.get_manager().interrupt_presentation(kill_flash=False)
        if event is None:
            return True
        braille.process_routing_key(event)
        return True

    def process_braille_cut_begin(
        self,
        script: default.Script | None = None,
        event: input_event.BrailleEvent | None = None,
    ) -> bool:
        """Clears the selection and moves the caret offset in the current text area."""

        if event is None:
            return True
        caret_context = braille.get_caret_context(event)
        if caret_context.offset < 0:
            return True

        presentation_manager.get_manager().interrupt_presentation()
        AXUtilities.clear_all_selected_text(caret_context.accessible)
        if script is not None:
            script.utilities.set_caret_offset(
                caret_context.accessible,
                caret_context.offset,
                reason=CaretSetReason.BRAILLE_CUT,
            )
        else:
            AXUtilities.set_caret_offset_with_reason(
                caret_context.accessible,
                caret_context.offset,
                CaretSetReason.BRAILLE_CUT,
            )
        return True

    def process_braille_cut_line(
        self,
        _script: default.Script | None = None,
        event: input_event.BrailleEvent | None = None,
    ) -> bool:
        """Extends the current text selection and copies it to the clipboard."""

        if event is None:
            return True
        caret_context = braille.get_caret_context(event)
        if caret_context.offset < 0:
            return True

        presentation_manager.get_manager().interrupt_presentation()
        start_offset = AXUtilities.get_selection_start_offset(caret_context.accessible)
        end_offset = AXUtilities.get_selection_end_offset(caret_context.accessible)
        if start_offset < 0 or end_offset < 0:
            caret_offset = AXText.get_caret_offset(caret_context.accessible)
            start_offset = min(caret_context.offset, caret_offset)
            end_offset = max(caret_context.offset, caret_offset)

        AXUtilities.set_selected_text(caret_context.accessible, start_offset, end_offset)
        text = AXUtilities.get_selected_text(caret_context.accessible)[0]
        clipboard.get_presenter().set_text(text)
        return True

    @dbus_service.command
    def toggle_monitor(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Toggles the braille monitor on and off."""

        tokens = [
            "BRAILLE PRESENTER: toggle_monitor. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if self.get_monitor_is_enabled():
            self.set_monitor_is_enabled(False)
            if script is not None and notify_user:
                presentation_manager.get_manager().present_message(
                    messages.BRAILLE_MONITOR_DISABLED,
                )
        else:
            self.set_monitor_is_enabled(True)
            if script is not None and notify_user:
                presentation_manager.get_manager().present_message(messages.BRAILLE_MONITOR_ENABLED)
        return True

    def get_table_names(self) -> dict[str, str]:
        """Returns table filenames mapped to localized display names."""

        return dict(brltablenames.TABLE_NAMES)

    @staticmethod
    def _build_command_names() -> dict[int, str]:
        """Return BrlTTY command names for presentation in the UI."""

        return braille_presenter_command_definitions.get_brltty_command_names()

    def get_command_names(self) -> dict[int, str]:
        """Returns a mapping of BrlTTY command IDs to user-visible labels."""

        if self._command_names is None:
            self._command_names = self._build_command_names()
        return dict(self._command_names)

    def create_preferences_grid(
        self,
        title_change_callback: Callable[[str], None] | None = None,
    ) -> BraillePreferencesGrid:
        """Returns the GtkGrid containing the preferences UI."""

        # pylint: disable-next=import-outside-toplevel
        from .braille_presenter_preferences_grid import BraillePreferencesGrid

        return BraillePreferencesGrid(self, title_change_callback)

    def _get_verbosity_is_detailed(self) -> bool:
        """Returns whether braille verbosity is set to detailed/verbose."""

        return self.get_verbosity_level() == "verbose"

    def _set_verbosity_is_detailed(self, value: bool) -> bool:
        """Sets braille verbosity to detailed/verbose if True, brief if False."""

        return self.set_verbosity_level("verbose" if value else "brief")

    def _get_use_abbreviated_rolenames(self) -> bool:
        """Returns whether abbreviated role names are used."""

        return self.get_rolename_style() == "brief"

    def _set_use_abbreviated_rolenames(self, value: bool) -> bool:
        """Sets whether abbreviated role names are used."""

        return self.set_rolename_style("brief" if value else "verbose")

    def _get_flash_duration_seconds(self) -> int:
        """Returns flash duration in seconds (converted from milliseconds)."""

        duration_ms = self.get_flash_message_duration()
        return max(1, duration_ms // 1000)

    def _set_flash_duration_seconds(self, value: int) -> None:
        """Sets flash duration in seconds (converts to milliseconds)."""

        duration_ms = value * 1000
        self.set_flash_message_duration(duration_ms)

    def use_braille(self) -> bool:
        """Returns whether braille is to be used."""

        result = self.get_braille_is_enabled() or self.get_monitor_is_enabled()
        if not result:
            msg = "BRAILLE PRESENTER: Braille is disabled."
            debug.print_message(debug.LEVEL_INFO, msg, True)
        return result

    @dbus_service.getter
    def get_monitor_is_enabled(self) -> bool:
        """Returns whether the braille monitor is enabled."""

        return self._monitor_enabled_override or False

    @dbus_service.setter
    def set_monitor_is_enabled(self, value: bool) -> bool:
        """Sets whether the braille monitor is enabled."""

        msg = f"BRAILLE PRESENTER: Setting enable braille monitor to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self._monitor_enabled_override = value
        if value:
            braille.set_monitor_cell_count(self.get_monitor_cell_count())
        else:
            braille.set_monitor_cell_count(0)
            self.destroy_monitor()
        return True

    @dbus_service.testing_command
    def set_log_file_for_testing(
        self,
        token: str = "",  # pylint: disable=unused-argument
        value: str = "",
        script: default.Script | None = None,  # pylint: disable=unused-argument
        event: input_event.InputEvent | None = None,  # pylint: disable=unused-argument
    ) -> bool:
        """Opens value for JSONL recording; an empty string closes any open file (test-only)."""

        msg = f"BRAILLE PRESENTER: Setting log file to {value!r}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return self._output_recorder.set_path(value)

    @gsettings_registry.get_registry().gsetting(
        key=KEY_MONITOR_CELL_COUNT,
        schema="braille",
        gtype="i",
        default=32,
        summary="Braille monitor cell count",
        migration_key="brailleMonitorCellCount",
    )
    @dbus_service.getter
    def get_monitor_cell_count(self) -> UInt32:
        """Returns the configured braille monitor cell count."""

        return self._get_setting(self.KEY_MONITOR_CELL_COUNT, "i", 32)

    @dbus_service.setter
    def set_monitor_cell_count(self, value: UInt32) -> bool:
        """Sets the braille monitor cell count."""

        msg = f"BRAILLE PRESENTER: Setting braille monitor cell count to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_MONITOR_CELL_COUNT,
            value,
        )
        if self.get_monitor_is_enabled():
            braille.set_monitor_cell_count(value)
        self.destroy_monitor()
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_MONITOR_SHOW_DOTS,
        schema="braille",
        gtype="b",
        default=False,
        summary="Show Unicode braille dots in braille monitor",
        migration_key="brailleMonitorShowDots",
    )
    @dbus_service.getter
    def get_monitor_show_dots(self) -> bool:
        """Returns whether the braille monitor shows Unicode braille dots."""

        return self._get_setting(self.KEY_MONITOR_SHOW_DOTS, "b", False)

    @dbus_service.setter
    def set_monitor_show_dots(self, value: bool) -> bool:
        """Sets whether the braille monitor shows Unicode braille dots."""

        msg = f"BRAILLE PRESENTER: Setting braille monitor show dots to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_MONITOR_SHOW_DOTS,
            value,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_MONITOR_FOREGROUND,
        schema="braille",
        gtype="s",
        default="#000000",
        summary="Braille monitor foreground color",
        migration_key="brailleMonitorForeground",
    )
    @dbus_service.getter
    def get_monitor_foreground(self) -> str:
        """Returns the braille monitor foreground color."""

        return self._get_setting(self.KEY_MONITOR_FOREGROUND, "s", "#000000")

    @dbus_service.setter
    def set_monitor_foreground(self, value: str) -> bool:
        """Sets the braille monitor foreground color."""

        msg = f"BRAILLE PRESENTER: Setting braille monitor foreground to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_MONITOR_FOREGROUND,
            value,
        )
        if self._monitor is not None:
            self._monitor.reapply_css(foreground=value)
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_MONITOR_BACKGROUND,
        schema="braille",
        gtype="s",
        default="#ffffff",
        summary="Braille monitor background color",
        migration_key="brailleMonitorBackground",
    )
    @dbus_service.getter
    def get_monitor_background(self) -> str:
        """Returns the braille monitor background color."""

        return self._get_setting(self.KEY_MONITOR_BACKGROUND, "s", "#ffffff")

    @dbus_service.setter
    def set_monitor_background(self, value: str) -> bool:
        """Sets the braille monitor background color."""

        msg = f"BRAILLE PRESENTER: Setting braille monitor background to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_MONITOR_BACKGROUND,
            value,
        )
        if self._monitor is not None:
            self._monitor.reapply_css(background=value)
        return True

    def present_regions(
        self,
        regions: list[braille.Region],
        focused_region: braille.Region | None,
        *,
        pan_to_cursor: bool = True,
        stop_flash: bool = True,
    ) -> None:
        """Build a line from regions and present it as a single braille line."""

        line = braille.Line()
        line.add_regions(regions)
        braille.display_line(
            line,
            focused_region,
            pan_to_cursor=pan_to_cursor,
            stop_flash=stop_flash,
        )

    def _build_generator_context(
        self,
        reason: PresentationReason | None = None,
        prior_obj: Atspi.Accessible | None = None,
        offset: int | None = None,
    ) -> BrailleGeneratorContext:
        """Builds the settings context for braille generators."""

        mgr = focus_manager.get_manager()
        active_mode, _obj = mgr.get_active_mode_and_object_of_interest()

        return BrailleGeneratorContext(
            enabled=self.use_braille(),
            verbose=self.use_verbose_braille(),
            focus=mgr.get_locus_of_focus(),
            in_focus_mode=document_presenter.get_presenter().get_in_focus_mode(),
            active_mode=active_mode,
            reason=reason or PresentationReason.FOCUS_CHANGE,
            prior_obj=prior_obj,
            offset=offset,
            leaving=False,
            ancestor_of=None,
            content_item=None,
            content_position=None,
            content_subject=None,
            resolved_role=None,
            role_subject=None,
            include_context=True,
            full_rolenames=self.use_full_rolenames(),
            display_ancestors=self.get_display_ancestors(),
            end_of_line_indicator=self.get_end_of_line_indicator_is_enabled(),
            present_mnemonics=self.get_present_mnemonics(),
            indicate_links=True,
        )

    def display_generated_contents(
        self,
        script: default.Script,
        contents: list[tuple[Atspi.Accessible, int, int, str]],
    ) -> None:
        """Generates braille for contents and displays the flattened regions."""

        if not self.use_braille():
            return

        context = self._build_generator_context()
        regions_list, focused_region = script.get_braille_generator().generate_contents(
            contents,
            context,
        )
        if not regions_list:
            return

        flattened_regions: list = []
        for regions in regions_list:
            flattened_regions.extend(regions)
        self.present_regions(flattened_regions, focused_region)

    def present_generated_braille(  # pylint: disable=too-many-arguments
        self,
        script: default.Script,
        obj: Atspi.Accessible,
        *,
        prior_obj: Atspi.Accessible | None = None,
        reason: PresentationReason | None = None,
        offset: int | None = None,
    ) -> None:
        """Generates braille for obj using the script's braille generator and displays it."""

        if not self.use_braille():
            return

        context = self._build_generator_context(
            reason,
            prior_obj=prior_obj,
            offset=offset,
        )
        generator = script.get_braille_generator()
        result, focused_region = generator.generate_braille(obj, context)
        if result:
            self.present_regions(list(result), focused_region)

    @gsettings_registry.get_registry().gsetting(
        key=KEY_ENABLED,
        schema="braille",
        gtype="b",
        default=True,
        summary="Enable braille output",
        migration_key="enableBraille",
    )
    @dbus_service.getter
    def get_braille_is_enabled(self) -> bool:
        """Returns whether braille is enabled."""

        return self._get_setting(self.KEY_ENABLED, "b", True)

    @dbus_service.setter
    def set_braille_is_enabled(self, value: bool) -> bool:
        """Sets whether braille is enabled."""

        if value == self.get_braille_is_enabled():
            return True

        msg = f"BRAILLE PRESENTER: Setting enable braille to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(self._SCHEMA, self.KEY_ENABLED, value)
        braille.set_enable_braille(value)

        if value:
            braille.init(input_event_manager.get_manager().process_braille_event)
        else:
            braille.shutdown()

        return True

    def use_verbose_braille(self) -> bool:
        """Returns whether the braille verbosity level is set to verbose."""

        return self.get_verbosity_level() == "verbose"

    @gsettings_registry.get_registry().gsetting(
        key=KEY_VERBOSITY_LEVEL,
        schema="braille",
        genum="org.gnome.Orca.VerbosityLevel",
        default="verbose",
        summary="Braille verbosity level (brief, verbose)",
        migration_key="brailleVerbosityLevel",
    )
    @dbus_service.getter
    def get_verbosity_level(self) -> str:
        """Returns the current braille verbosity level for object presentation."""

        return gsettings_registry.get_registry().layered_lookup(
            self._SCHEMA,
            self.KEY_VERBOSITY_LEVEL,
            "",
            genum="org.gnome.Orca.VerbosityLevel",
            default="verbose",
        )

    @dbus_service.setter
    def set_verbosity_level(self, value: str) -> bool:
        """Sets the braille verbosity level for object presentation."""

        try:
            level = VerbosityLevel[value.upper()]
        except KeyError:
            msg = f"BRAILLE PRESENTER: Invalid verbosity level: {value}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return False

        msg = f"BRAILLE PRESENTER: Setting verbosity level to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_VERBOSITY_LEVEL,
            level.string_name,
        )
        return True

    def use_full_rolenames(self) -> bool:
        """Returns whether full rolenames should be used."""

        return self.get_rolename_style() == "verbose"

    @gsettings_registry.get_registry().gsetting(
        key=KEY_ROLENAME_STYLE,
        schema="braille",
        genum="org.gnome.Orca.VerbosityLevel",
        default="verbose",
        summary="Braille rolename style (brief, verbose)",
        migration_key="brailleRolenameStyle",
    )
    @dbus_service.getter
    def get_rolename_style(self) -> str:
        """Returns the current rolename style for object presentation."""

        return gsettings_registry.get_registry().layered_lookup(
            self._SCHEMA,
            self.KEY_ROLENAME_STYLE,
            "",
            genum="org.gnome.Orca.VerbosityLevel",
            default="verbose",
        )

    @dbus_service.setter
    def set_rolename_style(self, value: str) -> bool:
        """Sets the current rolename style for object presentation."""

        try:
            level = VerbosityLevel[value.upper()]
        except KeyError:
            msg = f"BRAILLE PRESENTER: Invalid rolename style: {value}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return False

        msg = f"BRAILLE PRESENTER: Setting rolename style to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_ROLENAME_STYLE,
            level.string_name,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_PRESENT_MNEMONICS,
        schema="braille",
        gtype="b",
        default=True,
        summary="Present mnemonics on braille display",
        migration_key="displayObjectMnemonic",
    )
    @dbus_service.getter
    def get_present_mnemonics(self) -> bool:
        """Returns whether mnemonics are presented on the braille display."""

        return self._get_setting(self.KEY_PRESENT_MNEMONICS, "b", True)

    @dbus_service.setter
    def set_present_mnemonics(self, value: bool) -> bool:
        """Sets whether mnemonics are presented on the braille display."""

        msg = f"BRAILLE PRESENTER: Setting present mnemonics to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_PRESENT_MNEMONICS,
            value,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_DISPLAY_ANCESTORS,
        schema="braille",
        gtype="b",
        default=True,
        summary="Display ancestors of current object",
        migration_key="enableBrailleContext",
    )
    @dbus_service.getter
    def get_display_ancestors(self) -> bool:
        """Returns whether ancestors of the current object will be displayed."""

        return self._get_setting(self.KEY_DISPLAY_ANCESTORS, "b", True)

    @dbus_service.setter
    def set_display_ancestors(self, value: bool) -> bool:
        """Sets whether ancestors of the current object will be displayed."""

        msg = f"BRAILLE PRESENTER: Setting enable braille context to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_DISPLAY_ANCESTORS,
            value,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_BRAILLE_PROGRESS_BAR_UPDATES,
        schema="braille",
        gtype="b",
        default=False,
        summary="Show progress bar updates in braille",
        migration_key="brailleProgressBarUpdates",
    )
    @dbus_service.getter
    def get_braille_progress_bar_updates(self) -> bool:
        """Returns whether braille progress bar updates are enabled."""

        return self._get_setting(self.KEY_BRAILLE_PROGRESS_BAR_UPDATES, "b", False)

    @dbus_service.setter
    def set_braille_progress_bar_updates(self, value: bool) -> bool:
        """Sets whether braille progress bar updates are enabled."""

        msg = f"BRAILLE PRESENTER: Setting braille progress bar updates to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_BRAILLE_PROGRESS_BAR_UPDATES,
            value,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_PROGRESS_BAR_BRAILLE_INTERVAL,
        schema="braille",
        gtype="i",
        default=10,
        summary="Progress bar braille update interval in seconds",
        migration_key="progressBarBrailleInterval",
    )
    @dbus_service.getter
    def get_progress_bar_braille_interval(self) -> UInt32:
        """Returns the braille progress bar update interval in seconds."""

        return self._get_setting(self.KEY_PROGRESS_BAR_BRAILLE_INTERVAL, "i", 10)

    @dbus_service.setter
    def set_progress_bar_braille_interval(self, value: UInt32) -> bool:
        """Sets the braille progress bar update interval in seconds."""

        msg = f"BRAILLE PRESENTER: Setting progress bar braille interval to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_PROGRESS_BAR_BRAILLE_INTERVAL,
            value,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_PROGRESS_BAR_BRAILLE_VERBOSITY,
        schema="braille",
        genum="org.gnome.Orca.ProgressBarVerbosity",
        default="application",
        summary="Progress bar braille verbosity (all, application, window)",
        migration_key="progressBarBrailleVerbosity",
    )
    @dbus_service.getter
    def get_progress_bar_braille_verbosity(self) -> UInt32:
        """Returns the braille progress bar verbosity level."""

        nick = gsettings_registry.get_registry().layered_lookup(
            self._SCHEMA,
            self.KEY_PROGRESS_BAR_BRAILLE_VERBOSITY,
            "",
            genum="org.gnome.Orca.ProgressBarVerbosity",
            default="application",
        )
        return ProgressBarVerbosity[nick.upper()].value

    @dbus_service.setter
    def set_progress_bar_braille_verbosity(self, value: UInt32) -> bool:
        """Sets the braille progress bar verbosity level."""

        msg = f"BRAILLE PRESENTER: Setting progress bar braille verbosity to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        level = ProgressBarVerbosity(value)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_PROGRESS_BAR_BRAILLE_VERBOSITY,
            level.name.lower(),
        )
        return True

    def should_present_progress_bar_update(
        self,
        obj: Atspi.Accessible,
        percent: int | None,
        is_same_app: bool,
        is_same_window: bool,
    ) -> bool:
        """Returns True if the progress bar update should be brailled."""

        if not self.get_braille_progress_bar_updates():
            return False

        last_time, last_value = self._progress_bar_cache.get(id(obj), (0.0, None))
        if percent == last_value:
            return False

        if percent != 100:
            interval = int(time.time() - last_time)
            if interval < self.get_progress_bar_braille_interval():
                return False

        verbosity = self.get_progress_bar_braille_verbosity()
        if verbosity == ProgressBarVerbosity.ALL.value:
            present = True
        elif verbosity == ProgressBarVerbosity.APPLICATION.value:
            present = is_same_app
        elif verbosity == ProgressBarVerbosity.WINDOW.value:
            present = is_same_window
        else:
            present = True

        if present:
            self._progress_bar_cache[id(obj)] = (time.time(), percent)

        return present

    @gsettings_registry.get_registry().gsetting(
        key=KEY_CONTRACTED_BRAILLE,
        schema="braille",
        gtype="b",
        default=False,
        summary="Enable contracted braille",
        migration_key="enableContractedBraille",
    )
    @dbus_service.getter
    def get_contracted_braille_is_enabled(self) -> bool:
        """Returns whether contracted braille is enabled."""

        return self._get_setting(self.KEY_CONTRACTED_BRAILLE, "b", False)

    @dbus_service.setter
    def set_contracted_braille_is_enabled(self, value: bool) -> bool:
        """Sets whether contracted braille is enabled."""

        msg = f"BRAILLE PRESENTER: Setting enable contracted braille to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_CONTRACTED_BRAILLE,
            value,
        )
        braille.set_enable_contracted_braille(value)
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_COMPUTER_BRAILLE_AT_CURSOR,
        schema="braille",
        gtype="b",
        default=True,
        summary="Use computer braille at cursor position",
        migration_key="enableComputerBrailleAtCursor",
    )
    @dbus_service.getter
    def get_computer_braille_at_cursor_is_enabled(self) -> bool:
        """Returns whether computer braille is used at the cursor position."""

        return self._get_setting(self.KEY_COMPUTER_BRAILLE_AT_CURSOR, "b", True)

    @dbus_service.setter
    def set_computer_braille_at_cursor_is_enabled(self, value: bool) -> bool:
        """Sets whether computer braille is used at the cursor position."""

        msg = f"BRAILLE PRESENTER: Setting enable computer braille at cursor to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_COMPUTER_BRAILLE_AT_CURSOR,
            value,
        )
        braille.set_enable_computer_braille_at_cursor(value)
        return True

    def get_contraction_table_path(self) -> str:
        """Returns the current braille contraction table file path."""

        value = gsettings_registry.get_registry().layered_lookup(
            self._SCHEMA,
            self.KEY_CONTRACTION_TABLE,
            "s",
            default="",
        )
        return value or braille.get_default_contraction_table()

    @gsettings_registry.get_registry().gsetting(
        key=KEY_CONTRACTION_TABLE,
        schema="braille",
        gtype="s",
        default="",
        summary="Braille contraction table name",
        migration_key="brailleContractionTable",
    )
    @dbus_service.getter
    def get_contraction_table(self) -> str:
        """Returns the current braille contraction table name."""

        full_path = gsettings_registry.get_registry().layered_lookup(
            self._SCHEMA,
            self.KEY_CONTRACTION_TABLE,
            "s",
            default="",
        )
        if not full_path:
            return ""
        return os.path.splitext(os.path.basename(full_path))[0]

    @dbus_service.getter
    def get_available_contraction_tables(self) -> list[str]:
        """Returns a list of available contraction table names."""

        table_files = self._get_table_files()
        return [os.path.splitext(filename)[0] for filename in table_files]

    def get_contraction_tables_dict(self) -> dict[str, str]:
        """Returns a dictionary mapping display names to table file paths."""

        names = self.get_table_names()
        tables = {}
        for fname in self._get_table_files():
            display_name = names.get(fname, os.path.splitext(fname)[0])
            tables[display_name] = os.path.join(tablesdir, fname)
        return tables

    @dbus_service.setter
    def set_contraction_table(self, value: str) -> bool:
        """Sets the current braille contraction table."""

        table_files = self._get_table_files()
        base_name = os.path.splitext(value)[0]
        filename = None
        for table_file in table_files:
            if table_file.startswith(base_name + "."):
                filename = table_file
                break

        if not filename:
            msg = f"BRAILLE PRESENTER: Invalid contraction table: {value}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return False

        full_path = os.path.join(tablesdir, filename)
        return self.set_contraction_table_from_path(full_path)

    @staticmethod
    def _get_table_files() -> list[str]:
        """Returns a list of braille table filenames in the tables directory."""

        try:
            return [fname for fname in os.listdir(tablesdir) if fname[-4:] in (".utb", ".ctb")]
        except OSError:
            return []

    def set_contraction_table_from_path(self, file_path: str) -> bool:
        """Sets the current braille contraction table from a file path."""

        msg = f"BRAILLE PRESENTER: Setting contraction table to {file_path}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_CONTRACTION_TABLE,
            file_path,
        )
        braille.set_contraction_table(file_path)
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_END_OF_LINE_INDICATOR,
        schema="braille",
        gtype="b",
        default=True,
        summary="Show end-of-line indicator",
        migration_key="enableBrailleEOL",
    )
    @dbus_service.getter
    def get_end_of_line_indicator_is_enabled(self) -> bool:
        """Returns whether the end-of-line indicator is enabled."""

        return self._get_setting(self.KEY_END_OF_LINE_INDICATOR, "b", True)

    @dbus_service.setter
    def set_end_of_line_indicator_is_enabled(self, value: bool) -> bool:
        """Sets whether the end-of-line indicator is enabled."""

        msg = f"BRAILLE PRESENTER: Setting enable-eol to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_END_OF_LINE_INDICATOR,
            value,
        )
        braille.set_enable_eol(value)
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_WORD_WRAP,
        schema="braille",
        gtype="b",
        default=False,
        summary="Enable braille word wrap",
        migration_key="enableBrailleWordWrap",
    )
    @dbus_service.getter
    def get_word_wrap_is_enabled(self) -> bool:
        """Returns whether braille word wrap is enabled."""

        return self._get_setting(self.KEY_WORD_WRAP, "b", False)

    @dbus_service.setter
    def set_word_wrap_is_enabled(self, value: bool) -> bool:
        """Sets whether braille word wrap is enabled."""

        msg = f"BRAILLE PRESENTER: Setting enable word wrap to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(self._SCHEMA, self.KEY_WORD_WRAP, value)
        braille.set_enable_word_wrap(value)
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_FLASH_MESSAGES,
        schema="braille",
        gtype="b",
        default=True,
        summary="Enable braille flash messages",
        migration_key="enableFlashMessages",
    )
    @dbus_service.getter
    def get_flash_messages_are_enabled(self) -> bool:
        """Returns whether 'flash' messages (i.e. announcements) are enabled."""

        return self._get_setting(self.KEY_FLASH_MESSAGES, "b", True)

    @dbus_service.setter
    def set_flash_messages_are_enabled(self, value: bool) -> bool:
        """Sets whether 'flash' messages (i.e. announcements) are enabled."""

        msg = f"BRAILLE PRESENTER: Setting enable flash messages to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA, self.KEY_FLASH_MESSAGES, value
        )
        return True

    def get_flashtime_from_settings(self) -> int:
        """Returns flash message duration in milliseconds based on user settings."""

        if self.get_flash_messages_are_persistent():
            return -1
        return self.get_flash_message_duration()

    @gsettings_registry.get_registry().gsetting(
        key=KEY_FLASH_MESSAGE_DURATION,
        schema="braille",
        gtype="i",
        default=5000,
        summary="Flash message duration in milliseconds",
        migration_key="brailleFlashTime",
    )
    @dbus_service.getter
    def get_flash_message_duration(self) -> UInt32:
        """Returns flash message duration in milliseconds."""

        return self._get_setting(self.KEY_FLASH_MESSAGE_DURATION, "i", 5000)

    @dbus_service.setter
    def set_flash_message_duration(self, value: UInt32) -> bool:
        """Sets flash message duration in milliseconds."""

        msg = f"BRAILLE PRESENTER: Setting braille flash time to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_FLASH_MESSAGE_DURATION,
            value,
        )
        return True

    def set_selector_indicator_from_int(self, value: int) -> bool:
        """Sets the braille selector indicator from an int value."""

        msg = f"BRAILLE PRESENTER: Setting selector indicator to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        indicator = BrailleIndicator(value)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_SELECTOR_INDICATOR,
            indicator.string_name,
        )
        braille.set_selector_indicator(value)
        return True

    def set_link_indicator_from_int(self, value: int) -> bool:
        """Sets the braille link indicator from an int value."""

        msg = f"BRAILLE PRESENTER: Setting link indicator to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        indicator = BrailleIndicator(value)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_LINK_INDICATOR,
            indicator.string_name,
        )
        braille.set_link_indicator(value)
        return True

    def set_text_attributes_indicator_from_int(self, value: int) -> bool:
        """Sets the braille text attributes indicator from an int value."""

        msg = f"BRAILLE PRESENTER: Setting text attributes indicator to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        indicator = BrailleIndicator(value)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_TEXT_ATTRIBUTES_INDICATOR,
            indicator.string_name,
        )
        braille.set_text_attributes_indicator(value)
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_FLASH_MESSAGES_PERSISTENT,
        schema="braille",
        gtype="b",
        default=False,
        summary="Make flash messages persistent",
        migration_key="flashIsPersistent",
    )
    @dbus_service.getter
    def get_flash_messages_are_persistent(self) -> bool:
        """Returns whether 'flash' messages are persistent (as opposed to temporary)."""

        return self._get_setting(self.KEY_FLASH_MESSAGES_PERSISTENT, "b", False)

    @dbus_service.setter
    def set_flash_messages_are_persistent(self, value: bool) -> bool:
        """Sets whether 'flash' messages are persistent (as opposed to temporary)."""

        msg = f"BRAILLE PRESENTER: Setting flash messages are persistent to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_FLASH_MESSAGES_PERSISTENT,
            value,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key=KEY_FLASH_MESSAGES_DETAILED,
        schema="braille",
        gtype="b",
        default=True,
        summary="Use detailed flash messages",
        migration_key="flashIsDetailed",
    )
    @dbus_service.getter
    def get_flash_messages_are_detailed(self) -> bool:
        """Returns whether 'flash' messages are detailed (as opposed to brief)."""

        return self._get_setting(self.KEY_FLASH_MESSAGES_DETAILED, "b", True)

    @dbus_service.setter
    def set_flash_messages_are_detailed(self, value: bool) -> bool:
        """Sets whether 'flash' messages are detailed (as opposed to brief)."""

        msg = f"BRAILLE PRESENTER: Setting flash messages are detailed to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_FLASH_MESSAGES_DETAILED,
            value,
        )
        return True

    def _get_selector_indicator_as_int(self) -> int:
        """Returns the braille selector indicator as an int."""

        nick = gsettings_registry.get_registry().layered_lookup(
            self._SCHEMA,
            self.KEY_SELECTOR_INDICATOR,
            "",
            genum="org.gnome.Orca.BrailleIndicator",
            default="dots78",
        )
        value = BrailleIndicator[nick.upper()].value
        msg = f"BRAILLE PRESENTER: Getting selector indicator: {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return value

    @gsettings_registry.get_registry().gsetting(
        key=KEY_SELECTOR_INDICATOR,
        schema="braille",
        genum="org.gnome.Orca.BrailleIndicator",
        default="dots78",
        summary="Braille selector indicator style (none, dot7, dot8, dots78)",
        migration_key="brailleSelectorIndicator",
    )
    @dbus_service.getter
    def get_selector_indicator(self) -> str:
        """Returns the braille selector indicator style."""

        return gsettings_registry.get_registry().layered_lookup(
            self._SCHEMA,
            self.KEY_SELECTOR_INDICATOR,
            "",
            genum="org.gnome.Orca.BrailleIndicator",
            default="dots78",
        )

    @dbus_service.setter
    def set_selector_indicator(self, value: str) -> bool:
        """Sets the braille selector indicator style."""

        try:
            indicator = BrailleIndicator[value.upper()]
        except KeyError:
            msg = f"BRAILLE PRESENTER: Invalid selector indicator: {value}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return False

        msg = f"BRAILLE PRESENTER: Setting selector indicator to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_SELECTOR_INDICATOR,
            indicator.string_name,
        )
        braille.set_selector_indicator(indicator.value)
        return True

    def _get_link_indicator_as_int(self) -> int:
        """Returns the braille link indicator as an int."""

        nick = gsettings_registry.get_registry().layered_lookup(
            self._SCHEMA,
            self.KEY_LINK_INDICATOR,
            "",
            genum="org.gnome.Orca.BrailleIndicator",
            default="dots78",
        )
        value = BrailleIndicator[nick.upper()].value
        msg = f"BRAILLE PRESENTER: Getting link indicator: {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return value

    @gsettings_registry.get_registry().gsetting(
        key=KEY_LINK_INDICATOR,
        schema="braille",
        genum="org.gnome.Orca.BrailleIndicator",
        default="dots78",
        summary="Braille link indicator style (none, dot7, dot8, dots78)",
        migration_key="brailleLinkIndicator",
    )
    @dbus_service.getter
    def get_link_indicator(self) -> str:
        """Returns the braille link indicator style."""

        return gsettings_registry.get_registry().layered_lookup(
            self._SCHEMA,
            self.KEY_LINK_INDICATOR,
            "",
            genum="org.gnome.Orca.BrailleIndicator",
            default="dots78",
        )

    @dbus_service.setter
    def set_link_indicator(self, value: str) -> bool:
        """Sets the braille link indicator style."""

        try:
            indicator = BrailleIndicator[value.upper()]
        except KeyError:
            msg = f"BRAILLE PRESENTER: Invalid link indicator: {value}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return False

        msg = f"BRAILLE PRESENTER: Setting link indicator to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_LINK_INDICATOR,
            indicator.string_name,
        )
        braille.set_link_indicator(indicator.value)
        return True

    def _get_text_attributes_indicator_as_int(self) -> int:
        """Returns the braille text attributes indicator as an int."""

        nick = gsettings_registry.get_registry().layered_lookup(
            self._SCHEMA,
            self.KEY_TEXT_ATTRIBUTES_INDICATOR,
            "",
            genum="org.gnome.Orca.BrailleIndicator",
            default="none",
        )
        value = BrailleIndicator[nick.upper()].value
        msg = f"BRAILLE PRESENTER: Getting text attributes indicator: {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return value

    @gsettings_registry.get_registry().gsetting(
        key=KEY_TEXT_ATTRIBUTES_INDICATOR,
        schema="braille",
        genum="org.gnome.Orca.BrailleIndicator",
        default="none",
        summary="Braille text attributes indicator style (none, dot7, dot8, dots78)",
        migration_key="textAttributesBrailleIndicator",
    )
    @dbus_service.getter
    def get_text_attributes_indicator(self) -> str:
        """Returns the braille text attributes indicator style."""

        return gsettings_registry.get_registry().layered_lookup(
            self._SCHEMA,
            self.KEY_TEXT_ATTRIBUTES_INDICATOR,
            "",
            genum="org.gnome.Orca.BrailleIndicator",
            default="none",
        )

    @dbus_service.setter
    def set_text_attributes_indicator(self, value: str) -> bool:
        """Sets the braille text attributes indicator style."""

        try:
            indicator = BrailleIndicator[value.upper()]
        except KeyError:
            msg = f"BRAILLE PRESENTER: Invalid text attributes indicator: {value}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return False

        msg = f"BRAILLE PRESENTER: Setting text attributes indicator to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            self.KEY_TEXT_ATTRIBUTES_INDICATOR,
            indicator.string_name,
        )
        braille.set_text_attributes_indicator(indicator.value)
        return True

    def is_flash_active(self) -> bool:
        """Returns True if a flash message is currently being displayed."""

        return braille.is_flash_active()

    def kill_flash(self, restore_saved: bool = True) -> None:
        """Kills any flashed message currently being displayed."""

        braille.kill_flash(restore_saved)

    def present_message(
        self,
        message: str,
        restore_previous: bool = True,
        flash_time: int | None = None,
    ) -> None:
        """Displays a single line message in braille."""

        if not self.use_braille():
            return

        if flash_time is None:
            flash_time = self.get_flashtime_from_settings()

        if not restore_previous and flash_time:
            braille.kill_flash(restore_saved=False)

        braille.display_message(message, flash_time=flash_time)

    def pan_left(self) -> bool:
        """Pans the braille display left, returning True if the display moved."""

        if not self.use_braille():
            return False

        moved = braille.pan_left()
        if moved:
            braille.refresh(pan_to_cursor=False, stop_flash=False)
        return moved

    def pan_right(self) -> bool:
        """Pans the braille display right, returning True if the display moved."""

        if not self.use_braille():
            return False

        moved = braille.pan_right()
        if moved:
            braille.refresh(pan_to_cursor=False, stop_flash=False)
        return moved

    def refresh_braille(self, pan_to_cursor: bool = True) -> None:
        """Refreshes the braille display without rebuilding the line."""

        if not self.use_braille():
            return

        braille.refresh(pan_to_cursor=pan_to_cursor)

    def pan_to_beginning(self) -> None:
        """Pans the braille display all the way to the beginning of the line."""

        if not self.use_braille():
            return

        while braille.pan_left():
            pass
        braille.refresh(pan_to_cursor=False, stop_flash=True)

    def pan_to_end(self) -> None:
        """Pans the braille display all the way to the end of the line."""

        if not self.use_braille():
            return

        while braille.pan_right():
            pass
        braille.refresh(pan_to_cursor=False, stop_flash=True)

    def check_braille_setting(self) -> None:
        """Checks the braille setting and disables braille if necessary."""

        braille.check_braille_setting()

    def disable_braille(self) -> None:
        """Idles or shuts down braille output if enabled."""

        braille.disable_braille()

    def set_brlapi_priority(self, high: bool = False) -> None:
        """Sets the BrlAPI priority level.

        Args:
            high: If True, use high priority (for flat review). Otherwise use default.
        """

        if high:
            braille.set_brlapi_priority(braille.BRLAPI_PRIORITY_HIGH)
        else:
            braille.set_brlapi_priority()

    def update_monitor(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        cursor_cell: int,
        visible: str,
        visible_mask: str | None,
        display_size: int,
        full: str,
        full_mask: str | None,
    ) -> None:
        """Updates the braille monitor display, creating it on demand if enabled."""

        self._output_recorder.record(
            kind="braille",
            cursor_cell=cursor_cell,
            full=full,
            visible=visible,
            mask=full_mask,
        )
        if not self.get_monitor_is_enabled():
            return

        if braille.has_braille_device():
            cell_count = display_size
        else:
            cell_count = self.get_monitor_cell_count() or display_size
        if self._monitor is not None and len(self._monitor.cells) != cell_count:
            self.destroy_monitor()
        if self._monitor is None:
            self._monitor = braille_monitor.BrailleMonitor(
                cell_count,
                on_close=lambda: self.set_monitor_is_enabled(False),
                foreground=self.get_monitor_foreground(),
                background=self.get_monitor_background(),
            )
            self._monitor.show_all()  # pylint: disable=no-member

        if self.get_monitor_show_dots():
            visible = self._to_unicode_braille(visible)

        self._monitor.write_text(cursor_cell, visible, visible_mask)

    def _to_unicode_braille(self, text: str) -> str:
        """Convert text to Unicode braille dot pattern characters.

        Uses louis.charToDots() to map each character to its braille dot pattern,
        then converts to Unicode braille characters (U+2800 block).
        """

        try:
            import louis  # pylint: disable=import-outside-toplevel

            table = (
                self.get_contraction_table_path()
                if self.get_contracted_braille_is_enabled()
                else ""
            )
            if not table:
                table = "en-us-comp8.ctb"
            dots_str = louis.charToDots([table], text)
            return "".join(chr(0x2800 | (ord(c) & 0xFF)) for c in dots_str)
        except Exception:  # pylint: disable=broad-except
            return text

    def destroy_monitor(self) -> None:
        """Destroys the braille monitor widget if it exists."""

        if self._monitor is not None:
            self._monitor.destroy()
            self._monitor = None

    def init_braille(self) -> None:
        """Initializes braille if enabled."""

        braille.set_monitor_callback(self.update_monitor)
        if not self.get_braille_is_enabled():
            return

        braille.init(input_event_manager.get_manager().process_braille_event)
        self._sync_state_to_braille()

    def _sync_state_to_braille(self) -> None:
        """Pushes persisted dconf settings into the braille module's runtime state."""

        braille.set_enable_contracted_braille(self.get_contracted_braille_is_enabled())
        braille.set_contraction_table(self.get_contraction_table_path())
        braille.set_enable_computer_braille_at_cursor(
            self.get_computer_braille_at_cursor_is_enabled(),
        )
        braille.set_enable_eol(self.get_end_of_line_indicator_is_enabled())
        braille.set_enable_word_wrap(self.get_word_wrap_is_enabled())
        braille.set_selector_indicator(self._get_selector_indicator_as_int())
        braille.set_link_indicator(self._get_link_indicator_as_int())
        braille.set_text_attributes_indicator(self._get_text_attributes_indicator_as_int())

    def shutdown_braille(self) -> None:
        """Shuts down braille."""

        braille.shutdown()


_presenter: BraillePresenter = BraillePresenter()


def get_presenter() -> BraillePresenter:
    """Returns the Braille Presenter"""

    return _presenter
