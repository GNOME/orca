# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
# Copyright 2011-2025 Igalia, S.L.
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
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-instance-attributes

"""Module for commands related to the current accessible object."""

from __future__ import annotations

import unicodedata
from enum import Enum
from typing import TYPE_CHECKING

from . import (
    ax_event_synthesizer,
    cmdnames,
    command_manager,
    dbus_service,
    debug,
    focus_manager,
    gsettings_registry,
    guilabels,
    input_event,
    input_event_manager,
    keybindings,
    messages,
    preferences_grid_base,
    presentation_manager,
    speech_presenter,
    speechserver,
    structural_navigator,
)
from .acss import ACSS
from .ax_object import AXObject
from .ax_text import AXText
from .ax_utilities import AXUtilities

if TYPE_CHECKING:
    from collections.abc import Generator

    import gi

    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

    from .scripts import default


@gsettings_registry.get_registry().gsettings_enum(
    "org.gnome.Orca.SayAllStyle",
    values={"line": 0, "sentence": 1},
)
class SayAllStyle(Enum):
    """Style enumeration with int values from settings."""

    SENTENCE = 1
    LINE = 0

    @property
    def string_name(self) -> str:
        """Returns the lowercase string name for this enum value."""

        return self.name.lower()


class SayAllPreferencesGrid(preferences_grid_base.AutoPreferencesGrid):
    """GtkGrid containing the Say All preferences page."""

    _gsettings_schema = "say-all"

    def __init__(self, presenter: SayAllPresenter) -> None:
        self._only_speak_displayed_control = preferences_grid_base.BooleanPreferenceControl(
            label=guilabels.SPEECH_ONLY_SPEAK_DISPLAYED_TEXT,
            getter=presenter.get_only_speak_displayed_text,
            setter=presenter.set_only_speak_displayed_text,
            prefs_key="only-speak-displayed-text",
            member_of=guilabels.ANNOUNCEMENTS,
        )

        controls: list[preferences_grid_base.ControlType] = [
            preferences_grid_base.EnumPreferenceControl(
                label=guilabels.SAY_ALL_BY,
                options=[guilabels.SAY_ALL_STYLE_SENTENCE, guilabels.SAY_ALL_STYLE_LINE],
                values=[SayAllStyle.SENTENCE.value, SayAllStyle.LINE.value],
                getter=presenter.get_style_as_int,
                setter=presenter.set_style_from_int,
                prefs_key="style",
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.SAY_ALL_UP_AND_DOWN_ARROW,
                getter=presenter.get_rewind_and_fast_forward_enabled,
                setter=presenter.set_rewind_and_fast_forward_enabled,
                prefs_key="rewind-and-fast-forward",
                member_of=guilabels.SAY_ALL_REWIND_AND_FAST_FORWARD_BY,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.SAY_ALL_STRUCTURAL_NAVIGATION,
                getter=presenter.get_structural_navigation_enabled,
                setter=presenter.set_structural_navigation_enabled,
                prefs_key="structural-navigation",
                member_of=guilabels.SAY_ALL_REWIND_AND_FAST_FORWARD_BY,
            ),
            self._only_speak_displayed_control,
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.ANNOUNCE_BLOCKQUOTES,
                getter=presenter.get_announce_blockquote,
                setter=presenter.set_announce_blockquote,
                prefs_key="announce-blockquote",
                member_of=guilabels.ANNOUNCEMENTS,
                determine_sensitivity=self._only_speak_displayed_text_is_off,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.ANNOUNCE_FORMS,
                getter=presenter.get_announce_form,
                setter=presenter.set_announce_form,
                prefs_key="announce-form",
                member_of=guilabels.ANNOUNCEMENTS,
                determine_sensitivity=self._only_speak_displayed_text_is_off,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.ANNOUNCE_LANDMARKS,
                getter=presenter.get_announce_landmark,
                setter=presenter.set_announce_landmark,
                prefs_key="announce-landmark",
                member_of=guilabels.ANNOUNCEMENTS,
                determine_sensitivity=self._only_speak_displayed_text_is_off,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.ANNOUNCE_LISTS,
                getter=presenter.get_announce_list,
                setter=presenter.set_announce_list,
                prefs_key="announce-list",
                member_of=guilabels.ANNOUNCEMENTS,
                determine_sensitivity=self._only_speak_displayed_text_is_off,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.ANNOUNCE_PANELS,
                getter=presenter.get_announce_grouping,
                setter=presenter.set_announce_grouping,
                prefs_key="announce-grouping",
                member_of=guilabels.ANNOUNCEMENTS,
                determine_sensitivity=self._only_speak_displayed_text_is_off,
            ),
            preferences_grid_base.BooleanPreferenceControl(
                label=guilabels.ANNOUNCE_TABLES,
                getter=presenter.get_announce_table,
                setter=presenter.set_announce_table,
                prefs_key="announce-table",
                member_of=guilabels.ANNOUNCEMENTS,
                determine_sensitivity=self._only_speak_displayed_text_is_off,
            ),
        ]

        info = (
            f"{guilabels.SAY_ALL_INFO}\n\n{guilabels.SAY_ALL_NAVIGATION_INFO}"
            f"\n\n{guilabels.SAY_ALL_CONTAINER_INFO}"
        )
        super().__init__(guilabels.GENERAL_SAY_ALL, controls, info_message=info)

    def _only_speak_displayed_text_is_off(self) -> bool:
        """Returns True if only-speak-displayed-text is off in the UI."""

        widget = self.get_widget_for_control(self._only_speak_displayed_control)
        if widget:
            return not widget.get_active()
        return True


