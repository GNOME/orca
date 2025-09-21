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
# pylint: disable=too-many-branches
# pylint: disable=too-many-positional-arguments
# pylint: disable=too-many-statements
# pylint: disable=too-many-public-methods

"""Module for commands related to the current accessible object."""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc." \
                "Copyright (c) 2011-2025 Igalia, S.L."
__license__   = "LGPL"

from enum import Enum
from typing import Generator, TYPE_CHECKING

from . import cmdnames
from . import dbus_service
from . import debug
from . import focus_manager
from . import input_event
from . import input_event_manager
from . import keybindings
from . import messages
from . import speech
from . import settings
from . import settings_manager
from . import speechserver
from .acss import ACSS
from .ax_object import AXObject
from .ax_text import AXText
from .ax_utilities import AXUtilities

if TYPE_CHECKING:
    import gi
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

    from .scripts import default

class SayAllStyle(Enum):
    """Style enumeration with int values from settings."""

    SENTENCE = settings.SAYALL_STYLE_SENTENCE
    LINE = settings.SAYALL_STYLE_LINE

    @property
    def string_name(self) -> str:
        """Returns the lowercase string name for this enum value."""

        return self.name.lower()
class SayAllPresenter:
    """Module for commands related to the current accessible object."""

    def __init__(self) -> None:
        self._handlers: dict[str, input_event.InputEventHandler] = self.get_handlers(True)
        self._desktop_bindings: keybindings.KeyBindings = keybindings.KeyBindings()
        self._laptop_bindings: keybindings.KeyBindings = keybindings.KeyBindings()

        self._script: default.Script | None = None
        self._contents: list[tuple[Atspi.Accessible, int, int, str]] = []
        self._contexts: list[speechserver.SayAllContext] = []
        self._current_context: speechserver.SayAllContext | None = None

        msg = "SayAllPresenter: Registering D-Bus commands."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        controller = dbus_service.get_remote_controller()
        controller.register_decorated_module("SayAllPresenter", self)

    def get_bindings(
        self, refresh: bool = False, is_desktop: bool = True
    ) -> keybindings.KeyBindings:
        """Returns the say-all-presenter keybindings."""

        if refresh:
            msg = "SAY ALL PRESENTER: Refreshing bindings."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._desktop_bindings.remove_key_grabs("SAY ALL PRESENTER: Refreshing bindings.")
            self._laptop_bindings.remove_key_grabs("SAY ALL PRESENTER: Refreshing bindings.")
            self._setup_bindings()
        elif is_desktop and self._desktop_bindings.is_empty():
            self._setup_bindings()
        elif not is_desktop and self._laptop_bindings.is_empty():
            self._setup_bindings()

        if is_desktop:
            return self._desktop_bindings
        return self._laptop_bindings

    def get_handlers(self, refresh: bool = False) -> dict[str, input_event.InputEventHandler]:
        """Returns the say-all-presenter handlers."""

        if refresh:
            msg = "SAY ALL PRESENTER: Refreshing handlers."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self._setup_handlers()

        return self._handlers

    def _setup_bindings(self) -> None:
        """Sets up the say-all-presenter key bindings."""

        self._setup_desktop_bindings()
        self._setup_laptop_bindings()

    def _setup_handlers(self) -> None:
        """Sets up the say-all-presenter input event handlers."""

        self._handlers = {}

        self._handlers["sayAllHandler"] = \
            input_event.InputEventHandler(
                self.say_all,
                cmdnames.SAY_ALL)

        msg = "SAY ALL PRESENTER: Handlers set up."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def _setup_desktop_bindings(self) -> None:
        """Sets up the say-all-presenter desktop key bindings."""

        self._desktop_bindings = keybindings.KeyBindings()

        self._desktop_bindings.add(
            keybindings.KeyBinding(
                "KP_Add",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers["sayAllHandler"],
                1))

        msg = "SAY ALL PRESENTER: Desktop bindings set up."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def _setup_laptop_bindings(self) -> None:
        """Sets up the say-all-presenter laptop key bindings."""

        self._laptop_bindings = keybindings.KeyBindings()

        self._laptop_bindings.add(
            keybindings.KeyBinding(
                "semicolon",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers["sayAllHandler"],
                1))

        msg = "SAY ALL PRESENTER: Laptop bindings set up."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    @dbus_service.command
    def say_all(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
        obj: Atspi.Accessible | None = None,
        offset: int | None = None
    ) -> bool:
        """Speaks the entire document or text, starting from the current position."""

        self._contexts = []
        self._contents = []
        self._current_context = None

        tokens = ["SAY ALL PRESENTER: say_all. Script:", script, "Event:", event,
                  "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._script = script
        self._script.interrupt_presentation()
        obj = obj or focus_manager.get_manager().get_locus_of_focus()
        if not obj or AXObject.is_dead(obj):
            self._script.present_message(messages.LOCATION_NOT_FOUND_FULL)
            return True

        speech.say_all(self._say_all_iter(obj, offset), self._progress_callback)
        return True

    @dbus_service.command
    def rewind(
        self,
        script: default.Script,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Jumps back in the current Say All."""

        tokens = ["SAY ALL PRESENTER: rewind. Script:", script, "Event:", event,
                  "notify_user:", notify_user]
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

        tokens = ["SAY ALL PRESENTER: fast_forward. Script:", script, "Event:", event,
                  "notify_user:", notify_user]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return self._fast_forward(None, True)

    def _parse_utterances(
        self,
        utterances: list[str | ACSS | list]
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
        contents: list[tuple[Atspi.Accessible, int, int, str]] # pylint: disable=unused-argument
    ) -> bool:
        """Returns True if content should be skipped during say-all iteration."""

        obj, start_offset, end_offset, _text = content
        if start_offset == end_offset:
            return True
        if AXUtilities.get_is_label_for(obj):
            return True
        return False

    def _say_all_iter(
        self,
        obj: Atspi.Accessible,
        offset: int | None = None
    ) -> Generator[list[speechserver.SayAllContext | ACSS], None, None]:
        """A generator used by Say All."""

        assert self._script is not None, "Script must be set before calling _say_all_iter."

        prior_obj = obj
        style = settings_manager.get_manager().get_setting("sayAllStyle")
        say_all_by_sentence = style == settings.SAYALL_STYLE_SENTENCE

        if offset is None:
            offset = self._script.utilities.get_caret_context()[-1] or 0

        restrict_to = None
        if AXUtilities.is_text(obj) or AXUtilities.is_terminal(obj):
            restrict_to = obj

        while obj:
            if say_all_by_sentence:
                contents = self._script.utilities.get_sentence_contents_at_offset(obj, offset)
            else:
                contents = self._script.utilities.get_line_contents_at_offset(
                    obj, offset, layout_mode=True, use_cache=False)

            contents = self._script.utilities.filter_contents_for_presentation(contents)
            self._contents.extend(contents)
            for i, content in enumerate(contents):
                content_obj, start, end, text = content
                tokens = [f"SAY ALL PRESENTER: CONTENT: {i}.", content_obj,
                          f"'{text}' ({start}-{end})"]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)

                if self._say_all_should_skip_content(content, contents):
                    msg = "SAY ALL PRESENTER: Skipping content - script directive."
                    debug.print_message(debug.LEVEL_INFO, msg, True)
                    continue

                utterances = self._script.speech_generator.generate_contents(
                    [content], eliminatePauses=True, priorObj=prior_obj,
                    index=i, total=len(contents))
                prior_obj = content_obj
                elements, voices = self._parse_utterances(utterances)
                if len(elements) != len(voices):
                    tokens = ["SAY ALL PRESENTER: Skipping content - elements/voices mismatch:",
                              content_obj,
                              f"'{text}', elements: {len(elements)}, voices: {len(voices)}"]
                    debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                    continue

                for element, voice in zip(elements, voices):
                    if not element or (isinstance(element, str) and not element.strip()):
                        continue

                    context = speechserver.SayAllContext(content_obj, element, start, end)
                    self._contexts.append(context)
                    tokens = [context]
                    debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                    self._script.utilities.set_caret_offset(content_obj, start)
                    self._script.get_event_synthesizer().scroll_into_view(
                        context.obj, context.start_offset, context.end_offset)
                    yield [context, voice]

            if contents:
                last_obj, last_offset = contents[-1][0], contents[-1][2]
                obj, offset = self._script.utilities.next_context(
                    last_obj, last_offset, restrict_to=restrict_to)
            else:
                obj = self._script.utilities.find_next_object(obj, restrict_to)
                offset = 0

            if obj is not None:
                tokens = ["SAY ALL PRESENTER: Updating focus to", obj]
                focus_manager.get_manager().set_locus_of_focus(None, obj, notify_script=False)

        self._contexts = []
        self._contents = []
        self._current_context = None

    def _rewind(
        self,
        context: speechserver.SayAllContext | None,
        override_setting: bool = False
    ) -> bool:
        if not (override_setting
                or settings_manager.get_manager().get_setting("rewindAndFastForwardInSayAll")):
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
        override_setting: bool = False
    ) -> bool:
        if not (override_setting
                or settings_manager.get_manager().get_setting("rewindAndFastForwardInSayAll")):
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

        if AXText.character_at_offset_is_eoc(context.obj, context.current_offset):
            return

        if progress_type == speechserver.SayAllContext.PROGRESS:
            focus_manager.get_manager().emit_region_changed(
                context.obj, context.current_offset, context.current_end_offset,
                focus_manager.SAY_ALL)
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
                if settings_manager.get_manager().get_setting("structNavInSayAll") \
                   and self._script.get_structural_navigator().\
                       last_input_event_was_navigation_command():
                    return
                self._script.interrupt_presentation()
                AXText.set_caret_offset(context.obj, context.current_offset)
        else:
            tokens = ["SAY ALL PROGRESS CALLBACK: Completed", context]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        focus_manager.get_manager().set_locus_of_focus(None, context.obj, notify_script=False)
        focus_manager.get_manager().emit_region_changed(context.obj, context.current_offset)
        self._script.utilities.set_caret_context(context.obj, context.current_offset)

    @dbus_service.getter
    def get_announce_blockquote(self) -> bool:
        """Returns whether blockquotes are announced when entered."""

        return settings_manager.get_manager().get_setting("sayAllContextBlockquote")

    @dbus_service.setter
    def set_announce_blockquote(self, value: bool) -> bool:
        """Sets whether blockquotes are announced when entered."""

        msg = f"SAY ALL PRESENTER: Setting announce blockquotes to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("sayAllContextBlockquote", value)
        return True

    @dbus_service.getter
    def get_announce_form(self) -> bool:
        """Returns whether non-landmark forms are announced when entered."""

        return settings_manager.get_manager().get_setting("sayAllContextNonLandmarkForm")

    @dbus_service.setter
    def set_announce_form(self, value: bool) -> bool:
        """Sets whether non-landmark forms are announced when entered."""

        msg = f"SAY ALL PRESENTER: Setting announce forms to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("sayAllContextNonLandmarkForm", value)
        return True

    @dbus_service.getter
    def get_announce_grouping(self) -> bool:
        """Returns whether groupings are announced when entered."""

        return settings_manager.get_manager().get_setting("sayAllContextPanel")

    @dbus_service.setter
    def set_announce_grouping(self, value: bool) -> bool:
        """Sets whether groupings are announced when entered."""

        msg = f"SAY ALL PRESENTER: Setting announce groupings to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("sayAllContextPanel", value)
        return True

    @dbus_service.getter
    def get_announce_landmark(self) -> bool:
        """Returns whether landmarks are announced when entered."""

        return settings_manager.get_manager().get_setting("sayAllContextLandmark")

    @dbus_service.setter
    def set_announce_landmark(self, value: bool) -> bool:
        """Sets whether landmarks are announced when entered."""

        msg = f"SAY ALL PRESENTER: Setting announce landmarks to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("sayAllContextLandmark", value)
        return True

    @dbus_service.getter
    def get_announce_list(self) -> bool:
        """Returns whether lists are announced when entered."""

        return settings_manager.get_manager().get_setting("sayAllContextList")

    @dbus_service.setter
    def set_announce_list(self, value: bool) -> bool:
        """Sets whether lists are announced when entered."""

        msg = f"SAY ALL PRESENTER: Setting announce lists to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("sayAllContextList", value)
        return True

    @dbus_service.getter
    def get_announce_table(self) -> bool:
        """Returns whether tables are announced when entered."""

        return settings_manager.get_manager().get_setting("sayAllContextTable")

    @dbus_service.setter
    def set_announce_table(self, value: bool) -> bool:
        """Sets whether tables are announced when entered."""

        msg = f"SAY ALL PRESENTER: Setting announce tables to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("sayAllContextTable", value)
        return True

    @dbus_service.getter
    def get_style(self) -> str:
        """Returns the current Say All style."""

        int_value = settings_manager.get_manager().get_setting("sayAllStyle")
        return SayAllStyle(int_value).string_name

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
        settings_manager.get_manager().set_setting("sayAllStyle", style.value)
        return True

    @dbus_service.getter
    def get_structural_navigation_enabled(self) -> bool:
        """Returns whether structural navigation keys can be used in Say All."""

        return settings_manager.get_manager().get_setting("structNavInSayAll")

    @dbus_service.setter
    def set_structural_navigation_enabled(self, value: bool) -> bool:
        """Sets whether structural navigation keys can be used in Say All."""

        msg = f"SAY ALL PRESENTER: Setting enable structural navigation to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("structNavInSayAll", value)
        return True

    @dbus_service.getter
    def get_rewind_and_fast_forward_enabled(self) -> bool:
        """Returns whether Up and Down can be used in Say All."""

        return settings_manager.get_manager().get_setting("rewindAndFastForwardInSayAll")

    @dbus_service.setter
    def set_rewind_and_fast_forward_enabled(self, value: bool) -> bool:
        """Returns whether Up and Down can be used in Say All."""

        msg = f"SAY ALL PRESENTER: Setting enable rewind and fast forward to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("rewindAndFastForwardInSayAll", value)
        return True


_presenter : SayAllPresenter = SayAllPresenter()

def get_presenter() -> SayAllPresenter:
    """Returns the Say All Presenter"""

    return _presenter
