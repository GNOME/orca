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

"""Utilities for obtaining sounds to be presented for objects."""

__id__        = "$Id:$"
__version__   = "$Revision:$"
__date__      = "$Date:$"
__copyright__ = "Copyright (c) 2016 Igalia, S.L."
__license__   = "LGPL"

import gi
gi.require_version('Atspi', '2.0')
from gi.repository import Atspi

import os

from . import debug
from . import generator
from . import object_properties
from . import settings_manager
from .ax_object import AXObject
from .ax_utilities import AXUtilities
from .ax_value import AXValue

class Icon:
    """Sound file representing a particular aspect of an object."""

    def __init__(self, location, filename):
        self.path = os.path.join(location, filename)
        msg = f"SOUND GENERATOR: Looking for '{filename}' in {location}"
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def __str__(self):
        return f'Icon(path: {self.path}, isValid: {self.isValid()})'

    def isValid(self):
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

    def __init__(self, duration, frequency, volumeMultiplier=1, wave=SINE_WAVE):
        self.duration = duration
        self.frequency = min(max(0, frequency), 20000)
        self.volume = settings_manager.get_manager().get_setting('soundVolume') * volumeMultiplier
        self.wave = wave

    def __str__(self):
        return (
            f'Tone(duration: {self.duration}, '
            f'frequency: {self.frequency}, '
            f'volume: {self.volume}, '
            f'wave: {self.wave})'
        )

