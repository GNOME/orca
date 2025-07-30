# Orca
#
# Copyright 2016 Igalia, S.L.
#
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

# pylint: disable=too-many-lines
# pylint: disable=too-few-public-methods
# pylint: disable=wrong-import-position

"""Utilities for obtaining sounds to be presented for objects."""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__        = "$Id:$"
__version__   = "$Revision:$"
__date__      = "$Date:$"
__copyright__ = "Copyright (c) 2016 Igalia, S.L."
__license__   = "LGPL"

import os
from typing import TYPE_CHECKING, Any

import gi
gi.require_version('Atspi', '2.0')
from gi.repository import Atspi

from . import debug
from . import generator
from . import object_properties
from . import settings_manager
from .ax_object import AXObject
from .ax_utilities import AXUtilities
from .ax_value import AXValue

if TYPE_CHECKING:
    from . import script

class Icon:
    """Sound file representing a particular aspect of an object."""

    def __init__(self, location: str, filename: str) -> None:
        self.path = os.path.join(location, filename)
        msg = f"SOUND GENERATOR: Looking for '{filename}' in {location}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def __str__(self) -> str:
        return f'Icon(path: {self.path}, is_valid: {self.is_valid()})'

    def is_valid(self) -> bool:
        """Returns True if the path associated with this icon is valid."""
        return os.path.isfile(self.path)

class Tone:
    """Tone representing a particular aspect of an object."""

    SINE_WAVE = 0
    SQUARE_WAVE = 1
    SAW_WAVE = 2
    TRIANGLE_WAVE = 3
    SILENCE = 4
    WHITE_UNIFORM_NOISE = 5
    PINK_NOISE = 6
    SINE_WAVE_USING_TABLE = 7
    PERIODIC_TICKS = 8
    WHITE_GAUSSIAN_NOISE = 9
    RED_NOISE = 10
    INVERTED_PINK_NOISE = 11
    INVERTED_RED_NOISE = 12

    def __init__(
        self,
        duration: float,
        frequency: int,
        volume_multiplier: float = 1,
        wave: int = SINE_WAVE
    ) -> None:
        self.duration = duration
        self.frequency = min(max(0, frequency), 20000)
        self.volume = settings_manager.get_manager().get_setting('soundVolume') * volume_multiplier
        self.wave = wave

    def __str__(self) -> str:
        return (
            f'Tone(duration: {self.duration}, '
            f'frequency: {self.frequency}, '
            f'volume: {self.volume}, '
            f'wave: {self.wave})'
        )

