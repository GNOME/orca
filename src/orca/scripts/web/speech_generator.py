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

# pylint: disable=too-many-return-statements
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=too-many-boolean-expressions
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments

"""Produces speech presentation for accessible objects."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING, Any

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from orca import (
    caret_navigator,
    debug,
    focus_manager,
    input_event_manager,
    messages,
    object_properties,
    speech_generator,
    speechserver,
)
from orca.ax_object import AXObject
from orca.ax_table import AXTable
from orca.ax_text import AXText
from orca.ax_utilities import AXUtilities
from orca.generator import ContentItem, ContentPosition, PresentationReason

if TYPE_CHECKING:
    from orca.speech_generator import SpeechGeneratorContext

    from . import script


class SpeechGenerator(speech_generator.SpeechGenerator):
    """Produces speech presentation for accessible objects."""

    # Type annotation to override the base class script type
    _script: script.Script

    @staticmethod
    def log_generator_output(func):
        """Decorator for logging."""

        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            tokens = [f"WEB SPEECH GENERATOR: {func.__name__}:", result]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return result

        return wrapper

    @log_generator_output
    def _generate_old_ancestors(self, obj: Atspi.Accessible) -> list[Any]:
        if self._get_content_position(obj).index > 0:
            return []

        return super()._generate_old_ancestors(obj)

    @log_generator_output
    def _generate_new_ancestors(self, obj: Atspi.Accessible) -> list[Any]:
        if (
            self._get_content_position(obj).index > 0
            and AXUtilities.find_ancestor(obj, AXUtilities.is_list) is None
        ):
            return []

        return super()._generate_new_ancestors(obj)

    def _generate_ancestors(
        self,
        obj: Atspi.Accessible,
        *,
        include_only: list | None = None,
        skip_roles: list | None = None,
        stop_at_roles: list | None = None,
        stop_after_roles: list | None = None,
    ) -> list[Any]:
        if not self._script.utilities.in_document_content(obj):
            return super()._generate_ancestors(
                obj,
                include_only=include_only,
                skip_roles=skip_roles,
                stop_at_roles=stop_at_roles,
                stop_after_roles=stop_after_roles,
            )

        result: list[Any] = []
        prior_obj = self._get_prior_obj()
        if prior_obj and AXObject.get_parent(prior_obj) == AXObject.get_parent(obj):
            return result

        if prior_obj and self._script.utilities.in_document_content(prior_obj):
            prior_doc = self._script.utilities.get_document_for_object(prior_obj)
            doc = self._script.utilities.get_document_for_object(obj)
            if prior_doc != doc and not self._script.utilities.get_document_for_object(doc):
                result = [super()._generate_accessible_name(doc)]

        if not AXUtilities.get_table(obj) and (
            AXUtilities.is_landmark(obj)
            or AXUtilities.is_math_related(obj)
            or AXUtilities.is_tool_tip(obj)
            or AXUtilities.is_status_bar(obj)
        ):
            return result

        if self._script.utilities.is_item_for_editable_combo_box(obj, prior_obj):
            return result

        stop_at_roles = [
            Atspi.Role.DOCUMENT_WEB,
            Atspi.Role.EMBEDDED,
            Atspi.Role.INTERNAL_FRAME,
            Atspi.Role.MATH,
            Atspi.Role.MENU_BAR,
        ]
        skip_roles = [
            Atspi.Role.PARAGRAPH,
            Atspi.Role.HEADING,
            Atspi.Role.LABEL,
            Atspi.Role.LINK,
            Atspi.Role.LIST_ITEM,
            Atspi.Role.TEXT,
        ]
        if AXUtilities.find_ancestor(obj, AXUtilities.is_editable_combo_box):
            skip_roles.append(Atspi.Role.COMBO_BOX)

        result.extend(
            super()._generate_ancestors(
                obj,
                stop_at_roles=stop_at_roles,
                skip_roles=skip_roles,
                stop_after_roles=[Atspi.Role.TOOL_BAR],
            ),
        )

        return result

    @log_generator_output
    def _generate_state_has_popup(self, obj: Atspi.Accessible) -> list[Any]:
        # TODO - JD: Can this be merged into the default's
        if self._only_speak_displayed_text():
            return []

        result: list[Any] = []
        attrs = AXObject.get_attributes_dict(obj)
        popup_type = attrs.get("haspopup", "false").lower()
        if popup_type == "dialog":
            result = [messages.HAS_POPUP_DIALOG]
        elif popup_type == "grid":
            result = [messages.HAS_POPUP_GRID]
        elif popup_type == "listbox":
            result = [messages.HAS_POPUP_LISTBOX]
        elif popup_type in ("menu", "true"):
            result = [messages.HAS_POPUP_MENU]
        elif popup_type == "tree":
            result = [messages.HAS_POPUP_TREE]

        if result:
            result.extend(self.voice(speech_generator.SYSTEM, obj=obj))
            return result

        return super()._generate_state_has_popup(obj)

    @log_generator_output
    def _generate_has_click_action(self, obj: Atspi.Accessible) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        if not self._script.utilities.in_document_content(obj):
            return []

        if AXUtilities.is_feed_article(obj):
            return []

        if not self._script.utilities.is_clickable_element(obj):
            return []

        result: list[Any] = [object_properties.STATE_CLICKABLE]
        result.extend(self.voice(speech_generator.SYSTEM, obj=obj))
        return result

    @log_generator_output
    def _generate_accessible_description(self, obj: Atspi.Accessible) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        if not self._script.utilities.in_document_content(obj):
            return super()._generate_accessible_description(obj)

        if not AXObject.is_valid(obj):
            return []

        # TODO - JD: Can this logic be moved into the default speech generator?
        if self._prefer_description_over_name(obj):
            return []

        if obj != self._context.focus:
            if AXUtilities.is_dialog_or_alert(obj, self._get_resolved_role()):
                return super()._generate_accessible_description(obj)
            if self._context.active_mode != focus_manager.MOUSE_REVIEW:
                return []

        if AXUtilities.is_text(obj, self._get_resolved_role()) and (
            self._get_reason() != PresentationReason.WHERE_AM_I_BASIC
        ):
            return []

        if (
            AXUtilities.is_link(obj, self._get_resolved_role())
            and caret_navigator.get_navigator().last_input_event_was_navigation_command()
        ):
            return []

        return super()._generate_accessible_description(obj)

    @log_generator_output
    def _generate_has_long_description(self, obj: Atspi.Accessible) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        if not self._script.utilities.in_document_content(obj):
            return []

        if not self._script.utilities.has_long_desc(obj):
            return []

        result: list[Any] = [object_properties.STATE_HAS_LONGDESC]
        result.extend(self.voice(speech_generator.SYSTEM, obj=obj))
        return result

    @log_generator_output
    def _generate_has_details(self, obj: Atspi.Accessible) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        if not self._script.utilities.in_document_content(obj):
            return super()._generate_has_details(obj)

        objs = AXUtilities.get_details(obj)
        if not objs:
            return []

        def obj_string(x):
            return str.strip(f"{AXObject.get_name(x)} {self.get_localized_role_name(x)}")

        to_present = ", ".join(set(map(obj_string, objs)))
        result: list[Any] = [object_properties.RELATION_HAS_DETAILS % to_present]
        result.extend(self.voice(speech_generator.SYSTEM, obj=obj))
        return result

    @log_generator_output
    def _generate_all_details(self, obj: Atspi.Accessible) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        objs: list[Atspi.Accessible] = []
        container = obj
        while container and not objs:
            objs = AXUtilities.get_details(container)
            container = AXObject.get_parent(container)

        if not objs:
            return []

        result: list[Any] = [object_properties.RELATION_HAS_DETAILS % ""]
        result.extend(self.voice(speech_generator.SYSTEM, obj=obj))

        result = []
        for o in objs:
            result.append(self.get_localized_role_name(o))
            result.extend(self.voice(speech_generator.SYSTEM, obj=obj))

            string = self._script.utilities.expand_eocs(o)
            if not string.strip():
                continue

            result.append(string)
            result.extend(self.voice(speech_generator.DEFAULT, obj=obj))
            result.extend(self._generate_pause(o))

        return result

    @log_generator_output
    def _generate_details_for(self, obj: Atspi.Accessible) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        if not self._script.utilities.in_document_content(obj):
            return super()._generate_details_for(obj)

        objs = AXUtilities.get_is_details_for(obj)
        if not objs:
            return []

        if self._is_leaving():
            return []

        if self._is_say_all():
            return []

        manager = input_event_manager.get_manager()
        if manager.last_event_was_forward_caret_navigation() and self._get_start_offset(obj):
            return []
        if (
            manager.last_event_was_backward_caret_navigation()
            and self._script.utilities.treat_as_text_object(obj)
            and self._get_end_offset(obj) not in [None, AXText.get_character_count(obj)]
        ):
            return []

        result: list[Any] = []
        for o in objs:
            string = (
                self._script.utilities.expand_eocs(o)
                or AXObject.get_name(o)
                or self.get_localized_role_name(o)
            )
            words = string.split()
            if len(words) > 5:
                words = [*words[0:5], "..."]

            result.append(object_properties.RELATION_DETAILS_FOR % " ".join(words))
            result.extend(self.voice(speech_generator.SYSTEM, obj=obj))
            result.extend(self._generate_pause(o))

        return result

    @log_generator_output
    def _generate_accessible_label_and_name(self, obj: Atspi.Accessible) -> list[Any]:
        if not self._script.utilities.in_document_content(obj):
            return super()._generate_accessible_label_and_name(obj)

        if (
            self._script.utilities.is_text_block_element(obj)
            and AXUtilities.has_presentable_text(obj)
            and not AXUtilities.is_landmark(obj, self._get_resolved_role())
            and not self._script.utilities.is_document(obj)
            and not AXUtilities.is_dpub(obj, self._get_resolved_role())
            and not AXUtilities.is_suggestion(obj, self._get_resolved_role())
        ):
            return []

        if obj == self._get_prior_obj() and AXUtilities.is_editable(obj):
            return []

        if AXUtilities.is_label(obj, self._get_resolved_role()) and AXObject.supports_text(obj):
            return []

        return super()._generate_accessible_label_and_name(obj)

    @log_generator_output
    def _generate_accessible_name(self, obj: Atspi.Accessible) -> list[Any]:
        if not self._script.utilities.in_document_content(obj):
            return super()._generate_accessible_name(obj)

        if (
            self._script.utilities.is_text_block_element(obj)
            and AXUtilities.has_presentable_text(obj)
            and not AXUtilities.is_landmark(obj, self._get_resolved_role())
            and not AXUtilities.is_dpub(obj, self._get_resolved_role())
            and not self._in_flat_review
        ):
            return []

        if AXUtilities.is_link(obj) and self._get_content_string(obj):
            return []

        if AXUtilities.has_visible_caption(obj):
            return []

        if AXUtilities.is_figure(obj, self._get_resolved_role()) and self._get_ancestor_of():
            caption = self._get_ancestor_of()
            if not AXUtilities.is_caption(caption):
                caption = AXUtilities.find_ancestor(caption, AXUtilities.is_caption)
            if caption and obj in AXUtilities.get_is_label_for(caption):
                return []

        # TODO - JD: Can this logic be moved to the default speech generator?
        if AXObject.get_name(obj):
            if self._prefer_description_over_name(obj):
                result: list[Any] = [AXObject.get_description(obj)]
            else:
                name = AXObject.get_name(obj)
                if not AXUtilities.has_explicit_name(obj):
                    name = name.strip()
                result = [name]

            result.extend(self.voice(speech_generator.DEFAULT, obj=obj))
            return result

        return super()._generate_accessible_name(obj)

    @log_generator_output
    def _generate_accessible_label(self, obj: Atspi.Accessible) -> list[Any]:
        if not self._script.utilities.in_document_content(obj):
            return super()._generate_accessible_label(obj)

        label, _objects = self._script.utilities.infer_label_for(obj)
        if label:
            result: list[Any] = [label]
            result.extend(self.voice(speech_generator.DEFAULT, obj=obj))
            return result

        return []

    @log_generator_output
    def _generate_leaving(self, obj: Atspi.Accessible) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        if not self._is_leaving():
            return []

        if self._script.utilities.in_document_content(
            obj,
        ) and not self._script.utilities.in_document_content(
            self._context.focus,
        ):
            result: list[Any] = [""]
            result.extend(self.voice(speech_generator.SYSTEM, obj=obj))
            return result

        return super()._generate_leaving(obj)

    @log_generator_output
    def _generate_new_radio_button_group(self, obj: Atspi.Accessible) -> list[Any]:
        # TODO - JD: The default speech generator"s method determines group membership
        # via the member-of relation. We cannot count on that here. Plus, radio buttons
        # on the web typically live in a group which is labelled. Thus the new-ancestor
        # presentation accomplishes the same thing. Unless this can be further sorted out,
        # try to filter out some of the noise....
        return []

    @log_generator_output
    def _generate_number_of_children(self, obj: Atspi.Accessible) -> list[Any]:
        if self._only_speak_displayed_text() or not self._context.verbose:
            return []

        # We handle things even for non-document content due to issues in
        # other toolkits (e.g. exposing list items to us that are not
        # exposed to sighted users)
        roles = [Atspi.Role.DESCRIPTION_LIST, Atspi.Role.LIST, Atspi.Role.LIST_BOX, "ROLE_FEED"]
        role = self._get_resolved_role(obj)
        if role not in roles:
            return super()._generate_number_of_children(obj)

        set_size = AXUtilities.get_set_size(AXObject.get_child(obj, 0))
        if set_size is None:
            if AXUtilities.is_description_list(obj, role):
                set_size = len(AXUtilities.get_description_list_terms(obj))
            elif AXUtilities.is_list_box(obj, role) or AXUtilities.is_list(obj, role):
                set_size = len(list(AXObject.iter_children(obj, AXUtilities.is_list_item)))

        if not set_size:
            return []

        if AXUtilities.is_description_list(obj):
            result: list[Any] = [messages.description_list_term_count(set_size)]
        elif role == "ROLE_FEED":
            result = [messages.feed_article_count(set_size)]
        else:
            result = [messages.list_item_count(set_size)]
        result.extend(self.voice(speech_generator.SYSTEM, obj=obj))
        return result

    def get_localized_role_name(
        self, obj: Atspi.Accessible, *, role: Atspi.Role | str | None = None
    ) -> str:
        if not self._script.utilities.in_document_content(obj):
            return super().get_localized_role_name(obj, role=role)

        role_description = AXObject.get_role_description(obj)
        if role_description:
            return role_description

        return super().get_localized_role_name(obj, role=role)

    @log_generator_output
    def _generate_real_active_descendant_displayed_text(
        self,
        obj: Atspi.Accessible,
    ) -> list[Any]:
        if not self._script.utilities.in_document_content(obj):
            return super()._generate_real_active_descendant_displayed_text(obj)

        rad = AXUtilities.active_descendant(obj)
        return self._generate_text_content(rad)

    @log_generator_output
    def _generate_accessible_role(self, obj: Atspi.Accessible) -> list[Any]:
        if not self._script.utilities.in_document_content(obj):
            return super()._generate_accessible_role(obj)

        # Do this check before the roledescription check, e.g. navigation within VSCode's editor.
        if obj == self._get_prior_obj():
            return []

        roledescription = AXObject.get_role_description(obj)
        if roledescription:
            result: list[Any] = [roledescription]
            result.extend(self.voice(speech_generator.SYSTEM, obj=obj))
            return result

        role = self._get_resolved_role(obj)
        start = self._get_start_offset(obj)
        end = self._get_end_offset(obj)
        index = self._get_content_position(obj).index
        total = self._get_content_position(obj).total

        ancestor_with_usable_role = self._get_ancestor_with_usable_role(obj)
        if not self._should_speak_role(obj):
            # Only the focused object absorbs an ancestor's role; an ancestor presented as
            # context must not borrow a role from further up the tree.
            if ancestor_with_usable_role and not self._is_ancestor():
                return self._generate_accessible_role(ancestor_with_usable_role)
            return []

        result = []
        mgr = input_event_manager.get_manager()
        is_editable = AXUtilities.is_editable(obj)
        if is_editable and not self._script.utilities.is_content_editable_with_embedded_objects(
            obj,
        ):
            if self._is_say_all() and start:
                return []
            if mgr.last_event_was_forward_caret_navigation() and start:
                return []
            if (
                mgr.last_event_was_backward_caret_navigation()
                and self._script.utilities.treat_as_text_object(obj)
                and end not in [None, AXText.get_character_count(obj)]
            ):
                return []
            result.append(self.get_localized_role_name(obj))
            result.extend(self.voice(speech_generator.SYSTEM, obj=obj))

        elif is_editable and self._script.utilities.is_document(obj):
            parent = AXObject.get_parent(obj)
            if (
                parent
                and not AXUtilities.is_editable(parent)
                and not mgr.last_event_was_caret_navigation()
            ):
                result.append(object_properties.ROLE_EDITABLE_CONTENT)
                result.extend(self.voice(speech_generator.SYSTEM, obj=obj))

        elif role == Atspi.Role.HEADING:
            if index == total - 1:
                level = AXUtilities.get_heading_level(obj)
                if level:
                    result.append(
                        object_properties.ROLE_HEADING_LEVEL_SPEECH
                        % {"role": self.get_localized_role_name(obj), "level": level},
                    )
                    result.extend(self.voice(speech_generator.SYSTEM, obj=obj))
                else:
                    result.append(self.get_localized_role_name(obj))
                    result.extend(self.voice(speech_generator.SYSTEM, obj=obj))

        elif self._script.utilities.is_link(obj):
            if AXUtilities.is_image(AXObject.get_parent(obj)):
                result.append(messages.IMAGE_MAP_LINK)
                result.extend(self.voice(speech_generator.SYSTEM, obj=obj))
            else:
                if self._script.utilities.has_useless_canvas_descendant(obj):
                    result.append(self.get_localized_role_name(obj, role=Atspi.Role.IMAGE))
                    result.extend(self.voice(speech_generator.SYSTEM, obj=obj))
                if index == total - 1:
                    result.append(self.get_localized_role_name(obj))
                    result.extend(self.voice(speech_generator.SYSTEM, obj=obj))

        else:
            result.append(self.get_localized_role_name(obj))
            result.extend(self.voice(speech_generator.SYSTEM, obj=obj))

        if ancestor_with_usable_role:
            result[1:1] = self._generate_accessible_role(ancestor_with_usable_role)

        return result

    @log_generator_output
    def _generate_position_in_list(self, obj: Atspi.Accessible) -> list[Any]:
        if AXUtilities.is_list_item(obj):
            if self._get_content_position(obj).index + 1 < self._get_content_position(obj).total:
                return []

        if not self._is_where_am_i():
            if self._get_prior_obj() == obj:
                return []

        return super()._generate_position_in_list(obj)

    @log_generator_output
    def _generate_state_unselected(self, obj: Atspi.Accessible) -> list[Any]:
        if not self._context.in_focus_mode:
            return []

        return super()._generate_state_unselected(obj)

    # TODO - JD: This function and its associated fake role really need to die....
    # TODO - JD: Why isn"t this logic part of normal table cell generation?
    @log_generator_output
    def _generate_real_table_cell(self, obj: Atspi.Accessible) -> list[Any]:
        result = super()._generate_real_table_cell(obj)
        if not self._context.in_focus_mode:
            return result

        if self._context.announce_cell_coordinates:
            label = AXUtilities.get_label_for_cell_coordinates(obj)
            if label:
                result.append(label)
                result.extend(self.voice(speech_generator.SYSTEM, obj=obj))
                return result

            row, col = AXTable.get_cell_coordinates(obj)
            if AXUtilities.cell_row_changed(obj):
                result.append(messages.TABLE_ROW % (row + 1))
                result.extend(self.voice(speech_generator.SYSTEM, obj=obj))
            if AXUtilities.cell_column_changed(obj):
                result.append(messages.TABLE_COLUMN % (col + 1))
                result.extend(self.voice(speech_generator.SYSTEM, obj=obj))

        return result

    def generate_speech(
        self,
        obj: Atspi.Accessible,
        context: SpeechGeneratorContext,
        *,
        role: Atspi.Role | str | None = None,
        include_context: bool = True,
    ) -> list[Any]:
        if not self._script.utilities.in_document_content(obj):
            tokens = ["WEB:", obj, "is not in document content. Calling default speech generator."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return super().generate_speech(obj, context, role=role, include_context=include_context)

        tokens = ["WEB: Generating speech for document object", obj]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        result: list[Any] = []
        if self._script.utilities.is_link(obj):
            role = Atspi.Role.LINK
        elif AXUtilities.is_custom_image(obj):
            role = Atspi.Role.IMAGE
        elif self._script.utilities.treat_as_div(obj, offset=self._get_start_offset(obj)):
            role = Atspi.Role.SECTION

        if context.prior_obj is None:
            document = self._script.utilities.get_top_level_document_for_object(obj)
            prior_context = self._script.utilities.get_prior_context(document)
            if prior_context:
                context = replace(context, prior_obj=prior_context[0])

        item = self._get_content_item(obj)
        start = item.start_offset if item is not None else 0
        end = item.end_offset if item is not None else -1
        language, dialect = self._script.utilities.get_language_and_dialect_for_substring(
            obj, start, end
        )
        context = replace(context, language=language, dialect=dialect)

        if not result:
            result = list(
                filter(
                    lambda x: x,
                    super().generate_speech(
                        obj,
                        context,
                        role=role,
                        include_context=include_context,
                    ),
                ),
            )

        tokens = ["WEB: Speech generation for document object", obj, "complete."]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    def generate_contents(  # type: ignore[override]
        self,
        contents: list[tuple[Atspi.Accessible, int, int, str]],
        context: SpeechGeneratorContext,
    ) -> list[Any]:
        self._context = context
        return self._generate_web_contents(contents)

    def _generate_web_contents(
        self,
        contents: list[tuple[Atspi.Accessible, int, int, str]],
    ) -> list[Any]:
        if not contents:
            return []

        result: list[Any] = []
        contents = self._script.utilities.filter_contents_for_presentation(contents, True)
        tokens = ["WEB: Generating speech contents (length:", len(contents), ")"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        announce_attrs = len(contents) > 1 and self._should_announce_attribute_changes(
            contents[0][0],
        )
        prev_attrs: dict[str, str] = {}
        system_voice = self.voice(speechserver.VoiceType.SYSTEM) if announce_attrs else []

        original_context = self._context
        base_position = original_context.content_position
        for i, content in enumerate(contents):
            obj, start, end, string = content
            tokens = [f"ITEM {i}: ", obj, f"start: {start}, end: {end} '{string}'"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

            if announce_attrs and i > 0:
                curr_attrs, run_start, run_end = AXText.get_text_attributes_at_offset(obj, start)
                exclude = AXUtilities.get_redundant_text_attributes(obj, run_start, run_end)
                result.extend(
                    [desc, *system_voice]
                    for desc in self._get_attribute_change_descriptions(
                        prev_attrs, curr_attrs, exclude
                    )
                )
                prev_attrs = curr_attrs
            elif announce_attrs:
                prev_attrs = AXText.get_text_attributes_at_offset(obj, start)[0]

            if base_position is not None:
                position = ContentPosition(index=base_position.index + i, total=base_position.total)
            else:
                position = ContentPosition(index=i, total=len(contents))
            self._context = replace(
                self._context,
                content_item=ContentItem(start_offset=start, end_offset=end, string=string),
                content_position=position,
                content_subject=obj,
            )
            utterance = self.generate_speech(obj, self._context)
            if isinstance(utterance, list):

                def is_not_empty_list(x):
                    return not (isinstance(x, list) and not x)

                utterance = list(filter(is_not_empty_list, utterance))
            if utterance and utterance[0]:
                result.append(utterance)
                self._context = replace(self._context, prior_obj=obj)
        self._context = original_context

        if not result:
            if self._is_say_all() or not self._context.speak_blank_lines or self._is_ancestor():
                string = ""
            else:
                string = messages.BLANK
            # TODO - Why not [[string, *self.voice(speech_generator.DEFAULT)]] ?
            result = [string, *self.voice(speech_generator.DEFAULT)]

        return result

    def generate_line(
        self,
        obj: Atspi.Accessible,
        start_offset: int,
        end_offset: int,
        line: str,
        context: SpeechGeneratorContext,
    ) -> list[Any]:
        """Generates speech for a web document line via DOM-walking contents."""

        if not self._script.utilities.in_document_content(obj):
            return super().generate_line(obj, start_offset, end_offset, line, context)

        if AXUtilities.is_editable(obj) and "\ufffc" not in line:
            return super().generate_line(obj, start_offset, end_offset, line, context)

        document = self._script.utilities.get_top_level_document_for_object(obj)
        prior_context = self._script.utilities.get_prior_context(document=document)
        prior_obj = prior_context[0] if prior_context else None

        contents = self._script.utilities.get_line_contents_at_offset(
            obj,
            start_offset,
            use_cache=True,
        )
        return self.generate_contents(contents, replace(self._context, prior_obj=prior_obj))

    def generate_word(
        self,
        obj: Atspi.Accessible,
        offset: int,
        context: SpeechGeneratorContext,
    ) -> list[Any]:
        """Generates speech for a web document word via DOM-walking contents."""

        word_contents = self._script.utilities.get_word_contents_at_offset(
            obj,
            offset,
            use_cache=True,
        )
        if not word_contents:
            return []
        text_obj = word_contents[0][0]
        prior_obj = text_obj if AXUtilities.is_text_input(text_obj) else None
        return self.generate_contents(
            word_contents,
            replace(self._context, prior_obj=prior_obj),
        )
