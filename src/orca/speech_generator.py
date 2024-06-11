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

"""Utilities for obtaining speech utterances for objects."""

__id__        = "$Id:$"
__version__   = "$Revision:$"
__date__      = "$Date:$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import functools
import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

import urllib.parse
import urllib.request
import urllib.error
import urllib.parse

from . import acss
from . import debug
from . import generator
from . import input_event_manager
from . import mathsymbols
from . import messages
from . import object_properties
from . import settings
from . import settings_manager
from . import speech
from . import text_attribute_names
from .ax_document import AXDocument
from .ax_hypertext import AXHypertext
from .ax_object import AXObject
from .ax_table import AXTable
from .ax_text import AXText
from .ax_utilities import AXUtilities
from .ax_value import AXValue

class Pause:
    """A dummy class to indicate we want to insert a pause into an
    utterance."""
    def __init__(self):
        pass

    def __str__(self):
        return "PAUSE"

PAUSE = [Pause()]

class LineBreak:
    """A dummy class to indicate we want to break an utterance into
    separate calls to speak."""
    def __init__(self):
        pass

    def __str__(self):
        return "LINE BREAK"

LINE_BREAK = [LineBreak()]

# [[[WDW - general note -- for all the _generate* methods, it would be great if
# we could return an empty array if we can determine the method does not
# apply to the object.  This would allow us to reduce the number of strings
# needed in formatting.py.]]]

# The prefix to use for the individual generator methods
#
METHOD_PREFIX = "_generate"

DEFAULT        = "default"
UPPERCASE      = "uppercase"
HYPERLINK      = "hyperlink"
SYSTEM         = "system"
STATE          = "state" # Candidate for sound
VALUE          = "value" # Candidate for sound

voiceType = {
    DEFAULT: settings.DEFAULT_VOICE,
    UPPERCASE: settings.UPPERCASE_VOICE,
    HYPERLINK: settings.HYPERLINK_VOICE,
    SYSTEM: settings.SYSTEM_VOICE,
    STATE: settings.SYSTEM_VOICE, # Users may prefer DEFAULT_VOICE here
    VALUE: settings.SYSTEM_VOICE, # Users may prefer DEFAULT_VOICE here
}

