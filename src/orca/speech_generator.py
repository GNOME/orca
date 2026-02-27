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
# pylint: disable=too-many-boolean-expressions
# pylint: disable=unused-argument
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments

"""Produces speech presentation for accessible objects."""

from __future__ import annotations

import contextlib
import urllib.error
import urllib.parse
import urllib.request
from typing import TYPE_CHECKING, Any

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from . import (
    debug,
    focus_manager,
    generator,
    input_event_manager,
    mathsymbols,
    messages,
    object_properties,
    say_all_presenter,
    speech_manager,
    speech_presenter,
    speechserver,
)
from .acss import ACSS
from .ax_document import AXDocument
from .ax_hypertext import AXHypertext
from .ax_object import AXObject
from .ax_table import AXTable
from .ax_text import AXText
from .ax_utilities import AXUtilities
from .ax_value import AXValue
from .speechserver import VoiceFamily

if TYPE_CHECKING:
    from collections.abc import Callable

    from . import script


class Pause:
    """A dummy class to indicate we want to insert a pause into an
    utterance."""

    def __init__(self) -> None:
        pass

    def __str__(self) -> str:
        return "PAUSE"


PAUSE = [Pause()]

DEFAULT = "default"
UPPERCASE = "uppercase"
HYPERLINK = "hyperlink"
SYSTEM = "system"
STATE = "state"  # Candidate for sound
VALUE = "value"  # Candidate for sound

