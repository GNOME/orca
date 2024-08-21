# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
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
# pylint: disable=wrong-import-position
# pylint: disable=broad-exception-caught
# pylint: disable=too-few-public-methods

"""Produces braille presentation for accessible objects."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from . import braille
from . import debug
from . import focus_manager
from . import generator
from . import messages
from . import object_properties
from . import settings
from . import settings_manager
from .ax_object import AXObject
from .ax_text import AXText
from .ax_utilities import AXUtilities
from .braille_rolenames import shortRoleNames


class Space:
    """A dummy class to indicate we want to insert a space into an
    utterance, but only if there is text prior to the space."""
    def __init__(self, delimiter=" "):
        self.delimiter = delimiter

SPACE = [Space()]

class BrailleGenerator(generator.Generator):
    """Produces a list of braille Regions for accessible objects."""

    SKIP_CONTEXT_ROLES = (Atspi.Role.MENU,
                          Atspi.Role.MENU_BAR,
                          Atspi.Role.PAGE_TAB_LIST,
                          Atspi.Role.REDUNDANT_OBJECT,
                          Atspi.Role.UNKNOWN,
                          Atspi.Role.COMBO_BOX)

    def __init__(self, script):
        super().__init__(script, "braille")

    @staticmethod
    def log_generator_output(func):
        """Decorator for logging."""

        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            tokens = [f"BRAILLE GENERATOR: {func.__name__}:", result]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return result
        return wrapper

    def generate_braille(self, obj, **args):
        """Returns a [result, focused_region] list for presenting obj."""

        if not settings_manager.get_manager().get_setting("enableBraille") \
           and not settings_manager.get_manager().get_setting("enableBrailleMonitor"):
            debug.printMessage(debug.LEVEL_INFO, "BRAILLE GENERATOR: generation disabled", True)
            return [[], None]

        if obj == focus_manager.get_manager().get_locus_of_focus() \
           and not args.get("formatType", None):
            args["formatType"] = "focused"
        result = self.generate(obj, **args)

        # We guess at the focused region.  It's going to be a
        # Component or Text region whose accessible is the same
        # as the object we're generating braille for.  There is
        # a small hack-like thing here where we include knowledge
        # that we represent the text area of editable comboboxes
        # instead of the combobox itself.  We also do the same
        # for table cells because they sometimes have children
        # that we present.
        #
        try:
            focused_region = result[0]
        except Exception:
            focused_region = None

        for region in result:
            if isinstance(region, (braille.Component, braille.Text)) and region.accessible == obj:
                focused_region = region
                break
            if isinstance(region, braille.Text) and AXUtilities.is_combo_box(obj) \
               and AXObject.get_parent(region.accessible) == obj:
                focused_region = region
                break
            if isinstance(region, braille.Component) and AXUtilities.is_table_cell(obj) \
               and AXObject.get_parent(region.accessible) == obj:
                focused_region = region
                break
        else:

            def pred(region):
                if not isinstance(region, (braille.Component, braille.Text)):
                    return False

                if not AXUtilities.have_same_role(obj, region.accessible):
                    return False

                return AXObject.get_name(obj) == AXObject.get_name(region.accessible)

            candidates = list(filter(pred, result))
            tokens = ["BRAILLE GENERATOR: Could not determine focused region for",
                      obj, "Candidates:", candidates]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            if len(candidates) == 1:
                focused_region = candidates[0]

        return [result, focused_region]

    def get_localized_role_name(self, obj, **args):
        if settings_manager.get_manager().get_setting("brailleRolenameStyle") \
                == settings.BRAILLE_ROLENAME_STYLE_SHORT:
            rv = shortRoleNames.get(args.get("role", AXObject.get_role(obj)))
            if rv:
                return rv

        return super().get_localized_role_name(obj, **args)

    def _as_string(self, content, delimiter=" "):
        combined = ""
        prior = None
        if isinstance(content, str):
            combined = content
        elif content and isinstance(content, list):
            # Strip off leading and trailing spaces.
            #
            while content and isinstance(content[0], Space):
                content = content[1:]
            while content and isinstance(content[-1], Space):
                content = content[0:-1]
            for element in content:
                if isinstance(element, Space) and prior:
                    combined += element.delimiter
                    prior = None
                else:
                    prior = self._as_string(element)
                    combined = self._script.utilities.appendString(
                        combined, prior, delimiter)
        return combined

    def _generate_result_separator(self, _obj, **_args):
        return [braille.Region(" ")]

    ################################# BASIC DETAILS #################################

    @log_generator_output
    def _generate_accessible_role(self, obj, **args):

        if args.get('isProgressBarUpdate') \
           and not settings_manager.get_manager().get_setting('brailleProgressBarUpdates'):
            return []

        result = []
        role = args.get('role', AXObject.get_role(obj))
        verbosity_level = settings_manager.get_manager().get_setting('brailleVerbosityLevel')

        do_not_present = [Atspi.Role.UNKNOWN,
                        Atspi.Role.REDUNDANT_OBJECT,
                        Atspi.Role.FILLER,
                        Atspi.Role.EXTENDED,
                        Atspi.Role.LINK]

        # egg-list-box, e.g. privacy panel in gnome-control-center
        if AXUtilities.is_list_box(AXObject.get_parent(obj)):
            do_not_present.append(AXObject.get_role(obj))

        if verbosity_level == settings.VERBOSITY_LEVEL_BRIEF:
            do_not_present.extend([Atspi.Role.ICON, Atspi.Role.CANVAS])

        if role == Atspi.Role.HEADING:
            level = self._script.utilities.headingLevel(obj)
            result.append(object_properties.ROLE_HEADING_LEVEL_BRAILLE % level)
        elif verbosity_level == settings.VERBOSITY_LEVEL_VERBOSE \
           and not args.get('readingRow', False) and role not in do_not_present:
            result.append(self.get_localized_role_name(obj, **args))
        return result

    @log_generator_output
    def _generate_alert_and_dialog_count(self, obj,  **_args):
        result = []
        alert_and_dialog_count = self._script.utilities.unfocusedAlertAndDialogCount(obj)
        if alert_and_dialog_count > 0:
            result.append(messages.dialogCountBraille(alert_and_dialog_count))

        return result

    @log_generator_output
    def _generate_ancestors(self, obj, **args):
        if not settings_manager.get_manager().get_setting('enableBrailleContext'):
            return []
        if self._script.get_table_navigator().last_input_event_was_navigation_command():
            return []

        result = []
        args['includeContext'] = False
        parent = AXObject.get_parent_checked(obj)
        if parent and (AXObject.get_role(parent) in self.SKIP_CONTEXT_ROLES):
            parent = AXObject.get_parent_checked(parent)
        while parent:
            parent_result = []
            if not self._script.utilities.isLayoutOnly(parent):
                parent_result = self.generate(parent, **args)
            if result and parent_result:
                result.append(braille.Region(" "))
            result.extend(parent_result)
            parent = AXObject.get_parent_checked(parent)
        result.reverse()
        return result

    @log_generator_output
    def _generate_term_value_count(self, obj, **_args):
        count = len(self._script.utilities.valuesForTerm(obj))
        if count < 0:
            return []
        return [f"({messages.valueCountForTerm(count)})"]

    ################################### KEYBOARD ###################################

    def _generate_keyboard_accelerator(self, obj, **_args):
        verbosity_level = settings_manager.get_manager().get_setting('brailleVerbosityLevel')
        if verbosity_level == settings.VERBOSITY_LEVEL_BRIEF:
            return []

        result = []
        accelerator = self._script.utilities.mnemonicShortcutAccelerator(obj)[-1]
        if accelerator:
            result.append("(" + accelerator + ")")
        return result

    ################################ PROGRESS BARS ##################################

    @log_generator_output
    def _generate_progress_bar_index(self, obj, **_args):
        acc = self._get_most_recent_progress_bar_update()[0]
        if acc != obj:
            number = self._get_progress_bar_number_and_count(obj)[0]
            return [f'{number}']

        return []

    @log_generator_output
    def _generate_progress_bar_value(self, obj, **args):
        result = self._generate_value_as_percentage(obj, **args)
        if obj == focus_manager.get_manager().get_locus_of_focus() and not result:
            return [""]

        return result

    def _get_progress_bar_update_interval(self):
        interval = settings_manager.get_manager().get_setting("progressBarBrailleInterval")
        if interval is None:
            return super()._get_progress_bar_update_interval()

        return int(interval)

    def _should_present_progress_bar_update(self, obj, **args):
        if not settings_manager.get_manager().get_setting("brailleProgressBarUpdates"):
            return False

        return super()._should_present_progress_bar_update(obj, **args)

    ##################################### TEXT ######################################

    @log_generator_output
    def _generate_eol(self, obj, **_args):
        if settings_manager.get_manager().get_setting("disableBrailleEOL"):
            return []

        if not (AXUtilities.is_editable(obj) or AXUtilities.is_code(obj)):
            return []

        return [object_properties.EOL_INDICATOR_BRAILLE]


    ################################### PER-ROLE ####################################

    def _generate_default_prefix(self, obj, **args):
        """Provides the default/role-agnostic information to present before obj."""

        if args.get("includeContext") is False:
            return []

        if args.get("isProgressBarUpdate"):
            return []

        if self._script.get_table_navigator().last_input_event_was_navigation_command():
            return []

        # For multiline text areas, we only show the context if we are on the very first line,
        # and there is text on that line.
        if self._script.utilities.isTextArea(obj) or AXUtilities.is_label(obj):
            string, start, _end = AXText.get_line_at_offset(obj)
            if start != 0 or not string.strip():
                return []
            if AXUtilities.get_flows_from(obj):
                return []

        result = self._generate_ancestors(obj, **args)
        if result:
            result += [braille.Region(" ")]
        return result

    def _generate_default_presentation(self, obj, **args):
        """Provides a default/role-agnostic presentation of obj."""

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Component(
            obj, self._as_string(
                self._generate_accessible_label_and_name(obj, **args) +
                self._generate_text_content(obj, **args) +
                self._generate_value(obj, **args) +
                self._generate_accessible_role(obj, **args) +
                self._generate_state_required(obj, **args) +
                self._generate_state_invalid(obj, **args)))]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_default_suffix(self, obj, **args):
        """Provides the default/role-agnostic information to present after obj."""

        result = []
        description = self._generate_accessible_description(obj, **args)
        if description:
            result += [braille.Region(" ")]
            result += [braille.Component(obj, self._as_string(description))]

        return result

    def _generate_text_object(self, obj, **args):
        """Provides a default/role-agnostic generation of text objects."""

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Text(
            obj,
            self._as_string(
                self._generate_accessible_label_and_name(obj, **args) \
                    or self._generate_accessible_placeholder_text(obj, **args)),
            self._as_string(self._generate_eol(obj, **args)),
            args.get("startOffset"),
            args.get("endOffset"),
            args.get("caretOffset"))]

        # TODO - JD: The lines below reflect what we've been doing, but only make sense
        # for text fields. Historically we've also used generic text object generation
        # for things like paragraphs. For now, maintain the original logic so that we can
        # land the refactor. Then follow up with improvements.
        invalid = self._generate_state_invalid(obj, **args)
        if invalid:
            result += [braille.Region(" " + self._as_string(invalid))]

        required = self._generate_state_required(obj, **args)
        if required:
            result +=[braille.Region(" " + self._as_string(required))]

        readonly = self._generate_state_read_only(obj, **args)
        if readonly:
            result +=[braille.Region(" " + self._as_string(readonly))]

        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_accelerator_label(self, obj, **args):
        """Generates braille for the accelerator-label role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_alert(self, obj, **args):
        """Generates braille for the alert role."""

        if self._generate_text_substring(obj, **args):
            return self._generate_text_object(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Component(
            obj, self._as_string(
                self._generate_accessible_label_and_name(obj, **args) +
                self._generate_accessible_role(obj, **args)))]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_animation(self, obj, **args):
        """Generates braille for the animation role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_application(self, obj, **args):
        """Generates braille for the application role."""

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Component(
            obj, self._as_string(
                self._generate_accessible_label_and_name(obj, **args) +
                self._generate_accessible_role(obj, **args)))]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_arrow(self, obj, **args):
        """Generates braille for the arrow role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_article(self, obj, **args):
        """Generates braille for the article role."""

        if self._generate_text_substring(obj, **args):
            return self._generate_text_object(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Component(
            obj, self._as_string(
                self._generate_accessible_label_and_name(obj, **args) +
                self._generate_accessible_role(obj, **args)))]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_article_in_feed(self, obj, **args):
        """Generates braille for the article role when the article is in a feed."""

        if self._generate_text_substring(obj, **args):
            return self._generate_text_object(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Component(
            obj, self._as_string(
                self._generate_accessible_label_and_name(obj, **args) +
                self._generate_accessible_role(obj, **args)))]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_audio(self, obj, **args):
        """Generates braille for the audio role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_autocomplete(self, obj, **args):
        """Generates braille for the autocomplete role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_block_quote(self, obj, **args):
        """Generates braille for the block-quote role."""

        result = self._generate_text_object(obj, **args)
        result += [braille.Region(" " + self._as_string(
            self._generate_accessible_role(obj, **args) +
            self._generate_nesting_level(obj, **args)))]
        return result

    def _generate_calendar(self, obj, **args):
        """Generates braille for the calendar role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_canvas(self, obj, **args):
        """Generates braille for the canvas role."""

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Component(
            obj, self._as_string(
                self._generate_accessible_label_and_name(obj, **args) +
                (self._generate_accessible_image_description(obj, **args) \
                    or self._generate_accessible_role(obj, **args))))]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_caption(self, obj, **args):
        """Generates braille for the caption role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_chart(self, obj, **args):
        """Generates braille for the chart role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_check_box(self, obj, **args):
        """Generates braille for the check-box role."""

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Component(
            obj, self._as_string(
                self._generate_accessible_label_and_name(obj, **args) +
                self._generate_accessible_role(obj, **args)),
            indicator=self._as_string(self._generate_state_checked(obj, **args)))]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_check_menu_item(self, obj, **args):
        """Generates braille for the check-menu-item role."""

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Component(
            obj, self._as_string(
                self._generate_accessible_label_and_name(obj, **args) +
                self._generate_accessible_role(obj, **args) +
                self._generate_keyboard_accelerator(obj, **args)),
            indicator=self._as_string(self._generate_state_checked(obj, **args)))]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_color_chooser(self, obj, **args):
        """Generates braille for the color-chooser role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_column_header(self, obj, **args):
        """Generates braille for the column-header role."""

        if self._generate_text_substring(obj, **args):
            line = self._generate_text_line(obj, **args)
        else:
            line = self._generate_accessible_label_and_name(obj, **args)

        result = [braille.Component(
            obj, self._as_string(
                line + self._generate_accessible_role(obj, **args) + \
                    self._generate_table_sort_order(obj, **args)))]

        return result

    def _generate_combo_box(self, obj, **args):
        """Generates braille for the combo-box role."""

        result = self._generate_default_prefix(obj, **args)
        label = self._generate_accessible_label_and_name(obj, **args)
        if label:
            offset = len(label[0]) + 1
        else:
            offset = 0

        result += [braille.Component(
            obj, self._as_string(label +
                               self._generate_value(obj, **args) +
                               self._generate_accessible_role(obj, **args)), offset)]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_comment(self, obj, **args):
        """Generates braille for the comment role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_content_deletion(self, obj, **args):
        """Generates braille for the content-deletion role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_content_error(self, obj, **args):
        """Generates braille for a role with a content-related error."""

        return self._generate_default_presentation(obj, **args)

    def _generate_content_insertion(self, obj, **args):
        """Generates braille for the content-insertion role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_date_editor(self, obj, **args):
        """Generates braille for the date-editor role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_definition(self, obj, **args):
        """Generates braille for the definition role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_description_list(self, obj, **args):
        """Generates braille for the description-list role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_description_term(self, obj, **args):
        """Generates braille for the description-term role."""

        result = self._generate_text_object(obj, **args)
        result += [braille.Region(" " + self._as_string(
            self._generate_term_value_count(obj, **args)))]
        return result

    def _generate_description_value(self, obj, **args):
        """Generates braille for the description-value role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_desktop_frame(self, obj, **args):
        """Generates braille for the desktop-frame role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_desktop_icon(self, obj, **args):
        """Generates braille for the desktop-icon role."""

        return self._generate_icon(obj, **args)

    def _generate_dial(self, obj, **args):
        """Generates braille for the dial role."""

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Component(
            obj, self._as_string(
                self._generate_accessible_label_and_name(obj, **args) +
                self._generate_value(obj, **args) +
                self._generate_accessible_role(obj, **args)))]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_dialog(self, obj, **args):
        """Generates braille for the dialog role."""

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Component(
            obj, self._as_string(
                self._generate_accessible_label_and_name(obj, **args) +
                self._generate_accessible_role(obj, **args) +
                self._generate_accessible_static_text(obj, **args)))]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_directory_pane(self, obj, **args):
        """Generates braille for the directory_pane role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_document(self, obj, **args):
        """Generates braille for document-related roles."""

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Text(
            obj, "",
            self._as_string(self._generate_eol(obj, **args)),
            args.get("startOffset"),
            args.get("endOffset"))]
        return result

    def _generate_document_email(self, obj, **args):
        """Generates braille for the document-email role."""

        return self._generate_document(obj, **args)

    def _generate_document_frame(self, obj, **args):
        """Generates braille for the document-frame role."""

        return self._generate_document(obj, **args)

    def _generate_document_presentation(self, obj, **args):
        """Generates braille for the document-presentation role."""

        return self._generate_document(obj, **args)

    def _generate_document_spreadsheet(self, obj, **args):
        """Generates braille for the document-spreadsheet role."""

        return self._generate_document(obj, **args)

    def _generate_document_text(self, obj, **args):
        """Generates braille for the document-text role."""

        return self._generate_document(obj, **args)

    def _generate_document_web(self, obj, **args):
        """Generates braille for the document-web role."""

        return self._generate_document(obj, **args)

    def _generate_dpub_landmark(self, obj, **args):
        """Generates braille for the dpub section role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_dpub_section(self, obj, **args):
        """Generates braille for the dpub section role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_drawing_area(self, obj, **args):
        """Generates braille for the drawing-area role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_editbar(self, obj, **args):
        """Generates braille for the editbar role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_embedded(self, obj, **args):
        """Generates braille for the embedded role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_entry(self, obj, **args):
        """Generates braille for the entry role."""

        return self._generate_text_object(obj, **args)

    def _generate_feed(self, obj, **args):
        """Generates braille for the feed role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_file_chooser(self, obj, **args):
        """Generates braille for the file-chooser role."""

        return self._generate_dialog(obj, **args)

    def _generate_filler(self, obj, **args):
        """Generates braille for the filler role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_font_chooser(self, obj, **args):
        """Generates braille for the font-chooser role."""

        return self._generate_dialog(obj, **args)

    def _generate_footer(self, obj, **args):
        """Generates braille for the footer role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_footnote(self, obj, **args):
        """Generates braille for the footnote role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_form(self, obj, **args):
        """Generates braille for the form role."""

        if self._generate_text_substring(obj, **args):
            return self._generate_text_object(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Component(
            obj, self._as_string(
                self._generate_accessible_label_and_name(obj, **args) +
                self._generate_accessible_role(obj, **args)))]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_frame(self, obj, **args):
        """Generates braille for the frame role."""

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Component(
            obj, self._as_string(
                self._generate_accessible_label_and_name(obj, **args) +
                self._generate_accessible_role(obj, **args) +
                self._generate_alert_and_dialog_count(obj, **args)))]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_glass_pane(self, obj, **args):
        """Generates braille for the glass-pane role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_grouping(self, obj, **args):
        """Generates braille for the grouping role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_header(self, obj, **args):
        """Generates braille for the header role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_heading(self, obj, **args):
        """Generates braille for the heading role."""

        result = self._generate_text_object(obj, **args)
        result += [braille.Region(" " + self._as_string(
            self._generate_accessible_role(obj, **args)))]
        return result

    def _generate_html_container(self, obj, **args):
        """Generates braille for the html-container role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_icon(self, obj, **args):
        """Generates braille for the icon role."""

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Component(
            obj, self._as_string(
                self._generate_accessible_label_and_name(obj, **args) +
                (self._generate_accessible_image_description(obj, **args) \
                    or self._generate_accessible_role(obj, **args))))]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_image(self, obj, **args):
        """Generates braille for the image role."""

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Component(
            obj, self._as_string(
                self._generate_accessible_label_and_name(obj, **args) +
                self._generate_accessible_role(obj, **args)))]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_image_map(self, obj, **args):
        """Generates braille for the image-map role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_info_bar(self, obj, **args):
        """Generates braille for the info-bar role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_input_method_window(self, obj, **args):
        """Generates braille for the input-method-window role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_internal_frame(self, obj, **args):
        """Generates braille for the internal-frame role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_label(self, obj, **args):
        """Generates braille for the label role."""

        return self._generate_text_object(obj, **args)

    def _generate_landmark(self, obj, **args):
        """Generates braille for the landmark role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_layered_pane(self, obj, **args):
        """Generates braille for the layered-pane role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_level_bar(self, obj, **args):
        """Generates braille for the level-bar role."""

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Component(
            obj, self._as_string(
                self._generate_accessible_label_and_name(obj, **args) +
                self._generate_value(obj, **args) +
                self._generate_accessible_role(obj, **args)))]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_link(self, obj, **args):
        """Generates braille for the link role."""

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Link(
            obj, self._as_string(
                (self._generate_accessible_label_and_name(obj, **args) \
                    or self._generate_text_content(obj, **args))))]

        rolename = self._generate_accessible_role(obj, **args)
        if rolename:
            result += [braille.Region(" " + self._as_string(rolename))]

        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_list(self, obj, **args):
        """Generates braille for the list role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_list_box(self, obj, **args):
        """Generates braille for the list-box role."""

        result = self._generate_default_prefix(obj, **args)
        label = self._generate_accessible_label_and_name(obj, **args)
        if label:
            offset = len(label[0]) + 1
        else:
            offset = 0

        result += [braille.Component(
            obj, self._as_string(label +
                               self._generate_focused_item(obj, **args) +
                               self._generate_accessible_role(obj, **args)), offset)]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_list_item(self, obj, **args):
        """Generates braille for the list-item role."""

        if self._generate_text_substring(obj, **args):
            return self._generate_text_object(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        line = self._generate_text_line(obj, **args)
        if line and AXUtilities.is_editable(obj):
            result += [braille.Text(
                obj,
                "",
                self._as_string(self._generate_eol(obj, **args)),
                args.get("startOffset"),
                args.get("endOffset"),
                args.get("caretOffset"))]
        else:
            result += [braille.Component(
                obj,
                self._as_string(line or self._generate_accessible_label_and_name(obj, **args) +
                self._generate_state_expanded(obj, **args)))]

        level = self._generate_nesting_level(obj, **args)
        if level:
            result += [braille.Region(" " + self._as_string(level))]

        result += self._generate_descendants(obj, **args)
        return result

    def _generate_log(self, obj, **args):
        """Generates braille for the log role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_mark(self, obj, **args):
        """Generates braille for the mark role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_marquee(self, obj, **args):
        """Generates braille for the marquee role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_math(self, obj, **args):
        """Generates braille for the math role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_math_enclosed(self, obj, **args):
        """Generates braille for the math-enclosed role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_math_fenced(self, obj, **args):
        """Generates braille for the math-fenced role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_math_fraction(self, obj, **args):
        """Generates braille for the math-fraction role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_math_multiscript(self, obj, **args):
        """Generates braille for the math-multiscript role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_math_root(self, obj, **args):
        """Generates braille for the math-root role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_math_row(self, obj, **args):
        """Generates braille for the math-row role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_math_script_subsuper(self, obj, **args):
        """Generates braille for the math script subsuper role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_math_script_underover(self, obj, **args):
        """Generates braille for the math script underover role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_math_table(self, obj, **args):
        """Generates braille for the math-table role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_menu(self, obj, **args):
        """Generates braille for the menu role."""

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Component(
            obj, self._as_string(
                self._generate_accessible_label_and_name(obj, **args) +
                self._generate_accessible_role(obj, **args)))]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_menu_bar(self, obj, **args):
        """Generates braille for the menu-bar role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_menu_item(self, obj, **args):
        """Generates braille for the menu-item role."""

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Component(
            obj, self._as_string(
                self._generate_accessible_label_and_name(obj, **args) +
                self._generate_state_expanded(obj, **args) +
                self._generate_keyboard_accelerator(obj, **args)),
            indicator=self._as_string(self._generate_state_checked_if_checkable(obj, **args)))]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_notification(self, obj, **args):
        """Generates braille for the notification role."""

        if self._generate_text_substring(obj, **args):
            return self._generate_text_object(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Component(
            obj, self._as_string(
                self._generate_accessible_label_and_name(obj, **args) +
                self._generate_accessible_role(obj, **args)))]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_option_pane(self, obj, **args):
        """Generates braille for the option-pane role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_page(self, obj, **args):
        """Generates braille for the page role."""

        return self._generate_text_object(obj, **args)

    def _generate_page_tab(self, obj, **args):
        """Generates braille for the page-tab role."""

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Component(
            obj, self._as_string(
                self._generate_accessible_label_and_name(obj, **args) +
                self._generate_accessible_role(obj, **args) +
                self._generate_keyboard_accelerator(obj, **args)))]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_page_tab_list(self, obj, **args):
        """Generates braille for the page-tab-list role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_panel(self, obj, **args):
        """Generates braille for the panel role."""

        if self._generate_text_substring(obj, **args):
            return self._generate_text_object(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Component(
            obj, self._as_string(
                self._generate_accessible_label_and_name(obj, **args) +
                self._generate_accessible_role(obj, **args)))]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_paragraph(self, obj, **args):
        """Generates braille for the paragraph role."""

        return self._generate_text_object(obj, **args)

    def _generate_password_text(self, obj, **args):
        """Generates braille for the password-text role."""

        return self._generate_text_object(obj, **args)

    def _generate_popup_menu(self, obj, **args):
        """Generates braille for the popup-menu role."""

        return self._generate_menu(obj, **args)

    def _generate_progress_bar(self, obj, **args):
        """Generates braille for the progress-bar role."""

        if not args.get("isProgressBarUpdate") \
           or not self._should_present_progress_bar_update(obj, **args):
            return []

        value = self._generate_progress_bar_value(obj, **args)
        if not value:
            return []

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Component(
            obj, self._as_string(
                self._generate_accessible_label_and_name(obj, **args) +
                value +
                self._generate_accessible_role(obj, **args) +
                self._generate_progress_bar_index(obj, **args)))]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_push_button(self, obj, **args):
        """Generates braille for the push-button role."""

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Component(
            obj, self._as_string(
                self._generate_accessible_label_and_name(obj, **args) +
                self._generate_state_expanded(obj, **args) +
                self._generate_accessible_role(obj, **args)))]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_push_button_menu(self, obj, **args):
        """Generates braille for the push-button-menu role."""

        return self._generate_push_button(obj, **args)

    def _generate_radio_button(self, obj, **args):
        """Generates braille for the radio-button role."""

        result = self._generate_default_prefix(obj, **args)
        group = self._generate_radio_button_group(obj, **args)
        if group:
            result += [braille.Region(" " + self._as_string(group))]

        result += [braille.Component(
            obj, self._as_string(
                self._generate_accessible_label_and_name(obj, **args) +
                self._generate_accessible_role(obj, **args)),
            indicator=self._as_string(self._generate_state_selected_for_radio_button(obj, **args)))]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_radio_menu_item(self, obj, **args):
        """Generates braille for the radio-menu-item role."""

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Component(
            obj, self._as_string(
                self._generate_accessible_label_and_name(obj, **args) +
                self._generate_accessible_role(obj, **args) +
                self._generate_keyboard_accelerator(obj, **args)),
            indicator=self._as_string(self._generate_state_selected_for_radio_button(obj, **args)))]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_rating(self, obj, **args):
        """Generates braille for the rating role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_region(self, obj, **args):
        """Generates braille for the region landmark role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_root_pane(self, obj, **args):
        """Generates braille for the root-pane role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_row_header(self, obj, **args):
        """Generates braille for the row-header role."""

        if self._generate_text_substring(obj, **args):
            line = self._generate_text_line(obj, **args)
        else:
            line = self._generate_accessible_label_and_name(obj, **args)

        result = [braille.Component(
            obj, self._as_string(
                line + self._generate_accessible_role(obj, **args) +\
                    self._generate_table_sort_order(obj, **args)))]

        return result

    def _generate_ruler(self, obj, **args):
        """Generates braille for the ruler role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_scroll_bar(self, obj, **args):
        """Generates braille for the scroll-bar role."""

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Component(
            obj, self._as_string(
                self._generate_accessible_label_and_name(obj, **args) +
                self._generate_value(obj, **args) +
                self._generate_accessible_role(obj, **args)))]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_scroll_pane(self, obj, **args):
        """Generates braille for the scroll-pane role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_section(self, obj, **args):
        """Generates braille for the section role."""

        return self._generate_text_object(obj, **args)

    def _generate_separator(self, obj, **args):
        """Generates braille for the separator role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_slider(self, obj, **args):
        """Generates braille for the slider role."""

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Component(
            obj, self._as_string(
                self._generate_accessible_label_and_name(obj, **args) +
                self._generate_value(obj, **args) +
                self._generate_accessible_role(obj, **args)))]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_spin_button(self, obj, **args):
        """Generates braille for the spin-button role."""

        return self._generate_text_object(obj, **args)

    def _generate_split_pane(self, obj, **args):
        """Generates braille for the split-pane role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_static(self, obj, **args):
        """Generates braille for the static role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_status_bar(self, obj, **args):
        """Generates braille for the status-bar role."""

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Component(
            obj, self._as_string(
                self._generate_accessible_label_and_name(obj, **args) +
                self._generate_accessible_role(obj, **args)))]
        result += [braille.Region(" ")]
        result += self._generate_descendants(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_subscript(self, obj, **args):
        """Generates braille for the subscript role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_suggestion(self, obj, **args):
        """Generates braille for the suggestion role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_superscript(self, obj, **args):
        """Generates braille for the superscript role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_switch(self, obj, **args):
        """Generates braille for the switch role."""

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Component(
            obj, self._as_string(
                self._generate_accessible_label_and_name(obj, **args) +
                self._generate_accessible_role(obj, **args)),
            indicator=self._as_string(self._generate_state_checked_for_switch(obj, **args)))]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_table(self, obj, **args):
        """Generates braille for the table role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_table_cell(self, obj, **args):
        """Generates braille for the table-cell role."""

        suffix = []
        node_level = self._generate_tree_item_level(obj, **args)
        if node_level:
            suffix += [braille.Region(" " + self._as_string(node_level))]

        if self._generate_text_substring(obj, **args):
            result = self._generate_text_object(obj, **args)
            result += suffix
            return result

        result = []
        result += self._generate_state_checked_for_cell(obj, **args)
        result += [braille.Component(
            obj, self._as_string(
                self._generate_column_header_if_toggle_and_no_text(obj, **args) +
                (self._generate_real_active_descendant_displayed_text(obj, **args) \
                    or self._generate_accessible_label_and_name(obj, **args)) +
                self._generate_state_expanded(obj, **args)))]
        result += suffix
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_table_cell_in_row(self, obj, **args):
        """Generates braille for the table-cell role in the context of its row."""

        if self._generate_text_substring(obj, **args):
            return self._generate_text_object(obj, **args)

        args["includeContext"] = False
        result = self._generate_default_prefix(obj, **args)
        row_header = self._generate_table_cell_row_header(obj, **args)
        if row_header:
            result += [braille.Region(" " + self._as_string(row_header))]
        column_header = self._generate_table_cell_column_header(obj, **args)
        if column_header:
            result += [braille.Region(" " + self._as_string(column_header))]
        if row_header or column_header:
            result += [braille.Region(" ")]
        result += self._generate_table_cell_row(obj, **args)
        return result

    def _generate_table_column_header(self, obj, **args):
        """Generates braille for the table-column-header role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_table_row(self, obj, **args):
        """Generates braille for the table-row role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_table_row_header(self, obj, **args):
        """Generates braille for the table-row-header role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_tearoff_menu_item(self, obj, **args):
        """Generates braille for the tearoff-menu-item role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_terminal(self, obj, **_args):
        """Generates braille for the terminal role."""

        return [braille.Text(obj)]

    def _generate_text(self, obj, **args):
        """Generates braille for the text role."""

        return self._generate_text_object(obj, **args)

    def _generate_timer(self, obj, **args):
        """Generates braille for the timer role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_title_bar(self, obj, **args):
        """Generates braille for the title-bar role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_toggle_button(self, obj, **args):
        """Generates braille for the toggle-button role."""

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Component(
            obj, self._as_string(
                self._generate_accessible_label_and_name(obj, **args) +
                self._generate_state_expanded(obj, **args) +
                self._generate_accessible_role(obj, **args)),
            indicator=self._as_string(self._generate_state_pressed(obj, **args)))]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_tool_bar(self, obj, **args):
        """Generates braille for the tool-bar role."""

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Component(
            obj, self._as_string(
                self._generate_accessible_label_and_name(obj, **args) +
                self._generate_accessible_role(obj, **args)))]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_tool_tip(self, obj, **args):
        """Generates braille for the tool-tip role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_tree(self, obj, **args):
        """Generates braille for the tree role."""

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Component(
            obj, self._as_string(
                self._generate_accessible_label_and_name(obj, **args) +
                self._generate_accessible_role(obj, **args)))]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_tree_item(self, obj, **args):
        """Generates braille for the tree-item role."""

        if self._generate_text_substring(obj, **args):
            result = self._generate_text_object(obj, **args)
        else:
            result = [braille.Component(
                obj, self._as_string(
                    self._generate_accessible_label_and_name(obj, **args) +
                    self._generate_state_expanded(obj, **args)))]

        node_level = self._generate_tree_item_level(obj, **args)
        if node_level:
            result +=[braille.Region(" " + self._as_string(node_level))]

        return result

    def _generate_tree_table(self, obj, **args):
        """Generates braille for the tree-table role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_unknown(self, obj, **args):
        """Generates braille for the unknown role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_video(self, obj, **args):
        """Generates braille for the video role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_viewport(self, obj, **args):
        """Generates braille for the viewport role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_window(self, obj, **args):
        """Generates braille for the window role."""

        return self._generate_default_presentation(obj, **args)