class SpeechGenerator(generator.Generator):
    """Takes accessible objects and produces a string to speak for
    those objects.  See the generateSpeech method, which is the primary
    entry point.  Subclasses can feel free to override/extend the
    speech_generators instance field as they see fit."""

    def __init__(self, script):
        generator.Generator.__init__(self, script, "speech")
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

    def generate(self, obj, **args):
        _generator = self._generators.get(args.get("role") or AXObject.get_role(obj))
        if _generator is None:
            tokens = ["SPEECH GENERATOR:", obj, "lacks dedicated generator"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            _generator = self._generate_default_presentation

        args['mode'] = self._mode
        if not args.get('formatType', None):
            if args.get('alreadyFocused', False):
                args['formatType'] = 'focused'
            else:
                args['formatType'] = 'unfocused'

        tokens = ["SPEECH GENERATOR:", _generator, "for", obj, "args:", args]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        result = _generator(obj, **args)
        tokens = ["SPEECH GENERATOR: Results:", result]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return result

    def generateSpeech(self, obj, **args):
        rv = self.generate(obj, **args)
        if rv and not list(filter(lambda x: not isinstance(x, Pause), rv)):
            tokens = ["SPEECH GENERATOR: Results for", obj, "are pauses only"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            rv = []

        return rv

    def _resultElementToString(self, element, includeAll=True):
        if isinstance(element, acss.ACSS) and not includeAll:
            return ""

        if isinstance(element, list):
            rv = [self._resultElementToString(x, includeAll) for x in element]
            return " ".join(filter(lambda x: x, rv))

        return super()._resultElementToString(element, includeAll)

    #####################################################################
    #                                                                   #
    # Name, role, and label information                                 #
    #                                                                   #
    #####################################################################

    def _generateName(self, obj, **args):
        """Returns an array of strings for use by speech and braille that
        represent the name of the object.  If the object is directly
        displaying any text, that text will be treated as the name.
        Otherwise, the accessible name of the object will be used.  If
        there is no accessible name, then the description of the
        object will be used.  This method will return an empty array
        if nothing can be found.  [[[WDW - I wonder if we should just
        have _generateName, _generateDescription,
        _generateDisplayedText, etc., that don't do any fallback.
        Then, we can allow the formatting to do the fallback (e.g.,
        'displayedText or name or description'). [[[JD to WDW - I
        needed a _generateDescription for whereAmI. :-) See below.
        """

        is_layered_pane = AXUtilities.is_layered_pane(obj, args.get("role"))
        if is_layered_pane and settings_manager.get_manager().get_setting('onlySpeakDisplayedText'):
            return []

        result = generator.Generator._generateName(self, obj, **args)
        if result:
            if is_layered_pane:
                result.extend(self.voice(SYSTEM, obj=obj, **args))
            else:
                result.extend(self.voice(DEFAULT, obj=obj, **args))

        return result

    def _generateLabel(self, obj, **args):
        """Returns the label for an object as an array of strings for use by
        speech and braille.  The label is determined by the displayedLabel
        method of the script utility, and an empty array will be returned if
        no label can be found.
        """

        result = generator.Generator._generateLabel(self, obj, **args)
        if result:
            result.extend(self.voice(DEFAULT, obj=obj, **args))
        return result

    def _generatePlaceholderText(self, obj, **args):
        """Returns an array of strings for use by speech and braille that
        represent the 'placeholder' text. This is typically text that
        serves as a functional label and is found in a text widget until
        that widget is given focus at which point the text is removed,
        the assumption being that the user was able to see the text prior
        to giving the widget focus.
        """

        result = generator.Generator._generatePlaceholderText(self, obj, **args)
        if result:
            result.extend(self.voice(DEFAULT, obj=obj, **args))
        return result

    def _generateAlertText(self, obj, **args):
        result = self._generateExpandedEOCs(obj, **args) \
                 or self._generateUnrelatedLabels(obj, **args)
        if result:
            self._script.point_of_reference['usedDescriptionForAlert'] = False
            return result

        args['alerttext'] = True
        result = self._generateDescription(obj, **args)
        if result:
            self._script.point_of_reference['usedDescriptionForAlert'] = True

        return result

    def _generateDescription(self, obj, **args):
        """Returns an array of strings fo use by speech and braille that
        represent the description of the object, if that description
        is different from that of the name and label.
        """

        alreadyUsed = False
        if AXUtilities.is_alert(obj, args.get("role")):
            try:
                alreadyUsed = self._script.point_of_reference.pop('usedDescriptionForAlert')
            except Exception:
                pass
        else:
            try:
                alreadyUsed = self._script.point_of_reference.pop(
                    'usedDescriptionForUnrelatedLabels')
            except Exception:
                pass

        if alreadyUsed:
            return []

        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText'):
            return []

        if not settings_manager.get_manager().get_setting('speakDescription') \
           and not args.get('alerttext'):
            return []

        if args.get('inMouseReview') \
           and not settings_manager.get_manager().get_setting('presentToolTips'):
            return []

        priorObj = args.get('priorObj')
        if AXUtilities.is_tool_tip(priorObj):
            return []

        if priorObj == obj:
            return []

        result = generator.Generator._generateDescription(self, obj, **args)
        if result:
            result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    def _generateImageDescription(self, obj, **args ):
        """Returns an array of strings for use by speech and braille that
        represent the description of the image on the object."""

        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText'):
            return []

        if not settings_manager.get_manager().get_setting('speakDescription'):
            return []

        result = generator.Generator._generateImageDescription(self, obj, **args)
        if result:
            result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    def _generateReadOnly(self, obj, **args):
        """Returns an array of strings for use by speech and braille that
        represent the read only state of this object, but only if it
        is read only (i.e., it is a text area that cannot be edited).
        """

        result = generator.Generator._generateReadOnly(self, obj, **args)
        if result:
            result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    def _generateHasPopup(self, obj, **args):
        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText') \
           or settings_manager.get_manager().get_setting('speechVerbosityLevel') \
               == settings.VERBOSITY_LEVEL_BRIEF:
            return []

        if AXUtilities.is_menu(obj) or not AXUtilities.has_popup(obj):
            return []

        return [messages.HAS_POPUP, self.voice(SYSTEM, obj=obj, **args)]

    def _generateClickable(self, obj, **args):
        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText') \
           or settings_manager.get_manager().get_setting('speechVerbosityLevel') \
               == settings.VERBOSITY_LEVEL_BRIEF:
            return []

        result = generator.Generator._generateClickable(self, obj, **args)
        if result:
            result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    def _generateHasLongDesc(self, obj, **args):
        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText'):
            return []

        result = generator.Generator._generateHasLongDesc(self, obj, **args)
        if result:
            result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    def _generateHasDetails(self, obj, **args):
        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText'):
            return []

        result = generator.Generator._generateHasDetails(self, obj, **args)
        if result:
            result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    def _generateDetailsFor(self, obj, **args):
        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText'):
            return []

        result = generator.Generator._generateDetailsFor(self, obj, **args)
        if result:
            result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    def _generateAllDetails(self, obj, **args):
        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText'):
            return []

        result = generator.Generator._generateAllDetails(self, obj, **args)
        if result:
            result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    def _generateDeletionStart(self, obj, **args):
        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText'):
            return []

        startOffset = args.get('startOffset', 0)
        if startOffset != 0:
            return []

        result = []
        if self._script.utilities.isFirstItemInInlineContentSuggestion(obj):
            result.extend([object_properties.ROLE_CONTENT_SUGGESTION])
            result.extend(self.voice(SYSTEM, obj=obj, **args))
            result.extend(self._generatePause(obj, **args))

        result.extend([messages.CONTENT_DELETION_START])
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    def _generateDeletionEnd(self, obj, **args):
        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText'):
            return []

        endOffset = args.get('endOffset')
        if endOffset is not None:
            length = AXText.get_character_count(obj)
            if length and length != endOffset:
                return []

        result = [messages.CONTENT_DELETION_END]
        result.extend(self.voice(SYSTEM, obj=obj, **args))

        if self._script.utilities.isLastItemInInlineContentSuggestion(obj):
            result.extend(self._generatePause(obj, **args))
            result.extend([messages.CONTENT_SUGGESTION_END])
            result.extend(self.voice(SYSTEM, obj=obj, **args))

            container = AXObject.find_ancestor(obj, self._script.utilities.hasDetails)
            if AXUtilities.is_suggestion(container):
                result.extend(self._generatePause(obj, **args))
                result.extend(self._generateHasDetails(container, mode=args.get('mode')))

        return result

    def _generateInsertionStart(self, obj, **args):
        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText'):
            return []

        startOffset = args.get('startOffset', 0)
        if startOffset != 0:
            return []

        result = []
        if self._script.utilities.isFirstItemInInlineContentSuggestion(obj):
            result.extend([object_properties.ROLE_CONTENT_SUGGESTION])
            result.extend(self.voice(SYSTEM, obj=obj, **args))
            result.extend(self._generatePause(obj, **args))

        result.extend([messages.CONTENT_INSERTION_START])
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    def _generateInsertionEnd(self, obj, **args):
        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText'):
            return []

        endOffset = args.get('endOffset')
        if endOffset is not None:
            length = AXText.get_character_count(obj)
            if length and length != endOffset:
                return []

        result = [messages.CONTENT_INSERTION_END]
        result.extend(self.voice(SYSTEM, obj=obj, **args))

        if self._script.utilities.isLastItemInInlineContentSuggestion(obj):
            result.extend(self._generatePause(obj, **args))
            result.extend([messages.CONTENT_SUGGESTION_END])
            result.extend(self.voice(SYSTEM, obj=obj, **args))

            container = AXObject.find_ancestor(obj, self._script.utilities.hasDetails)
            if AXUtilities.is_suggestion(container):
                result.extend(self._generatePause(obj, **args))
                result.extend(self._generateHasDetails(container, mode=args.get('mode')))

        return result

    def _generateMarkStart(self, obj, **args):
        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText'):
            return []

        startOffset = args.get('startOffset', 0)
        if startOffset != 0:
            return []

        result = []
        roledescription = self._script.utilities.getRoleDescription(obj)
        if roledescription:
            result.append(roledescription)
            result.extend(self.voice(SYSTEM, obj=obj, **args))
            result.extend(self._generatePause(obj, **args))

        result.append(messages.CONTENT_MARK_START)
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    def _generateMarkEnd(self, obj, **args):
        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText'):
            return []

        endOffset = args.get('endOffset')
        if endOffset is not None:
            length = AXText.get_character_count(obj)
            if length and length != endOffset:
                return []

        result = [messages.CONTENT_MARK_END]
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    def _generateAvailability(self, obj, **args):
        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText'):
            return []

        if AXUtilities.is_sensitive(obj):
            return []

        result = [object_properties.STATE_INSENSITIVE_SPEECH]
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    def _generateInvalid(self, obj, **args):
        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText'):
            return []

        result = generator.Generator._generateInvalid(self, obj, **args)
        if result:
            result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    def _generateRequired(self, obj, **args):
        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText'):
            return []

        result = generator.Generator._generateRequired(self, obj, **args)
        if result:
            result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    def _generateTable(self, obj, **args):
        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText'):
            return []

        if args.get("leaving"):
            return []

        if self._script.utilities.isTextDocumentTable(obj):
            role = args.get('role', AXObject.get_role(obj))
            enabled, disabled = self._getEnabledAndDisabledContextRoles()
            if role in disabled:
                return []

        if settings_manager.get_manager().get_setting('speechVerbosityLevel') \
           == settings.VERBOSITY_LEVEL_BRIEF:
            return self._generateRoleName(obj, **args)

        result = generator.Generator._generateTable(self, obj, **args)
        if result:
            result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    def _generateRoleName(self, obj, **args):
        """Returns the role name for the object in an array of strings (and
        possibly voice and audio specifications), with the exception
        that the Atspi.Role.UNKNOWN role will yield an empty array.
        Note that a 'role' attribute in args will override the
        accessible role of the obj.
        """
        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText'):
            return []

        if self._script.utilities.isStatusBarNotification(obj):
            return []

        if self._script.utilities.isDesktop(obj):
            return []

        if self._script.utilities.isDockedFrame(obj):
            return []

        result = []
        role = args.get('role', AXObject.get_role(obj))

        doNotPresent = [Atspi.Role.UNKNOWN,
                        Atspi.Role.REDUNDANT_OBJECT,
                        Atspi.Role.FILLER,
                        Atspi.Role.EXTENDED]

        parent = AXObject.get_parent(obj)
        if AXUtilities.is_menu(obj, args.get("role")) and AXUtilities.is_combo_box(parent):
            return self._generateRoleName(parent)

        if self._script.utilities.isSingleLineAutocompleteEntry(obj):
            result.append(self.getLocalizedRoleName(obj, role=Atspi.Role.AUTOCOMPLETE))
            result.extend(self.voice(SYSTEM, obj=obj, **args))
            return result

        if AXUtilities.is_panel(obj, args.get("role")) and AXUtilities.is_selected(obj):
            return []

        # egg-list-box, e.g. privacy panel in gnome-control-center
        if AXUtilities.is_list_box(parent):
            doNotPresent.append(AXObject.get_role(obj))

        if self._script.utilities.isStatusBarDescendant(obj):
            doNotPresent.append(Atspi.Role.LABEL)

        if settings_manager.get_manager().get_setting('speechVerbosityLevel') \
                == settings.VERBOSITY_LEVEL_BRIEF:
            doNotPresent.extend([Atspi.Role.ICON, Atspi.Role.CANVAS])

        if AXUtilities.is_heading(obj):
            level = self._script.utilities.headingLevel(obj)
            if level:
                result.append(object_properties.ROLE_HEADING_LEVEL_SPEECH % {
                    'role': self.getLocalizedRoleName(obj, **args),
                    'level': level})
                result.extend(self.voice(SYSTEM, obj=obj, **args))

        if role not in doNotPresent and not result:
            result.append(self.getLocalizedRoleName(obj, **args))
            result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    def getRoleName(self, obj, **args):
        """Returns the role name for the object in an array of strings (and
        possibly voice and audio specifications), with the exception
        that the Atspi.Role.UNKNOWN role will yield an empty array.
        Note that a 'role' attribute in args will override the
        accessible role of the obj.  This is provided mostly as a
        method for scripts to call.
        """
        generated = self._generateRoleName(obj, **args)
        if generated:
            return generated[0]

        return ""

    def getName(self, obj, **args):
        generated = self._generateName(obj, **args)
        if generated:
            return generated[0]

        return ""

    def getLocalizedRoleName(self, obj, **args):
        """Returns the localized name of the given Accessible object; the name
        is suitable to be spoken.

        Arguments:
        - obj: an Accessible object
        """

        if self._script.utilities.isEditableComboBox(obj) \
           or self._script.utilities.isEditableDescendantOfComboBox(obj):
            return object_properties.ROLE_EDITABLE_COMBO_BOX

        if AXUtilities.is_link(obj, args.get("role")) and AXUtilities.is_visited(obj):
            return object_properties.ROLE_VISITED_LINK

        return super().getLocalizedRoleName(obj, **args)

    def _generateUnrelatedLabels(self, obj, **args):
        """Returns, as an array of strings (and possibly voice
        specifications), all the labels which are underneath the obj's
        hierarchy and which are not in a label for or labelled by
        relation.
        """
        result = []
        visibleOnly = not self._script.utilities.isStatusBarNotification(obj)

        minimumWords = 1
        role = args.get("role")
        if AXUtilities.is_panel(obj, role) \
           or (AXUtilities.is_dialog(obj, role) and not AXUtilities.is_message_dialog(obj)):
            minimumWords = 3

        labels = self._script.utilities.unrelatedLabels(obj, visibleOnly, minimumWords)
        for label in labels:
            name = self._generateName(label, **args)
            if name and len(name[0]) == 1 and AXUtilities.is_math_related(obj):
                charname = mathsymbols.getCharacterName(name[0])
                if charname:
                    name[0] = charname
            result.extend(name)
        if result:
            result.extend(self.voice(DEFAULT, obj=obj, **args))
        return result

    #####################################################################
    #                                                                   #
    # State information                                                 #
    #                                                                   #
    #####################################################################

    def _generateCheckedState(self, obj, **args):
        """Returns an array of strings for use by speech and braille that
        represent the checked state of the object.  This is typically
        for check boxes. [[[WDW - should we return an empty array if
        we can guarantee we know this thing is not checkable?]]]
        """
        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText'):
            return []

        result = generator.Generator._generateCheckedState(self, obj, **args)
        if result:
            result.extend(self.voice(STATE, obj=obj, **args))
        return result

    def _generateExpandableState(self, obj, **args):
        """Returns an array of strings for use by speech and braille that
        represent the expanded/collapsed state of an object, such as a
        tree node. If the object is not expandable, an empty array
        will be returned.
        """
        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText'):
            return []

        result = generator.Generator._generateExpandableState(self, obj, **args)
        if result:
            result.extend(self.voice(STATE, obj=obj, **args))
        return result

    def _generateCheckedStateIfCheckable(self, obj, **args):
        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText'):
            return []

        result = super()._generateCheckedStateIfCheckable(obj, **args)
        if result:
            result.extend(self.voice(STATE, obj=obj, **args))
        return result

    def _generateMenuItemCheckedState(self, obj, **args):
        """Returns an array of strings for use by speech and braille that
        represent the checked state of the menu item, only if it is
        checked. Otherwise, and empty array will be returned.
        """
        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText'):
            return []

        result = generator.Generator.\
            _generateMenuItemCheckedState(self, obj, **args)
        if result:
            result.extend(self.voice(STATE, obj=obj, **args))
        return result

    def _generateMultiselectableState(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the multiselectable state of
        the object.  This is typically for list boxes. If the object
        is not multiselectable, an empty array will be returned.
        """
        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText'):
            return []

        result = super()._generateMultiselectableState(obj, **args)
        if result:
            result.extend(self.voice(STATE, obj=obj, **args))
        return result

    def _generateRadioState(self, obj, **args):
        """Returns an array of strings for use by speech and braille that
        represent the checked state of the object.  This is typically
        for check boxes. [[[WDW - should we return an empty array if
        we can guarantee we know this thing is not checkable?]]]
        """
        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText'):
            return []

        result = generator.Generator._generateRadioState(self, obj, **args)
        if result:
            result.extend(self.voice(STATE, obj=obj, **args))
        return result

    def _generateSwitchState(self, obj, **args):
        """Returns an array of strings indicating the on/off state of obj."""
        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText'):
            return []

        result = generator.Generator._generateSwitchState(self, obj, **args)
        if result:
            result.extend(self.voice(STATE, obj=obj, **args))
        return result

    def _generateToggleState(self, obj, **args):
        """Returns an array of strings for use by speech and braille that
        represent the checked state of the object.  This is typically
        for check boxes. [[[WDW - should we return an empty array if
        we can guarantee we know this thing is not checkable?]]]
        """
        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText'):
            return []

        result = generator.Generator._generateToggleState(self, obj, **args)
        if result:
            result.extend(self.voice(STATE, obj=obj, **args))
        return result

    #####################################################################
    #                                                                   #
    # Link information                                                  #
    #                                                                   #
    #####################################################################

    def _generateLinkInfo(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the protocol of the URI of
        the link associated with obj.
        """
        result = []
        # Get the URI for the link of interest and parse it. The parsed
        # URI is returned as a tuple containing six components:
        # scheme://netloc/path;parameters?query#fragment.
        #
        link_uri = AXHypertext.get_link_uri(obj)
        if not link_uri:
            # [[[TODO - JD: For some reason, this is failing for certain
            # links. The current whereAmI code says, "It might be an anchor.
            # Try to speak the text." and passes things off to whereAmI's
            # _speakText method. That won't work in the new world order.
            # Therefore, for now, I will hack in some code to do that
            # work here so that the before and after end results match.]]]
            #
            result.extend(self._generateLabel(obj))
            result.extend(self._generateRoleName(obj))
            result.append(self._script.utilities.displayedText(obj))
        else:
            link_uri_info = urllib.parse.urlparse(link_uri)
            if link_uri_info[0] in ["ftp", "ftps", "file"]:
                fileName = link_uri_info[2].split('/')
                result.append(messages.LINK_TO_FILE \
                              % {"uri" : link_uri_info[0],
                                 "file" : fileName[-1]})
            else:
                linkOutput = messages.LINK_WITH_PROTOCOL % link_uri_info[0]
                text = self._script.utilities.displayedText(obj)
                isVisited = AXUtilities.is_visited(obj)
                if not isVisited:
                    linkOutput = messages.LINK_WITH_PROTOCOL % link_uri_info[0]
                else:
                    linkOutput = messages.LINK_WITH_PROTOCOL_VISITED % link_uri_info[0]
                if not text:
                    # If there's no text for the link, expose part of the
                    # URI to the user.
                    #
                    text = AXHypertext.get_link_basename(obj)
                if text:
                    linkOutput += " " + text
                result.append(linkOutput)
                child = AXObject.get_child(obj, 0)
                if AXUtilities.is_image(child):
                    result.extend(self._generateRoleName(child))
        if result:
            result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    def _generateSiteDescription(self, obj, **args):
        if not self._script.utilities.inDocumentContent(obj):
            return []

        link_uri = AXHypertext.get_link_uri(obj)
        if not link_uri:
            return []

        link_uri_info = urllib.parse.urlparse(link_uri)
        doc_uri = AXDocument.get_uri(self._script.utilities.documentFrame())
        if not doc_uri:
            return []

        result = []
        doc_uri_info = urllib.parse.urlparse(doc_uri)
        if link_uri_info[1] == doc_uri_info[1]:
            if link_uri_info[2] == doc_uri_info[2]:
                result.append(messages.LINK_SAME_PAGE)
            else:
                result.append(messages.LINK_SAME_SITE)
        else:
            linkdomain = link_uri_info[1].split('.')
            docdomain = doc_uri_info[1].split('.')
            if len(linkdomain) > 1 and len(docdomain) > 1  \
               and linkdomain[-1] == docdomain[-1]  \
               and linkdomain[-2] == docdomain[-2]:
                result.append(messages.LINK_SAME_SITE)
            else:
                result.append(messages.LINK_DIFFERENT_SITE)

        if result:
            result.extend(self.voice(SYSTEM, obj=obj, **args))

        return result

    def _generateFileSize(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the size (Content-length) of
        the file pointed to by the URI of the link associated with
        obj.
        """
        result = []
        sizeString = ""
        uri = AXHypertext.get_link_uri(obj)
        if not uri:
            return result
        try:
            x = urllib.request.urlopen(uri)
            try:
                sizeString = x.info()['Content-length']
            except KeyError:
                pass
        except (ValueError, urllib.error.URLError, OSError):
            pass
        if sizeString:
            size = int(sizeString)
            if size < 10000:
                result.append(messages.fileSizeBytes(size))
            elif size < 1000000:
                result.append(messages.FILE_SIZE_KB % (float(size) * .001))
            elif size >= 1000000:
                result.append(messages.FILE_SIZE_MB % (float(size) * .000001))
        if result:
            result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    #####################################################################
    #                                                                   #
    # Image information                                                 #
    #                                                                   #
    #####################################################################

    def _generateImage(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the image on the object, if
        it exists.  Otherwise, an empty array is returned.
        """

        if not AXObject.supports_image(obj):
            return []

        args['role'] = Atspi.Role.IMAGE
        return self.generate(obj, **args)

    #####################################################################
    #                                                                   #
    # Table interface information                                       #
    #                                                                   #
    #####################################################################

    def _generateColumnHeader(self, obj, **args):
        if self._script.inSayAll():
            return []

        result = super()._generateColumnHeader(obj, **args)
        if result:
            result.extend(self.voice(DEFAULT, obj=obj, **args))

        return result

    def _generateRowHeader(self, obj, **args):
        if self._script.inSayAll():
            return []

        result = super()._generateRowHeader(obj, **args)
        if result:
            result.extend(self.voice(DEFAULT, obj=obj, **args))

        return result

    def _generateSortOrder(self, obj, **args):
        result = super()._generateSortOrder(obj, **args)
        if result:
            result.extend(self.voice(SYSTEM, obj=obj, **args))

        return result

    def _generateNewRowHeader(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the row header for an object
        that is in a table, if it exists and if it is different from
        the previous row header.  Otherwise, an empty array is
        returned.  The previous row header is determined by looking at
        the row header for the 'priorObj' attribute of the args
        dictionary.  The 'priorObj' is typically set by Orca to be the
        previous object with focus.
        """

        if not self._script.utilities.cellRowChanged(obj, args.get('priorObj')):
            return []

        if args.get('readingRow'):
            return []

        if not settings_manager.get_manager().get_setting('speakCellHeaders'):
            return []

        args['newOnly'] = True
        return self._generateRowHeader(obj, **args)

    def _generateNewColumnHeader(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the column header for an object
        that is in a table, if it exists and if it is different from
        the previous column header.  Otherwise, an empty array is
        returned.  The previous column header is determined by looking
        at the column header for the 'priorObj' attribute of the args
        dictionary.  The 'priorObj' is typically set by Orca to be the
        previous object with focus.
        """

        if not self._script.utilities.cellColumnChanged(obj, args.get('priorObj')):
            return []

        if args.get('readingRow'):
            return []

        if not settings_manager.get_manager().get_setting('speakCellHeaders'):
            return []

        args['newOnly'] = True
        return self._generateColumnHeader(obj, **args)

    def _generateRealTableCell(self, obj, **args):
        """Orca has a feature to automatically read an entire row of a table
        as the user arrows up/down the roles.  This leads to complexity in
        the code.  This method is used to return an array of strings
        (and possibly voice and audio specifications) for a single table
        cell itself.  The string, 'blank', is added for empty cells.
        """
        result = []
        oldRole = self._overrideRole('REAL_ROLE_TABLE_CELL', args)
        result.extend(self.generate(obj, **args))
        self._restoreRole(oldRole, args)
        if not (result and result[0]) \
           and settings_manager.get_manager().get_setting('speakBlankLines') \
           and not args.get('readingRow', False) \
           and args.get('formatType') != 'ancestor':
            result.append(messages.BLANK)
            if result:
                result.extend(self.voice(DEFAULT, obj=obj, **args))

        return result

    def _generateUnselectedStateIfSelectable(self, obj, **args):
        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText'):
            return []

        if args.get('inMouseReview'):
            return []

        if not obj:
            return []

        if not AXObject.supports_selection(AXObject.get_parent(obj)):
            return []

        if AXUtilities.is_selected(obj):
            return []

        result = [object_properties.STATE_UNSELECTED_LIST_ITEM]
        result.extend(self.voice(STATE, obj=obj, **args))

        return result

    def _generateUnselectedCell(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) if this is an icon within an layered pane or a
        table cell within a table or a tree table and the item is
        focused but not selected.  Otherwise, an empty array is
        returned.  [[[WDW - I wonder if this string should be moved to
        settings.py.]]]
        """
        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText'):
            return []

        if args.get('inMouseReview'):
            return []

        if not obj:
            return []

        parent = AXObject.get_parent(obj)
        if not AXObject.supports_selection(parent):
            return []

        if AXUtilities.is_selected(obj):
            return []

        if AXUtilities.is_text(obj):
            return []

        table = AXTable.get_table(obj)
        if table:
            if input_event_manager.get_manager().last_event_was_left_or_right():
                return []
            if self._script.utilities.isLayoutOnly(table):
                return []
        elif AXUtilities.is_layered_pane(parent):
            if obj in self._script.utilities.selectedChildren(parent):
                return []
        else:
            return []

        result = [object_properties.STATE_UNSELECTED_TABLE_CELL]
        result.extend(self.voice(STATE, obj=obj, **args))

        return result

    def _generateNewColumn(self, obj, **args):
        if not self._script.utilities.cellColumnChanged(obj):
            return []

        if args.get('readingRow'):
            return []

        if not settings_manager.get_manager().get_setting('speakCellCoordinates'):
            return []

        return self._generateColumn(obj, **args)

    def _generateColumn(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) reflecting the column number of a cell.
        """
        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText'):
            return []

        col = AXTable.get_cell_coordinates(obj, find_cell=True)[1]
        if col == -1:
            return []

        result = [messages.TABLE_COLUMN % (col + 1)]
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    def _generateNewRow(self, obj, **args):
        if not self._script.utilities.cellRowChanged(obj):
            return []

        if args.get('readingRow'):
            return []

        if not settings_manager.get_manager().get_setting('speakCellCoordinates'):
            return []

        return self._generateRow(obj, **args)

    def _generateRow(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) reflecting the row number of a cell.
        """
        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText'):
            return []

        row = AXTable.get_cell_coordinates(obj, find_cell=True)[0]
        if row == -1:
            return []

        result = [messages.TABLE_ROW % (row + 1)]
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    def _generateColumnAndRow(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) reflecting the position of the cell in terms
        of its column number, the total number of columns, its row,
        and the total number of rows.
        """
        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText'):
            return []

        row, col = AXTable.get_cell_coordinates(obj, find_cell=True)
        if row == -1 or col == -1:
            return []

        table = AXTable.get_table(obj)
        if table is None:
            return []

        result = []
        rows = AXTable.get_row_count(table)
        columns = AXTable.get_column_count(table)

        result.append(messages.TABLE_COLUMN_DETAILED % {"index" : (col + 1), "total" : columns})
        result.append(messages.TABLE_ROW_DETAILED % {"index" : (row + 1), "total" : rows})
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    def _generateEndOfTableIndicator(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) indicating that this cell is the last cell
        in the table.
        """
        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText'):
            return []

        if settings_manager.get_manager().get_setting('speechVerbosityLevel') \
           != settings.VERBOSITY_LEVEL_VERBOSE:
            return []

        if AXTable.is_last_cell(obj):
            result = [messages.TABLE_END]
            result.extend(self.voice(SYSTEM, obj=obj, **args))
            return result

        return []

    #####################################################################
    #                                                                   #
    # Text interface information                                        #
    #                                                                   #
    #####################################################################

    def _generateCurrentLineText(self, obj, **args):
        """Returns an array of strings for use by speech and braille
        that represents the current line of text, if
        this is a text object.  [[[WDW - consider returning an empty
        array if this is not a text object.]]]
        """

        if args.get('inMouseReview') \
           and AXUtilities.is_editable(obj):
            return []

        result = self._generateSubstring(obj, **args)
        if result and result[0]:
            return result

        text, startOffset = AXText.get_line_at_offset(obj)[0:2]
        if text == '\n' and settings_manager.get_manager().get_setting('speakBlankLines') \
           and not self._script.inSayAll() and args.get('total', 1) == 1 \
           and args.get('formatType') != 'ancestor':
            result = [messages.BLANK]
            result.extend(self.voice(string=text, obj=obj, **args))
            return result

        result = []
        endOffset = startOffset + len(text)
        split = self._script.utilities.splitSubstringByLanguage(obj, startOffset, endOffset)
        for start, end, string, language, dialect in split:
            string = string.replace(self._script.EMBEDDED_OBJECT_CHARACTER, "")
            if not string:
                continue
            args["language"], args["dialect"] = language, dialect
            if "string" in args:
                msg = f"INFO: Found existing string '{args.get('string')}'; using '{string}'"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                args.pop("string")

            voice = self.voice(string=string, obj=obj, **args)
            string = self._script.utilities.adjustForLinks(obj, string, start)
            rv = [self._script.utilities.adjustForRepeats(string)]
            rv.extend(voice)

            # TODO - JD: speech.speak() has a bug which causes a list of utterances to
            # be presented before a string+voice pair that comes first. Until we can
            # fix speak() properly, we'll avoid triggering it here.
            # result.append(rv)
            result.extend(rv)

        return result

    def _generateDisplayedText(self, obj, **args):
        result = self._generateSubstring(obj, **args)
        if result and result[0]:
            return result

        result = generator.Generator._generateDisplayedText(self, obj, **args)
        if not (result and result[0]):
            return []

        string = result[0].strip()
        if len(string) == 1 and AXUtilities.is_math_related(obj):
            charname = mathsymbols.getCharacterName(string)
            if charname != string:
                result[0] = charname

        result.extend(self.voice(DEFAULT, obj=obj, **args))
        return result

    def _getTextInformation(self, obj):
        """Returns [textContents, startOffset, endOffset, selected] as
        follows:

        A. if no text on the current line is selected, the current line
        B. if text is selected, the selected text
        C. if the current line is blank/empty, 'blank'

        Also sets up a 'textInformation' attribute in
        self._script.generator_cache to prevent computing this
        information repeatedly while processing a single event.
        """

        try:
            return self._script.generator_cache['textInformation']
        except Exception:
            pass

        textContents, startOffset, endOffset = self._script.utilities.allSelectedText(obj)
        selected = textContents != ""

        if not selected:
            line, startOffset, endOffset = AXText.get_line_at_offset(obj)
            if line:
                line = self._script.utilities.adjustForRepeats(line)
                textContents = line
            else:
                char = AXText.get_character_at_offset(obj)[0]
                if char == "\n":
                    textContents = char

        if self._script.utilities.shouldVerbalizeAllPunctuation(obj):
            textContents = self._script.utilities.verbalizeAllPunctuation(textContents)

        self._script.generator_cache['textInformation'] = \
            [textContents, startOffset, endOffset, selected]

        return self._script.generator_cache['textInformation']

    def _generateTextContent(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) containing the text content.  This requires
        _generateTextInformation to have been called prior to this method.
        """

        result = self._generateSubstring(obj, **args)
        if result:
            return result

        line = self._getTextInformation(obj)[0]
        if not line:
            return []

        result = [line]
        result.extend(self.voice(DEFAULT, obj=obj, **args))
        return result

    def _getAttributesStringAndOffsets(self, obj, offset, keys=["style", "weight", "underline"]):
        attrs, start, end = AXText.get_text_attributes_at_offset(obj, offset)
        if not attrs:
            return ""

        result = ""
        for key in keys:
            attribute = attrs.get(key)
            if not attribute:
                continue

            localizedKey = text_attribute_names.getTextAttributeName(key, self._script)
            localizedValue = text_attribute_names.getTextAttributeName(attribute, self._script)
            if key == "weight":
                if int(attribute) > 400:
                    result += f" {messages.BOLD}"
            elif key == "underline":
                if attribute != "none":
                    result += f" {localizedKey}"
            elif key == "style":
                if attribute != "normal":
                    result += f" {localizedValue}"
            else:
                result += " "
                result += (localizedKey + " " + localizedValue)

        if AXHypertext.get_all_links_in_range(obj, offset, offset + 1):
            result += f" {messages.LINK}"

        return result, start, end

    def _generateTextContentWithAttributes(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) containing the text content, obtained from the
        'textInformation' value, with character attribute information
        mixed in.  This requires _generateTextInformation to have been
        called prior to this method.
        """

        [line, startOffset, endOffset, selected] = self._getTextInformation(obj)
        newLine = ""
        textOffset = startOffset
        while textOffset < endOffset:
            attribs, start, end = self._getAttributesStringAndOffsets(obj, textOffset)
            newLine += f" {attribs} {AXText.get_substring(obj, start, end)}"
            textOffset = end

        attribs = self._getAttributesStringAndOffsets(obj, startOffset, ["paragraph-style"])[0]
        if attribs:
            newLine += f" {attribs}"

        result = [newLine]
        result.extend(self.voice(DEFAULT, obj=obj, **args))
        return result

    def _generateAnyTextSelection(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that says if any of the text for the entire
        object is selected. [[[WDW - I wonder if this string should be
        moved to settings.py.]]]
        """
        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText'):
            return []

        if not AXText.has_selected_text(obj):
            return []

        result = [messages.TEXT_SELECTED]
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    def _generateAllTextSelection(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that says if all the text for the entire
        object is selected. [[[WDW - I wonder if this string should be
        moved to settings.py.]]]
        """
        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText'):
            return []

        if not AXText.is_all_text_selected(obj):
            return []

        result = [messages.TEXT_SELECTED]
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    def _generateSubstring(self, obj, **args):
        result = super()._generateSubstring(obj, **args)
        if not (result and result[0]):
            return []

        result.extend(self.voice(DEFAULT, obj=obj, **args))
        if result[0] in ['\n', ''] \
           and settings_manager.get_manager().get_setting('speakBlankLines') \
           and not self._script.inSayAll() and args.get('total', 1) == 1 \
           and args.get('formatType') != 'ancestor':
            result[0] = messages.BLANK

        if self._script.utilities.shouldVerbalizeAllPunctuation(obj):
            result[0] = self._script.utilities.verbalizeAllPunctuation(result[0])

        return result

    def _generateTextIndentation(self, obj, **args):
        """Speaks a summary of the number of spaces and/or tabs at the
        beginning of the given line.

        Arguments:
        - obj: the text object.
        """

        if not settings_manager.get_manager().get_setting('enableSpeechIndentation'):
            return []

        line = AXText.get_line_at_offset(obj)[0]
        description = self._script.utilities.indentationDescription(line)
        if not description:
            return []

        result = [description]
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    def _generateNestingLevel(self, obj, **args):
        result = super()._generateNestingLevel(obj, **args)
        if result:
            result.extend(self.voice(SYSTEM, obj=obj, **args))

        return result

    #####################################################################
    #                                                                   #
    # Tree interface information                                        #
    #                                                                   #
    #####################################################################

    def _generateNewNodeLevel(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represents the tree node level of the
        object, or an empty array if the object is not a tree node or
        if the node level is not different from the 'priorObj'
        'priorObj' attribute of the args dictionary.  The 'priorObj'
        is typically set by Orca to be the previous object with
        focus.
        """
        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText'):
            return []

        result = []
        oldLevel = self._script.utilities.nodeLevel(args.get('priorObj', None))
        newLevel = self._script.utilities.nodeLevel(obj)
        if (oldLevel != newLevel) and (newLevel >= 0):
            result.extend(self._generateNodeLevel(obj, **args))
            result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    #####################################################################
    #                                                                   #
    # Value interface information                                       #
    #                                                                   #
    #####################################################################

    def _generateValue(self, obj, **args):
        result = super()._generateValue(obj, **args)
        if result:
            result.extend(self.voice(DEFAULT, obj=obj, **args))

        return result

    def _generatePercentage(self, obj, **args ):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represents the percentage value of the
        object.  This is typically for progress bars. [[[WDW - we
        should consider returning an empty array if there is no value.
        """
        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText'):
            return []

        percentValue = AXValue.get_value_as_percent(obj)
        if percentValue is not None:
            result = [messages.percentage(percentValue)]
            result.extend(self.voice(SYSTEM, obj=obj, **args))
            return result

        return []

    #####################################################################
    #                                                                   #
    # Hierarchy and related dialog information                          #
    #                                                                   #
    #####################################################################

    def _generateNewRadioButtonGroup(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represents the radio button group label
        of the object, or an empty array if the object has no such
        label or if the radio button group is not different from the
        'priorObj' 'priorObj' attribute of the args dictionary.  The
        'priorObj' is typically set by Orca to be the previous object
        with focus.
        """

        if not AXUtilities.is_radio_button(obj):
            return []

        result = super()._generateRadioButtonGroup(obj, **args)
        if not result:
            return []

        result.extend(self.voice(DEFAULT, obj=obj, **args))
        priorObj = args.get('priorObj', None)
        if not AXUtilities.is_radio_button(priorObj):
            return result

        # TODO - JD: We need other ways to determine group membership. Not all
        # implementations expose the member-of relation. Gtk3 does. Others are TBD.
        members = AXObject.get_relation_targets(obj, Atspi.RelationType.MEMBER_OF)
        if priorObj not in members:
            return result

        return []

    def _generateTermValueCount(self, obj, **args):
        count = self._script.utilities.getValueCountForTerm(obj)
        # If we have a simple 1-term, 1-value situation, this announcment is chatty.
        if count in (-1, 1):
            return []

        result = [messages.valueCountForTerm(count)]
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    def _generateNumberOfChildren(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represents the number of children the
        object has.  [[[WDW - can we always return an empty array if
        this doesn't apply?]]] [[[WDW - I wonder if this string should
        be moved to settings.py.]]]
        """

        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText') \
           or settings_manager.get_manager().get_setting('speechVerbosityLevel') \
               == settings.VERBOSITY_LEVEL_BRIEF:
            return []

        result = []
        childNodes = self._script.utilities.childNodes(obj)
        children = len(childNodes)
        if children:
            result.append(messages.itemCount(children))
            result.extend(self.voice(SYSTEM, obj=obj, **args))
            return result

        role = args.get("role")
        if AXUtilities.is_list(obj, role) or AXUtilities.is_list_box(obj, role):
            children = [x for x in AXObject.iter_children(obj, AXUtilities.is_list_item)]
            setsize = len(children)
            if not setsize:
                return []

            result = [messages.listItemCount(setsize)]
            result.extend(self.voice(SYSTEM, obj=obj, **args))

        return result

    def _generateNoShowingChildren(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that says if this object has no showing
        children (e.g., it's an empty table or list).  object has.
        [[[WDW - can we always return an empty array if this doesn't
        apply?]]] [[[WDW - I wonder if this string should be moved to
        settings.py.]]]
        """
        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText'):
            return []

        result = []
        hasItems = any(True for _ in AXObject.iter_children(obj, AXUtilities.is_showing))
        if not hasItems:
            result.append(messages.ZERO_ITEMS)
            result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    def _generateNoChildren(self, obj, **args ):
        """Returns an array of strings (and possibly voice and audio
        specifications) that says if this object has no children at
        all (e.g., it's an empty table or list).  object has.  [[[WDW
        - can we always return an empty array if this doesn't
        apply?]]] [[[WDW - I wonder if this string should be moved to
        settings.py.]]]
        """
        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText'):
            return []

        result = []
        if not AXObject.get_child_count(obj):
            result.append(messages.ZERO_ITEMS)
            result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    def _generateFocusedItem(self, obj, **args):
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
        for item in map(self._generateName, items):
            result.extend(item)

        return result

    def _generateSelectedItemCount(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) indicating how many items are selected in this
        and the position of the current item. This object will be an icon
        panel or a layered pane.
        """

        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText'):
            return []

        container = obj
        if not AXObject.supports_selection(container):
            container = AXObject.get_parent(obj)
            if not AXObject.supports_selection(container):
                return []

        result = []
        childCount = AXObject.get_child_count(container)
        selectedCount = len(self._script.utilities.selectedChildren(container))
        result.append(messages.selectedItemsCount(selectedCount, childCount))
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        result.append(object_properties.ICON_INDEX_SPEECH \
                      % {"index" : AXObject.get_index_in_parent(obj) + 1,
                         "total" : childCount})
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    def _generateSelectedItems(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) containing the names of all the selected items.
        This object will be an icon panel or a layered pane.
        """

        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText'):
            return []

        container = obj
        if not AXObject.supports_selection(container):
            container = AXObject.get_parent(obj)
            if not AXObject.supports_selection(container):
                return []

        selectedItems = self._script.utilities.selectedChildren(container)
        return list(map(self._generateLabelAndName, selectedItems))

    def generateSelectedItems(self, obj, **args):
        return self._generateSelectedItems(obj, **args)

    def _generateUnfocusedDialogCount(self, obj,  **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that says how many unfocused alerts and
        dialogs are associated with the application for this object.
        [[[WDW - I wonder if this string should be moved to
        settings.py.]]]
        """
        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText'):
            return []

        result = []
        # If this application has more than one unfocused alert or
        # dialog window, then speak '<m> unfocused dialogs'
        # to let the user know.
        #
        try:
            alertAndDialogCount = \
                self._script.utilities.unfocusedAlertAndDialogCount(obj)
        except Exception:
            alertAndDialogCount = 0
        if alertAndDialogCount > 0:
            result.append(messages.dialogCountSpeech(alertAndDialogCount))
            result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    def _getEnabledAndDisabledContextRoles(self):
        allRoles = [Atspi.Role.BLOCK_QUOTE,
                    Atspi.Role.CONTENT_DELETION,
                    Atspi.Role.CONTENT_INSERTION,
                    Atspi.Role.MARK,
                    Atspi.Role.SUGGESTION,
                    'ROLE_DPUB_LANDMARK',
                    'ROLE_DPUB_SECTION',
                    Atspi.Role.DESCRIPTION_LIST,
                    'ROLE_FEED',
                    Atspi.Role.FORM,
                    Atspi.Role.LANDMARK,
                    Atspi.Role.LIST,
                    Atspi.Role.PANEL,
                    'ROLE_REGION',
                    Atspi.Role.TABLE,
                    Atspi.Role.TOOL_TIP]

        enabled, disabled = [], []
        if self._script.inSayAll():
            if settings_manager.get_manager().get_setting('sayAllContextBlockquote'):
                enabled.append(Atspi.Role.BLOCK_QUOTE)
            if settings_manager.get_manager().get_setting('sayAllContextLandmark'):
                enabled.extend([Atspi.Role.LANDMARK, 'ROLE_DPUB_LANDMARK'])
            if settings_manager.get_manager().get_setting('sayAllContextList'):
                enabled.append(Atspi.Role.LIST)
                enabled.append(Atspi.Role.DESCRIPTION_LIST)
                enabled.append('ROLE_FEED')
            if settings_manager.get_manager().get_setting('sayAllContextPanel'):
                enabled.extend([Atspi.Role.PANEL,
                                Atspi.Role.TOOL_TIP,
                                Atspi.Role.CONTENT_DELETION,
                                Atspi.Role.CONTENT_INSERTION,
                                Atspi.Role.MARK,
                                Atspi.Role.SUGGESTION,
                                'ROLE_DPUB_SECTION'])
            if settings_manager.get_manager().get_setting('sayAllContextNonLandmarkForm'):
                enabled.append(Atspi.Role.FORM)
            if settings_manager.get_manager().get_setting('sayAllContextTable'):
                enabled.append(Atspi.Role.TABLE)
        else:
            if settings_manager.get_manager().get_setting('speakContextBlockquote'):
                enabled.append(Atspi.Role.BLOCK_QUOTE)
            if settings_manager.get_manager().get_setting('speakContextLandmark'):
                enabled.extend([Atspi.Role.LANDMARK, 'ROLE_DPUB_LANDMARK', 'ROLE_REGION'])
            if settings_manager.get_manager().get_setting('speakContextList'):
                enabled.append(Atspi.Role.LIST)
                enabled.append(Atspi.Role.DESCRIPTION_LIST)
                enabled.append('ROLE_FEED')
            if settings_manager.get_manager().get_setting('speakContextPanel'):
                enabled.extend([Atspi.Role.PANEL,
                                Atspi.Role.TOOL_TIP,
                                Atspi.Role.CONTENT_DELETION,
                                Atspi.Role.CONTENT_INSERTION,
                                Atspi.Role.MARK,
                                Atspi.Role.SUGGESTION,
                                'ROLE_DPUB_SECTION'])
            if settings_manager.get_manager().get_setting('speakContextNonLandmarkForm'):
                enabled.append(Atspi.Role.FORM)
            if settings_manager.get_manager().get_setting('speakContextTable'):
                enabled.append(Atspi.Role.TABLE)

        disabled = list(set(allRoles).symmetric_difference(enabled))
        return enabled, disabled

    def _generateLeaving(self, obj, **args):
        if not args.get('leaving'):
            return []

        role = args.get('role', AXObject.get_role(obj))
        enabled, disabled = self._getEnabledAndDisabledContextRoles()
        if not (role in enabled or self._script.utilities.isDetails(obj)):
            return []

        count = args.get('count', 1)

        result = []
        if self._script.utilities.isDetails(obj):
            result.append(messages.LEAVING_DETAILS)
        elif role == Atspi.Role.BLOCK_QUOTE:
            if count > 1:
                result.append(messages.leavingNBlockquotes(count))
            else:
                result.append(messages.LEAVING_BLOCKQUOTE)
        elif role in [Atspi.Role.LIST, Atspi.Role.DESCRIPTION_LIST] \
            and self._script.utilities.isDocumentList(obj):
            if count > 1:
                result.append(messages.leavingNLists(count))
            else:
                result.append(messages.LEAVING_LIST)
        elif role == 'ROLE_FEED':
            result.append(messages.LEAVING_FEED)
        elif role == Atspi.Role.PANEL:
            if AXUtilities.is_figure(obj):
                result.append(messages.LEAVING_FIGURE)
            elif self._script.utilities.isDocumentPanel(obj):
                result.append(messages.LEAVING_PANEL)
            else:
                result = ['']
        elif role == Atspi.Role.TABLE and self._script.utilities.isTextDocumentTable(obj):
            result.append(messages.LEAVING_TABLE)
        elif role == 'ROLE_DPUB_LANDMARK':
            if AXUtilities.is_dpub_acknowledgments(obj):
                result.append(messages.LEAVING_ACKNOWLEDGMENTS)
            elif AXUtilities.is_dpub_afterword(obj):
                result.append(messages.LEAVING_AFTERWORD)
            elif AXUtilities.is_dpub_appendix(obj):
                result.append(messages.LEAVING_APPENDIX)
            elif AXUtilities.is_dpub_bibliography(obj):
                result.append(messages.LEAVING_BIBLIOGRAPHY)
            elif AXUtilities.is_dpub_chapter(obj):
                result.append(messages.LEAVING_CHAPTER)
            elif AXUtilities.is_dpub_conclusion(obj):
                result.append(messages.LEAVING_CONCLUSION)
            elif AXUtilities.is_dpub_credits(obj):
                result.append(messages.LEAVING_CREDITS)
            elif AXUtilities.is_dpub_endnotes(obj):
                result.append(messages.LEAVING_ENDNOTES)
            elif AXUtilities.is_dpub_epilogue(obj):
                result.append(messages.LEAVING_EPILOGUE)
            elif AXUtilities.is_dpub_errata(obj):
                result.append(messages.LEAVING_ERRATA)
            elif AXUtilities.is_dpub_foreword(obj):
                result.append(messages.LEAVING_FOREWORD)
            elif AXUtilities.is_dpub_glossary(obj):
                result.append(messages.LEAVING_GLOSSARY)
            elif AXUtilities.is_dpub_index(obj):
                result.append(messages.LEAVING_INDEX)
            elif AXUtilities.is_dpub_introduction(obj):
                result.append(messages.LEAVING_INTRODUCTION)
            elif AXUtilities.is_dpub_pagelist(obj):
                result.append(messages.LEAVING_PAGELIST)
            elif AXUtilities.is_dpub_part(obj):
                result.append(messages.LEAVING_PART)
            elif AXUtilities.is_dpub_preface(obj):
                result.append(messages.LEAVING_PREFACE)
            elif AXUtilities.is_dpub_prologue(obj):
                result.append(messages.LEAVING_PROLOGUE)
            elif AXUtilities.is_dpub_toc(obj):
                result.append(messages.LEAVING_TOC)
        elif role == 'ROLE_DPUB_SECTION':
            if AXUtilities.is_dpub_abstract(obj):
                result.append(messages.LEAVING_ABSTRACT)
            elif AXUtilities.is_dpub_colophon(obj):
                result.append(messages.LEAVING_COLOPHON)
            elif AXUtilities.is_dpub_credit(obj):
                result.append(messages.LEAVING_CREDIT)
            elif AXUtilities.is_dpub_dedication(obj):
                result.append(messages.LEAVING_DEDICATION)
            elif AXUtilities.is_dpub_epigraph(obj):
                result.append(messages.LEAVING_EPIGRAPH)
            elif AXUtilities.is_dpub_example(obj):
                result.append(messages.LEAVING_EXAMPLE)
            elif AXUtilities.is_dpub_pullquote(obj):
                result.append(messages.LEAVING_PULLQUOTE)
            elif AXUtilities.is_dpub_qna(obj):
                result.append(messages.LEAVING_QNA)
        elif AXUtilities.is_landmark(obj):
            if AXUtilities.is_landmark_banner(obj):
                result.append(messages.LEAVING_LANDMARK_BANNER)
            elif AXUtilities.is_landmark_complementary(obj):
                result.append(messages.LEAVING_LANDMARK_COMPLEMENTARY)
            elif AXUtilities.is_landmark_contentinfo(obj):
                result.append(messages.LEAVING_LANDMARK_CONTENTINFO)
            elif AXUtilities.is_landmark_main(obj):
                result.append(messages.LEAVING_LANDMARK_MAIN)
            elif AXUtilities.is_landmark_navigation(obj):
                result.append(messages.LEAVING_LANDMARK_NAVIGATION)
            elif AXUtilities.is_landmark_region(obj):
                result.append(messages.LEAVING_LANDMARK_REGION)
            elif AXUtilities.is_landmark_search(obj):
                result.append(messages.LEAVING_LANDMARK_SEARCH)
            elif AXUtilities.is_landmark_form(obj):
                result.append(messages.LEAVING_FORM)
            else:
                result = ['']
        elif role == Atspi.Role.FORM:
            result.append(messages.LEAVING_FORM)
        elif role == Atspi.Role.TOOL_TIP:
            result.append(messages.LEAVING_TOOL_TIP)
        elif role == Atspi.Role.CONTENT_DELETION:
            result.append(messages.CONTENT_DELETION_END)
        elif role == Atspi.Role.CONTENT_INSERTION:
            result.append(messages.CONTENT_INSERTION_END)
        elif role == Atspi.Role.MARK:
            result.append(messages.CONTENT_MARK_END)
        elif role == Atspi.Role.SUGGESTION and not self._script.utilities.isInlineSuggestion(obj):
            result.append(messages.LEAVING_SUGGESTION)
        else:
            result = ['']
        if result:
            result.extend(self.voice(SYSTEM, obj=obj, **args))

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

        leaving = args.get('leaving')
        if leaving and args.get('priorObj'):
              priorObj = obj
              obj = args.get('priorObj')
        else:
              priorObj = args.get('priorObj')

        if priorObj and AXObject.is_dead(priorObj):
            return []

        if AXUtilities.is_tool_tip(priorObj):
            return []

        if priorObj and AXObject.get_parent(priorObj) == AXObject.get_parent(obj):
            return []

        if self._script.utilities.isTypeahead(priorObj):
            return []

        if AXUtilities.is_page_tab(obj):
            return []

        if AXUtilities.is_tool_tip(obj):
            return []

        commonAncestor = self._script.utilities.commonAncestor(priorObj, obj)
        if obj == commonAncestor:
            return []

        includeOnly = args.get('includeOnly', [])

        skipRoles = args.get('skipRoles', [])
        skipRoles.append(Atspi.Role.TREE_ITEM)
        enabled, disabled = self._getEnabledAndDisabledContextRoles()
        skipRoles.extend(disabled)

        stopAtRoles = args.get('stopAtRoles', [])
        stopAtRoles.extend([Atspi.Role.APPLICATION, Atspi.Role.MENU_BAR])

        stopAfterRoles = args.get('stopAfterRoles', [])
        stopAfterRoles.extend([Atspi.Role.TOOL_TIP])

        presentOnce = [Atspi.Role.BLOCK_QUOTE, Atspi.Role.LIST]

        presentCommonAncestor = False
        if commonAncestor and not leaving:
            commonRole = self._getAlternativeRole(commonAncestor)
            if commonRole in presentOnce:
                def pred(x):
                    return self._getAlternativeRole(x) == commonRole
                objAncestor = AXObject.find_ancestor(obj, pred)
                priorAncestor = AXObject.find_ancestor(priorObj, pred)
                objLevel = self._script.utilities.nestingLevel(objAncestor)
                priorLevel = self._script.utilities.nestingLevel(priorAncestor)
                presentCommonAncestor = objLevel != priorLevel

        ancestors, ancestorRoles = [], []
        parent = AXObject.get_parent_checked(obj)
        while parent:
            parentRole = self._getAlternativeRole(parent)
            if parentRole in stopAtRoles:
                break

            # TODO - JD: Create an alternative role for this.
            if parentRole in skipRoles and not self._script.utilities.isSpreadSheetTable(parent):
                pass
            elif includeOnly and parentRole not in includeOnly:
                pass
            elif self._script.utilities.isLayoutOnly(parent):
                pass
            elif self._script.utilities.isButtonWithPopup(parent):
                pass
            elif parent != commonAncestor or presentCommonAncestor:
                isRedundant = False
                for ancestor in ancestors:
                    if AXUtilities.is_redundant_object(ancestor, parent):
                        isRedundant = True
                        break
                if not isRedundant:
                    ancestors.append(parent)
                    ancestorRoles.append(parentRole)

            if parent == commonAncestor or parentRole in stopAfterRoles:
                break

            parent = AXObject.get_parent_checked(parent)

        presentedRoles = []
        for i, x in enumerate(ancestors):
            altRole = ancestorRoles[i]
            if altRole in presentOnce and altRole in presentedRoles:
                continue

            presentedRoles.append(altRole)
            count = ancestorRoles.count(altRole)
            self._overrideRole(altRole, args)
            result.append(
                self.generate(x, formatType='ancestor', role=altRole,
                              leaving=leaving, count=count, ancestorOf=obj, priorObj=priorObj))
            self._restoreRole(altRole, args)

        if not leaving:
            result.reverse()
        return result

    def _generateOldAncestors(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the text of the ancestors for
        the object being left."""

        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText'):
            return []

        if self._script.utilities.inFindContainer():
            return []

        priorObj = args.get('priorObj')
        if not priorObj or obj == priorObj or not AXObject.is_valid(priorObj):
            return []

        if AXUtilities.is_page_tab(obj):
            return []

        if AXObject.get_application(obj) != AXObject.get_application(priorObj) \
           or AXObject.find_ancestor(obj, lambda x: x == priorObj):
            return []

        frame, dialog = self._script.utilities.frameAndDialog(obj)
        if dialog:
            return []

        args['leaving'] = True
        args['includeOnly'] = [Atspi.Role.BLOCK_QUOTE,
                               Atspi.Role.DESCRIPTION_LIST,
                               Atspi.Role.FORM,
                               Atspi.Role.LANDMARK,
                               Atspi.Role.CONTENT_DELETION,
                               Atspi.Role.CONTENT_INSERTION,
                               Atspi.Role.MARK,
                               Atspi.Role.SUGGESTION,
                               'ROLE_DPUB_LANDMARK',
                               'ROLE_DPUB_SECTION',
                               'ROLE_FEED',
                               Atspi.Role.LIST,
                               Atspi.Role.PANEL,
                               'ROLE_REGION',
                               Atspi.Role.TABLE,
                               Atspi.Role.TOOL_TIP]

        result = []
        if AXUtilities.is_block_quote(priorObj):
            oldRole = self._getAlternativeRole(priorObj)
            self._overrideRole(oldRole, args)
            result.extend(self.generate(
                priorObj, role=oldRole, formatType='focused', leaving=True))
            self._restoreRole(oldRole, args)

        result.extend(self._generateAncestors(obj, **args))
        args.pop('leaving')
        args.pop('includeOnly')

        return result

    def _generateNewAncestors(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the text of the ancestors for
        the object.  This is typically used to present the context for
        an object (e.g., the names of the window, the panels, etc.,
        that the object is contained in).  If the 'priorObj' attribute
        of the args dictionary is set, only the differences in
        ancestry between the 'priorObj' and the current obj will be
        computed.  Otherwise, no ancestry will be computed.  The
        'priorObj' is typically set by Orca to be the previous object
        with focus.
        """

        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText'):
            return []

        if self._script.utilities.inFindContainer():
            return []

        priorObj = args.get('priorObj')
        if priorObj == obj:
            return []

        role = args.get('role', AXObject.get_role(obj))
        if role in [Atspi.Role.FRAME, Atspi.Role.WINDOW]:
            return []

        if role == Atspi.Role.MENU_ITEM and (not priorObj or AXUtilities.is_window(priorObj)):
            return []

        if priorObj is not None:
            return self._generateAncestors(obj, **args)

        frame, dialog = self._script.utilities.frameAndDialog(obj)
        topLevel = dialog or frame
        if AXUtilities.is_dialog_or_alert(topLevel):
            return self._generateAncestors(obj, **args)

        return []

    def generateContext(self, obj, **args):
        if args.get('priorObj') == obj:
            return []

        result = self._generateOldAncestors(obj, **args)
        result.append(self._generateNewAncestors(obj, **args))
        return result

    def _generateParentRoleName(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) containing the role name of the parent of obj.
        """
        if args.get('role', AXObject.get_role(obj)) == Atspi.Role.ICON \
           and args.get('formatType', None) \
               in ['basicWhereAmI', 'detailedWhereAmI']:
            return [object_properties.ROLE_ICON_PANEL]

        parent = AXObject.get_parent(obj)
        if AXUtilities.is_table_cell(parent) or AXUtilities.is_menu(parent):
            obj = parent
        return self._generateRoleName(AXObject.get_parent(obj))

    def _generatePositionInGroup(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the relative position of an
        object in a group.
        """
        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText'):
            return []

        # TODO - JD: We need other ways to determine group membership. Not all
        # implementations expose the member-of relation. Gtk3 does. Others are TBD.
        members = AXObject.get_relation_targets(
            obj, Atspi.RelationType.MEMBER_OF, AXUtilities.is_showing)
        if obj not in members:
            return []

        result = []

        # TODO - JD: We used to adjust the position on the basis of this particular
        # relation "tending to be given in the reverse order". But there's no reason
        # that should be the case. And doesn't always appear to be the case in Gtk3.
        # Until we sort out the position in group/list mess, try a more reliable
        # "adjustment."
        def cmp(x, y):
            return AXObject.get_index_in_parent(y) - AXObject.get_index_in_parent(x)

        members = sorted(members, key=functools.cmp_to_key(cmp))
        result.append(object_properties.GROUP_INDEX_SPEECH % {"index": members.index(obj) + 1,
                                                              "total": len(members)})
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    def _generatePositionInList(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the relative position of an
        object in a list.
        """

        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText') \
           or not (settings_manager.get_manager().get_setting('enablePositionSpeaking') \
                   or args.get('forceList', False)):
            return []

        if self._script.utilities.isTopLevelMenu(obj):
            return []

        if self._script.utilities.isEditableComboBox(obj):
            return []

        result = []
        position, total = self._script.utilities.getPositionAndSetSize(obj, **args)
        if position < 0:
            return []

        string = object_properties.GROUP_INDEX_SPEECH
        if total < 0:
            if not self._script.utilities.setSizeUnknown(obj):
                return []
            string = object_properties.GROUP_INDEX_TOTAL_UNKNOWN_SPEECH

        if total == 1 and AXUtilities.is_menu(obj):
            return []

        position += 1
        result.append(string % {"index": position, "total": total})
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    def _generateProgressBarIndex(self, obj, **args):
        if not args.get('isProgressBarUpdate') \
           or not self._shouldPresentProgressBarUpdate(obj, **args):
            return []

        result = []
        acc, updateTime, updateValue = self._getMostRecentProgressBarUpdate()
        if acc != obj:
            number, count = self.getProgressBarNumberAndCount(obj)
            result = [messages.PROGRESS_BAR_NUMBER % (number)]
            result.extend(self.voice(SYSTEM, obj=obj, **args))

        return result

    def _generateProgressBarValue(self, obj, **args):
        if args.get('isProgressBarUpdate') \
           and not self._shouldPresentProgressBarUpdate(obj, **args):
            return ['']

        result = []
        percent = AXValue.get_value_as_percent(obj)
        if percent is not None:
            result.append(messages.percentage(percent))
            result.extend(self.voice(SYSTEM, obj=obj, **args))

        return result

    def _getProgressBarUpdateInterval(self):
        interval = settings_manager.get_manager().get_setting('progressBarSpeechInterval')
        if interval is None:
            interval = super()._getProgressBarUpdateInterval()

        return int(interval)

    def _shouldPresentProgressBarUpdate(self, obj, **args):
        if not settings_manager.get_manager().get_setting('speakProgressBarUpdates'):
            return False

        return super()._shouldPresentProgressBarUpdate(obj, **args)

    def _generateStatusBar(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the status bar of a window.
        """

        if not AXUtilities.is_status_bar(obj):
            return []

        items = self._script.utilities.statusBarItems(obj)
        if not items or items == [obj]:
            return []

        result = []
        for child in items:
            if child == obj:
                continue

            childResult = self.generate(child, includeContext=False)
            if childResult:
                result.extend(childResult)
                if not isinstance(childResult[-1], Pause):
                    result.extend(self._generatePause(child, **args))

        return result

    def generateTitle(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the title of the window, obj.
        containing the object, along with information associated with
        any unfocused dialog boxes.
        """
        result = []
        frame, dialog = self._script.utilities.frameAndDialog(obj)
        if frame:
            frameResult = self._generateLabelAndName(frame)
            if not frameResult:
                frameResult = self._generateRoleName(frame)
            result.append(frameResult)

        if dialog:
            result.append(self._generateLabelAndName(dialog))

        alertAndDialogCount = self._script.utilities.unfocusedAlertAndDialogCount(obj)
        if alertAndDialogCount > 0:
            dialogs = [messages.dialogCountSpeech(alertAndDialogCount)]
            dialogs.extend(self.voice(DEFAULT, obj=obj, **args))
            result.append(dialogs)
        return result

    def _generateListBoxItemWidgets(self, obj, **args):
        if not AXUtilities.is_list_box(AXObject.get_parent(obj)):
            return []

        result = []
        widgets = AXUtilities.get_all_widgets(obj)
        for widget in widgets:
            result.append(self.generate(widget, includeContext=False))
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
        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText'):
            return []

        result = []
        [mnemonic, shortcut, accelerator] = \
            self._script.utilities.mnemonicShortcutAccelerator(obj)
        if accelerator:
            result.append(accelerator)
            result.extend(self.voice(SYSTEM, obj=obj, **args))

        return result

    def _generateMnemonic(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the mnemonic for the object, or
        an empty array if no mnemonic can be found.
        """
        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText'):
            return []

        result = []
        if settings_manager.get_manager().get_setting('enableMnemonicSpeaking') \
           or args.get('forceMnemonic', False):
            [mnemonic, shortcut, accelerator] = \
                self._script.utilities.mnemonicShortcutAccelerator(obj)
            if mnemonic:
                mnemonic = mnemonic[-1] # we just want a single character
            if not mnemonic and shortcut:
                mnemonic = shortcut
            if mnemonic:
                result = [mnemonic]
                result.extend(self.voice(SYSTEM, obj=obj, **args))

        return result

    def _generateTutorial(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the tutorial for the object."""

        if not settings_manager.get_manager().get_setting('enableTutorialMessages') \
           and not args.get('formatType', '').endswith('WhereAmI'):
            return []

        text = AXObject.get_help_text(obj)
        if not text:
            return []

        return [text, self.voice(SYSTEM, obj=obj, **args)]

    # Math

    def _generateMath(self, obj, **args):
        result = []
        children = [child for child in AXObject.iter_children(obj)]
        if not children and not AXUtilities.is_math(obj):
            children = [obj]

        for child in children:
            if AXUtilities.is_math_layout_only(child) and AXObject.get_child_count(child):
                result.extend(self._generateMath(child))
                continue

            oldRole = self._getAlternativeRole(child)
            self._overrideRole(oldRole, args)
            result.extend(self.generate(child, role=oldRole))
            self._restoreRole(oldRole, args)

        return result

    def _generateEnclosedEnclosures(self, obj, **args):
        strings = []
        enclosures = self._script.utilities.getMathEnclosures(obj)
        if 'actuarial' in enclosures:
            strings.append(messages.MATH_ENCLOSURE_ACTUARIAL)
        if 'box' in enclosures:
            strings.append(messages.MATH_ENCLOSURE_BOX)
        if 'circle' in enclosures:
            strings.append(messages.MATH_ENCLOSURE_CIRCLE)
        if 'longdiv' in enclosures:
            strings.append(messages.MATH_ENCLOSURE_LONGDIV)
        if 'radical' in enclosures:
            strings.append(messages.MATH_ENCLOSURE_RADICAL)
        if 'roundedbox' in enclosures:
            strings.append(messages.MATH_ENCLOSURE_ROUNDEDBOX)
        if 'horizontalstrike' in enclosures:
            strings.append(messages.MATH_ENCLOSURE_HORIZONTALSTRIKE)
        if 'verticalstrike' in enclosures:
            strings.append(messages.MATH_ENCLOSURE_VERTICALSTRIKE)
        if 'downdiagonalstrike' in enclosures:
            strings.append(messages.MATH_ENCLOSURE_DOWNDIAGONALSTRIKE)
        if 'updiagonalstrike' in enclosures:
            strings.append(messages.MATH_ENCLOSURE_UPDIAGONALSTRIKE)
        if 'northeastarrow' in enclosures:
            strings.append(messages.MATH_ENCLOSURE_NORTHEASTARROW)
        if 'bottom' in enclosures:
            strings.append(messages.MATH_ENCLOSURE_BOTTOM)
        if 'left' in enclosures:
            strings.append(messages.MATH_ENCLOSURE_LEFT)
        if 'right' in enclosures:
            strings.append(messages.MATH_ENCLOSURE_RIGHT)
        if 'top' in enclosures:
            strings.append(messages.MATH_ENCLOSURE_TOP)
        if 'phasorangle' in enclosures:
            strings.append(messages.MATH_ENCLOSURE_PHASOR_ANGLE)
        if 'madruwb' in enclosures:
            strings.append(messages.MATH_ENCLOSURE_MADRUWB)
        if not strings:
            tokens = ["SPEECH GENERATOR: Could not get enclosure message for", enclosures]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return []

        if len(strings) == 1:
            result = [messages.MATH_ENCLOSURE_ENCLOSED_BY % strings[0]]
        else:
            strings.insert(-1, messages.MATH_ENCLOSURE_AND)
            if len(strings) == 3:
                result = [messages.MATH_ENCLOSURE_ENCLOSED_BY % " ".join(strings)]
            else:
                result = [messages.MATH_ENCLOSURE_ENCLOSED_BY % ", ".join(strings)]

        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    def _generateFencedStart(self, obj, **args):
        fenceStart, fenceEnd = self._script.utilities.getMathFences(obj)
        if fenceStart:
            result = [mathsymbols.getCharacterName(fenceStart)]
            result.extend(self.voice(DEFAULT, obj=obj, **args))
            return result

        return []

    def _generateFencedContents(self, obj, **args):
        result = []
        separators = self._script.utilities.getMathFencedSeparators(obj)
        for x in range(len(separators), AXObject.get_child_count(obj)-1):
            separators.append(separators[-1])
        separators.append('')

        for i, child in enumerate(AXObject.iter_children(obj)):
            result.extend(self._generateMath(child, **args))
            separatorName = mathsymbols.getCharacterName(separators[i])
            result.append(separatorName)
            result.extend(self.voice(DEFAULT, obj=obj, **args))
            if separatorName:
                result.extend(self._generatePause(obj, **args))

        return result

    def _generateFencedEnd(self, obj, **args):
        fenceStart, fenceEnd = self._script.utilities.getMathFences(obj)
        if fenceEnd:
            result = [mathsymbols.getCharacterName(fenceEnd)]
            result.extend(self.voice(DEFAULT, obj=obj, **args))
            return result

        return []

    def _generateFractionStart(self, obj, **args):
        if AXUtilities.is_math_fraction_without_bar(obj):
            result = [messages.MATH_FRACTION_WITHOUT_BAR_START]
        else:
            result = [messages.MATH_FRACTION_START]
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    def _generateFractionNumerator(self, obj, **args):
        numerator = self._script.utilities.getMathNumerator(obj)
        if AXUtilities.is_math_layout_only(numerator):
            return self._generateMath(numerator)

        oldRole = self._getAlternativeRole(numerator)
        self._overrideRole(oldRole, args)
        result = self.generate(numerator, role=oldRole)
        self._restoreRole(oldRole, args)
        return result

    def _generateFractionDenominator(self, obj, **args):
        denominator = self._script.utilities.getMathDenominator(obj)
        if AXUtilities.is_math_layout_only(denominator):
            return self._generateMath(denominator)

        oldRole = self._getAlternativeRole(denominator)
        self._overrideRole(oldRole, args)
        result = self.generate(denominator, role=oldRole)
        self._restoreRole(oldRole, args)
        return result

    def _generateFractionLine(self, obj, **args):
        result = [messages.MATH_FRACTION_LINE]
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    def _generateFractionEnd(self, obj, **args):
        result = [messages.MATH_FRACTION_END]
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    def _generateRootStart(self, obj, **args):
        result = []
        if AXUtilities.is_math_square_root(obj):
            result = [messages.MATH_SQUARE_ROOT_OF]
        else:
            index = self._script.utilities.getMathRootIndex(obj)
            string = self._script.utilities.displayedText(index)
            if string == "2":
                result = [messages.MATH_SQUARE_ROOT_OF]
            elif string == "3":
                result = [messages.MATH_CUBE_ROOT_OF]
            elif string:
                result = [string]
                result.extend([messages.MATH_ROOT_OF])
            elif AXUtilities.is_math_layout_only(index):
                result = self._generateMath(index)
                result.extend([messages.MATH_ROOT_OF])
            else:
                oldRole = self._getAlternativeRole(index)
                self._overrideRole(oldRole, args)
                result.extend(self.generate(index, role=oldRole))
                self._restoreRole(oldRole, args)
                result.extend([messages.MATH_ROOT_OF])

        if result:
            result.extend(self.voice(SYSTEM, obj=obj, **args))

        return result

    def _generateRootBase(self, obj, **args):
        base = self._script.utilities.getMathRootBase(obj)
        if not base:
            return []

        if AXUtilities.is_math_square_root(obj) \
           or AXUtilities.is_math_token(base) \
           or AXUtilities.is_math_layout_only(base):
            return self._generateMath(base)

        result = [self._generatePause(obj, **args)]
        oldRole = self._getAlternativeRole(base)
        self._overrideRole(oldRole, args)
        result.extend(self.generate(base, role=oldRole))
        self._restoreRole(oldRole, args)

        return result

    def _generateRootEnd(self, obj, **args):
        result = [messages.MATH_ROOT_END]
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    def _generateScriptBase(self, obj, **args):
        base = self._script.utilities.getMathScriptBase(obj)
        if not base:
            return []

        return self._generateMath(base)

    def _generateScriptScript(self, obj, **args):
        if AXUtilities.is_math_layout_only(obj):
            return self._generateMath(obj)

        oldRole = self._getAlternativeRole(obj)
        self._overrideRole(oldRole, args)
        result = self.generate(obj, role=oldRole)
        self._restoreRole(oldRole, args)

        return result

    def _generateScriptSubscript(self, obj, **args):
        subscript = self._script.utilities.getMathScriptSubscript(obj)
        if not subscript:
            return []

        result = [messages.MATH_SUBSCRIPT]
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        result.extend(self._generateScriptScript(subscript))

        return result

    def _generateScriptSuperscript(self, obj, **args):
        superscript = self._script.utilities.getMathScriptSuperscript(obj)
        if not superscript:
            return []

        result = [messages.MATH_SUPERSCRIPT]
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        result.extend(self._generateScriptScript(superscript))

        return result

    def _generateScriptUnderscript(self, obj, **args):
        underscript = self._script.utilities.getMathScriptUnderscript(obj)
        if not underscript:
            return []

        result = [messages.MATH_UNDERSCRIPT]
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        result.extend(self._generateScriptScript(underscript))

        return result

    def _generateScriptOverscript(self, obj, **args):
        overscript = self._script.utilities.getMathScriptOverscript(obj)
        if not overscript:
            return []

        result = [messages.MATH_OVERSCRIPT]
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        result.extend(self._generateScriptScript(overscript))

        return result

    def _generateScriptPrescripts(self, obj, **args):
        result = []
        prescripts = self._script.utilities.getMathPrescripts(obj)
        for i, script in enumerate(prescripts):
            if AXUtilities.is_math_layout_only(script):
                continue
            if i % 2:
                rv = [messages.MATH_PRE_SUPERSCRIPT]
            else:
                rv = [messages.MATH_PRE_SUBSCRIPT]
            rv.extend(self.voice(SYSTEM, obj=obj, **args))
            rv.extend(self._generateScriptScript(script))
            result.append(rv)

        return result

    def _generateScriptPostscripts(self, obj, **args):
        result = []
        postscripts = self._script.utilities.getMathPostscripts(obj)
        for i, script in enumerate(postscripts):
            if AXUtilities.is_math_layout_only(script):
                continue
            if i % 2:
                rv = [messages.MATH_SUPERSCRIPT]
            else:
                rv = [messages.MATH_SUBSCRIPT]
            rv.extend(self.voice(SYSTEM, obj=obj, **args))
            rv.extend(self._generateScriptScript(script))
            result.append(rv)

        return result

    def _generateMathTableStart(self, obj, **args):
        if not AXObject.supports_table(obj):
            return []

        rows = AXTable.get_row_count(obj)
        columns = AXTable.get_column_count(obj)
        nestingLevel = self._script.utilities.getMathNestingLevel(obj)
        if nestingLevel > 0:
            result = [messages.mathNestedTableSize(rows, columns)]
        else:
            result = [messages.mathTableSize(rows, columns)]
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    def _generateMathTableRows(self, obj, **args):
        result = []
        for row in AXObject.iter_children(obj):
            oldRole = self._getAlternativeRole(row)
            self._overrideRole(oldRole, args)
            result.extend(self.generate(row, role=oldRole))
            self._restoreRole(oldRole, args)

        return result

    def _generateMathTableEnd(self, obj, **args):
        nestingLevel = self._script.utilities.getMathNestingLevel(obj)
        if nestingLevel > 0:
            result = [messages.MATH_NESTED_TABLE_END]
        else:
            result = [messages.MATH_TABLE_END]
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    #####################################################################
    #                                                                   #
    # Other things for prosody and voice selection                      #
    #                                                                   #
    #####################################################################

    def _generatePause(self, obj, **args):
        if not settings_manager.get_manager().get_setting('enablePauseBreaks') \
           or args.get('eliminatePauses', False):
            return []

        if settings_manager.get_manager().get_setting('verbalizePunctuationStyle') == \
           settings.PUNCTUATION_STYLE_ALL:
            return []

        return PAUSE

    def _generateLineBreak(self, obj, **args):
        return LINE_BREAK

    def voice(self, key=None, **args):
        """Returns an array containing a voice.  The key is a value
        to be used to look up the voice in the settings.py:voices
        dictionary. Other arguments can be passed in for future
        decision making.
        """

        voicename = voiceType.get(key) or voiceType.get(DEFAULT)
        voices = settings_manager.get_manager().get_setting('voices')
        voice = acss.ACSS(voices.get(voiceType.get(DEFAULT), {}))

        language = args.get('language')
        dialect = args.get('dialect', '')
        msg = (
            f"SPEECH GENERATOR: {key} voice requested with "
            f"language='{language}', dialect='{dialect}'"
        )
        debug.printMessage(debug.LEVEL_INFO, msg, True)

        # This is purely for debugging. The code needed to actually switch voices
        # does not yet exist due to some problems which need to be debugged and
        # fixed.
        checkVoicesForLanguage = False
        if language and checkVoicesForLanguage:
            server = speech.get_speech_server()
            server.shouldChangeVoiceForLanguage(language, dialect)

        if key in [None, DEFAULT]:
            string = args.get('string', '')
            obj = args.get('obj')
            if AXUtilities.is_link(obj):
                voice.update(voices.get(voiceType.get(HYPERLINK), {}))
            elif isinstance(string, str) and string.isupper() and string.strip().isalpha():
                voice.update(voices.get(voiceType.get(UPPERCASE), {}))
        else:
            override = voices.get(voicename)
            if override and override.get('established', True):
                voice.update(override)

        return [voice]

    def utterancesToString(self, utterances):
        string = ""
        for u in utterances:
            if isinstance(u, str):
                string += f" {u}"
            elif isinstance(u, Pause) and string and string[-1].isalnum():
                string += "."

        return string.strip()

#########################################################################################

    def _generate_default_prefix(self, obj, **args):
        """Provides the default/role-agnostic information to present before obj."""

        if args.get("includeContext") is False:
            return []

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generateDetailsFor(obj, **args)
        if format_type == "unfocused":
            return self._generateOldAncestors(obj, **args) + self._generateNewAncestors(obj, **args)
        return []

    def _generate_default_presentation(self, obj, **args):
        """Provides a default/role-agnostic presentation of obj."""

        result = self._generate_default_prefix(obj, **args)
        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return result

        result += self._generateLabelAndName(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateAvailability(obj, **args)
        result += self._generateMnemonic(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_default_suffix(self, obj, **args):
        """Provides the default/role-agnostic information to present after obj."""

        if args.get("includeContext") is False:
            return []

        format_type = args.get("formatType", "unfocused")
        if format_type == "focused":
            return []
        if format_type == "ancestor":
            return self._generateUnrelatedLabelsOrDescription(obj, **args)

        result = []
        if format_type.endswith("WhereAmI"):
            result += self._generateTutorial(obj, **args)
            if result and not isinstance(result[-1], Pause):
                result += self._generatePause(obj, **args)

        result += self._generateClickable(obj, **args)
        if result and not isinstance(result[-1], Pause):
            result += self._generatePause(obj, **args)
        result += self._generateHasDetails(obj, **args)
        result += self._generateDetailsFor(obj, **args)
        result += self._generateDescription(obj, **args)
        if result and not isinstance(result[-1], Pause):
            result += self._generatePause(obj, **args)
        result += self._generateHasPopup(obj, **args)
        if format_type == "unfocused":
            result += self._generateTutorial(obj, **args)

        return result

    def _generate_accelerator_label(self, obj, **args):
        """Generates speech for the accelerator-label role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_alert(self, obj, **args):
        """Generates speech for the alert role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateLabelAndName(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generateAlertText(obj, **args)
        return result

    def _generate_animation(self, obj, **args):
        """Generates speech for the animation role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_application(self, obj, **args):
        """Generates speech for the application role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_arrow(self, obj, **args):
        """Generates speech for the arrow role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_article(self, obj, **args):
        """Generates speech for the article role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generateLabelAndName(obj, **args)

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return result

        result += self._generatePause(obj, **args)
        result += self._generateCurrentLineText(obj, **args)
        result += self._generateAllTextSelection(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_article_in_feed(self, obj, **args):
        """Generates speech for the article role when the article is in a feed."""

        result = []
        result += self._generateLabelAndName(obj, **args)
        if not result:
            result += self._generateCurrentLineText(obj, **args)
        if not result:
            result += self._generateRoleName(obj, **args)
        result += self._generatePositionInList(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return self._generate_default_prefix(obj, **args) + result

    def _generate_audio(self, obj, **args):
        """Generates speech for the audio role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_autocomplete(self, obj, **args):
        """Generates speech for the autocomplete role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_block_quote(self, obj, **args):
        """Generates speech for the block-quote role."""

        result = []
        if args.get("priorObj") != obj:
            result += self._generate_default_prefix(obj, **args)
            result += self._generateRoleName(obj, **args)
            result += self._generatePause(obj, **args)
            result += self._generateNestingLevel(obj, **args)

        result += self._generateCurrentLineText(obj, **args)
        result += self._generateAllTextSelection(obj, **args)

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generateLeaving(obj, **args) or result

        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_calendar(self, obj, **args):
        """Generates speech for the calendar role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_canvas(self, obj, **args):
        """Generates speech for the canvas role."""

        result = self._generate_default_prefix(obj, **args)
        format_type = args.get("formatType", "unfocused")
        if format_type.endswith("WhereAmI"):
            result += self._generateParentRoleName(obj, **args)
            result += self._generatePause(obj, **args)

        result += self._generateLabelAndName(obj, **args)
        result += (self._generateImageDescription(obj, **args) \
            or self._generateRoleName(obj, **args))
        result += self._generatePause(obj, **args)

        if format_type.endswith("WhereAmI"):
            result += self._generateSelectedItemCount(obj, **args)
            result += self._generatePause(obj, **args)
            result += self._generateSelectedItems(obj, **args)
        else:
            result += self._generatePositionInList(obj, **args)

        result += self._generateUnselectedCell(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_caption(self, obj, **args):
        """Generates speech for the caption role."""

        result = []
        if self._generateSubstring(obj, **args):
            result += self._generateCurrentLineText(obj, **args)
        if not result:
            result += self._generateLabelAndName(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return self._generate_default_prefix(obj, **args) + result

    def _generate_chart(self, obj, **args):
        """Generates speech for the chart role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_check_box(self, obj, **args):
        """Generates speech for the check-box role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generateCheckedState(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        if format_type.endswith("WhereAmI"):
            result += self._generateNamedContainingPanel(obj, **args)

        result += self._generateLabelAndName(obj, **args)
        result += self._generateReadOnly(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateCheckedState(obj, **args)
        result += self._generateRequired(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generateInvalid(obj, **args)
        result += self._generateAvailability(obj, **args)
        result += self._generateMnemonic(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_check_menu_item(self, obj, **args):
        """Generates speech for the check-menu-item role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generateCheckedState(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        if format_type.endswith("WhereAmI"):
            result += self._generateAncestors(obj, **args)
            result += self._generatePause(obj, **args)

        result += self._generateLabelAndName(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateCheckedState(obj, **args)
        result += self._generateAvailability(obj, **args)
        result += self._generateMnemonic(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generateAccelerator(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generatePositionInList(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_color_chooser(self, obj, **args):
        """Generates speech for the color-chooser role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generateValue(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generateLabelAndName(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateValue(obj, **args)

        if format_type.endswith("WhereAmI"):
            result += self._generatePercentage(obj, **args)

        result += self._generateAccelerator(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_column_header(self, obj, **args):
        """Generates speech for the column-header role."""

        result = []
        format_type = args.get("formatType", "unfocused")
        if format_type != "focused" and self._generateSubstring(obj, **args):
            result += self._generateCurrentLineText(obj, **args)
        if not result:
            result += self._generateLabelAndName(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateSortOrder(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generateNewRow(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generateNewColumn(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return self._generate_default_prefix(obj, **args) + result

    def _generate_combo_box(self, obj, **args):
        """Generates speech for the combo-box role."""

        result = []
        result += self._generateLabelAndName(obj, **args)
        result += self._generateRoleName(obj, **args)
        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            result += self._generateExpandableState(obj, **args)
            return result

        result += self._generateValue(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generatePositionInList(obj, **args)
        result += self._generateMnemonic(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_comment(self, obj, **args):
        """Generates speech for the comment role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generateLabelAndName(obj, **args)
        result += self._generateRoleName(obj, **args)
        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return result

        result += self._generatePause(obj, **args)
        result += self._generateCurrentLineText(obj, **args)
        result += self._generateAllTextSelection(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_content_deletion(self, obj, **args):
        """Generates speech for the content-deletion role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generateLeaving(obj, **args) or self._generateDeletionStart(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generateDeletionStart(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generateDisplayedText(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generateDeletionEnd(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_content_error(self, obj, **args):
        """Generates speech for a role with a content-related error."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generateDisplayedText(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generateInvalid(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_content_insertion(self, obj, **args):
        """Generates speech for the content-insertion role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generateLeaving(obj, **args) or self._generateInsertionStart(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generateInsertionStart(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generateDisplayedText(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generateInsertionEnd(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_date_editor(self, obj, **args):
        """Generates speech for the date-editor role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_definition(self, obj, **args):
        """Generates speech for the definition role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateDisplayedText(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_description_list(self, obj, **args):
        """Generates speech for the description-list role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            result = self._generateLeaving(obj, **args)
            if result:
                return result

        result = self._generate_default_prefix(obj, **args)
        result += self._generateLabelAndName(obj, **args)
        result += (self._generateNumberOfChildren(obj, **args) \
            or self._generateRoleName(obj, **args))
        result += self._generateNestingLevel(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_description_term(self, obj, **args):
        """Generates speech for the description-term role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generateLabelAndName(obj, **args)
        if not result:
            result += self._generateDisplayedText(obj, **args)
            result += self._generateAllTextSelection(obj, **args)

        result += self._generateRoleName(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generateTermValueCount(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generatePositionInList(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_description_value(self, obj, **args):
        """Generates speech for the description-value role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generateLabelAndName(obj, **args)
        if not result:
            result += self._generateDisplayedText(obj, **args)
            result += self._generateAllTextSelection(obj, **args)

        result += self._generateRoleName(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generatePositionInList(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_desktop_frame(self, obj, **args):
        """Generates speech for the desktop-frame role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_desktop_icon(self, obj, **args):
        """Generates speech for the desktop-icon role."""

        return self._generate_icon(obj, **args)

    def _generate_dial(self, obj, **args):
        """Generates speech for the dial role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generateValue(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generateLabelAndName(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateValue(obj, **args)
        result += self._generateRequired(obj, **args)
        result += self._generatePercentage(obj, **args)
        result += self._generateAvailability(obj, **args)
        result += self._generateMnemonic(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_dialog(self, obj, **args):
        """Generates speech for the dialog role."""

        result = self._generate_default_prefix(obj, **args)
        format_type = args.get("formatType", "unfocused")
        if format_type != "focused":
            result = self._generateExpandedEOCs(obj, **args)
            if result:
                return result

        result += self._generateLabelAndName(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateUnrelatedLabelsOrDescription(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_directory_pane(self, obj, **args):
        """Generates speech for the directory_pane role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_document(self, obj, **args):
        """Generates speech for document-related roles."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generateLabelAndName(obj, **args)
        result += self._generateReadOnly(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateCurrentLineText(obj, **args)
        result += self._generateAnyTextSelection(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_document_email(self, obj, **args):
        """Generates speech for the document-email role."""

        return self._generate_document(obj, **args)

    def _generate_document_frame(self, obj, **args):
        """Generates speech for the document-frame role."""

        return self._generate_document(obj, **args)

    def _generate_document_presentation(self, obj, **args):
        """Generates speech for the document-presentation role."""

        return self._generate_document(obj, **args)

    def _generate_document_spreadsheet(self, obj, **args):
        """Generates speech for the document-spreadsheet role."""

        return self._generate_document(obj, **args)

    def _generate_document_text(self, obj, **args):
        """Generates speech for the document-text role."""

        return self._generate_document(obj, **args)

    def _generate_document_web(self, obj, **args):
        """Generates speech for the document-web role."""

        return self._generate_document(obj, **args)

    def _generate_dpub_landmark(self, obj, **args):
        """Generates speech for the dpub section role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generateLabelAndName(obj, **args)
        result += self._generateRoleName(obj, **args)

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generateLeaving(obj, **args) or result

        result += self._generatePause(obj, **args)
        result += self._generateCurrentLineText(obj, **args)
        result += self._generateAllTextSelection(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_dpub_section(self, obj, **args):
        """Generates speech for the dpub section role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generateLabelAndName(obj, **args)
        result += self._generateRoleName(obj, **args)

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generateLeaving(obj, **args) or result

        result += self._generatePause(obj, **args)
        result += self._generateCurrentLineText(obj, **args)
        result += self._generateAllTextSelection(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_drawing_area(self, obj, **args):
        """Generates speech for the drawing-area role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_editbar(self, obj, **args):
        """Generates speech for the editbar role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generateLabelAndName(obj, **args)
        result += self._generateReadOnly(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generateTextIndentation(obj, **args)
        result += self._generateCurrentLineText(obj, **args)
        result += self._generateAllTextSelection(obj, **args)
        result += self._generateMnemonic(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_embedded(self, obj, **args):
        """Generates speech for the embedded role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generateLabelAndName(obj, **args)

        format_type = args.get("formatType", "unfocused")
        if format_type != "focused":
            result += (self._generateExpandedEOCs(obj, **args) \
                or self._generateUnrelatedLabels(obj, **args))

        result += self._generateRoleName(obj, **args)
        result += self._generateAvailability(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_entry(self, obj, **args):
        """Generates speech for the entry role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generateLabelAndName(obj, **args)
        result += self._generateReadOnly(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += (self._generateCurrentLineText(obj, **args) \
            or self._generatePlaceholderText(obj, **args))
        result += self._generateAllTextSelection(obj, **args)
        result += self._generateRequired(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generateInvalid(obj, **args)
        result += self._generateMnemonic(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_feed(self, obj, **args):
        """Generates speech for the feed role."""

        result = self._generate_default_prefix(obj, **args)
        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            result += self._generateLeaving(obj, **args)
            if result:
                return result

        result += self._generateLabelAndName(obj, **args)
        result += (self._generateNumberOfChildren(obj, **args) \
            or self._generateRoleName(obj, **args))
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_file_chooser(self, obj, **args):
        """Generates speech for the file-chooser role."""

        return self._generate_dialog(obj, **args)

    def _generate_filler(self, obj, **args):
        """Generates speech for the filler role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generateLabelAndName(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_font_chooser(self, obj, **args):
        """Generates speech for the font-chooser role."""

        return self._generate_dialog(obj, **args)

    def _generate_footer(self, obj, **args):
        """Generates speech for the footer role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateCurrentLineText(obj, **args)
        result += self._generateAllTextSelection(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_footnote(self, obj, **args):
        """Generates speech for the footnote role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateCurrentLineText(obj, **args)
        result += self._generateAllTextSelection(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_form(self, obj, **args):
        """Generates speech for the form role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generateLeaving(obj, **args) \
                or (self._generateLabelAndName(obj, **args) + self._generateRoleName(obj, **args))

        result = self._generate_default_prefix(obj, **args)
        if self._generateSubstring(obj, **args):
            result += self._generateCurrentLineText(obj, **args)
        else:
            result += self._generateLabelAndName(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_frame(self, obj, **args):
        """Generates speech for the frame role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generateLabelAndName(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generateLabelAndName(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateUnfocusedDialogCount(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_glass_pane(self, obj, **args):
        """Generates speech for the glass-pane role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_grouping(self, obj, **args):
        """Generates speech for the grouping role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_header(self, obj, **args):
        """Generates speech for the header role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateCurrentLineText(obj, **args)
        result += self._generateAllTextSelection(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_heading(self, obj, **args):
        """Generates speech for the heading role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generateDisplayedText(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateExpandableState(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_html_container(self, obj, **args):
        """Generates speech for the html-container role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_icon(self, obj, **args):
        """Generates speech for the icon role."""

        result = self._generate_default_prefix(obj, **args)
        format_type = args.get("formatType", "unfocused")
        if format_type.endswith("WhereAmI"):
            result += self._generateParentRoleName(obj, **args)
            result += self._generatePause(obj, **args)

        result += self._generateLabelAndName(obj, **args)
        result += (self._generateImageDescription(obj, **args) \
            or self._generateRoleName(obj, **args))
        result += self._generatePause(obj, **args)

        if format_type.endswith("WhereAmI"):
            result += self._generateSelectedItemCount(obj, **args)
            result += self._generatePause(obj, **args)
            result += self._generateSelectedItems(obj, **args)
        else:
            result += self._generatePositionInList(obj, **args)

        result += self._generateUnselectedCell(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_image(self, obj, **args):
        """Generates speech for the image role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generateLabelAndName(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateHasLongDesc(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_image_map(self, obj, **args):
        """Generates speech for the image-map role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generateLabelAndName(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_info_bar(self, obj, **args):
        """Generates speech for the info-bar role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generateLabelAndName(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateUnrelatedLabels(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_input_method_window(self, obj, **args):
        """Generates speech for the input-method-window role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_internal_frame(self, obj, **args):
        """Generates speech for the internal-frame role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generateLabelAndName(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_label(self, obj, **args):
        """Generates speech for the label role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generateLabel(obj, **args)
        result += (self._generateDisplayedText(obj) or self._generateName(obj))
        result += self._generateAllTextSelection(obj)
        result += self._generateRoleName(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_landmark(self, obj, **args):
        """Generates speech for the landmark role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            result = self._generateLeaving(obj, **args)
            if not result:
                result += self._generateRoleName(obj, **args)
                result += self._generateLabelAndName(obj, **args)
            return result

        result = self._generate_default_prefix(obj, **args)
        prior_obj = args.get("priorObj")
        if prior_obj and obj != prior_obj and not AXObject.is_ancestor(prior_obj, obj):
            result += self._generateRoleName(obj, **args)
            result += self._generateLabelAndName(obj, **args)
        result += self._generateCurrentLineText(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_layered_pane(self, obj, **args):
        """Generates speech for the layered-pane role."""

        result = self._generate_default_prefix(obj, **args)
        result += (self._generateLabelAndName(obj, **args) or self._generateRoleName(obj, **args))
        result += self._generateAvailability(obj, **args)
        result += self._generateNoShowingChildren(obj, **args)

        format_type = args.get("formatType", "unfocused")
        if not format_type.endswith("WhereAmI"):
            return result

        result += self._generateSelectedItemCount(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generateSelectedItems(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_level_bar(self, obj, **args):
        """Generates speech for the level-bar role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generateValue(obj, **args)

        result = []
        result += self._generateLabelAndName(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateValue(obj, **args)
        result += self._generateAvailability(obj, **args)
        result += self._generateMnemonic(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_link(self, obj, **args):
        """Generates speech for the link role."""

        result = self._generate_default_prefix(obj, **args)
        format_type = args.get("formatType", "unfocused")
        if format_type.endswith("WhereAmI"):
            result += self._generateLinkInfo(obj, **args)
            result += self._generatePause(obj, **args)
            result += self._generateSiteDescription(obj, **args)
            result += self._generatePause(obj, **args)
            result += self._generateFileSize(obj, **args)
            return result

        result += (self._generateLabelAndName(obj, **args) \
            or self._generateDisplayedText(obj, **args))
        result += self._generateRoleName(obj, **args)
        result += self._generateExpandableState(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_list(self, obj, **args):
        """Generates speech for the list role."""

        result = self._generate_default_prefix(obj, **args)
        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            result += self._generateLeaving(obj, **args)
            if result:
                return result

        result += self._generateLabelAndName(obj, **args)
        result += (self._generateNumberOfChildren(obj, **args) \
            or self._generateRoleName(obj, **args))
        result += self._generateNestingLevel(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_list_box(self, obj, **args):
        """Generates speech for the list-box role."""

        result = self._generate_default_prefix(obj, **args)
        format_type = args.get("formatType", "unfocused")
        result += self._generateLabelAndName(obj, **args)

        if format_type != "focused":
            result += self._generateFocusedItem(obj, **args)
            result += self._generatePause(obj, **args)

        result += self._generateMultiselectableState(obj, **args)
        result += (self._generateNumberOfChildren(obj, **args) \
            or self._generateRoleName(obj, **args))
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_list_item(self, obj, **args):
        """Generates speech for the list-item role."""

        result = self._generate_default_prefix(obj, **args)
        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            result += self._generateCheckedStateIfCheckable(obj, **args)
            result += self._generatePause(obj, **args)
            result += self._generateExpandableState(obj, **args)
            return result

        result += (self._generateLabelAndName(obj, **args) or \
            (self._generateDisplayedText(obj, **args) +
             self._generateAllTextSelection(obj, **args)))
        result += self._generateCheckedStateIfCheckable(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generateUnselectedStateIfSelectable(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generateExpandableState(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generatePositionInList(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generateListBoxItemWidgets(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_log(self, obj, **args):
        """Generates speech for the log role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_mark(self, obj, **args):
        """Generates speech for the mark role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generateLeaving(obj, **args) or self._generateMarkStart(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generateMarkStart(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generateDisplayedText(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generateMarkEnd(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_marquee(self, obj, **args):
        """Generates speech for the marquee role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_math(self, obj, **args):
        """Generates speech for the math role."""

        # TODO - JD: Move this logic here.
        return self._generateMath(obj, **args)

    def _generate_math_enclosed(self, obj, **args):
        """Generates speech for the math-enclosed role."""

        result = []
        result += self._generate_math(obj, **args)
        # TODO - JD: Move this logic here.
        result += self._generateEnclosedEnclosures(obj, **args)
        return result

    def _generate_math_fenced(self, obj, **args):
        """Generates speech for the math-fenced role."""

        # TODO - JD: Move the logic from these functions here.

        result = []
        result += self._generateFencedStart(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generateFencedContents(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generateFencedEnd(obj, **args)
        return result

    def _generate_math_fraction(self, obj, **args):
        """Generates speech for the math-fraction role."""

        # TODO - JD: Move the logic from these functions here.

        result = []
        result += self._generateFractionStart(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generateFractionNumerator(obj, **args)
        result += self._generateFractionLine(obj, **args)
        result += self._generateFractionDenominator(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generateFractionEnd(obj, **args)
        result += self._generatePause(obj, **args)
        return result

    def _generate_math_multiscript(self, obj, **args):
        """Generates speech for the math-multiscript role."""

        # TODO - JD: Move the logic from these functions here.

        result = []
        result += self._generateScriptBase(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generateScriptPrescripts(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generateScriptPostscripts(obj, **args)
        result += self._generatePause(obj, **args)
        return result

    def _generate_math_root(self, obj, **args):
        """Generates speech for the math-root role."""

        # TODO - JD: Move the logic from these functions here.

        result = []
        result += self._generateRootStart(obj, **args)
        result += self._generateRootBase(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generateRootEnd(obj, **args)
        result += self._generatePause(obj, **args)
        return result

    def _generate_math_row(self, obj, **args):
        """Generates speech for the math-row role."""

        result = [messages.TABLE_ROW % (AXObject.get_index_in_parent(obj) + 1)]
        result += (self.voice(SYSTEM, obj=obj, **args))
        result += self._generatePause(obj, **args)
        for child in AXObject.iter_children(obj):
            result += self._generateMath(child)
            result += self._generatePause(child, **args)
        return result

    def _generate_math_script_subsuper(self, obj, **args):
        """Generates speech for the math script subsuper role."""

        # TODO - JD: Move the logic from these functions here.

        result = []
        result += self._generateScriptBase(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generateScriptSubscript(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generateScriptSuperscript(obj, **args)
        result += self._generatePause(obj, **args)
        return result

    def _generate_math_script_underover(self, obj, **args):
        """Generates speech for the math script underover role."""

        # TODO - JD: Move the logic from these functions here.

        result = []
        result += self._generateScriptBase(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generateScriptUnderscript(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generateScriptOverscript(obj, **args)
        result += self._generatePause(obj, **args)
        return result

    def _generate_math_table(self, obj, **args):
        """Generates speech for the math-table role."""

        # TODO - JD: Move the logic from these functions here.

        result = []
        result += self._generateMathTableStart(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generateMathTableRows(obj, **args)
        result += self._generateMathTableEnd(obj, **args)
        result += self._generatePause(obj, **args)
        return result

    def _generate_menu(self, obj, **args):
        """Generates speech for the menu role."""

        result = self._generate_default_prefix(obj, **args)
        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            result += self._generateLabelAndName(obj, **args)
            result += self._generateRoleName(obj, **args)
            return result

        if format_type.endswith("WhereAmI"):
            result += (self._generateAncestors(obj, **args) \
                or self._generateParentRoleName(obj, **args))
            result += self._generatePause(obj, **args)

        result += self._generateLabelAndName(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateExpandableState(obj, **args)
        result += self._generateAvailability(obj, **args)
        result += self._generateMnemonic(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generateAccelerator(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generatePositionInList(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_menu_bar(self, obj, **args):
        """Generates speech for the menu-bar role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generateLabelAndName(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_menu_item(self, obj, **args):
        """Generates speech for the menu-item role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generateExpandableState(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        if format_type.endswith("WhereAmI"):
            result += self._generateAncestors(obj, **args)
            result += self._generatePause(obj, **args)

        result += self._generateLabelAndName(obj, **args)
        result += self._generateCheckedStateIfCheckable(obj, **args)
        result += self._generateExpandableState(obj, **args)
        result += self._generateAvailability(obj, **args)
        result += self._generateMnemonic(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generateAccelerator(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generatePositionInList(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_notification(self, obj, **args):
        """Generates speech for the notification role."""

        result = []
        result += self._generateRoleName(obj, **args)
        result += self._generateLabelAndName(obj, **args)
        result += self._generatePause(obj, **args)
        result += (self._generateExpandedEOCs(obj, **args) \
            or self._generateUnrelatedLabelsOrDescription(obj, **args))
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_option_pane(self, obj, **args):
        """Generates speech for the option-pane role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_page(self, obj, **args):
        """Generates speech for the page role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generateLabelAndName(obj, **args)
        result += self._generateReadOnly(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateCurrentLineText(obj, **args)
        result += self._generateAllTextSelection(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_page_tab(self, obj, **args):
        """Generates speech for the page-tab role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generateLabelAndName(obj, **args)
        result += self._generateExpandableState(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateAvailability(obj, **args)
        result += self._generateMnemonic(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generatePositionInList(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_page_tab_list(self, obj, **args):
        """Generates speech for the page-tab-list role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_panel(self, obj, **args):
        """Generates speech for the panel role."""

        result = self._generate_default_prefix(obj, **args)
        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            result += self._generateLeaving(obj, **args)
            if result:
                return result

        if self._generateSubstring(obj, **args):
            result += self._generateCurrentLineText(obj, **args)
        if not result:
            result += self._generateLabelAndName(obj, **args)

        result += self._generateUnrelatedLabelsOrDescription(obj, **args)

        child = args.get("ancestorOf")
        if child and AXUtilities.is_widget(child):
            result += self._generateRoleName(obj, **args)

        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_paragraph(self, obj, **args):
        """Generates speech for the paragraph role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generateLabelAndName(obj, **args)
        result += self._generateReadOnly(obj, **args)
        result += self._generateTextIndentation(obj, **args)
        result += self._generateCurrentLineText(obj, **args)
        result += self._generateAllTextSelection(obj, **args)
        result += self._generateMnemonic(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_password_text(self, obj, **args):
        """Generates speech for the password-text role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generateLabelAndName(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateCurrentLineText(obj, **args)
        result += self._generateAllTextSelection(obj, **args)
        result += self._generateMnemonic(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_popup_menu(self, obj, **args):
        """Generates speech for the popup-menu role."""

        return self._generate_menu(obj, **args)

    def _generate_progress_bar(self, obj, **args):
        """Generates speech for the progress-bar role."""

        result = []
        result += self._generateProgressBarIndex(obj, **args)
        format_type = args.get("formatType", "unfocused")
        if format_type != "focused":
            result += self._generateLabelAndName(obj, **args)
        result += (self._generateProgressBarValue(obj, **args) \
            or self._generateRoleName(obj, **args))
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_push_button(self, obj, **args):
        """Generates speech for the push-button role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generateExpandableState(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generateLabelAndName(obj, **args)
        result += self._generateExpandableState(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateAvailability(obj, **args)
        result += self._generateMnemonic(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_push_button_menu(self, obj, **args):
        """Generates speech for the push-button-menu role."""

        return self._generate_push_button(obj, **args)

    def _generate_radio_button(self, obj, **args):
        """Generates speech for the radio-button role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generateRadioState(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        if format_type.endswith("WhereAmI"):
            result += self._generateRadioButtonGroup(obj, **args)
        else:
            result += self._generateNewRadioButtonGroup(obj, **args)

        result += self._generatePause(obj, **args)
        result += self._generateLabelAndName(obj, **args)
        result += self._generateRadioState(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateAvailability(obj, **args)
        result += self._generateMnemonic(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generatePositionInGroup(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_radio_menu_item(self, obj, **args):
        """Generates speech for the radio-menu-item role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generateRadioState(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        if format_type.endswith("WhereAmI"):
            result += self._generateAncestors(obj, **args)
            result += self._generatePause(obj, **args)

        result += self._generateLabelAndName(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateRadioState(obj, **args)
        result += self._generateAvailability(obj, **args)
        result += self._generateMnemonic(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generateAccelerator(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generatePositionInList(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_rating(self, obj, **args):
        """Generates speech for the rating role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_region(self, obj, **args):
        """Generates speech for the region landmark role."""

        result = self._generate_default_prefix(obj, **args)
        prior_obj = args.get("priorObj")
        if prior_obj and obj != prior_obj and not AXObject.is_ancestor(prior_obj, obj):
            result += self._generateLabelAndName(obj, **args)
            result += self._generateRoleName(obj, **args)

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generateLeaving(obj, **args) or result

        result += self._generatePause(obj, **args)
        result += self._generateCurrentLineText(obj, **args)
        result += self._generateAllTextSelection(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_root_pane(self, obj, **args):
        """Generates speech for the root-pane role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_row_header(self, obj, **args):
        """Generates speech for the row-header role."""

        result = self._generate_default_prefix(obj, **args)
        format_type = args.get("formatType", "unfocused")
        if format_type != "focused" and self._generateSubstring(obj, **args):
            result += self._generateCurrentLineText(obj, **args)
        if not result:
            result += self._generateLabelAndName(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateSortOrder(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generateNewRow(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generateNewColumn(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_ruler(self, obj, **args):
        """Generates speech for the ruler role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_scroll_bar(self, obj, **args):
        """Generates speech for the scroll-bar role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generateValue(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generateLabelAndName(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateValue(obj, **args)
        result += self._generatePercentage(obj, **args)
        result += self._generateAvailability(obj, **args)
        result += self._generateMnemonic(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_scroll_pane(self, obj, **args):
        """Generates speech for the scroll-pane role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generateLabelAndName(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateCurrentLineText(obj, **args)
        result += self._generateAllTextSelection(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_section(self, obj, **args):
        """Generates speech for the section role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generateLabelAndName(obj, **args)
        result += self._generateCurrentLineText(obj, **args)
        result += self._generateAllTextSelection(obj, **args)
        result += self._generateMnemonic(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_separator(self, obj, **args):
        """Generates speech for the separator role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateAvailability(obj, **args)

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return result

        result += (self._generateLabelAndName(obj, **args) \
            or self._generateDisplayedText(obj, **args) \
            or self._generateValue(obj, **args))
        result += self._generateMnemonic(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_slider(self, obj, **args):
        """Generates speech for the slider role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generateValue(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generateLabelAndName(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateValue(obj, **args)
        result += self._generatePercentage(obj, **args)
        result += self._generateAvailability(obj, **args)
        result += self._generateMnemonic(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_spin_button(self, obj, **args):
        """Generates speech for the spin-button role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generateDisplayedText(obj, **args) or self._generateValue(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generateLabelAndName(obj, **args) + result
        result += self._generateRoleName(obj, **args)
        result += self._generateRequired(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generateInvalid(obj, **args)
        result += self._generateAvailability(obj, **args)
        result += self._generateMnemonic(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_split_pane(self, obj, **args):
        """Generates speech for the split-pane role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generateValue(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generateLabelAndName(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateValue(obj, **args)
        result += self._generatePercentage(obj, **args)
        result += self._generateAvailability(obj, **args)
        result += self._generateMnemonic(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_static(self, obj, **args):
        """Generates speech for the static role."""

        result = self._generate_default_prefix(obj, **args)
        result += (self._generateDisplayedText(obj, **args) or self._generateName(obj, **args))
        result += self._generateRoleName(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_status_bar(self, obj, **args):
        """Generates speech for the status-bar role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generateLabelAndName(obj, **args)
        result += self._generateRoleName(obj, **args)

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return result

        result += self._generatePause(obj, **args)
        # TODO - JD: Move this logic here.
        result += self._generateStatusBar(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_subscript(self, obj, **args):
        """Generates speech for the subscript role."""

        result = []
        result += self._generateRoleName(obj, **args)
        result += self._generateCurrentLineText(obj, **args)
        result += self._generateAllTextSelection(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_suggestion(self, obj, **args):
        """Generates speech for the suggestion role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generateLeaving(obj, **args) or self._generateRoleName(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generateDisplayedText(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_superscript(self, obj, **args):
        """Generates speech for the superscript role."""

        result = []
        result += self._generateRoleName(obj, **args)
        result += self._generateCurrentLineText(obj, **args)
        result += self._generateAllTextSelection(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_switch(self, obj, **args):
        """Generates speech for the switch role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generateSwitchState(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generateLabelAndName(obj, **args)
        result += self._generateSwitchState(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateAvailability(obj, **args)
        result += self._generateMnemonic(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_table(self, obj, **args):
        """Generates speech for the table role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            result = self._generateLeaving(obj, **args)
            if result:
                return result

        result = self._generate_default_prefix(obj, **args)
        result += self._generateLabelAndName(obj, **args)
        result += self._generatePause(obj, **args)
        # TODO - JD: Move this logic here.
        result += self._generateTable(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_table_cell(self, obj, **args):
        """Generates speech for the table-cell role."""

        # TODO - JD: There should be separate generators for each type of cell.
        result = self._generate_default_prefix(obj, **args)
        result = self._generateNewRowHeader(obj, **args)
        result += (self._generateNewColumnHeader(obj, **args) \
            or self._generateColumnHeaderIfToggleAndNoText(obj, **args))
        result += self._generateCellCheckedState(obj, **args)
        result += (self._generateRealActiveDescendantDisplayedText(obj, **args) \
            or self._generateImageDescription(obj, **args))
        result += self._generateExpandableState(obj, **args)
        result += self._generateNumberOfChildren(obj, **args)
        result += self._generateRequired(obj, **args)
        if result and not isinstance(result[-1], Pause):
            result += self._generatePause(obj, **args)
        result += self._generateInvalid(obj, **args)
        if result and not isinstance(result[-1], Pause):
            result += self._generatePause(obj, **args)
        result += self._generateNewNodeLevel(obj, **args)
        result += self._generateUnselectedCell(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_table_cell_in_row(self, obj, **args):
        """Generates speech for the table-cell role in the context of its row."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            result = self._generateCellCheckedState(obj, **args)
            if result and not isinstance(result[-1], Pause):
                result += self._generatePause(obj, **args)
            result += self._generateExpandableState(obj, **args)
            if result and not isinstance(result[-1], Pause):
                result += self._generatePause(obj, **args)
            result += self._generateNumberOfChildren(obj, **args)
            return result

        if format_type == "ancestor":
            result = self._generateNewRowHeader(obj, **args)
            result += self._generateNewColumnHeader(obj, **args)
            if result and not isinstance(result[-1], Pause):
                result += self._generatePause(obj, **args)
            result += self._generateNewRow(obj, **args)
            if result and not isinstance(result[-1], Pause):
                result += self._generatePause(obj, **args)
            result += self._generateNewColumn(obj, **args)
            return result

        if format_type.endswith("WhereAmI"):
            result += self._generateRowHeader(obj, **args)
            if result and not isinstance(result[-1], Pause):
                result += self._generatePause(obj, **args)
            result = self._generateColumnHeader(obj, **args)
            if result and not isinstance(result[-1], Pause):
                result += self._generatePause(obj, **args)
            result += self._generateRoleName(obj, **args)
            result += self._generateTableCellRow(obj, **args)
            if result and not isinstance(result[-1], Pause):
                result += self._generatePause(obj, **args)
            result += self._generateColumnAndRow(obj, **args)
            return result

        result = self._generateTableCellRow(obj, **args)
        return result

    def _generate_table_column_header(self, obj, **args):
        """Generates speech for the table-column-header role."""

        result = self._generate_default_prefix(obj, **args)
        format_type = args.get("formatType", "unfocused")
        if format_type != "focused" and self._generateSubstring(obj, **args):
            result += self._generateCurrentLineText(obj, **args)
        if not result:
            result += self._generateLabelAndName(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateSortOrder(obj, **args)
        if result and not isinstance(result[-1], Pause):
            result += self._generatePause(obj, **args)
        result += self._generateNewRow(obj, **args)
        if result and not isinstance(result[-1], Pause):
            result += self._generatePause(obj, **args)
        result += self._generateNewColumn(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_table_row(self, obj, **args):
        """Generates speech for the table-row role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generateExpandableState(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += (self._generateLabelAndName(obj, **args) \
            or self._generateDisplayedText(obj, **args))
        result += self._generatePause(obj, **args)
        result += self._generateExpandableState(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generatePositionInList(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_table_row_header(self, obj, **args):
        """Generates speech for the table-row-header role."""

        result = self._generate_default_prefix(obj, **args)
        format_type = args.get("formatType", "unfocused")
        if format_type != "focused" and self._generateSubstring(obj, **args):
            result += self._generateCurrentLineText(obj, **args)
        if not result:
            result += self._generateLabelAndName(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateSortOrder(obj, **args)
        if result and not isinstance(result[-1], Pause):
            result += self._generatePause(obj, **args)
        result += self._generateNewRow(obj, **args)
        if result and not isinstance(result[-1], Pause):
            result += self._generatePause(obj, **args)
        result += self._generateNewColumn(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_tearoff_menu_item(self, obj, **args):
        """Generates speech for the tearoff-menu-item role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generateLabelAndName(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateExpandableState(obj, **args)
        result += self._generateAvailability(obj, **args)
        result += self._generateMnemonic(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generateAccelerator(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generatePositionInList(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_terminal(self, obj, **args):
        """Generates speech for the terminal role."""

        result = self._generate_default_prefix(obj, **args)
        format_type = args.get("formatType", "unfocused")
        if not format_type.endswith("WhereAmI"):
            return result + self._generateTextContent(obj, **args)

        result += self._generateLabelAndName(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateTextContent(obj, **args)
        result += self._generateAnyTextSelection(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_text(self, obj, **args):
        """Generates speech for the text role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generateLabelAndName(obj, **args)
        result += self._generateReadOnly(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generatePause(obj, **args)
        result += self._generateTextIndentation(obj, **args)
        result += (self._generateCurrentLineText(obj, **args) \
            or self._generatePlaceholderText(obj, **args))
        result += self._generateAllTextSelection(obj, **args)
        result += self._generateMnemonic(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_timer(self, obj, **args):
        """Generates speech for the timer role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_title_bar(self, obj, **args):
        """Generates speech for the title-bar role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_toggle_button(self, obj, **args):
        """Generates speech for the toggle-button role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generateExpandableState(obj, **args) \
                or self._generateToggleState(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generateLabelAndName(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += (self._generateExpandableState(obj, **args) \
                or self._generateToggleState(obj, **args))
        result += self._generateAvailability(obj, **args)
        result += self._generateMnemonic(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_tool_bar(self, obj, **args):
        """Generates speech for the tool-bar role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_tool_tip(self, obj, **args):
        """Generates speech for the tool-tip role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generateLeaving(obj, **args) or self._generateRoleName(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generateRoleName(obj, **args)
        result += self._generateLabelAndName(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_tree(self, obj, **args):
        """Generates speech for the tree role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_tree_item(self, obj, **args):
        """Generates speech for the tree-item role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generateExpandableState(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        if format_type.endswith("WhereAmI"):
            result += self._generateAncestors(obj, **args)
            result += self._generatePause(obj, **args)

        result += (self._generateLabelAndName(obj, **args) \
            or self._generateDisplayedText(obj, **args))
        result += self._generatePause(obj, **args)
        result += self._generateExpandableState(obj, **args)
        if result and not isinstance(result[-1], Pause):
            result += self._generatePause(obj, **args)
        result += self._generatePositionInList(obj, **args)
        if result and not isinstance(result[-1], Pause):
            result += self._generatePause(obj, **args)
        result += self._generateNewNodeLevel(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_tree_table(self, obj, **args):
        """Generates speech for the tree-table role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_unknown(self, obj, **args):
        """Generates speech for the unknown role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generateLabelAndName(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_video(self, obj, **args):
        """Generates speech for the video role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_viewport(self, obj, **args):
        """Generates speech for the viewport role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_window(self, obj, **args):
        """Generates speech for the window role."""

        return self._generate_default_presentation(obj, **args)
