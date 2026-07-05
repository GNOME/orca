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
# pylint: disable=too-many-locals
# pylint: disable=unused-argument

"""Produces braille presentation for accessible objects."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Any

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from . import (
    braille,
    debug,
    generator,
    math_presenter,
    messages,
    object_properties,
    table_navigator,
)
from .ax_object import AXObject
from .ax_text import AXText
from .ax_utilities import AXUtilities
from .braille_rolenames import short_role_names
from .generator import (
    ContentItem,
    ContentPosition,
    GeneratorContext,
    GeneratorMode,
    PresentationReason,
)

if TYPE_CHECKING:
    from . import script


@dataclass(frozen=True)
class BrailleGeneratorContext(GeneratorContext):
    """Settings context for braille generators."""

    full_rolenames: bool
    display_ancestors: bool
    end_of_line_indicator: bool
    present_mnemonics: bool
    indicate_links: bool


class Space:
    """A dummy class to indicate we want to insert a space into an
    utterance, but only if there is text prior to the space."""

    def __init__(self, delimiter: str = " ") -> None:
        self.delimiter = delimiter


SPACE = [Space()]


class BrailleGenerator(generator.Generator):
    """Produces a list of braille Regions for accessible objects."""

    _context: BrailleGeneratorContext

    SKIP_CONTEXT_ROLES = (
        Atspi.Role.MENU,
        Atspi.Role.MENU_BAR,
        Atspi.Role.PAGE_TAB_LIST,
        Atspi.Role.REDUNDANT_OBJECT,
        Atspi.Role.UNKNOWN,
        Atspi.Role.COMBO_BOX,
    )

    def __init__(self, script: script.Script) -> None:
        super().__init__(script, GeneratorMode.BRAILLE)

    @staticmethod
    def log_generator_output(func):
        """Decorator for logging."""

        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            tokens = [f"BRAILLE GENERATOR: {func.__name__}:", result]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return result

        return wrapper

    def generate_braille(
        self,
        obj: Atspi.Accessible,
        context: BrailleGeneratorContext,
        *,
        role: Atspi.Role | str | None = None,
        include_context: bool = True,
    ) -> list[Any]:
        """Returns a [result, focused_region] list for presenting obj."""

        self._context = context
        return self._generate_braille(obj, role=role, include_context=include_context)

    def _generate_braille(
        self,
        obj: Atspi.Accessible,
        *,
        role: Atspi.Role | str | None = None,
        include_context: bool = True,
    ) -> list[Any]:
        if not self._context.enabled:
            return [[], None]

        result = self.generate(obj, role=role, include_context=include_context)

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
        except IndexError:
            focused_region = None

        for region in result:
            if isinstance(region, (braille.Component, braille.Text)) and region.accessible == obj:
                focused_region = region
                break
            if (
                isinstance(region, braille.Text)
                and AXUtilities.is_combo_box(obj)
                and AXObject.get_parent(region.accessible) == obj
            ):
                focused_region = region
                break
            if (
                isinstance(region, braille.Component)
                and AXUtilities.is_table_cell(obj)
                and AXObject.get_parent(region.accessible) == obj
            ):
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
            tokens = [
                "BRAILLE GENERATOR: Could not determine focused region for",
                obj,
                "Candidates:",
                candidates,
            ]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            if len(candidates) == 1:
                focused_region = candidates[0]

        return [result, focused_region]

    def _needs_separator(self, last_char: str, next_char: str) -> bool:
        if last_char.isspace() or next_char.isspace():
            return False

        opening_punctuation = ["(", "[", "{", "<"]
        closing_punctuation = [".", "?", "!", ":", ",", ";", ")", "]", "}", ">"]
        if last_char in closing_punctuation or next_char in opening_punctuation:
            return True
        if last_char in opening_punctuation or next_char in closing_punctuation:
            return False

        return last_char.isalnum()

    def generate_contents(  # type: ignore[override]
        self,
        contents: list[tuple[Atspi.Accessible, int, int, str]],
        context: BrailleGeneratorContext,
    ) -> tuple[list[list[Any]], Atspi.Accessible | None]:
        """Generates braille for the specified contents."""

        self._context = context
        return self._generate_contents(contents)

    def _generate_contents(
        self,
        contents: list[tuple[Atspi.Accessible, int, int, str]],
    ) -> tuple[list[list[Any]], Atspi.Accessible | None]:
        result = []
        last_region = None
        focused_region = None
        obj, offset = self._script.utilities.get_caret_context()
        original_context = self._context
        for i, content in enumerate(contents):
            acc, start, end, string = content
            item_context = replace(
                original_context,
                content_item=ContentItem(
                    start_offset=start, end_offset=end, string=string, caret_offset=offset
                ),
                content_position=ContentPosition(index=i, total=len(contents)),
                content_subject=acc,
            )
            regions, f_region = self.generate_braille(acc, item_context)
            if not regions:
                continue

            if acc == obj and start <= offset < end:
                focused_region = f_region

            if last_region and regions:
                last_char = next_char = ""
                if last_region.string:
                    last_char = last_region.string[-1]
                if regions[0].string:
                    next_char = regions[0].string[0]
                if self._needs_separator(last_char, next_char):
                    regions.insert(0, braille.Region(" "))

            last_region = regions[-1]
            result.append(regions)

        self._context = original_context
        return result, focused_region

    def get_localized_role_name(
        self, obj: Atspi.Accessible, *, role: Atspi.Role | str | None = None
    ) -> str:
        if self._context is not None and not self._context.full_rolenames:
            rv = short_role_names.get(role if role is not None else self._get_resolved_role(obj))
            if rv:
                return rv

        return super().get_localized_role_name(obj, role=role)

    def _as_string(self, content: Any, delimiter: str = " ") -> str:
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
                    if combined and prior:
                        combined = f"{combined}{delimiter}{prior}"
                    elif not combined:
                        combined = prior
        return combined

    def _generate_result_separator(self, obj: Atspi.Accessible) -> list[Any]:
        return [braille.Region(" ")]

    ################################# BASIC DETAILS #################################

    @log_generator_output
    def _generate_accessible_role(self, obj: Atspi.Accessible) -> list[Any]:
        result = []
        role = self._get_resolved_role(obj)
        do_not_present = [
            Atspi.Role.UNKNOWN,
            Atspi.Role.REDUNDANT_OBJECT,
            Atspi.Role.FILLER,
            Atspi.Role.EXTENDED,
            Atspi.Role.LINK,
        ]

        # egg-list-box, e.g. privacy panel in gnome-control-center
        if AXUtilities.is_list_box(AXObject.get_parent(obj)):
            do_not_present.append(AXObject.get_role(obj))

        is_verbose = self._context.verbose
        if not is_verbose:
            do_not_present.extend([Atspi.Role.ICON, Atspi.Role.CANVAS])

        level = AXUtilities.get_heading_level(obj)
        if level:
            result.append(object_properties.ROLE_HEADING_LEVEL_BRAILLE % level)
        elif is_verbose and role not in do_not_present:
            result.append(self.get_localized_role_name(obj))
        return result

    @log_generator_output
    def _generate_alert_and_dialog_count(self, obj: Atspi.Accessible) -> list[Any]:
        result = []
        alert_and_dialog_count = len(AXUtilities.get_unfocused_alerts_and_dialogs(obj))
        if alert_and_dialog_count > 0:
            result.append(messages.dialog_count_braille(alert_and_dialog_count))

        return result

    @log_generator_output
    def _generate_ancestors(self, obj: Atspi.Accessible) -> list[Any]:
        if not self._context.display_ancestors:
            return []
        if table_navigator.get_navigator().last_input_event_was_navigation_command():
            return []

        result: list[Any] = []
        original_context = self._context
        self._context = replace(original_context, ancestor_of=obj)
        parent = AXObject.get_parent_checked(obj)
        if parent and (AXObject.get_role(parent) in self.SKIP_CONTEXT_ROLES):
            parent = AXObject.get_parent_checked(parent)
        while parent:
            parent_result = []
            if not AXUtilities.is_layout_only(parent):
                parent_result = self.generate(parent, include_context=False)
            if result and parent_result:
                result.append(braille.Region(" "))
            result.extend(parent_result)
            parent = AXObject.get_parent_checked(parent)
        self._context = original_context
        result.reverse()
        return result

    ################################### KEYBOARD ###################################

    def _generate_keyboard_accelerator(self, obj: Atspi.Accessible) -> list[Any]:
        if not self._context.verbose:
            return []

        result = []
        accelerator = AXUtilities.get_accelerator(obj)
        if accelerator:
            result.append("(" + accelerator + ")")
        return result

    def _generate_keyboard_mnemonic(self, obj: Atspi.Accessible) -> list[Any]:
        if not (
            self._context.present_mnemonics
            or self._get_reason() == PresentationReason.WHERE_AM_I_DETAILED
        ):
            return []

        return super()._generate_keyboard_mnemonic(obj)

    ################################ PROGRESS BARS ##################################

    @log_generator_output
    def _generate_progress_bar_index(self, obj: Atspi.Accessible) -> list[Any]:
        acc = self._get_most_recent_progress_bar_update()[0]
        if acc != obj:
            number = self._get_progress_bar_number_and_count(obj)[0]
            return [f"{number}"]

        return []

    @log_generator_output
    def _generate_progress_bar_value(self, obj: Atspi.Accessible) -> list[Any]:
        result = self._generate_value_as_percentage(obj)
        if self._context is not None and obj == self._context.focus and not result:
            return [""]

        return result

    ##################################### TEXT ######################################

    @log_generator_output
    def _generate_eol(self, obj: Atspi.Accessible) -> list[Any]:
        if not self._context.end_of_line_indicator:
            return []

        if not (
            AXUtilities.is_editable(obj)
            or AXUtilities.is_code_block_descendant(obj, inclusive=True)
        ):
            return []

        return [object_properties.EOL_INDICATOR_BRAILLE]

    ################################### PER-ROLE ####################################

    def _generate_default_prefix(self, obj: Atspi.Accessible) -> list[Any]:
        """Provides the default/role-agnostic information to present before obj."""

        if not self._include_context():
            return []

        if self._is_progress_bar_update():
            return []

        if table_navigator.get_navigator().last_input_event_was_navigation_command():
            return []

        # For multiline text areas, we only show the context if we are on the very first line,
        # and there is text on that line.
        is_text_area = AXUtilities.is_editable(obj) or AXUtilities.is_terminal(obj)
        if is_text_area or AXUtilities.is_label(obj):
            string, start, _end = AXText.get_line_at_offset(obj)
            if start != 0 or not string.strip():
                return []
            if AXUtilities.get_flows_from(obj):
                return []

        result = self._generate_ancestors(obj)
        if result:
            result += [braille.Region(" ")]
        return result

    def _generate_default_presentation(self, obj: Atspi.Accessible) -> list[Any]:
        """Provides a default/role-agnostic presentation of obj."""

        if self._is_ancestor():
            result = [
                braille.Component(
                    obj,
                    self._as_string(
                        self._generate_accessible_label_and_name(obj)
                        + self._generate_accessible_role(obj),
                    ),
                ),
            ]
            return result

        result = self._generate_default_prefix(obj)
        result += [
            braille.Component(
                obj,
                self._as_string(
                    self._generate_accessible_label_and_name(obj)
                    + self._generate_text_content(obj)
                    + self._generate_value(obj)
                    + self._generate_accessible_role(obj)
                    + self._generate_state_required(obj)
                    + self._generate_state_invalid(obj)
                    + self._generate_keyboard_mnemonic(obj),
                ),
            ),
        ]
        result += self._generate_default_suffix(obj)
        return result

    def _generate_default_suffix(self, obj: Atspi.Accessible) -> list[Any]:
        """Provides the default/role-agnostic information to present after obj."""

        result = []
        description = self._generate_accessible_description(obj)
        if description:
            result += [braille.Region(" ")]
            result += [braille.Component(obj, self._as_string(description))]
        current = self._generate_state_current(obj)
        if current:
            result += [braille.Region(" ")]
            result += [braille.Component(obj, self._as_string(current))]

        return result

    def _generate_text_object(self, obj: Atspi.Accessible) -> list[Any]:
        """Provides a default/role-agnostic generation of text objects."""

        result = self._generate_default_prefix(obj)
        result += [
            braille.Text(
                obj,
                self._as_string(
                    self._generate_accessible_label_and_name(obj)
                    or self._generate_accessible_placeholder_text(obj),
                ),
                self._as_string(
                    self._generate_eol(obj) + self._generate_keyboard_mnemonic(obj),
                ),
                self._get_start_offset(obj),
                self._get_end_offset(obj),
                self._get_caret_offset(obj, self._get_offset()),
                indicate_links=self._context.indicate_links,
            ),
        ]

        # TODO - JD: The lines below reflect what we've been doing, but only make sense
        # for text fields. Historically we've also used generic text object generation
        # for things like paragraphs. For now, maintain the original logic so that we can
        # land the refactor. Then follow up with improvements.
        invalid = self._generate_state_invalid(obj)
        if invalid:
            result += [braille.Region(" " + self._as_string(invalid))]

        required = self._generate_state_required(obj)
        if required:
            result += [braille.Region(" " + self._as_string(required))]

        readonly = self._generate_state_read_only(obj)
        if readonly:
            result += [braille.Region(" " + self._as_string(readonly))]

        result += self._generate_default_suffix(obj)
        return result

    def _generate_accelerator_label(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the accelerator-label role."""

        return self._generate_default_presentation(obj)

    def _generate_alert(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the alert role."""

        if self._generate_text_substring(obj):
            return self._generate_text_object(obj)

        result = self._generate_default_prefix(obj)
        result += [
            braille.Component(
                obj,
                self._as_string(
                    self._generate_accessible_label_and_name(obj)
                    + self._generate_accessible_role(obj),
                ),
            ),
        ]
        result += self._generate_default_suffix(obj)
        return result

    def _generate_animation(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the animation role."""

        return self._generate_default_presentation(obj)

    def _generate_application(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the application role."""

        result = self._generate_default_prefix(obj)
        result += [
            braille.Component(
                obj,
                self._as_string(
                    self._generate_accessible_label_and_name(obj)
                    + self._generate_accessible_role(obj),
                ),
            ),
        ]
        result += self._generate_default_suffix(obj)
        return result

    def _generate_arrow(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the arrow role."""

        return self._generate_default_presentation(obj)

    def _generate_article(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the article role."""

        if self._generate_text_substring(obj):
            return self._generate_text_object(obj)

        result = self._generate_default_prefix(obj)
        result += [
            braille.Component(
                obj,
                self._as_string(
                    self._generate_accessible_label_and_name(obj)
                    + self._generate_accessible_role(obj),
                ),
            ),
        ]
        result += self._generate_default_suffix(obj)
        return result

    def _generate_article_in_feed(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the article role when the article is in a feed."""

        if self._generate_text_substring(obj):
            return self._generate_text_object(obj)

        result = self._generate_default_prefix(obj)
        result += [
            braille.Component(
                obj,
                self._as_string(
                    self._generate_accessible_label_and_name(obj)
                    + self._generate_accessible_role(obj)
                    + self._generate_keyboard_mnemonic(obj),
                ),
            ),
        ]
        result += self._generate_default_suffix(obj)
        return result

    def _generate_audio(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the audio role."""

        return self._generate_default_presentation(obj)

    def _generate_autocomplete(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the autocomplete role."""

        return self._generate_default_presentation(obj)

    def _generate_block_quote(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the block-quote role."""

        result = self._generate_text_object(obj)
        result += [
            braille.Region(
                " "
                + self._as_string(
                    self._generate_accessible_role(obj) + self._generate_nesting_level(obj),
                ),
            ),
        ]
        return result

    def _generate_calendar(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the calendar role."""

        return self._generate_default_presentation(obj)

    def _generate_canvas(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the canvas role."""

        result = self._generate_default_prefix(obj)
        result += [
            braille.Component(
                obj,
                self._as_string(
                    self._generate_accessible_label_and_name(obj)
                    + (
                        self._generate_accessible_image_description(obj)
                        or self._generate_accessible_role(obj)
                    ),
                ),
            ),
        ]
        result += self._generate_default_suffix(obj)
        return result

    def _generate_caption(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the caption role."""

        return self._generate_default_presentation(obj)

    def _generate_chart(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the chart role."""

        return self._generate_default_presentation(obj)

    def _generate_check_box(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the check-box role."""

        result = self._generate_default_prefix(obj)
        result += [
            braille.Component(
                obj,
                self._as_string(
                    self._generate_accessible_label_and_name(obj)
                    + self._generate_accessible_role(obj)
                    + self._generate_state_required(obj)
                    + self._generate_state_invalid(obj),
                ),
                indicator=self._as_string(self._generate_state_checked(obj)),
            ),
        ]
        result += self._generate_default_suffix(obj)
        return result

    def _generate_check_menu_item(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the check-menu-item role."""

        result = self._generate_default_prefix(obj)
        result += [
            braille.Component(
                obj,
                self._as_string(
                    self._generate_accessible_label_and_name(obj)
                    + self._generate_accessible_role(obj)
                    + self._generate_keyboard_mnemonic(obj)
                    + self._generate_keyboard_accelerator(obj),
                ),
                indicator=self._as_string(self._generate_state_checked(obj)),
            ),
        ]
        result += self._generate_default_suffix(obj)
        return result

    def _generate_color_chooser(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the color-chooser role."""

        return self._generate_default_presentation(obj)

    def _generate_column_header(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the column-header role."""

        if self._generate_text_substring(obj):
            line = self._generate_text_line(obj)
        else:
            line = self._generate_accessible_label_and_name(obj)

        result = [
            braille.Component(
                obj,
                self._as_string(
                    line
                    + self._generate_accessible_role(obj)
                    + self._generate_table_sort_order(obj),
                ),
            ),
        ]

        return result

    def _generate_combo_box(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the combo-box role."""

        if AXUtilities.is_editable(obj):
            return self._generate_text_object(obj)

        result = self._generate_default_prefix(obj)
        label = self._generate_accessible_label_and_name(obj)
        if label:
            offset = len(label[0]) + 1
        else:
            offset = 0

        value = self._generate_value(obj)
        if value and value[0] in self._as_string(label):
            value = []

        result += [
            braille.Component(
                obj,
                self._as_string(
                    label
                    + value
                    + self._generate_accessible_role(obj)
                    + self._generate_keyboard_mnemonic(obj),
                ),
                offset,
            ),
        ]
        result += self._generate_default_suffix(obj)
        return result

    def _generate_code_block(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the code block role."""

        return self._generate_text_object(obj)

    def _generate_comment(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the comment role."""

        return self._generate_default_presentation(obj)

    def _generate_content_deletion(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the content-deletion role."""

        return self._generate_default_presentation(obj)

    def _generate_content_insertion(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the content-insertion role."""

        return self._generate_default_presentation(obj)

    def _generate_date_editor(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the date-editor role."""

        return self._generate_default_presentation(obj)

    def _generate_definition(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the definition role."""

        return self._generate_default_presentation(obj)

    def _generate_description_list(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the description-list role."""

        return self._generate_default_presentation(obj)

    def _generate_description_term(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the description-term role."""

        result = self._generate_text_object(obj)
        result += [
            braille.Region(" " + self._as_string(self._generate_term_value_count(obj))),
        ]
        return result

    def _generate_description_value(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the description-value role."""

        return self._generate_default_presentation(obj)

    def _generate_desktop_frame(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the desktop-frame role."""

        return self._generate_default_presentation(obj)

    def _generate_desktop_icon(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the desktop-icon role."""

        return self._generate_icon(obj)

    def _generate_dial(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the dial role."""

        result = self._generate_default_prefix(obj)
        result += [
            braille.Component(
                obj,
                self._as_string(
                    self._generate_accessible_label_and_name(obj)
                    + self._generate_value(obj)
                    + self._generate_keyboard_mnemonic(obj)
                    + self._generate_accessible_role(obj),
                ),
            ),
        ]
        result += self._generate_default_suffix(obj)
        return result

    def _generate_dialog(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the dialog role."""

        result = self._generate_default_prefix(obj)
        result += [
            braille.Component(
                obj,
                self._as_string(
                    self._generate_accessible_label_and_name(obj)
                    + self._generate_accessible_role(obj)
                    + self._generate_accessible_static_text(obj),
                ),
            ),
        ]
        result += self._generate_default_suffix(obj)
        return result

    def _generate_directory_pane(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the directory_pane role."""

        return self._generate_default_presentation(obj)

    def _generate_document(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for document-related roles."""

        result = self._generate_default_prefix(obj)
        result += [
            braille.Text(
                obj,
                "",
                self._as_string(self._generate_eol(obj)),
                self._get_start_offset(obj),
                self._get_end_offset(obj),
                indicate_links=self._context.indicate_links,
            ),
        ]
        return result

    def _generate_document_email(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the document-email role."""

        return self._generate_document(obj)

    def _generate_document_frame(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the document-frame role."""

        return self._generate_document(obj)

    def _generate_document_presentation(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the document-presentation role."""

        return self._generate_document(obj)

    def _generate_document_spreadsheet(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the document-spreadsheet role."""

        return self._generate_document(obj)

    def _generate_document_text(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the document-text role."""

        return self._generate_document(obj)

    def _generate_document_web(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the document-web role."""

        return self._generate_document(obj)

    def _generate_dpub_landmark(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the dpub section role."""

        return self._generate_default_presentation(obj)

    def _generate_dpub_section(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the dpub section role."""

        return self._generate_default_presentation(obj)

    def _generate_drawing_area(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the drawing-area role."""

        return self._generate_default_presentation(obj)

    def _generate_editbar(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the editbar role."""

        return self._generate_default_presentation(obj)

    def _generate_embedded(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the embedded role."""

        return self._generate_default_presentation(obj)

    def _generate_entry(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the entry role."""

        return self._generate_text_object(obj)

    def _generate_feed(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the feed role."""

        return self._generate_default_presentation(obj)

    def _generate_file_chooser(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the file-chooser role."""

        return self._generate_dialog(obj)

    def _generate_filler(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the filler role."""

        return self._generate_default_presentation(obj)

    def _generate_font_chooser(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the font-chooser role."""

        return self._generate_dialog(obj)

    def _generate_footer(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the footer role."""

        return self._generate_default_presentation(obj)

    def _generate_footnote(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the footnote role."""

        return self._generate_default_presentation(obj)

    def _generate_form(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the form role."""

        if self._generate_text_substring(obj):
            return self._generate_text_object(obj)

        result = self._generate_default_prefix(obj)
        result += [
            braille.Component(
                obj,
                self._as_string(
                    self._generate_accessible_label_and_name(obj)
                    + self._generate_accessible_role(obj),
                ),
            ),
        ]
        result += self._generate_default_suffix(obj)
        return result

    def _generate_frame(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the frame role."""

        result = self._generate_default_prefix(obj)
        result += [
            braille.Component(
                obj,
                self._as_string(
                    self._generate_accessible_label_and_name(obj)
                    + self._generate_accessible_role(obj)
                    + self._generate_alert_and_dialog_count(obj),
                ),
            ),
        ]
        result += self._generate_default_suffix(obj)
        return result

    def _generate_glass_pane(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the glass-pane role."""

        return self._generate_default_presentation(obj)

    def _generate_grouping(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the grouping role."""

        if self._generate_text_substring(obj):
            return self._generate_text_object(obj)

        result = self._generate_default_prefix(obj)
        result += [
            braille.Component(
                obj,
                self._as_string(
                    self._generate_accessible_label_and_name(obj)
                    + self._generate_accessible_role(obj),
                ),
            ),
        ]
        result += self._generate_default_suffix(obj)
        return result

    def _generate_header(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the header role."""

        return self._generate_default_presentation(obj)

    def _generate_heading(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the heading role."""

        result = self._generate_text_object(obj)
        result += [
            braille.Region(" " + self._as_string(self._generate_accessible_role(obj))),
        ]
        return result

    def _generate_html_container(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the html-container role."""

        return self._generate_default_presentation(obj)

    def _generate_icon(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the icon role."""

        result = self._generate_default_prefix(obj)
        result += [
            braille.Component(
                obj,
                self._as_string(
                    self._generate_accessible_label_and_name(obj)
                    + (
                        self._generate_accessible_image_description(obj)
                        or self._generate_accessible_role(obj)
                    ),
                ),
            ),
        ]
        result += self._generate_default_suffix(obj)
        return result

    def _generate_image(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the image role."""

        result = self._generate_default_prefix(obj)
        result += [
            braille.Component(
                obj,
                self._as_string(
                    self._generate_accessible_label_and_name(obj)
                    + self._generate_accessible_role(obj),
                ),
            ),
        ]
        result += self._generate_default_suffix(obj)
        return result

    def _generate_image_map(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the image-map role."""

        return self._generate_default_presentation(obj)

    def _generate_info_bar(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the info-bar role."""

        return self._generate_default_presentation(obj)

    def _generate_input_method_window(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the input-method-window role."""

        return self._generate_default_presentation(obj)

    def _generate_internal_frame(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the internal-frame role."""

        return self._generate_default_presentation(obj)

    def _generate_label(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the label role."""

        return self._generate_text_object(obj)

    def _generate_landmark(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the landmark role."""

        return self._generate_default_presentation(obj)

    def _generate_layered_pane(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the layered-pane role."""

        return self._generate_default_presentation(obj)

    def _generate_level_bar(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the level-bar role."""

        result = self._generate_default_prefix(obj)
        result += [
            braille.Component(
                obj,
                self._as_string(
                    self._generate_accessible_label_and_name(obj)
                    + self._generate_value(obj)
                    + self._generate_accessible_role(obj)
                    + self._generate_keyboard_mnemonic(obj),
                ),
            ),
        ]
        result += self._generate_default_suffix(obj)
        return result

    def _generate_link(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the link role."""

        result = self._generate_default_prefix(obj)
        result += [
            braille.Link(
                obj,
                self._as_string(
                    self._generate_accessible_label_and_name(obj)
                    or self._generate_text_content(obj),
                ),
            ),
        ]
        rolename = self._generate_accessible_role(obj)
        if rolename:
            result += [
                braille.Region(
                    " "
                    + self._as_string(
                        rolename
                        + self._generate_keyboard_mnemonic(obj)
                        + self._generate_keyboard_accelerator(obj),
                    ),
                ),
            ]
        result += self._generate_default_suffix(obj)
        return result

    def _generate_list(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the list role."""

        return self._generate_default_presentation(obj)

    def _generate_list_box(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the list-box role."""

        result = self._generate_default_prefix(obj)
        label = self._generate_accessible_label_and_name(obj)
        if label:
            offset = len(label[0]) + 1
        else:
            offset = 0

        result += [
            braille.Component(
                obj,
                self._as_string(
                    label + self._generate_focused_item(obj) + self._generate_accessible_role(obj),
                ),
                offset,
            ),
        ]
        result += self._generate_default_suffix(obj)
        return result

    def _generate_list_item(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the list-item role."""

        if self._generate_text_substring(obj):
            return self._generate_text_object(obj)

        result = self._generate_default_prefix(obj)
        line = self._generate_text_line(obj)
        if line and AXUtilities.is_editable(obj):
            result += [
                braille.Text(
                    obj,
                    "",
                    self._as_string(self._generate_eol(obj)),
                    self._get_start_offset(obj),
                    self._get_end_offset(obj),
                    self._get_caret_offset(obj),
                    indicate_links=self._context.indicate_links,
                ),
            ]
        else:
            result += [
                braille.Component(
                    obj,
                    self._as_string(
                        line
                        or self._generate_accessible_label_and_name(obj)
                        + self._generate_state_expanded(obj),
                    ),
                ),
            ]

        level = self._generate_nesting_level(obj)
        if level:
            result += [braille.Region(" " + self._as_string(level))]

        if not self._is_ancestor():
            result += self._generate_descendants(obj)
        return result

    def _generate_log(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the log role."""

        return self._generate_default_presentation(obj)

    def _generate_mark(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the mark role."""

        return self._generate_default_presentation(obj)

    def _generate_marquee(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the marquee role."""

        return self._generate_default_presentation(obj)

    def _generate_math(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the math role."""

        if braille_string := math_presenter.get_presenter().get_braille_for_math(obj):
            return [braille.Component(obj, braille_string, contracted=False)]

        return self._generate_default_presentation(obj)

    def _generate_menu(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the menu role."""

        result = self._generate_default_prefix(obj)
        result += [
            braille.Component(
                obj,
                self._as_string(
                    self._generate_accessible_label_and_name(obj)
                    + self._generate_accessible_role(obj)
                    + self._generate_keyboard_mnemonic(obj)
                    + self._generate_keyboard_accelerator(obj),
                ),
            ),
        ]
        result += self._generate_default_suffix(obj)
        return result

    def _generate_menu_bar(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the menu-bar role."""

        return self._generate_default_presentation(obj)

    def _generate_menu_item(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the menu-item role."""

        result = self._generate_default_prefix(obj)
        result += [
            braille.Component(
                obj,
                self._as_string(
                    self._generate_accessible_label_and_name(obj)
                    + self._generate_state_expanded(obj)
                    + self._generate_keyboard_mnemonic(obj)
                    + self._generate_keyboard_accelerator(obj),
                ),
                indicator=self._as_string(self._generate_state_checked_if_checkable(obj)),
            ),
        ]
        result += self._generate_default_suffix(obj)
        return result

    def _generate_notification(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the notification role."""

        if self._generate_text_substring(obj):
            return self._generate_text_object(obj)

        result = self._generate_default_prefix(obj)
        result += [
            braille.Component(
                obj,
                self._as_string(
                    self._generate_accessible_label_and_name(obj)
                    + self._generate_accessible_role(obj),
                ),
            ),
        ]
        result += self._generate_default_suffix(obj)
        return result

    def _generate_option_pane(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the option-pane role."""

        return self._generate_default_presentation(obj)

    def _generate_page(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the page role."""

        return self._generate_text_object(obj)

    def _generate_page_tab(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the page-tab role."""

        result = self._generate_default_prefix(obj)
        result += [
            braille.Component(
                obj,
                self._as_string(
                    self._generate_accessible_label_and_name(obj)
                    + self._generate_accessible_role(obj)
                    + self._generate_keyboard_mnemonic(obj)
                    + self._generate_keyboard_accelerator(obj),
                ),
            ),
        ]
        result += self._generate_default_suffix(obj)
        return result

    def _generate_page_tab_list(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the page-tab-list role."""

        return self._generate_default_presentation(obj)

    def _generate_panel(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the panel role."""

        if self._generate_text_substring(obj):
            return self._generate_text_object(obj)

        result = self._generate_default_prefix(obj)
        result += [
            braille.Component(
                obj,
                self._as_string(
                    self._generate_accessible_label_and_name(obj)
                    + self._generate_accessible_role(obj),
                ),
            ),
        ]
        result += self._generate_default_suffix(obj)
        return result

    def _generate_paragraph(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the paragraph role."""

        return self._generate_text_object(obj)

    def _generate_password_text(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the password-text role."""

        return self._generate_text_object(obj)

    def _generate_popup_menu(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the popup-menu role."""

        return self._generate_menu(obj)

    def _generate_progress_bar(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the progress-bar role."""

        if not self._is_progress_bar_update():
            return []

        value = self._generate_progress_bar_value(obj)
        if not value:
            return []

        result = self._generate_default_prefix(obj)
        result += [
            braille.Component(
                obj,
                self._as_string(
                    self._generate_accessible_label_and_name(obj)
                    + value
                    + self._generate_accessible_role(obj)
                    + self._generate_progress_bar_index(obj),
                ),
            ),
        ]
        result += self._generate_default_suffix(obj)
        return result

    def _generate_push_button(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the push-button role."""

        result = self._generate_default_prefix(obj)
        result += [
            braille.Component(
                obj,
                self._as_string(
                    self._generate_accessible_label_and_name(obj)
                    + self._generate_state_expanded(obj)
                    + self._generate_accessible_role(obj)
                    + self._generate_keyboard_mnemonic(obj)
                    + self._generate_keyboard_accelerator(obj),
                ),
            ),
        ]
        result += self._generate_default_suffix(obj)
        return result

    def _generate_push_button_menu(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the push-button-menu role."""

        return self._generate_push_button(obj)

    def _generate_radio_button(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the radio-button role."""

        result = self._generate_default_prefix(obj)
        group = self._generate_radio_button_group(obj)
        if group:
            result += [braille.Region(" " + self._as_string(group))]

        result += [
            braille.Component(
                obj,
                self._as_string(
                    self._generate_accessible_label_and_name(obj)
                    + self._generate_accessible_role(obj)
                    + self._generate_keyboard_mnemonic(obj),
                ),
                indicator=self._as_string(
                    self._generate_state_selected_for_radio_button(obj),
                ),
            ),
        ]
        result += self._generate_default_suffix(obj)
        return result

    def _generate_radio_menu_item(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the radio-menu-item role."""

        result = self._generate_default_prefix(obj)
        result += [
            braille.Component(
                obj,
                self._as_string(
                    self._generate_accessible_label_and_name(obj)
                    + self._generate_accessible_role(obj)
                    + self._generate_keyboard_mnemonic(obj)
                    + self._generate_keyboard_accelerator(obj),
                ),
                indicator=self._as_string(
                    self._generate_state_selected_for_radio_button(obj),
                ),
            ),
        ]
        result += self._generate_default_suffix(obj)
        return result

    def _generate_rating(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the rating role."""

        return self._generate_default_presentation(obj)

    def _generate_region(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the region landmark role."""

        return self._generate_default_presentation(obj)

    def _generate_root_pane(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the root-pane role."""

        return self._generate_default_presentation(obj)

    def _generate_row_header(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the row-header role."""

        if self._generate_text_substring(obj):
            line = self._generate_text_line(obj)
        else:
            line = self._generate_accessible_label_and_name(obj)

        result = [
            braille.Component(
                obj,
                self._as_string(
                    line
                    + self._generate_accessible_role(obj)
                    + self._generate_table_sort_order(obj),
                ),
            ),
        ]

        return result

    def _generate_ruler(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the ruler role."""

        return self._generate_default_presentation(obj)

    def _generate_scroll_bar(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the scroll-bar role."""

        result = self._generate_default_prefix(obj)
        result += [
            braille.Component(
                obj,
                self._as_string(
                    self._generate_accessible_label_and_name(obj)
                    + self._generate_value(obj)
                    + self._generate_accessible_role(obj)
                    + self._generate_keyboard_mnemonic(obj),
                ),
            ),
        ]
        result += self._generate_default_suffix(obj)
        return result

    def _generate_scroll_pane(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the scroll-pane role."""

        return self._generate_default_presentation(obj)

    def _generate_section(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the section role."""

        return self._generate_text_object(obj)

    def _generate_separator(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the separator role."""

        return self._generate_default_presentation(obj)

    def _generate_slider(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the slider role."""

        result = self._generate_default_prefix(obj)
        result += [
            braille.Component(
                obj,
                self._as_string(
                    self._generate_accessible_label_and_name(obj)
                    + self._generate_value(obj)
                    + self._generate_accessible_role(obj)
                    + self._generate_keyboard_mnemonic(obj),
                ),
            ),
        ]
        result += self._generate_default_suffix(obj)
        return result

    def _generate_spin_button(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the spin-button role."""

        if AXUtilities.is_editable(obj) or AXText.get_character_count(obj) > 0:
            return self._generate_text_object(obj)

        # No accessible text: render the value via the Value interface like a slider.
        result = self._generate_default_prefix(obj)
        result += [
            braille.Component(
                obj,
                self._as_string(
                    self._generate_accessible_label_and_name(obj)
                    + self._generate_value(obj)
                    + self._generate_accessible_role(obj)
                    + self._generate_keyboard_mnemonic(obj),
                ),
            ),
        ]
        result += self._generate_default_suffix(obj)
        return result

    def _generate_split_pane(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the split-pane role."""

        return self._generate_default_presentation(obj)

    def _generate_static(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the static role."""

        if AXObject.supports_text(obj):
            return self._generate_text_object(obj)

        return self._generate_default_presentation(obj)

    def _generate_status_bar(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the status-bar role."""

        result = self._generate_default_prefix(obj)
        result += [
            braille.Component(
                obj,
                self._as_string(
                    self._generate_accessible_label_and_name(obj)
                    + self._generate_accessible_role(obj),
                ),
            ),
        ]
        content = self._generate_descendants(obj)
        if not content:
            text = self._generate_text_content(obj)
            if not text and AXObject.get_child_count(obj) == 1:
                text = self._generate_text_content(AXObject.get_child(obj, 0))
            if text:
                content = [braille.Region(self._as_string(text))]
        if content:
            result += [braille.Region(" ")]
            result += content
        result += self._generate_default_suffix(obj)
        return result

    def _generate_subscript(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the subscript role."""

        return self._generate_default_presentation(obj)

    def _generate_suggestion(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the suggestion role."""

        return self._generate_default_presentation(obj)

    def _generate_superscript(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the superscript role."""

        return self._generate_default_presentation(obj)

    def _generate_switch(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the switch role."""

        result = self._generate_default_prefix(obj)
        result += [
            braille.Component(
                obj,
                self._as_string(
                    self._generate_accessible_label_and_name(obj)
                    + self._generate_accessible_role(obj)
                    + self._generate_keyboard_mnemonic(obj),
                ),
                indicator=self._as_string(self._generate_state_checked_for_switch(obj)),
            ),
        ]
        result += self._generate_default_suffix(obj)
        return result

    def _generate_table(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the table role."""

        return self._generate_default_presentation(obj)

    @log_generator_output
    def _generate_table_cell_contents(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates the core braille for the table-cell role."""

        suffix = []
        node_level = self._generate_tree_item_level(obj)
        if node_level:
            suffix += [braille.Region(" " + self._as_string(node_level))]

        if self._generate_text_substring(obj):
            result = self._generate_text_object(obj)
            result += suffix
            return result

        result = []
        result += self._generate_state_checked_for_cell(obj)
        result += [
            braille.Component(
                obj,
                self._as_string(
                    self._generate_column_header_if_toggle_and_no_text(obj)
                    + (
                        self._generate_real_active_descendant_displayed_text(obj)
                        or self._generate_accessible_label_and_name(obj)
                    )
                    + self._generate_state_expanded(obj),
                ),
            ),
        ]
        result += suffix
        result += self._generate_default_suffix(obj)
        return result

    def _generate_table_cell(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the table-cell role."""

        if self._generate_text_substring(obj):
            return self._generate_text_object(obj)

        # The cell's prefix/headers/row are presented without their own surrounding context.
        original_context = self._context
        self._context = replace(original_context, include_context=False)
        result = self._generate_default_prefix(obj)
        row_header = self._generate_table_cell_row_header(obj)
        if row_header:
            result += [braille.Region(" " + self._as_string(row_header))]
        column_header = self._generate_table_cell_column_header(obj)
        if column_header:
            result += [braille.Region(" " + self._as_string(column_header))]
        if row_header or column_header:
            result += [braille.Region(" ")]
        result += self._combine_cell_results(obj)
        self._context = original_context
        return result

    def _generate_table_column_header(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the table-column-header role."""

        return self._generate_default_presentation(obj)

    def _generate_table_row(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the table-row role."""

        result = self._generate_default_prefix(obj)
        result += [
            braille.Component(
                obj,
                self._as_string(
                    self._generate_accessible_label_and_name(obj)
                    + self._generate_text_content(obj)
                    + self._generate_value(obj)
                    + self._generate_accessible_role(obj)
                    + self._generate_state_required(obj)
                    + self._generate_state_invalid(obj)
                    + self._generate_state_expanded(obj),
                ),
            ),
        ]
        result += self._generate_default_suffix(obj)
        return result

    def _generate_table_row_header(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the table-row-header role."""

        return self._generate_default_presentation(obj)

    def _generate_tearoff_menu_item(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the tearoff-menu-item role."""

        return self._generate_default_presentation(obj)

    def _generate_terminal(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the terminal role."""

        result = [
            braille.Text(
                obj,
                start_offset=self._get_start_offset(obj),
                end_offset=self._get_end_offset(obj),
                caret_offset=self._get_caret_offset(obj, self._get_offset()),
                indicate_links=self._context.indicate_links,
            ),
        ]
        return result

    def _generate_text(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the text role."""

        return self._generate_text_object(obj)

    def _generate_timer(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the timer role."""

        return self._generate_default_presentation(obj)

    def _generate_title_bar(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the title-bar role."""

        return self._generate_default_presentation(obj)

    def _generate_toggle_button(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the toggle-button role."""

        result = self._generate_default_prefix(obj)
        result += [
            braille.Component(
                obj,
                self._as_string(
                    self._generate_accessible_label_and_name(obj)
                    + self._generate_state_expanded(obj)
                    + self._generate_accessible_role(obj)
                    + self._generate_keyboard_mnemonic(obj),
                ),
                indicator=self._as_string(self._generate_state_pressed(obj)),
            ),
        ]
        result += self._generate_default_suffix(obj)
        return result

    def _generate_tool_bar(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the tool-bar role."""

        result = self._generate_default_prefix(obj)
        result += [
            braille.Component(
                obj,
                self._as_string(
                    self._generate_accessible_label_and_name(obj)
                    + self._generate_accessible_role(obj),
                ),
            ),
        ]
        result += self._generate_default_suffix(obj)
        return result

    def _generate_tool_tip(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the tool-tip role."""

        return self._generate_default_presentation(obj)

    def _generate_tree(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the tree role."""

        result = self._generate_default_prefix(obj)
        result += [
            braille.Component(
                obj,
                self._as_string(
                    self._generate_accessible_label_and_name(obj)
                    + self._generate_accessible_role(obj),
                ),
            ),
        ]
        result += self._generate_default_suffix(obj)
        return result

    def _generate_tree_item(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the tree-item role."""

        if self._generate_text_substring(obj):
            result = self._generate_text_object(obj)
        else:
            result = [
                braille.Component(
                    obj,
                    self._as_string(
                        self._generate_accessible_label_and_name(obj)
                        + self._generate_state_expanded(obj),
                    ),
                ),
            ]

        node_level = self._generate_tree_item_level(obj)
        if node_level:
            result += [braille.Region(" " + self._as_string(node_level))]

        return result

    def _generate_tree_table(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the tree-table role."""

        return self._generate_default_presentation(obj)

    def _generate_unknown(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the unknown role."""

        return self._generate_default_presentation(obj)

    def _generate_video(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the video role."""

        return self._generate_default_presentation(obj)

    def _generate_viewport(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the viewport role."""

        return self._generate_default_presentation(obj)

    def _generate_window(self, obj: Atspi.Accessible) -> list[Any]:
        """Generates braille for the window role."""

        return self._generate_default_presentation(obj)