@gsettings_registry.get_registry().gsettings_schema("org.gnome.Orca.SayAll", name="say-all")
class SayAllPresenter:
    """Module for commands related to the current accessible object."""

    _SCHEMA = "say-all"

    def _get_setting(self, key: str, default: bool) -> bool:
        """Returns the dconf value for key, or default if not in dconf."""

        return gsettings_registry.get_registry().layered_lookup(
            self._SCHEMA,
            key,
            "b",
            default=default,
        )

    def __init__(self) -> None:
        self._script: default.Script | None = None
        self._contents: list[tuple[Atspi.Accessible, int, int, str]] = []
        self._contexts: list[speechserver.SayAllContext] = []
        self._current_context: speechserver.SayAllContext | None = None
        self._say_all_is_running: bool = False
        self._initialized: bool = False

        msg = "SAY ALL PRESENTER: Registering D-Bus commands."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        controller = dbus_service.get_remote_controller()
        controller.register_decorated_module("SayAllPresenter", self)

    def set_up_commands(self) -> None:
        """Sets up commands with CommandManager."""

        if self._initialized:
            return
        self._initialized = True

        manager = command_manager.get_manager()
        group_label = guilabels.KB_GROUP_DEFAULT

        # Layout-specific keybindings
        kb_desktop = keybindings.KeyBinding("KP_Add", keybindings.NO_MODIFIER_MASK)
        kb_laptop = keybindings.KeyBinding("semicolon", keybindings.ORCA_MODIFIER_MASK)

        manager.add_command(
            command_manager.KeyboardCommand(
                "sayAllHandler",
                self.say_all,
                group_label,
                cmdnames.SAY_ALL,
                desktop_keybinding=kb_desktop,
                laptop_keybinding=kb_laptop,
            ),
        )

        msg = "SAY ALL PRESENTER: Commands set up."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def create_preferences_grid(self) -> SayAllPreferencesGrid:
        """Returns the GtkGrid containing the Say All preferences UI."""

        return SayAllPreferencesGrid(self)

    def get_style_as_int(self) -> int:
        """Returns the current Say All style as an integer value."""

        style_name = self.get_style()
        return SayAllStyle[style_name.upper()].value

    def set_style_from_int(self, value: int) -> bool:
        """Sets the Say All style from an integer value."""

        msg = f"SAY ALL PRESENTER: Setting style to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        style_name = SayAllStyle(value).string_name
        gsettings_registry.get_registry().set_runtime_value(self._SCHEMA, "style", style_name)
        return True

    @dbus_service.command
    def say_all(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
        obj: Atspi.Accessible | None = None,
        offset: int | None = None,
    ) -> bool:
        """Speaks the entire document or text, starting from the current position."""

        self._contexts = []
        self._contents = []
        self._current_context = None
        self._say_all_is_running = False

        tokens = [
            "SAY ALL PRESENTER: say_all. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._script = script
        presentation_manager.get_manager().interrupt_presentation()
        obj = obj or focus_manager.get_manager().get_locus_of_focus()
        if not obj or AXObject.is_dead(obj):
            presentation_manager.get_manager().present_message(messages.LOCATION_NOT_FOUND_FULL)
            return True

        speech_presenter.get_presenter().say_all(
            self._say_all_iter(obj, offset),
            self._progress_callback,
        )
        return True

    @dbus_service.command
    def rewind(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Jumps back in the current Say All."""

        tokens = [
            "SAY ALL PRESENTER: rewind. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return self._rewind(None, True)

    @dbus_service.command
    def fast_forward(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Jumps forward in the current Say All."""

        tokens = [
            "SAY ALL PRESENTER: fast_forward. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return self._fast_forward(None, True)

    def stop(self) -> None:
        """Stops the current Say All."""

        self._contexts = []
        self._contents = []
        self._current_context = None
        self._say_all_is_running = False
        focus_manager.get_manager().reset_active_mode("SAY ALL PRESENTER: Stopped Say All.")

    def _parse_utterances(
        self,
        utterances: list[str | ACSS | list],
    ) -> tuple[list[str], list[ACSS]]:
        """Parse utterances into elements and voices lists."""

        # TODO - JD: This is a workaround from the web script. Ideally, the speech servers' say-all
        # would be able to handle more complex utterances.
        elements, voices = [], []
        for u in utterances:
            if isinstance(u, list):
                e, v = self._parse_utterances(u)
                elements.extend(e)
                voices.extend(v)
            elif isinstance(u, str):
                elements.append(u)
            elif isinstance(u, ACSS):
                voices.append(u)
        return elements, voices

    def _say_all_should_skip_content(
        self,
        content: tuple[Atspi.Accessible, int, int, str],
        contents: list[tuple[Atspi.Accessible, int, int, str]],  # pylint: disable=unused-argument
    ) -> tuple[bool, str]:
        """Returns True if content should be skipped during say-all iteration."""

        obj, start_offset, end_offset, _text = content
        if start_offset == end_offset:
            return True, "start_offset equals end_offset"
        if AXUtilities.get_is_label_for(obj) and not AXUtilities.is_focusable(obj):
            return True, "is non-focusable label for other object"
        stripped = _text.strip()
        if stripped and all(unicodedata.category(c).startswith("P") for c in stripped):
            return True, "is punctuation only"
        return False, ""

    def _advance_to_next(
        self,
        obj: Atspi.Accessible,
        _offset: int,
        contents: list,
        restrict_to: Atspi.Accessible | None,
    ) -> tuple[Atspi.Accessible | None, int]:
        """Advances to the next content position during say-all iteration."""

        assert self._script is not None
        if contents:
            last_obj, last_offset = contents[-1][0], contents[-1][2]
            # last_offset is the start of the next text unit (per AT-SPI2 semantics).
            # next_context() looks for the position after the provided offset. In the case of
            # text, we will wind up with the same text unit for last_offset and last_offset - 1.
            # However, if the character at last_offset is an embedded object, we'll skip over
            # its contents if we pass last_offset directly. Only decrement in that case so that
            # next_context() can still cross object boundaries at end of text.
            if AXUtilities.character_at_offset_is_eoc(last_obj, last_offset):
                last_offset = max(0, last_offset - 1)
            next_obj, next_offset = self._script.utilities.next_context(
                last_obj,
                last_offset,
                restrict_to=restrict_to,
            )
        else:
            next_obj = self._script.utilities.find_next_object(obj, restrict_to)
            next_offset = 0

        if next_obj is not None:
            tokens = ["SAY ALL PRESENTER: Updating focus to", next_obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            focus_manager.get_manager().set_locus_of_focus(None, next_obj, notify_script=False)

        return next_obj, next_offset

    def _build_displayed_text_context(
        self,
        contents: list[tuple[Atspi.Accessible, int, int, str]],
    ) -> tuple[speechserver.SayAllContext, ACSS] | None:
        """Returns a single SayAllContext from displayed text, or None if empty."""

        assert self._script is not None

        parts: list[str] = []
        first_obj, first_start, last_end = None, 0, 0
        for content in contents:
            content_obj, start, end, _text = content
            skip, _reason = self._say_all_should_skip_content(content, contents)
            if skip:
                continue
            expanded = self._script.utilities.expand_eocs(content_obj, start, end)
            if not expanded.strip():
                continue
            if first_obj is None:
                first_obj, first_start = content_obj, start
            last_end = end
            parts.append(expanded)

        if first_obj is None or not parts:
            return None

        combined = " ".join(parts)
        context = speechserver.SayAllContext(first_obj, combined, first_start, last_end)
        self._contexts.append(context)
        tokens = [
            "SAY ALL PRESENTER: Speaking (displayed-text):",
            first_obj,
            f"'{combined}' ({first_start}-{last_end})",
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        self._script.utilities.set_caret_offset(first_obj, first_start)
        ax_event_synthesizer.get_synthesizer().scroll_into_view(
            context.obj,
            context.start_offset,
            context.end_offset,
        )
        return context, ACSS()

    def _generate_speech_contexts(
        self,
        contents: list[tuple[Atspi.Accessible, int, int, str]],
        prior_obj: Atspi.Accessible,
    ) -> Generator[list[speechserver.SayAllContext | ACSS], None, None]:
        """Yields [SayAllContext, ACSS] pairs for each content item."""

        assert self._script is not None

        for i, content in enumerate(contents):
            content_obj, start, end, text = content
            tokens = [
                f"SAY ALL PRESENTER: CONTENT: {i}.",
                content_obj,
                f"'{text}' ({start}-{end})",
            ]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

            skip, reason = self._say_all_should_skip_content(content, contents)
            if skip:
                msg = f"SAY ALL PRESENTER: Skipping content - {reason}."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                continue

            utterances = speech_presenter.get_presenter().generate_speech_contents(
                self._script,
                [content],
                eliminatePauses=True,
                priorObj=prior_obj,
                index=i,
                total=len(contents),
            )
            prior_obj = content_obj
            elements, voices = self._parse_utterances(utterances)
            if len(elements) != len(voices):
                tokens = [
                    "SAY ALL PRESENTER: Skipping content - elements/voices mismatch:",
                    content_obj,
                    f"'{text}', elements: {len(elements)}, voices: {len(voices)}",
                ]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                continue

            for element, voice in zip(elements, voices, strict=True):
                if not element or (isinstance(element, str) and not element.strip()):
                    continue

                context = speechserver.SayAllContext(content_obj, element, start, end)
                self._contexts.append(context)
                tokens = [
                    "SAY ALL PRESENTER: Speaking (contents):",
                    content_obj,
                    f"'{element}' ({start}-{end})",
                ]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                self._script.utilities.set_caret_offset(content_obj, start)
                ax_event_synthesizer.get_synthesizer().scroll_into_view(
                    context.obj,
                    context.start_offset,
                    context.end_offset,
                )
                yield [context, voice]

    def _say_all_iter(
        self,
        obj: Atspi.Accessible,
        offset: int | None = None,
    ) -> Generator[list[speechserver.SayAllContext | ACSS], None, None]:
        """A generator used by Say All."""

        assert self._script is not None, "Script must be set before calling _say_all_iter."

        prior_obj = obj
        say_all_by_sentence = self.get_style() == "sentence"

        if offset is None:
            offset = self._script.utilities.get_caret_context()[-1] or 0

        restrict_to = None
        if AXUtilities.is_text(obj) or AXUtilities.is_terminal(obj):
            restrict_to = obj

        prev_obj, prev_offset = None, None
        while obj:
            if obj == prev_obj and offset == prev_offset:
                obj, offset = self._script.utilities.next_context(obj, offset)
                tokens = [
                    "SAY ALL PRESENTER: Stuck at",
                    prev_obj,
                    f"offset {prev_offset}.",
                    "Moving to",
                    obj,
                    f"offset {offset}.",
                ]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                continue
            prev_obj, prev_offset = obj, offset

            if say_all_by_sentence:
                contents = self._script.utilities.get_sentence_contents_at_offset(obj, offset)
            else:
                contents = self._script.utilities.get_line_contents_at_offset(
                    obj,
                    offset,
                    layout_mode=True,
                    use_cache=False,
                )

            contents = self._script.utilities.filter_contents_for_presentation(contents)
            self._contents.extend(contents)

            if self.get_only_speak_displayed_text():
                if (result := self._build_displayed_text_context(contents)) is not None:
                    yield list(result)
            else:
                yield from self._generate_speech_contexts(contents, prior_obj)

            obj, offset = self._advance_to_next(obj, offset, contents, restrict_to)

        self.stop()

    def _rewind(
        self,
        context: speechserver.SayAllContext | None,
        override_setting: bool = False,
    ) -> bool:
        if not (override_setting or self.get_rewind_and_fast_forward_enabled()):
            return False

        if context is None:
            context = self._current_context

        obj = None
        try:
            obj, start, _end, _string = self._contents[0]
        except IndexError:
            if context is not None:
                obj, start = context.obj, context.start_offset

        if obj is None:
            return False

        focus_manager.get_manager().set_locus_of_focus(None, obj, notify_script=False)
        assert self._script is not None, "Script must be set before calling _rewind."
        self._script.utilities.set_caret_context(obj, start)

        prev_obj, prev_offset = self._script.utilities.previous_context(obj, start, True)
        self.say_all(self._script, obj=prev_obj, offset=prev_offset)
        return True

    def _fast_forward(
        self,
        context: speechserver.SayAllContext | None,
        override_setting: bool = False,
    ) -> bool:
        if not (override_setting or self.get_rewind_and_fast_forward_enabled()):
            return False

        if context is None:
            context = self._current_context

        obj = None
        try:
            obj, _start, end, _string = self._contents[-1]
        except IndexError:
            if context is not None:
                obj, end = context.obj, context.end_offset

        if obj is None:
            return False

        focus_manager.get_manager().set_locus_of_focus(None, obj, notify_script=False)
        assert self._script is not None, "Script must be set before calling _fast_forward."
        self._script.utilities.set_caret_context(obj, end)

        next_obj, next_offset = self._script.utilities.next_context(obj, end, True)
        self.say_all(self._script, obj=next_obj, offset=next_offset)
        return True

    def _progress_callback(self, context: speechserver.SayAllContext, progress_type: int) -> None:
        self._current_context = context
        self._say_all_is_running = True

        if progress_type == speechserver.SayAllContext.PROGRESS:
            if AXUtilities.character_at_offset_is_eoc(context.obj, context.current_offset):
                return
            focus_manager.get_manager().emit_region_changed(
                context.obj,
                context.current_offset,
                context.current_end_offset,
                focus_manager.SAY_ALL,
            )
            return

        assert self._script is not None, "Script must be set before calling _progress_callback."

        if progress_type == speechserver.SayAllContext.INTERRUPTED:
            tokens = ["SAY ALL PROGRESS CALLBACK: Interrupted", context]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            manager = input_event_manager.get_manager()
            if manager.last_event_was_keyboard():
                if manager.last_event_was_down() and self._fast_forward(context):
                    return
                if manager.last_event_was_up() and self._rewind(context):
                    return
                navigator = structural_navigator.get_navigator()
                if (
                    self.get_structural_navigation_enabled()
                    and navigator.last_input_event_was_navigation_command()
                ):
                    return
                presentation_manager.get_manager().interrupt_presentation()
                AXText.set_caret_offset(context.obj, context.current_offset)
                self._say_all_is_running = False
        else:
            tokens = ["SAY ALL PROGRESS CALLBACK: Completed", context]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        focus_manager.get_manager().set_locus_of_focus(None, context.obj, notify_script=False)
        mode = focus_manager.SAY_ALL if self._say_all_is_running else focus_manager.FOCUS_TRACKING
        focus_manager.get_manager().emit_region_changed(
            context.obj,
            context.current_offset,
            None,
            mode,
        )
        self._script.utilities.set_caret_context(context.obj, context.current_offset)

    @gsettings_registry.get_registry().gsetting(
        key="announce-blockquote",
        schema="say-all",
        gtype="b",
        default=True,
        summary="Announce blockquotes",
        migration_key="sayAllContextBlockquote",
    )
    @dbus_service.getter
    def get_announce_blockquote(self) -> bool:
        """Returns whether blockquotes are announced when entered."""

        return self._get_setting("announce-blockquote", True)

    @dbus_service.setter
    def set_announce_blockquote(self, value: bool) -> bool:
        """Sets whether blockquotes are announced when entered."""

        msg = f"SAY ALL PRESENTER: Setting announce blockquotes to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            "announce-blockquote",
            value,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key="announce-form",
        schema="say-all",
        gtype="b",
        default=True,
        summary="Announce non-landmark forms",
        migration_key="sayAllContextNonLandmarkForm",
    )
    @dbus_service.getter
    def get_announce_form(self) -> bool:
        """Returns whether non-landmark forms are announced when entered."""

        return self._get_setting("announce-form", True)

    @dbus_service.setter
    def set_announce_form(self, value: bool) -> bool:
        """Sets whether non-landmark forms are announced when entered."""

        msg = f"SAY ALL PRESENTER: Setting announce forms to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(self._SCHEMA, "announce-form", value)
        return True

    @gsettings_registry.get_registry().gsetting(
        key="announce-grouping",
        schema="say-all",
        gtype="b",
        default=True,
        summary="Announce groupings",
        migration_key="sayAllContextPanel",
    )
    @dbus_service.getter
    def get_announce_grouping(self) -> bool:
        """Returns whether groupings are announced when entered."""

        return self._get_setting("announce-grouping", True)

    @dbus_service.setter
    def set_announce_grouping(self, value: bool) -> bool:
        """Sets whether groupings are announced when entered."""

        msg = f"SAY ALL PRESENTER: Setting announce groupings to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            "announce-grouping",
            value,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key="announce-landmark",
        schema="say-all",
        gtype="b",
        default=True,
        summary="Announce landmarks",
        migration_key="sayAllContextLandmark",
    )
    @dbus_service.getter
    def get_announce_landmark(self) -> bool:
        """Returns whether landmarks are announced when entered."""

        return self._get_setting("announce-landmark", True)

    @dbus_service.setter
    def set_announce_landmark(self, value: bool) -> bool:
        """Sets whether landmarks are announced when entered."""

        msg = f"SAY ALL PRESENTER: Setting announce landmarks to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            "announce-landmark",
            value,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key="announce-list",
        schema="say-all",
        gtype="b",
        default=True,
        summary="Announce lists",
        migration_key="sayAllContextList",
    )
    @dbus_service.getter
    def get_announce_list(self) -> bool:
        """Returns whether lists are announced when entered."""

        return self._get_setting("announce-list", True)

    @dbus_service.setter
    def set_announce_list(self, value: bool) -> bool:
        """Sets whether lists are announced when entered."""

        msg = f"SAY ALL PRESENTER: Setting announce lists to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(self._SCHEMA, "announce-list", value)
        return True

    @gsettings_registry.get_registry().gsetting(
        key="announce-table",
        schema="say-all",
        gtype="b",
        default=True,
        summary="Announce tables",
        migration_key="sayAllContextTable",
    )
    @dbus_service.getter
    def get_announce_table(self) -> bool:
        """Returns whether tables are announced when entered."""

        return self._get_setting("announce-table", True)

    @dbus_service.setter
    def set_announce_table(self, value: bool) -> bool:
        """Sets whether tables are announced when entered."""

        msg = f"SAY ALL PRESENTER: Setting announce tables to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(self._SCHEMA, "announce-table", value)
        return True

    @gsettings_registry.get_registry().gsetting(
        key="only-speak-displayed-text",
        schema="say-all",
        gtype="b",
        default=False,
        summary="Only speak displayed text",
    )
    @dbus_service.getter
    def get_only_speak_displayed_text(self) -> bool:
        """Returns whether Say All only speaks displayed text."""

        return self._get_setting("only-speak-displayed-text", False)

    @dbus_service.setter
    def set_only_speak_displayed_text(self, value: bool) -> bool:
        """Sets whether Say All only speaks displayed text."""

        msg = f"SAY ALL PRESENTER: Setting only speak displayed text to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            "only-speak-displayed-text",
            value,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key="style",
        schema="say-all",
        genum="org.gnome.Orca.SayAllStyle",
        default="sentence",
        summary="Say All style (line, sentence)",
        migration_key="sayAllStyle",
    )
    @dbus_service.getter
    def get_style(self) -> str:
        """Returns the current Say All style."""

        return gsettings_registry.get_registry().layered_lookup(
            self._SCHEMA,
            "style",
            "",
            genum="org.gnome.Orca.SayAllStyle",
            default="sentence",
        )

    @dbus_service.setter
    def set_style(self, value: str) -> bool:
        """Sets the current Say All style."""

        try:
            style = SayAllStyle[value.upper()]
        except KeyError:
            msg = f"SAY ALL PRESENTER: Invalid style: {value}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return False

        msg = f"SAY ALL PRESENTER: Setting style to {value} ({style.value})."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            "style",
            style.string_name,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key="structural-navigation",
        schema="say-all",
        gtype="b",
        default=False,
        summary="Enable structural navigation in Say All",
        migration_key="structNavInSayAll",
    )
    @dbus_service.getter
    def get_structural_navigation_enabled(self) -> bool:
        """Returns whether structural navigation keys can be used in Say All."""

        return self._get_setting("structural-navigation", False)

    @dbus_service.setter
    def set_structural_navigation_enabled(self, value: bool) -> bool:
        """Sets whether structural navigation keys can be used in Say All."""

        msg = f"SAY ALL PRESENTER: Setting enable structural navigation to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            "structural-navigation",
            value,
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key="rewind-and-fast-forward",
        schema="say-all",
        gtype="b",
        default=False,
        summary="Enable rewind and fast forward in Say All",
        migration_key="rewindAndFastForwardInSayAll",
    )
    @dbus_service.getter
    def get_rewind_and_fast_forward_enabled(self) -> bool:
        """Returns whether Up and Down can be used in Say All."""

        return self._get_setting("rewind-and-fast-forward", False)

    @dbus_service.setter
    def set_rewind_and_fast_forward_enabled(self, value: bool) -> bool:
        """Returns whether Up and Down can be used in Say All."""

        msg = f"SAY ALL PRESENTER: Setting enable rewind and fast forward to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SCHEMA,
            "rewind-and-fast-forward",
            value,
        )
        return True


_presenter: SayAllPresenter = SayAllPresenter()


def get_presenter() -> SayAllPresenter:
    """Returns the Say All Presenter"""

    return _presenter