class SoundGenerator(generator.Generator):
    """Takes accessible objects and produces the sound(s) to be played."""

    def __init__(self, script):
        super().__init__(script, "sound")
        self._sounds = os.path.join(settings_manager.get_manager().get_prefs_dir(), "sounds")
        self._generators = {
            Atspi.Role.ALERT: self._generate_alert,
            Atspi.Role.ANIMATION: self._generate_animation,
            Atspi.Role.ARTICLE: self._generate_article,
            'ROLE_ARTICLE_IN_FEED': self._generate_article_in_feed,
            Atspi.Role.BLOCK_QUOTE: self._generate_block_quote,
            Atspi.Role.CANVAS: self._generate_canvas,
            Atspi.Role.CAPTION: self._generate_caption,
            Atspi.Role.CHECK_BOX: self._generate_check_box,
            Atspi.Role.CHECK_MENU_ITEM: self._generate_check_menu_item,
            Atspi.Role.COLOR_CHOOSER: self._generate_color_chooser,
            Atspi.Role.COLUMN_HEADER: self._generate_column_header,
            Atspi.Role.COMBO_BOX: self._generate_combo_box,
            Atspi.Role.COMMENT: self._generate_comment,
            Atspi.Role.CONTENT_DELETION: self._generate_content_deletion,
            'ROLE_CONTENT_ERROR': self._generate_content_error,
            Atspi.Role.CONTENT_INSERTION: self._generate_content_insertion,
            Atspi.Role.DEFINITION: self._generate_definition,
            Atspi.Role.DESCRIPTION_LIST: self._generate_description_list,
            Atspi.Role.DESCRIPTION_TERM: self._generate_description_term,
            Atspi.Role.DESCRIPTION_VALUE: self._generate_description_value,
            Atspi.Role.DIAL: self._generate_dial,
            Atspi.Role.DIALOG: self._generate_dialog,
            Atspi.Role.DOCUMENT_EMAIL: self._generate_document_email,
            Atspi.Role.DOCUMENT_FRAME: self._generate_document_frame,
            Atspi.Role.DOCUMENT_PRESENTATION: self._generate_document_presentation,
            Atspi.Role.DOCUMENT_SPREADSHEET: self._generate_document_spreadsheet,
            Atspi.Role.DOCUMENT_TEXT: self._generate_document_text,
            Atspi.Role.DOCUMENT_WEB: self._generate_document_web,
            'ROLE_DPUB_LANDMARK': self._generate_dpub_landmark,
            'ROLE_DPUB_SECTION': self._generate_dpub_section,
            Atspi.Role.EDITBAR: self._generate_editbar,
            Atspi.Role.EMBEDDED: self._generate_embedded,
            Atspi.Role.ENTRY: self._generate_entry,
            'ROLE_FEED': self._generate_feed,
            Atspi.Role.FOOTNOTE: self._generate_footnote,
            Atspi.Role.FOOTER: self._generate_footer,
            Atspi.Role.FORM: self._generate_form,
            Atspi.Role.FRAME: self._generate_frame,
            Atspi.Role.HEADER: self._generate_header,
            Atspi.Role.HEADING: self._generate_heading,
            Atspi.Role.ICON: self._generate_icon,
            Atspi.Role.IMAGE: self._generate_image,
            Atspi.Role.INFO_BAR: self._generate_info_bar,
            Atspi.Role.INTERNAL_FRAME: self._generate_internal_frame,
            Atspi.Role.LABEL: self._generate_label,
            Atspi.Role.LANDMARK: self._generate_landmark,
            Atspi.Role.LAYERED_PANE: self._generate_layered_pane,
            Atspi.Role.LINK: self._generate_link,
            Atspi.Role.LEVEL_BAR: self._generate_level_bar,
            Atspi.Role.LIST: self._generate_list,
            Atspi.Role.LIST_BOX: self._generate_list_box,
            Atspi.Role.LIST_ITEM: self._generate_list_item,
            Atspi.Role.MATH: self._generate_math,
            'ROLE_MATH_ENCLOSED': self._generate_math_enclosed,
            'ROLE_MATH_FENCED': self._generate_math_fenced,
            Atspi.Role.MATH_FRACTION: self._generate_math_fraction,
            Atspi.Role.MATH_ROOT: self._generate_math_root,
            'ROLE_MATH_MULTISCRIPT': self._generate_math_multiscript,
            'ROLE_MATH_SCRIPT_SUBSUPER': self._generate_math_script_subsuper,
            'ROLE_MATH_SCRIPT_UNDEROVER': self._generate_math_script_underover,
            'ROLE_MATH_TABLE': self._generate_math_table,
            'ROLE_MATH_TABLE_ROW': self._generate_math_row,
            Atspi.Role.MARK: self._generate_mark,
            Atspi.Role.MENU: self._generate_menu,
            Atspi.Role.MENU_ITEM: self._generate_menu_item,
            Atspi.Role.NOTIFICATION: self._generate_notification,
            Atspi.Role.PAGE: self._generate_page,
            Atspi.Role.PAGE_TAB: self._generate_page_tab,
            Atspi.Role.PANEL: self._generate_panel,
            Atspi.Role.PARAGRAPH: self._generate_paragraph,
            Atspi.Role.PASSWORD_TEXT: self._generate_password_text,
            Atspi.Role.PROGRESS_BAR: self._generate_progress_bar,
            Atspi.Role.PUSH_BUTTON: self._generate_push_button,
            Atspi.Role.RADIO_BUTTON: self._generate_radio_button,
            Atspi.Role.RADIO_MENU_ITEM: self._generate_radio_menu_item,
            'ROLE_REGION': self._generate_region,
            Atspi.Role.ROW_HEADER: self._generate_row_header,
            Atspi.Role.SCROLL_BAR: self._generate_scroll_bar,
            Atspi.Role.SCROLL_PANE: self._generate_scroll_pane,
            Atspi.Role.SECTION: self._generate_section,
            Atspi.Role.SLIDER: self._generate_slider,
            Atspi.Role.SPIN_BUTTON: self._generate_spin_button,
            Atspi.Role.SEPARATOR: self._generate_separator,
            Atspi.Role.SPLIT_PANE: self._generate_split_pane,
            Atspi.Role.STATIC: self._generate_static,
            Atspi.Role.STATUS_BAR: self._generate_status_bar,
            Atspi.Role.SUBSCRIPT: self._generate_subscript,
            Atspi.Role.SUGGESTION: self._generate_suggestion,
            Atspi.Role.SUPERSCRIPT: self._generate_superscript,
            'ROLE_SWITCH': self._generate_switch,
            Atspi.Role.TABLE: self._generate_table,
            Atspi.Role.TABLE_CELL: self._generate_table_cell_in_row,
            'REAL_ROLE_TABLE_CELL': self._generate_table_cell,
            Atspi.Role.TABLE_ROW: self._generate_table_row,
            Atspi.Role.TEAROFF_MENU_ITEM: self._generate_tearoff_menu_item,
            Atspi.Role.TERMINAL: self._generate_terminal,
            Atspi.Role.TEXT: self._generate_text,
            Atspi.Role.TOGGLE_BUTTON: self._generate_toggle_button,
            Atspi.Role.TOOL_BAR: self._generate_tool_bar,
            Atspi.Role.TOOL_TIP: self._generate_tool_tip,
            Atspi.Role.TREE: self._generate_tree,
            Atspi.Role.TREE_ITEM: self._generate_tree_item,
            Atspi.Role.WINDOW: self._generate_window,
        }

    def _convertFilenameToIcon(self, filename):
        icon = Icon(self._sounds, filename)
        if icon.isValid():
            return icon

        return None

    def generate(self, obj, **args):
        _generator = self._generators.get(args.get("role") or AXObject.get_role(obj))
        if _generator is None:
            tokens = ["SOUND GENERATOR:", obj, "lacks dedicated generator"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            _generator = self._generate_default_presentation

        args["mode"] = self._mode
        if not args.get("formatType", None):
            if args.get("alreadyFocused", False):
                args["formatType"] = "focused"
            else:
                args["formatType"] = "unfocused"

        tokens = ["SOUND GENERATOR:", _generator, "for", obj, "args:", args]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        result = _generator(obj, **args)
        tokens = ["SOUND GENERATOR: Results:", result]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return result

    def generateSound(self, obj, **args):
        """Returns an array of sounds for the complete presentation of obj."""

        if not settings_manager.get_manager().get_setting("enableSound"):
            debug.printMessage(debug.LEVEL_INFO, "SOUND GENERATOR: Generation disabled", True)
            return []

        return self.generate(obj, **args)

    #####################################################################
    #                                                                   #
    # State information                                                 #
    #                                                                   #
    #####################################################################

    def _generateAvailability(self, obj, **args):
        """Returns an array of sounds indicating obj is grayed out."""

        if not settings_manager.get_manager().get_setting("playSoundForState"):
            return []

        if AXUtilities.is_sensitive(obj):
            return []

        filename = object_properties.STATE_INSENSITIVE_SPEECH
        result = self._convertFilenameToIcon(filename)
        if result:
            return [result]

        return []

    def _generateCheckedState(self, obj, **args):
        """Returns an array of sounds indicating the checked state of obj."""

        if not settings_manager.get_manager().get_setting("playSoundForState"):
            return []

        filenames = super()._generateCheckedState(obj, **args)
        if filenames and filenames[0]:
            result = self._convertFilenameToIcon(filenames[0])
            if result:
                return [result]

        return []

    def _generateClickable(self, obj, **args):
        """Returns an array of sounds indicating obj is clickable."""

        if not settings_manager.get_manager().get_setting("playSoundForState"):
            return []

        if not self._script.utilities.isClickableElement(obj):
            return []

        filename = object_properties.STATE_CLICKABLE_SOUND
        result = self._convertFilenameToIcon(filename)
        if result:
            return [result]

        return []

    def _generateExpandableState(self, obj, **args):
        """Returns an array of sounds indicating the expanded state of obj."""

        if not settings_manager.get_manager().get_setting("playSoundForState"):
            return []

        filenames = super()._generateExpandableState(obj, **args)
        if filenames and filenames[0]:
            result = self._convertFilenameToIcon(filenames[0])
            if result:
                return [result]

        return []

    def _generateInvalid(self, obj, **args):
        """Returns an array of sounds indicating the invalid state of obj."""

        if not settings_manager.get_manager().get_setting("playSoundForState"):
            return []

        filenames = super()._generateInvalid(obj, **args)
        if filenames and filenames[0]:
            result = self._convertFilenameToIcon(filenames[0])
            if result:
                return [result]

        return []

    def _generateHasLongDesc(self, obj, **args):
        """Returns an array of sounds indicating obj has a longdesc."""

        if not settings_manager.get_manager().get_setting("playSoundForState"):
            return []

        if not self._script.utilities.hasLongDesc(obj):
            return []

        filename = object_properties.STATE_HAS_LONGDESC_SOUND
        result = self._convertFilenameToIcon(filename)
        if result:
            return [result]

        return []

    def _generateMenuItemCheckedState(self, obj, **args):
        """Returns an array of sounds indicating the checked state of obj."""

        if not settings_manager.get_manager().get_setting("playSoundForState"):
            return []

        filenames = super()._generateMenuItemCheckedState(obj, **args)
        if filenames and filenames[0]:
            result = self._convertFilenameToIcon(filenames[0])
            if result:
                return [result]

        return []

    def _generateMultiselectableState(self, obj, **args):
        """Returns an array of sounds indicating obj is multiselectable."""

        if not settings_manager.get_manager().get_setting("playSoundForState"):
            return []

        filenames = super()._generateMultiselectableState(obj, **args)
        if filenames and filenames[0]:
            result = self._convertFilenameToIcon(filenames[0])
            if result:
                return [result]

        return []

    def _generateRadioState(self, obj, **args):
        """Returns an array of sounds indicating the selected state of obj."""

        if not settings_manager.get_manager().get_setting("playSoundForState"):
            return []

        filenames = super()._generateRadioState(obj, **args)
        if filenames and filenames[0]:
            result = self._convertFilenameToIcon(filenames[0])
            if result:
                return [result]

        return []

    def _generateReadOnly(self, obj, **args):
        """Returns an array of sounds indicating obj is read only."""

        if not settings_manager.get_manager().get_setting("playSoundForState"):
            return []

        filenames = super()._generateReadOnly(obj, **args)
        if filenames and filenames[0]:
            result = self._convertFilenameToIcon(filenames[0])
            if result:
                return [result]

        return []

    def _generateRequired(self, obj, **args):
        """Returns an array of sounds indicating obj is required."""

        if not settings_manager.get_manager().get_setting("playSoundForState"):
            return []

        filenames = super()._generateRequired(obj, **args)
        if filenames and filenames[0]:
            result = self._convertFilenameToIcon(filenames[0])
            if result:
                return [result]

        return []

    def _generateSwitchState(self, obj, **args):
        """Returns an array of sounds indicating the on/off state of obj."""

        if not settings_manager.get_manager().get_setting("playSoundForState"):
            return []

        filenames = super()._generateSwitchState(obj, **args)
        if filenames and filenames[0]:
            result = self._convertFilenameToIcon(filenames[0])
            if result:
                return [result]

        return []

    def _generateToggleState(self, obj, **args):
        """Returns an array of sounds indicating the toggled state of obj."""

        if not settings_manager.get_manager().get_setting("playSoundForState"):
            return []

        filenames = super()._generateToggleState(obj, **args)
        if filenames and filenames[0]:
            result = self._convertFilenameToIcon(filenames[0])
            if result:
                return [result]

        return []

    def _generateVisitedState(self, obj, **args):
        """Returns an array of sounds indicating the visited state of obj."""

        if not settings_manager.get_manager().get_setting("playSoundForState"):
            return []

        if not AXUtilities.is_visited(obj):
            return []

        filename = object_properties.STATE_VISITED_SOUND
        result = self._convertFilenameToIcon(filename)
        if result:
            return [result]

        return []

    #####################################################################
    #                                                                   #
    # Value interface information                                       #
    #                                                                   #
    #####################################################################

    def _generatePercentage(self, obj, **args):
        """Returns an array of sounds reflecting the percentage of obj."""

        if not settings_manager.get_manager().get_setting('playSoundForValue'):
            return []

        percent = AXValue.get_value_as_percent(obj)
        if percent is None:
            return []

        return []

    def _generateProgressBarValue(self, obj, **args):
        """Returns an array of sounds representing the progress bar value."""

        if args.get('isProgressBarUpdate'):
            if not self._shouldPresentProgressBarUpdate(obj, **args):
                return []
        elif not settings_manager.get_manager().get_setting('playSoundForValue'):
            return []

        percent = AXValue.get_value_as_percent(obj)
        if percent is None:
            return []

        # To better indicate the progress completion.
        if percent >= 99:
            duration = 1
        else:
            duration = 0.075

        # Reduce volume as pitch increases.
        volumeMultiplier = 1 - (percent / 120)

        # Adjusting so that the initial beeps are not too deep.
        if percent < 7:
            frequency = int(98 + percent * 5.4)
        else:
            frequency = int(percent * 22)

        return [Tone(duration, frequency, volumeMultiplier, Tone.SINE_WAVE)]

    def _getProgressBarUpdateInterval(self):
        interval = settings_manager.get_manager().get_setting('progressBarBeepInterval')
        if interval is None:
            return super()._getProgressBarUpdateInterval()

        return int(interval)

    def _shouldPresentProgressBarUpdate(self, obj, **args):
        if not settings_manager.get_manager().get_setting('beepProgressBarUpdates'):
            return False

        return super()._shouldPresentProgressBarUpdate(obj, **args)

    #####################################################################
    #                                                                   #
    # Role and hierarchical information                                 #
    #                                                                   #
    #####################################################################

    def _generatePositionInSet(self, obj, **args):
        """Returns an array of sounds reflecting the set position of obj."""

        if not settings_manager.get_manager().get_setting('playSoundForPositionInSet'):
            return []

        # TODO: Implement the result.
        # position, setSize = self._script.utilities.getPositionAndSetSize(obj)
        # percent = int((position / setSize) * 100)

        return []

    def _generateRoleName(self, obj, **args):
        """Returns an array of sounds indicating the role of obj."""

        if not settings_manager.get_manager().get_setting('playSoundForRole'):
            return []

        role = args.get("role", AXObject.get_role(obj))
        filenames = [Atspi.role_get_name(role).replace(" ", "-")]
        if filenames and filenames[0]:
            result = self._convertFilenameToIcon(filenames[0])
            if result:
                return [result]

        return []

#########################################################################################

    def _generate_default_prefix(self, _obj, **_args):
        """Provides the default/role-agnostic information to present before obj."""

        return []

    def _generate_default_presentation(self, obj, **args):
        """Provides a default/role-agnostic presentation of obj."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_default_suffix(self, _obj, **_args):
        """Provides the default/role-agnostic information to present after obj."""

        return []

    def _generate_accelerator_label(self, obj, **args):
        """Generates sound for the accelerator-label role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_alert(self, obj, **args):
        """Generates sound for the alert role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_animation(self, obj, **args):
        """Generates sound for the animation role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_application(self, obj, **args):
        """Generates sound for the application role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_arrow(self, obj, **args):
        """Generates sound for the arrow role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_article(self, obj, **args):
        """Generates sound for the article role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_article_in_feed(self, obj, **args):
        """Generates sound for the article role when the article is in a feed."""

        return self._generate_default_presentation(obj, **args)

    def _generate_audio(self, obj, **args):
        """Generates sound for the audio role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_autocomplete(self, obj, **args):
        """Generates sound for the autocomplete role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_block_quote(self, obj, **args):
        """Generates sound for the block-quote role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_calendar(self, obj, **args):
        """Generates sound for the calendar role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_canvas(self, obj, **args):
        """Generates sound for the canvas role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generatePositionInSet(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_caption(self, obj, **args):
        """Generates sound for the caption role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_chart(self, obj, **args):
        """Generates sound for the chart role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_check_box(self, obj, **args):
        """Generates sound for the check-box role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generateCheckedState(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateCheckedState(obj, **args)
        result += self._generateRequired(obj, **args)
        result += self._generateInvalid(obj, **args)
        result += self._generateAvailability(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_check_menu_item(self, obj, **args):
        """Generates sound for the check-menu-item role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generateCheckedState(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateCheckedState(obj, **args)
        result += self._generateAvailability(obj, **args)
        result += self._generatePositionInSet(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_color_chooser(self, obj, **args):
        """Generates sound for the color-chooser role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_column_header(self, obj, **args):
        """Generates sound for the column-header role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_combo_box(self, obj, **args):
        """Generates sound for the combo-box role."""

        result = []
        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            result += self._generateExpandableState(obj, **args)
            return result

        result = self._generate_default_prefix(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateExpandableState(obj, **args)
        result += self._generatePositionInSet(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_comment(self, obj, **args):
        """Generates sound for the comment role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_content_deletion(self, obj, **args):
        """Generates sound for the content-deletion role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_content_error(self, obj, **args):
        """Generates sound for a role with a content-related error."""

        return self._generate_default_presentation(obj, **args)

    def _generate_content_insertion(self, obj, **args):
        """Generates sound for the content-insertion role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_date_editor(self, obj, **args):
        """Generates sound for the date-editor role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_definition(self, obj, **args):
        """Generates sound for the definition role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_description_list(self, obj, **args):
        """Generates sound for the description-list role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_description_term(self, obj, **args):
        """Generates sound for the description-term role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_description_value(self, obj, **args):
        """Generates sound for the description-value role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_desktop_frame(self, obj, **args):
        """Generates sound for the desktop-frame role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_desktop_icon(self, obj, **args):
        """Generates sound for the desktop-icon role."""

        return self._generate_icon(obj, **args)

    def _generate_dial(self, obj, **args):
        """Generates sound for the dial role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generatePercentage(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generatePercentage(obj, **args)
        result += self._generateRequired(obj, **args)
        result += self._generateInvalid(obj, **args)
        result += self._generateAvailability(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_dialog(self, obj, **args):
        """Generates sound for the dialog role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_directory_pane(self, obj, **args):
        """Generates sound for the directory_pane role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_document(self, obj, **args):
        """Generates sound for document-related roles."""

        return self._generate_default_presentation(obj, **args)

    def _generate_document_email(self, obj, **args):
        """Generates sound for the document-email role."""

        return self._generate_document(obj, **args)

    def _generate_document_frame(self, obj, **args):
        """Generates sound for the document-frame role."""

        return self._generate_document(obj, **args)

    def _generate_document_presentation(self, obj, **args):
        """Generates sound for the document-presentation role."""

        return self._generate_document(obj, **args)

    def _generate_document_spreadsheet(self, obj, **args):
        """Generates sound for the document-spreadsheet role."""

        return self._generate_document(obj, **args)

    def _generate_document_text(self, obj, **args):
        """Generates sound for the document-text role."""

        return self._generate_document(obj, **args)

    def _generate_document_web(self, obj, **args):
        """Generates sound for the document-web role."""

        return self._generate_document(obj, **args)

    def _generate_dpub_landmark(self, obj, **args):
        """Generates sound for the dpub section role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_dpub_section(self, obj, **args):
        """Generates sound for the dpub section role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_drawing_area(self, obj, **args):
        """Generates sound for the drawing-area role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_editbar(self, obj, **args):
        """Generates sound for the editbar role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_embedded(self, obj, **args):
        """Generates sound for the embedded role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_entry(self, obj, **args):
        """Generates sound for the entry role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateReadOnly(obj, **args)
        result += self._generateRequired(obj, **args)
        result += self._generateInvalid(obj, **args)
        result += self._generateAvailability(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_feed(self, obj, **args):
        """Generates sound for the feed role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_file_chooser(self, obj, **args):
        """Generates sound for the file-chooser role."""

        return self._generate_dialog(obj, **args)

    def _generate_filler(self, obj, **args):
        """Generates sound for the filler role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_font_chooser(self, obj, **args):
        """Generates sound for the font-chooser role."""

        return self._generate_dialog(obj, **args)

    def _generate_footer(self, obj, **args):
        """Generates sound for the footer role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_footnote(self, obj, **args):
        """Generates sound for the footnote role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_form(self, obj, **args):
        """Generates sound for the form role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_frame(self, obj, **args):
        """Generates sound for the frame role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_glass_pane(self, obj, **args):
        """Generates sound for the glass-pane role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_grouping(self, obj, **args):
        """Generates sound for the grouping role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_header(self, obj, **args):
        """Generates sound for the header role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_heading(self, obj, **args):
        """Generates sound for the heading role."""

        result = []
        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            result += self._generateExpandableState(obj, **args)
            return result

        result = self._generate_default_prefix(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateExpandableState(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_html_container(self, obj, **args):
        """Generates sound for the html-container role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_icon(self, obj, **args):
        """Generates sound for the icon role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generatePositionInSet(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_image(self, obj, **args):
        """Generates sound for the image role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_image_map(self, obj, **args):
        """Generates sound for the image-map role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_info_bar(self, obj, **args):
        """Generates sound for the info-bar role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_input_method_window(self, obj, **args):
        """Generates sound for the input-method-window role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_internal_frame(self, obj, **args):
        """Generates sound for the internal-frame role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_label(self, obj, **args):
        """Generates sound for the label role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_landmark(self, obj, **args):
        """Generates sound for the landmark role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_layered_pane(self, obj, **args):
        """Generates sound for the layered-pane role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_level_bar(self, obj, **args):
        """Generates sound for the level-bar role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generatePercentage(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generatePercentage(obj, **args)
        result += self._generateRequired(obj, **args)
        result += self._generateInvalid(obj, **args)
        result += self._generateAvailability(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_link(self, obj, **args):
        """Generates sound for the link role."""

        result = []
        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            result += self._generateExpandableState(obj, **args)
            return result

        result = self._generate_default_prefix(obj, **args)
        result += self._generateExpandableState(obj, **args)
        result += self._generateVisitedState(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_list(self, obj, **args):
        """Generates sound for the list role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_list_box(self, obj, **args):
        """Generates sound for the list-box role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateMultiselectableState(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_list_item(self, obj, **args):
        """Generates sound for the list-item role."""

        result = []
        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            result += self._generateExpandableState(obj, **args)
            return result

        result = self._generate_default_prefix(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateExpandableState(obj, **args)
        result += self._generatePositionInSet(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_log(self, obj, **args):
        """Generates sound for the log role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_mark(self, obj, **args):
        """Generates sound for the mark role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_marquee(self, obj, **args):
        """Generates sound for the marquee role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_math(self, obj, **args):
        """Generates sound for the math role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_math_enclosed(self, obj, **args):
        """Generates sound for the math-enclosed role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_math_fenced(self, obj, **args):
        """Generates sound for the math-fenced role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_math_fraction(self, obj, **args):
        """Generates sound for the math-fraction role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_math_multiscript(self, obj, **args):
        """Generates sound for the math-multiscript role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_math_root(self, obj, **args):
        """Generates sound for the math-root role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_math_row(self, obj, **args):
        """Generates sound for the math-row role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_math_script_subsuper(self, obj, **args):
        """Generates sound for the math script subsuper role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_math_script_underover(self, obj, **args):
        """Generates sound for the math script underover role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_math_table(self, obj, **args):
        """Generates sound for the math-table role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_menu(self, obj, **args):
        """Generates sound for the menu role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_menu_bar(self, obj, **args):
        """Generates sound for the menu-bar role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_menu_item(self, obj, **args):
        """Generates sound for the menu-item role."""

        result = []
        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            result += self._generateExpandableState(obj, **args)
            return result

        result = self._generate_default_prefix(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateExpandableState(obj, **args)
        result += self._generateAvailability(obj, **args)
        result += self._generatePositionInSet(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_notification(self, obj, **args):
        """Generates sound for the notification role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_option_pane(self, obj, **args):
        """Generates sound for the option-pane role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_page(self, obj, **args):
        """Generates sound for the page role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_page_tab(self, obj, **args):
        """Generates sound for the page-tab role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generatePositionInSet(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_page_tab_list(self, obj, **args):
        """Generates sound for the page-tab-list role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_panel(self, obj, **args):
        """Generates sound for the panel role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_paragraph(self, obj, **args):
        """Generates sound for the paragraph role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_password_text(self, obj, **args):
        """Generates sound for the password-text role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_popup_menu(self, obj, **args):
        """Generates sound for the popup-menu role."""

        return self._generate_menu(obj, **args)

    def _generate_progress_bar(self, obj, **args):
        """Generates sound for the progress-bar role."""

        result = []
        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            result += self._generateProgressBarValue(obj, **args)
            return result

        result = self._generate_default_prefix(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateProgressBarValue(obj, **args)
        return result

    def _generate_push_button(self, obj, **args):
        """Generates sound for the push-button role."""

        result = []
        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            result += self._generateExpandableState(obj, **args)
            return result

        result = self._generate_default_prefix(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateExpandableState(obj, **args)
        result += self._generateAvailability(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_push_button_menu(self, obj, **args):
        """Generates sound for the push-button-menu role."""

        return self._generate_push_button(obj, **args)

    def _generate_radio_button(self, obj, **args):
        """Generates sound for the radio-button role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generateRadioState(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateRadioState(obj, **args)
        result += self._generateAvailability(obj, **args)
        result += self._generatePositionInSet(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_radio_menu_item(self, obj, **args):
        """Generates sound for the radio-menu-item role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generateRadioState(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateRadioState(obj, **args)
        result += self._generateAvailability(obj, **args)
        result += self._generatePositionInSet(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_rating(self, obj, **args):
        """Generates sound for the rating role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_region(self, obj, **args):
        """Generates sound for the region landmark role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_root_pane(self, obj, **args):
        """Generates sound for the root-pane role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_row_header(self, obj, **args):
        """Generates sound for the row-header role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_ruler(self, obj, **args):
        """Generates sound for the ruler role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_scroll_bar(self, obj, **args):
        """Generates sound for the scroll-bar role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generatePercentage(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generatePercentage(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_scroll_pane(self, obj, **args):
        """Generates sound for the scroll-pane role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_section(self, obj, **args):
        """Generates sound for the section role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_separator(self, obj, **args):
        """Generates sound for the separator role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_slider(self, obj, **args):
        """Generates sound for the slider role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generatePercentage(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generatePercentage(obj, **args)
        result += self._generateRequired(obj, **args)
        result += self._generateInvalid(obj, **args)
        result += self._generateAvailability(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_spin_button(self, obj, **args):
        """Generates sound for the spin-button role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generatePercentage(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generatePercentage(obj, **args)
        result += self._generateRequired(obj, **args)
        result += self._generateInvalid(obj, **args)
        result += self._generateAvailability(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_split_pane(self, obj, **args):
        """Generates sound for the split-pane role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generatePercentage(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generatePercentage(obj, **args)
        result += self._generateAvailability(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_static(self, obj, **args):
        """Generates sound for the static role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_status_bar(self, obj, **args):
        """Generates sound for the status-bar role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_subscript(self, obj, **args):
        """Generates sound for the subscript role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_suggestion(self, obj, **args):
        """Generates sound for the suggestion role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_superscript(self, obj, **args):
        """Generates sound for the superscript role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_switch(self, obj, **args):
        """Generates sound for the switch role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generateSwitchState(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateSwitchState(obj, **args)
        result += self._generateAvailability(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_table(self, obj, **args):
        """Generates sound for the table role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_table_cell(self, obj, **args):
        """Generates sound for the table-cell role."""

        result = []
        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            result += self._generateExpandableState(obj, **args)
            return result

        result = self._generate_default_prefix(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateExpandableState(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_table_cell_in_row(self, obj, **args):
        """Generates sound for the table-cell role in the context of its row."""

        return self._generate_default_presentation(obj, **args)

    def _generate_table_column_header(self, obj, **args):
        """Generates sound for the table-column-header role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_table_row(self, obj, **args):
        """Generates sound for the table-row role."""

        result = []
        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            result += self._generateExpandableState(obj, **args)
            return result

        result = self._generate_default_prefix(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateExpandableState(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_table_row_header(self, obj, **args):
        """Generates sound for the table-row-header role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_tearoff_menu_item(self, obj, **args):
        """Generates sound for the tearoff-menu-item role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_terminal(self, obj, **args):
        """Generates sound for the terminal role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_text(self, obj, **args):
        """Generates sound for the text role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_timer(self, obj, **args):
        """Generates sound for the timer role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_title_bar(self, obj, **args):
        """Generates sound for the title-bar role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_toggle_button(self, obj, **args):
        """Generates sound for the toggle-button role."""

        result = []
        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generateExpandableState(obj, **args) \
                or self._generateToggleState(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += (self._generateExpandableState(obj, **args) \
                or self._generateToggleState(obj, **args))
        result += self._generateAvailability(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_tool_bar(self, obj, **args):
        """Generates sound for the tool-bar role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_tool_tip(self, obj, **args):
        """Generates sound for the tool-tip role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_tree(self, obj, **args):
        """Generates sound for the tree role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_tree_item(self, obj, **args):
        """Generates sound for the tree-item role."""

        result = []
        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            result += self._generateExpandableState(obj, **args)
            return result

        result = self._generate_default_prefix(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateExpandableState(obj, **args)
        result += self._generatePositionInSet(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_tree_table(self, obj, **args):
        """Generates sound for the tree-table role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_unknown(self, obj, **args):
        """Generates sound for the unknown role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_video(self, obj, **args):
        """Generates sound for the video role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_viewport(self, obj, **args):
        """Generates sound for the viewport role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_window(self, obj, **args):
        """Generates sound for the window role."""

        return self._generate_default_presentation(obj, **args)
