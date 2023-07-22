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

"""
Utilities for obtaining role-related information.
These utilities are app-type- and toolkit-agnostic. Utilities that might have
different implementations or results depending on the type of app (e.g. terminal,
chat, web) or toolkit (e.g. Qt, Gtk) should be in script_utilities.py file(s).

N.B. There are currently utilities that should never have custom implementations
that live in script_utilities.py files. These will be moved over time.
"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2023 Igalia, S.L."
__license__   = "LGPL"

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from .ax_object import AXObject

class AXUtilitiesRole:

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
        return role == Atspi.Role.BLOCK_QUOTE

    @staticmethod
    def is_button(obj, role=None):
        """Returns True if obj has the push- or toggle-button role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role in [Atspi.Role.PUSH_BUTTON, Atspi.Role.TOGGLE_BUTTON]

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
        return role == Atspi.Role.COMMENT

    @staticmethod
    def is_content_deletion(obj, role=None):
        """Returns True if obj has the content deletion role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.CONTENT_DELETION

    @staticmethod
    def is_content_insertion(obj, role=None):
        """Returns True if obj has the content insertion role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.CONTENT_INSERTION

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
        return role == Atspi.Role.DESCRIPTION_LIST

    @staticmethod
    def is_description_term(obj, role=None):
        """Returns True if obj has the description term role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.DESCRIPTION_TERM

    @staticmethod
    def is_description_value(obj, role=None):
        """Returns True if obj has the description value role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.DESCRIPTION_VALUE

    @staticmethod
    def is_desktop_frame(obj, role=None):
        """Returns True if obj has the desktop frame role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.DESKTOP_FRAME

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

        roles = [Atspi.Role.ALERT,
                 Atspi.Role.COLOR_CHOOSER,
                 Atspi.Role.DIALOG,
                 Atspi.Role.FILE_CHOOSER]
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
    def is_document(obj, role=None):
        """Returns True if obj has any document-related role"""

        roles = [Atspi.Role.DOCUMENT_EMAIL,
                 Atspi.Role.DOCUMENT_FRAME,
                 Atspi.Role.DOCUMENT_PRESENTATION,
                 Atspi.Role.DOCUMENT_SPREADSHEET,
                 Atspi.Role.DOCUMENT_TEXT,
                 Atspi.Role.DOCUMENT_WEB]
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
        return role == Atspi.Role.INTERNAL_FRAME

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
        return role == Atspi.Role.MARK

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
    def is_math_fraction(obj, role=None):
        """Returns True if obj has the math fraction role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.MATH_FRACTION

    @staticmethod
    def is_math_root(obj, role=None):
        """Returns True if obj has the math root role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.MATH_ROOT

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

        roles = [Atspi.Role.MENU_ITEM,
                 Atspi.Role.CHECK_MENU_ITEM,
                 Atspi.Role.RADIO_MENU_ITEM,
                 Atspi.Role.TEAROFF_MENU_ITEM]
        if role is None:
            role = AXObject.get_role(obj)
        return role in roles

    @staticmethod
    def is_menu_related(obj, role=None):
        """Returns True if obj has any menu-related role"""

        roles = [Atspi.Role.MENU,
                 Atspi.Role.MENU_BAR,
                 Atspi.Role.POPUP_MENU,
                 Atspi.Role.MENU_ITEM,
                 Atspi.Role.CHECK_MENU_ITEM,
                 Atspi.Role.RADIO_MENU_ITEM,
                 Atspi.Role.TEAROFF_MENU_ITEM]
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
    def is_redundant_object(obj, role=None):
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
    def is_single_line_entry(obj, role=None):
        """Returns True if obj has the entry role and multiline state"""

        return AXUtilitiesRole.is_entry(obj, role) \
            and AXObject.has_state(obj, Atspi.StateType.SINGLE_LINE)

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
        return role == Atspi.Role.SUGGESTION

    @staticmethod
    def is_superscript(obj, role=None):
        """Returns True if obj has the superscript role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.SUPERSCRIPT

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

        roles = [Atspi.Role.TABLE_CELL,
                 Atspi.Role.TABLE_COLUMN_HEADER,
                 Atspi.Role.TABLE_ROW_HEADER,
                 Atspi.Role.COLUMN_HEADER,
                 Atspi.Role.ROW_HEADER]
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

        roles = [Atspi.Role.TABLE_COLUMN_HEADER,
                 Atspi.Role.TABLE_ROW_HEADER,
                 Atspi.Role.COLUMN_HEADER,
                 Atspi.Role.ROW_HEADER]
        if role is None:
            role = AXObject.get_role(obj)
        return role in roles

    @staticmethod
    def is_table_related(obj, role=None):
        roles = [Atspi.Role.TABLE,
                 Atspi.Role.TABLE_CELL,
                 Atspi.Role.TABLE_COLUMN_HEADER,
                 Atspi.Role.TABLE_ROW_HEADER,
                 Atspi.Role.COLUMN_HEADER,
                 Atspi.Role.ROW_HEADER]
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
    def is_window(obj, role=None):
        """Returns True if obj has the window role"""

        if role is None:
            role = AXObject.get_role(obj)
        return role == Atspi.Role.WINDOW
