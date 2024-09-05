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

# pylint: disable=wrong-import-position
# pylint: disable=too-many-return-statements
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements

"""Produces speech presentation for accessible objects."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc." \
                "Copyright (c) 2010-2011 Orca Team" \
                "Copyright (c) 2011-2015 Igalia, S.L."
__license__   = "LGPL"

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from orca import debug
from orca import focus_manager
from orca import input_event_manager
from orca import messages
from orca import object_properties
from orca import settings
from orca import settings_manager
from orca import speech_generator
from orca.ax_object import AXObject
from orca.ax_table import AXTable
from orca.ax_text import AXText
from orca.ax_utilities import AXUtilities


class SpeechGenerator(speech_generator.SpeechGenerator):
    """Produces speech presentation for accessible objects."""

    @staticmethod
    def log_generator_output(func):
        """Decorator for logging."""

        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            tokens = [f"WEB SPEECH GENERATOR: {func.__name__}:", result]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return result
        return wrapper

    @log_generator_output
    def _generate_old_ancestors(self, obj, **args):
        if args.get("index", 0) > 0:
            return []

        return super()._generate_old_ancestors(obj, **args)

    @log_generator_output
    def _generate_new_ancestors(self, obj, **args):
        if args.get("index", 0) > 0 and not self._script.utilities.isListDescendant(obj):
            return []

        return super()._generate_new_ancestors(obj, **args)

    def _generate_ancestors(self, obj, **args):
        if not self._script.utilities.inDocumentContent(obj):
            return super()._generate_ancestors(obj, **args)

        if self._script.inSayAll() and obj == focus_manager.get_manager().get_locus_of_focus():
            return []

        result = []
        prior_obj = args.get("priorObj")
        if prior_obj and self._script.utilities.inDocumentContent(prior_obj):
            prior_doc = self._script.utilities.getDocumentForObject(prior_obj)
            doc = self._script.utilities.getDocumentForObject(obj)
            if prior_doc != doc and not self._script.utilities.getDocumentForObject(doc):
                result = [super()._generate_accessible_name(doc)]

        if not AXTable.get_table(obj) \
           and (AXUtilities.is_landmark(obj) \
                or AXUtilities.is_math_related(obj) \
                or AXUtilities.is_tool_tip(obj) \
                or AXUtilities.is_status_bar(obj)):
            return result

        if self._script.utilities.isItemForEditableComboBox(obj, prior_obj):
            return result

        args["stop_at_roles"] = [Atspi.Role.DOCUMENT_WEB,
                               Atspi.Role.EMBEDDED,
                               Atspi.Role.INTERNAL_FRAME,
                               Atspi.Role.MATH,
                               Atspi.Role.MENU_BAR]
        args["skipRoles"] = [Atspi.Role.PARAGRAPH,
                             Atspi.Role.HEADING,
                             Atspi.Role.LABEL,
                             Atspi.Role.LINK,
                             Atspi.Role.LIST_ITEM,
                             Atspi.Role.TEXT]
        args["stop_after_roles"] = [Atspi.Role.TOOL_BAR]

        if self._script.utilities.isEditableDescendantOfComboBox(obj):
            args["skipRoles"].append(Atspi.Role.COMBO_BOX)

        result.extend(super()._generate_ancestors(obj, **args))

        return result

    @log_generator_output
    def _generate_state_has_popup(self, obj, **args):
        # TODO - JD: Can this be merged into the default's
        if settings_manager.get_manager().get_setting("onlySpeakDisplayedText"):
            return []

        result = []
        popup_type = self._script.utilities.popupType(obj)
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
            result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))
            return result

        return super()._generate_state_has_popup(obj, **args)

    @log_generator_output
    def _generate_has_click_action(self, obj, **args):
        if settings_manager.get_manager().get_setting("onlySpeakDisplayedText"):
            return []

        if not self._script.utilities.inDocumentContent(obj):
            return []

        if AXUtilities.is_feed_article(obj):
            return []

        if not self._script.utilities.isClickableElement(obj):
            return []

        result = [object_properties.STATE_CLICKABLE]
        result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_accessible_description(self, obj, **args):
        if settings_manager.get_manager().get_setting("onlySpeakDisplayedText"):
            return []

        if not self._script.utilities.inDocumentContent(obj):
            return super()._generate_accessible_description(obj, **args)

        if not AXObject.is_valid(obj):
            return []

        if self._script.utilities.preferDescriptionOverName(obj):
            return []

        if obj != focus_manager.get_manager().get_locus_of_focus():
            if AXUtilities.is_dialog_or_alert(obj, args.get("role")):
                return super()._generate_accessible_description(obj, **args)
            if not args.get("inMouseReview"):
                return []

        format_type = args.get("formatType")
        if format_type == "basicWhereAmI" and self._script.utilities.isLiveRegion(obj):
            return self._script.live_region_manager.generateLiveRegionDescription(obj, **args)

        if AXUtilities.is_text(obj, args.get("role")) and format_type != "basicWhereAmI":
            return []

        if AXUtilities.is_link(obj, args.get("role")) \
           and self._script.caret_navigation.last_input_event_was_navigation_command():
            return []

        return super()._generate_accessible_description(obj, **args)

    @log_generator_output
    def _generate_has_long_description(self, obj, **args):
        if settings_manager.get_manager().get_setting("onlySpeakDisplayedText"):
            return []

        if not self._script.utilities.inDocumentContent(obj):
            return []

        if not self._script.utilities.hasLongDesc(obj):
            return []

        result = [object_properties.STATE_HAS_LONGDESC]
        result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_has_details(self, obj, **args):
        if settings_manager.get_manager().get_setting("onlySpeakDisplayedText"):
            return []

        if not self._script.utilities.inDocumentContent(obj):
            return super()._generate_has_details(obj, **args)

        objs = AXUtilities.get_details(obj)
        if not objs:
            return []

        def obj_string(x):
            return str.strip(f"{AXObject.get_name(x)} {self.get_localized_role_name(x)}")

        to_present = ", ".join(set(map(obj_string, objs)))
        result = [object_properties.RELATION_HAS_DETAILS % to_present]
        result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_all_details(self, obj, **args):
        if settings_manager.get_manager().get_setting("onlySpeakDisplayedText"):
            return []

        objs = []
        container = obj
        while container and not objs:
            objs = AXUtilities.get_details(container)
            container = AXObject.get_parent(container)

        if not objs:
            return []

        result = [object_properties.RELATION_HAS_DETAILS % ""]
        result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))

        result = []
        for o in objs:
            result.append(self.get_localized_role_name(o))
            result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))

            string = self._script.utilities.expandEOCs(o)
            if not string.strip():
                continue

            result.append(string)
            result.extend(self.voice(speech_generator.DEFAULT, obj=obj, **args))
            result.extend(self._generate_pause(o))

        return result

    @log_generator_output
    def _generate_details_for(self, obj, **args):
        if settings_manager.get_manager().get_setting("onlySpeakDisplayedText"):
            return []

        if not self._script.utilities.inDocumentContent(obj):
            return super()._generate_details_for(obj, **args)

        objs = AXUtilities.get_is_details_for(obj)
        if not objs:
            return []

        if args.get("leaving"):
            return []

        manager = input_event_manager.get_manager()
        if (manager.last_event_was_forward_caret_navigation() or self._script.inSayAll()) \
           and args.get("startOffset"):
            return []
        if manager.last_event_was_backward_caret_navigation() \
           and self._script.utilities.treatAsTextObject(obj) \
           and args.get("endOffset") not in [None, AXText.get_character_count(obj)]:
            return []

        result = []
        for o in objs:
            string = self._script.utilities.expandEOCs(o) or AXObject.get_name(o) \
                or self.get_localized_role_name(o)
            words = string.split()
            if len(words) > 5:
                words = words[0:5] + ["..."]

            result.append(object_properties.RELATION_DETAILS_FOR % " ".join(words))
            result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))
            result.extend(self._generate_pause(o, **args))

        return result

    @log_generator_output
    def _generate_accessible_label_and_name(self, obj, **args):
        if not self._script.utilities.inDocumentContent(obj):
            return super()._generate_accessible_label_and_name(obj, **args)

        if self._script.utilities.isTextBlockElement(obj) \
           and AXText.has_presentable_text(obj)  \
           and not AXUtilities.is_landmark(obj, args.get("role")) \
           and not self._script.utilities.isDocument(obj) \
           and not AXUtilities.is_dpub(obj, args.get("role")) \
           and not AXUtilities.is_suggestion(obj, args.get("role")):
            return []

        if obj == args.get("priorObj") and AXUtilities.is_editable(obj):
            return []

        if AXUtilities.is_label(obj, args.get("role")) and AXObject.supports_text(obj):
            return []

        return super()._generate_accessible_label_and_name(obj, **args)

    @log_generator_output
    def _generate_accessible_name(self, obj, **args):
        if not self._script.utilities.inDocumentContent(obj):
            return super()._generate_accessible_name(obj, **args)

        if self._script.utilities.isTextBlockElement(obj) \
           and AXText.has_presentable_text(obj)  \
           and not AXUtilities.is_landmark(obj, args.get("role")) \
           and not AXUtilities.is_dpub(obj, args.get("role")) \
           and not args.get("inFlatReview"):
            return []

        if AXUtilities.is_link(obj) and args.get("string"):
            return []

        if self._script.utilities.hasVisibleCaption(obj):
            return []

        if AXUtilities.is_figure(obj, args.get("role")) and args.get("ancestorOf"):
            caption = args.get("ancestorOf")
            if not AXUtilities.is_caption(caption):
                caption = AXObject.find_ancestor(caption, AXUtilities.is_caption)
            if caption and obj in AXUtilities.get_is_label_for(caption):
                return []

        # TODO - JD: Can this logic be moved to the default speech generator?
        if AXObject.get_name(obj):
            if self._script.utilities.preferDescriptionOverName(obj):
                result = [AXObject.get_description(obj)]
            else:
                name = AXObject.get_name(obj)
                if not self._script.utilities.hasExplicitName(obj):
                    name = name.strip()
                result = [name]

            result.extend(self.voice(speech_generator.DEFAULT, obj=obj, **args))
            return result

        return super()._generate_accessible_name(obj, **args)

    @log_generator_output
    def _generate_accessible_label(self, obj, **args):
        if not self._script.utilities.inDocumentContent(obj):
            return super()._generate_accessible_label(obj, **args)

        label, _objects = self._script.utilities.inferLabelFor(obj)
        if label:
            result = [label]
            result.extend(self.voice(speech_generator.DEFAULT, obj=obj, **args))
            return result

        return []

    @log_generator_output
    def _generate_leaving(self, obj, **args):
        if settings_manager.get_manager().get_setting("onlySpeakDisplayedText"):
            return []

        if not args.get("leaving"):
            return []

        if self._script.utilities.inDocumentContent(obj) \
           and not self._script.utilities.inDocumentContent(
               focus_manager.get_manager().get_locus_of_focus()):
            result = [""]
            result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))
            return result

        return super()._generate_leaving(obj, **args)

    @log_generator_output
    def _generate_new_radio_button_group(self, obj, **args):
        # TODO - JD: The default speech generator"s method determines group membership
        # via the member-of relation. We cannot count on that here. Plus, radio buttons
        # on the web typically live in a group which is labelled. Thus the new-ancestor
        # presentation accomplishes the same thing. Unless this can be further sorted out,
        # try to filter out some of the noise....
        return []

    @log_generator_output
    def _generate_number_of_children(self, obj, **args):
        if settings_manager.get_manager().get_setting("onlySpeakDisplayedText") \
           or settings_manager.get_manager().get_setting("speechVerbosityLevel") \
               == settings.VERBOSITY_LEVEL_BRIEF:
            return []

        # We handle things even for non-document content due to issues in
        # other toolkits (e.g. exposing list items to us that are not
        # exposed to sighted users)
        roles = [Atspi.Role.DESCRIPTION_LIST,
                 Atspi.Role.LIST,
                 Atspi.Role.LIST_BOX,
                 "ROLE_FEED"]
        role = args.get("role", AXObject.get_role(obj))
        if role not in roles:
            return super()._generate_number_of_children(obj, **args)

        set_size = AXUtilities.get_set_size(AXObject.get_child(obj, 0))
        if set_size is None:
            if AXUtilities.is_description_list(obj, role):
                set_size = len(self._script.utilities.descriptionListTerms(obj))
            elif AXUtilities.is_list_box(obj, role) or AXUtilities.is_list(obj, role):
                set_size = len(list(AXObject.iter_children(obj, AXUtilities.is_list_item)))

        if not set_size:
            return []

        if AXUtilities.is_description_list(obj):
            result = [messages.descriptionListTermCount(set_size)]
        elif role == "ROLE_FEED":
            result = [messages.feedArticleCount(set_size)]
        else:
            result = [messages.listItemCount(set_size)]
        result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))
        return result

    def get_localized_role_name(self, obj, **args):
        if not self._script.utilities.inDocumentContent(obj):
            return super().get_localized_role_name(obj, **args)

        role_description = self._script.utilities.getRoleDescription(obj)
        if role_description:
            return role_description

        return super().get_localized_role_name(obj, **args)

    @log_generator_output
    def _generate_real_active_descendant_displayed_text(self, obj, **args):
        if not self._script.utilities.inDocumentContent(obj):
            return super()._generate_real_active_descendant_displayed_text(obj, **args)

        rad = self._script.utilities.realActiveDescendant(obj)
        return self._generate_text_content(rad, **args)

    @log_generator_output
    def _generate_accessible_role(self, obj, **args):
        if not self._script.utilities.inDocumentContent(obj):
            return super()._generate_accessible_role(obj, **args)

        # Do this check before the roledescription check, e.g. navigation within VSCode's editor.
        if AXUtilities.is_editable(obj) and obj == args.get("priorObj"):
            return []

        roledescription = self._script.utilities.getRoleDescription(obj)
        if roledescription:
            result = [roledescription]
            result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))
            return result

        role = args.get("role", AXObject.get_role(obj))
        start = args.get("startOffset")
        end = args.get("endOffset")
        index = args.get("index", 0)
        total = args.get("total", 1)

        ancestor_with_usable_role = self._get_ancestor_with_usable_role(obj, **args)
        if not self._should_speak_role(obj, **args):
            if ancestor_with_usable_role:
                return self._generate_accessible_role(ancestor_with_usable_role)
            return []

        result = []
        mgr = input_event_manager.get_manager()
        is_editable = AXUtilities.is_editable(obj)
        if is_editable and not self._script.utilities.isContentEditableWithEmbeddedObjects(obj):
            if (mgr.last_event_was_forward_caret_navigation() or self._script.inSayAll()) and start:
                return []
            if mgr.last_event_was_backward_caret_navigation() \
               and self._script.utilities.treatAsTextObject(obj) \
               and end not in [None, AXText.get_character_count(obj)]:
                return []
            result.append(self.get_localized_role_name(obj, **args))
            result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))

        elif is_editable and self._script.utilities.isDocument(obj):
            parent = AXObject.get_parent(obj)
            if parent and not AXUtilities.is_editable(parent) \
               and not mgr.last_event_was_caret_navigation():
                result.append(object_properties.ROLE_EDITABLE_CONTENT)
                result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))

        elif role == Atspi.Role.HEADING:
            if index == total - 1 or not self._script.utilities.isFocusableWithMathChild(obj):
                level = self._script.utilities.headingLevel(obj)
                if level:
                    result.append(object_properties.ROLE_HEADING_LEVEL_SPEECH % {
                        "role": self.get_localized_role_name(obj, **args),
                        "level": level})
                    result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))
                else:
                    result.append(self.get_localized_role_name(obj, **args))
                    result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))

        elif self._script.utilities.isLink(obj):
            if AXUtilities.is_image(AXObject.get_parent(obj)):
                result.append(messages.IMAGE_MAP_LINK)
                result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))
            else:
                if self._script.utilities.hasUselessCanvasDescendant(obj):
                    result.append(self.get_localized_role_name(obj, role=Atspi.Role.IMAGE))
                    result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))
                if index == total - 1 or not self._script.utilities.isFocusableWithMathChild(obj):
                    result.append(self.get_localized_role_name(obj, **args))
                    result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))

        else:
            result.append(self.get_localized_role_name(obj, **args))
            result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))

        if ancestor_with_usable_role:
            result[1:1] = self._generate_accessible_role(ancestor_with_usable_role)

        return result

    @log_generator_output
    def _generate_position_in_list(self, obj, **args):
        if AXUtilities.is_list_item(obj):
            if args.get("index", 0) + 1 < args.get("total", 1):
                return []

        if args.get("formatType") not in ["basicWhereAmI", "detailedWhereAmI"]:
            if args.get("priorObj") == obj:
                return []

        return super()._generate_position_in_list(obj, **args)

    @log_generator_output
    def _generate_state_unselected(self, obj, **args):
        if not self._script.inFocusMode():
            return []

        return super()._generate_state_unselected(obj, **args)

    # TODO - JD: This function and its associated fake role really need to die....
    # TODO - JD: Why isn"t this logic part of normal table cell generation?
    @log_generator_output
    def _generate_real_table_cell(self, obj, **args):
        result = super()._generate_real_table_cell(obj, **args)
        if not self._script.inFocusMode():
            return result

        if settings_manager.get_manager().get_setting("speakCellCoordinates"):
            label = AXTable.get_label_for_cell_coordinates(obj)
            if label:
                result.append(label)
                result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))
                return result

            row, col = AXTable.get_cell_coordinates(obj)
            if self._script.utilities.cellRowChanged(obj):
                result.append(messages.TABLE_ROW % (row + 1))
                result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))
            if self._script.utilities.cellColumnChanged(obj):
                result.append(messages.TABLE_COLUMN % (col + 1))
                result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))

        return result

    def generate_speech(self, obj, **args):
        if not self._script.utilities.inDocumentContent(obj):
            tokens = ["WEB:", obj, "is not in document content. Calling default speech generator."]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return super().generate_speech(obj, **args)

        tokens = ["WEB: Generating speech for document object", obj]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        result = []
        if self._script.utilities.isLink(obj):
            args["role"] = Atspi.Role.LINK
        elif self._script.utilities.isCustomImage(obj):
            args["role"] = Atspi.Role.IMAGE
        elif self._script.utilities.treatAsDiv(obj, offset=args.get("startOffset")):
            args["role"] = Atspi.Role.SECTION
        else:
            args["role"] = self._get_functional_role(obj, **args)

        if "priorObj" not in args:
            document = self._script.utilities.getTopLevelDocumentForObject(obj)
            args["priorObj"] = self._script.utilities.getPriorContext(document)[0]

        start = args.get("startOffset", 0)
        end = args.get("endOffset", -1)
        args["language"], args["dialect"] = \
            self._script.utilities.getLanguageAndDialectForSubstring(obj, start, end)

        if not result:
            result = list(filter(lambda x: x, super().generate_speech(obj, **args)))

        tokens = ["WEB: Speech generation for document object", obj, "complete."]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return result

    def generate_contents(self, contents, **args):
        if not contents:
            return []

        result = []
        contents = self._script.utilities.filterContentsForPresentation(contents, True)
        tokens = ["WEB: Generating speech contents (length:", len(contents), ")"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        for i, content in enumerate(contents):
            obj, start, end, string = content
            tokens = [f"ITEM {i}: ", obj, f"start: {start}, end: {end} '{string}'"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            utterance = self.generate_speech(
                obj, startOffset=start, endOffset=end, string=string,
                index=i, total=len(contents), **args)
            if isinstance(utterance, list):
                def is_not_empty_list(x):
                    return not (isinstance(x, list) and not x)
                utterance = list(filter(is_not_empty_list, utterance))
            if utterance and utterance[0]:
                result.append(utterance)
                args["priorObj"] = obj

        if not result:
            if self._script.inSayAll(treatInterruptedAsIn=False) \
               or not settings_manager.get_manager().get_setting("speakBlankLines") \
               or args.get("formatType") == "ancestor":
                string = ""
            else:
                string = messages.BLANK
            result = [string, self.voice(speech_generator.DEFAULT, **args)]

        return result