voice_type = {
    DEFAULT: speechserver.DEFAULT_VOICE,
    UPPERCASE: speechserver.UPPERCASE_VOICE,
    HYPERLINK: speechserver.HYPERLINK_VOICE,
    SYSTEM: speechserver.SYSTEM_VOICE,
    STATE: speechserver.SYSTEM_VOICE,  # Users may prefer DEFAULT_VOICE here
    VALUE: speechserver.SYSTEM_VOICE,  # Users may prefer DEFAULT_VOICE here
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
            obj,
            AXUtilities.is_spreadsheet_table,
        ):
            if spreadsheet_result := self._generate_accessible_label_and_name(spreadsheet):
                result.append(spreadsheet_result)

        alert_and_dialog_count = len(AXUtilities.get_unfocused_alerts_and_dialogs(obj))
        if alert_and_dialog_count > 0:
            dialogs = [messages.dialog_count_speech(alert_and_dialog_count)]
            dialogs.extend(self.voice(DEFAULT, obj=obj, **args))
            result.append(dialogs)
        return result

    def _only_speak_displayed_text(self) -> bool:
        return speech_presenter.get_presenter().get_only_speak_displayed_text()

    def _generate_result_separator(self, obj: Atspi.Accessible, **args) -> list[Any]:
        return PAUSE

    def _generate_pause(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if not speech_manager.get_manager().get_insert_pauses_between_utterances() or args.get(
            "eliminatePauses",
            False,
        ):
            return []

        if speech_manager.get_manager().get_punctuation_level() == "all":
            return []

        return PAUSE

    def _resolve_language_and_dialect(
        self,
        obj: Atspi.Accessible | None,
        language: str,
        dialect: str,
        server: speechserver.SpeechServer,
        family: dict,
    ) -> tuple[str, str]:
        """Returns the resolved language and dialect for voice selection."""

        if not language:
            obj_locale = AXObject.get_locale(obj).split(".")[0]
            if parts := obj_locale.split("_"):
                language = parts[0]
                if len(parts) > 1:
                    dialect = parts[1]
            tokens = ["SPEECH GENERATOR: Reported locale of", obj, "is", obj_locale]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if len(language) <= 1 or not language.isalpha():
            language = ""
            dialect = ""
        elif len(dialect) <= 1 or not dialect.isalpha():
            dialect = ""

        if not language:
            language, dialect = server.get_language_and_dialect(family)
            msg = f"SPEECH GENERATOR: Updated to: '{language}', '{dialect}'"
            debug.print_message(debug.LEVEL_INFO, msg, True)

        return language, dialect

    def _apply_default_voice_overrides(
        self,
        voice_props: ACSS,
        family: dict,
        obj: Atspi.Accessible | None,
        server: speechserver.SpeechServer,
        language: str,
        dialect: str,
        string: str,
    ) -> dict:
        """Applies voice overrides and auto-language-switching for default voice key."""

        mgr = speech_manager.get_manager()
        voice_override: ACSS | None = None
        if AXUtilities.is_link(obj):
            voice_override = mgr.get_voice_properties(voice_type[HYPERLINK])
        elif isinstance(string, str) and string.isupper() and string.strip().isalpha():
            voice_override = mgr.get_voice_properties(voice_type[UPPERCASE])

        if voice_override:
            voice_props.update(voice_override)
            if ACSS.FAMILY in voice_override:
                family.update(voice_override[ACSS.FAMILY])

        auto_lang_switching = (
            not focus_manager.get_manager().is_in_preferences_window()
            and mgr.get_auto_language_switching()
        )
        # Only update the language if it has changed from the user's preferred voice.
        # If that occurred, changing the dialect should not be problematic/bothersome.
        # For now, ignore dialect changes for the same language to avoid two potential
        # problems: 1) Unexpected voice changes when we have both a user-specified and
        # object-specified dialect (e.g. American English versus British English). In
        # the future, we can make this change opt-in. 2) Unexpected voice changes and/or
        # pauses when either the user or the object lacks a dialect because the families
        # won't match.
        if auto_lang_switching and language and language != family.get(VoiceFamily.LANG):
            family[VoiceFamily.LANG] = language
            family[VoiceFamily.DIALECT] = dialect
            if families := server.get_voice_families_for_language(
                language,
                dialect,
                family.get(VoiceFamily.VARIANT),
            ):
                family[VoiceFamily.NAME] = families[0][0]
            else:
                # On occasions (e.g. SD + espeak + "zh"), we might not get any matching
                # family. When that occurs, setting/updating the language but leaving the
                # original name can cause the voice to not be updated, whereas clearing the
                # name seems to be enough to trigger the correct language to be used.
                family[VoiceFamily.NAME] = ""
            tokens = ["SPEECH GENERATOR: Family updated to", family]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        return family

    def voice(self, key: str | None = None, **args) -> list[ACSS]:
        """Returns an array containing a voice."""

        voicename = voice_type.get(key or DEFAULT, voice_type[DEFAULT])
        mgr = speech_manager.get_manager()
        voice = mgr.get_voice_properties(voice_type[DEFAULT])

        obj = args.get("obj")
        language = args.get("language", "")
        dialect = args.get("dialect", "")
        family = voice.get(ACSS.FAMILY, {}).copy()
        tokens = [
            f"SPEECH GENERATOR: {key} voice requested for",
            obj,
            f"language='{language}', dialect='{dialect}'",
            f"Unmodified voice={voice}",
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        server = mgr.get_server()
        # TODO - JD: We probably never should have gotten to this point if there is no speech
        # server. Thus we should probably return early in generate_speech() instead. For now,
        # this check is in place of an assertion that was being reached on a user's system.
        if server is None:
            msg = "SPEECH GENERATOR: No speech server available"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return [voice]

        language, dialect = self._resolve_language_and_dialect(
            obj,
            language,
            dialect,
            server,
            family,
        )

        if key in [None, DEFAULT]:
            family = self._apply_default_voice_overrides(
                voice,
                family,
                obj,
                server,
                language,
                dialect,
                args.get("string", ""),
            )
        else:
            override = mgr.get_voice_properties(voicename)
            if override:
                voice.update(override)
                if ACSS.FAMILY in override:
                    family = override[ACSS.FAMILY]

        voice[ACSS.FAMILY] = family
        tokens = ["SPEECH GENERATOR: Final voice is", voice]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
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
    def _generate_accessible_description(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if (
            not speech_presenter.get_presenter().get_speak_description()
            or self._only_speak_displayed_text()
        ):
            return []

        prior_obj = args.get("priorObj")
        if prior_obj == obj:
            return []

        if AXUtilities.is_tool_tip(prior_obj):
            return []

        result = super()._generate_accessible_description(obj, **args)
        if result:
            manager = speech_presenter.get_presenter()
            result[0] = manager.adjust_for_presentation(obj, result[0])
            result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_accessible_image_description(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        result = super()._generate_accessible_image_description(obj, **args)
        if result:
            result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_accessible_label(self, obj: Atspi.Accessible, **args) -> list[Any]:
        result = super()._generate_accessible_label(obj, **args)
        if result:
            result.extend(self.voice(DEFAULT, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_accessible_name(self, obj: Atspi.Accessible, **args) -> list[Any]:
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
    def _generate_accessible_label_and_name(self, obj: Atspi.Accessible, **args) -> list[Any]:
        result = super()._generate_accessible_label_and_name(obj, **args)
        if result:
            manager = speech_presenter.get_presenter()
            result[0] = manager.adjust_for_presentation(obj, result[0])
            if len(result) == 1:
                result.extend(self.voice(DEFAULT, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_accessible_placeholder_text(self, obj: Atspi.Accessible, **args) -> list[Any]:
        result = super()._generate_accessible_placeholder_text(obj, **args)
        if result:
            manager = speech_presenter.get_presenter()
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

        do_not_speak = list(disabled)
        do_not_speak.extend(
            [
                Atspi.Role.ARTICLE,
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
                Atspi.Role.UNKNOWN,
            ]
        )
        if not speech_presenter.get_presenter().use_verbose_speech():
            do_not_speak.extend([Atspi.Role.CANVAS, Atspi.Role.ICON])
        if args.get("string"):
            do_not_speak.append("ROLE_CONTENT_SUGGESTION")
        if args.get("formatType") != "basicWhereAmI":
            do_not_speak.extend([Atspi.Role.LIST, Atspi.Role.LIST_ITEM])
        if args.get("startOffset") is not None or args.get("endOffset") is not None:
            do_not_speak.extend(
                [
                    Atspi.Role.ALERT,
                    Atspi.Role.DOCUMENT_FRAME,
                    Atspi.Role.DOCUMENT_PRESENTATION,
                    Atspi.Role.DOCUMENT_SPREADSHEET,
                    Atspi.Role.DOCUMENT_TEXT,
                    Atspi.Role.DOCUMENT_WEB,
                ]
            )
        if args.get("total", 1) > 1:
            do_not_speak.append(Atspi.Role.ROW_HEADER)

        if role in do_not_speak:
            return False

        if (
            AXUtilities.is_combo_box(AXObject.get_parent(obj))
            or self._script.utilities.is_anchor(obj)
            or AXUtilities.is_desktop_frame(obj)
            or AXUtilities.is_docked_frame(obj)
        ):
            return False

        if AXUtilities.is_panel(obj, role) and (
            AXUtilities.is_selected(obj)
            or not (args.get("ancestorOf") and AXUtilities.is_widget(args.get("ancestorOf")))
        ):
            return False

        return obj != args.get("priorObj")

    @log_generator_output
    def _generate_accessible_role(self, obj: Atspi.Accessible, **args) -> list[Any]:
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
            result = [
                object_properties.ROLE_HEADING_LEVEL_SPEECH
                % {"role": self.get_localized_role_name(obj, **args), "level": level},
            ]
            result.extend(self.voice(SYSTEM, obj=obj, **args))
            return result

        result = [self.get_localized_role_name(obj, **args)]
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_tutorial(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Provides the tutorial message for obj."""

        if not speech_presenter.get_presenter().get_speak_tutorial_messages() and not args.get(
            "formatType",
            "",
        ).endswith("WhereAmI"):
            return []

        text = AXObject.get_help_text(obj)
        if not text:
            return []

        return [text, self.voice(SYSTEM, obj=obj, **args)]

    @log_generator_output
    def _generate_has_click_action(self, obj: Atspi.Accessible, **args) -> list[Any]:
        return []

    @log_generator_output
    def _generate_has_long_description(self, obj: Atspi.Accessible, **args) -> list[Any]:
        return []

    @log_generator_output
    def _generate_has_details(self, obj: Atspi.Accessible, **args) -> list[Any]:
        return []

    @log_generator_output
    def _generate_details_for(self, obj: Atspi.Accessible, **args) -> list[Any]:
        return []

    @log_generator_output
    def _generate_all_details(self, obj: Atspi.Accessible, **args) -> list[Any]:
        return []

    @log_generator_output
    def _generate_new_radio_button_group(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if not AXUtilities.is_radio_button(obj):
            return []

        result = super()._generate_radio_button_group(obj, **args)
        if not result:
            return []

        result.extend(self.voice(DEFAULT, obj=obj, **args))
        prior_obj = args.get("priorObj")
        if not AXUtilities.is_radio_button(prior_obj):
            return result

        # TODO - JD: We need other ways to determine group membership. Not all
        # implementations expose the member-of relation. Gtk3 does. Others are TBD.
        members = AXUtilities.get_is_member_of(obj)
        if prior_obj not in members:
            return result

        return []

    @log_generator_output
    def _generate_term_value_count(self, obj: Atspi.Accessible, **args) -> list[Any]:
        result = super()._generate_term_value_count(obj, **args)
        if result:
            result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_number_of_children(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if (
            self._only_speak_displayed_text()
            or not speech_presenter.get_presenter().use_verbose_speech()
        ):
            return []

        if AXObject.find_ancestor(obj, AXUtilities.is_tree_or_tree_table):
            child_nodes = self._script.utilities.child_nodes(obj)
            result: list[Any] = [messages.item_count(len(child_nodes))] if child_nodes else []
            if result:
                result.extend(self.voice(SYSTEM, obj=obj, **args))
            return result

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
    def _generate_selected_item_count(self, obj: Atspi.Accessible, **args) -> list[Any]:
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
        result.append(
            object_properties.ICON_INDEX_SPEECH
            % {"index": AXObject.get_index_in_parent(obj) + 1, "total": child_count},
        )
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_selected_items(self, obj: Atspi.Accessible, **args) -> list[Any]:
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
    def _generate_unfocused_dialog_count(self, obj: Atspi.Accessible, **args) -> list[Any]:
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
        all_roles = [
            Atspi.Role.BLOCK_QUOTE,
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
            Atspi.Role.TOOL_TIP,
        ]

        enabled, disabled = [], []

        if focus_manager.get_manager().in_say_all():
            provider = say_all_presenter.get_presenter()
        else:
            provider = speech_presenter.get_presenter()

        if provider.get_announce_blockquote():
            enabled.append(Atspi.Role.BLOCK_QUOTE)
        if provider.get_announce_landmark():
            enabled.extend([Atspi.Role.LANDMARK, "ROLE_DPUB_LANDMARK"])
        if provider.get_announce_list():
            enabled.append(Atspi.Role.LIST)
            enabled.append(Atspi.Role.DESCRIPTION_LIST)
            enabled.append("ROLE_FEED")
        if provider.get_announce_grouping():
            enabled.extend(
                [
                    Atspi.Role.PANEL,
                    Atspi.Role.TOOL_TIP,
                    Atspi.Role.CONTENT_DELETION,
                    Atspi.Role.CONTENT_INSERTION,
                    Atspi.Role.GROUPING,
                    Atspi.Role.MARK,
                    Atspi.Role.SUGGESTION,
                    "ROLE_DPUB_SECTION",
                ],
            )
        if provider.get_announce_form():
            enabled.append(Atspi.Role.FORM)
        if provider.get_announce_table():
            enabled.append(Atspi.Role.TABLE)

        disabled = list(set(all_roles).symmetric_difference(enabled))
        return enabled, disabled

    @log_generator_output
    @staticmethod
    def _get_dpub_landmark_leaving_message(obj: Atspi.Accessible) -> str:
        """Returns the leaving message for a DPUB landmark."""

        dpub_landmark_checks: list[tuple[Callable, str]] = [
            (AXUtilities.is_dpub_acknowledgments, messages.LEAVING_ACKNOWLEDGMENTS),
            (AXUtilities.is_dpub_afterword, messages.LEAVING_AFTERWORD),
            (AXUtilities.is_dpub_appendix, messages.LEAVING_APPENDIX),
            (AXUtilities.is_dpub_bibliography, messages.LEAVING_BIBLIOGRAPHY),
            (AXUtilities.is_dpub_chapter, messages.LEAVING_CHAPTER),
            (AXUtilities.is_dpub_conclusion, messages.LEAVING_CONCLUSION),
            (AXUtilities.is_dpub_credits, messages.LEAVING_CREDITS),
            (AXUtilities.is_dpub_endnotes, messages.LEAVING_ENDNOTES),
            (AXUtilities.is_dpub_epilogue, messages.LEAVING_EPILOGUE),
            (AXUtilities.is_dpub_errata, messages.LEAVING_ERRATA),
            (AXUtilities.is_dpub_foreword, messages.LEAVING_FOREWORD),
            (AXUtilities.is_dpub_glossary, messages.LEAVING_GLOSSARY),
            (AXUtilities.is_dpub_index, messages.LEAVING_INDEX),
            (AXUtilities.is_dpub_introduction, messages.LEAVING_INTRODUCTION),
            (AXUtilities.is_dpub_pagelist, messages.LEAVING_PAGELIST),
            (AXUtilities.is_dpub_part, messages.LEAVING_PART),
            (AXUtilities.is_dpub_preface, messages.LEAVING_PREFACE),
            (AXUtilities.is_dpub_prologue, messages.LEAVING_PROLOGUE),
            (AXUtilities.is_dpub_toc, messages.LEAVING_TOC),
        ]
        for predicate, msg in dpub_landmark_checks:
            if predicate(obj):
                return msg
        return ""

    @staticmethod
    def _get_dpub_section_leaving_message(obj: Atspi.Accessible) -> str:
        """Returns the leaving message for a DPUB section."""

        dpub_section_checks: list[tuple[Callable, str]] = [
            (AXUtilities.is_dpub_abstract, messages.LEAVING_ABSTRACT),
            (AXUtilities.is_dpub_colophon, messages.LEAVING_COLOPHON),
            (AXUtilities.is_dpub_credit, messages.LEAVING_CREDIT),
            (AXUtilities.is_dpub_dedication, messages.LEAVING_DEDICATION),
            (AXUtilities.is_dpub_epigraph, messages.LEAVING_EPIGRAPH),
            (AXUtilities.is_dpub_example, messages.LEAVING_EXAMPLE),
            (AXUtilities.is_dpub_pullquote, messages.LEAVING_PULLQUOTE),
            (AXUtilities.is_dpub_qna, messages.LEAVING_QNA),
        ]
        for predicate, msg in dpub_section_checks:
            if predicate(obj):
                return msg
        return ""

    @staticmethod
    def _get_landmark_leaving_message(obj: Atspi.Accessible) -> str:
        """Returns the leaving message for a landmark."""

        landmark_checks: list[tuple[Callable, str]] = [
            (AXUtilities.is_landmark_banner, messages.LEAVING_LANDMARK_BANNER),
            (AXUtilities.is_landmark_complementary, messages.LEAVING_LANDMARK_COMPLEMENTARY),
            (AXUtilities.is_landmark_contentinfo, messages.LEAVING_LANDMARK_CONTENTINFO),
            (AXUtilities.is_landmark_main, messages.LEAVING_LANDMARK_MAIN),
            (AXUtilities.is_landmark_navigation, messages.LEAVING_LANDMARK_NAVIGATION),
            (AXUtilities.is_landmark_region, messages.LEAVING_LANDMARK_REGION),
            (AXUtilities.is_landmark_search, messages.LEAVING_LANDMARK_SEARCH),
            (AXUtilities.is_landmark_form, messages.LEAVING_FORM),
        ]
        for predicate, msg in landmark_checks:
            if predicate(obj):
                return msg
        return ""

    def _generate_leaving(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if not args.get("leaving"):
            return []

        role = args.get("role", AXObject.get_role(obj))
        enabled, _disabled = self._get_enabled_and_disabled_context_roles()
        is_details = bool(AXUtilities.get_is_details_for(obj))
        if not (role in enabled or is_details):
            return []

        count = args.get("count", 1)

        result = self._get_leaving_message(obj, role, count, is_details)
        if result:
            result.extend(self.voice(SYSTEM, obj=obj, **args))

        return result

    def _get_leaving_message(
        self,
        obj: Atspi.Accessible,
        role: Atspi.Role | str,
        count: int,
        is_details: bool,
    ) -> list[Any]:
        """Returns the leaving message for the given object and role."""

        simple_role_messages: dict[Atspi.Role | str, str] = {
            "ROLE_FEED": messages.LEAVING_FEED,
            Atspi.Role.GROUPING: messages.LEAVING_GROUPING,
            Atspi.Role.FORM: messages.LEAVING_FORM,
            Atspi.Role.TOOL_TIP: messages.LEAVING_TOOL_TIP,
            Atspi.Role.CONTENT_DELETION: messages.CONTENT_DELETION_END,
            Atspi.Role.CONTENT_INSERTION: messages.CONTENT_INSERTION_END,
            Atspi.Role.MARK: messages.CONTENT_MARK_END,
        }

        result = ""
        if is_details:
            result = messages.LEAVING_DETAILS
        elif role == Atspi.Role.BLOCK_QUOTE:
            result = (
                messages.leaving_n_blockquotes(count) if count > 1 else messages.LEAVING_BLOCKQUOTE
            )
        elif self._script.utilities.is_document_list(obj):
            result = messages.leaving_n_lists(count) if count > 1 else messages.LEAVING_LIST
        elif role == Atspi.Role.PANEL:
            if AXUtilities.is_figure(obj):
                result = messages.LEAVING_FIGURE
            elif self._script.utilities.is_document_panel(obj):
                result = messages.LEAVING_PANEL
        elif role == Atspi.Role.TABLE and AXUtilities.is_text_document_table(obj):
            result = messages.LEAVING_TABLE
        elif role == "ROLE_DPUB_LANDMARK":
            result = self._get_dpub_landmark_leaving_message(obj)
        elif role == "ROLE_DPUB_SECTION":
            result = self._get_dpub_section_leaving_message(obj)
        elif AXUtilities.is_landmark(obj):
            result = self._get_landmark_leaving_message(obj)
        elif role in simple_role_messages:
            result = simple_role_messages[role]
        elif role == Atspi.Role.SUGGESTION and not AXUtilities.is_inline_suggestion(obj, role):
            result = messages.LEAVING_SUGGESTION

        return [result]

    def _should_present_common_ancestor(
        self,
        obj: Atspi.Accessible,
        prior_obj: Atspi.Accessible | None,
        common_ancestor: Atspi.Accessible,
        present_once: list[Atspi.Role],
    ) -> bool:
        """Returns True if the common ancestor's nesting level has changed."""

        common_role = self._get_functional_role(common_ancestor)
        if common_role not in present_once:
            return False

        def pred(x: Atspi.Accessible) -> bool:
            return self._get_functional_role(x) == common_role

        obj_level = self._get_nesting_level(AXObject.find_ancestor(obj, pred))
        prior_level = self._get_nesting_level(AXObject.find_ancestor(prior_obj, pred))
        return obj_level != prior_level

    def _present_ancestor_results(
        self,
        ancestors: list[Atspi.Accessible],
        ancestor_roles: list[Atspi.Role],
        obj: Atspi.Accessible,
        prior_obj: Atspi.Accessible | None,
        leaving: Any,
    ) -> list[Any]:
        """Generates presentations for the collected ancestor chain."""

        present_once = [Atspi.Role.BLOCK_QUOTE, Atspi.Role.LIST]
        result: list[Any] = []
        presented_roles: list[Atspi.Role] = []
        for i, ancestor in enumerate(ancestors):
            alt_role = ancestor_roles[i]
            if alt_role in present_once and alt_role in presented_roles:
                continue

            presented_roles.append(alt_role)
            result.append(
                self.generate(
                    ancestor,
                    formatType="ancestor",
                    role=alt_role,
                    leaving=leaving,
                    count=ancestor_roles.count(alt_role),
                    ancestorOf=obj,
                    priorObj=prior_obj,
                ),
            )

        if not leaving:
            result.reverse()
        return result

    def _generate_ancestors(self, obj: Atspi.Accessible, **args) -> list[Any]:
        leaving = args.get("leaving")
        if leaving and args.get("priorObj"):
            prior_obj = obj
            obj = args.get("priorObj")
        else:
            prior_obj = args.get("priorObj")

        if (prior_obj and AXObject.is_dead(prior_obj)) or AXUtilities.is_tool_tip(prior_obj):
            return []

        if prior_obj and AXObject.get_parent(prior_obj) == AXObject.get_parent(obj):
            return []

        if AXUtilities.is_page_tab(obj) or AXUtilities.is_tool_tip(obj):
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
        present_common = (
            common_ancestor is not None
            and not leaving
            and self._should_present_common_ancestor(obj, prior_obj, common_ancestor, present_once)
        )

        ancestors: list[Atspi.Accessible] = []
        ancestor_roles: list[Atspi.Role] = []
        parent = AXObject.get_parent_checked(obj)
        while parent:
            parent_role = self._get_functional_role(parent)
            if parent_role in stop_at_roles:
                break

            # TODO - JD: Create an alternative role for this.
            should_skip = (
                (parent_role in skip_roles and not AXUtilities.is_spreadsheet_table(parent))
                or (include_only and parent_role not in include_only)
                or AXUtilities.is_layout_only(parent)
                or AXUtilities.is_button_with_popup(parent)
            )
            if (
                not should_skip
                and (parent != common_ancestor or present_common)
                and not any(AXUtilities.is_redundant_object(a, parent) for a in ancestors)
            ):
                ancestors.append(parent)
                ancestor_roles.append(parent_role)

            if parent == common_ancestor or parent_role in stop_after_roles:
                break

            parent = AXObject.get_parent_checked(parent)

        return self._present_ancestor_results(ancestors, ancestor_roles, obj, prior_obj, leaving)

    @log_generator_output
    def _generate_old_ancestors(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if self._only_speak_displayed_text() or self._script.utilities.in_find_container():
            return []

        prior_obj = args.get("priorObj")
        if not prior_obj or obj == prior_obj or not AXObject.is_valid(prior_obj):
            return []

        if AXUtilities.is_page_tab(obj):
            return []

        if AXUtilities.get_application(obj) != AXUtilities.get_application(
            prior_obj,
        ) or AXObject.find_ancestor(obj, lambda x: x == prior_obj):
            return []

        _frame, dialog = self._script.utilities.frame_and_dialog(obj)
        if dialog:
            return []

        args["leaving"] = True
        args["includeOnly"] = [
            Atspi.Role.BLOCK_QUOTE,
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
            Atspi.Role.TOOL_TIP,
        ]

        result = []
        if AXUtilities.is_block_quote(prior_obj):
            result.extend(
                self.generate(
                    prior_obj,
                    role=self._get_functional_role(prior_obj),
                    formatType="focused",
                    leaving=True,
                ),
            )

        result.extend(self._generate_ancestors(obj, **args))
        args.pop("leaving")
        args.pop("includeOnly")

        return result

    @log_generator_output
    def _generate_new_ancestors(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if self._only_speak_displayed_text() or self._script.utilities.in_find_container():
            return []

        prior_obj = args.get("priorObj")
        if prior_obj == obj:
            return []

        role = args.get("role", AXObject.get_role(obj))
        if (
            AXUtilities.is_frame(obj, role)
            or AXUtilities.is_window(obj, role)
            or (
                AXUtilities.is_menu_item_of_any_kind(obj, role)
                and (not prior_obj or AXUtilities.is_window(prior_obj))
            )
        ):
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

    def _generate_parent_role_name(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if args.get("role", AXObject.get_role(obj)) == Atspi.Role.ICON and args.get(
            "formatType",
        ) in ["basicWhereAmI", "detailedWhereAmI"]:
            return [object_properties.ROLE_ICON_PANEL]

        parent = AXObject.get_parent(obj)
        if AXUtilities.is_table_cell(parent) or AXUtilities.is_menu(parent):
            obj = parent
        return self._generate_accessible_role(AXObject.get_parent(obj))

    @log_generator_output
    def _generate_position_in_list(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if (
            self._only_speak_displayed_text()
            or not (
                speech_presenter.get_presenter().get_speak_position_in_set()
                or args.get("forceList", False)
            )
            or args.get("formatType") == "ancestor"
        ):
            return []

        if (
            args.get("index", 0) + 1 < args.get("total", 1)
            or obj != focus_manager.get_manager().get_locus_of_focus()
        ):
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
    def _generate_keyboard_accelerator(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        result: list[Any] = []
        accelerator = AXObject.get_accelerator(obj)
        if accelerator:
            result.append(accelerator)
            result.extend(self.voice(SYSTEM, obj=obj, **args))

        return result

    @log_generator_output
    def _generate_keyboard_mnemonic(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        if not (
            speech_presenter.get_presenter().get_speak_widget_mnemonic()
            or args.get("forceMnemonic", False)
        ):
            return []

        if result := super()._generate_keyboard_mnemonic(obj, **args):
            result.extend(self.voice(SYSTEM, obj=obj, **args))

        return result

    ##################################### LINK #####################################

    @log_generator_output
    def _generate_link_info(self, obj: Atspi.Accessible, **args) -> list[Any]:
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
            result.append(messages.LINK_TO_FILE % {"uri": link_uri_info[0], "file": file_name[-1]})
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
    def _generate_link_site_description(self, obj: Atspi.Accessible, **args) -> list[Any]:
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
            if (
                len(link_domain) > 1
                and len(doc_domain) > 1
                and link_domain[-1] == doc_domain[-1]
                and link_domain[-2] == doc_domain[-2]
            ):
                result.append(messages.LINK_SAME_SITE)
            else:
                result.append(messages.LINK_DIFFERENT_SITE)

        if result:
            result.extend(self.voice(SYSTEM, obj=obj, **args))

        return result

    @log_generator_output
    def _generate_link_file_size(self, obj: Atspi.Accessible, **args) -> list[Any]:
        result: list[Any] = []
        size_string = ""
        uri = AXHypertext.get_link_uri(obj)
        if not uri:
            return result
        try:
            with urllib.request.urlopen(uri) as x, contextlib.suppress(KeyError):
                size_string = x.info()["Content-length"]
        except (ValueError, urllib.error.URLError, OSError):
            pass
        if size_string:
            size = int(size_string)
            if size < 10000:
                result.append(messages.file_size_bytes(size))
            elif size < 1000000:
                result.append(messages.FILE_SIZE_KB % (float(size) * 0.001))
            elif size >= 1000000:
                result.append(messages.FILE_SIZE_MB % (float(size) * 0.000001))
        if result:
            result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    ##################################### MATH #####################################

    @log_generator_output
    def _generate_math_contents(self, obj: Atspi.Accessible, **args) -> list[Any]:
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
    def _generate_math_enclosed_enclosures(self, obj: Atspi.Accessible, **args) -> list[Any]:
        enclosure_messages = {
            "actuarial": messages.MATH_ENCLOSURE_ACTUARIAL,
            "box": messages.MATH_ENCLOSURE_BOX,
            "circle": messages.MATH_ENCLOSURE_CIRCLE,
            "longdiv": messages.MATH_ENCLOSURE_LONGDIV,
            "radical": messages.MATH_ENCLOSURE_RADICAL,
            "roundedbox": messages.MATH_ENCLOSURE_ROUNDEDBOX,
            "horizontalstrike": messages.MATH_ENCLOSURE_HORIZONTALSTRIKE,
            "verticalstrike": messages.MATH_ENCLOSURE_VERTICALSTRIKE,
            "downdiagonalstrike": messages.MATH_ENCLOSURE_DOWNDIAGONALSTRIKE,
            "updiagonalstrike": messages.MATH_ENCLOSURE_UPDIAGONALSTRIKE,
            "northeastarrow": messages.MATH_ENCLOSURE_NORTHEASTARROW,
            "bottom": messages.MATH_ENCLOSURE_BOTTOM,
            "left": messages.MATH_ENCLOSURE_LEFT,
            "right": messages.MATH_ENCLOSURE_RIGHT,
            "top": messages.MATH_ENCLOSURE_TOP,
            "phasorangle": messages.MATH_ENCLOSURE_PHASOR_ANGLE,
            "madruwb": messages.MATH_ENCLOSURE_MADRUWB,
        }
        attrs = AXObject.get_attributes_dict(obj)
        enclosures = attrs.get("notation", "longdiv").split()
        strings = [enclosure_messages[e] for e in enclosures if e in enclosure_messages]
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
    def _generate_math_fenced_contents(self, obj: Atspi.Accessible, **args) -> list[Any]:
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
    def _generate_math_fraction_numerator(self, obj: Atspi.Accessible, **args) -> list[Any]:
        numerator = AXObject.get_child(obj, 0)
        if AXUtilities.is_math_layout_only(numerator):
            return self._generate_math_contents(numerator)

        result = self.generate(numerator, role=self._get_functional_role(numerator))
        return result

    @log_generator_output
    def _generate_math_fraction_denominator(self, obj: Atspi.Accessible, **args) -> list[Any]:
        denominator = AXObject.get_child(obj, 1)
        if AXUtilities.is_math_layout_only(denominator):
            return self._generate_math_contents(denominator)

        result = self.generate(denominator, role=self._get_functional_role(denominator))
        return result

    @log_generator_output
    def _generate_math_fraction_line(self, obj: Atspi.Accessible, **args) -> list[Any]:
        result = [messages.MATH_FRACTION_LINE]
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_math_root_base(self, obj: Atspi.Accessible, **args) -> list[Any]:
        is_square_root = AXUtilities.is_math_square_root(obj)
        if is_square_root:
            base = obj
        else:
            base = AXObject.get_child(obj, 0)
        if not base:
            return []

        if (
            is_square_root
            or AXUtilities.is_math_token(base)
            or AXUtilities.is_math_layout_only(base)
        ):
            return self._generate_math_contents(base)

        result = [self._generate_pause(obj, **args)]
        result.extend(self.generate(base, role=self._get_functional_role(base)))
        return result

    @log_generator_output
    def _generate_math_script_base(self, obj: Atspi.Accessible, **args) -> list[Any]:
        base = AXObject.get_child(obj, 0)
        if not base:
            return []

        return self._generate_math_contents(base)

    @log_generator_output
    def _generate_math_script_script(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if AXUtilities.is_math_layout_only(obj):
            return self._generate_math_contents(obj)

        result = self.generate(obj, role=self._get_functional_role(obj))
        return result

    @log_generator_output
    def _generate_math_script_subscript(self, obj: Atspi.Accessible, **args) -> list[Any]:
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
    def _generate_math_script_superscript(self, obj: Atspi.Accessible, **args) -> list[Any]:
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
    def _generate_math_script_underscript(self, obj: Atspi.Accessible, **args) -> list[Any]:
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
    def _generate_math_script_overscript(self, obj: Atspi.Accessible, **args) -> list[Any]:
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
    def _generate_math_script_prescripts(self, obj: Atspi.Accessible, **args) -> list[Any]:
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
    def _generate_math_script_postscripts(self, obj: Atspi.Accessible, **args) -> list[Any]:
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
    def _generate_math_table_rows(self, obj: Atspi.Accessible, **args) -> list[Any]:
        result = []
        for row in AXObject.iter_children(obj):
            result.extend(self.generate(row, role=self._get_functional_role(row)))

        return result

    ############################### START-OF/END-OF ################################

    @log_generator_output
    def _generate_start_of_deletion(self, obj: Atspi.Accessible, **args) -> list[Any]:
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
    def _generate_end_of_deletion(self, obj: Atspi.Accessible, **args) -> list[Any]:
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
            suggestion,
            AXObject.get_child_count(suggestion) - 1,
        ):
            result.extend(self._generate_pause(obj, **args))
            result.extend([messages.CONTENT_SUGGESTION_END])
            result.extend(self.voice(SYSTEM, obj=obj, **args))

            container = AXObject.find_ancestor(obj, lambda x: bool(AXUtilities.get_details(x)))
            if AXUtilities.is_suggestion(container):
                result.extend(self._generate_pause(obj, **args))
                result.extend(self._generate_has_details(container))

        return result

    @log_generator_output
    def _generate_start_of_insertion(self, obj: Atspi.Accessible, **args) -> list[Any]:
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
    def _generate_end_of_insertion(self, obj: Atspi.Accessible, **args) -> list[Any]:
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
            suggestion,
            AXObject.get_child_count(suggestion) - 1,
        ):
            result.extend(self._generate_pause(obj, **args))
            result.extend([messages.CONTENT_SUGGESTION_END])
            result.extend(self.voice(SYSTEM, obj=obj, **args))

            container = AXObject.find_ancestor(obj, lambda x: bool(AXUtilities.get_details(x)))
            if AXUtilities.is_suggestion(container):
                result.extend(self._generate_pause(obj, **args))
                result.extend(self._generate_has_details(container))

        return result

    @log_generator_output
    def _generate_start_of_mark(self, obj: Atspi.Accessible, **args) -> list[Any]:
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
    def _generate_end_of_mark(self, obj: Atspi.Accessible, **args) -> list[Any]:
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
    def _generate_start_of_math_fenced(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        attrs = AXObject.get_attributes_dict(obj)
        fence_start = attrs.get("open", "(")
        result = [mathsymbols.get_character_name(fence_start)]
        result.extend(self.voice(DEFAULT, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_end_of_math_fenced(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        attrs = AXObject.get_attributes_dict(obj)
        fence_end = attrs.get("close", ")")
        result = [mathsymbols.get_character_name(fence_end)]
        result.extend(self.voice(DEFAULT, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_start_of_math_fraction(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        if AXUtilities.is_math_fraction_without_bar(obj):
            result = [messages.MATH_FRACTION_WITHOUT_BAR_START]
        else:
            result = [messages.MATH_FRACTION_START]
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_end_of_math_fraction(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        result = [messages.MATH_FRACTION_END]
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_start_of_math_root(self, obj: Atspi.Accessible, **args) -> list[Any]:
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
    def _generate_end_of_math_root(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        result = [messages.MATH_ROOT_END]
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_start_of_math_table(self, obj: Atspi.Accessible, **args) -> list[Any]:
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
    def _generate_end_of_math_table(self, obj: Atspi.Accessible, **args) -> list[Any]:
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
    def _generate_state_current(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        result = super()._generate_state_current(obj, **args)
        if result:
            result.extend(self.voice(STATE, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_state_checked(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        result = super()._generate_state_checked(obj, **args)
        if result:
            result.extend(self.voice(STATE, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_state_checked_for_switch(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        result = super()._generate_state_checked_for_switch(obj, **args)
        if result:
            result.extend(self.voice(STATE, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_state_checked_if_checkable(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        result = super()._generate_state_checked_if_checkable(obj, **args)
        if result:
            result.extend(self.voice(STATE, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_state_expanded(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        result = super()._generate_state_expanded(obj, **args)
        if result:
            result.extend(self.voice(STATE, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_state_has_popup(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if (
            self._only_speak_displayed_text()
            or not speech_presenter.get_presenter().use_verbose_speech()
        ):
            return []

        if AXUtilities.is_menu(obj) or not AXUtilities.has_popup(obj):
            return []

        return [messages.HAS_POPUP, self.voice(SYSTEM, obj=obj, **args)]

    @log_generator_output
    def _generate_state_invalid(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        result = super()._generate_state_invalid(obj, **args)
        if result:
            result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_state_multiselectable(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        result = super()._generate_state_multiselectable(obj, **args)
        if result:
            result.extend(self.voice(STATE, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_state_pressed(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        result = super()._generate_state_pressed(obj, **args)
        if result:
            result.extend(self.voice(STATE, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_state_read_only(self, obj: Atspi.Accessible, **args) -> list[Any]:
        result = super()._generate_state_read_only(obj, **args)
        if result:
            result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_state_required(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        if args.get("alreadyFocused"):
            return []

        result = super()._generate_state_required(obj, **args)
        if result:
            result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_state_selected_for_radio_button(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        result = super()._generate_state_selected_for_radio_button(obj, **args)
        if result:
            result.extend(self.voice(STATE, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_state_sensitive(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        result = super()._generate_state_sensitive(obj, **args)
        if result:
            result.extend(self.voice(STATE, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_state_unselected(self, obj: Atspi.Accessible, **args) -> list[Any]:
        role = args.get("role")
        if (
            self._only_speak_displayed_text()
            or args.get("inMouseReview")
            or not obj
            or not AXUtilities.is_selectable(obj)
            or AXUtilities.is_selected(obj)
            or AXUtilities.is_text(obj, role)
        ):
            return []

        if AXUtilities.is_list_item(obj, role):
            result = [object_properties.STATE_UNSELECTED_LIST_ITEM]
            result.extend(self.voice(STATE, obj=obj, **args))
            return result

        parent = AXObject.get_parent(obj)
        table = AXUtilities.get_table(obj)
        if table:
            if (
                input_event_manager.get_manager().last_event_was_left_or_right()
                or AXUtilities.is_layout_table(table)
                or not AXUtilities.is_gui_cell(obj)
            ):
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
    def _generate_nesting_level(self, obj: Atspi.Accessible, **args) -> list[Any]:
        result = super()._generate_nesting_level(obj, **args)
        if result:
            result.extend(self.voice(SYSTEM, obj=obj, **args))

        return result

    @log_generator_output
    def _generate_tree_item_level(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        args["newOnly"] = True
        result = super()._generate_tree_item_level(obj, **args)
        if result:
            result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    ################################ PROGRESS BARS ##################################

    @log_generator_output
    def _generate_progress_bar_index(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if not args.get("isProgressBarUpdate"):
            return []

        result = []
        acc = self._get_most_recent_progress_bar_update()[0]
        if acc != obj:
            number = self._get_progress_bar_number_and_count(obj)[0]
            result = [messages.PROGRESS_BAR_NUMBER % (number)]
            result.extend(self.voice(SYSTEM, obj=obj, **args))

        return result

    @log_generator_output
    def _generate_progress_bar_value(self, obj: Atspi.Accessible, **args) -> list[Any]:
        result = []
        percent = AXValue.get_value_as_percent(obj)
        if percent is not None:
            result.append(messages.percentage(percent))
            result.extend(self.voice(SYSTEM, obj=obj, **args))

        return result

    ##################################### TABLE #####################################

    # TODO - JD: This function and fake role really need to die....
    @log_generator_output
    def _generate_real_table_cell(self, obj: Atspi.Accessible, **args) -> list[Any]:
        result = super()._generate_real_table_cell(obj, **args)
        if (
            not (result and result[0])
            and speech_presenter.get_presenter().get_speak_blank_lines()
            and not args.get("readingRow", False)
            and args.get("formatType") != "ancestor"
        ):
            result.append(messages.BLANK)
            if result:
                result.extend(self.voice(DEFAULT, obj=obj, **args))
        elif has_formula := self._generate_has_formula(obj, **args):
            result.extend(self._generate_pause(obj, **args))
            result.extend(has_formula)

        return result

    @log_generator_output
    def _generate_table_cell_column_header(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if not speech_presenter.get_presenter().get_announce_cell_headers():
            return []

        if focus_manager.get_manager().in_say_all():
            return []

        if not AXUtilities.cell_column_changed(
            obj,
            args.get("priorObj"),
        ) and not args.get("formatType", "").endswith("WhereAmI"):
            return []

        args["newOnly"] = not self._get_is_nameless_toggle(obj)
        result = super()._generate_table_cell_column_header(obj, **args)
        if result:
            result.extend(self.voice(DEFAULT, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_table_cell_row_header(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if args.get("readingRow"):
            return []

        if not speech_presenter.get_presenter().get_announce_cell_headers():
            return []

        if focus_manager.get_manager().in_say_all():
            return []

        if not AXUtilities.cell_row_changed(obj, args.get("priorObj")) and not args.get(
            "formatType",
            "",
        ).endswith("WhereAmI"):
            return []

        args["newOnly"] = True
        result = super()._generate_table_cell_row_header(obj, **args)
        if result:
            result.extend(self.voice(DEFAULT, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_table_size(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if (
            self._only_speak_displayed_text()
            or args.get("leaving")
            or AXUtilities.is_layout_table(obj)
            or AXUtilities.is_spreadsheet_table(obj)
        ):
            return []

        if not speech_presenter.get_presenter().use_verbose_speech():
            return self._generate_accessible_role(obj, **args)

        if AXUtilities.is_text_document_table(obj):
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
    def _generate_table_sort_order(self, obj: Atspi.Accessible, **args) -> list[Any]:
        result = super()._generate_table_sort_order(obj, **args)
        if result:
            result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_table_cell_column_index(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if args.get("readingRow"):
            return []

        if not speech_presenter.get_presenter().get_announce_cell_coordinates():
            return []

        if not AXUtilities.cell_column_changed(obj):
            return []

        col = AXTable.get_cell_coordinates(obj, find_cell=True)[1]
        if col == -1:
            return []

        result = [messages.TABLE_COLUMN % (col + 1)]
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_table_cell_row_index(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if not AXUtilities.cell_row_changed(obj):
            return []

        if args.get("readingRow"):
            return []

        if not speech_presenter.get_presenter().get_announce_cell_coordinates():
            return []

        row = AXTable.get_cell_coordinates(obj, find_cell=True)[0]
        if row == -1:
            return []

        result = [messages.TABLE_ROW % (row + 1)]
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_table_cell_position(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        row, col = AXTable.get_cell_coordinates(obj, find_cell=True)
        if row == -1 or col == -1:
            return []

        table = AXUtilities.get_table(obj)
        if table is None:
            return []

        result = []
        rows = AXTable.get_row_count(table)
        columns = AXTable.get_column_count(table)

        result.append(messages.TABLE_COLUMN_DETAILED % {"index": (col + 1), "total": columns})
        result.append(messages.TABLE_ROW_DETAILED % {"index": (row + 1), "total": rows})
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    def _generate_has_formula(self, obj: Atspi.Accessible, **args) -> list[Any]:
        formula = AXUtilities.get_cell_formula(obj)
        if not formula:
            return []

        if args.get("formatType") == "basicWhereAmI":
            result: list[Any] = [f"{messages.HAS_FORMULA}. {formula}"]
        else:
            result = [messages.HAS_FORMULA]

        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    ##################################### TEXT ######################################

    @log_generator_output
    def _generate_text_substring(self, obj: Atspi.Accessible, **args) -> list[Any]:
        result = super()._generate_text_substring(obj, **args)
        if not result:
            return []

        result.extend(self.voice(DEFAULT, obj=obj, **args))
        if result[0] in ["\n", ""]:
            if args.get("total", 1) > 1:
                return [""]
            if (
                speech_presenter.get_presenter().get_speak_blank_lines()
                and not focus_manager.get_manager().in_say_all()
                and not AXUtilities.is_table_cell_or_header(obj)
                and args.get("formatType") != "ancestor"
            ):
                result[0] = messages.BLANK

        manager = speech_presenter.get_presenter()
        result[0] = manager.adjust_for_presentation(obj, result[0])
        return result

    @log_generator_output
    def _generate_text_line(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if args.get("inMouseReview") and AXUtilities.is_editable(obj):
            return []

        result = self._generate_text_substring(obj, **args)
        if result:
            return result

        text, start_offset = AXText.get_line_at_offset(obj)[0:2]
        if text == "\n":
            if args.get("total", 1) > 1:
                return [""]

            if (
                speech_presenter.get_presenter().get_speak_blank_lines()
                and not focus_manager.get_manager().in_say_all()
                and not AXUtilities.is_table_cell_or_header(obj)
                and args.get("formatType") != "ancestor"
            ):
                result = [messages.BLANK]
                result.extend(self.voice(string=text, obj=obj, **args))
                return result

        end_offset = start_offset + len(text)
        for (
            start,
            _end,
            string,
            language,
            dialect,
        ) in self._script.utilities.split_substring_by_language(obj, start_offset, end_offset):
            cleaned_string = string.replace("\ufffc", "")
            if not cleaned_string:
                continue
            args["language"], args["dialect"] = language, dialect
            if "string" in args:
                existing = args.get("string")
                msg = f"INFO: Found existing string '{existing}'; using '{cleaned_string}'"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                args.pop("string")

            voice = self.voice(string=cleaned_string, obj=obj, **args)
            manager = speech_presenter.get_presenter()
            rv: list[Any] = [manager.adjust_for_presentation(obj, cleaned_string, start)]
            rv.extend(voice)

            # TODO - JD: speech.speak() has a bug which causes a list of utterances to
            # be presented before a string+voice pair that comes first. Until we can
            # fix speak() properly, we'll avoid triggering it here.
            # result.append(rv)
            result.extend(rv)

        return result

    @log_generator_output
    def _generate_text_content(self, obj: Atspi.Accessible, **args) -> list[Any]:
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

        manager = speech_presenter.get_presenter()
        result[0] = manager.adjust_for_presentation(obj, result[0])
        result.extend(self.voice(DEFAULT, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_text_selection(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        if not AXUtilities.is_all_text_selected(obj):
            return []

        result = [messages.TEXT_SELECTED]
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    @log_generator_output
    def _generate_text_indentation(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if not speech_presenter.get_presenter().get_speak_indentation_and_justification():
            return []

        if input_event_manager.get_manager().last_event_was_word_navigation():
            return []

        format_type = args.get("formatType", "unfocused")
        only_if_changed = None
        if format_type.endswith("WhereAmI"):
            only_if_changed = False

        line = AXText.get_line_at_offset(obj, args.get("startOffset"))[0]
        description = speech_presenter.get_presenter().get_indentation_description(
            line,
            only_if_changed,
        )
        if not description:
            return []

        result: list[Any] = [description]
        result.extend(self.voice(SYSTEM, obj=obj, **args))
        return result

    ##################################### VALUE #####################################

    @log_generator_output
    def _generate_value(self, obj: Atspi.Accessible, **args) -> list[Any]:
        result = super()._generate_value(obj, **args)
        if result:
            result.extend(self.voice(DEFAULT, obj=obj, **args))

        return result

    @log_generator_output
    def _generate_value_as_percentage(self, obj: Atspi.Accessible, **args) -> list[Any]:
        if self._only_speak_displayed_text():
            return []

        percent_value = AXValue.get_value_as_percent(obj)
        if percent_value is not None:
            result = [messages.percentage(percent_value)]
            result.extend(self.voice(SYSTEM, obj=obj, **args))
            return result

        return []

    ################################### PER-ROLE ###################################

    def _generate_default_prefix(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Provides the default/role-agnostic information to present before obj."""

        if args.get("includeContext") is False:
            return []

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generate_details_for(obj, **args)
        if format_type == "unfocused":
            return self._generate_old_ancestors(obj, **args) + self._generate_new_ancestors(
                obj,
                **args,
            )
        if format_type == "detailedWhereAmI":
            return self._generate_ancestors(obj, **args)
        return []

    def _generate_default_presentation(self, obj: Atspi.Accessible, **args) -> list[Any]:
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

    def _generate_default_suffix(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Provides the default/role-agnostic information to present after obj."""

        if args.get("includeContext") is False:
            return []

        if obj == args.get("priorObj"):
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
        if cell := AXObject.find_ancestor(obj, AXUtilities.is_table_cell):
            result += self._generate_has_formula(cell, **args)
            if result and not isinstance(result[-1], Pause):
                result += self._generate_pause(obj, **args)
        if format_type == "unfocused":
            result += self._generate_tutorial(obj, **args)

        return result

    def _generate_accelerator_label(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the accelerator-label role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_alert(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the alert role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_accessible_static_text(obj, **args)
        return result

    def _generate_animation(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the animation role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_application(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the application role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_arrow(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the arrow role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_article(self, obj: Atspi.Accessible, **args) -> list[Any]:
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

    def _generate_article_in_feed(self, obj: Atspi.Accessible, **args) -> list[Any]:
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

    def _generate_audio(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the audio role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_autocomplete(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the autocomplete role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_block_quote(self, obj: Atspi.Accessible, **args) -> list[Any]:
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

    def _generate_calendar(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the calendar role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_canvas(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the canvas role."""

        result = self._generate_default_prefix(obj, **args)
        format_type = args.get("formatType", "unfocused")
        if format_type.endswith("WhereAmI"):
            result += self._generate_parent_role_name(obj, **args)
            result += self._generate_pause(obj, **args)

        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_accessible_image_description(
            obj,
            **args,
        ) or self._generate_accessible_role(obj, **args)
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

    def _generate_caption(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the caption role."""

        result = []
        if self._generate_text_substring(obj, **args):
            result += self._generate_text_line(obj, **args)
        if not result:
            result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return self._generate_default_prefix(obj, **args) + result

    def _generate_chart(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the chart role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_check_box(self, obj: Atspi.Accessible, **args) -> list[Any]:
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

    def _generate_check_menu_item(self, obj: Atspi.Accessible, **args) -> list[Any]:
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

    def _generate_color_chooser(self, obj: Atspi.Accessible, **args) -> list[Any]:
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

        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_column_header(self, obj: Atspi.Accessible, **args) -> list[Any]:
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

    def _generate_combo_box(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the combo-box role."""

        result = []
        label_and_name = self._generate_accessible_label_and_name(obj, **args)
        result += label_and_name
        result += self._generate_accessible_role(obj, **args)
        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            result += self._generate_state_expanded(obj, **args)
            return result

        value = self._generate_value(obj, **args)
        if value and value[0] and value[0] not in label_and_name:
            result += value
        result += self._generate_pause(obj, **args)
        result += self._generate_position_in_list(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_state_required(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_state_invalid(obj, **args)
        result += self._generate_keyboard_mnemonic(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return self._generate_default_prefix(obj, **args) + result

    def _generate_comment(self, obj: Atspi.Accessible, **args) -> list[Any]:
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

    def _generate_content_deletion(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the content-deletion role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generate_leaving(obj, **args) or self._generate_start_of_deletion(
                obj,
                **args,
            )

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_start_of_deletion(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_text_content(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_end_of_deletion(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_content_insertion(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the content-insertion role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generate_leaving(obj, **args) or self._generate_start_of_insertion(
                obj,
                **args,
            )

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_start_of_insertion(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_text_content(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_end_of_insertion(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_date_editor(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the date-editor role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_definition(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the definition role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_text_content(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_description_list(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the description-list role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            result = self._generate_leaving(obj, **args)
            if result:
                return result

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_number_of_children(obj, **args) or self._generate_accessible_role(
            obj,
            **args,
        )
        result += self._generate_nesting_level(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_description_term(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the description-term role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return []

        result = self._generate_default_prefix(obj, **args)

        if self._generate_text_substring(obj, **args):
            result += self._generate_text_line(obj, **args)
        else:
            result += self._generate_accessible_label_and_name(
                obj,
                **args,
            ) or self._generate_text_line(obj, **args)

        if speech_presenter.get_presenter().get_announce_list():
            if args.get("index", 0) + 1 < args.get("total", 1):
                return result

            result += self._generate_accessible_role(obj, **args)
            result += self._generate_pause(obj, **args)
            result += self._generate_term_value_count(obj, **args)
            result += self._generate_pause(obj, **args)
            result += self._generate_position_in_list(obj, **args)

        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_description_value(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the description-value role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return []

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args) or self._generate_text_line(
            obj,
            **args,
        )

        if speech_presenter.get_presenter().get_announce_list():
            if args.get("index", 0) + 1 < args.get("total", 1):
                return result

            result += self._generate_accessible_role(obj, **args)
            result += self._generate_pause(obj, **args)
            result += self._generate_position_in_list(obj, **args)

        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_desktop_frame(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the desktop-frame role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_desktop_icon(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the desktop-icon role."""

        return self._generate_icon(obj, **args)

    def _generate_dial(self, obj: Atspi.Accessible, **args) -> list[Any]:
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

    def _generate_dialog(self, obj: Atspi.Accessible, **args) -> list[Any]:
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

    def _generate_directory_pane(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the directory_pane role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_document(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for document-related roles."""

        result = []
        prior_doc = None
        if prior_obj := args.get("priorObj"):
            prior_doc = AXObject.find_ancestor_inclusive(prior_obj, AXUtilities.is_document)

        if prior_doc != obj:
            result += self._generate_default_prefix(obj, **args)
            result += self._generate_accessible_label_and_name(obj, **args)
            result += self._generate_state_read_only(obj, **args)
            result += self._generate_accessible_role(obj, **args)

        result += self._generate_text_line(obj, **args)

        if prior_doc != obj:
            result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_document_email(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the document-email role."""

        return self._generate_document(obj, **args)

    def _generate_document_frame(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the document-frame role."""

        return self._generate_document(obj, **args)

    def _generate_document_presentation(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the document-presentation role."""

        return self._generate_document(obj, **args)

    def _generate_document_spreadsheet(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the document-spreadsheet role."""

        return self._generate_document(obj, **args)

    def _generate_document_text(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the document-text role."""

        return self._generate_document(obj, **args)

    def _generate_document_web(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the document-web role."""

        return self._generate_document(obj, **args)

    def _generate_dpub_landmark(self, obj: Atspi.Accessible, **args) -> list[Any]:
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

    def _generate_dpub_section(self, obj: Atspi.Accessible, **args) -> list[Any]:
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

    def _generate_drawing_area(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the drawing-area role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_editbar(self, obj: Atspi.Accessible, **args) -> list[Any]:
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

    def _generate_embedded(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the embedded role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)

        format_type = args.get("formatType", "unfocused")
        if format_type != "focused":
            result += self._generate_text_expanding_embedded_objects(
                obj,
                **args,
            ) or self._generate_accessible_static_text(obj, **args)

        result += self._generate_accessible_role(obj, **args)
        result += self._generate_state_sensitive(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_entry(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the entry role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_state_read_only(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_text_indentation(obj, **args)
        result += self._generate_text_line(
            obj,
            **args,
        ) or self._generate_accessible_placeholder_text(obj, **args)
        result += self._generate_text_selection(obj, **args)
        result += self._generate_state_required(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_state_invalid(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_keyboard_mnemonic(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_feed(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the feed role."""

        result = self._generate_default_prefix(obj, **args)
        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            result += self._generate_leaving(obj, **args)
            if result:
                return result

        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_number_of_children(obj, **args) or self._generate_accessible_role(
            obj,
            **args,
        )
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_file_chooser(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the file-chooser role."""

        return self._generate_dialog(obj, **args)

    def _generate_filler(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the filler role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_font_chooser(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the font-chooser role."""

        return self._generate_dialog(obj, **args)

    def _generate_footer(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the footer role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_text_line(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_footnote(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the footnote role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_text_line(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_form(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the form role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generate_leaving(obj, **args) or (
                self._generate_accessible_label_and_name(obj, **args)
                + self._generate_accessible_role(obj, **args)
            )

        result = self._generate_default_prefix(obj, **args)
        if self._generate_text_substring(obj, **args):
            result += self._generate_text_line(obj, **args)
        else:
            result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_frame(self, obj: Atspi.Accessible, **args) -> list[Any]:
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

    def _generate_glass_pane(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the glass-pane role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_grouping(self, obj: Atspi.Accessible, **args) -> list[Any]:
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

    def _generate_header(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the header role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_text_line(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_heading(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the heading role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_text_content(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_state_expanded(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_html_container(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the html-container role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_icon(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the icon role."""

        result = self._generate_default_prefix(obj, **args)
        format_type = args.get("formatType", "unfocused")
        if format_type.endswith("WhereAmI"):
            result += self._generate_parent_role_name(obj, **args)
            result += self._generate_pause(obj, **args)

        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_accessible_image_description(
            obj,
            **args,
        ) or self._generate_accessible_role(obj, **args)
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

    def _generate_image(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the image role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_has_long_description(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_image_map(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the image-map role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_info_bar(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the info-bar role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_accessible_static_text(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_input_method_window(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the input-method-window role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_internal_frame(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the internal-frame role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_label(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the label role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label(obj, **args)
        result += self._generate_text_content(obj) or self._generate_accessible_name(obj)
        result += self._generate_text_selection(obj)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_landmark(self, obj: Atspi.Accessible, **args) -> list[Any]:
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

    def _generate_layered_pane(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the layered-pane role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(
            obj,
            **args,
        ) or self._generate_accessible_role(obj, **args)
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

    def _generate_level_bar(self, obj: Atspi.Accessible, **args) -> list[Any]:
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

    def _generate_link(self, obj: Atspi.Accessible, **args) -> list[Any]:
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

        result += self._generate_accessible_label_and_name(
            obj,
            **args,
        ) or self._generate_text_content(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_state_expanded(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_keyboard_mnemonic(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_keyboard_accelerator(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_list(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the list role."""

        result = self._generate_default_prefix(obj, **args)
        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            result += self._generate_leaving(obj, **args)
            if result:
                return result

        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_number_of_children(obj, **args) or self._generate_accessible_role(
            obj,
            **args,
        )
        if AXUtilities.is_gui_list(obj):
            result += self._generate_accessible_static_text(obj, **args)
        else:
            result += self._generate_nesting_level(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_list_box(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the list-box role."""

        result = self._generate_default_prefix(obj, **args)
        format_type = args.get("formatType", "unfocused")
        result += self._generate_accessible_label_and_name(obj, **args)

        if format_type not in ["focused", "ancestor"]:
            result += self._generate_focused_item(obj, **args)
            result += self._generate_pause(obj, **args)

        result += self._generate_state_multiselectable(obj, **args)
        result += self._generate_number_of_children(obj, **args) or self._generate_accessible_role(
            obj,
            **args,
        )
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_list_item(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the list-item role."""

        result = self._generate_default_prefix(obj, **args)
        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            result += self._generate_state_checked_if_checkable(obj, **args)
            result += self._generate_pause(obj, **args)
            result += self._generate_state_expanded(obj, **args)
            return result

        result += self._generate_text_line(obj, **args) or self._generate_accessible_label_and_name(
            obj,
            **args,
        )
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

    def _generate_log(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the log role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_mark(self, obj: Atspi.Accessible, **args) -> list[Any]:
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

    def _generate_marquee(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the marquee role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_math(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the math role."""

        # TODO - JD: Move this logic here.
        return self._generate_math_contents(obj, **args)

    def _generate_math_enclosed(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the math-enclosed role."""

        result = []
        result += self._generate_math_contents(obj, **args)
        # TODO - JD: Move this logic here.
        result += self._generate_math_enclosed_enclosures(obj, **args)
        return result

    def _generate_math_fenced(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the math-fenced role."""

        # TODO - JD: Move the logic from these functions here.

        result = []
        result += self._generate_start_of_math_fenced(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_math_fenced_contents(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_end_of_math_fenced(obj, **args)
        return result

    def _generate_math_fraction(self, obj: Atspi.Accessible, **args) -> list[Any]:
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

    def _generate_math_multiscript(self, obj: Atspi.Accessible, **args) -> list[Any]:
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

    def _generate_math_root(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the math-root role."""

        # TODO - JD: Move the logic from these functions here.

        result = []
        result += self._generate_start_of_math_root(obj, **args)
        result += self._generate_math_root_base(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_end_of_math_root(obj, **args)
        result += self._generate_pause(obj, **args)
        return result

    def _generate_math_row(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the math-row role."""

        result = [messages.TABLE_ROW % (AXObject.get_index_in_parent(obj) + 1)]
        result += self.voice(SYSTEM, obj=obj, **args)
        result += self._generate_pause(obj, **args)
        for child in AXObject.iter_children(obj):
            result += self._generate_math_contents(child)
            result += self._generate_pause(child, **args)
        return result

    def _generate_math_script_subsuper(self, obj: Atspi.Accessible, **args) -> list[Any]:
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

    def _generate_math_script_underover(self, obj: Atspi.Accessible, **args) -> list[Any]:
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

    def _generate_math_table(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the math-table role."""

        # TODO - JD: Move the logic from these functions here.

        result = []
        result += self._generate_start_of_math_table(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_math_table_rows(obj, **args)
        result += self._generate_end_of_math_table(obj, **args)
        result += self._generate_pause(obj, **args)
        return result

    def _generate_menu(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the menu role."""

        result = self._generate_default_prefix(obj, **args)
        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            result += self._generate_accessible_label_and_name(obj, **args)
            result += self._generate_accessible_role(obj, **args)
            return result

        if format_type.endswith("WhereAmI"):
            result += self._generate_ancestors(obj, **args) or self._generate_parent_role_name(
                obj,
                **args,
            )
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

    def _generate_menu_bar(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the menu-bar role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_menu_item(self, obj: Atspi.Accessible, **args) -> list[Any]:
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

    def _generate_notification(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the notification role."""

        # TODO - JD: Should this instead or also be using the logic in get_notification_content()?
        result = []
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_text_expanding_embedded_objects(
            obj,
            **args,
        ) or self._generate_accessible_static_text(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_option_pane(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the option-pane role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_page(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the page role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_state_read_only(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_text_line(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_page_tab(self, obj: Atspi.Accessible, **args) -> list[Any]:
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

    def _generate_page_tab_list(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the page-tab-list role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_panel(self, obj: Atspi.Accessible, **args) -> list[Any]:
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

    def _generate_paragraph(self, obj: Atspi.Accessible, **args) -> list[Any]:
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

    def _generate_password_text(self, obj: Atspi.Accessible, **args) -> list[Any]:
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

    def _generate_popup_menu(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the popup-menu role."""

        return self._generate_menu(obj, **args)

    def _generate_progress_bar(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the progress-bar role."""

        result = []
        result += self._generate_progress_bar_index(obj, **args)
        format_type = args.get("formatType", "unfocused")
        if format_type != "focused":
            result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_progress_bar_value(obj, **args) or self._generate_accessible_role(
            obj,
            **args,
        )
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_push_button(self, obj: Atspi.Accessible, **args) -> list[Any]:
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

    def _generate_push_button_menu(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the push-button-menu role."""

        return self._generate_push_button(obj, **args)

    def _generate_radio_button(self, obj: Atspi.Accessible, **args) -> list[Any]:
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

    def _generate_radio_menu_item(self, obj: Atspi.Accessible, **args) -> list[Any]:
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

    def _generate_rating(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the rating role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_region(self, obj: Atspi.Accessible, **args) -> list[Any]:
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

    def _generate_root_pane(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the root-pane role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_row_header(self, obj: Atspi.Accessible, **args) -> list[Any]:
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

    def _generate_ruler(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the ruler role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_scroll_bar(self, obj: Atspi.Accessible, **args) -> list[Any]:
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

    def _generate_scroll_pane(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the scroll-pane role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_text_line(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_section(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the section role."""

        # pylint: disable-next=import-outside-toplevel
        from . import document_presenter

        format_type = args.get("formatType", "unfocused")
        result = self._generate_default_prefix(obj, **args)
        if AXUtilities.is_focusable(obj) and (
            AXUtilities.has_explicit_name(obj)
            or document_presenter.get_presenter().get_in_focus_mode()
        ):
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

    def _generate_separator(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the separator role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_state_sensitive(obj, **args)

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return result

        result += (
            self._generate_accessible_label_and_name(obj, **args)
            or self._generate_text_content(obj, **args)
            or self._generate_value(obj, **args)
        )
        result += self._generate_pause(obj, **args)
        result += self._generate_keyboard_mnemonic(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_slider(self, obj: Atspi.Accessible, **args) -> list[Any]:
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

    def _generate_spin_button(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the spin-button role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generate_text_content(obj, **args) or self._generate_value(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args) + result
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_text_content(obj, **args) or self._generate_value(obj, **args)
        result += self._generate_state_required(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_state_invalid(obj, **args)
        result += self._generate_state_sensitive(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_keyboard_mnemonic(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_split_pane(self, obj: Atspi.Accessible, **args) -> list[Any]:
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

    def _generate_static(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the static role."""

        result = self._generate_default_prefix(obj, **args)
        if AXUtilities.is_code(obj):
            result += self._generate_text_indentation(obj, **args)
            result += self._generate_text_line(obj, **args)
        else:
            result += self._generate_text_content(obj, **args) or self._generate_accessible_name(
                obj,
                **args,
            )
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_status_bar(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the status-bar role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_accessible_role(obj, **args)

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return result

        content = self._generate_descendants(obj, **args) or self._generate_text_content(
            obj,
            **args,
        )
        if not content and AXObject.get_child_count(obj) == 1:
            content = self._generate_text_content(AXObject.get_child(obj, 0), **args)
        if content:
            result += self._generate_pause(obj, **args) + content

        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_subscript(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the subscript role."""

        result = []
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_text_line(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_suggestion(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the suggestion role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generate_leaving(obj, **args) or self._generate_accessible_role(
                obj,
                **args,
            )

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_text_content(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_superscript(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the superscript role."""

        result = []
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_text_line(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_switch(self, obj: Atspi.Accessible, **args) -> list[Any]:
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

    def _generate_table(self, obj: Atspi.Accessible, **args) -> list[Any]:
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

    def _generate_table_cell(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the table-cell role."""

        # TODO - JD: There should be separate generators for each type of cell.
        result = self._generate_default_prefix(obj, **args)
        result += self._generate_table_cell_row_header(obj, **args)
        result += self._generate_table_cell_column_header(obj, **args)
        result += self._generate_state_checked_for_cell(obj, **args)
        result += (
            self._generate_real_active_descendant_displayed_text(obj, **args)
            or self._generate_accessible_label_and_name(obj, **args)
            or self._generate_accessible_image_description(obj, **args)
        )
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

    def _generate_table_cell_in_row(self, obj: Atspi.Accessible, **args) -> list[Any]:
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

    def _generate_table_column_header(self, obj: Atspi.Accessible, **args) -> list[Any]:
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

    def _generate_table_row(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the table-row role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generate_state_expanded(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(
            obj,
            **args,
        ) or self._generate_text_content(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_state_expanded(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_position_in_list(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_table_row_header(self, obj: Atspi.Accessible, **args) -> list[Any]:
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

    def _generate_tearoff_menu_item(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the tearoff-menu-item role."""

        return self._generate_menu_item(obj, **args)

    def _generate_terminal(self, obj: Atspi.Accessible, **args) -> list[Any]:
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

    def _generate_text(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the text role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_state_read_only(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_text_indentation(obj, **args)
        result += self._generate_text_line(
            obj,
            **args,
        ) or self._generate_accessible_placeholder_text(obj, **args)
        result += self._generate_text_selection(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_keyboard_mnemonic(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_timer(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the timer role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_title_bar(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the title-bar role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_toggle_button(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the toggle-button role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generate_state_expanded(obj, **args) or self._generate_state_pressed(
                obj,
                **args,
            )

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_state_expanded(obj, **args) or self._generate_state_pressed(
            obj,
            **args,
        )
        result += self._generate_state_sensitive(obj, **args)
        result += self._generate_pause(obj, **args)
        result += self._generate_keyboard_mnemonic(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_tool_bar(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the tool-bar role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_tool_tip(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the tool-tip role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generate_leaving(obj, **args) or self._generate_accessible_role(
                obj,
                **args,
            )

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_role(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_tree(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the tree role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_tree_item(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the tree-item role."""

        format_type = args.get("formatType", "unfocused")
        if format_type in ["focused", "ancestor"]:
            return self._generate_state_expanded(obj, **args)

        result = self._generate_default_prefix(obj, **args)
        if format_type.endswith("WhereAmI"):
            result += self._generate_ancestors(obj, **args)
            result += self._generate_pause(obj, **args)

        result += self._generate_accessible_label_and_name(
            obj,
            **args,
        ) or self._generate_text_content(obj, **args)
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

    def _generate_tree_table(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the tree-table role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_unknown(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the unknown role."""

        result = self._generate_default_prefix(obj, **args)
        result += self._generate_accessible_label_and_name(obj, **args)
        result += self._generate_default_suffix(obj, **args)
        return result

    def _generate_video(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the video role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_viewport(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the viewport role."""

        return self._generate_default_presentation(obj, **args)

    def _generate_window(self, obj: Atspi.Accessible, **args) -> list[Any]:
        """Generates speech for the window role."""

        return self._generate_default_presentation(obj, **args)

    def generate_contents(
        self,
        contents: list[tuple[Atspi.Accessible, int, int, str]],
        **args,
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
            if (
                focus_manager.get_manager().in_say_all()
                or not speech_presenter.get_presenter().get_speak_blank_lines()
                or args.get("formatType") == "ancestor"
            ):
                string = ""
            else:
                string = messages.BLANK
            result = [[string, self.voice(DEFAULT, **args)]]

        return result

    def generate_line(
        self,
        obj: Atspi.Accessible,
        start_offset: int,
        end_offset: int,
        line: str,
    ) -> list[Any]:
        """Generates speech for a line of text, handling language splitting and voice selection."""

        if not line or line == "\n":
            if not speech_presenter.get_presenter().get_speak_blank_lines():
                return []
            return [messages.BLANK, self.voice(DEFAULT)]

        presenter = speech_presenter.get_presenter()
        split = self._script.utilities.split_substring_by_language(obj, start_offset, end_offset)
        if not split:
            text = presenter.adjust_for_presentation(obj, line)
            return [text, self.voice(obj=obj, string=text)]

        result: list[Any] = []
        for start, _end, text, language, dialect in split:
            if not text:
                continue
            adjusted_text = presenter.adjust_for_presentation(obj, text, start).lstrip()
            if not adjusted_text:
                continue
            voice = self.voice(obj=obj, string=adjusted_text, language=language, dialect=dialect)
            result.extend([adjusted_text, voice])

        return result

    def generate_phrase(
        self,
        obj: Atspi.Accessible,
        start_offset: int,
        end_offset: int,
        phrase: str,
    ) -> list[Any]:
        """Generates speech for a phrase of text with voice selection and text adjustment."""

        presenter = speech_presenter.get_presenter()
        text = presenter.adjust_for_presentation(obj, phrase)
        if not text:
            return []
        voice = self.voice(obj=obj, string=text)
        return [text, voice]

    def generate_word(self, obj: Atspi.Accessible, offset: int) -> list[Any]:
        """Generates speech for a word at offset. Overridden by web for DOM-walking."""

        return []
