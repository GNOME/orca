# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
# Copyright 2010-2011 Orca Team
# Copyright 2011-2015 Igalia, S.L.
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

# pylint: disable=too-many-locals

"""Produces braille presentation for accessible objects."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING, Any

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from orca import braille, braille_generator, debug, messages, object_properties
from orca.ax_object import AXObject
from orca.ax_utilities import AXUtilities
from orca.generator import ContentItem, ContentPosition

if TYPE_CHECKING:
    from orca.braille_generator import BrailleGeneratorContext

    from . import script


class BrailleGenerator(braille_generator.BrailleGenerator):
    """Produces braille presentation for accessible objects."""

    # Type annotation to override the base class script type
    _script: script.Script

    @staticmethod
    def log_generator_output(func):
        """Decorator for logging."""

        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            tokens = [f"WEB BRAILLE GENERATOR: {func.__name__}:", result]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return result

        return wrapper

    def get_localized_role_name(self, obj: Atspi.Accessible, **args) -> str:
        if not self._script.utilities.in_document_content(obj):
            return super().get_localized_role_name(obj, **args)

        role_description = AXObject.get_role_description(obj, True)
        if role_description:
            return role_description

        return super().get_localized_role_name(obj, **args)

    @log_generator_output
    def _generate_accessible_role(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Prevents some roles from being displayed."""

        if not self._script.utilities.in_document_content(obj):
            return super()._generate_accessible_role(obj, **args)

        role_description = AXObject.get_role_description(obj, True)
        if role_description:
            return [role_description]

        # TODO - JD: Can this logic be moved to the default braille generator?
        do_not_display = [
            Atspi.Role.FORM,
            Atspi.Role.PARAGRAPH,
            Atspi.Role.STATIC,
            Atspi.Role.SECTION,
            Atspi.Role.REDUNDANT_OBJECT,
            Atspi.Role.UNKNOWN,
        ]

        if not AXUtilities.is_focusable(obj):
            do_not_display.extend(
                [
                    Atspi.Role.LIST,
                    Atspi.Role.LIST_ITEM,
                    Atspi.Role.COLUMN_HEADER,
                    Atspi.Role.ROW_HEADER,
                    Atspi.Role.TABLE_CELL,
                    Atspi.Role.PANEL,
                ],
            )

        if self._get_start_offset() is not None and self._get_end_offset() is not None:
            do_not_display.append(Atspi.Role.ALERT)

        result = []
        role = self._get_resolved_role(obj)

        level = AXUtilities.get_heading_level(obj)
        if level:
            result.append(object_properties.ROLE_HEADING_LEVEL_BRAILLE % level)
            return result

        if self._script.utilities.is_link(obj) and obj == self._context.focus:
            if AXUtilities.is_image(AXObject.get_parent(obj)):
                result.append(messages.IMAGE_MAP_LINK)

        elif role not in do_not_display:
            label = AXUtilities.get_label_for_cell_coordinates(obj)
            if label:
                result.append(label)
            else:
                result = super()._generate_accessible_role(obj, **args)

        if self._get_content_position().index == self._get_content_position().total - 1 and (
            AXUtilities.is_image(obj, self._get_resolved_role())
            or self._script.utilities.treat_as_text_object(obj)
        ):
            heading = AXUtilities.find_ancestor(obj, AXUtilities.is_heading)
            if heading is not None:
                result.extend(self._generate_accessible_role(heading))

        return result

    @log_generator_output
    def _generate_accessible_label(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if not self._script.utilities.in_document_content(obj):
            return super()._generate_accessible_label(obj, **args)

        label, _objects = self._script.utilities.infer_label_for(obj)
        if label:
            return [label]

        return super()._generate_accessible_label(obj, **args)

    @log_generator_output
    def _generate_accessible_label_and_name(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if not self._script.utilities.in_document_content(obj):
            return super()._generate_accessible_label_and_name(obj, **args)

        if self._script.utilities.is_text_block_element(obj):
            return []

        if AXUtilities.is_editable(obj) and AXUtilities.find_ancestor(obj, AXUtilities.is_code):
            return []

        role = self._get_resolved_role(obj)
        if role == Atspi.Role.LABEL and AXObject.supports_text(obj):
            return []

        return super()._generate_accessible_label_and_name(obj, **args)

    @log_generator_output
    def _generate_accessible_description(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if not self._script.utilities.in_document_content(obj):
            return super()._generate_accessible_description(obj, **args)

        # TODO - JD: Can this logic be moved into the default braille generator?
        if self._prefer_description_over_name(obj):
            return []

        return super()._generate_accessible_description(obj, **args)

    @log_generator_output
    def _generate_accessible_name(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if not self._script.utilities.in_document_content(obj):
            return super()._generate_accessible_name(obj, **args)

        braille_label = AXObject.get_attributes_dict(obj).get("braillelabel")
        if braille_label:
            return [braille_label]

        # TODO - JD: Can this logic be moved into the default braille generator?
        if self._prefer_description_over_name(obj):
            return [AXObject.get_description(obj)]

        if AXObject.get_name(obj) and not self._script.utilities.has_valid_name(obj):
            return []

        result = super()._generate_accessible_name(obj, **args)
        if result and result[0] and not AXUtilities.has_explicit_name(obj):
            result[0] = result[0].strip()
        elif not result and AXUtilities.is_check_box(obj):
            grid_cell = AXUtilities.find_ancestor(obj, AXUtilities.is_grid_cell)
            if grid_cell:
                return super()._generate_accessible_name(grid_cell, **args)

        return result

    @log_generator_output
    def _generate_real_active_descendant_displayed_text(
        self,
        obj: Atspi.Accessible,
        **args,
    ) -> list[Any]:
        if not self._script.utilities.in_document_content(obj):
            return super()._generate_real_active_descendant_displayed_text(obj, **args)

        rad = AXUtilities.active_descendant(obj)
        return self._generate_text_content(rad, **args)

    def generate_braille(
        self,
        obj: Atspi.Accessible,
        context: BrailleGeneratorContext,
        *,
        role: Atspi.Role | str | None = None,
        include_context: bool = True,
        **args,
    ) -> list[Any]:
        if not self._script.utilities.in_document_content(obj):
            tokens = ["WEB:", obj, "is not in document content. Calling default braille generator."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return super().generate_braille(
                obj, context, role=role, include_context=include_context, **args
            )

        tokens = ["WEB: Generating braille for document object", obj, args]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True, True)

        result = []

        include_context = not self._script.utilities.in_document_content(obj)
        if self._script.utilities.is_clickable_element(obj) or self._script.utilities.is_link(obj):
            role = Atspi.Role.LINK
        elif AXUtilities.is_custom_image(obj):
            role = Atspi.Role.IMAGE
        elif AXUtilities.is_anchor(obj):
            role = Atspi.Role.STATIC
        elif self._script.utilities.treat_as_div(obj, offset=self._get_start_offset()):
            role = Atspi.Role.SECTION

        if AXUtilities.is_menu_item(obj):
            combo_box = AXUtilities.find_ancestor(obj, AXUtilities.is_combo_box)
            if combo_box and not AXUtilities.is_expanded(combo_box):
                obj = combo_box
        result.extend(
            super().generate_braille(
                obj, context, role=role, include_context=include_context, **args
            ),
        )
        return result

    def generate_contents(  # type: ignore[override]
        self,
        contents: list[tuple[Atspi.Accessible, int, int, str]],
        context: BrailleGeneratorContext,
        **args,
    ) -> tuple[list[list[Any]], Atspi.Accessible | None]:
        self._context = context
        return self._generate_web_braille_contents(contents, **args)

    def _generate_web_braille_contents(
        self,
        contents: list[tuple[Atspi.Accessible, int, int, str]],
        **args,
    ) -> tuple[list[list[Any]], Atspi.Accessible | None]:
        if not contents:
            return [], None

        result = []
        contents = self._script.utilities.filter_contents_for_presentation(contents, True)

        obj, offset = self._script.utilities.get_caret_context()
        index = self._script.utilities.find_object_in_contents(obj, offset, contents)

        last_region = None
        focused_region = None
        original_context = self._context
        for i, content in enumerate(contents):
            acc, start, end, string = content
            item_context = replace(
                original_context,
                content_item=ContentItem(
                    start_offset=start, end_offset=end, string=string, caret_offset=offset
                ),
                content_position=ContentPosition(index=i, total=len(contents)),
            )
            regions, f_region = self.generate_braille(acc, item_context)
            if not regions:
                continue

            if i == index:
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
