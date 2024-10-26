# Orca
#
# Copyright 2009 Sun Microsystems Inc.
# Copyright 2015-2016 Igalia, S.L.
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
# pylint: disable=too-many-return-statements
# pylint: disable=broad-exception-caught
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements

"""Superclass of classes used to generate presentations for objects."""

__id__        = "$Id:$"
__version__   = "$Revision:$"
__date__      = "$Date:$"
__copyright__ = "Copyright (c) 2009 Sun Microsystems Inc." \
                "Copyright (c) 2015-2016 Igalia, S.L."
__license__   = "LGPL"

import time
import threading

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from . import braille
from . import debug
from . import focus_manager
from . import object_properties
from . import settings
from . import settings_manager
from .ax_hypertext import AXHypertext
from .ax_object import AXObject
from .ax_table import AXTable
from .ax_text import AXText
from .ax_utilities import AXUtilities
from .ax_value import AXValue

class Generator:
    """Superclass of classes used to generate presentations for objects."""

    CACHED_DESCRIPTION: dict = {}
    CACHED_IMAGE_DESCRIPTION: dict = {}
    CACHED_IS_NAMELESS_TOGGLE: dict = {}
    CACHED_NESTING_LEVEL: dict = {}
    CACHED_STATIC_TEXT: dict = {}
    CACHED_TEXT_SUBSTRING: dict = {}
    CACHED_TEXT_LINE: dict = {}
    CACHED_TEXT: dict = {}
    CACHED_TEXT_EXPANDING_EOCS: dict = {}
    CACHED_TREE_ITEM_LEVEL: dict = {}
    USED_DESCRIPTION_FOR_NAME: dict = {}
    USED_DESCRIPTION_FOR_STATIC_TEXT: dict = {}

    _lock = threading.Lock()

    def __init__(self, script, mode):
        self._mode = mode
        self._script = script
        self._active_progress_bars = {}
        self._generators = {
            Atspi.Role.ALERT: self._generate_alert,
            Atspi.Role.ANIMATION: self._generate_animation,
            Atspi.Role.ARTICLE: self._generate_article,
            "ROLE_ARTICLE_IN_FEED": self._generate_article_in_feed,
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
            "ROLE_CONTENT_ERROR": self._generate_content_error,
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
            "ROLE_DPUB_LANDMARK": self._generate_dpub_landmark,
            "ROLE_DPUB_SECTION": self._generate_dpub_section,
            Atspi.Role.EDITBAR: self._generate_editbar,
            Atspi.Role.EMBEDDED: self._generate_embedded,
            Atspi.Role.ENTRY: self._generate_entry,
            "ROLE_FEED": self._generate_feed,
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
            "ROLE_MATH_ENCLOSED": self._generate_math_enclosed,
            "ROLE_MATH_FENCED": self._generate_math_fenced,
            Atspi.Role.MATH_FRACTION: self._generate_math_fraction,
            Atspi.Role.MATH_ROOT: self._generate_math_root,
            "ROLE_MATH_MULTISCRIPT": self._generate_math_multiscript,
            "ROLE_MATH_SCRIPT_SUBSUPER": self._generate_math_script_subsuper,
            "ROLE_MATH_SCRIPT_UNDEROVER": self._generate_math_script_underover,
            "ROLE_MATH_TABLE": self._generate_math_table,
            "ROLE_MATH_TABLE_ROW": self._generate_math_row,
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
            "ROLE_REGION": self._generate_region,
            Atspi.Role.ROOT_PANE: self._generate_root_pane,
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
            "ROLE_SWITCH": self._generate_switch,
            Atspi.Role.TABLE: self._generate_table,
            Atspi.Role.TABLE_CELL: self._generate_table_cell_in_row,
            "REAL_ROLE_TABLE_CELL": self._generate_table_cell,
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

    @staticmethod
    def log_generator_output(func):
        """Decorator for logging."""

        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            tokens = [f"GENERATOR: {func.__name__}:", result]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return result
        return wrapper

    @staticmethod
    def _clear_stored_data():
        """Clears any data we have cached for objects"""

        while True:
            time.sleep(2)
            msg = "GENERATOR: Clearing cache."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            with Generator._lock:
                Generator.CACHED_DESCRIPTION = {}
                Generator.CACHED_IMAGE_DESCRIPTION = {}
                Generator.CACHED_IS_NAMELESS_TOGGLE = {}
                Generator.CACHED_NESTING_LEVEL = {}
                Generator.CACHED_STATIC_TEXT = {}
                Generator.CACHED_TEXT_SUBSTRING = {}
                Generator.CACHED_TEXT_LINE = {}
                Generator.CACHED_TEXT = {}
                Generator.CACHED_TEXT_EXPANDING_EOCS = {}
                Generator.CACHED_TREE_ITEM_LEVEL = {}
                Generator.USED_DESCRIPTION_FOR_NAME = {}
                Generator.USED_DESCRIPTION_FOR_STATIC_TEXT = {}

    @staticmethod
    def start_cache_clearing_thread():
        """Starts thread to periodically clear cached details."""

        thread = threading.Thread(target=Generator._clear_stored_data)
        thread.daemon = True
        thread.start()

    def generate_contents(self, _contents, **_args):
        """Returns presentation for a list of [obj, start, end, string]."""

        return []

    def generate_context(self, _obj, **_args):
        """Returns the presentation of the context of the object. Subclasses must override this."""

        return []

    def generate(self, obj, **args):
        """Returns the presentation of the object."""

        _generator = self._generators.get(args.get("role") or AXObject.get_role(obj))
        if _generator is None:
            tokens = [f"{self._mode.upper()} GENERATOR:", obj, "lacks dedicated generator"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            _generator = self._generate_default_presentation

        if not args.get("formatType", None):
            if args.get('alreadyFocused', False):
                args["formatType"] = "focused"
            else:
                args["formatType"] = "unfocused"

        tokens = [f"{self._mode.upper()} GENERATOR:", _generator, "for", obj, "args:", args]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        result = _generator(obj, **args)
        tokens = [f"{self._mode.upper()} GENERATOR: Results:", result]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        if args.get("isProgressBarUpdate") and result and result[0]:
            self._set_progress_bar_update_time_and_value(obj)

        return result

    def get_localized_role_name(self, obj, **args):
        """Returns a string representing the localized rolename of obj."""

        result = AXUtilities.get_localized_role_name(obj, args.get("role"))
        return result

    def get_state_indicator(self, obj, **args):
        """Returns an array with the generated state of obj."""

        role = args.get("role", AXObject.get_role(obj))
        if AXUtilities.is_menu_item(obj, role):
            return self._generate_state_checked_if_checkable(obj, **args)
        if AXUtilities.is_radio_button(obj, role):
            return self._generate_state_selected_for_radio_button(obj, **args)
        if AXUtilities.is_radio_menu_item(obj, role):
            return self._generate_state_selected_for_radio_button(obj, **args)
        if AXUtilities.is_check_box(obj, role):
            return self._generate_state_checked(obj, **args)
        if AXUtilities.is_check_menu_item(obj, **args):
            return self._generate_state_checked(obj, **args)
        if AXUtilities.is_switch(obj, role):
            return self._generate_state_checked_for_switch(obj, **args)
        if AXUtilities.is_toggle_button(obj, role):
            return self._generate_state_pressed(obj, **args)
        if AXUtilities.is_table_cell(obj, role):
            return self._generate_state_checked_for_cell(obj, **args)
        return []

    def get_value(self, obj, **args):
        """Returns an array with the generated value."""

        role = args.get("role", AXObject.get_role(obj))
        if AXUtilities.is_progress_bar(obj, role):
            return self._generate_progress_bar_value(obj, **args)

        if AXUtilities.is_scroll_bar(obj, role) or AXUtilities.is_slider(obj, role):
            return self._generate_value_as_percentage(obj, **args)

        return []

    def _generate_result_separator(self, _obj, **_args):
        return []

    ################################# BASIC DETAILS #################################

    @log_generator_output
    def _generate_accessible_description(self, obj, **args):
        if args.get("omitDescription"):
            return []

        if hash(obj) in Generator.CACHED_DESCRIPTION:
            return Generator.CACHED_DESCRIPTION.get(hash(obj))

        if Generator.USED_DESCRIPTION_FOR_STATIC_TEXT.get(hash(obj)):
            Generator.CACHED_DESCRIPTION[hash(obj)] = []
            return []

        if Generator.USED_DESCRIPTION_FOR_NAME.get(hash(obj)):
            Generator.CACHED_DESCRIPTION[hash(obj)] = []
            return []

        description = AXObject.get_description(obj) \
            or self._script.utilities.displayedDescription(obj) or ""
        if not description:
            Generator.CACHED_DESCRIPTION[hash(obj)] = []
            return []

        if self._script.utilities.stringsAreRedundant(AXObject.get_name(obj), description):
            Generator.CACHED_DESCRIPTION[hash(obj)] = []
            return []

        focus = focus_manager.get_manager().get_locus_of_focus()
        if focus and obj != focus \
           and description in [AXObject.get_name(focus), AXObject.get_description(focus)]:
            Generator.CACHED_DESCRIPTION[hash(obj)] = []
            return []

        Generator.CACHED_DESCRIPTION[hash(obj)] = [description]
        return [description]

    @log_generator_output
    def _generate_accessible_image_description(self, obj, **_args):
        if hash(obj) in Generator.CACHED_IMAGE_DESCRIPTION:
            return Generator.CACHED_IMAGE_DESCRIPTION.get(hash(obj))

        description = AXObject.get_image_description(obj)
        if not description:
            Generator.CACHED_IMAGE_DESCRIPTION[hash(obj)] = []
            return []

        Generator.CACHED_IMAGE_DESCRIPTION[hash(obj)] = [description]
        return [description]

    @log_generator_output
    def _generate_accessible_label(self, obj, **_args):
        result = []
        label = self._script.utilities.displayedLabel(obj)
        if label:
            result.append(label)
        return result

    @log_generator_output
    def _generate_accessible_label_and_name(self, obj, **args):
        focus = focus_manager.get_manager().get_locus_of_focus()
        # TODO - JD: The role check is a quick workaround for issue #535 in which we stopped
        # presenting Qt table cells because Qt keeps giving us a different object each and
        # every time we ask for the cell. File a bug against Qt to get them to stop that.
        if focus and obj != focus and AXObject.get_role(obj) != AXObject.get_role(focus):
            name = AXObject.get_name(obj) or AXObject.get_description(obj)
            if name and name in [AXObject.get_name(focus), AXObject.get_description(focus)]:
                return []

        result = []
        label = self._generate_accessible_label(obj, **args)
        name = self._generate_accessible_name(obj, **args)
        role = args.get("role", AXObject.get_role(obj))
        if not (label or name) and role == Atspi.Role.TABLE_CELL:
            descendant = self._script.utilities.realActiveDescendant(obj)
            name = self._generate_accessible_name(descendant)

        # If we don't have a label, always use the name.
        if not label:
            return name

        result.extend(label)
        if not name:
            return result

        if self._script.utilities.stringsAreRedundant(name[0], label[0]):
            if len(name[0]) < len(label[0]):
                return label
            return name

        result.extend(name)
        if result:
            return result

        parent = AXObject.get_parent(obj)
        if AXUtilities.is_autocomplete(parent):
            result = self._generate_accessible_label_and_name(parent, **args)

        return result

    @log_generator_output
    def _generate_accessible_name(self, obj, **args):
        Generator.USED_DESCRIPTION_FOR_NAME[hash(obj)] = False
        name = AXObject.get_name(obj)
        if name:
            return [name]

        description = AXObject.get_description(obj)
        if description:
            Generator.USED_DESCRIPTION_FOR_NAME[hash(obj)] = True
            return [description]

        link = None
        parent = AXObject.get_parent(obj)
        if AXUtilities.is_link(obj, args.get("role")):
            link = obj
        elif AXUtilities.is_link(parent):
            link = parent
        if link:
            basename = AXHypertext.get_link_basename(link, remove_extension=True)
            if basename:
                return [basename]

        # To make the unlabeled icons in gnome-panel more accessible.
        if AXUtilities.is_icon(obj) and AXUtilities.is_panel(parent):
            return self._generate_accessible_name(parent)

        return []

    @log_generator_output
    def _generate_accessible_placeholder_text(self, obj, **_args):
        attrs = AXObject.get_attributes_dict(obj)
        placeholder = attrs.get("placeholder-text")
        if placeholder and placeholder != AXObject.get_name(obj):
            return [placeholder]

        placeholder = attrs.get("placeholder")
        if placeholder and placeholder != AXObject.get_name(obj):
            return [placeholder]

        return []

    @log_generator_output
    def _generate_accessible_role(self, _obj, **_args):
        return []

    @log_generator_output
    def _generate_accessible_static_text(self, obj, **args):
        if hash(obj) in Generator.CACHED_STATIC_TEXT:
            return Generator.CACHED_STATIC_TEXT.get(hash(obj))

        result = self._generate_accessible_description(obj, **args)
        Generator.USED_DESCRIPTION_FOR_STATIC_TEXT[hash(obj)] = bool(result)
        if result:
            Generator.CACHED_STATIC_TEXT[hash(obj)] = result
            return result

        if args.get("formatType") != "ancestor":
            result = self._generate_text_expanding_embedded_objects(obj, **args)
            if result:
                Generator.CACHED_STATIC_TEXT[hash(obj)] = result
                return result

        labels = self._script.utilities.unrelatedLabels(obj)
        for label in labels:
            result.extend(self._generate_accessible_name(label, **args))

        Generator.CACHED_STATIC_TEXT[hash(obj)] = result
        return result

    @log_generator_output
    def _get_functional_role(self, obj, **args):
        role = args.get("role", AXObject.get_role(obj))
        if AXUtilities.is_math_related(obj):
            if AXUtilities.is_math_sub_or_super_script(obj):
                return "ROLE_MATH_SCRIPT_SUBSUPER"
            if AXUtilities.is_math_under_or_over_script(obj):
                return "ROLE_MATH_SCRIPT_UNDEROVER"
            if AXUtilities.is_math_multi_script(obj):
                return "ROLE_MATH_MULTISCRIPT"
            if AXUtilities.is_math_enclose(obj):
                return "ROLE_MATH_ENCLOSED"
            if AXUtilities.is_math_fenced(obj):
                return "ROLE_MATH_FENCED"
            if AXUtilities.is_math_table(obj):
                return "ROLE_MATH_TABLE"
            if AXUtilities.is_math_table_row(obj):
                return "ROLE_MATH_TABLE_ROW"
        if AXUtilities.is_dpub(obj, role):
            if AXUtilities.is_landmark(obj):
                return "ROLE_DPUB_LANDMARK"
            if AXUtilities.is_section(obj, role):
                return "ROLE_DPUB_SECTION"
        if AXUtilities.is_switch(obj, role):
            return "ROLE_SWITCH"
        if self._script.utilities.isAnchor(obj):
            return Atspi.Role.STATIC
        if AXUtilities.is_block_quote(obj, role):
            return Atspi.Role.BLOCK_QUOTE
        if AXUtilities.is_comment(obj, role):
            return Atspi.Role.COMMENT
        if self._script.utilities.isContentError(obj):
            return "ROLE_CONTENT_ERROR"
        if AXUtilities.is_description_list(obj, role):
            return Atspi.Role.DESCRIPTION_LIST
        if AXUtilities.is_description_term(obj, role):
            return Atspi.Role.DESCRIPTION_TERM
        if AXUtilities.is_description_value(obj, role):
            return Atspi.Role.DESCRIPTION_VALUE
        if AXUtilities.is_feed_article(obj, role):
            return "ROLE_ARTICLE_IN_FEED"
        if AXUtilities.is_feed(obj, role):
            return "ROLE_FEED"
        if AXUtilities.is_landmark(obj, role):
            if AXUtilities.is_landmark_region(obj):
                return "ROLE_REGION"
            return Atspi.Role.LANDMARK
        if self._script.utilities.isFocusableLabel(obj):
            return Atspi.Role.LIST_ITEM
        if self._script.utilities.isDocument(obj) and AXObject.supports_image(obj):
            return Atspi.Role.IMAGE

        return role

    @log_generator_output
    def _generate_descendants(self, obj, **args):
        result = []
        obj_name = AXObject.get_name(obj) or self._script.utilities.displayedLabel(obj)
        obj_desc = AXObject.get_description(obj) or self._script.utilities.displayedDescription(obj)
        descendants = self._script.utilities.getOnScreenObjects(obj)
        used_description_as_static_text = False
        for child in descendants:
            if child == obj:
                continue
            if AXUtilities.is_section(child):
                continue
            if AXUtilities.is_paragraph(child):
                continue
            if AXUtilities.is_table_related(child):
                continue
            if AXUtilities.is_static(child):
                continue
            if AXUtilities.is_link(child):
                continue
            if AXUtilities.is_image(child):
                continue
            if AXUtilities.is_separator(child):
                continue

            child_name = AXObject.get_name(child)
            if AXUtilities.is_button(child) and child_name in obj_name:
                continue

            if AXUtilities.is_label(child):
                if not AXText.has_presentable_text(child):
                    continue
                if self._script.utilities.stringsAreRedundant(obj_name, child_name):
                    continue
                if self._script.utilities.stringsAreRedundant(obj_desc, child_name):
                    used_description_as_static_text = True

            child_result = self.generate(child, includeContext=False, omitDescription=True)
            if child_result:
                result.extend(child_result)
                result.extend(self._generate_result_separator(child, **args))

        Generator.USED_DESCRIPTION_FOR_STATIC_TEXT[hash(obj)] = used_description_as_static_text
        return result

    @log_generator_output
    def _generate_focused_item(self, obj, **args):
        role = args.get("role")
        if not (AXUtilities.is_list(obj, role) or AXUtilities.is_list_box(obj, role)):
            return []

        if AXObject.supports_selection(obj):
            items = self._script.utilities.selectedChildren(obj)
        else:
            items = [AXUtilities.get_focused_object(obj)]
        if not (items and items[0]):
            return []

        result = []
        for item in map(self._generate_accessible_name, items):
            result.extend(item)

        return result

    @log_generator_output
    def _generate_radio_button_group(self, obj, **_args):
        if not AXUtilities.is_radio_button(obj):
            return []

        radio_group_label = None
        labels = AXUtilities.get_is_labelled_by(obj, False)
        if labels:
            radio_group_label = labels[0]
        if radio_group_label:
            return [AXObject.get_name(radio_group_label)]

        parent = AXObject.get_parent_checked(obj)
        while parent:
            if AXUtilities.is_panel(parent) or AXUtilities.is_filler(parent):
                label = self._generate_accessible_label_and_name(parent)
                if label:
                    return label
            parent = AXObject.get_parent_checked(parent)
        return []

    ##################################### STATE #####################################

    @log_generator_output
    def _generate_state_checked(self, obj, **_args):
        if self._mode == "braille":
            indicators = object_properties.CHECK_BOX_INDICATORS_BRAILLE
        elif self._mode == "speech":
            indicators = object_properties.CHECK_BOX_INDICATORS_SPEECH
        elif self._mode == "sound":
            indicators = object_properties.CHECK_BOX_INDICATORS_SOUND
        else:
            return []

        if AXUtilities.is_checked(obj):
            return [indicators[1]]
        if AXUtilities.is_indeterminate(obj):
            return [indicators[2]]
        return [indicators[0]]

    @log_generator_output
    def _generate_state_checked_for_cell(self, obj, **args):
        result = []
        if self._script.utilities.hasMeaningfulToggleAction(obj):
            args["role"] = Atspi.Role.CHECK_BOX
            result.extend(self.generate(obj, **args))

        return result

    @log_generator_output
    def _generate_state_checked_for_switch(self, obj, **_args):
        if self._mode == "braille":
            indicators = object_properties.SWITCH_INDICATORS_BRAILLE
        elif self._mode == "speech":
            indicators = object_properties.SWITCH_INDICATORS_SPEECH
        elif self._mode == "sound":
            indicators = object_properties.SWITCH_INDICATORS_SOUND
        else:
            return []

        if AXUtilities.is_checked(obj) or AXUtilities.is_pressed(obj):
            return [indicators[1]]
        return [indicators[0]]

    @log_generator_output
    def _generate_state_checked_if_checkable(self, obj, **args):
        if AXUtilities.is_checkable(obj) or AXUtilities.is_check_menu_item(obj):
            return self._generate_state_checked(obj, **args)

        if AXUtilities.is_checked(obj):
            return self._generate_state_checked(obj, **args)

        return []

    @log_generator_output
    def _generate_state_expanded(self, obj, **_args):
        if self._mode == "braille":
            indicators = object_properties.EXPANSION_INDICATORS_BRAILLE
        elif self._mode == "speech":
            indicators = object_properties.EXPANSION_INDICATORS_SPEECH
        elif self._mode == "sound":
            indicators = object_properties.EXPANSION_INDICATORS_SOUND
        else:
            return []

        if AXUtilities.is_collapsed(obj):
            return [indicators[0]]
        if AXUtilities.is_expanded(obj):
            return [indicators[1]]
        if AXUtilities.is_expandable(obj):
            return [indicators[0]]
        return []

    @log_generator_output
    def _generate_state_has_popup(self, _obj, **_args):
        return []

    @log_generator_output
    def _generate_state_invalid(self, obj, **_args):
        error = self._script.utilities.getError(obj)
        if not error:
            return []

        if self._mode == "braille":
            indicators = object_properties.INVALID_INDICATORS_BRAILLE
        elif self._mode == "speech":
            indicators = object_properties.INVALID_INDICATORS_SPEECH
        elif self._mode == "sound":
            indicators = object_properties.INVALID_INDICATORS_SOUND
        else:
            return []

        result = []
        if error == 'spelling':
            indicator = indicators[1]
        elif error == 'grammar':
            indicator = indicators[2]
        else:
            indicator = indicators[0]

        error_message = self._script.utilities.getErrorMessage(obj)
        if error_message:
            result.append(f"{indicator}: {error_message}")
        else:
            result.append(indicator)

        return result

    @log_generator_output
    def _generate_state_multiselectable(self, obj, **_args):
        if not (AXUtilities.is_multiselectable(obj) and AXObject.get_child_count(obj)):
            return []

        # TODO - JD: There is no braille property and the braille generation
        # doesn't generate this state. Shouldn't it be presented in braille?

        if self._mode == "speech":
            return [object_properties.STATE_MULTISELECT_SPEECH]
        if self._mode == "sound":
            return [object_properties.STATE_MULTISELECT_SOUND]
        return []

    @log_generator_output
    def _generate_state_pressed(self, obj, **_args):
        if self._mode == "braille":
            indicators = object_properties.TOGGLE_BUTTON_INDICATORS_BRAILLE
        elif self._mode == "speech":
            indicators = object_properties.TOGGLE_BUTTON_INDICATORS_SPEECH
        elif self._mode == "sound":
            indicators = object_properties.TOGGLE_BUTTON_INDICATORS_SOUND
        else:
            return []

        if AXUtilities.is_checked(obj) or AXUtilities.is_pressed(obj):
            return [indicators[1]]
        return [indicators[0]]

    @log_generator_output
    def _generate_state_read_only(self, obj, **_args):
        if not (AXUtilities.is_read_only(obj) or self._script.utilities.isReadOnlyTextArea(obj)):
            return []

        if self._mode == "braille":
            return [object_properties.STATE_READ_ONLY_BRAILLE]
        if self._mode == "speech":
            return [object_properties.STATE_READ_ONLY_SPEECH]
        if self._mode == "sound":
            return [object_properties.STATE_READ_ONLY_SOUND]

        return []

    @log_generator_output
    def _generate_state_required(self, obj, **_args):
        is_required = AXUtilities.is_required(obj)
        if not is_required and AXUtilities.is_radio_button(obj):
            is_required = AXUtilities.is_required(AXObject.get_parent(obj))
        if not is_required:
            return []

        if self._mode == "braille":
            return [object_properties.STATE_REQUIRED_BRAILLE]
        if self._mode == "speech":
            return [object_properties.STATE_REQUIRED_SPEECH]
        if self._mode == "sound":
            return [object_properties.STATE_REQUIRED_SOUND]

        return []

    @log_generator_output
    def _generate_state_selected_for_radio_button(self, obj, **_args):
        if self._mode == "braille":
            indicators = object_properties.RADIO_BUTTON_INDICATORS_BRAILLE
        elif self._mode == "speech":
            indicators = object_properties.RADIO_BUTTON_INDICATORS_SPEECH
        elif self._mode == "sound":
            indicators = object_properties.RADIO_BUTTON_INDICATORS_SOUND
        else:
            return []

        if AXUtilities.is_checked(obj):
            return [indicators[1]]
        return [indicators[0]]

    @log_generator_output
    def _generate_state_sensitive(self, obj, **_args):
        if AXUtilities.is_sensitive(obj):
            return []

        if self._script.utilities.isSpreadSheetCell(obj):
            return []

        if self._mode == "braille":
            return [object_properties.STATE_INSENSITIVE_BRAILLE]
        if self._mode == "speech":
            return [object_properties.STATE_INSENSITIVE_SPEECH]
        if self._mode == "sound":
            return [object_properties.STATE_INSENSITIVE_SOUND]

        return []

    @log_generator_output
    def _generate_state_unselected(self, _obj, **_args):
        return []

    @log_generator_output
    def _generate_state_visited(self, _obj, **_args):
        # Note that in the case of speech, this state is added to the role name.
        return []

    ##################################### TEXT ######################################

    @log_generator_output
    def _generate_text_substring(self, obj, **args):
        start = args.get("startOffset")
        end = args.get("endOffset")
        if (hash(obj), start, end) in Generator.CACHED_TEXT_SUBSTRING:
            return Generator.CACHED_TEXT_SUBSTRING.get((hash(obj), start, end))

        if start is None or end is None:
            if not AXUtilities.is_editable(obj):
                Generator.CACHED_TEXT_SUBSTRING[(hash(obj), start, end)] = []
            return []

        substring = args.get("string", AXText.get_substring(obj, start, end))
        if self._script.EMBEDDED_OBJECT_CHARACTER not in substring:
            if not AXUtilities.is_editable(obj):
                Generator.CACHED_TEXT_SUBSTRING[(hash(obj), start, end)] = [substring]
            return [substring]

        if not AXUtilities.is_editable(obj):
            Generator.CACHED_TEXT_SUBSTRING[(hash(obj), start, end)] = []
        return []

    @log_generator_output
    def _generate_text_line(self, obj, **args):
        start = args.get("startOffset")
        end = args.get("endOffset")
        if (hash(obj), start, end) in Generator.CACHED_TEXT_LINE:
            return Generator.CACHED_TEXT_LINE.get((hash(obj), start, end))

        result = Generator._generate_text_substring(self, obj, **args)
        if result:
            if not AXUtilities.is_editable(obj):
                Generator.CACHED_TEXT_LINE[(hash(obj), start, end)] = result
            return result

        text = AXText.get_line_at_offset(obj)[0]
        if text and self._script.EMBEDDED_OBJECT_CHARACTER not in text:
            if not AXUtilities.is_editable(obj):
                Generator.CACHED_TEXT_LINE[(hash(obj), start, end)] = [text]
            return [text]

        if not AXUtilities.is_editable(obj):
            Generator.CACHED_TEXT_LINE[(hash(obj), start, end)] = []
        return []

    @log_generator_output
    def _generate_text_content(self, obj, **args):
        if hash(obj) in Generator.CACHED_TEXT:
            return Generator.CACHED_TEXT.get(hash(obj))

        result = Generator._generate_text_substring(self, obj, **args)
        if result:
            if not AXUtilities.is_editable(obj):
                Generator.CACHED_TEXT[hash(obj)] = result
            return result

        text = AXText.get_all_text(obj)
        if text and self._script.EMBEDDED_OBJECT_CHARACTER not in text:
            if not AXUtilities.is_editable(obj):
                Generator.CACHED_TEXT[hash(obj)] = [text]
            return [text]

        if not AXUtilities.is_editable(obj):
            Generator.CACHED_TEXT[hash(obj)] = []
        return []

    @log_generator_output
    def _generate_text_expanding_embedded_objects(self, obj, **args):
        start = args.get("startOffset")
        end = args.get("endOffset")
        if (hash(obj), start, end) in Generator.CACHED_TEXT_EXPANDING_EOCS:
            return Generator.CACHED_TEXT_EXPANDING_EOCS.get((hash(obj), start, end))

        text = self._script.utilities.expandEOCs(
            obj, args.get("startOffset", 0), args.get("endOffset", -1))
        if text.strip() and self._script.EMBEDDED_OBJECT_CHARACTER not in text \
           and not self._script.utilities.stringsAreRedundant(AXObject.get_name(obj), text):
            if not AXUtilities.is_editable(obj):
                Generator.CACHED_TEXT_EXPANDING_EOCS[hash(obj), start, end] = [text]
            return [text]

        if not AXUtilities.is_editable(obj):
            Generator.CACHED_TEXT_EXPANDING_EOCS[(hash(obj), start, end)] = []
        return []

    ################################## POSITION #####################################

    @log_generator_output
    def _get_nesting_level(self, obj):
        level = Generator.CACHED_NESTING_LEVEL.get(hash(obj))
        if level is None:
            level = self._script.utilities.nestingLevel(obj)
            Generator.CACHED_NESTING_LEVEL[hash(obj)] = level
        return level

    @log_generator_output
    def _generate_nesting_level(self, obj, **args):
        if args.get("startOffset") is not None and args.get("endOffset") is not None:
            return []

        level = self._get_nesting_level(obj)
        if not level:
            return []

        if self._mode == "braille":
            return [object_properties.NESTING_LEVEL_BRAILLE % (level)]
        if self._mode == "speech":
            return [object_properties.NESTING_LEVEL_SPEECH % (level)]
        return []

    @log_generator_output
    def _generate_position_in_list(self, _obj, **_args):
        return []

    @log_generator_output
    def _generate_tree_item_level(self, obj, **args):
        level = Generator.CACHED_TREE_ITEM_LEVEL.get(hash(obj))
        if level is None:
            level = self._script.utilities.nodeLevel(obj)
            Generator.CACHED_TREE_ITEM_LEVEL[hash(obj)] = level

        if level < 0:
            return []

        prior_object = args.get("priorObj")
        if args.get("newOnly") and prior_object:
            old_level = Generator.CACHED_TREE_ITEM_LEVEL.get(hash(prior_object))
            if old_level is None:
                old_level = self._script.utilities.nodeLevel(prior_object)
                Generator.CACHED_TREE_ITEM_LEVEL[hash(prior_object)] = old_level
            if old_level == level:
                return []

        if self._mode == "braille":
            return [object_properties.NODE_LEVEL_BRAILLE % (level + 1)]
        if self._mode == "speech":
            return [object_properties.NODE_LEVEL_SPEECH % (level + 1)]
        return []

    ################################ PROGRESS BARS ##################################

    @log_generator_output
    def _generate_progress_bar_index(self, _obj, **_args):
        return []

    @log_generator_output
    def _generate_progress_bar_value(self, _obj, **_args):
        return []

    def _get_progress_bar_update_interval(self):
        return int(settings_manager.get_manager().get_setting('progressBarUpdateInterval'))

    def _should_present_progress_bar_update(self, obj, **_args):
        percent = AXValue.get_value_as_percent(obj)
        last_time, last_value = self._get_progress_bar_update_time_and_value(obj, type=self)
        if percent == last_value:
            tokens = ["GENERATOR: Not presenting update for", obj, ". Value still", percent]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return False

        if percent == 100:
            return True

        interval = int(time.time() - last_time)
        return interval >= self._get_progress_bar_update_interval()

    def _clean_up_cached_progress_bars(self):
        bars = list(filter(AXObject.is_valid, self._active_progress_bars))
        self._active_progress_bars = {x:self._active_progress_bars.get(x) for x in bars}

    def _get_most_recent_progress_bar_update(self):
        self._clean_up_cached_progress_bars()
        if not self._active_progress_bars.values():
            return None, 0.0, None

        sorted_values = sorted(self._active_progress_bars.values(), key=lambda x: x[0])
        prev_time, prev_value = sorted_values[-1]
        return list(self._active_progress_bars.keys())[-1], prev_time, prev_value

    def _get_progress_bar_number_and_count(self, obj):
        self._clean_up_cached_progress_bars()
        if obj not in self._active_progress_bars:
            self._active_progress_bars[obj] = 0.0, None

        this_value = self._get_progress_bar_update_time_and_value(obj)
        index = list(self._active_progress_bars.values()).index(this_value)
        return index + 1, len(self._active_progress_bars)

    def _get_progress_bar_update_time_and_value(self, obj, **_args):
        if obj not in self._active_progress_bars:
            self._active_progress_bars[obj] = 0.0, None

        return self._active_progress_bars.get(obj)

    def _set_progress_bar_update_time_and_value(self, obj, last_time=None, last_value=None):
        last_time = last_time or time.time()
        last_value = last_value or AXValue.get_value_as_percent(obj)
        self._active_progress_bars[obj] = last_time, last_value

    ##################################### TABLE #####################################

    # TODO - JD: This function and fake role really need to die....
    @log_generator_output
    def _generate_real_table_cell(self, obj, **args):
        result = []
        args["role"] = "REAL_ROLE_TABLE_CELL"
        result.extend(self.generate(obj, **args))
        return result

    def _get_is_nameless_toggle(self, obj):
        if hash(obj) in Generator.CACHED_IS_NAMELESS_TOGGLE:
            return Generator.CACHED_IS_NAMELESS_TOGGLE[hash(obj)]

        if not self._script.utilities.hasMeaningfulToggleAction(obj):
            Generator.CACHED_IS_NAMELESS_TOGGLE[hash(obj)] = False
            return False

        descendant = self._script.utilities.realActiveDescendant(obj)
        if AXObject.get_name(descendant) or AXText.get_all_text(descendant):
            Generator.CACHED_IS_NAMELESS_TOGGLE[hash(obj)] = False
            return False

        Generator.CACHED_IS_NAMELESS_TOGGLE[hash(obj)] = True
        return True

    # TODO - JD: This is part of the complicated "REAL_ROLE_TABLE_CELL" mess.
    @log_generator_output
    def _generate_table_cell_row(self, obj, **args):
        present_all = args.get("readingRow") is True \
            or args.get("formatType") == "detailedWhereAmI" \
            or self._script.utilities.shouldReadFullRow(obj, args.get("priorObj"))

        if not present_all:
            return self._generate_real_table_cell(obj, **args)

        args["readingRow"] = True
        result = []
        cells = self._script.utilities.getShowingCellsInSameRow(
            obj, forceFullRow=not self._script.utilities.isSpreadSheetCell(obj))

        row = AXObject.find_ancestor(obj, AXUtilities.is_table_row)
        if row and AXObject.get_name(row) and not self._script.utilities.isLayoutOnly(row):
            return self.generate(row)

        # Remove any pre-calculated values which only apply to obj and not row cells.
        do_not_include = ["startOffset", "endOffset", "string"]
        other_cell_args = args.copy()
        for arg in do_not_include:
            other_cell_args.pop(arg, None)

        for cell in cells:
            if cell == obj:
                cell_result = self._generate_real_table_cell(cell, **args)
            else:
                cell_result = self._generate_real_table_cell(cell, **other_cell_args)
            if cell_result and result and self._mode == "braille":
                result.append(braille.Region(object_properties.TABLE_CELL_DELIMITER_BRAILLE))
            result.extend(cell_result)

        result.extend(self._generate_position_in_list(obj, **args))
        return result


    # TODO - JD: If we had dedicated generators for cell types, we wouldn't need this.
    @log_generator_output
    def _generate_column_header_if_toggle_and_no_text(self, obj, **_args):
        if not self._get_is_nameless_toggle(obj):
            return []

        result = []
        headers = AXTable.get_column_headers(obj)
        if headers:
            result.append(AXObject.get_name(headers[0]) or AXText.get_all_text(headers[0]))

        return result

    # TODO - JD: This needs to also be looked into.
    @log_generator_output
    def _generate_real_active_descendant_displayed_text(self, obj, **args):
        rad = self._script.utilities.realActiveDescendant(obj)

        if not (AXUtilities.is_table_cell(rad) and AXObject.get_child_count(rad)):
            return self._generate_text_content(rad, **args)

        content = {AXObject.get_name(x) for x in AXObject.iter_children(rad)}
        rv = " ".join(filter(lambda x: x, content))
        if not rv:
            return self._generate_text_content(rad, **args)
        return [rv]

    @log_generator_output
    def _generate_table_cell_column_header(self, obj, **args):
        if args.get("readingRow") and not self._get_is_nameless_toggle(obj):
            return []

        result = []
        if args.get("newOnly"):
            headers = AXTable.get_new_column_headers(obj, args.get("priorObj"))
        else:
            headers = AXTable.get_column_headers(obj)

        tokens = []
        for header in headers:
            token = AXObject.get_name(header).strip() or AXText.get_all_text(header).strip()
            if token:
                tokens.append(token)

        if not tokens:
            return result

        text = ". ".join(tokens)
        if not self._get_is_nameless_toggle(obj):
            role_string = self.get_localized_role_name(obj, role=Atspi.Role.COLUMN_HEADER)
            if self._mode == "speech":
                if settings.speechVerbosityLevel == settings.VERBOSITY_LEVEL_VERBOSE \
                and args.get("formatType") not in ["basicWhereAmI", "detailedWhereAmI"]:
                    text = f"{text} {role_string}"
            elif self._mode == "braille":
                text = f"{text} {role_string}"

        result.append(text)
        return result

    @log_generator_output
    def _generate_table_cell_row_header(self, obj, **args):
        if args.get("readingRow"):
            return []

        result = []
        if args.get("newOnly"):
            headers = AXTable.get_new_row_headers(obj, args.get("priorObj"))
        else:
            headers = AXTable.get_row_headers(obj)

        tokens = []
        for header in headers:
            token = AXObject.get_name(header).strip() or AXText.get_all_text(header).strip()
            if token:
                tokens.append(token)

        if not tokens:
            return result

        text = ". ".join(tokens)
        role_string =  self.get_localized_role_name(obj, role=Atspi.Role.ROW_HEADER)
        if self._mode == "speech":
            if settings.speechVerbosityLevel == settings.VERBOSITY_LEVEL_VERBOSE \
               and args.get("formatType") not in ["basicWhereAmI", "detailedWhereAmI"]:
                text = f"{text} {role_string}"
        elif self._mode == "braille":
            text = f"{text} {role_string}"

        result.append(text)
        return result

    @log_generator_output
    def _generate_table_sort_order(self, obj, **_args):
        description = self._script.utilities.getSortOrderDescription(obj)
        if not description:
            return []

        return [description]

    ##################################### VALUE #####################################

    @log_generator_output
    def _generate_value(self, obj, **args):
        if AXUtilities.is_combo_box(obj, args.get("role")):
            value = self._script.utilities.getComboBoxValue(obj)
            return [value]

        if AXUtilities.is_separator(obj, args.get("role")) and not AXUtilities.is_focused(obj):
            return []

        result = AXValue.get_current_value_text(obj)
        if result:
            return [result]
        return []

    @log_generator_output
    def _generate_value_as_percentage(self, obj, **_args):
        percent = AXValue.get_value_as_percent(obj)
        if percent is not None:
            return [f'{percent}%']

        return []

    ################################### PER-ROLE ###################################

    def _generate_default_presentation(self, _obj, **_args):
        """Provides a default/role-agnostic presentation of obj."""

        return []

    def _generate_accelerator_label(self, _obj, **_args):
        """Generates presentation for the accelerator-label role."""

        return []

    def _generate_alert(self, _obj, **_args):
        """Generates presentation for the alert role."""

        return []

    def _generate_animation(self, _obj, **_args):
        """Generates presentation for the animation role."""

        return []

    def _generate_application(self, _obj, **_args):
        """Generates presentation for the application role."""

        return []

    def _generate_arrow(self, _obj, **_args):
        """Generates presentation for the arrow role."""

        return []

    def _generate_article(self, _obj, **_args):
        """Generates presentation for the article role."""

        return []

    def _generate_article_in_feed(self, _obj, **_args):
        """Generates presentation for the article role when the article is in a feed."""

        return []

    def _generate_audio(self, _obj, **_args):
        """Generates presentation for the audio role."""

        return []

    def _generate_autocomplete(self, _obj, **_args):
        """Generates presentation for the autocomplete role."""

        return []

    def _generate_block_quote(self, _obj, **_args):
        """Generates presentation for the block-quote role."""

        return []

    def _generate_calendar(self, _obj, **_args):
        """Generates presentation for the calendar role."""

        return []

    def _generate_canvas(self, _obj, **_args):
        """Generates presentation for the canvas role."""

        return []

    def _generate_caption(self, _obj, **_args):
        """Generates presentation for the caption role."""

        return []

    def _generate_chart(self, _obj, **_args):
        """Generates presentation for the chart role."""

        return []

    def _generate_check_box(self, _obj, **_args):
        """Generates presentation for the check-box role."""

        return []

    def _generate_check_menu_item(self, _obj, **_args):
        """Generates presentation for the check-menu-item role."""

        return []

    def _generate_color_chooser(self, _obj, **_args):
        """Generates presentation for the color-chooser role."""

        return []

    def _generate_column_header(self, _obj, **_args):
        """Generates presentation for the column-header role."""

        return []

    def _generate_combo_box(self, _obj, **_args):
        """Generates presentation for the combo-box role."""

        return []

    def _generate_comment(self, _obj, **_args):
        """Generates presentation for the comment role."""

        return []

    def _generate_content_deletion(self, _obj, **_args):
        """Generates presentation for the content-deletion role."""

        return []

    def _generate_content_error(self, _obj, **_args):
        """Generates presentation for a role with a content-related error."""

        return []

    def _generate_content_insertion(self, _obj, **_args):
        """Generates presentation for the content-insertion role."""

        return []

    def _generate_date_editor(self, _obj, **_args):
        """Generates presentation for the date-editor role."""

        return []

    def _generate_definition(self, _obj, **_args):
        """Generates presentation for the definition role."""

        return []

    def _generate_description_list(self, _obj, **_args):
        """Generates presentation for the description-list role."""

        return []

    def _generate_description_term(self, _obj, **_args):
        """Generates presentation for the description-term role."""

        return []

    def _generate_description_value(self, _obj, **_args):
        """Generates presentation for the description-value role."""

        return []

    def _generate_desktop_frame(self, _obj, **_args):
        """Generates presentation for the desktop-frame role."""

        return []

    def _generate_desktop_icon(self, _obj, **_args):
        """Generates presentation for the desktop-icon role."""

        return []

    def _generate_dial(self, _obj, **_args):
        """Generates presentation for the dial role."""

        return []

    def _generate_dialog(self, _obj, **_args):
        """Generates presentation for the dialog role."""

        return []

    def _generate_directory_pane(self, _obj, **_args):
        """Generates presentation for the directory_pane role."""

        return []

    def _generate_document(self, _obj, **_args):
        """Generates presentation for document-related roles."""

        return []

    def _generate_document_email(self, _obj, **_args):
        """Generates presentation for the document-email role."""

        return []

    def _generate_document_frame(self, _obj, **_args):
        """Generates presentation for the document-frame role."""

        return []

    def _generate_document_presentation(self, _obj, **_args):
        """Generates presentation for the document-presentation role."""

        return []

    def _generate_document_spreadsheet(self, _obj, **_args):
        """Generates presentation for the document-spreadsheet role."""

        return []

    def _generate_document_text(self, _obj, **_args):
        """Generates presentation for the document-text role."""

        return []

    def _generate_document_web(self, _obj, **_args):
        """Generates presentation for the document-web role."""

        return []

    def _generate_dpub_landmark(self, _obj, **_args):
        """Generates presentation for the dpub section role."""

        return []

    def _generate_dpub_section(self, _obj, **_args):
        """Generates presentation for the dpub section role."""

        return []

    def _generate_drawing_area(self, _obj, **_args):
        """Generates presentation for the drawing-area role."""

        return []

    def _generate_editbar(self, _obj, **_args):
        """Generates presentation for the editbar role."""

        return []

    def _generate_embedded(self, _obj, **_args):
        """Generates presentation for the embedded role."""

        return []

    def _generate_entry(self, _obj, **_args):
        """Generates presentation for the entry role."""

        return []

    def _generate_feed(self, _obj, **_args):
        """Generates presentation for the feed role."""

        return []

    def _generate_file_chooser(self, _obj, **_args):
        """Generates presentation for the file-chooser role."""

        return []

    def _generate_filler(self, _obj, **_args):
        """Generates presentation for the filler role."""

        return []

    def _generate_font_chooser(self, _obj, **_args):
        """Generates presentation for the font-chooser role."""

        return []

    def _generate_footer(self, _obj, **_args):
        """Generates presentation for the footer role."""

        return []

    def _generate_footnote(self, _obj, **_args):
        """Generates presentation for the footnote role."""

        return []

    def _generate_form(self, _obj, **_args):
        """Generates presentation for the form role."""

        return []

    def _generate_frame(self, _obj, **_args):
        """Generates presentation for the frame role."""

        return []

    def _generate_glass_pane(self, _obj, **_args):
        """Generates presentation for the glass-pane role."""

        return []

    def _generate_grouping(self, _obj, **_args):
        """Generates presentation for the grouping role."""

        return []

    def _generate_header(self, _obj, **_args):
        """Generates presentation for the header role."""

        return []

    def _generate_heading(self, _obj, **_args):
        """Generates presentation for the heading role."""

        return []

    def _generate_html_container(self, _obj, **_args):
        """Generates presentation for the html-container role."""

        return []

    def _generate_icon(self, _obj, **_args):
        """Generates presentation for the icon role."""

        return []

    def _generate_image(self, _obj, **_args):
        """Generates presentation for the image role."""

        return []

    def _generate_image_map(self, _obj, **_args):
        """Generates presentation for the image-map role."""

        return []

    def _generate_info_bar(self, _obj, **_args):
        """Generates presentation for the info-bar role."""

        return []

    def _generate_input_method_window(self, _obj, **_args):
        """Generates presentation for the input-method-window role."""

        return []

    def _generate_internal_frame(self, _obj, **_args):
        """Generates presentation for the internal-frame role."""

        return []

    def _generate_label(self, _obj, **_args):
        """Generates presentation for the label role."""

        return []

    def _generate_landmark(self, _obj, **_args):
        """Generates presentation for the landmark role."""

        return []

    def _generate_layered_pane(self, _obj, **_args):
        """Generates presentation for the layered-pane role."""

        return []

    def _generate_level_bar(self, _obj, **_args):
        """Generates presentation for the level-bar role."""

        return []

    def _generate_link(self, _obj, **_args):
        """Generates presentation for the link role."""

        return []

    def _generate_list(self, _obj, **_args):
        """Generates presentation for the list role."""

        return []

    def _generate_list_box(self, _obj, **_args):
        """Generates presentation for the list-box role."""

        return []

    def _generate_list_item(self, _obj, **_args):
        """Generates presentation for the list-item role."""

        return []

    def _generate_log(self, _obj, **_args):
        """Generates presentation for the log role."""

        return []

    def _generate_mark(self, _obj, **_args):
        """Generates presentation for the mark role."""

        return []

    def _generate_marquee(self, _obj, **_args):
        """Generates presentation for the marquee role."""

        return []

    def _generate_math(self, _obj, **_args):
        """Generates presentation for the math role."""

        return []

    def _generate_math_enclosed(self, _obj, **_args):
        """Generates presentation for the math-enclosed role."""

        return []

    def _generate_math_fenced(self, _obj, **_args):
        """Generates presentation for the math-fenced role."""

        return []

    def _generate_math_fraction(self, _obj, **_args):
        """Generates presentation for the math-fraction role."""

        return []

    def _generate_math_multiscript(self, _obj, **_args):
        """Generates presentation for the math-multiscript role."""

        return []

    def _generate_math_root(self, _obj, **_args):
        """Generates presentation for the math-root role."""

        return []

    def _generate_math_row(self, _obj, **_args):
        """Generates presentation for the math-row role."""

        return []

    def _generate_math_script_subsuper(self, _obj, **_args):
        """Generates presentation for the math script subsuper role."""

        return []

    def _generate_math_script_underover(self, _obj, **_args):
        """Generates presentation for the math script underover role."""

        return []

    def _generate_math_table(self, _obj, **_args):
        """Generates presentation for the math-table role."""

        return []

    def _generate_menu(self, _obj, **_args):
        """Generates presentation for the menu role."""

        return []

    def _generate_menu_bar(self, _obj, **_args):
        """Generates presentation for the menu-bar role."""

        return []

    def _generate_menu_item(self, _obj, **_args):
        """Generates presentation for the menu-item role."""

        return []

    def _generate_notification(self, _obj, **_args):
        """Generates presentation for the notification role."""

        return []

    def _generate_option_pane(self, _obj, **_args):
        """Generates presentation for the option-pane role."""

        return []

    def _generate_page(self, _obj, **_args):
        """Generates presentation for the page role."""

        return []

    def _generate_page_tab(self, _obj, **_args):
        """Generates presentation for the page-tab role."""

        return []

    def _generate_page_tab_list(self, _obj, **_args):
        """Generates presentation for the page-tab-list role."""

        return []

    def _generate_panel(self, _obj, **_args):
        """Generates presentation for the panel role."""

        return []

    def _generate_paragraph(self, _obj, **_args):
        """Generates presentation for the paragraph role."""

        return []

    def _generate_password_text(self, _obj, **_args):
        """Generates presentation for the password-text role."""

        return []

    def _generate_popup_menu(self, _obj, **_args):
        """Generates presentation for the popup-menu role."""

        return []

    def _generate_progress_bar(self, _obj, **_args):
        """Generates presentation for the progress-bar role."""

        return []

    def _generate_push_button(self, _obj, **_args):
        """Generates presentation for the push-button role."""

        return []

    def _generate_push_button_menu(self, _obj, **_args):
        """Generates presentation for the push-button-menu role."""

        return []

    def _generate_radio_button(self, _obj, **_args):
        """Generates presentation for the radio-button role."""

        return []

    def _generate_radio_menu_item(self, _obj, **_args):
        """Generates presentation for the radio-menu-item role."""

        return []

    def _generate_rating(self, _obj, **_args):
        """Generates presentation for the rating role."""

        return []

    def _generate_region(self, _obj, **_args):
        """Generates presentation for the region landmark role."""

        return []

    def _generate_root_pane(self, _obj, **_args):
        """Generates presentation for the root-pane role."""

        return []

    def _generate_row_header(self, _obj, **_args):
        """Generates presentation for the row-header role."""

        return []

    def _generate_ruler(self, _obj, **_args):
        """Generates presentation for the ruler role."""

        return []

    def _generate_scroll_bar(self, _obj, **_args):
        """Generates presentation for the scroll-bar role."""

        return []

    def _generate_scroll_pane(self, _obj, **_args):
        """Generates presentation for the scroll-pane role."""

        return []

    def _generate_section(self, _obj, **_args):
        """Generates presentation for the section role."""

        return []

    def _generate_separator(self, _obj, **_args):
        """Generates presentation for the separator role."""

        return []

    def _generate_slider(self, _obj, **_args):
        """Generates presentation for the slider role."""

        return []

    def _generate_spin_button(self, _obj, **_args):
        """Generates presentation for the spin-button role."""

        return []

    def _generate_split_pane(self, _obj, **_args):
        """Generates presentation for the split-pane role."""

        return []

    def _generate_static(self, _obj, **_args):
        """Generates presentation for the static role."""

        return []

    def _generate_status_bar(self, _obj, **_args):
        """Generates presentation for the status-bar role."""

        return []

    def _generate_subscript(self, _obj, **_args):
        """Generates presentation for the subscript role."""

        return []

    def _generate_suggestion(self, _obj, **_args):
        """Generates presentation for the suggestion role."""

        return []

    def _generate_superscript(self, _obj, **_args):
        """Generates presentation for the superscript role."""

        return []

    def _generate_switch(self, _obj, **_args):
        """Generates presentation for the switch role."""

        return []

    def _generate_table(self, _obj, **_args):
        """Generates presentation for the table role."""

        return []

    def _generate_table_cell(self, _obj, **_args):
        """Generates presentation for the table-cell role."""

        return []

    def _generate_table_cell_in_row(self, _obj, **_args):
        """Generates presentation for the table-cell role in the context of its row."""

        return []

    def _generate_table_column_header(self, _obj, **_args):
        """Generates presentation for the table-column-header role."""

        return []

    def _generate_table_row(self, _obj, **_args):
        """Generates presentation for the table-row role."""

        return []

    def _generate_table_row_header(self, _obj, **_args):
        """Generates presentation for the table-row-header role."""

        return []

    def _generate_tearoff_menu_item(self, _obj, **_args):
        """Generates presentation for the tearoff-menu-item role."""

        return []

    def _generate_terminal(self, _obj, **_args):
        """Generates presentation for the terminal role."""

        return []

    def _generate_text(self, _obj, **_args):
        """Generates presentation for the text role."""

        return []

    def _generate_timer(self, _obj, **_args):
        """Generates presentation for the timer role."""

        return []

    def _generate_title_bar(self, _obj, **_args):
        """Generates presentation for the title-bar role."""

        return []

    def _generate_toggle_button(self, _obj, **_args):
        """Generates presentation for the toggle-button role."""

        return []

    def _generate_tool_bar(self, _obj, **_args):
        """Generates presentation for the tool-bar role."""

        return []

    def _generate_tool_tip(self, _obj, **_args):
        """Generates presentation for the tool-tip role."""

        return []

    def _generate_tree(self, _obj, **_args):
        """Generates presentation for the tree role."""

        return []

    def _generate_tree_item(self, _obj, **_args):
        """Generates presentation for the tree-item role."""

        return []

    def _generate_tree_table(self, _obj, **_args):
        """Generates presentation for the tree-table role."""

        return []

    def _generate_unknown(self, _obj, **_args):
        """Generates presentation for the unknown role."""

        return []

    def _generate_video(self, _obj, **_args):
        """Generates presentation for the video role."""

        return []

    def _generate_viewport(self, _obj, **_args):
        """Generates presentation for the viewport role."""

        return []

    def _generate_window(self, _obj, **_args):
        """Generates presentation for the window role."""

        return []

Generator.start_cache_clearing_thread()
