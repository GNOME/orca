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

"""Utilities for obtaining braille presentations for objects."""

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
from .ax_value import AXValue
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
        generator.Generator.__init__(self, script, "braille")
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

    def _isCandidateFocusedRegion(self, obj, region):
        if not isinstance(region, (braille.Component, braille.Text)):
            return False

        if not AXUtilities.have_same_role(obj, region.accessible):
            return False

        return AXObject.get_name(obj) == AXObject.get_name(region.accessible)

    def generate(self, obj, **args):
        _generator = self._generators.get(args.get("role") or AXObject.get_role(obj))
        if _generator is None:
            tokens = ["BRAILLE GENERATOR:", obj, "lacks dedicated generator"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            _generator = self._generate_default_presentation

        args['mode'] = self._mode
        if not args.get('formatType', None):
            if args.get('alreadyFocused', False):
                args['formatType'] = 'focused'
            else:
                args['formatType'] = 'unfocused'

        tokens = ["BRAILLE GENERATOR:", _generator, "for", obj, "args:", args]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        result = _generator(obj, **args)
        tokens = ["BRAILLE GENERATOR: Results:", result]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return result

    def generateBraille(self, obj, **args):
        if not settings_manager.get_manager().get_setting('enableBraille') \
           and not settings_manager.get_manager().get_setting('enableBrailleMonitor'):
            debug.printMessage(debug.LEVEL_INFO, "BRAILLE GENERATOR: generation disabled", True)
            return [[], None]

        if obj == focus_manager.get_manager().get_locus_of_focus() \
           and not args.get('formatType', None):
            args['formatType'] = 'focused'
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
            focusedRegion = result[0]
        except Exception:
            focusedRegion = None

        for region in result:
            if isinstance(region, (braille.Component, braille.Text)) and region.accessible == obj:
                focusedRegion = region
                break
            elif isinstance(region, braille.Text) \
                 and AXUtilities.is_combo_box(obj) \
                 and AXObject.get_parent(region.accessible) == obj:
                focusedRegion = region
                break
            elif isinstance(region, braille.Component) \
                 and AXUtilities.is_table_cell(obj) \
                 and AXObject.get_parent(region.accessible) == obj:
                focusedRegion = region
                break
        else:

            def pred(x):
                return self._isCandidateFocusedRegion(obj, x)

            candidates = list(filter(pred, result))
            tokens = ["BRAILLE GENERATOR: Could not determine focused region for",
                      obj, "Candidates:", candidates]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            if len(candidates) == 1:
                focusedRegion = candidates[0]

        return [result, focusedRegion]

    #####################################################################
    #                                                                   #
    # Name, role, and label information                                 #
    #                                                                   #
    #####################################################################

    def _generateRoleName(self, obj, **args):
        """Returns the role name for the object in an array of strings, with
        the exception that the Atspi.Role.UNKNOWN role will yield an
        empty array.  Note that a 'role' attribute in args will
        override the accessible role of the obj.
        """

        if args.get('isProgressBarUpdate') \
           and not settings_manager.get_manager().get_setting('brailleProgressBarUpdates'):
            return []

        result = []
        role = args.get('role', AXObject.get_role(obj))
        verbosityLevel = settings_manager.get_manager().get_setting('brailleVerbosityLevel')

        doNotPresent = [Atspi.Role.UNKNOWN,
                        Atspi.Role.REDUNDANT_OBJECT,
                        Atspi.Role.FILLER,
                        Atspi.Role.EXTENDED,
                        Atspi.Role.LINK]

        # egg-list-box, e.g. privacy panel in gnome-control-center
        if AXUtilities.is_list_box(AXObject.get_parent(obj)):
            doNotPresent.append(AXObject.get_role(obj))

        if verbosityLevel == settings.VERBOSITY_LEVEL_BRIEF:
            doNotPresent.extend([Atspi.Role.ICON, Atspi.Role.CANVAS])

        if role == Atspi.Role.HEADING:
            level = self._script.utilities.headingLevel(obj)
            result.append(object_properties.ROLE_HEADING_LEVEL_BRAILLE % level)

        elif verbosityLevel == settings.VERBOSITY_LEVEL_VERBOSE \
           and not args.get('readingRow', False) and role not in doNotPresent:
            result.append(self.getLocalizedRoleName(obj, **args))
        return result

    def getLocalizedRoleName(self, obj, **args):
        """Returns the localized name of the given Accessible object; the name
        is suitable to be brailled.

        Arguments:
        - obj: an Accessible object
        """

        if settings_manager.get_manager().get_setting('brailleRolenameStyle') \
                == settings.BRAILLE_ROLENAME_STYLE_SHORT:
            role = args.get('role', AXObject.get_role(obj))
            rv = shortRoleNames.get(role)
            if rv:
                return rv

        return super().getLocalizedRoleName(obj, **args)

    def _generateUnrelatedLabels(self, obj, **args):
        result = []
        labels = self._script.utilities.unrelatedLabels(obj)
        for label in labels:
            name = self._generateName(label, **args)
            result.extend(name)

        return result

    #####################################################################
    #                                                                   #
    # Keyboard shortcut information                                     #
    #                                                                   #
    #####################################################################

    def _generateAccelerator(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the accelerator for the object,
        or an empty array if no accelerator can be found.
        """

        verbosityLevel = settings_manager.get_manager().get_setting('brailleVerbosityLevel')
        if verbosityLevel == settings.VERBOSITY_LEVEL_BRIEF:
            return []

        result = []
        [mnemonic, shortcut, accelerator] = \
            self._script.utilities.mnemonicShortcutAccelerator(obj)
        if accelerator:
            result.append("(" + accelerator + ")")
        return result

    #####################################################################
    #                                                                   #
    # Hierarchy and related dialog information                          #
    #                                                                   #
    #####################################################################

    def _generateAlertAndDialogCount(self, obj,  **args):
        """Returns an array of strings that says how many alerts and dialogs
        are associated with the application for this object.  [[[WDW -
        I wonder if this string should be moved to settings.py.]]]
        """
        result = []
        try:
            alertAndDialogCount = \
                self._script.utilities.unfocusedAlertAndDialogCount(obj)
        except Exception:
            alertAndDialogCount = 0
        if alertAndDialogCount > 0:
             result.append(messages.dialogCountBraille(alertAndDialogCount))

        return result

    def _generateAncestors(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the text of the ancestors for
        the object.  This is typically used to present the context for
        an object (e.g., the names of the window, the panels, etc.,
        that the object is contained in).  If the 'priorObj' attribute
        of the args dictionary is set, only the differences in
        ancestry between the 'priorObj' and the current obj will be
        computed.  The 'priorObj' is typically set by Orca to be the
        previous object with focus.
        """
        result = []
        if not settings_manager.get_manager().get_setting('enableBrailleContext'):
            return result
        args['includeContext'] = False

        # Radio button group names are treated separately from the
        # ancestors.  However, they can appear in the ancestry as a
        # labeled panel.  So, we need to exclude the first one of
        # these things we come across.  See also the
        # generator.py:_generateRadioButtonGroup method that is
        # used to find the radio button group name.
        #
        role = args.get('role', AXObject.get_role(obj))
        excludeRadioButtonGroup = role == Atspi.Role.RADIO_BUTTON

        parent = AXObject.get_parent_checked(obj)
        if parent and (AXObject.get_role(parent) in self.SKIP_CONTEXT_ROLES):
            parent = AXObject.get_parent_checked(parent)
        while parent:
            parentResult = []
            # [[[TODO: WDW - we might want to include more things here
            # besides just those things that have labels.  For example,
            # page tab lists might be a nice thing to include. Logged
            # as bugzilla bug 319751.]]]
            #
            role = AXObject.get_role(parent)
            if role != Atspi.Role.FILLER \
                and role != Atspi.Role.INVALID \
                and role != Atspi.Role.SECTION \
                and role != Atspi.Role.SPLIT_PANE \
                and role != Atspi.Role.DESKTOP_FRAME \
                and not self._script.utilities.isLayoutOnly(parent):
                args['role'] = role
                parentResult = self.generate(parent, **args)
            # [[[TODO: HACK - we've discovered oddness in hierarchies
            # such as the gedit Edit->Preferences dialog.  In this
            # dialog, we have labeled groupings of objects.  The
            # grouping is done via a FILLER with two children - one
            # child is the overall label, and the other is the
            # container for the grouped objects.  When we detect this,
            # we add the label to the overall context.]]]
            #
            if role in [Atspi.Role.FILLER, Atspi.Role.PANEL]:
                label = self._script.utilities.displayedLabel(parent)
                if label and len(label) and not label.isspace():
                    if not excludeRadioButtonGroup:
                        args['role'] = AXObject.get_role(parent)
                        parentResult = self.generate(parent, **args)
                    else:
                        excludeRadioButtonGroup = False
            if result and parentResult:
                result.append(braille.Region(" "))
            result.extend(parentResult)
            if role == Atspi.Role.EMBEDDED:
                break

            parent = AXObject.get_parent_checked(parent)
        result.reverse()
        return result

    def _generateFocusedItem(self, obj, **args):
        result = []
        role = args.get('role', AXObject.get_role(obj))
        if role not in [Atspi.Role.LIST, Atspi.Role.LIST_BOX]:
            return result

        if AXObject.supports_selection(obj):
            items = self._script.utilities.selectedChildren(obj)
        else:
            items = [AXUtilities.get_focused_object(obj)]
        if not (items and items[0]):
            return result

        for item in map(self._generateName, items):
            result.extend(item)

        return result

    def _generateTermValueCount(self, obj, **args):
        count = self._script.utilities.getValueCountForTerm(obj)
        if count < 0:
            return []

        return [f"({messages.valueCountForTerm(count)})"]

    def _generateStatusBar(self, obj, **args):
        if not AXUtilities.is_status_bar(obj):
            return []

        items = self._script.utilities.statusBarItems(obj)
        if not items or items == [obj]:
            return []

        result = []
        for child in items:
            childResult = self.generate(child, includeContext=False)
            if childResult:
                result.extend(childResult)
                result.append(braille.Region(" "))

        return result

    def _generateListBoxItemWidgets(self, obj, **args):
        if not AXUtilities.is_list_box(AXObject.get_parent(obj)):
            return []

        result = []
        for widget in AXUtilities.get_all_widgets(obj):
            result.extend(self.generate(widget, includeContext=False))
            result.append(braille.Region(" "))
        return result

    def _generateProgressBarIndex(self, obj, **args):
        if not args.get('isProgressBarUpdate') \
           or not self._shouldPresentProgressBarUpdate(obj, **args):
            return []

        acc, updateTime, updateValue = self._getMostRecentProgressBarUpdate()
        if acc != obj:
            number, count = self.getProgressBarNumberAndCount(obj)
            return [f'{number}']

        return []

    def _generateProgressBarValue(self, obj, **args):
        if args.get('isProgressBarUpdate') \
           and not self._shouldPresentProgressBarUpdate(obj, **args):
            return []

        result = self._generatePercentage(obj, **args)
        if obj == focus_manager.get_manager().get_locus_of_focus() and not result:
            return ['']

        return result

    def _generatePercentage(self, obj, **args):
        percent = AXValue.get_value_as_percent(obj)
        if percent is not None:
            return [f'{percent}%']

        return []

    def _getProgressBarUpdateInterval(self):
        interval = settings_manager.get_manager().get_setting('progressBarBrailleInterval')
        if interval is None:
            return super()._getProgressBarUpdateInterval()

        return int(interval)

    def _shouldPresentProgressBarUpdate(self, obj, **args):
        if not settings_manager.get_manager().get_setting('brailleProgressBarUpdates'):
            return False

        return super()._shouldPresentProgressBarUpdate(obj, **args)

    def _generateIncludeContext(self, obj, **args):
        """Returns True or False to indicate whether context should be
        included or not.
        """

        if args.get('isProgressBarUpdate'):
            return False

        # For multiline text areas, we only show the context if we
        # are on the very first line.  Otherwise, we show only the
        # line.
        #
        include = settings_manager.get_manager().get_setting('enableBrailleContext')
        if not include:
            return include

        if self._script.utilities.isTextArea(obj) or AXUtilities.is_label(obj):
            include = AXText.get_line_at_offset(obj)[1] == 0
            if include:
                targets = AXUtilities.get_flows_from(obj)
                if targets:
                    include = not self._script.utilities.isTextArea(targets[0])
        return include

    #####################################################################
    #                                                                   #
    # Other things for spacing                                          #
    #                                                                   #
    #####################################################################

    def _generateEol(self, obj, **args):
        if settings_manager.get_manager().get_setting("disableBrailleEOL"):
            return []

        if not (AXUtilities.is_editable(obj) or AXUtilities.is_code(obj)):
            return []

        return [object_properties.EOL_INDICATOR_BRAILLE]

    def space(self, delimiter=" "):
        if delimiter == " ":
            return SPACE
        else:
            return [Space(delimiter)]

    def asString(self, content, delimiter=" "):
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
                    prior = self.asString(element)
                    combined = self._script.utilities.appendString(
                        combined, prior, delimiter)
        return combined

#########################################################################################

    def _generate_default_prefix(self, obj, **args):
        """Provides the default/role-agnostic information to present before obj."""

        if args.get("includeContext") is False:
            return []

        result = self._generateAncestors(obj, **args)
        if result:
            result += [braille.Region(" ")]
        return result

    def _generate_default_presentation(self, obj, **args):
        """Provides a default/role-agnostic presentation of obj."""

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Component(
            obj, self.asString(
                self._generateLabelAndName(obj, **args) +
                self._generateDisplayedText(obj, **args) +
                self._generateValue(obj, **args) +
                self._generateRoleName(obj, **args) +
                self._generateRequired(obj, **args) +
                self._generateInvalid(obj, **args)))]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_default_suffix(self, obj, **args):
        """Provides the default/role-agnostic information to present after obj."""

        return []

    def _generate_text_object(self, obj, **args):
        """Provides a default/role-agnostic generation of text objects."""

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Text(
            obj,
            self.asString(
                self._generateLabelAndName(obj, **args) \
                    or self._generatePlaceholderText(obj, **args)),
            self.asString(self._generateEol(obj, **args)),
            self._generateStartOffset(obj, **args),
            self._generateEndOffset(obj, **args),
            self._generateCaretOffset(obj, **args))]

        # TODO - JD: The lines below reflect what we've been doing, but only make sense
        # for text fields. Historically we've also used generic text object generation
        # for things like paragraphs. For now, maintain the original logic so that we can
        # land the refactor. Then follow up with improvements.
        invalid = self._generateInvalid(obj, **args)
        if invalid:
            result += [braille.Region(" " + self.asString(invalid))]

        required = self._generateRequired(obj, **args)
        if required:
            result +=[braille.Region(" " + self.asString(required))]

        readonly = self._generateReadOnly(obj, **args)
        if readonly:
            result +=[braille.Region(" " + self.asString(readonly))]

        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_accelerator_label(self, obj, **args):
        """Generates braille for the accelerator-label role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_alert(self, obj, **args):
        """Generates braille for the alert role."""

        if self._generateSubstring(obj, **args):
            return self._generate_text_object(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Component(
            obj, self.asString(
                self._generateLabelAndName(obj, **args) +
                self._generateRoleName(obj, **args)))]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_animation(self, obj, **args):
        """Generates braille for the animation role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_application(self, obj, **args):
        """Generates braille for the application role."""

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Component(
            obj, self.asString(
                self._generateLabelAndName(obj, **args) +
                self._generateRoleName(obj, **args)))]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_arrow(self, obj, **args):
        """Generates braille for the arrow role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_article(self, obj, **args):
        """Generates braille for the article role."""

        if self._generateSubstring(obj, **args):
            return self._generate_text_object(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Component(
            obj, self.asString(
                self._generateLabelAndName(obj, **args) +
                self._generateRoleName(obj, **args)))]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_article_in_feed(self, obj, **args):
        """Generates braille for the article role when the article is in a feed."""

        if self._generateSubstring(obj, **args):
            return self._generate_text_object(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Component(
            obj, self.asString(
                self._generateLabelAndName(obj, **args) +
                self._generateRoleName(obj, **args)))]
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
        result += [braille.Region(" " + self.asString(
            self._generateRoleName(obj, **args) + self._generateNestingLevel(obj, **args)))]
        return result

    def _generate_calendar(self, obj, **args):
        """Generates braille for the calendar role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_canvas(self, obj, **args):
        """Generates braille for the canvas role."""

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Component(
            obj, self.asString(
                self._generateLabelAndName(obj, **args) +
                (self._generateImageDescription(obj, **args) \
                    or self._generateRoleName(obj, **args))))]
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
            obj, self.asString(
                self._generateLabelAndName(obj, **args) +
                self._generateRoleName(obj, **args)),
            indicator=self.asString(self._generateCheckedState(obj, **args)))]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_check_menu_item(self, obj, **args):
        """Generates braille for the check-menu-item role."""

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Component(
            obj, self.asString(
                self._generateLabelAndName(obj, **args) +
                self._generateRoleName(obj, **args) +
                self._generateAccelerator(obj, **args)),
            indicator=self.asString(self._generateCheckedState(obj, **args)))]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_color_chooser(self, obj, **args):
        """Generates braille for the color-chooser role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_column_header(self, obj, **args):
        """Generates braille for the column-header role."""

        if self._generateSubstring(obj, **args):
            line = self._generateCurrentLineText(obj, **args)
        else:
            line = self._generateLabelAndName(obj, **args)

        result = [braille.Component(
            obj, self.asString(
                line + self._generateRoleName(obj, **args) + self._generateSortOrder(obj, **args)))]

        return result

    def _generate_combo_box(self, obj, **args):
        """Generates braille for the combo-box role."""

        result = self._generate_default_prefix(obj, **args)
        label = self._generateLabelAndName(obj, **args)
        if label:
            offset = len(label[0]) + 1
        else:
            offset = 0

        result += [braille.Component(
            obj, self.asString(label +
                               self._generateValue(obj, **args) +
                               self._generateRoleName(obj, **args)), offset)]
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
        result += [braille.Region(" " + self.asString(self._generateTermValueCount(obj, **args)))]
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
            obj, self.asString(
                self._generateLabelAndName(obj, **args) +
                self._generateValue(obj, **args) +
                self._generateRoleName(obj, **args)))]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_dialog(self, obj, **args):
        """Generates braille for the dialog role."""

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Component(
            obj, self.asString(
                self._generateLabelAndName(obj, **args) +
                self._generateRoleName(obj, **args) +
                self._generateUnrelatedLabelsOrDescription(obj, **args)))]
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
            self.asString(self._generateEol(obj, **args)),
            self._generateStartOffset(obj, **args),
            self._generateEndOffset(obj, **args))]
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

        if self._generateSubstring(obj, **args):
            return self._generate_text_object(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Component(
            obj, self.asString(
                self._generateLabelAndName(obj, **args) +
                self._generateRoleName(obj, **args)))]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_frame(self, obj, **args):
        """Generates braille for the frame role."""

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Component(
            obj, self.asString(
                self._generateLabelAndName(obj, **args) +
                self._generateRoleName(obj, **args) +
                self._generateAlertAndDialogCount(obj, **args)))]
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
        result += [braille.Region(" " + self.asString(self._generateRoleName(obj, **args)))]
        return result

    def _generate_html_container(self, obj, **args):
        """Generates braille for the html-container role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_icon(self, obj, **args):
        """Generates braille for the icon role."""

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Component(
            obj, self.asString(
                self._generateLabelAndName(obj, **args) +
                (self._generateImageDescription(obj, **args) \
                    or self._generateRoleName(obj, **args))))]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_image(self, obj, **args):
        """Generates braille for the image role."""

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Component(
            obj, self.asString(
                self._generateLabelAndName(obj, **args) +
                self._generateRoleName(obj, **args)))]
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
            obj, self.asString(
                self._generateLabelAndName(obj, **args) +
                self._generateValue(obj, **args) +
                self._generateRoleName(obj, **args)))]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_link(self, obj, **args):
        """Generates braille for the link role."""

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Link(
            obj, self.asString(
                (self._generateLabelAndName(obj, **args) \
                    or self._generateDisplayedText(obj, **args))))]

        rolename = self._generateRoleName(obj, **args)
        if rolename:
            result += [braille.Region(" " + self.asString(rolename))]

        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_list(self, obj, **args):
        """Generates braille for the list role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_list_box(self, obj, **args):
        """Generates braille for the list-box role."""

        result = self._generate_default_prefix(obj, **args)
        label = self._generateLabelAndName(obj, **args)
        if label:
            offset = len(label[0]) + 1
        else:
            offset = 0

        result += [braille.Component(
            obj, self.asString(label +
                               self._generateFocusedItem(obj, **args) +
                               self._generateRoleName(obj, **args)), offset)]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_list_item(self, obj, **args):
        """Generates braille for the list-item role."""

        if self._generateSubstring(obj, **args):
            return self._generate_text_object(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Component(
            obj, self.asString(
                self._generateLabelAndName(obj, **args) +
                self._generateExpandableState(obj, **args)))]

        level = self._generateNestingLevel(obj, **args)
        if level:
            result += [braille.Region(" " + self.asString(level))]

        widgets = self._generateListBoxItemWidgets(obj, **args)
        if widgets:
            result += [braille.Region(" " + self.asString(widgets))]

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
            obj, self.asString(
                self._generateLabelAndName(obj, **args) +
                self._generateRoleName(obj, **args)))]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_menu_bar(self, obj, **args):
        """Generates braille for the menu-bar role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_menu_item(self, obj, **args):
        """Generates braille for the menu-item role."""

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Component(
            obj, self.asString(
                self._generateLabelAndName(obj, **args) +
                self._generateExpandableState(obj, **args) +
                self._generateAccelerator(obj, **args)),
            indicator=self.asString(self._generateCheckedStateIfCheckable(obj, **args)))]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_notification(self, obj, **args):
        """Generates braille for the notification role."""

        if self._generateSubstring(obj, **args):
            return self._generate_text_object(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Component(
            obj, self.asString(
                self._generateLabelAndName(obj, **args) +
                self._generateRoleName(obj, **args)))]
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
            obj, self.asString(
                self._generateLabelAndName(obj, **args) +
                self._generateRoleName(obj, **args) +
                self._generateAccelerator(obj, **args)))]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_page_tab_list(self, obj, **args):
        """Generates braille for the page-tab-list role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_panel(self, obj, **args):
        """Generates braille for the panel role."""

        if self._generateSubstring(obj, **args):
            return self._generate_text_object(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Component(
            obj, self.asString(
                self._generateLabelAndName(obj, **args) +
                self._generateRoleName(obj, **args)))]
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

        value = self._generateProgressBarValue(obj, **args)
        if not value:
            return []

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Component(
            obj, self.asString(
                self._generateLabelAndName(obj, **args) +
                value +
                self._generateRoleName(obj, **args) +
                self._generateProgressBarIndex(obj, **args)))]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_push_button(self, obj, **args):
        """Generates braille for the push-button role."""

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Component(
            obj, self.asString(
                self._generateLabelAndName(obj, **args) +
                self._generateExpandableState(obj, **args) +
                self._generateRoleName(obj, **args)))]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_push_button_menu(self, obj, **args):
        """Generates braille for the push-button-menu role."""

        return self._generate_push_button(obj, **args)

    def _generate_radio_button(self, obj, **args):
        """Generates braille for the radio-button role."""

        result = self._generate_default_prefix(obj, **args)
        group = self._generateRadioButtonGroup(obj, **args)
        if group:
            result += [braille.Region(" " + self.asString(group))]

        result += [braille.Component(
            obj, self.asString(
                self._generateLabelAndName(obj, **args) +
                self._generateRoleName(obj, **args)),
            indicator=self.asString(self._generateRadioState(obj, **args)))]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_radio_menu_item(self, obj, **args):
        """Generates braille for the radio-menu-item role."""

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Component(
            obj, self.asString(
                self._generateLabelAndName(obj, **args) +
                self._generateRoleName(obj, **args) +
                self._generateAccelerator(obj, **args)),
            indicator=self.asString(self._generateRadioState(obj, **args)))]
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

        if self._generateSubstring(obj, **args):
            line = self._generateCurrentLineText(obj, **args)
        else:
            line = self._generateLabelAndName(obj, **args)

        result = [braille.Component(
            obj, self.asString(
                line + self._generateRoleName(obj, **args) + self._generateSortOrder(obj, **args)))]

        return result

    def _generate_ruler(self, obj, **args):
        """Generates braille for the ruler role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_scroll_bar(self, obj, **args):
        """Generates braille for the scroll-bar role."""

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Component(
            obj, self.asString(
                self._generateLabelAndName(obj, **args) +
                self._generateValue(obj, **args) +
                self._generateRoleName(obj, **args)))]
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
            obj, self.asString(
                self._generateLabelAndName(obj, **args) +
                self._generateValue(obj, **args) +
                self._generateRoleName(obj, **args)))]
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
            obj, self.asString(
                self._generateLabelAndName(obj, **args) +
                self._generateRoleName(obj, **args)))]
        result += [braille.Region(" ")]
        result += self._generateStatusBar(obj, **args)
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
            obj, self.asString(
                self._generateLabelAndName(obj, **args) +
                self._generateRoleName(obj, **args)),
            indicator=self.asString(self._generateSwitchState(obj, **args)))]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_table(self, obj, **args):
        """Generates braille for the table role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_table_cell(self, obj, **args):
        """Generates braille for the table-cell role."""

        suffix = []
        node_level = self._generateNodeLevel(obj, **args)
        if node_level:
            suffix += [braille.Region(" " + self.asString(node_level))]

        if self._generateSubstring(obj, **args):
            result = self._generate_text_object(obj, **args)
            result += suffix
            return result

        result = []
        result += self._generateCellCheckedState(obj, **args)
        result += [braille.Component(
            obj, self.asString(
                self._generateColumnHeaderIfToggleAndNoText(obj, **args) +
                self._generateRealActiveDescendantDisplayedText(obj, **args) +
                self._generateRealActiveDescendantRoleName(obj, **args) +
                self._generateExpandableState(obj, **args)))]
        result += suffix
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_table_cell_in_row(self, obj, **args):
        """Generates braille for the table-cell role in the context of its row."""

        if self._generateSubstring(obj, **args):
            return self._generate_text_object(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        row_header = self._generateRowHeader(obj, **args)
        if row_header:
            result += [braille.Region(" " + self.asString(row_header))]
        column_header = self._generateColumnHeader(obj, **args)
        if column_header:
            result += [braille.Region(" " + self.asString(column_header))]
        if row_header or column_header:
            result += [braille.Region(" ")]
        result += self._generateTableCellRow(obj, **args)
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

    def _generate_terminal(self, obj, **args):
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
            obj, self.asString(
                self._generateLabelAndName(obj, **args) +
                self._generateExpandableState(obj, **args) +
                self._generateRoleName(obj, **args)),
            indicator=self.asString(self._generateToggleState(obj, **args)))]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_tool_bar(self, obj, **args):
        """Generates braille for the tool-bar role."""

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Component(
            obj, self.asString(
                self._generateLabelAndName(obj, **args) +
                self._generateRoleName(obj, **args)))]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_tool_tip(self, obj, **args):
        """Generates braille for the tool-tip role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_tree(self, obj, **args):
        """Generates braille for the tree role."""

        result = self._generate_default_prefix(obj, **args)
        result += [braille.Component(
            obj, self.asString(
                self._generateLabelAndName(obj, **args) +
                self._generateRoleName(obj, **args)))]
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_tree_item(self, obj, **args):
        """Generates braille for the tree-item role."""

        if self._generateSubstring(obj, **args):
            result = self._generate_text_object(obj, **args)
        else:
            result = [braille.Component(
                obj, self.asString(
                    self._generateLabelAndName(obj, **args) +
                    self._generateExpandableState(obj, **args)))]

        node_level = self._generateNodeLevel(obj, **args)
        if node_level:
            result +=[braille.Region(" " + self.asString(node_level))]

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
