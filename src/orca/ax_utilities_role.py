# Utilities for obtaining role-related information.
#
# Copyright 2023 Igalia, S.L.
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

# pylint: disable=wrong-import-position
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-lines
# pylint: disable=too-many-branches
# pylint: disable=too-many-return-statements
# pylint: disable=too-many-statements
# pylint: disable=duplicate-code

"""Utilities for obtaining role-related information."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2023 Igalia, S.L."
__license__   = "LGPL"

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from . import object_properties
from .ax_object import AXObject
from .ax_utilities_state import AXUtilitiesState

class AXUtilitiesRole:
    """Utilities for obtaining role-related information."""

    @staticmethod
    def _get_tag(obj):
        attrs = AXObject.get_attributes_dict(obj)
        return attrs.get("tag")

    @staticmethod
    def _get_xml_roles(obj):
        attrs = AXObject.get_attributes_dict(obj)
        return attrs.get("xml-roles", "").split()

    @staticmethod
    def get_dialog_roles(include_alert_as_dialog=True):
        """Returns the list of roles we consider documents"""

        roles = [Atspi.Role.COLOR_CHOOSER,
                 Atspi.Role.DIALOG,
                 Atspi.Role.FILE_CHOOSER]
        if include_alert_as_dialog:
            roles.append(Atspi.Role.ALERT)
        return roles

    @staticmethod
    def get_document_roles():
        """Returns the list of roles we consider documents"""

        roles = [Atspi.Role.DOCUMENT_EMAIL,
                 Atspi.Role.DOCUMENT_FRAME,
                 Atspi.Role.DOCUMENT_PRESENTATION,
                 Atspi.Role.DOCUMENT_SPREADSHEET,
                 Atspi.Role.DOCUMENT_TEXT,
                 Atspi.Role.DOCUMENT_WEB]
        return roles

    @staticmethod
    def get_form_field_roles():
        """Returns the list of roles we consider form fields"""

        roles = [Atspi.Role.CHECK_BOX,
                 Atspi.Role.RADIO_BUTTON,
                 Atspi.Role.COMBO_BOX,
                 Atspi.Role.DOCUMENT_FRAME, # rich text editing pred recommended
                 Atspi.Role.TEXT, # predicate recommended to check it is editable
                 Atspi.Role.LIST_BOX,
                 Atspi.Role.ENTRY,
                 Atspi.Role.PASSWORD_TEXT,
                 Atspi.Role.PUSH_BUTTON,
                 Atspi.Role.SPIN_BUTTON,
                 Atspi.Role.TOGGLE_BUTTON]
        return roles

    @staticmethod
    def get_layout_only_roles():
        """Returns the list of roles we consider are for layout only"""

        roles = [Atspi.Role.AUTOCOMPLETE,
                 Atspi.Role.FILLER,
                 Atspi.Role.REDUNDANT_OBJECT,
                 Atspi.Role.UNKNOWN,
                 Atspi.Role.SCROLL_PANE,
                 Atspi.Role.TEAROFF_MENU_ITEM]
        return roles

    @staticmethod
    def get_menu_item_roles():
        """Returns the list of roles we consider menu items"""

        roles = [Atspi.Role.MENU_ITEM,
                 Atspi.Role.CHECK_MENU_ITEM,
                 Atspi.Role.RADIO_MENU_ITEM,
                 Atspi.Role.TEAROFF_MENU_ITEM]
        return roles

    @staticmethod
    def get_menu_related_roles():
        """Returns the list of roles we consider menu related"""

        roles = [Atspi.Role.MENU,
                 Atspi.Role.MENU_BAR,
                 Atspi.Role.POPUP_MENU,
                 Atspi.Role.MENU_ITEM,
                 Atspi.Role.CHECK_MENU_ITEM,
                 Atspi.Role.RADIO_MENU_ITEM,
                 Atspi.Role.TEAROFF_MENU_ITEM]
        return roles

    @staticmethod
    def get_roles_to_exclude_from_clickables_list():
        """Returns the list of roles we want to exclude from the list of clickables"""

        roles = [Atspi.Role.COMBO_BOX,
                 Atspi.Role.ENTRY,
                 Atspi.Role.LIST_BOX,
                 Atspi.Role.MENU,
                 Atspi.Role.MENU_ITEM,
                 Atspi.Role.CHECK_MENU_ITEM,
                 Atspi.Role.RADIO_MENU_ITEM,
                 Atspi.Role.PAGE_TAB,
                 Atspi.Role.PAGE_TAB_LIST,
                 Atspi.Role.PASSWORD_TEXT,
                 Atspi.Role.PROGRESS_BAR,
                 Atspi.Role.SLIDER,
                 Atspi.Role.SPIN_BUTTON,
                 Atspi.Role.TOOL_BAR,
                 Atspi.Role.TREE_ITEM,
                 Atspi.Role.TREE_TABLE,
                 Atspi.Role.TREE]
        return roles

    @staticmethod
    def get_set_container_roles():
        """Returns the list of roles we consider a set container"""

        roles = [Atspi.Role.LIST,
                 Atspi.Role.MENU,
                 Atspi.Role.PAGE_TAB_LIST,
                 Atspi.Role.TABLE,
                 Atspi.Role.TREE,
                 Atspi.Role.TREE_TABLE]
        return roles

    @staticmethod
    def get_table_cell_roles(include_headers=True):
        """Returns the list of roles we consider table cells"""

        roles = [Atspi.Role.TABLE_CELL]
        if include_headers:
            roles.extend([Atspi.Role.TABLE_COLUMN_HEADER,
                          Atspi.Role.TABLE_ROW_HEADER,
                          Atspi.Role.COLUMN_HEADER,
                          Atspi.Role.ROW_HEADER])
        return roles

    @staticmethod
    def get_table_header_roles():
        """Returns the list of roles we consider table headers"""

        roles = [Atspi.Role.TABLE_COLUMN_HEADER,
                 Atspi.Role.TABLE_ROW_HEADER,
                 Atspi.Role.COLUMN_HEADER,
                 Atspi.Role.ROW_HEADER]
        return roles

    @staticmethod
    def get_table_related_roles(include_caption=False):
        """Returns the list of roles we consider table related"""

        roles = [Atspi.Role.TABLE,
                 Atspi.Role.TABLE_CELL,
                 Atspi.Role.TABLE_COLUMN_HEADER,
                 Atspi.Role.TABLE_ROW_HEADER,
                 Atspi.Role.COLUMN_HEADER,
                 Atspi.Role.ROW_HEADER]
        if include_caption:
            roles.append(Atspi.Role.CAPTION)
        return roles

    @staticmethod
    def get_tree_related_roles():
        """Returns the list of roles we consider tree related"""

        roles = [Atspi.Role.TREE,
                 Atspi.Role.TREE_ITEM,
                 Atspi.Role.TREE_TABLE]
        return roles

    @staticmethod
    def get_widget_roles():
        """Returns the list of roles we consider widgets"""

        roles = [Atspi.Role.CHECK_BOX,
                 Atspi.Role.COMBO_BOX,
                 Atspi.Role.ENTRY,
                 Atspi.Role.LIST_BOX,
                 Atspi.Role.PASSWORD_TEXT,
                 Atspi.Role.PUSH_BUTTON,
                 Atspi.Role.RADIO_BUTTON,
                 Atspi.Role.SLIDER,
                 Atspi.Role.SPIN_BUTTON,
                 Atspi.Role.TEXT, # predicate recommended to check it is editable
                 Atspi.Role.TOGGLE_BUTTON]
        return roles

    @staticmethod
    def get_localized_role_name(obj, role=None):
        """Returns a string representing the localized role name of obj."""

        if role is None:
            role = AXObject.get_role(obj)

        if AXObject.supports_value(obj):
            if AXUtilitiesRole.is_horizontal_slider(obj, role):
                return object_properties.ROLE_SLIDER_HORIZONTAL
            if AXUtilitiesRole.is_vertical_slider(obj, role):
                return object_properties.ROLE_SLIDER_VERTICAL
            if AXUtilitiesRole.is_horizontal_scrollbar(obj, role):
                return object_properties.ROLE_SCROLL_BAR_HORIZONTAL
            if AXUtilitiesRole.is_vertical_scrollbar(obj, role):
                return object_properties.ROLE_SCROLL_BAR_VERTICAL
            if AXUtilitiesRole.is_horizontal_separator(obj, role):
                return object_properties.ROLE_SPLITTER_HORIZONTAL
            if AXUtilitiesRole.is_vertical_separator(obj, role):
                return object_properties.ROLE_SPLITTER_VERTICAL
            if AXUtilitiesRole.is_split_pane(obj, role):
                # The splitter has the opposite orientation of the split pane.
                if AXObject.has_state(obj, Atspi.StateType.HORIZONTAL):
                    return object_properties.ROLE_SPLITTER_VERTICAL
                if AXObject.has_state(obj, Atspi.StateType.VERTICAL):
                    return object_properties.ROLE_SPLITTER_HORIZONTAL

        if AXUtilitiesRole.is_suggestion(obj, role):
            return object_properties.ROLE_CONTENT_SUGGESTION

        if AXUtilitiesRole.is_feed(obj, role):
            return object_properties.ROLE_FEED

        if AXUtilitiesRole.is_figure(obj, role):
            return object_properties.ROLE_FIGURE

        if AXUtilitiesRole.is_switch(obj, role):
            return object_properties.ROLE_SWITCH

        if AXUtilitiesRole.is_dpub(obj):
            if AXUtilitiesRole.is_landmark(obj, role):
                if AXUtilitiesRole.is_dpub_acknowledgments(obj, role):
                    return object_properties.ROLE_ACKNOWLEDGMENTS
                if AXUtilitiesRole.is_dpub_afterword(obj, role):
                    return object_properties.ROLE_AFTERWORD
                if AXUtilitiesRole.is_dpub_appendix(obj, role):
                    return object_properties.ROLE_APPENDIX
                if AXUtilitiesRole.is_dpub_bibliography(obj, role):
                    return object_properties.ROLE_BIBLIOGRAPHY
                if AXUtilitiesRole.is_dpub_chapter(obj, role):
                    return object_properties.ROLE_CHAPTER
                if AXUtilitiesRole.is_dpub_conclusion(obj, role):
                    return object_properties.ROLE_CONCLUSION
                if AXUtilitiesRole.is_dpub_credits(obj, role):
                    return object_properties.ROLE_CREDITS
                if AXUtilitiesRole.is_dpub_endnotes(obj, role):
                    return object_properties.ROLE_ENDNOTES
                if AXUtilitiesRole.is_dpub_epilogue(obj, role):
                    return object_properties.ROLE_EPILOGUE
                if AXUtilitiesRole.is_dpub_errata(obj, role):
                    return object_properties.ROLE_ERRATA
                if AXUtilitiesRole.is_dpub_foreword(obj, role):
                    return object_properties.ROLE_FOREWORD
                if AXUtilitiesRole.is_dpub_glossary(obj, role):
                    return object_properties.ROLE_GLOSSARY
                if AXUtilitiesRole.is_dpub_index(obj, role):
                    return object_properties.ROLE_INDEX
                if AXUtilitiesRole.is_dpub_introduction(obj, role):
                    return object_properties.ROLE_INTRODUCTION
                if AXUtilitiesRole.is_dpub_pagelist(obj, role):
                    return object_properties.ROLE_PAGELIST
                if AXUtilitiesRole.is_dpub_part(obj, role):
                    return object_properties.ROLE_PART
                if AXUtilitiesRole.is_dpub_preface(obj, role):
                    return object_properties.ROLE_PREFACE
                if AXUtilitiesRole.is_dpub_prologue(obj, role):
                    return object_properties.ROLE_PROLOGUE
                if AXUtilitiesRole.is_dpub_toc(obj, role):
                    return object_properties.ROLE_TOC
            elif role == "ROLE_DPUB_SECTION":
                if AXUtilitiesRole.is_dpub_abstract(obj, role):
                    return object_properties.ROLE_ABSTRACT
                if AXUtilitiesRole.is_dpub_colophon(obj, role):
                    return object_properties.ROLE_COLOPHON
                if AXUtilitiesRole.is_dpub_credit(obj, role):
                    return object_properties.ROLE_CREDIT
                if AXUtilitiesRole.is_dpub_dedication(obj, role):
                    return object_properties.ROLE_DEDICATION
                if AXUtilitiesRole.is_dpub_epigraph(obj, role):
                    return object_properties.ROLE_EPIGRAPH
                if AXUtilitiesRole.is_dpub_example(obj, role):
                    return object_properties.ROLE_EXAMPLE
                if AXUtilitiesRole.is_dpub_pullquote(obj, role):
                    return object_properties.ROLE_PULLQUOTE
                if AXUtilitiesRole.is_dpub_qna(obj, role):
                    return object_properties.ROLE_QNA
            elif AXUtilitiesRole.is_list_item(obj, role):
                if AXUtilitiesRole.is_dpub_biblioref(obj, role):
                    return object_properties.ROLE_BIBLIOENTRY
                if AXUtilitiesRole.is_dpub_endnote(obj, role):
                    return object_properties.ROLE_ENDNOTE
            else:
                if AXUtilitiesRole.is_dpub_cover(obj, role):
                    return object_properties.ROLE_COVER
                if AXUtilitiesRole.is_dpub_pagebreak(obj, role):
                    return object_properties.ROLE_PAGEBREAK
                if AXUtilitiesRole.is_dpub_subtitle(obj, role):
                    return object_properties.ROLE_SUBTITLE

        if AXUtilitiesRole.is_landmark(obj, role):
            if AXUtilitiesRole.is_landmark_without_type(obj, role):
                return ""
            if AXUtilitiesRole.is_landmark_banner(obj, role):
                return object_properties.ROLE_LANDMARK_BANNER
            if AXUtilitiesRole.is_landmark_complementary(obj, role):
                return object_properties.ROLE_LANDMARK_COMPLEMENTARY
            if AXUtilitiesRole.is_landmark_contentinfo(obj, role):
                return object_properties.ROLE_LANDMARK_CONTENTINFO
            if AXUtilitiesRole.is_landmark_main(obj, role):
                return object_properties.ROLE_LANDMARK_MAIN
            if AXUtilitiesRole.is_landmark_navigation(obj, role):
                return object_properties.ROLE_LANDMARK_NAVIGATION
            if AXUtilitiesRole.is_landmark_region(obj, role):
                return object_properties.ROLE_LANDMARK_REGION
            if AXUtilitiesRole.is_landmark_search(obj, role):
                return object_properties.ROLE_LANDMARK_SEARCH
            if AXUtilitiesRole.is_landmark_form(obj, role):
                role = Atspi.Role.FORM
        elif AXUtilitiesRole.is_comment(obj, role):
            role = Atspi.Role.COMMENT

        if not isinstance(role, Atspi.Role):
            return AXObject.get_role_name(obj, True)

        return Atspi.role_get_localized_name(role)

    @staticmethod
    def have_same_role(obj1, obj2):
        """Returns True if obj1 and obj2 have the same role"""

        return AXObject.get_role(obj1) == AXObject.get_role(obj2)

    @staticmethod
    def is_accelerator_label(obj, role=None):
        """Returns True if obj has the accelerator label role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.ACCELERATOR_LABEL

    @staticmethod
    def is_alert(obj, role=None):
        """Returns True if obj has the alert role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.ALERT

    @staticmethod
    def is_animation(obj, role=None):
        """Returns True if obj has the animation role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.ANIMATION

    @staticmethod
    def is_application(obj, role=None):
        """Returns True if obj has the application role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.APPLICATION

    @staticmethod
    def is_arrow(obj, role=None):
        """Returns True if obj has the arrow role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.ARROW

    @staticmethod
    def is_article(obj, role=None):
        """Returns True if obj has the article role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.ARTICLE

    @staticmethod
    def is_audio(obj, role=None):
        """Returns True if obj has the audio role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.AUDIO

    @staticmethod
    def is_autocomplete(obj, role=None):
        """Returns True if obj has the autocomplete role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.AUTOCOMPLETE

    @staticmethod
    def is_block_quote(obj, role=None):
        """Returns True if obj has the block quote role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.BLOCK_QUOTE or AXUtilitiesRole._get_tag(obj) == "blockquote"

    @staticmethod
    def is_button(obj, role=None):
        """Returns True if obj has the push- or toggle-button role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role in [Atspi.Role.PUSH_BUTTON, Atspi.Role.TOGGLE_BUTTON]

    @staticmethod
    def is_button_with_popup(obj, role=None):
        """Returns True if obj has the push- or toggle-button role and a popup"""

        if not AXUtilitiesRole.is_button(obj, role):
            return False
        return AXUtilitiesState.has_popup(obj)

    @staticmethod
    def is_calendar(obj, role=None):
        """Returns True if obj has the calendar role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.CALENDAR

    @staticmethod
    def is_canvas(obj, role=None):
        """Returns True if obj has the canvas role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.CANVAS

    @staticmethod
    def is_caption(obj, role=None):
        """Returns True if obj has the caption role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.CAPTION

    @staticmethod
    def is_chart(obj, role=None):
        """Returns True if obj has the chart role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.CHART

    @staticmethod
    def is_check_box(obj, role=None):
        """Returns True if obj has the checkbox role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.CHECK_BOX

    @staticmethod
    def is_check_menu_item(obj, role=None):
        """Returns True if obj has the check menuitem role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.CHECK_MENU_ITEM

    @staticmethod
    def is_code(obj, _role=None):
        """Returns True if obj has the code or code-like role"""

        return "code" in AXUtilitiesRole._get_xml_roles(obj) \
            or AXUtilitiesRole._get_tag(obj) in ["code", "pre"]

    @staticmethod
    def is_color_chooser(obj, role=None):
        """Returns True if obj has the color_chooser role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.COLOR_CHOOSER

    @staticmethod
    def is_column_header(obj, role=None):
        """Returns True if obj has the column header role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.COLUMN_HEADER

    @staticmethod
    def is_combo_box(obj, role=None):
        """Returns True if obj has the combobox role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.COMBO_BOX

    @staticmethod
    def is_comment(obj, role=None):
        """Returns True if obj has the comment role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.COMMENT or "comment" in AXUtilitiesRole._get_xml_roles(obj)

    @staticmethod
    def is_content_deletion(obj, role=None):
        """Returns True if obj has the content deletion role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.CONTENT_DELETION \
                or "deletion" in AXUtilitiesRole._get_xml_roles(obj) \
                or "del" == AXUtilitiesRole._get_tag(obj)

    @staticmethod
    def is_content_insertion(obj, role=None):
        """Returns True if obj has the content insertion role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.CONTENT_INSERTION \
                or "insertion" in AXUtilitiesRole._get_xml_roles(obj) \
                or "ins" == AXUtilitiesRole._get_tag(obj)

    @staticmethod
    def is_date_editor(obj, role=None):
        """Returns True if obj has the date editor role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.DATE_EDITOR

    @staticmethod
    def is_default_button(obj, role=None):
        """Returns True if obj has the push button role the is-default state"""

        return AXUtilitiesRole.is_push_button(obj, role) \
            and AXObject.has_state(obj, Atspi.StateType.IS_DEFAULT)

    @staticmethod
    def is_definition(obj, role=None):
        """Returns True if obj has the definition role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.DEFINITION

    @staticmethod
    def is_description_list(obj, role=None):
        """Returns True if obj has the description list role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.DESCRIPTION_LIST \
            or "dl" == AXUtilitiesRole._get_tag(obj)

    @staticmethod
    def is_description_term(obj, role=None):
        """Returns True if obj has the description term role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.DESCRIPTION_TERM \
            or "dt" == AXUtilitiesRole._get_tag(obj)

    @staticmethod
    def is_description_value(obj, role=None):
        """Returns True if obj has the description value role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.DESCRIPTION_VALUE \
            or "dd" == AXUtilitiesRole._get_tag(obj)

    @staticmethod
    def is_desktop_frame(obj, role=None):
        """Returns True if obj has the desktop frame role"""

        if role is None:
            role = AXObject.get_role(obj)
        if role == Atspi.Role.DESKTOP_FRAME:
            return True
        if role == Atspi.Role.FRAME:
            attrs = AXObject.get_attributes_dict(obj)
            return attrs.get("is-desktop") == "true"
        return False

    @staticmethod
    def is_desktop_icon(obj, role=None):
        """Returns True if obj has the desktop icon role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.DESKTOP_ICON

    @staticmethod
    def is_dial(obj, role=None):
        """Returns True if obj has the dial role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.DIAL

    @staticmethod
    def is_dialog(obj, role=None):
        """Returns True if obj has the dialog role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.DIALOG

    @staticmethod
    def is_dialog_or_alert(obj, role=None):
        """Returns True if obj has any dialog or alert role"""

        roles = AXUtilitiesRole.get_dialog_roles(True)
        if role is None:
            role = AXObject.get_role(obj)
        return role in roles

    @staticmethod
    def is_dialog_or_window(obj, role=None):
        """Returns True if obj has any dialog or window-related role"""

        roles = AXUtilitiesRole.get_dialog_roles(False)
        roles.extend((Atspi.Role.FRAME, Atspi.Role.WINDOW))
        if role is None:
            role = AXObject.get_role(obj)
        return role in roles

    @staticmethod
    def is_directory_pane(obj, role=None):
        """Returns True if obj has the directory pane role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.DIRECTORY_PANE

    @staticmethod
    def is_docked_frame(obj, role=None):
        """Returns True if obj has the frame role and is docked."""

        if not AXUtilitiesRole.is_frame(obj, role):
            return False

        attrs = AXObject.get_attributes_dict(obj)
        return attrs.get("window-type") == "dock"

    @staticmethod
    def is_document(obj, role=None):
        """Returns True if obj has any document-related role"""

        roles = AXUtilitiesRole.get_document_roles()
        if role is None:
            role = AXObject.get_role(obj)
        return role in roles

    @staticmethod
    def is_document_email(obj, role=None):
        """Returns True if obj has the document email role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.DOCUMENT_EMAIL

    @staticmethod
    def is_document_frame(obj, role=None):
        """Returns True if obj has the document frame role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.DOCUMENT_FRAME

    @staticmethod
    def is_document_presentation(obj, role=None):
        """Returns True if obj has the document presentation role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.DOCUMENT_PRESENTATION

    @staticmethod
    def is_document_spreadsheet(obj, role=None):
        """Returns True if obj has the document spreadsheet role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.DOCUMENT_SPREADSHEET

    @staticmethod
    def is_document_text(obj, role=None):
        """Returns True if obj has the document text role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.DOCUMENT_TEXT

    @staticmethod
    def is_document_web(obj, role=None):
        """Returns True if obj has the document web role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.DOCUMENT_WEB

    @staticmethod
    def is_dpub(obj, _role=None):
        """Returns True if obj has a DPub role."""

        roles = AXUtilitiesRole._get_xml_roles(obj)
        rv = bool(list(filter(lambda x: x.startswith("doc-"), roles)))
        return rv

    @staticmethod
    def is_dpub_abstract(obj, _role=None):
        """Returns True if obj has the DPub abstract role."""

        return "doc-abstract" in AXUtilitiesRole._get_xml_roles(obj)

    @staticmethod
    def is_dpub_acknowledgments(obj, _role=None):
        """Returns True if obj has the DPub acknowledgments role."""

        return "doc-acknowledgments" in AXUtilitiesRole._get_xml_roles(obj)

    @staticmethod
    def is_dpub_afterword(obj, _role=None):
        """Returns True if obj has the DPub afterword role."""

        return "doc-afterword" in AXUtilitiesRole._get_xml_roles(obj)

    @staticmethod
    def is_dpub_appendix(obj, _role=None):
        """Returns True if obj has the DPub appendix role."""

        return "doc-appendix" in AXUtilitiesRole._get_xml_roles(obj)

    @staticmethod
    def is_dpub_backlink(obj, _role=None):
        """Returns True if obj has the DPub backlink role."""

        return "doc-backlink" in AXUtilitiesRole._get_xml_roles(obj)

    @staticmethod
    def is_dpub_biblioref(obj, _role=None):
        """Returns True if obj has the DPub biblioref role."""

        return "doc-biblioref" in AXUtilitiesRole._get_xml_roles(obj)

    @staticmethod
    def is_dpub_bibliography(obj, _role=None):
        """Returns True if obj has the DPub bibliography role."""

        return "doc-bibliography" in AXUtilitiesRole._get_xml_roles(obj)

    @staticmethod
    def is_dpub_chapter(obj, _role=None):
        """Returns True if obj has the DPub chapter role."""

        return "doc-chapter" in AXUtilitiesRole._get_xml_roles(obj)

    @staticmethod
    def is_dpub_colophon(obj, _role=None):
        """Returns True if obj has the DPub colophon role."""

        return "doc-colophon" in AXUtilitiesRole._get_xml_roles(obj)

    @staticmethod
    def is_dpub_conclusion(obj, _role=None):
        """Returns True if obj has the DPub conclusion role."""

        return "doc-conclusion" in AXUtilitiesRole._get_xml_roles(obj)

    @staticmethod
    def is_dpub_cover(obj, _role=None):
        """Returns True if obj has the DPub cover role."""

        return "doc-cover" in AXUtilitiesRole._get_xml_roles(obj)

    @staticmethod
    def is_dpub_credit(obj, _role=None):
        """Returns True if obj has the DPub credit role."""

        return "doc-credit" in AXUtilitiesRole._get_xml_roles(obj)

    @staticmethod
    def is_dpub_credits(obj, _role=None):
        """Returns True if obj has the DPub credits role."""

        return "doc-credits" in AXUtilitiesRole._get_xml_roles(obj)

    @staticmethod
    def is_dpub_dedication(obj, _role=None):
        """Returns True if obj has the DPub dedication role."""

        return "doc-dedication" in AXUtilitiesRole._get_xml_roles(obj)

    @staticmethod
    def is_dpub_endnote(obj, _role=None):
        """Returns True if obj has the DPub endnote role."""

        return "doc-endnote" in AXUtilitiesRole._get_xml_roles(obj)

    @staticmethod
    def is_dpub_endnotes(obj, _role=None):
        """Returns True if obj has the DPub endnotes role."""

        return "doc-endnotes" in AXUtilitiesRole._get_xml_roles(obj)

    @staticmethod
    def is_dpub_epigraph(obj, _role=None):
        """Returns True if obj has the DPub epigraph role."""

        return "doc-epigraph" in AXUtilitiesRole._get_xml_roles(obj)

    @staticmethod
    def is_dpub_epilogue(obj, _role=None):
        """Returns True if obj has the DPub epilogue role."""

        return "doc-epilogue" in AXUtilitiesRole._get_xml_roles(obj)

    @staticmethod
    def is_dpub_errata(obj, _role=None):
        """Returns True if obj has the DPub errata role."""

        return "doc-errata" in AXUtilitiesRole._get_xml_roles(obj)

    @staticmethod
    def is_dpub_example(obj, _role=None):
        """Returns True if obj has the DPub example role."""

        return "doc-example" in AXUtilitiesRole._get_xml_roles(obj)

    @staticmethod
    def is_dpub_footnote(obj, _role=None):
        """Returns True if obj has the DPub footnote role."""

        return "doc-footnote" in AXUtilitiesRole._get_xml_roles(obj)

    @staticmethod
    def is_dpub_foreword(obj, _role=None):
        """Returns True if obj has the DPub foreword role."""

        return "doc-foreword" in AXUtilitiesRole._get_xml_roles(obj)

    @staticmethod
    def is_dpub_glossary(obj, _role=None):
        """Returns True if obj has the DPub glossary role."""

        return "doc-glossary" in AXUtilitiesRole._get_xml_roles(obj)

    @staticmethod
    def is_dpub_glossref(obj, _role=None):
        """Returns True if obj has the DPub glossref role."""

        return "doc-glossref" in AXUtilitiesRole._get_xml_roles(obj)

    @staticmethod
    def is_dpub_index(obj, _role=None):
        """Returns True if obj has the DPub index role."""

        return "doc-index" in AXUtilitiesRole._get_xml_roles(obj)

    @staticmethod
    def is_dpub_introduction(obj, _role=None):
        """Returns True if obj has the DPub introduction role."""

        return "doc-introduction" in AXUtilitiesRole._get_xml_roles(obj)

    @staticmethod
    def is_dpub_noteref(obj, _role=None):
        """Returns True if obj has the DPub noteref role."""

        return "doc-noteref" in AXUtilitiesRole._get_xml_roles(obj)

    @staticmethod
    def is_dpub_pagelist(obj, _role=None):
        """Returns True if obj has the DPub pagelist role."""

        return "doc-pagelist" in AXUtilitiesRole._get_xml_roles(obj)

    @staticmethod
    def is_dpub_pagebreak(obj, _role=None):
        """Returns True if obj has the DPub pagebreak role."""

        return "doc-pagebreak" in AXUtilitiesRole._get_xml_roles(obj)

    @staticmethod
    def is_dpub_part(obj, _role=None):
        """Returns True if obj has the DPub part role."""

        return "doc-part" in AXUtilitiesRole._get_xml_roles(obj)

    @staticmethod
    def is_dpub_preface(obj, _role=None):
        """Returns True if obj has the DPub preface role."""

        return "doc-preface" in AXUtilitiesRole._get_xml_roles(obj)

    @staticmethod
    def is_dpub_prologue(obj, _role=None):
        """Returns True if obj has the DPub prologue role."""

        return "doc-prologue" in AXUtilitiesRole._get_xml_roles(obj)

    @staticmethod
    def is_dpub_pullquote(obj, _role=None):
        """Returns True if obj has the DPub pullquote role."""

        return "doc-pullquote" in AXUtilitiesRole._get_xml_roles(obj)

    @staticmethod
    def is_dpub_qna(obj, _role=None):
        """Returns True if obj has the DPub qna role."""

        return "doc-qna" in AXUtilitiesRole._get_xml_roles(obj)

    @staticmethod
    def is_dpub_subtitle(obj, _role=None):
        """Returns True if obj has the DPub subtitle role."""

        return "doc-subtitle" in AXUtilitiesRole._get_xml_roles(obj)

    @staticmethod
    def is_dpub_toc(obj, _role=None):
        """Returns True if obj has the DPub toc role."""

        return "doc-toc" in AXUtilitiesRole._get_xml_roles(obj)

    @staticmethod
    def is_drawing_area(obj, role=None):
        """Returns True if obj has the drawing area role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.DRAWING_AREA

    @staticmethod
    def is_editbar(obj, role=None):
        """Returns True if obj has the editbar role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.EDITBAR

    @staticmethod
    def is_embedded(obj, role=None):
        """Returns True if obj has the embedded role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.EMBEDDED

    @staticmethod
    def is_entry(obj, role=None):
        """Returns True if obj has the entry role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.ENTRY

    @staticmethod
    def is_extended(obj, role=None):
        """Returns True if obj has the extended role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.EXTENDED

    @staticmethod
    def is_feed(obj, _role=None):
        """Returns True if obj has the feed role"""

        return "feed" in AXUtilitiesRole._get_xml_roles(obj)

    @staticmethod
    def is_feed_article(obj, role=None):
        """Returns True if obj has the article role and descends from a feed."""

        if not AXUtilitiesRole.is_article(obj, role):
            return False

        return AXObject.find_ancestor(obj, AXUtilitiesRole.is_feed) is not None

    @staticmethod
    def is_figure(obj, _role=None):
        """Returns True if obj has the figure role or tag."""

        return "figure" in AXUtilitiesRole._get_xml_roles(obj) \
            or AXUtilitiesRole._get_tag(obj) == "figure"

    @staticmethod
    def is_file_chooser(obj, role=None):
        """Returns True if obj has the file chooser role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.FILE_CHOOSER

    @staticmethod
    def is_filler(obj, role=None):
        """Returns True if obj has the filler role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.FILLER

    @staticmethod
    def is_focus_traversable(obj, role=None):
        """Returns True if obj has the focus traversable role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.FOCUS_TRAVERSABLE

    @staticmethod
    def is_font_chooser(obj, role=None):
        """Returns True if obj has the font chooser role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.FONT_CHOOSER

    @staticmethod
    def is_footer(obj, role=None):
        """Returns True if obj has the footer role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.FOOTER

    @staticmethod
    def is_footnote(obj, role=None):
        """Returns True if obj has the footnote role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.FOOTNOTE

    @staticmethod
    def is_form(obj, role=None):
        """Returns True if obj has the form role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.FORM

    @staticmethod
    def is_frame(obj, role=None):
        """Returns True if obj has the frame role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.FRAME

    @staticmethod
    def is_glass_pane(obj, role=None):
        """Returns True if obj has the glass pane role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.GLASS_PANE

    @staticmethod
    def is_grid(obj, role=None):
        """Returns True if obj has the grid role."""

        if not AXUtilitiesRole.is_table(obj, role):
            return False

        return "grid" in AXUtilitiesRole._get_xml_roles(obj)

    @staticmethod
    def is_grid_cell(obj, role=None):
        """Returns True if obj has the gridcell role or the cell role and is in a grid."""

        if not AXUtilitiesRole.is_table_cell(obj, role):
            return False

        roles = AXUtilitiesRole._get_xml_roles(obj)
        if "gridcell" in roles:
            return True
        if "cell" in roles:
            return AXObject.find_ancestor(obj, AXUtilitiesRole.is_grid)
        return False

    @staticmethod
    def is_group(obj, _role=None):
        """Returns True if obj is an ARIA group."""

        return "group" in AXUtilitiesRole._get_xml_roles(obj)

    @staticmethod
    def is_grouping(obj, role=None):
        """Returns True if obj has the grouping role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.GROUPING

    @staticmethod
    def is_header(obj, role=None):
        """Returns True if obj has the header role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.HEADER

    @staticmethod
    def is_heading(obj, role=None):
        """Returns True if obj has the heading role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.HEADING

    @staticmethod
    def is_html_container(obj, role=None):
        """Returns True if obj has the html container role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.HTML_CONTAINER

    @staticmethod
    def is_horizontal_scrollbar(obj, role=None):
        """Returns True if obj is a horizontal scrollbar"""

        return AXUtilitiesRole.is_scroll_bar(obj, role) \
            and AXObject.has_state(obj, Atspi.StateType.HORIZONTAL)

    @staticmethod
    def is_horizontal_separator(obj, role=None):
        """Returns True if obj is a horizontal separator"""

        return AXUtilitiesRole.is_separator(obj, role) \
            and AXObject.has_state(obj, Atspi.StateType.HORIZONTAL)

    @staticmethod
    def is_horizontal_slider(obj, role=None):
        """Returns True if obj is a horizontal slider"""

        return AXUtilitiesRole.is_slider(obj, role) \
            and AXObject.has_state(obj, Atspi.StateType.HORIZONTAL)

    @staticmethod
    def is_icon(obj, role=None):
        """Returns True if obj has the icon role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.ICON

    @staticmethod
    def is_icon_or_canvas(obj, role=None):
        """Returns True if obj has the icon or canvas role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role in [Atspi.Role.ICON, Atspi.Role.CANVAS]

    @staticmethod
    def is_image(obj, role=None):
        """Returns True if obj has the image role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.IMAGE

    @staticmethod
    def is_image_or_canvas(obj, role=None):
        """Returns True if obj has the image or canvas role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role in [Atspi.Role.IMAGE, Atspi.Role.CANVAS]

    @staticmethod
    def is_image_map(obj, role=None):
        """Returns True if obj has the image map role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.IMAGE_MAP

    @staticmethod
    def is_info_bar(obj, role=None):
        """Returns True if obj has the info bar role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.INFO_BAR

    @staticmethod
    def is_input_method_window(obj, role=None):
        """Returns True if obj has the input method window role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.INPUT_METHOD_WINDOW

    @staticmethod
    def is_internal_frame(obj, role=None):
        """Returns True if obj has the internal frame role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.INTERNAL_FRAME or AXUtilitiesRole._get_tag(obj) == "iframe"

    @staticmethod
    def is_invalid_role(obj, role=None):
        """Returns True if obj has the invalid role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.INVALID

    @staticmethod
    def is_label(obj, role=None):
        """Returns True if obj has the label role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.LABEL

    @staticmethod
    def is_label_or_caption(obj, role=None):
        """Returns True if obj has the label or caption role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role in [Atspi.Role.LABEL, Atspi.Role.CAPTION]

    @staticmethod
    def is_landmark(obj, role=None):
        """Returns True if obj has the landmark role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.LANDMARK

    @staticmethod
    def is_landmark_banner(obj, _role=None):
        """Returns True if obj has the banner landmark role"""

        return "banner" in AXUtilitiesRole._get_xml_roles(obj)

    @staticmethod
    def is_landmark_complementary(obj, _role=None):
        """Returns True if obj has the complementary landmark role"""

        return "complementary" in AXUtilitiesRole._get_xml_roles(obj)

    @staticmethod
    def is_landmark_contentinfo(obj, _role=None):
        """Returns True if obj has the contentinfo landmark role"""

        return "contentinfo" in AXUtilitiesRole._get_xml_roles(obj)

    @staticmethod
    def is_landmark_form(obj, _role=None):
        """Returns True if obj has the form landmark role"""

        return "form" in AXUtilitiesRole._get_xml_roles(obj)

    @staticmethod
    def is_landmark_main(obj, _role=None):
        """Returns True if obj has the main landmark role"""

        return "main" in AXUtilitiesRole._get_xml_roles(obj)

    @staticmethod
    def is_landmark_navigation(obj, _role=None):
        """Returns True if obj has the navigation landmark role"""

        return "navigation" in AXUtilitiesRole._get_xml_roles(obj)

    @staticmethod
    def is_landmark_region(obj, _role=None):
        """Returns True if obj has the region landmark role"""

        return "region" in AXUtilitiesRole._get_xml_roles(obj)

    @staticmethod
    def is_landmark_search(obj, _role=None):
        """Returns True if obj has the search landmark role"""

        return "search" in AXUtilitiesRole._get_xml_roles(obj)

    @staticmethod
    def is_landmark_without_type(obj, role=None):
        """Returns True if obj has the landmark role but no type"""

        if not AXUtilitiesRole.is_landmark(obj, role):
            return False

        roles = AXUtilitiesRole._get_xml_roles(obj)
        return not roles

    @staticmethod
    def is_layered_pane(obj, role=None):
        """Returns True if obj has the layered pane role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.LAYERED_PANE

    @staticmethod
    def is_level_bar(obj, role=None):
        """Returns True if obj has the level bar role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.LEVEL_BAR

    @staticmethod
    def is_link(obj, role=None):
        """Returns True if obj has the link role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.LINK

    @staticmethod
    def is_list(obj, role=None):
        """Returns True if obj has the list role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.LIST

    @staticmethod
    def is_list_box(obj, role=None):
        """Returns True if obj has the list box role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.LIST_BOX

    @staticmethod
    def is_list_item(obj, role=None):
        """Returns True if obj has the list item role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.LIST_ITEM

    @staticmethod
    def is_log(obj, role=None):
        """Returns True if obj has the log role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.LOG

    @staticmethod
    def is_mark(obj, role=None):
        """Returns True if obj has the mark role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.MARK \
               or "mark" in AXUtilitiesRole._get_xml_roles(obj) \
               or "mark" == AXUtilitiesRole._get_tag(obj)

    @staticmethod
    def is_marquee(obj, role=None):
        """Returns True if obj has the marquee role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.MARQUEE

    @staticmethod
    def is_math(obj, role=None):
        """Returns True if obj has the math role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.MATH

    @staticmethod
    def is_math_enclose(obj):
        """Returns True if obj has the math enclose role/tag"""

        return AXUtilitiesRole._get_tag(obj) == "menclose"

    @staticmethod
    def is_math_fenced(obj):
        """Returns True if obj has the math fenced role/tag"""

        return AXUtilitiesRole._get_tag(obj) == "mfenced"

    @staticmethod
    def is_math_fraction(obj, role=None):
        """Returns True if obj has the math fraction role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.MATH_FRACTION

    @staticmethod
    def is_math_fraction_without_bar(obj, role=None):
        """Returns True if obj has the math fraction role and lacks the fraction bar"""

        if not AXUtilitiesRole.is_math_fraction(obj, role):
            return False

        line_thickness = AXObject.get_attribute(obj, "linethickness")
        if not line_thickness:
            return False

        for char in line_thickness:
            if char.isnumeric() and char != "0":
                return False

        return True

    @staticmethod
    def is_math_layout_only(obj):
        """Returns True if obj has a layout-only math role"""

        return AXUtilitiesRole._get_tag(obj) in ["mrow", "mstyle", "merror", "mpadded", "none"]

    @staticmethod
    def is_math_multi_script(obj):
        """Returns True if obj has the math multi-scripts role/tag"""

        return AXUtilitiesRole._get_tag(obj) == "mmultiscripts"

    @staticmethod
    def is_math_related(obj, role=None):
        """Returns True if obj has a math-related role"""

        if role is None:
            role = AXObject.get_role(obj)
        if role in [Atspi.Role.MATH, Atspi.Role.MATH_FRACTION, Atspi.Role.MATH_ROOT]:
            return True
        return AXUtilitiesRole._get_tag(obj) in ["math",
                                                 "maction",
                                                 "maligngroup",
                                                 "malignmark",
                                                 "menclose",
                                                 "merror",
                                                 "mfenced",
                                                 "mfrac",
                                                 "mglyph",
                                                 "mi",
                                                 "mlabeledtr",
                                                 "mlongdiv",
                                                 "mmultiscripts",
                                                 "mn",
                                                 "mo",
                                                 "mover",
                                                 "mpadded",
                                                 "mphantom",
                                                 "mprescripts",
                                                 "mroot",
                                                 "mrow",
                                                 "ms",
                                                 "mscarries",
                                                 "mscarry",
                                                 "msgroup",
                                                 "msline",
                                                 "mspace",
                                                 "msqrt",
                                                 "msrow",
                                                 "mstack",
                                                 "mstyle",
                                                 "msub",
                                                 "msup",
                                                 "msubsup",
                                                 "mtable",
                                                 "mtd",
                                                 "mtext",
                                                 "mtr",
                                                 "munder",
                                                 "munderover"]

    @staticmethod
    def is_math_root(obj, role=None):
        """Returns True if obj has the math root role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.MATH_ROOT

    @staticmethod
    def is_math_square_root(obj):
        """Returns True if obj has the math root role/tag"""

        return AXUtilitiesRole._get_tag(obj) == "msqrt"

    @staticmethod
    def is_math_sub_or_super_script(obj):
        """Returns True if obj has the math subscript or superscript role/tag"""

        return AXUtilitiesRole._get_tag(obj) in ["msub", "msup", "msubsup"]

    @staticmethod
    def is_math_table(obj):
        """Returns True if obj has the math table role/tag"""

        return AXUtilitiesRole._get_tag(obj) == "mtable"

    @staticmethod
    def is_math_table_row(obj):
        """Returns True if obj has the math table row role/tag"""

        return AXUtilitiesRole._get_tag(obj) in ["mtr", "mlabeledtr"]

    @staticmethod
    def is_math_token(obj):
        """Returns True if obj has a math token role/tag"""

        return AXUtilitiesRole._get_tag(obj) in ["mi", "mn", "mo", "mtext", "ms", "mspace"]

    @staticmethod
    def is_math_under_or_over_script(obj):
        """Returns True if obj has the math under-script or over-script role/tag"""

        return AXUtilitiesRole._get_tag(obj) in ["mover", "munder", "munderover"]

    @staticmethod
    def is_menu(obj, role=None):
        """Returns True if obj has the menu role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.MENU

    @staticmethod
    def is_menu_bar(obj, role=None):
        """Returns True if obj has the menubar role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.MENU_BAR

    @staticmethod
    def is_menu_item(obj, role=None):
        """Returns True if obj has the menu item role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.MENU_ITEM

    @staticmethod
    def is_menu_item_of_any_kind(obj, role=None):
        """Returns True if obj has any menu item role"""

        roles = AXUtilitiesRole.get_menu_item_roles()
        if role is None:
            role = AXObject.get_role(obj)
        return role in roles

    @staticmethod
    def is_menu_related(obj, role=None):
        """Returns True if obj has any menu-related role"""

        roles = AXUtilitiesRole.get_menu_related_roles()
        if role is None:
            role = AXObject.get_role(obj)
        return role in roles

    @staticmethod
    def is_modal_dialog(obj, role=None):
        """Returns True if obj has the alert or dialog role and modal state"""

        return AXUtilitiesRole.is_dialog_or_alert(obj, role) \
            and AXObject.has_state(obj, Atspi.StateType.MODAL)

    @staticmethod
    def is_multi_line_entry(obj, role=None):
        """Returns True if obj has the entry role and multiline state"""

        return AXUtilitiesRole.is_entry(obj, role) \
            and AXObject.has_state(obj, Atspi.StateType.MULTI_LINE)

    @staticmethod
    def is_notification(obj, role=None):
        """Returns True if obj has the notification role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.NOTIFICATION

    @staticmethod
    def is_option_pane(obj, role=None):
        """Returns True if obj has the option pane role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.OPTION_PANE

    @staticmethod
    def is_page(obj, role=None):
        """Returns True if obj has the page role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.PAGE

    @staticmethod
    def is_page_tab(obj, role=None):
        """Returns True if obj has the page tab role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.PAGE_TAB

    @staticmethod
    def is_page_tab_list(obj, role=None):
        """Returns True if obj has the page tab list role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.PAGE_TAB_LIST

    @staticmethod
    def is_page_tab_list_related(obj, role=None):
        """Returns True if obj has the page tab or page tab list role"""

        roles = [Atspi.Role.PAGE_TAB_LIST, Atspi.Role.PAGE_TAB]
        if role is None:
            role = AXObject.get_role(obj)
        return role in roles

    @staticmethod
    def is_panel(obj, role=None):
        """Returns True if obj has the panel role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.PANEL

    @staticmethod
    def is_paragraph(obj, role=None):
        """Returns True if obj has the paragraph role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.PARAGRAPH

    @staticmethod
    def is_password_text(obj, role=None):
        """Returns True if obj has the password text role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.PASSWORD_TEXT

    @staticmethod
    def is_popup_menu(obj, role=None):
        """Returns True if obj has the popup menu role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.POPUP_MENU

    @staticmethod
    def is_progress_bar(obj, role=None):
        """Returns True if obj has the progress bar role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.PROGRESS_BAR

    @staticmethod
    def is_push_button(obj, role=None):
        """Returns True if obj has the push button role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.PUSH_BUTTON

    @staticmethod
    def is_push_button_menu(obj, role=None):
        """Returns True if obj has the push button menu role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.PUSH_BUTTON_MENU

    @staticmethod
    def is_radio_button(obj, role=None):
        """Returns True if obj has the radio button role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.RADIO_BUTTON

    @staticmethod
    def is_radio_menu_item(obj, role=None):
        """Returns True if obj has the radio menu item role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.RADIO_MENU_ITEM

    @staticmethod
    def is_rating(obj, role=None):
        """Returns True if obj has the rating role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.RATING

    @staticmethod
    def is_redundant_object_role(obj, role=None):
        """Returns True if obj has the redundant object role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.REDUNDANT_OBJECT

    @staticmethod
    def is_root_pane(obj, role=None):
        """Returns True if obj has the root pane role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.ROOT_PANE

    @staticmethod
    def is_row_header(obj, role=None):
        """Returns True if obj has the row header role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.ROW_HEADER

    @staticmethod
    def is_ruler(obj, role=None):
        """Returns True if obj has the ruler role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.RULER

    @staticmethod
    def is_scroll_bar(obj, role=None):
        """Returns True if obj has the scrollbar role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.SCROLL_BAR

    @staticmethod
    def is_scroll_pane(obj, role=None):
        """Returns True if obj has the scroll pane role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.SCROLL_PANE

    @staticmethod
    def is_section(obj, role=None):
        """Returns True if obj has the section role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.SECTION

    @staticmethod
    def is_separator(obj, role=None):
        """Returns True if obj has the separator role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.SEPARATOR

    @staticmethod
    def is_single_line_autocomplete_entry(obj, role=None):
        """Returns True if obj has the entry role and single-line state"""

        if not AXUtilitiesRole.is_single_line_entry(obj, role):
            return False

        return AXUtilitiesState.supports_autocompletion(obj)

    @staticmethod
    def is_single_line_entry(obj, role=None):
        """Returns True if obj has the entry role and the single-line state"""

        if not AXUtilitiesState.is_single_line(obj):
            return False
        if AXUtilitiesRole.is_entry(obj, role):
            return True
        if AXUtilitiesRole.is_text(obj, role):
            return AXUtilitiesState.is_editable(obj)
        return False

    @staticmethod
    def is_slider(obj, role=None):
        """Returns True if obj has the slider role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.SLIDER

    @staticmethod
    def is_spin_button(obj, role=None):
        """Returns True if obj has the spin button role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.SPIN_BUTTON

    @staticmethod
    def is_split_pane(obj, role=None):
        """Returns True if obj has the split pane role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.SPLIT_PANE

    @staticmethod
    def is_static(obj, role=None):
        """Returns True if obj has the static role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.STATIC

    @staticmethod
    def is_status_bar(obj, role=None):
        """Returns True if obj has the statusbar role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.STATUS_BAR

    @staticmethod
    def is_subscript(obj, role=None):
        """Returns True if obj has the subscript role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.SUBSCRIPT

    @staticmethod
    def is_subscript_or_superscript(obj, role=None):
        """Returns True if obj has the subscript or superscript role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role in [Atspi.Role.SUBSCRIPT, Atspi.Role.SUPERSCRIPT]

    @staticmethod
    def is_suggestion(obj, role=None):
        """Returns True if obj has the suggestion role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.SUGGESTION \
              or "suggestion" in AXUtilitiesRole._get_xml_roles(obj)

    @staticmethod
    def is_superscript(obj, role=None):
        """Returns True if obj has the superscript role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.SUPERSCRIPT

    @staticmethod
    def is_svg(obj):
        """Returns True if obj is an svg."""

        return AXUtilitiesRole._get_tag(obj) == "svg"

    @staticmethod
    def is_switch(obj, _role=None):
        """Returns True if obj has the switch role."""

        return "switch" in AXUtilitiesRole._get_xml_roles(obj)

    @staticmethod
    def is_table(obj, role=None):
        """Returns True if obj has the table role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.TABLE

    @staticmethod
    def is_table_cell(obj, role=None):
        """Returns True if obj has the table cell role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.TABLE_CELL

    @staticmethod
    def is_table_cell_or_header(obj, role=None):
        """Returns True if obj has the table cell or a header-related role"""

        roles = AXUtilitiesRole.get_table_cell_roles()
        if role is None:
            role = AXObject.get_role(obj)
        return role in roles

    @staticmethod
    def is_table_column_header(obj, role=None):
        """Returns True if obj has the table column header role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.TABLE_COLUMN_HEADER

    @staticmethod
    def is_table_header(obj, role=None):
        """Returns True if obj has a table header related role"""

        roles = AXUtilitiesRole.get_table_header_roles()
        if role is None:
            role = AXObject.get_role(obj)
        return role in roles

    @staticmethod
    def is_table_related(obj, role=None, include_caption=False):
        """Returns True if obj has a table-related role"""

        roles = AXUtilitiesRole.get_table_related_roles(include_caption)
        if role is None:
            role = AXObject.get_role(obj)
        return role in roles

    @staticmethod
    def is_table_row(obj, role=None):
        """Returns True if obj has the table row role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.TABLE_ROW

    @staticmethod
    def is_table_row_header(obj, role=None):
        """Returns True if obj has the table row header role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.TABLE_ROW_HEADER

    @staticmethod
    def is_tearoff_menu_item(obj, role=None):
        """Returns True if obj has the tearoff menu item role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.TEAROFF_MENU_ITEM

    @staticmethod
    def is_terminal(obj, role=None):
        """Returns True if obj has the terminal role"""
        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.TERMINAL

    @staticmethod
    def is_text(obj, role=None):
        """Returns True if obj has the text role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.TEXT

    @staticmethod
    def is_text_input(obj, role=None):
        """Returns True if obj has any role associated with textual input"""

        roles = [Atspi.Role.ENTRY, Atspi.Role.PASSWORD_TEXT, Atspi.Role.SPIN_BUTTON]
        if role is None:
            role = AXObject.get_role(obj)
        return role in roles

    @staticmethod
    def is_text_input_date(obj, role=None):
        """Returns True if obj is a date text input"""

        if not AXUtilitiesRole.is_text_input(obj, role):
            return False

        attrs = AXObject.get_attributes_dict(obj)
        return attrs.get("text-input-type") == "date"

    @staticmethod
    def is_text_input_email(obj, role=None):
        """Returns True if obj is an email text input"""

        if not AXUtilitiesRole.is_text_input(obj, role):
            return False

        attrs = AXObject.get_attributes_dict(obj)
        return attrs.get("text-input-type") == "email"

    @staticmethod
    def is_text_input_number(obj, role=None):
        """Returns True if obj is a numeric text input"""

        if not AXUtilitiesRole.is_text_input(obj, role):
            return False

        attrs = AXObject.get_attributes_dict(obj)
        return attrs.get("text-input-type") == "number"

    @staticmethod
    def is_text_input_telephone(obj, role=None):
        """Returns True if obj is a telephone text input"""

        if not AXUtilitiesRole.is_text_input(obj, role):
            return False

        attrs = AXObject.get_attributes_dict(obj)
        return attrs.get("text-input-type") == "telephone"

    @staticmethod
    def is_text_input_time(obj, role=None):
        """Returns True if obj is a time text input"""

        if not AXUtilitiesRole.is_text_input(obj, role):
            return False

        attrs = AXObject.get_attributes_dict(obj)
        return attrs.get("text-input-type") == "time"

    @staticmethod
    def is_text_input_url(obj, role=None):
        """Returns True if obj is a url text input"""

        if not AXUtilitiesRole.is_text_input(obj, role):
            return False

        attrs = AXObject.get_attributes_dict(obj)
        return attrs.get("text-input-type") == "url"

    @staticmethod
    def is_text_input_week(obj, role=None):
        """Returns True if obj is a week text input"""

        if not AXUtilitiesRole.is_text_input(obj, role):
            return False

        attrs = AXObject.get_attributes_dict(obj)
        return attrs.get("text-input-type") == "week"

    @staticmethod
    def is_time(obj, _role=None):
        """Returns True if obj has the time role"""

        return "time" in AXUtilitiesRole._get_xml_roles(obj) \
            or "time" == AXUtilitiesRole._get_tag(obj)

    @staticmethod
    def is_timer(obj, role=None):
        """Returns True if obj has the timer role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.TIMER

    @staticmethod
    def is_title_bar(obj, role=None):
        """Returns True if obj has the titlebar role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.TITLE_BAR

    @staticmethod
    def is_toggle_button(obj, role=None):
        """Returns True if obj has the toggle button role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.TOGGLE_BUTTON

    @staticmethod
    def is_tool_bar(obj, role=None):
        """Returns True if obj has the toolbar role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.TOOL_BAR

    @staticmethod
    def is_tool_tip(obj, role=None):
        """Returns True if obj has the tooltip role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.TOOL_TIP

    @staticmethod
    def is_tree(obj, role=None):
        """Returns True if obj has the tree role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.TREE

    @staticmethod
    def is_tree_or_tree_table(obj, role=None):
        """Returns True if obj has the tree or tree table role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role in [Atspi.Role.TREE, Atspi.Role.TREE_TABLE]

    @staticmethod
    def is_tree_related(obj, role=None):
        """Returns True if obj has a tree-related role"""

        roles = [Atspi.Role.TREE,
                 Atspi.Role.TREE_ITEM,
                 Atspi.Role.TREE_TABLE]
        if role is None:
            role = AXObject.get_role(obj)
        return role in roles

    @staticmethod
    def is_tree_item(obj, role=None):
        """Returns True if obj has the tree item role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.TREE_ITEM

    @staticmethod
    def is_tree_table(obj, role=None):
        """Returns True if obj has the tree table role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.TREE_TABLE

    @staticmethod
    def is_unknown(obj, role=None):
        """Returns True if obj has the unknown role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.UNKNOWN

    @staticmethod
    def is_unknown_or_redundant(obj, role=None):
        """Returns True if obj has the unknown or redundant object role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role in [Atspi.Role.UNKNOWN, Atspi.Role.REDUNDANT_OBJECT]

    @staticmethod
    def is_vertical_scrollbar(obj, role=None):
        """Returns True if obj is a vertical scrollbar"""

        return AXUtilitiesRole.is_scroll_bar(obj, role) \
            and AXObject.has_state(obj, Atspi.StateType.VERTICAL)

    @staticmethod
    def is_vertical_separator(obj, role=None):
        """Returns True if obj is a vertical separator"""

        return AXUtilitiesRole.is_separator(obj, role) \
            and AXObject.has_state(obj, Atspi.StateType.VERTICAL)

    @staticmethod
    def is_vertical_slider(obj, role=None):
        """Returns True if obj is a vertical slider"""

        return AXUtilitiesRole.is_slider(obj, role) \
            and AXObject.has_state(obj, Atspi.StateType.VERTICAL)

    @staticmethod
    def is_video(obj, role=None):
        """Returns True if obj has the video role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.VIDEO

    @staticmethod
    def is_viewport(obj, role=None):
        """Returns True if obj has the viewport role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.VIEWPORT

    @staticmethod
    def is_web_element(obj, exclude_pseudo_elements=True):
        """Returns True if obj is a web element"""

        tag = AXUtilitiesRole._get_tag(obj)
        if not tag:
            return False
        if not exclude_pseudo_elements:
            return True
        exclude = ["::before", "::after", "::marker"]
        return tag not in exclude

    @staticmethod
    def is_widget(obj, role=None):
        """Returns True if obj has a widget role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role in AXUtilitiesRole.get_widget_roles()

    @staticmethod
    def is_window(obj, role=None):
        """Returns True if obj has the window role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.WINDOW
