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
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=wrong-import-position
# pylint: disable=too-many-return-statements
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-locals
# pylint: disable=too-many-boolean-expressions
# pylint: disable=unused-argument

"""Produces speech presentation for accessible objects."""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__        = "$Id:$"
__version__   = "$Revision:$"
__date__      = "$Date:$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import urllib.error
import urllib.parse
import urllib.request
from typing import Any, TYPE_CHECKING

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from . import acss
from . import debug
from . import focus_manager
from . import generator
from . import input_event_manager
from . import mathsymbols
from . import messages
from . import object_properties
from . import say_all_presenter
from . import settings
from . import settings_manager
from . import speech
from . import speech_and_verbosity_manager
from .ax_document import AXDocument
from .ax_hypertext import AXHypertext
from .ax_object import AXObject
from .ax_table import AXTable
from .ax_text import AXText
from .ax_utilities import AXUtilities
from .ax_value import AXValue

if TYPE_CHECKING:
    from . import script

class Pause:
    """A dummy class to indicate we want to insert a pause into an
    utterance."""
    def __init__(self) -> None:
        pass

    def __str__(self) -> str:
        return "PAUSE"

PAUSE = [Pause()]

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
    """Produces speech presentation for accessible objects."""

    def __init__(self, script: script.Script) -> None:
        super().__init__(script, "speech")

    @staticmethod
    def log_generator_output(func):
        """Decorator for logging."""

        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            tokens = [f"SPEECH GENERATOR: {func.__name__}:", result]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return result
        return wrapper

    def generate_speech(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech presentation for obj."""

        rv = self.generate(obj, **args)
        if rv and not list(filter(lambda x: not isinstance(x, Pause), rv)):
            tokens = ["SPEECH GENERATOR: Results for", obj, "are pauses only"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            rv = []

        return rv

    def get_name(self, obj: Atspi.Accessible, **args) -> str:
        """Returns the generated name of obj as a string."""

        generated = self._generate_accessible_name(obj, **args)
        if generated:
            return generated[0]
        return ""

    def get_error_message(self, obj: Atspi.Accessible, **args) -> str:
        """Returns the generated error message for obj as a string."""

        generated = self._generate_state_invalid(obj, **args)
        if generated:
            return generated[0]
        return ""

    def get_localized_role_name(self, obj: Atspi.Accessible, **args) -> str:
        if AXObject.find_ancestor_inclusive(obj, AXUtilities.is_editable_combo_box):
            return object_properties.ROLE_EDITABLE_COMBO_BOX

        if AXUtilities.is_link(obj, args.get("role")) and AXUtilities.is_visited(obj):
            return object_properties.ROLE_VISITED_LINK

        return super().get_localized_role_name(obj, **args)

    def get_role_name(self, obj, **args):
        """Returns the generated rolename of obj as a string."""

        generated = self._generate_accessible_role(obj, **args)
        if generated:
            return generated[0]

        return ""

    def generate_window_title(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Returns an array of strings the represents details about the window title for obj."""

        result = []
        frame, dialog = self._script.utilities.frame_and_dialog(obj)
        if frame:
            frame_result = self._generate_accessible_label_and_name(frame)
            if not frame_result:
                frame_result = self._generate_accessible_role(frame)
            if frame_result:
                result.append(frame_result)

        if dialog:
            if dialog_result := self._generate_accessible_label_and_name(dialog):
                result.append(dialog_result)
        elif spreadsheet := AXObject.find_ancestor(
                obj, self._script.utilities.is_spreadsheet_table):
            if spreadsheet_result := self._generate_accessible_label_and_name(spreadsheet):
                result.append(spreadsheet_result)

        alert_and_dialog_count = len(AXUtilities.get_unfocused_alerts_and_dialogs(obj))
        if alert_and_dialog_count > 0:
            dialogs = [messages.dialog_count_speech(alert_and_dialog_count)]
            dialogs.extend(self.voice(DEFAULT, obj=obj, **args))
            result.append(dialogs)
        return result

    def _only_speak_displayed_text(self) -> bool:
        return speech_and_verbosity_manager.get_manager().get_only_speak_displayed_text()

    def _generate_result_separator(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        return PAUSE

    def _generate_pause(self, obj: Atspi.Accessible, **args) -> list[Any]:
        manager = speech_and_verbosity_manager.get_manager()
        if not manager.get_insert_pauses_between_utterances() or args.get("eliminatePauses", False):
            return []

        if settings_manager.get_manager().get_setting("verbalizePunctuationStyle") == \
           settings.PUNCTUATION_STYLE_ALL:
            return []

        return PAUSE

    def voice(self, key: str | None = None, **args) -> list[acss.ACSS]:
        """Returns an array containing a voice."""

        voicename = voiceType.get(key or DEFAULT, voiceType.get(DEFAULT))
        voices = settings_manager.get_manager().get_setting("voices")
        voice = acss.ACSS(voices.get(voiceType.get(DEFAULT), acss.ACSS()))

        language = args.get("language")
        dialect = args.get("dialect", "")
        msg = (
            f"SPEECH GENERATOR: {key} voice requested with "
            f"language='{language}', dialect='{dialect}'"
        )
        debug.print_message(debug.LEVEL_INFO, msg, True)

        # This is purely for debugging. The code needed to actually switch voices
        # does not yet exist due to some problems which need to be debugged and
        # fixed.
        check_voices_for_language = False
        if language and check_voices_for_language:
            server = speech.get_speech_server()
            assert server, "No speech server available"
            server.should_change_voice_for_language(language, dialect)

        if key in [None, DEFAULT]:
            string = args.get("string", "")
            obj = args.get("obj")
            if AXUtilities.is_link(obj):
                voice.update(voices.get(voiceType.get(HYPERLINK), acss.ACSS()))
            elif isinstance(string, str) and string.isupper() and string.strip().isalpha():
                voice.update(voices.get(voiceType.get(UPPERCASE), acss.ACSS()))
        else:
            override = voices.get(voicename)
            if override and override.get("established", True):
                voice.update(override)

        return [voice]

    def utterances_to_string(self, utterances: list[Any]) -> str:
        """Converts utterances to a string."""

        string = ""
        for u in utterances:
            if isinstance(u, str):
                string += f" {u}"
            elif isinstance(u, Pause) and string and string[-1].isalnum():
                string += "."

        return string.strip()

    ################################# BASIC DETAILS #################################

    @log_generator_output
    def _generate_accessible_description(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if not speech_and_verbosity_manager.get_manager().get_speak_description() \
           or self._only_speak_displayed_text():
            return []

        mgr = settings_manager.get_manager()
        if args.get("inMouseReview") and not mgr.get_setting("presentToolTips"):
            return []

        prior_obj = args.get("priorObj")
        if prior_obj == obj:
            return []

        if AXUtilities.is_tool_tip(prior_obj):
            return []

        result = super()._generate_accessible_description(obj, **args)
        if result:
            manager = speech_and_verbosity_manager.get_manager()
            result[0] = manager.adjust_for_presentation(obj, result[0])
            result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_accessible_image_description(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        result = super()._generate_accessible_image_description(obj, **args)
        if result:
            result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_accessible_label(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        result = super()._generate_accessible_label(obj, **args)
        if result:
            result.extend(self.voice(DEFAULT, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_accessible_name(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        is_layered_pane = AXUtilities.is_layered_pane(obj, args.get("role"))
        if is_layered_pane and self._only_speak_displayed_text():
            return []

        result = super()._generate_accessible_name(obj, **args)
        if result:
            if is_layered_pane:
                result.extend(self.voice(SYSTEM, obj=obj, **args))
            else:
                result.extend(self.voice(DEFAULT, obj=obj, **args))

        return result

    @log_generator_output
    def _generate_accessible_label_and_name(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        result = super()._generate_accessible_label_and_name(obj, **args)
        if result:
            manager = speech_and_verbosity_manager.get_manager()
            result[0] = manager.adjust_for_presentation(obj, result[0])
            if len(result) == 1:
                result.extend(self.voice(DEFAULT, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_accessible_placeholder_text(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        result = super()._generate_accessible_placeholder_text(obj, **args)
        if result:
            manager = speech_and_verbosity_manager.get_manager()
            result[0] = manager.adjust_for_presentation(obj, result[0])
            result.extend(self.voice(DEFAULT, obj=obj, **args))
        return result

    def _get_ancestor_with_usable_role(self, obj, **args):
        role = args.get("role", AXObject.get_role(obj))
        index = args.get("index", 0)
        total = args.get("total", 1)

        def use_ancestor_role(x):
            if not (AXUtilities.is_heading(x) or AXUtilities.is_link(x)):
                return False
            if AXObject.get_role(x) == role:
                return False
            return index == total - 1 or AXObject.get_name(x) == AXObject.get_name(obj)

        return AXObject.find_ancestor(obj, use_ancestor_role)

    def _should_speak_role(self, obj, **args):
        if self._only_speak_displayed_text():
            return False

        mode, _acc = focus_manager.get_manager().get_active_mode_and_object_of_interest()
        if mode == focus_manager.OBJECT_NAVIGATOR:
            return True

        role = args.get("role", AXObject.get_role(obj))
        _enabled, disabled = self._get_enabled_and_disabled_context_roles()
        if role in disabled:
            return False

        do_not_speak = [Atspi.Role.ARTICLE,
                        Atspi.Role.EXTENDED,
                        Atspi.Role.FILLER,
                        Atspi.Role.FOOTER,
                        Atspi.Role.FORM,
                        Atspi.Role.LABEL,
                        Atspi.Role.MENU_ITEM,
                        Atspi.Role.PARAGRAPH,
                        Atspi.Role.REDUNDANT_OBJECT,
                        Atspi.Role.SECTION,
                        Atspi.Role.STATIC,
                        Atspi.Role.TABLE_CELL,
                        Atspi.Role.UNKNOWN]
        if not speech_and_verbosity_manager.get_manager().use_verbose_speech():
            do_not_speak.extend([
                Atspi.Role.CANVAS,
                Atspi.Role.ICON,
            ])

        if args.get("string"):
            do_not_speak.extend([
                "ROLE_CONTENT_SUGGESTION",
            ])
        if args.get("formatType") != "basicWhereAmI":
            do_not_speak.extend([
                Atspi.Role.LIST,
                Atspi.Role.LIST_ITEM,
            ])
        if args.get("startOffset") is not None or args.get("endOffset") is not None:
            do_not_speak.extend([
                Atspi.Role.ALERT,
                Atspi.Role.DOCUMENT_FRAME,
                Atspi.Role.DOCUMENT_PRESENTATION,
                Atspi.Role.DOCUMENT_SPREADSHEET,
                Atspi.Role.DOCUMENT_TEXT,
                Atspi.Role.DOCUMENT_WEB,
            ])
        if args.get("total", 1) > 1:
            do_not_speak.extend([
                Atspi.Role.ROW_HEADER,
            ])

        if role in do_not_speak:
            return False

        if AXUtilities.is_combo_box(AXObject.get_parent(obj)):
            return False

        if self._script.utilities.is_anchor(obj):
            return False

        if AXUtilities.is_desktop_frame(obj):
            return False

        if AXUtilities.is_docked_frame(obj):
            return False

        if AXUtilities.is_panel(obj, role):
            if AXUtilities.is_selected(obj):
                return False
            child = args.get("ancestorOf")
            if not (child and AXUtilities.is_widget(child)):
                return False

        if AXUtilities.is_editable(obj) and obj == args.get("priorObj"):
            return False

        return True

    @log_generator_output
    def _generate_accessible_role(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if not self._should_speak_role(obj, **args):
            return []

        parent = AXObject.get_parent(obj)
        if AXUtilities.is_menu(obj, args.get("role")) and AXUtilities.is_combo_box(parent):
            return self._generate_accessible_role(parent)

        if AXUtilities.is_single_line_autocomplete_entry(obj):
            result: list[Any] = [self.get_localized_role_name(obj, role=Atspi.Role.AUTOCOMPLETE)]
            result.extend(self.voice(SYSTEM, obj=obj, **args))
            return result

        level = AXUtilities.get_heading_level(obj)
        if level:
            result = [object_properties.ROLE_HEADING_LEVEL_SPEECH % {
                "role": self.get_localized_role_name(obj, **args),
                "level": level}]
            result.extend(self.voice(SYSTEM, obj=obj, **args))
            return result

        result = [self.get_localized_role_name(obj, **args)]
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_tutorial(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Provides the tutorial message for obj."""

        if not speech_and_verbosity_manager.get_manager().get_speak_tutorial_messages() \
           and not args.get("formatType", "").endswith("WhereAmI"):
            return []

        text = AXObject.get_help_text(obj)
        if not text:
            return []

        return [text, self.voice(SYSTEM, obj=obj, **args)]

    @log_generator_output
    def _generate_has_click_action(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        return []

    @log_generator_output
    def _generate_has_long_description(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        return []

    @log_generator_output
    def _generate_has_details(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        return []

    @log_generator_output
    def _generate_details_for(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        return []

    @log_generator_output
    def _generate_all_details(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        return []

    @log_generator_output
    def _generate_new_radio_button_group(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if not AXUtilities.is_radio_button(obj):
            return []

        result = super()._generate_radio_button_group(obj, **args)
        if not result:
            return []

        result.extend(self.voice(DEFAULT, obj=obj, **args))
        prior_obj = args.get("priorObj", None)
        if not AXUtilities.is_radio_button(prior_obj):
            return result

        # TODO - JD: We need other ways to determine group membership. Not all
        # implementations expose the member-of relation. Gtk3 does. Others are TBD.
        members = AXUtilities.get_is_member_of(obj)
        if prior_obj not in members:
            return result

        return []

    @log_generator_output
    def _generate_term_value_count(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        result = super()._generate_term_value_count(obj, **args)
        if result:
            result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_number_of_children(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if self._only_speak_displayed_text() \
           or not speech_and_verbosity_manager.get_manager().use_verbose_speech():
            return []

        if AXObject.find_ancestor(obj, AXUtilities.is_tree_or_tree_table):
            child_nodes = self._script.utilities.child_nodes(obj)
            if child_nodes:
                result = [messages.item_count(len(child_nodes))]
                result.extend(self.voice(SYSTEM, obj=obj, **args))
                return result
            return []

        role = args.get("role")
        if AXUtilities.is_list(obj, role) or AXUtilities.is_list_box(obj, role):
            set_size = AXUtilities.get_set_size(obj)
            if set_size:
                result = [messages.list_item_count(set_size)]
                result.extend(self.voice(SYSTEM, obj=obj, **args))
                return result
            return []

        # TODO - JD: Only presenting the lack of children is what we were doing before the
        # generator cleanup. This is potentially because we would (optionally) present the
        # number of children as part of the selected child's presentation. Figure out what
        # we should really be doing, e.g in the case where no item is selected.
        if AXUtilities.is_layered_pane(obj, role):
            children = list(AXObject.iter_children(obj, AXUtilities.is_icon_or_canvas))
            if not children:
                result = [messages.ZERO_ITEMS]
                result.extend(self.voice(SYSTEM, obj=obj, **args))
                return result

        return []

    @log_generator_output
    def _generate_selected_item_count(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        container = obj
        if not AXObject.supports_selection(container):
            container = AXObject.get_parent(obj)
            if not AXObject.supports_selection(container):
                return []

        result = []
        child_count = AXObject.get_child_count(container)
        selected_count = len(self._script.utilities.selected_children(container))
        result.append(messages.selected_items_count(selected_count, child_count))
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        result.append(object_properties.ICON_INDEX_SPEECH \
                      % {"index" : AXObject.get_index_in_parent(obj) + 1,
                         "total" : child_count})
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_selected_items(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        container = obj
        if not AXObject.supports_selection(container):
            container = AXObject.get_parent(obj)
            if not AXObject.supports_selection(container):
                return []

        selected_items = self._script.utilities.selected_children(container)
        return list(map(self._generate_accessible_label_and_name, selected_items))

    @log_generator_output
    def _generate_unfocused_dialog_count(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        result = []
        alert_and_dialog_count = len(AXUtilities.get_unfocused_alerts_and_dialogs(obj))
        if alert_and_dialog_count > 0:
            result.append(messages.dialog_count_speech(alert_and_dialog_count))
            result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    def _get_enabled_and_disabled_context_roles(self):
        # TODO - JD: Move to the speech and verbosity manager.
        all_roles = [Atspi.Role.BLOCK_QUOTE,
                    Atspi.Role.CONTENT_DELETION,
                    Atspi.Role.CONTENT_INSERTION,
                    Atspi.Role.MARK,
                    Atspi.Role.SUGGESTION,
                    "ROLE_DPUB_LANDMARK",
                    "ROLE_DPUB_SECTION",
                    Atspi.Role.DESCRIPTION_LIST,
                    "ROLE_FEED",
                    Atspi.Role.FORM,
                    Atspi.Role.GROUPING,
                    Atspi.Role.LANDMARK,
                    Atspi.Role.LIST,
                    Atspi.Role.PANEL,
                    "ROLE_REGION",
                    Atspi.Role.TABLE,
                    Atspi.Role.TOOL_TIP]

        enabled, disabled = [], []

        if focus_manager.get_manager().in_say_all():
            provider = say_all_presenter.get_presenter()
        else:
            provider = speech_and_verbosity_manager.get_manager()

        if provider.get_announce_blockquote():
            enabled.append(Atspi.Role.BLOCK_QUOTE)
        if provider.get_announce_landmark():
            enabled.extend([Atspi.Role.LANDMARK, "ROLE_DPUB_LANDMARK"])
        if provider.get_announce_list():
            enabled.append(Atspi.Role.LIST)
            enabled.append(Atspi.Role.DESCRIPTION_LIST)
            enabled.append("ROLE_FEED")
        if provider.get_announce_grouping():
            enabled.extend([Atspi.Role.PANEL,
                            Atspi.Role.TOOL_TIP,
                            Atspi.Role.CONTENT_DELETION,
                            Atspi.Role.CONTENT_INSERTION,
                            Atspi.Role.GROUPING,
                            Atspi.Role.MARK,
                            Atspi.Role.SUGGESTION,
                            "ROLE_DPUB_SECTION"])
        if provider.get_announce_form():
            enabled.append(Atspi.Role.FORM)
        if provider.get_announce_table():
            enabled.append(Atspi.Role.TABLE)

        disabled = list(set(all_roles).symmetric_difference(enabled))
        return enabled, disabled

    @log_generator_output
    def _generate_leaving(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if not args.get("leaving"):
            return []

        role = args.get("role", AXObject.get_role(obj))
        enabled, _disabled = self._get_enabled_and_disabled_context_roles()
        is_details = bool(AXUtilities.get_is_details_for(obj))
        if not (role in enabled or is_details):
            return []

        count = args.get("count", 1)

        result = []
        if is_details:
            result.append(messages.LEAVING_DETAILS)
        elif role == Atspi.Role.BLOCK_QUOTE:
            if count > 1:
                result.append(messages.leaving_n_blockquotes(count))
            else:
                result.append(messages.LEAVING_BLOCKQUOTE)
        elif self._script.utilities.is_document_list(obj):
            if count > 1:
                result.append(messages.leaving_n_lists(count))
            else:
                result.append(messages.LEAVING_LIST)
        elif role == "ROLE_FEED":
            result.append(messages.LEAVING_FEED)
        elif role == Atspi.Role.PANEL:
            if AXUtilities.is_figure(obj):
                result.append(messages.LEAVING_FIGURE)
            elif self._script.utilities.is_document_panel(obj):
                result.append(messages.LEAVING_PANEL)
            else:
                result = [""]
        elif role == Atspi.Role.GROUPING:
            result.append(messages.LEAVING_GROUPING)
        elif role == Atspi.Role.TABLE and self._script.utilities.is_text_document_table(obj):
            result.append(messages.LEAVING_TABLE)
        elif role == "ROLE_DPUB_LANDMARK":
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
        elif role == "ROLE_DPUB_SECTION":
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
                result = [""]
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
        elif role == Atspi.Role.SUGGESTION and not AXUtilities.is_inline_suggestion(obj, role):
            result.append(messages.LEAVING_SUGGESTION)
        else:
            result = [""]
        if result:
            result.extend(self.voice(SYSTEM, obj=obj, **args))

        return result

    def _generate_ancestors(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        result = []

        leaving = args.get("leaving")
        if leaving and args.get("priorObj"):
            prior_obj = obj
            obj = args.get("priorObj")
        else:
            prior_obj = args.get("priorObj")

        if prior_obj and AXObject.is_dead(prior_obj):
            return []

        if AXUtilities.is_tool_tip(prior_obj):
            return []

        if prior_obj and AXObject.get_parent(prior_obj) == AXObject.get_parent(obj):
            return []

        if AXUtilities.is_page_tab(obj):
            return []

        if AXUtilities.is_tool_tip(obj):
            return []

        common_ancestor = AXObject.get_common_ancestor(prior_obj, obj)
        if obj == common_ancestor:
            return []

        include_only = args.get("includeOnly", [])

        skip_roles = args.get("skipRoles", [])
        skip_roles.append(Atspi.Role.TREE_ITEM)
        _enabled, disabled = self._get_enabled_and_disabled_context_roles()
        skip_roles.extend(disabled)

        stop_at_roles = args.get("stop_at_roles", [])
        stop_at_roles.extend([Atspi.Role.APPLICATION, Atspi.Role.MENU_BAR])

        stop_after_roles = args.get("stop_after_roles", [])
        stop_after_roles.extend([Atspi.Role.TOOL_TIP])

        present_once = [Atspi.Role.BLOCK_QUOTE, Atspi.Role.LIST]

        present_common_ancestor = False
        if common_ancestor and not leaving:
            common_role = self._get_functional_role(common_ancestor)
            if common_role in present_once:
                def pred(x):
                    return self._get_functional_role(x) == common_role
                obj_ancestor = AXObject.find_ancestor(obj, pred)
                prior_ancestor = AXObject.find_ancestor(prior_obj, pred)
                obj_level = self._get_nesting_level(obj_ancestor)
                prior_level = self._get_nesting_level(prior_ancestor)
                present_common_ancestor = obj_level != prior_level

        ancestors: list[Atspi.Accessible] = []
        ancestor_roles: list[Atspi.Role] = []
        parent = AXObject.get_parent_checked(obj)
        while parent:
            parent_role = self._get_functional_role(parent)
            if parent_role in stop_at_roles:
                break

            # TODO - JD: Create an alternative role for this.
            if parent_role in skip_roles \
                    and not self._script.utilities.is_spreadsheet_table(parent):
                pass
            elif include_only and parent_role not in include_only:
                pass
            elif AXUtilities.is_layout_only(parent):
                pass
            elif AXUtilities.is_button_with_popup(parent):
                pass
            elif parent != common_ancestor or present_common_ancestor:
                is_redundant = False
                for ancestor in ancestors:
                    if AXUtilities.is_redundant_object(ancestor, parent):
                        is_redundant = True
                        break
                if not is_redundant:
                    ancestors.append(parent)
                    ancestor_roles.append(parent_role)

            if parent == common_ancestor or parent_role in stop_after_roles:
                break

            parent = AXObject.get_parent_checked(parent)

        presented_roles = []
        for i, x in enumerate(ancestors):
            alt_role = ancestor_roles[i]
            if alt_role in present_once and alt_role in presented_roles:
                continue

            presented_roles.append(alt_role)
            count = ancestor_roles.count(alt_role)
            result.append(
                self.generate(x, formatType="ancestor", role=alt_role,
                              leaving=leaving, count=count, ancestorOf=obj, priorObj=prior_obj))

        if not leaving:
            result.reverse()
        return result

    @log_generator_output
    def _generate_old_ancestors(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        if self._script.utilities.in_find_container():
            return []

        prior_obj = args.get("priorObj")
        if not prior_obj or obj == prior_obj or not AXObject.is_valid(prior_obj):
            return []

        if AXUtilities.is_page_tab(obj):
            return []

        if AXUtilities.get_application(obj) != AXUtilities.get_application(prior_obj) \
           or AXObject.find_ancestor(obj, lambda x: x == prior_obj):
            return []

        _frame, dialog = self._script.utilities.frame_and_dialog(obj)
        if dialog:
            return []

        args["leaving"] = True
        args["includeOnly"] = [Atspi.Role.BLOCK_QUOTE,
                               Atspi.Role.DESCRIPTION_LIST,
                               Atspi.Role.FORM,
                               Atspi.Role.LANDMARK,
                               Atspi.Role.CONTENT_DELETION,
                               Atspi.Role.CONTENT_INSERTION,
                               Atspi.Role.MARK,
                               Atspi.Role.SUGGESTION,
                               "ROLE_DPUB_LANDMARK",
                               "ROLE_DPUB_SECTION",
                               "ROLE_FEED",
                               Atspi.Role.LIST,
                               Atspi.Role.PANEL,
                               "ROLE_REGION",
                               Atspi.Role.TABLE,
                               Atspi.Role.TOOL_TIP]

        result = []
        if AXUtilities.is_block_quote(prior_obj):
            result.extend(self.generate(prior_obj,
                                        role=self._get_functional_role(prior_obj),
                                        formatType="focused",
                                        leaving=True))

        result.extend(self._generate_ancestors(obj, **args))
        args.pop("leaving")
        args.pop("includeOnly")

        return result

    @log_generator_output
    def _generate_new_ancestors(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        if self._script.utilities.in_find_container():
            return []

        prior_obj = args.get("priorObj")
        if prior_obj == obj:
            return []

        role = args.get("role", AXObject.get_role(obj))
        if AXUtilities.is_frame(obj, role) or AXUtilities.is_window(obj, role):
            return []

        if AXUtilities.is_menu_item_of_any_kind(obj, role) \
           and (not prior_obj or AXUtilities.is_window(prior_obj)):
            return []

        if prior_obj is not None:
            return self._generate_ancestors(obj, **args)

        frame, dialog = self._script.utilities.frame_and_dialog(obj)
        top_level = dialog or frame
        if AXUtilities.is_dialog_or_alert(top_level):
            return self._generate_ancestors(obj, **args)

        return []

    def generate_context(self, obj, **args):
        if args.get("priorObj") == obj:
            return []

        result = self._generate_old_ancestors(obj, **args)
        result.append(self._generate_new_ancestors(obj, **args))
        return result

    def _generate_parent_role_name(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if args.get("role", AXObject.get_role(obj)) == Atspi.Role.ICON \
           and args.get("formatType", None) \
               in ["basicWhereAmI", "detailedWhereAmI"]:
            return [object_properties.ROLE_ICON_PANEL]

        parent = AXObject.get_parent(obj)
        if AXUtilities.is_table_cell(parent) or AXUtilities.is_menu(parent):
            obj = parent
        return self._generate_accessible_role(AXObject.get_parent(obj))

    @log_generator_output
    def _generate_position_in_list(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if self._only_speak_displayed_text() \
           or not (speech_and_verbosity_manager.get_manager().get_speak_position_in_set() \
                   or args.get("forceList", False)) \
           or args.get("formatType") == "ancestor":
            return []

        if args.get("index", 0) + 1 < args.get("total", 1):
            return []

        result = []
        position = AXUtilities.get_position_in_set(obj)
        total = AXUtilities.get_set_size(obj)
        if position < 0:
            return []

        string = object_properties.GROUP_INDEX_SPEECH
        if total < 0:
            if not AXUtilities.get_set_size_is_unknown(obj):
                return []
            string = object_properties.GROUP_INDEX_TOTAL_UNKNOWN_SPEECH

        if total == 1 and AXUtilities.is_menu(obj):
            return []

        position += 1
        result.append(string % {"index": position, "total": total})
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    ################################### KEYBOARD ###################################

    @log_generator_output
    def _generate_keyboard_accelerator(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        result: list[Any] = []
        accelerator = AXObject.get_accelerator(obj)
        if accelerator:
            result.append(accelerator)
            result.extend(self.voice(SYSTEM, obj=obj, **args))

        return result

    @log_generator_output
    def _generate_keyboard_mnemonic(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        result: list[Any] = []
        if speech_and_verbosity_manager.get_manager().get_speak_widget_mnemonic() \
           or args.get("forceMnemonic", False):
            mnemonic = AXObject.get_mnemonic(obj)
            if mnemonic:
                result = [mnemonic[-1]] # we just want a single character
                result.extend(self.voice(SYSTEM, obj=obj, **args))

        return result

    ##################################### LINK #####################################

    @log_generator_output
    def _generate_link_info(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        result = []
        link_uri = AXHypertext.get_link_uri(obj)
        if not link_uri:
            result.extend(self._generate_accessible_label(obj))
            result.extend(self._generate_accessible_role(obj))
            result.append(AXText.get_all_text(obj))
            result.extend(self.voice(SYSTEM, obj=obj, **args))
            return result

        link_uri_info = urllib.parse.urlparse(link_uri)
        if link_uri_info[0] in ["ftp", "ftps", "file"]:
            file_name = link_uri_info[2].split("/")
            result.append(
                messages.LINK_TO_FILE % {"uri" : link_uri_info[0], "file" : file_name[-1]})
            result.extend(self.voice(SYSTEM, obj=obj, **args))
            return result

        link_output = messages.LINK_WITH_PROTOCOL % link_uri_info[0]
        text = AXText.get_all_text(obj)
        if not AXUtilities.is_visited(obj):
            link_output = messages.LINK_WITH_PROTOCOL % link_uri_info[0]
        else:
            link_output = messages.LINK_WITH_PROTOCOL_VISITED % link_uri_info[0]
        if not text:
            text = AXHypertext.get_link_basename(obj)
        if text:
            link_output += " " + text
        result.append(link_output)
        child = AXObject.get_child(obj, 0)
        if AXUtilities.is_image(child):
            result.extend(self._generate_accessible_role(child))

        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_link_site_description(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        link_uri = AXHypertext.get_link_uri(obj)
        if not link_uri:
            return []

        link_uri_info = urllib.parse.urlparse(link_uri)
        doc_uri = AXDocument.get_uri(self._script.utilities.active_document())
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
            link_domain = link_uri_info[1].split(".")
            doc_domain = doc_uri_info[1].split(".")
            if len(link_domain) > 1 and len(doc_domain) > 1  \
               and link_domain[-1] == doc_domain[-1]  \
               and link_domain[-2] == doc_domain[-2]:
                result.append(messages.LINK_SAME_SITE)
            else:
                result.append(messages.LINK_DIFFERENT_SITE)

        if result:
            result.extend(self.voice(SYSTEM, obj=obj, **args))

        return result

    @log_generator_output
    def _generate_link_file_size(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        result: list[Any] = []
        size_string = ""
        uri = AXHypertext.get_link_uri(obj)
        if not uri:
            return result
        try:
            with urllib.request.urlopen(uri) as x:
                try:
                    size_string = x.info()["Content-length"]
                except KeyError:
                    pass
        except (ValueError, urllib.error.URLError, OSError):
            pass
        if size_string:
            size = int(size_string)
            if size < 10000:
                result.append(messages.file_size_bytes(size))
            elif size < 1000000:
                result.append(messages.FILE_SIZE_KB % (float(size) * .001))
            elif size >= 1000000:
                result.append(messages.FILE_SIZE_MB % (float(size) * .000001))
        if result:
            result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    ##################################### MATH #####################################

    @log_generator_output
    def _generate_math_contents(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        result = []
        children = list(AXObject.iter_children(obj))
        if not children and not AXUtilities.is_math(obj):
            children = [obj]

        for child in children:
            if AXUtilities.is_math_layout_only(child) and AXObject.get_child_count(child):
                result.extend(self._generate_math_contents(child))
                continue
            result.extend(self.generate(child, role=self._get_functional_role(child)))

        return result

    @log_generator_output
    def _generate_math_enclosed_enclosures(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        strings = []
        attrs = AXObject.get_attributes_dict(obj)
        enclosures = attrs.get("notation", "longdiv").split()
        if "actuarial" in enclosures:
            strings.append(messages.MATH_ENCLOSURE_ACTUARIAL)
        if "box" in enclosures:
            strings.append(messages.MATH_ENCLOSURE_BOX)
        if "circle" in enclosures:
            strings.append(messages.MATH_ENCLOSURE_CIRCLE)
        if "longdiv" in enclosures:
            strings.append(messages.MATH_ENCLOSURE_LONGDIV)
        if "radical" in enclosures:
            strings.append(messages.MATH_ENCLOSURE_RADICAL)
        if "roundedbox" in enclosures:
            strings.append(messages.MATH_ENCLOSURE_ROUNDEDBOX)
        if "horizontalstrike" in enclosures:
            strings.append(messages.MATH_ENCLOSURE_HORIZONTALSTRIKE)
        if "verticalstrike" in enclosures:
            strings.append(messages.MATH_ENCLOSURE_VERTICALSTRIKE)
        if "downdiagonalstrike" in enclosures:
            strings.append(messages.MATH_ENCLOSURE_DOWNDIAGONALSTRIKE)
        if "updiagonalstrike" in enclosures:
            strings.append(messages.MATH_ENCLOSURE_UPDIAGONALSTRIKE)
        if "northeastarrow" in enclosures:
            strings.append(messages.MATH_ENCLOSURE_NORTHEASTARROW)
        if "bottom" in enclosures:
            strings.append(messages.MATH_ENCLOSURE_BOTTOM)
        if "left" in enclosures:
            strings.append(messages.MATH_ENCLOSURE_LEFT)
        if "right" in enclosures:
            strings.append(messages.MATH_ENCLOSURE_RIGHT)
        if "top" in enclosures:
            strings.append(messages.MATH_ENCLOSURE_TOP)
        if "phasorangle" in enclosures:
            strings.append(messages.MATH_ENCLOSURE_PHASOR_ANGLE)
        if "madruwb" in enclosures:
            strings.append(messages.MATH_ENCLOSURE_MADRUWB)
        if not strings:
            tokens = ["SPEECH GENERATOR: Could not get enclosure message for", enclosures]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
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

    @log_generator_output
    def _generate_math_fenced_contents(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        result = []
        attrs = AXObject.get_attributes_dict(obj)
        separators = list(attrs.get("separators", ","))
        child_count = AXObject.get_child_count(obj)
        separators.extend(separators[-1] for _ in range(len(separators), child_count - 1))
        separators.append("")

        for i, child in enumerate(AXObject.iter_children(obj)):
            result.extend(self._generate_math_contents(child, **args))
            separator_name = mathsymbols.get_character_name(separators[i])
            result.append(separator_name)
            result.extend(self.voice(DEFAULT, obj=obj, **args))
            if separator_name:
                result.extend(self._generate_pause(obj, **args))

        return result

    @log_generator_output
    def _generate_math_fraction_numerator(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        numerator = AXObject.get_child(obj, 0)
        if AXUtilities.is_math_layout_only(numerator):
            return self._generate_math_contents(numerator)

        result = self.generate(numerator, role=self._get_functional_role(numerator))
        return result

    @log_generator_output
    def _generate_math_fraction_denominator(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        denominator = AXObject.get_child(obj, 1)
        if AXUtilities.is_math_layout_only(denominator):
            return self._generate_math_contents(denominator)

        result = self.generate(denominator, role=self._get_functional_role(denominator))
        return result

    @log_generator_output
    def _generate_math_fraction_line(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        result = [messages.MATH_FRACTION_LINE]
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_math_root_base(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        is_square_root = AXUtilities.is_math_square_root(obj)
        if is_square_root:
            base = obj
        else:
            base = AXObject.get_child(obj, 0)
        if not base:
            return []

        if is_square_root or AXUtilities.is_math_token(base) \
           or AXUtilities.is_math_layout_only(base):
            return self._generate_math_contents(base)

        result = [self._generate_pause(obj, **args)]
        result.extend(self.generate(base, role=self._get_functional_role(base)))
        return result

    @log_generator_output
    def _generate_math_script_base(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        base = AXObject.get_child(obj, 0)
        if not base:
            return []

        return self._generate_math_contents(base)

    @log_generator_output
    def _generate_math_script_script(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if AXUtilities.is_math_layout_only(obj):
            return self._generate_math_contents(obj)

        result = self.generate(obj, role=self._get_functional_role(obj))
        return result

    @log_generator_output
    def _generate_math_script_subscript(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if AXObject.get_attribute(obj, "tag") == "msup":
            return []

        subscript = AXObject.get_child(obj, 1)
        if not subscript:
            return []

        result = [messages.MATH_SUBSCRIPT]
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        result.extend(self._generate_math_script_script(subscript))
        return result

    @log_generator_output
    def _generate_math_script_superscript(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        tag = AXObject.get_attribute(obj, "tag")
        if tag == "msup":
            superscript = AXObject.get_child(obj, 1)
        elif tag == "msubsup":
            superscript = AXObject.get_child(obj, 2)
        else:
            return []

        result = [messages.MATH_SUPERSCRIPT]
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        result.extend(self._generate_math_script_script(superscript))
        return result

    @log_generator_output
    def _generate_math_script_underscript(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if AXObject.get_attribute(obj, "tag") == "mover":
            return []

        underscript = AXObject.get_child(obj, 1)
        if not underscript:
            return []

        result = [messages.MATH_UNDERSCRIPT]
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        result.extend(self._generate_math_script_script(underscript))
        return result

    @log_generator_output
    def _generate_math_script_overscript(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        tag = AXObject.get_attribute(obj, "tag")
        if tag == "mover":
            overscript = AXObject.get_child(obj, 1)
        elif tag == "munderover":
            overscript = AXObject.get_child(obj, 2)
        else:
            return []

        result = [messages.MATH_OVERSCRIPT]
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        result.extend(self._generate_math_script_script(overscript))
        return result

    @log_generator_output
    def _generate_math_script_prescripts(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        prescripts = []
        found_separator = False
        for child in AXObject.iter_children(obj):
            if AXObject.get_attribute(child, "tag") == "mprescripts":
                found_separator = True
                continue
            if found_separator:
                prescripts.append(child)

        result = []
        for i, script in enumerate(prescripts):
            if AXUtilities.is_math_layout_only(script):
                continue
            if i % 2:
                rv = [messages.MATH_PRE_SUPERSCRIPT]
            else:
                rv = [messages.MATH_PRE_SUBSCRIPT]
            rv.extend(self.voice(SYSTEM, obj=obj, **args))
            rv.extend(self._generate_math_script_script(script))
            result.append(rv)

        return result

    @log_generator_output
    def _generate_math_script_postscripts(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        postscripts = []
        child = AXObject.get_child(obj, 1)
        while child and AXObject.get_attribute(child, "tag") != "mprescripts":
            postscripts.append(child)
            child = AXObject.get_next_sibling(child)

        result = []
        for i, script in enumerate(postscripts):
            if AXUtilities.is_math_layout_only(script):
                continue
            if i % 2:
                rv = [messages.MATH_SUPERSCRIPT]
            else:
                rv = [messages.MATH_SUBSCRIPT]
            rv.extend(self.voice(SYSTEM, obj=obj, **args))
            rv.extend(self._generate_math_script_script(script))
            result.append(rv)

        return result

    @log_generator_output
    def _generate_math_table_rows(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        result = []
        for row in AXObject.iter_children(obj):
            result.extend(self.generate(row, role=self._get_functional_role(row)))

        return result

    ############################### START-OF/END-OF ################################

    @log_generator_output
    def _generate_start_of_deletion(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        start_offset = args.get("startOffset", 0)
        if start_offset != 0:
            return []

        result = []
        suggestion = AXObject.find_ancestor(obj, AXUtilities.is_inline_suggestion)
        if suggestion and obj == AXObject.get_child(suggestion, 0):
            result.extend([object_properties.ROLE_CONTENT_SUGGESTION])
            result.extend(self.voice(SYSTEM, obj=obj, **args))
            result.extend(self._generate_pause(obj, **args))

        result.extend([messages.CONTENT_DELETION_START])
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_end_of_deletion(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        end_offset = args.get("endOffset")
        if end_offset is not None:
            length = AXText.get_character_count(obj)
            if length and length != end_offset:
                return []

        result = [messages.CONTENT_DELETION_END]
        result.extend(self.voice(SYSTEM, obj=obj, **args))

        suggestion = AXObject.find_ancestor(obj, AXUtilities.is_inline_suggestion)
        if suggestion and obj == AXObject.get_child(
                suggestion, AXObject.get_child_count(suggestion) - 1):
            result.extend(self._generate_pause(obj, **args))
            result.extend([messages.CONTENT_SUGGESTION_END])
            result.extend(self.voice(SYSTEM, obj=obj, **args))

            container = AXObject.find_ancestor(obj, lambda x: bool(AXUtilities.get_details(x)))
            if AXUtilities.is_suggestion(container):
                result.extend(self._generate_pause(obj, **args))
                result.extend(self._generate_has_details(container))

        return result

    @log_generator_output
    def _generate_start_of_insertion(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        start_offset = args.get("startOffset", 0)
        if start_offset != 0:
            return []

        result = []
        suggestion = AXObject.find_ancestor(obj, AXUtilities.is_inline_suggestion)
        if suggestion and obj == AXObject.get_child(suggestion, 0):
            result.extend([object_properties.ROLE_CONTENT_SUGGESTION])
            result.extend(self.voice(SYSTEM, obj=obj, **args))
            result.extend(self._generate_pause(obj, **args))

        result.extend([messages.CONTENT_INSERTION_START])
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_end_of_insertion(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        end_offset = args.get("endOffset")
        if end_offset is not None:
            length = AXText.get_character_count(obj)
            if length and length != end_offset:
                return []

        result = [messages.CONTENT_INSERTION_END]
        result.extend(self.voice(SYSTEM, obj=obj, **args))

        suggestion = AXObject.find_ancestor(obj, AXUtilities.is_inline_suggestion)
        if suggestion and obj == AXObject.get_child(
                suggestion, AXObject.get_child_count(suggestion) - 1):
            result.extend(self._generate_pause(obj, **args))
            result.extend([messages.CONTENT_SUGGESTION_END])
            result.extend(self.voice(SYSTEM, obj=obj, **args))

            container = AXObject.find_ancestor(obj, lambda x: bool(AXUtilities.get_details(x)))
            if AXUtilities.is_suggestion(container):
                result.extend(self._generate_pause(obj, **args))
                result.extend(self._generate_has_details(container))

        return result

    @log_generator_output
    def _generate_start_of_mark(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        start_offset = args.get("startOffset", 0)
        if start_offset != 0:
            return []

        result: list[Any] = []
        role_description = AXObject.get_role_description(obj)
        if role_description:
            result.append(role_description)
            result.extend(self.voice(SYSTEM, obj=obj, **args))
            result.extend(self._generate_pause(obj, **args))

        result.append(messages.CONTENT_MARK_START)
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_end_of_mark(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        end_offset = args.get("endOffset")
        if end_offset is not None:
            length = AXText.get_character_count(obj)
            if length and length != end_offset:
                return []

        result = [messages.CONTENT_MARK_END]
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_start_of_math_fenced(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        attrs = AXObject.get_attributes_dict(obj)
        fence_start = attrs.get("open", "(")
        result = [mathsymbols.get_character_name(fence_start)]
        result.extend(self.voice(DEFAULT, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_end_of_math_fenced(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        attrs = AXObject.get_attributes_dict(obj)
        fence_end = attrs.get("close", ")")
        result = [mathsymbols.get_character_name(fence_end)]
        result.extend(self.voice(DEFAULT, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_start_of_math_fraction(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        if AXUtilities.is_math_fraction_without_bar(obj):
            result = [messages.MATH_FRACTION_WITHOUT_BAR_START]
        else:
            result = [messages.MATH_FRACTION_START]
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_end_of_math_fraction(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        result = [messages.MATH_FRACTION_END]
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_start_of_math_root(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        result = []
        if AXUtilities.is_math_square_root(obj):
            result = [messages.MATH_SQUARE_ROOT_OF]
        else:
            index = AXObject.get_child(obj, 1)
            string = AXText.get_all_text(index)
            if string == "2":
                result = [messages.MATH_SQUARE_ROOT_OF]
            elif string == "3":
                result = [messages.MATH_CUBE_ROOT_OF]
            elif string:
                result = [string]
                result.extend([messages.MATH_ROOT_OF])
            elif AXUtilities.is_math_layout_only(index):
                result = self._generate_math_contents(index)
                result.extend([messages.MATH_ROOT_OF])
            else:
                result.extend(self.generate(index, role=self._get_functional_role(index)))
                result.extend([messages.MATH_ROOT_OF])

        if result:
            result.extend(self.voice(SYSTEM, obj=obj, **args))

        return result

    @log_generator_output
    def _generate_end_of_math_root(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        result = [messages.MATH_ROOT_END]
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_start_of_math_table(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        if not AXObject.supports_table(obj):
            return []

        rows = AXTable.get_row_count(obj)
        columns = AXTable.get_column_count(obj)
        nesting_level = self._get_nesting_level(obj)
        if nesting_level > 0:
            result = [messages.math_nested_table_size(rows, columns)]
        else:
            result = [messages.math_table_size(rows, columns)]
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_end_of_math_table(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        nesting_level = self._get_nesting_level(obj)
        if nesting_level > 0:
            result = [messages.MATH_NESTED_TABLE_END]
        else:
            result = [messages.MATH_TABLE_END]
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    ##################################### STATE #####################################

    @log_generator_output
    def _generate_state_current(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        result = super()._generate_state_current(obj, **args)
        if result:
            result.extend(self.voice(STATE, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_state_checked(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        result = super()._generate_state_checked(obj, **args)
        if result:
            result.extend(self.voice(STATE, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_state_checked_for_switch(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        result = super()._generate_state_checked_for_switch(obj, **args)
        if result:
            result.extend(self.voice(STATE, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_state_checked_if_checkable(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        result = super()._generate_state_checked_if_checkable(obj, **args)
        if result:
            result.extend(self.voice(STATE, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_state_expanded(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        result = super()._generate_state_expanded(obj, **args)
        if result:
            result.extend(self.voice(STATE, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_state_has_popup(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if self._only_speak_displayed_text() \
           or not speech_and_verbosity_manager.get_manager().use_verbose_speech():
            return []

        if AXUtilities.is_menu(obj) or not AXUtilities.has_popup(obj):
            return []

        return [messages.HAS_POPUP, self.voice(SYSTEM, obj=obj, **args)]

    @log_generator_output
    def _generate_state_invalid(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        result = super()._generate_state_invalid(obj, **args)
        if result:
            result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_state_multiselectable(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        result = super()._generate_state_multiselectable(obj, **args)
        if result:
            result.extend(self.voice(STATE, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_state_pressed(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        result = super()._generate_state_pressed(obj, **args)
        if result:
            result.extend(self.voice(STATE, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_state_read_only(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        result = super()._generate_state_read_only(obj, **args)
        if result:
            result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_state_required(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        if args.get("alreadyFocused"):
            return []

        result = super()._generate_state_required(obj, **args)
        if result:
            result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_state_selected_for_radio_button(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        result = super()._generate_state_selected_for_radio_button(obj, **args)
        if result:
            result.extend(self.voice(STATE, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_state_sensitive(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        result = super()._generate_state_sensitive(obj, **args)
        if result:
            result.extend(self.voice(STATE, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_state_unselected(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        if args.get("inMouseReview"):
            return []

        if not obj:
            return []

        if not AXUtilities.is_selectable(obj):
            return []

        if AXUtilities.is_selected(obj):
            return []

        if AXUtilities.is_text(obj, args.get("role")):
            return []

        if AXUtilities.is_list_item(obj, args.get("role")):
            result = [object_properties.STATE_UNSELECTED_LIST_ITEM]
            result.extend(self.voice(STATE, obj=obj, **args))
            return result

        parent = AXObject.get_parent(obj)
        table = AXTable.get_table(obj)
        if table:
            if input_event_manager.get_manager().last_event_was_left_or_right():
                return []
            if AXTable.is_layout_table(table):
                return []
            if not self._script.utilities.is_gui_cell(obj):
                return []
        elif AXUtilities.is_layered_pane(parent):
            if obj in self._script.utilities.selected_children(parent):
                return []
        else:
            return []

        result = [object_properties.STATE_UNSELECTED_TABLE_CELL]
        result.extend(self.voice(STATE, obj=obj, **args))
        return result

    ################################## POSITION #####################################

    @log_generator_output
    def _generate_nesting_level(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        result = super()._generate_nesting_level(obj, **args)
        if result:
            result.extend(self.voice(SYSTEM, obj=obj, **args))

        return result

    @log_generator_output
    def _generate_tree_item_level(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        args["newOnly"] = True
        result = super()._generate_tree_item_level(obj, **args)
        if result:
            result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

   ################################ PROGRESS BARS ##################################

    @log_generator_output
    def _generate_progress_bar_index(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if not args.get("isProgressBarUpdate") \
           or not self._should_present_progress_bar_update(obj, **args):
            return []

        result = []
        acc = self._get_most_recent_progress_bar_update()[0]
        if acc != obj:
            number = self._get_progress_bar_number_and_count(obj)[0]
            result = [messages.PROGRESS_BAR_NUMBER % (number)]
            result.extend(self.voice(SYSTEM, obj=obj, **args))

        return result

    @log_generator_output
    def _generate_progress_bar_value(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if args.get("isProgressBarUpdate") \
           and not self._should_present_progress_bar_update(obj, **args):
            return [""]

        result = []
        percent = AXValue.get_value_as_percent(obj)
        if percent is not None:
            result.append(messages.percentage(percent))
            result.extend(self.voice(SYSTEM, obj=obj, **args))

        return result

    def _get_progress_bar_update_interval(self):
        interval = settings_manager.get_manager().get_setting("progressBarSpeechInterval")
        if interval is None:
            interval = super()._get_progress_bar_update_interval()

        return int(interval)

    def _should_present_progress_bar_update(self, obj, **args):
        if not settings_manager.get_manager().get_setting("speakProgressBarUpdates"):
            return False

        return super()._should_present_progress_bar_update(obj, **args)

    ##################################### TABLE #####################################

    # TODO - JD: This function and fake role really need to die....
    @log_generator_output
    def _generate_real_table_cell(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        result = super()._generate_real_table_cell(obj, **args)
        if not (result and result[0]) \
           and speech_and_verbosity_manager.get_manager().get_speak_blank_lines() \
           and not args.get("readingRow", False) \
           and args.get("formatType") != "ancestor":
            result.append(messages.BLANK)
            if result:
                result.extend(self.voice(DEFAULT, obj=obj, **args))

        return result

    @log_generator_output
    def _generate_table_cell_column_header(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if not speech_and_verbosity_manager.get_manager().get_announce_cell_headers():
            return []

        if focus_manager.get_manager().in_say_all():
            return []

        if not self._script.utilities.cell_column_changed(obj, args.get("priorObj")) \
           and not args.get("formatType", "").endswith("WhereAmI"):
            return []

        args["newOnly"] = not self._get_is_nameless_toggle(obj)
        result = super()._generate_table_cell_column_header(obj, **args)
        if result:
            result.extend(self.voice(DEFAULT, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_table_cell_row_header(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if args.get("readingRow"):
            return []

        if not speech_and_verbosity_manager.get_manager().get_announce_cell_headers():
            return []

        if focus_manager.get_manager().in_say_all():
            return []

        if not self._script.utilities.cell_row_changed(obj, args.get("priorObj")) \
           and not args.get("formatType", "").endswith("WhereAmI"):
            return []

        args["newOnly"] = True
        result = super()._generate_table_cell_row_header(obj, **args)
        if result:
            result.extend(self.voice(DEFAULT, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_table_size(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        if args.get("leaving"):
            return []

        if AXTable.is_layout_table(obj):
            return []

        if self._script.utilities.is_spreadsheet_table(obj):
            return []

        if not speech_and_verbosity_manager.get_manager().use_verbose_speech():
            return self._generate_accessible_role(obj, **args)

        if self._script.utilities.is_text_document_table(obj):
            role = args.get("role", AXObject.get_role(obj))
            _enabled, disabled = self._get_enabled_and_disabled_context_roles()
            if role in disabled:
                return []

        rows = AXTable.get_row_count(obj)
        cols = AXTable.get_column_count(obj)
        if (rows < 0 or cols < 0) and not AXUtilities.get_set_size_is_unknown(obj):
            return []

        result = [messages.table_size(rows, cols)]
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_table_sort_order(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        result = super()._generate_table_sort_order(obj, **args)
        if result:
            result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_table_cell_column_index(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if args.get("readingRow"):
            return []

        if not speech_and_verbosity_manager.get_manager().get_announce_cell_coordinates():
            return []

        if not self._script.utilities.cell_column_changed(obj):
            return []

        col = AXTable.get_cell_coordinates(obj, find_cell=True)[1]
        if col == -1:
            return []

        result = [messages.TABLE_COLUMN % (col + 1)]
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_table_cell_row_index(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if not self._script.utilities.cell_row_changed(obj):
            return []

        if args.get("readingRow"):
            return []

        if not speech_and_verbosity_manager.get_manager().get_announce_cell_coordinates():
            return []

        row = AXTable.get_cell_coordinates(obj, find_cell=True)[0]
        if row == -1:
            return []

        result = [messages.TABLE_ROW % (row + 1)]
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_table_cell_position(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if self._only_speak_displayed_text():
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

    ##################################### TEXT ######################################

    @log_generator_output
    def _generate_text_substring(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        result = super()._generate_text_substring(obj, **args)
        if not result:
            return []

        result.extend(self.voice(DEFAULT, obj=obj, **args))
        if result[0] in ["\n", ""] \
           and speech_and_verbosity_manager.get_manager().get_speak_blank_lines() \
           and not focus_manager.get_manager().in_say_all() \
           and args.get("total", 1) == 1 \
           and not AXUtilities.is_table_cell_or_header(obj) \
           and args.get("formatType") != "ancestor":
            result[0] = messages.BLANK

        manager = speech_and_verbosity_manager.get_manager()
        result[0] = manager.adjust_for_presentation(obj, result[0])
        return result

    @log_generator_output
    def _generate_text_line(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if args.get("inMouseReview") and AXUtilities.is_editable(obj):
            return []

        result = self._generate_text_substring(obj, **args)
        if result:
            return result

        text, start_offset = AXText.get_line_at_offset(obj)[0:2]
        if text == "\n" and speech_and_verbosity_manager.get_manager().get_speak_blank_lines() \
           and not focus_manager.get_manager().in_say_all() \
           and args.get("total", 1) == 1 \
           and not AXUtilities.is_table_cell_or_header(obj) \
           and args.get("formatType") != "ancestor":
            result = [messages.BLANK]
            result.extend(self.voice(string=text, obj=obj, **args))
            return result

        end_offset = start_offset + len(text)
        for start, _end, string, language, dialect in \
                self._script.utilities.split_substring_by_language(obj, start_offset, end_offset):
            string = string.replace("\ufffc", "")
            if not string:
                continue
            args["language"], args["dialect"] = language, dialect
            if "string" in args:
                msg = f"INFO: Found existing string '{args.get('string')}'; using '{string}'"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                args.pop("string")

            voice = self.voice(string=string, obj=obj, **args)
            manager = speech_and_verbosity_manager.get_manager()
            rv: list[Any] = [manager.adjust_for_presentation(obj, string, start)]
            rv.extend(voice)

            # TODO - JD: speech.speak() has a bug which causes a list of utterances to
            # be presented before a string+voice pair that comes first. Until we can
            # fix speak() properly, we'll avoid triggering it here.
            # result.append(rv)
            result.extend(rv)

        return result

    @log_generator_output
    def _generate_text_content(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        result = self._generate_text_substring(obj, **args)
        if result and result[0]:
            return result

        result = super()._generate_text_content(obj, **args)
        if not (result and result[0]):
            return []

        string = result[0].strip()
        if len(string) == 1 and AXUtilities.is_math_related(obj):
            charname = mathsymbols.get_character_name(string)
            if charname and charname != string:
                result[0] = charname

        manager = speech_and_verbosity_manager.get_manager()
        result[0] = manager.adjust_for_presentation(obj, result[0])
        result.extend(self.voice(DEFAULT, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_text_selection(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        if not AXText.is_all_text_selected(obj):
            return []

        result = [messages.TEXT_SELECTED]
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_text_indentation(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if not speech_and_verbosity_manager.get_manager().get_speak_indentation_and_justification():
            return []

        format_type = args.get("formatType", "unfocused")
        only_if_changed = None
        if format_type.endswith("WhereAmI"):
            only_if_changed = False

        line = AXText.get_line_at_offset(obj, args.get("startOffset"))[0]
        description = speech_and_verbosity_manager.get_manager().get_indentation_description(
            line, only_if_changed)
        if not description:
            return []

        result: list[Any] = [description]
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    ##################################### VALUE #####################################

    @log_generator_output
    def _generate_value(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        result = super()._generate_value(obj, **args)
        if result:
            result.extend(self.voice(DEFAULT, obj=obj, **args))

        return result

    @log_generator_output
    def _generate_value_as_percentage(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        percent_value = AXValue.get_value_as_percent(obj)
        if percent_value is not None:
            result = [messages.percentage(percent_value)]
            result.extend(self.voice(SYSTEM, obj=obj, **args))
            return result

        return []

    ################################### PER-ROLE ###################################

    def _generate_default_prefix(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Provides the default/role-agnostic information to present before obj."""

        if args.get("includeContext") is False:
            return []

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generate_details_for(obj, **args)
        if format_type == "unfocused":
            return self._generate_old_ancestors(obj, **args) + \
                self._generate_new_ancestors(obj, **args)
        if format_type == "detailedWhereAmI":
            return self._generate_ancestors(obj, **args)
        return []

    def _generate_default_presentation(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Provides a default/role-agnostic presentation of obj."""

        result = self._generate_default_prefix(obj, **args)
        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return result

        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_state_sensitive(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_keyboard_mnemonic(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_default_suffix(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Provides the default/role-agnostic information to present after obj."""

        if args.get("includeContext") is False:
            return []

        # Do not call _generate_accessible_static_text here for ancestors.
        # The roles of objects which typically have static text we want to
        # present (panels, groupings, dialogs) already generate it. If we
        # include it here, it will be double-presented.
        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return []

        result = []
        if format_type.endswith("WhereAmI"):
            result += self._generate_tutorial(obj, **args)
            if result and not isinstance(result[-1], Pause):
                result += self._generate_pause(obj, **args)

        result += self._generate_state_current(obj, **args)
        if result and not isinstance(result[-1], Pause):
            result += self._generate_pause(obj, **args)
        result += self._generate_has_click_action(obj, **args)
        if result and not isinstance(result[-1], Pause):
            result += self._generate_pause(obj, **args)
        result += self._generate_has_details(obj, **args)
        result += self._generate_details_for(obj, **args)
        result += self._generate_accessible_description(obj, **args)
        if result and not isinstance(result[-1], Pause):
            result += self._generate_pause(obj, **args)
        result += self._generate_state_has_popup(obj, **args)
        if format_type == "unfocused":
            result += self._generate_tutorial(obj, **args)

        return result

    def _generate_accelerator_label(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the accelerator-label role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_alert(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the alert role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_accessible_static_text(obj, **args)
        return result

    def _generate_animation(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the animation role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_application(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the application role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_arrow(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the arrow role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_article(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the article role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_accessible_role(obj, **args)

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return result

        result += self._generate_pause(obj, **args)
        result += self._generate_text_line(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_article_in_feed(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the article role when the article is in a feed."""

        result = []
        result += self._generate_accessible_label_and_name(obj, **args)
        if not result:
            result += self._generate_text_line(obj, **args)
        if not result:
            result += self._generate_accessible_role(obj, **args)
        result += self._generate_position_in_list(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return self._generate_default_prefix(obj, **args) + result

    def _generate_audio(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the audio role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_autocomplete(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the autocomplete role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_block_quote(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the block-quote role."""

        result = []
        if args.get("priorObj") != obj:
            result += self._generate_default_prefix(obj, **args)
            result += self._generate_accessible_role(obj, **args)
            result += self._generate_pause(obj, **args)
            result += self._generate_nesting_level(obj, **args)

        result += self._generate_text_line(obj, **args)
        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generate_leaving(obj, **args) or result

        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_calendar(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the calendar role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_canvas(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the canvas role."""

        result = self._generate_default_prefix(obj, **args)
        format_type = args.get("formatType", "unfocused")
        if format_type.endswith("WhereAmI"):
            result += self._generate_parent_role_name(obj, **args)
            result += self._generate_pause(obj, **args)

        result += self._generate_accessible_label_and_name(obj, **args)
        result += (self._generate_accessible_image_description(obj, **args) \
            or self._generate_accessible_role(obj, **args))
        result += self._generate_pause(obj, **args)

        if format_type.endswith("WhereAmI"):
            result += self._generate_selected_item_count(obj, **args)
            result += self._generate_pause(obj, **args)
            result += self._generate_selected_items(obj, **args)
        else:
            result += self._generate_position_in_list(obj, **args)

        result += self._generate_state_unselected(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_caption(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the caption role."""

        result = []
        if self._generate_text_substring(obj, **args):
            result += self._generate_text_line(obj, **args)
        if not result:
            result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return self._generate_default_prefix(obj, **args) + result

    def _generate_chart(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the chart role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_check_box(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the check-box role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generate_state_checked(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_state_read_only(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_state_checked(obj, **args)
        result += self._generate_state_required(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_state_invalid(obj, **args)
        result += self._generate_state_sensitive(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_keyboard_mnemonic(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_check_menu_item(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the check-menu-item role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generate_state_checked(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        if format_type.endswith("WhereAmI"):
            result += self._generate_ancestors(obj, **args)
            result += self._generate_pause(obj, **args)

        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_state_checked(obj, **args)
        result += self._generate_state_sensitive(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_keyboard_mnemonic(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_keyboard_accelerator(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_position_in_list(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_color_chooser(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the color-chooser role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generate_value(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_value(obj, **args)

        if format_type.endswith("WhereAmI"):
            result += self._generate_value_as_percentage(obj, **args)

        result += self._generate_keyboard_accelerator(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_column_header(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the column-header role."""

        result = []
        format_type = args.get("formatType", "unfocused")
        if format_type != "focused" and self._generate_text_substring(obj, **args):
            result += self._generate_text_line(obj, **args)
        if not result:
            result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_table_sort_order(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_table_cell_row_index(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_table_cell_column_index(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return self._generate_default_prefix(obj, **args) + result

    def _generate_combo_box(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the combo-box role."""

        result = []
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            result += self._generate_state_expanded(obj, **args)
            return result

        result += self._generate_value(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_position_in_list(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_state_required(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_state_invalid(obj, **args)
        result += self._generate_keyboard_mnemonic(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return self._generate_default_prefix(obj, **args) + result

    def _generate_comment(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the comment role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return result

        result += self._generate_pause(obj, **args)
        result += self._generate_text_line(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_content_deletion(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the content-deletion role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generate_leaving(obj, **args) \
                or self._generate_start_of_deletion(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_start_of_deletion(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_text_content(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_end_of_deletion(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_content_insertion(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the content-insertion role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generate_leaving(obj, **args) \
                or self._generate_start_of_insertion(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_start_of_insertion(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_text_content(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_end_of_insertion(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_date_editor(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the date-editor role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_definition(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the definition role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_text_content(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_description_list(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the description-list role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            result = self._generate_leaving(obj, **args)
            if result:
                return result

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += (self._generate_number_of_children(obj, **args) \
            or self._generate_accessible_role(obj, **args))
        result += self._generate_nesting_level(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_description_term(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the description-term role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return []

        result = self._generate_default_prefix(obj, **args)

        if self._generate_text_substring(obj, **args):
            result += self._generate_text_line(obj, **args)
        else:
            result += (self._generate_accessible_label_and_name(obj, **args) or \
                self._generate_text_line(obj, **args))

        if speech_and_verbosity_manager.get_manager().get_announce_list():
            if args.get("index", 0) + 1 < args.get("total", 1):
                return result

            result += self._generate_accessible_role(obj, **args)
            result += self._generate_pause(obj, **args)
            result += self._generate_term_value_count(obj, **args)
            result += self._generate_pause(obj, **args)
            result += self._generate_position_in_list(obj, **args)

        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_description_value(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the description-value role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return []

        result = self._generate_default_prefix(obj, **args)
        result += (self._generate_accessible_label_and_name(obj, **args) or \
            self._generate_text_line(obj, **args))

        if speech_and_verbosity_manager.get_manager().get_announce_list():
            if args.get("index", 0) + 1 < args.get("total", 1):
                return result

            result += self._generate_accessible_role(obj, **args)
            result += self._generate_pause(obj, **args)
            result += self._generate_position_in_list(obj, **args)

        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_desktop_frame(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the desktop-frame role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_desktop_icon(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the desktop-icon role."""

        return self._generate_icon(obj, **args)

    def _generate_dial(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the dial role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generate_value(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_value(obj, **args)
        result += self._generate_state_required(obj, **args)
        result += self._generate_value_as_percentage(obj, **args)
        result += self._generate_state_sensitive(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_keyboard_mnemonic(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_dialog(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the dialog role."""

        result = self._generate_default_prefix(obj, **args)
        format_type = args.get("formatType", "unfocused")
        if format_type != "focused":
            result = self._generate_text_expanding_embedded_objects(obj, **args)
            if result:
                return result

        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_accessible_static_text(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_directory_pane(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the directory_pane role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_document(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for document-related roles."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_state_read_only(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_text_line(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_document_email(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the document-email role."""

        return self._generate_document(obj, **args)

    def _generate_document_frame(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the document-frame role."""

        return self._generate_document(obj, **args)

    def _generate_document_presentation(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the document-presentation role."""

        return self._generate_document(obj, **args)

    def _generate_document_spreadsheet(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the document-spreadsheet role."""

        return self._generate_document(obj, **args)

    def _generate_document_text(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the document-text role."""

        return self._generate_document(obj, **args)

    def _generate_document_web(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the document-web role."""

        return self._generate_document(obj, **args)

    def _generate_dpub_landmark(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the dpub section role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_accessible_role(obj, **args)

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generate_leaving(obj, **args) or result

        result += self._generate_pause(obj, **args)
        result += self._generate_text_line(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_dpub_section(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the dpub section role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_accessible_role(obj, **args)

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generate_leaving(obj, **args) or result

        result += self._generate_pause(obj, **args)
        result += self._generate_text_line(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_drawing_area(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the drawing-area role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_editbar(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the editbar role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_state_read_only(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_text_indentation(obj, **args)
        result += self._generate_text_line(obj, **args)
        result += self._generate_text_selection(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_keyboard_mnemonic(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_embedded(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the embedded role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)

        format_type = args.get("formatType", "unfocused")
        if format_type != "focused":
            result += (self._generate_text_expanding_embedded_objects(obj, **args) \
                or self._generate_accessible_static_text(obj, **args))

        result += self._generate_accessible_role(obj, **args)
        result += self._generate_state_sensitive(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_entry(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the entry role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_state_read_only(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_text_indentation(obj, **args)
        result += (self._generate_text_line(obj, **args) \
            or self._generate_accessible_placeholder_text(obj, **args))
        result += self._generate_text_selection(obj, **args)
        result += self._generate_state_required(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_state_invalid(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_keyboard_mnemonic(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_feed(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the feed role."""

        result = self._generate_default_prefix(obj, **args)
        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            result += self._generate_leaving(obj, **args)
            if result:
                return result

        result += self._generate_accessible_label_and_name(obj, **args)
        result += (self._generate_number_of_children(obj, **args) \
            or self._generate_accessible_role(obj, **args))
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_file_chooser(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the file-chooser role."""

        return self._generate_dialog(obj, **args)

    def _generate_filler(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the filler role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_font_chooser(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the font-chooser role."""

        return self._generate_dialog(obj, **args)

    def _generate_footer(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the footer role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_text_line(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_footnote(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the footnote role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_text_line(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_form(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the form role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generate_leaving(obj, **args) \
                or (self._generate_accessible_label_and_name(obj, **args) + \
                    self._generate_accessible_role(obj, **args))

        result = self._generate_default_prefix(obj, **args)
        if self._generate_text_substring(obj, **args):
            result += self._generate_text_line(obj, **args)
        else:
            result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_frame(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the frame role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generate_accessible_label_and_name(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_unfocused_dialog_count(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_glass_pane(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the glass-pane role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_grouping(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the grouping role."""

        result = self._generate_default_prefix(obj, **args)
        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            result += self._generate_leaving(obj, **args)
            if result:
                return result

        if self._generate_text_substring(obj, **args):
            result += self._generate_text_line(obj, **args)
        if not result:
            result += self._generate_accessible_label_and_name(obj, **args)

        result += self._generate_accessible_static_text(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_header(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the header role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_text_line(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_heading(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the heading role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_text_content(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_state_expanded(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_html_container(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the html-container role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_icon(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the icon role."""

        result = self._generate_default_prefix(obj, **args)
        format_type = args.get("formatType", "unfocused")
        if format_type.endswith("WhereAmI"):
            result += self._generate_parent_role_name(obj, **args)
            result += self._generate_pause(obj, **args)

        result += self._generate_accessible_label_and_name(obj, **args)
        result += (self._generate_accessible_image_description(obj, **args) \
            or self._generate_accessible_role(obj, **args))
        result += self._generate_pause(obj, **args)

        if format_type.endswith("WhereAmI"):
            result += self._generate_selected_item_count(obj, **args)
            result += self._generate_pause(obj, **args)
            result += self._generate_selected_items(obj, **args)
        else:
            result += self._generate_position_in_list(obj, **args)

        result += self._generate_state_unselected(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_image(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the image role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_has_long_description(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_image_map(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the image-map role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_info_bar(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the info-bar role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_accessible_static_text(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_input_method_window(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the input-method-window role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_internal_frame(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the internal-frame role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_label(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the label role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label(obj, **args)
        result += (self._generate_text_content(obj) or self._generate_accessible_name(obj))
        result += self._generate_text_selection(obj)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_landmark(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the landmark role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            result = self._generate_leaving(obj, **args)
            if not result:
                result += self._generate_accessible_role(obj, **args)
                result += self._generate_accessible_label_and_name(obj, **args)
            return result

        result = self._generate_default_prefix(obj, **args)
        prior_obj = args.get("priorObj")
        if prior_obj and obj != prior_obj and not AXObject.is_ancestor(prior_obj, obj):
            result += self._generate_accessible_role(obj, **args)
            result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_text_line(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_layered_pane(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the layered-pane role."""

        result = self._generate_default_prefix(obj, **args)
        result += (self._generate_accessible_label_and_name(obj, **args) \
            or self._generate_accessible_role(obj, **args))
        result += self._generate_state_sensitive(obj, **args)
        result += self._generate_number_of_children(obj, **args)

        format_type = args.get("formatType", "unfocused")
        if not format_type.endswith("WhereAmI"):
            return result

        result += self._generate_selected_item_count(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_selected_items(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_level_bar(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the level-bar role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generate_value(obj, **args)

        result = []
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_value(obj, **args)
        result += self._generate_state_sensitive(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_keyboard_mnemonic(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_link(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the link role."""

        result = self._generate_default_prefix(obj, **args)
        format_type = args.get("formatType", "unfocused")
        if format_type.endswith("WhereAmI"):
            result += self._generate_link_info(obj, **args)
            result += self._generate_pause(obj, **args)
            result += self._generate_link_site_description(obj, **args)
            result += self._generate_pause(obj, **args)
            result += self._generate_link_file_size(obj, **args)
            return result

        result += (self._generate_accessible_label_and_name(obj, **args) \
            or self._generate_text_content(obj, **args))
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_state_expanded(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_keyboard_mnemonic(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_keyboard_accelerator(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_list(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the list role."""

        result = self._generate_default_prefix(obj, **args)
        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            result += self._generate_leaving(obj, **args)
            if result:
                return result

        result += self._generate_accessible_label_and_name(obj, **args)
        result += (self._generate_number_of_children(obj, **args) \
            or self._generate_accessible_role(obj, **args))
        if AXUtilities.is_gui_list(obj):
            result += self._generate_accessible_static_text(obj, **args)
        else:
            result += self._generate_nesting_level(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_list_box(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the list-box role."""

        result = self._generate_default_prefix(obj, **args)
        format_type = args.get("formatType", "unfocused")
        result += self._generate_accessible_label_and_name(obj, **args)

        if format_type not in ["focused", "ancestor"]:
            result += self._generate_focused_item(obj, **args)
            result += self._generate_pause(obj, **args)

        result += self._generate_state_multiselectable(obj, **args)
        result += (self._generate_number_of_children(obj, **args) \
            or self._generate_accessible_role(obj, **args))
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_list_item(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the list-item role."""

        result = self._generate_default_prefix(obj, **args)
        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            result += self._generate_state_checked_if_checkable(obj, **args)
            result += self._generate_pause(obj, **args)
            result += self._generate_state_expanded(obj, **args)
            return result

        result += (self._generate_text_line(obj, **args) or \
            self._generate_accessible_label_and_name(obj, **args))
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_state_checked_if_checkable(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_state_unselected(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_state_expanded(obj, **args)
        if AXUtilities.is_focusable(obj):
            result += self._generate_descendants(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_position_in_list(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_log(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the log role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_mark(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the mark role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generate_leaving(obj, **args) or self._generate_start_of_mark(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_start_of_mark(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_text_content(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_end_of_mark(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_marquee(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the marquee role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_math(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the math role."""

        # TODO - JD: Move this logic here.
        return self._generate_math_contents(obj, **args)

    def _generate_math_enclosed(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the math-enclosed role."""

        result = []
        result += self._generate_math_contents(obj, **args)
        # TODO - JD: Move this logic here.
        result += self._generate_math_enclosed_enclosures(obj, **args)
        return result

    def _generate_math_fenced(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the math-fenced role."""

        # TODO - JD: Move the logic from these functions here.

        result = []
        result += self._generate_start_of_math_fenced(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_math_fenced_contents(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_end_of_math_fenced(obj, **args)
        return result

    def _generate_math_fraction(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the math-fraction role."""

        # TODO - JD: Move the logic from these functions here.

        result = []
        result += self._generate_start_of_math_fraction(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_math_fraction_numerator(obj, **args)
        result += self._generate_math_fraction_line(obj, **args)
        result += self._generate_math_fraction_denominator(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_end_of_math_fraction(obj, **args)
        result += self._generate_pause(obj, **args)
        return result

    def _generate_math_multiscript(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the math-multiscript role."""

        # TODO - JD: Move the logic from these functions here.

        result = []
        result += self._generate_math_script_base(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_math_script_prescripts(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_math_script_postscripts(obj, **args)
        result += self._generate_pause(obj, **args)
        return result

    def _generate_math_root(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the math-root role."""

        # TODO - JD: Move the logic from these functions here.

        result = []
        result += self._generate_start_of_math_root(obj, **args)
        result += self._generate_math_root_base(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_end_of_math_root(obj, **args)
        result += self._generate_pause(obj, **args)
        return result

    def _generate_math_row(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the math-row role."""

        result = [messages.TABLE_ROW % (AXObject.get_index_in_parent(obj) + 1)]
        result += (self.voice(SYSTEM, obj=obj, **args))
        result += self._generate_pause(obj, **args)
        for child in AXObject.iter_children(obj):
            result += self._generate_math_contents(child)
            result += self._generate_pause(child, **args)
        return result

    def _generate_math_script_subsuper(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the math script subsuper role."""

        # TODO - JD: Move the logic from these functions here.

        result = []
        result += self._generate_math_script_base(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_math_script_subscript(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_math_script_superscript(obj, **args)
        result += self._generate_pause(obj, **args)
        return result

    def _generate_math_script_underover(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the math script underover role."""

        # TODO - JD: Move the logic from these functions here.

        result = []
        result += self._generate_math_script_base(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_math_script_underscript(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_math_script_overscript(obj, **args)
        result += self._generate_pause(obj, **args)
        return result

    def _generate_math_table(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the math-table role."""

        # TODO - JD: Move the logic from these functions here.

        result = []
        result += self._generate_start_of_math_table(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_math_table_rows(obj, **args)
        result += self._generate_end_of_math_table(obj, **args)
        result += self._generate_pause(obj, **args)
        return result

    def _generate_menu(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the menu role."""

        result = self._generate_default_prefix(obj, **args)
        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            result += self._generate_accessible_label_and_name(obj, **args)
            result += self._generate_accessible_role(obj, **args)
            return result

        if format_type.endswith("WhereAmI"):
            result += (self._generate_ancestors(obj, **args) \
                or self._generate_parent_role_name(obj, **args))
            result += self._generate_pause(obj, **args)

        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_state_expanded(obj, **args)
        result += self._generate_state_sensitive(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_keyboard_mnemonic(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_keyboard_accelerator(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_position_in_list(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_menu_bar(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the menu-bar role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_menu_item(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the menu-item role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generate_state_expanded(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        if format_type.endswith("WhereAmI"):
            result += self._generate_ancestors(obj, **args)
            result += self._generate_pause(obj, **args)

        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_state_checked_if_checkable(obj, **args)
        result += self._generate_state_expanded(obj, **args)
        result += self._generate_state_sensitive(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_keyboard_mnemonic(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_keyboard_accelerator(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_position_in_list(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_notification(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the notification role."""

        # TODO - JD: Should this instead or also be using the logic in get_notification_content()?
        result = []
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_pause(obj, **args)
        result += (self._generate_text_expanding_embedded_objects(obj, **args) \
            or self._generate_accessible_static_text(obj, **args))
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_option_pane(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the option-pane role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_page(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the page role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_state_read_only(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_text_line(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_page_tab(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the page-tab role."""

        format_type = args.get("formatType", "unfocused")
        if format_type == "ancestor":
            result = self._generate_accessible_label_and_name(obj, **args)
            result += self._generate_accessible_role(obj, **args)
            return result

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_state_expanded(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_state_sensitive(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_keyboard_mnemonic(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_position_in_list(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_page_tab_list(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the page-tab-list role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_panel(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the panel role."""

        result = self._generate_default_prefix(obj, **args)
        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            result += self._generate_leaving(obj, **args)
            if result:
                return result

        if self._generate_text_substring(obj, **args):
            result += self._generate_text_line(obj, **args)
        if not result:
            result += self._generate_accessible_label_and_name(obj, **args)


        result += self._generate_accessible_static_text(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_paragraph(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the paragraph role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_state_read_only(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_text_indentation(obj, **args)
        result += self._generate_text_line(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_keyboard_mnemonic(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_password_text(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the password-text role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_text_line(obj, **args)
        result += self._generate_text_selection(obj, **args)
        result += self._generate_state_required(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_state_invalid(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_keyboard_mnemonic(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_popup_menu(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the popup-menu role."""

        return self._generate_menu(obj, **args)

    def _generate_progress_bar(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the progress-bar role."""

        result = []
        result += self._generate_progress_bar_index(obj, **args)
        format_type = args.get("formatType", "unfocused")
        if format_type != "focused":
            result += self._generate_accessible_label_and_name(obj, **args)
        result += (self._generate_progress_bar_value(obj, **args) \
            or self._generate_accessible_role(obj, **args))
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_push_button(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the push-button role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generate_state_expanded(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_state_expanded(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_state_sensitive(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_keyboard_mnemonic(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_keyboard_accelerator(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_push_button_menu(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the push-button-menu role."""

        return self._generate_push_button(obj, **args)

    def _generate_radio_button(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the radio-button role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generate_state_selected_for_radio_button(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        if format_type.endswith("WhereAmI"):
            result += self._generate_radio_button_group(obj, **args)
        else:
            result += self._generate_new_radio_button_group(obj, **args)

        result += self._generate_pause(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_state_selected_for_radio_button(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        if not AXUtilities.is_focused(obj):
            return result

        result += self._generate_state_sensitive(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_keyboard_mnemonic(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_position_in_list(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_radio_menu_item(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the radio-menu-item role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generate_state_selected_for_radio_button(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        if format_type.endswith("WhereAmI"):
            result += self._generate_ancestors(obj, **args)
            result += self._generate_pause(obj, **args)

        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_state_selected_for_radio_button(obj, **args)
        result += self._generate_state_sensitive(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_keyboard_mnemonic(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_keyboard_accelerator(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_position_in_list(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_rating(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the rating role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_region(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the region landmark role."""

        result = self._generate_default_prefix(obj, **args)
        prior_obj = args.get("priorObj")
        if prior_obj and obj != prior_obj and not AXObject.is_ancestor(prior_obj, obj):
            result += self._generate_accessible_label_and_name(obj, **args)
            result += self._generate_accessible_role(obj, **args)

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generate_leaving(obj, **args) or result

        result += self._generate_pause(obj, **args)
        result += self._generate_text_line(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_root_pane(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the root-pane role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_row_header(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the row-header role."""

        result = self._generate_default_prefix(obj, **args)
        format_type = args.get("formatType", "unfocused")
        if format_type != "focused" and self._generate_text_substring(obj, **args):
            result += self._generate_text_line(obj, **args)
        if not result:
            result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_table_sort_order(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_table_cell_row_index(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_table_cell_column_index(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_ruler(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the ruler role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_scroll_bar(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the scroll-bar role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generate_value(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_value(obj, **args)
        result += self._generate_value_as_percentage(obj, **args)
        result += self._generate_state_sensitive(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_keyboard_mnemonic(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_scroll_pane(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the scroll-pane role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_text_line(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_section(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the section role."""

        format_type = args.get("formatType", "unfocused")
        result = self._generate_default_prefix(obj, **args)
        if AXUtilities.is_focusable(obj) or AXUtilities.has_explicit_name(obj):
            result += self._generate_accessible_label_and_name(obj, **args)
            result += self._generate_pause(obj, **args)
        if format_type == "ancestor":
            return result

        result += self._generate_text_indentation(obj, **args)
        result += self._generate_text_line(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_keyboard_mnemonic(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_separator(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the separator role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_state_sensitive(obj, **args)

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return result

        result += (self._generate_accessible_label_and_name(obj, **args) \
            or self._generate_text_content(obj, **args) \
            or self._generate_value(obj, **args))
        result += self._generate_pause(obj, **args)
        result += self._generate_keyboard_mnemonic(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_slider(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the slider role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generate_value(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_value(obj, **args)
        result += self._generate_value_as_percentage(obj, **args)
        result += self._generate_state_sensitive(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_keyboard_mnemonic(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_spin_button(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the spin-button role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generate_text_content(obj, **args) or self._generate_value(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args) + result
        result += self._generate_accessible_role(obj, **args)
        result += (self._generate_text_content(obj, **args) or self._generate_value(obj, **args))
        result += self._generate_state_required(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_state_invalid(obj, **args)
        result += self._generate_state_sensitive(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_keyboard_mnemonic(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_split_pane(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the split-pane role."""

        format_type = args.get("formatType", "unfocused")
        if format_type == "focused":
            return self._generate_value(obj, **args)
        if format_type == "ancestor":
            return []

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_value(obj, **args)
        result += self._generate_value_as_percentage(obj, **args)
        result += self._generate_state_sensitive(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_keyboard_mnemonic(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_static(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the static role."""

        result = self._generate_default_prefix(obj, **args)
        if AXUtilities.is_code(obj):
            result += self._generate_text_indentation(obj, **args)
            result += self._generate_text_line(obj, **args)
        else:
            result += (self._generate_text_content(obj, **args) \
                or self._generate_accessible_name(obj, **args))
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_status_bar(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the status-bar role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_accessible_role(obj, **args)

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return result

        content = self._generate_descendants(obj, **args) \
            or self._generate_text_content(obj, **args)
        if not content and AXObject.get_child_count(obj) == 1:
            content = self._generate_text_content(AXObject.get_child(obj, 0), **args)
        if content:
            result += self._generate_pause(obj, **args) + content

        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_subscript(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the subscript role."""

        result = []
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_text_line(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_suggestion(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the suggestion role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generate_leaving(obj, **args) \
                or self._generate_accessible_role(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_text_content(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_superscript(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the superscript role."""

        result = []
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_text_line(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_switch(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the switch role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generate_state_checked_for_switch(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_state_checked_for_switch(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_state_sensitive(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_keyboard_mnemonic(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_table(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the table role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            result = self._generate_leaving(obj, **args)
            if result:
                return result

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_table_size(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_table_cell(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the table-cell role."""

        # TODO - JD: There should be separate generators for each type of cell.
        result = self._generate_default_prefix(obj, **args)
        result = self._generate_table_cell_row_header(obj, **args)
        result += self._generate_table_cell_column_header(obj, **args)
        result += self._generate_state_checked_for_cell(obj, **args)
        result += (self._generate_real_active_descendant_displayed_text(obj, **args) \
            or self._generate_accessible_label_and_name(obj, **args) \
            or self._generate_accessible_image_description(obj, **args))
        result += self._generate_state_expanded(obj, **args)
        result += self._generate_number_of_children(obj, **args)
        result += self._generate_state_required(obj, **args)
        if result and not isinstance(result[-1], Pause):
            result += self._generate_pause(obj, **args)
        result += self._generate_state_invalid(obj, **args)
        if result and not isinstance(result[-1], Pause):
            result += self._generate_pause(obj, **args)
        result += self._generate_state_sensitive(obj, **args)
        if result and not isinstance(result[-1], Pause):
            result += self._generate_pause(obj, **args)
        result += self._generate_tree_item_level(obj, **args)
        result += self._generate_state_unselected(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_table_cell_in_row(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the table-cell role in the context of its row."""

        format_type = args.get("formatType", "unfocused")
        if format_type == "focused":
            result = self._generate_state_checked_for_cell(obj, **args)
            if result and not isinstance(result[-1], Pause):
                result += self._generate_pause(obj, **args)
            result += self._generate_state_expanded(obj, **args)
            if result and not isinstance(result[-1], Pause):
                result += self._generate_pause(obj, **args)
            result += self._generate_number_of_children(obj, **args)
            return result

        if format_type == "ancestor":
            result = self._generate_table_cell_row_header(obj, **args)
            result += self._generate_table_cell_column_header(obj, **args)
            if result and not isinstance(result[-1], Pause):
                result += self._generate_pause(obj, **args)
            result += self._generate_table_cell_row_index(obj, **args)
            if result and not isinstance(result[-1], Pause):
                result += self._generate_pause(obj, **args)
            result += self._generate_table_cell_column_index(obj, **args)
            return result

        if format_type.endswith("WhereAmI"):
            result = self._generate_row_header(obj, **args)
            if result and not isinstance(result[-1], Pause):
                result += self._generate_pause(obj, **args)
            result = self._generate_column_header(obj, **args)
            if result and not isinstance(result[-1], Pause):
                result += self._generate_pause(obj, **args)
            result += self._generate_accessible_role(obj, **args)
            result += self._generate_table_cell_row(obj, **args)
            if result and not isinstance(result[-1], Pause):
                result += self._generate_pause(obj, **args)
            result += self._generate_table_cell_position(obj, **args)
            return result

        result = self._generate_table_cell_row(obj, **args)
        return result

    def _generate_table_column_header(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the table-column-header role."""

        result = self._generate_default_prefix(obj, **args)
        format_type = args.get("formatType", "unfocused")
        if format_type != "focused" and self._generate_text_substring(obj, **args):
            result += self._generate_text_line(obj, **args)
        if not result:
            result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_table_sort_order(obj, **args)
        if result and not isinstance(result[-1], Pause):
            result += self._generate_pause(obj, **args)
        result += self._generate_table_cell_row_index(obj, **args)
        if result and not isinstance(result[-1], Pause):
            result += self._generate_pause(obj, **args)
        result += self._generate_table_cell_column_index(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_table_row(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the table-row role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generate_state_expanded(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += (self._generate_accessible_label_and_name(obj, **args) \
            or self._generate_text_content(obj, **args))
        result += self._generate_pause(obj, **args)
        result += self._generate_state_expanded(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_position_in_list(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_table_row_header(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the table-row-header role."""

        result = self._generate_default_prefix(obj, **args)
        format_type = args.get("formatType", "unfocused")
        if format_type != "focused" and self._generate_text_substring(obj, **args):
            result += self._generate_text_line(obj, **args)
        if not result:
            result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_table_sort_order(obj, **args)
        if result and not isinstance(result[-1], Pause):
            result += self._generate_pause(obj, **args)
        result += self._generate_table_cell_row_index(obj, **args)
        if result and not isinstance(result[-1], Pause):
            result += self._generate_pause(obj, **args)
        result += self._generate_table_cell_column_index(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_tearoff_menu_item(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the tearoff-menu-item role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_state_expanded(obj, **args)
        result += self._generate_state_sensitive(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_keyboard_mnemonic(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_keyboard_accelerator(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_position_in_list(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_terminal(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the terminal role."""

        result = self._generate_default_prefix(obj, **args)
        format_type = args.get("formatType", "unfocused")
        if not format_type.endswith("WhereAmI"):
            return result + self._generate_text_line(obj, **args)

        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_text_line(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_text(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the text role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_state_read_only(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_text_indentation(obj, **args)
        result += (self._generate_text_line(obj, **args) \
            or self._generate_accessible_placeholder_text(obj, **args))
        result += self._generate_text_selection(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_keyboard_mnemonic(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_timer(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the timer role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_title_bar(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the title-bar role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_toggle_button(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the toggle-button role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generate_state_expanded(obj, **args) \
                or self._generate_state_pressed(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += (self._generate_state_expanded(obj, **args) \
                or self._generate_state_pressed(obj, **args))
        result += self._generate_state_sensitive(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_keyboard_mnemonic(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_tool_bar(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the tool-bar role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_tool_tip(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the tool-tip role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generate_leaving(obj, **args) \
                or self._generate_accessible_role(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_tree(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the tree role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_tree_item(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the tree-item role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generate_state_expanded(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        if format_type.endswith("WhereAmI"):
            result += self._generate_ancestors(obj, **args)
            result += self._generate_pause(obj, **args)

        result += (self._generate_accessible_label_and_name(obj, **args) \
            or self._generate_text_content(obj, **args))
        result += self._generate_pause(obj, **args)
        result += self._generate_state_expanded(obj, **args)
        if result and not isinstance(result[-1], Pause):
            result += self._generate_pause(obj, **args)
        result += self._generate_position_in_list(obj, **args)
        if result and not isinstance(result[-1], Pause):
            result += self._generate_pause(obj, **args)
        result += self._generate_tree_item_level(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_tree_table(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the tree-table role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_unknown(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the unknown role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_video(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the video role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_viewport(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the viewport role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_window(
        self,
        obj: Atspi.Accessible,
        **args
    ) -> list[Any]:
        """Generates speech for the window role."""

        return self._generate_default_presentation(obj, **args)

    def generate_contents(
        self,
        contents: list[tuple[Atspi.Accessible, int, int, str]],
        **args
    ) -> list[Any]:
        """Generates speech for a list of [obj, start, end, string] contents."""

        result = []
        for content in contents:
            obj, _start, _end, text = content
            if not text:
                continue
            voices = self.voice(obj=obj, string=text)
            voice = voices[0] if voices and isinstance(voices, list) else voices
            result.append([text, voice])

        if not result or (len(result) == 1 and result[0][0] == "\n"):
            if focus_manager.get_manager().in_say_all() \
               or not speech_and_verbosity_manager.get_manager().get_speak_blank_lines() \
               or args.get("formatType") == "ancestor":
                string = ""
            else:
                string = messages.BLANK
            result = [[string, self.voice(DEFAULT, **args)]]

        return result