class SoundGenerator(generator.Generator):
    """Takes accessible objects and produces the sound(s) to be played."""

    def __init__(self, script: script.Script) -> None:
        super().__init__(script, "sound")
        prefs_dir = settings_manager.get_manager().get_prefs_dir()
        self._sounds = os.path.join(prefs_dir or "", "sounds")

    def _convert_filename_to_icon(self, filename: str) -> Icon | None:
        icon = Icon(self._sounds, filename)
        if icon.is_valid():
            return icon

        return None

    def generate_sound(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Returns an array of sounds for the complete presentation of obj."""

        if not settings_manager.get_manager().get_setting("enableSound"):
            debug.print_message(debug.LEVEL_INFO, "SOUND GENERATOR: Generation disabled", True)
            return []

        return self.generate(obj, **args)

    #####################################################################
    #                                                                   #
    # State information                                                 #
    #                                                                   #
    #####################################################################

    def _generate_state_sensitive(self, obj: Atspi.Accessible, **_args) -> list[Any]:
        """Returns an array of sounds indicating obj is grayed out."""

        if not settings_manager.get_manager().get_setting("playSoundForState"):
            return []

        if AXUtilities.is_sensitive(obj):
            return []

        filename = object_properties.STATE_INSENSITIVE_SPEECH
        result = self._convert_filename_to_icon(filename)
        if result:
            return [result]

        return []

    def _generate_state_checked(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Returns an array of sounds indicating the checked state of obj."""

        if not settings_manager.get_manager().get_setting("playSoundForState"):
            return []

        filenames = super()._generate_state_checked(obj, **args)
        if filenames and filenames[0]:
            result = self._convert_filename_to_icon(filenames[0])
            if result:
                return [result]

        return []

    def _generate_has_click_action(self, obj: Atspi.Accessible, **_args) -> list[Any]:
        """Returns an array of sounds indicating obj is clickable."""

        if not settings_manager.get_manager().get_setting("playSoundForState"):
            return []

        if not self._script.utilities.is_clickable_element(obj):
            return []

        filename = object_properties.STATE_CLICKABLE_SOUND
        result = self._convert_filename_to_icon(filename)
        if result:
            return [result]

        return []

    def _generate_state_expanded(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Returns an array of sounds indicating the expanded state of obj."""

        if not settings_manager.get_manager().get_setting("playSoundForState"):
            return []

        filenames = super()._generate_state_expanded(obj, **args)
        if filenames and filenames[0]:
            result = self._convert_filename_to_icon(filenames[0])
            if result:
                return [result]

        return []

    def _generate_state_invalid(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Returns an array of sounds indicating the invalid state of obj."""

        if not settings_manager.get_manager().get_setting("playSoundForState"):
            return []

        filenames = super()._generate_state_invalid(obj, **args)
        if filenames and filenames[0]:
            result = self._convert_filename_to_icon(filenames[0])
            if result:
                return [result]

        return []

    def _generate_has_long_description(self, obj: Atspi.Accessible, **_args) -> list[Any]:
        """Returns an array of sounds indicating obj has a longdesc."""

        if not settings_manager.get_manager().get_setting("playSoundForState"):
            return []

        if not self._script.utilities.has_long_desc(obj):
            return []

        filename = object_properties.STATE_HAS_LONGDESC_SOUND
        result = self._convert_filename_to_icon(filename)
        if result:
            return [result]

        return []

    def _generate_state_multiselectable(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Returns an array of sounds indicating obj is multiselectable."""

        if not settings_manager.get_manager().get_setting("playSoundForState"):
            return []

        filenames = super()._generate_state_multiselectable(obj, **args)
        if filenames and filenames[0]:
            result = self._convert_filename_to_icon(filenames[0])
            if result:
                return [result]

        return []

    def _generate_state_selected_for_radio_button(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Returns an array of sounds indicating the selected state of obj."""

        if not settings_manager.get_manager().get_setting("playSoundForState"):
            return []

        filenames = super()._generate_state_selected_for_radio_button(obj, **args)
        if filenames and filenames[0]:
            result = self._convert_filename_to_icon(filenames[0])
            if result:
                return [result]

        return []

    def _generate_state_read_only(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Returns an array of sounds indicating obj is read only."""

        if not settings_manager.get_manager().get_setting("playSoundForState"):
            return []

        filenames = super()._generate_state_read_only(obj, **args)
        if filenames and filenames[0]:
            result = self._convert_filename_to_icon(filenames[0])
            if result:
                return [result]

        return []

    def _generate_state_required(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Returns an array of sounds indicating obj is required."""

        if not settings_manager.get_manager().get_setting("playSoundForState"):
            return []

        filenames = super()._generate_state_required(obj, **args)
        if filenames and filenames[0]:
            result = self._convert_filename_to_icon(filenames[0])
            if result:
                return [result]

        return []

    def _generate_state_checked_for_switch(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Returns an array of sounds indicating the on/off state of obj."""

        if not settings_manager.get_manager().get_setting("playSoundForState"):
            return []

        filenames = super()._generate_state_checked_for_switch(obj, **args)
        if filenames and filenames[0]:
            result = self._convert_filename_to_icon(filenames[0])
            if result:
                return [result]

        return []

    def _generate_state_pressed(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Returns an array of sounds indicating the toggled state of obj."""

        if not settings_manager.get_manager().get_setting("playSoundForState"):
            return []

        filenames = super()._generate_state_pressed(obj, **args)
        if filenames and filenames[0]:
            result = self._convert_filename_to_icon(filenames[0])
            if result:
                return [result]

        return []

    def _generate_visited_state(self, obj: Atspi.Accessible, **_args) -> list[Any]:
        """Returns an array of sounds indicating the visited state of obj."""

        if not settings_manager.get_manager().get_setting("playSoundForState"):
            return []

        if not AXUtilities.is_visited(obj):
            return []

        filename = object_properties.STATE_VISITED_SOUND
        result = self._convert_filename_to_icon(filename)
        if result:
            return [result]

        return []

    def _generate_value_as_percentage(self, obj: Atspi.Accessible, **_args) -> list[Any]:
        """Returns an array of sounds reflecting the percentage of obj."""

        if not settings_manager.get_manager().get_setting('playSoundForValue'):
            return []

        percent = AXValue.get_value_as_percent(obj)
        if percent is None:
            return []

        return []

    def _generate_progress_bar_value(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Returns an array of sounds representing the progress bar value."""

        if args.get('isProgressBarUpdate'):
            if not self._should_present_progress_bar_update(obj, **args):
                return []
        elif not settings_manager.get_manager().get_setting('playSoundForValue'):
            return []

        percent = AXValue.get_value_as_percent(obj)
        if percent is None:
            return []

        # To better indicate the progress completion.
        if percent >= 99:
            duration = 1.0
        else:
            duration = 0.075

        # Reduce volume as pitch increases.
        volume_multiplier = 1 - (percent / 120)

        # Adjusting so that the initial beeps are not too deep.
        if percent < 7:
            frequency = int(98 + percent * 5.4)
        else:
            frequency = int(percent * 22)

        return [Tone(duration, frequency, volume_multiplier, Tone.SINE_WAVE)]

    def _get_progress_bar_update_interval(self) -> int:
        interval = settings_manager.get_manager().get_setting('progressBarBeepInterval')
        if interval is None:
            return super()._get_progress_bar_update_interval()

        return int(interval)

    def _should_present_progress_bar_update(self, obj: Atspi.Accessible, **args) -> bool:
        if not settings_manager.get_manager().get_setting('beepProgressBarUpdates'):
            return False

        return super()._should_present_progress_bar_update(obj, **args)

    def _generate_position_in_set(self, _obj: Atspi.Accessible, **_args) -> list[Any]:
        """Returns an array of sounds reflecting the set position of obj."""

        if not settings_manager.get_manager().get_setting('playSoundForPositionInSet'):
            return []

        # TODO: Implement the result.
        # index = AXUtilities.get_position_in_set(obj)
        # total = AXUtilities.get_set_size(obj)
        # percent = int((index / total) * 100)

        return []

    def _generate_accessible_role(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Returns an array of sounds indicating the role of obj."""

        if not settings_manager.get_manager().get_setting('playSoundForRole'):
            return []

        role = args.get("role", AXObject.get_role(obj))
        filenames = [Atspi.role_get_name(role).replace(" ", "-")]
        if filenames and filenames[0]:
            result = self._convert_filename_to_icon(filenames[0])
            if result:
                return [result]

        return []

#########################################################################################

    def _generate_default_prefix(self, _obj: Atspi.Accessible, **_args) -> list[Any]:
        """Provides the default/role-agnostic information to present before obj."""

        return []

    def _generate_default_presentation(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Provides a default/role-agnostic presentation of obj."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_default_suffix(self, _obj: Atspi.Accessible, **_args) -> list[Any]:
        """Provides the default/role-agnostic information to present after obj."""

        return []

    def _generate_accelerator_label(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the accelerator-label role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_alert(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the alert role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_animation(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the animation role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_application(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the application role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_arrow(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the arrow role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_article(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the article role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_article_in_feed(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the article role when the article is in a feed."""

        return self._generate_default_presentation(obj, **args)

    def _generate_audio(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the audio role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_autocomplete(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the autocomplete role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_block_quote(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the block-quote role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_calendar(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the calendar role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_canvas(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the canvas role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_position_in_set(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_caption(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the caption role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_chart(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the chart role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_check_box(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the check-box role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generate_state_checked(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_state_checked(obj, **args)
        result += self._generate_state_required(obj, **args)
        result += self._generate_state_invalid(obj, **args)
        result += self._generate_state_sensitive(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_check_menu_item(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the check-menu-item role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generate_state_checked(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_state_checked(obj, **args)
        result += self._generate_state_sensitive(obj, **args)
        result += self._generate_position_in_set(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_color_chooser(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the color-chooser role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_column_header(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the column-header role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_combo_box(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the combo-box role."""

        result = []
        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            result += self._generate_state_expanded(obj, **args)
            return result

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_state_expanded(obj, **args)
        result += self._generate_position_in_set(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_comment(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the comment role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_content_deletion(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the content-deletion role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_content_insertion(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the content-insertion role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_date_editor(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the date-editor role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_definition(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the definition role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_description_list(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the description-list role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_description_term(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the description-term role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_description_value(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the description-value role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_desktop_frame(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the desktop-frame role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_desktop_icon(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the desktop-icon role."""

        return self._generate_icon(obj, **args)

    def _generate_dial(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the dial role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generate_value_as_percentage(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_value_as_percentage(obj, **args)
        result += self._generate_state_required(obj, **args)
        result += self._generate_state_invalid(obj, **args)
        result += self._generate_state_sensitive(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_dialog(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the dialog role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_directory_pane(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the directory_pane role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_document(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for document-related roles."""

        return self._generate_default_presentation(obj, **args)

    def _generate_document_email(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the document-email role."""

        return self._generate_document(obj, **args)

    def _generate_document_frame(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the document-frame role."""

        return self._generate_document(obj, **args)

    def _generate_document_presentation(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the document-presentation role."""

        return self._generate_document(obj, **args)

    def _generate_document_spreadsheet(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the document-spreadsheet role."""

        return self._generate_document(obj, **args)

    def _generate_document_text(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the document-text role."""

        return self._generate_document(obj, **args)

    def _generate_document_web(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the document-web role."""

        return self._generate_document(obj, **args)

    def _generate_dpub_landmark(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the dpub section role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_dpub_section(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the dpub section role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_drawing_area(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the drawing-area role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_editbar(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the editbar role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_embedded(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the embedded role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_entry(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the entry role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_state_read_only(obj, **args)
        result += self._generate_state_required(obj, **args)
        result += self._generate_state_invalid(obj, **args)
        result += self._generate_state_sensitive(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_feed(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the feed role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_file_chooser(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the file-chooser role."""

        return self._generate_dialog(obj, **args)

    def _generate_filler(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the filler role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_font_chooser(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the font-chooser role."""

        return self._generate_dialog(obj, **args)

    def _generate_footer(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the footer role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_footnote(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the footnote role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_form(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the form role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_frame(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the frame role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_glass_pane(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the glass-pane role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_grouping(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the grouping role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_header(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the header role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_heading(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the heading role."""

        result = []
        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            result += self._generate_state_expanded(obj, **args)
            return result

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_state_expanded(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_html_container(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the html-container role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_icon(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the icon role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_position_in_set(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_image(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the image role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_image_map(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the image-map role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_info_bar(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the info-bar role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_input_method_window(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the input-method-window role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_internal_frame(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the internal-frame role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_label(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the label role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_landmark(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the landmark role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_layered_pane(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the layered-pane role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_level_bar(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the level-bar role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generate_value_as_percentage(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_value_as_percentage(obj, **args)
        result += self._generate_state_required(obj, **args)
        result += self._generate_state_invalid(obj, **args)
        result += self._generate_state_sensitive(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_link(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the link role."""

        result = []
        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            result += self._generate_state_expanded(obj, **args)
            return result

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_state_expanded(obj, **args)
        result += self._generate_visited_state(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_list(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the list role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_list_box(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the list-box role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_state_multiselectable(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_list_item(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the list-item role."""

        result = []
        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            result += self._generate_state_expanded(obj, **args)
            return result

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_state_expanded(obj, **args)
        result += self._generate_position_in_set(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_log(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the log role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_mark(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the mark role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_marquee(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the marquee role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_math(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the math role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_math_enclosed(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the math-enclosed role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_math_fenced(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the math-fenced role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_math_fraction(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the math-fraction role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_math_multiscript(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the math-multiscript role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_math_root(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the math-root role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_math_row(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the math-row role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_math_script_subsuper(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the math script subsuper role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_math_script_underover(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the math script underover role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_math_table(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the math-table role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_menu(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the menu role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_menu_bar(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the menu-bar role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_menu_item(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the menu-item role."""

        result = []
        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            result += self._generate_state_expanded(obj, **args)
            return result

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_state_expanded(obj, **args)
        result += self._generate_state_sensitive(obj, **args)
        result += self._generate_position_in_set(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_notification(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the notification role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_option_pane(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the option-pane role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_page(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the page role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_page_tab(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the page-tab role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_position_in_set(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_page_tab_list(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the page-tab-list role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_panel(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the panel role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_paragraph(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the paragraph role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_password_text(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the password-text role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_popup_menu(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the popup-menu role."""

        return self._generate_menu(obj, **args)

    def _generate_progress_bar(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the progress-bar role."""

        result = []
        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            result += self._generate_progress_bar_value(obj, **args)
            return result

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_progress_bar_value(obj, **args)
        return result

    def _generate_push_button(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the push-button role."""

        result = []
        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            result += self._generate_state_expanded(obj, **args)
            return result

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_state_expanded(obj, **args)
        result += self._generate_state_sensitive(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_push_button_menu(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the push-button-menu role."""

        return self._generate_push_button(obj, **args)

    def _generate_radio_button(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the radio-button role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generate_state_selected_for_radio_button(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_state_selected_for_radio_button(obj, **args)
        result += self._generate_state_sensitive(obj, **args)
        result += self._generate_position_in_set(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_radio_menu_item(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the radio-menu-item role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generate_state_selected_for_radio_button(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_state_selected_for_radio_button(obj, **args)
        result += self._generate_state_sensitive(obj, **args)
        result += self._generate_position_in_set(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_rating(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the rating role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_region(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the region landmark role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_root_pane(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the root-pane role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_row_header(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the row-header role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_ruler(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the ruler role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_scroll_bar(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the scroll-bar role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generate_value_as_percentage(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_value_as_percentage(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_scroll_pane(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the scroll-pane role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_section(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the section role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_separator(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the separator role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_slider(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the slider role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generate_value_as_percentage(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_value_as_percentage(obj, **args)
        result += self._generate_state_required(obj, **args)
        result += self._generate_state_invalid(obj, **args)
        result += self._generate_state_sensitive(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_spin_button(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the spin-button role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generate_value_as_percentage(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_value_as_percentage(obj, **args)
        result += self._generate_state_required(obj, **args)
        result += self._generate_state_invalid(obj, **args)
        result += self._generate_state_sensitive(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_split_pane(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the split-pane role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generate_value_as_percentage(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_value_as_percentage(obj, **args)
        result += self._generate_state_sensitive(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_static(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the static role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_status_bar(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the status-bar role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_subscript(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the subscript role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_suggestion(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the suggestion role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_superscript(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the superscript role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_switch(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the switch role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generate_state_checked_for_switch(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_state_checked_for_switch(obj, **args)
        result += self._generate_state_sensitive(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_table(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the table role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_table_cell(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the table-cell role."""

        result = []
        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            result += self._generate_state_expanded(obj, **args)
            return result

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_state_expanded(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_table_cell_in_row(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the table-cell role in the context of its row."""

        return self._generate_default_presentation(obj, **args)

    def _generate_table_column_header(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the table-column-header role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_table_row(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the table-row role."""

        result = []
        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            result += self._generate_state_expanded(obj, **args)
            return result

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_state_expanded(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_table_row_header(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the table-row-header role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_tearoff_menu_item(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the tearoff-menu-item role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_terminal(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the terminal role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_text(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the text role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_timer(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the timer role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_title_bar(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the title-bar role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_toggle_button(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the toggle-button role."""

        result = []
        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generate_state_expanded(obj, **args) \
                or self._generate_state_pressed(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += (self._generate_state_expanded(obj, **args) \
                or self._generate_state_pressed(obj, **args))
        result += self._generate_state_sensitive(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_tool_bar(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the tool-bar role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_tool_tip(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the tool-tip role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_tree(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the tree role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_tree_item(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the tree-item role."""

        result = []
        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            result += self._generate_state_expanded(obj, **args)
            return result

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_state_expanded(obj, **args)
        result += self._generate_position_in_set(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_tree_table(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the tree-table role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_unknown(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the unknown role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_video(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the video role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_viewport(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the viewport role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_window(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates sound for the window role."""

        return self._generate_default_presentation(obj, **args)
