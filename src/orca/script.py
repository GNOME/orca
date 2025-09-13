# Orca
#
# Copyright 2004-2009 Sun Microsystems Inc.
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

# pylint:disable=too-many-instance-attributes
# pylint:disable=too-many-public-methods
# pylint:disable=unused-argument

"""Each script maintains a set of key bindings, braille bindings, and
AT-SPI event listeners.  The key bindings are an instance of
KeyBindings.  The braille bindings are also a dictionary where the
keys are BrlTTY command integers and the values are instances of
InputEventHandler.  The listeners field is a dictionary where the keys
are AT-SPI event names and the values are function pointers.

Instances of scripts are intended to be created solely by the
script manager.

This Script class is not intended to be instantiated directly.
Instead, it is expected that subclasses of the Script class will be
created in their own module.  The module defining the Script subclass
is also required to have a 'get_script(app)' method that returns an
instance of the Script subclass.  See default.py for an example."""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc."
__license__   = "LGPL"

from typing import TYPE_CHECKING

from . import ax_event_synthesizer
from . import bypass_mode_manager
from . import action_presenter
from . import braille_generator
from . import caret_navigator
from . import clipboard
from . import debug
from . import debugging_tools_manager
from . import flat_review_finder
from . import flat_review_presenter
from . import keybindings
from . import learn_mode_presenter
from . import mouse_review
from . import notification_presenter
from . import object_navigator
from . import say_all_presenter
from . import script_utilities
from . import sleep_mode_manager
from . import sound_generator
from . import speech_and_verbosity_manager
from . import speech_generator
from . import structural_navigator
from . import system_information_presenter
from . import table_navigator
from . import typing_echo_presenter
from . import bookmarks
from . import where_am_i_presenter
from .ax_object import AXObject

if TYPE_CHECKING:
    import gi
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

    from . import chat
    from . import label_inference
    from . import liveregions
    from . import spellcheck

class Script:
    """The base Script class."""

    def __init__(self, app: Atspi.Accessible) -> None:
        self.app = app
        self.name = f"{AXObject.get_name(self.app) or 'default'} (module={self.__module__})"
        self.present_if_inactive: bool = True
        self.run_find_command_on: Atspi.Accessible | None = None
        self.input_event_handlers: dict = {}
        self.point_of_reference: dict = {}
        self.event_cache: dict = {}
        self.key_bindings = keybindings.KeyBindings()

        self.listeners = self.get_listeners()
        self.utilities = self.get_utilities()

        self.braille_generator = self.get_braille_generator()
        self.sound_generator = self.get_sound_generator()
        self.speech_generator = self.get_speech_generator()
        self.bookmarks = self.get_bookmarks()

        # pylint:disable=assignment-from-none
        self.live_region_manager = self.get_live_region_manager()
        self.label_inference = self.get_label_inference()
        self.chat = self.get_chat()
        self.spellcheck = self.get_spellcheck()
        # pylint:enable=assignment-from-none

        self.setup_input_event_handlers()
        self.braille_bindings = self.get_braille_bindings()

        self._default_sn_mode: structural_navigator.NavigationMode = \
            structural_navigator.NavigationMode.OFF
        self._default_caret_navigation_enabled: bool = False

        msg = f"SCRIPT: {self.name} initialized"
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def __str__(self) -> str:
        return f"{self.name}"

    def get_listeners(self) -> dict:
        """Returns a dictionary of the event listeners for this script."""

        return {}

    def setup_input_event_handlers(self) -> None:
        """Defines the input event handlers for this script."""

    def get_key_bindings(self, enabled_only: bool = True) -> keybindings.KeyBindings:
        """Returns the key bindings for this script."""

        return keybindings.KeyBindings()

    def get_app_key_bindings(self) -> keybindings.KeyBindings:
        """Returns the application-specific keybindings for this script."""

        return keybindings.KeyBindings()

    def get_braille_bindings(self) -> dict:
        """Returns the braille bindings for this script."""

        return {}

    def get_braille_generator(self) -> braille_generator.BrailleGenerator:
        """Returns the braille generator for this script."""

        return braille_generator.BrailleGenerator(self)

    def get_sound_generator(self) -> sound_generator.SoundGenerator:
        """Returns the sound generator for this script."""

        return sound_generator.SoundGenerator(self)

    def get_speech_generator(self) -> speech_generator.SpeechGenerator:
        """Returns the speech generator for this script."""

        return speech_generator.SpeechGenerator(self)

    def get_chat(self) -> chat.Chat | None:
        """Returns the 'chat' class for this script."""

        return None

    def get_spellcheck(self) -> spellcheck.SpellCheck | None:
        """Returns the spellcheck support for this script."""

        return None

    def get_caret_navigator(self) -> caret_navigator.CaretNavigator:
        """Returns the caret navigator for this script."""

        return caret_navigator.get_navigator()

    def get_clipboard_presenter(self) -> clipboard.ClipboardPresenter:
        """Returns the clipboard presenter for this script."""

        return clipboard.get_presenter()

    def get_debugging_tools_manager(self) -> debugging_tools_manager.DebuggingToolsManager:
        """Returns the debugging tools manager for this script."""

        return debugging_tools_manager.get_manager()

    def get_utilities(self) -> script_utilities.Utilities:
        """Returns the utilities for this script."""

        return script_utilities.Utilities(self)

    def get_label_inference(self) -> label_inference.LabelInference | None:
        """Returns the label inference functionality for this script."""

        return None

    def get_say_all_presenter(self) -> say_all_presenter.SayAllPresenter:
        """Returns the 'say all' presenter for this script."""

        return say_all_presenter.get_presenter()

    def get_structural_navigator(self) -> structural_navigator.StructuralNavigator:
        """Returns the 'structural navigator' class for this script."""

        return structural_navigator.get_navigator()

    def get_typing_echo_presenter(self) -> typing_echo_presenter.TypingEchoPresenter:
        """Returns the 'typing echo' presenter for this script."""

        return typing_echo_presenter.get_presenter()

    def get_live_region_manager(self) -> liveregions.LiveRegionManager | None:
        """Returns the live region manager for this script."""

        return None

    def get_notification_presenter(self) -> notification_presenter.NotificationPresenter:
        """Returns the notification presenter for this script."""

        return notification_presenter.get_presenter()

    def get_flat_review_finder(self) -> flat_review_finder.FlatReviewFinder:
        """Returns the flat review finder for this script."""

        return flat_review_finder.get_finder()

    def get_flat_review_presenter(self) -> flat_review_presenter.FlatReviewPresenter:
        """Returns the flat review presenter for this script."""

        return flat_review_presenter.get_presenter()

    def get_system_information_presenter(
        self
    ) -> system_information_presenter.SystemInformationPresenter:
        """Returns the system information presenter for this script."""

        return system_information_presenter.get_presenter()

    def get_object_navigator(self) -> object_navigator.ObjectNavigator:
        """Returns the object navigator for this script."""

        return object_navigator.get_navigator()

    def get_table_navigator(self) -> table_navigator.TableNavigator:
        """Returns the table navigator for this script."""

        return table_navigator.get_navigator()

    def get_speech_and_verbosity_manager(
        self
    ) -> speech_and_verbosity_manager.SpeechAndVerbosityManager:
        """Returns the speech and verbosity manager for this script."""

        return speech_and_verbosity_manager.get_manager()

    def get_bypass_mode_manager(self) -> bypass_mode_manager.BypassModeManager:
        """Returns the bypass mode manager for this script."""

        return bypass_mode_manager.get_manager()

    def get_where_am_i_presenter(self) -> where_am_i_presenter.WhereAmIPresenter:
        """Returns the where-am-I presenter for this script."""

        return where_am_i_presenter.get_presenter()

    def get_learn_mode_presenter(self) -> learn_mode_presenter.LearnModePresenter:
        """Returns the learn-mode presenter for this script."""

        return learn_mode_presenter.get_presenter()

    def get_action_presenter(self) -> action_presenter.ActionPresenter:
        """Returns the action presenter for this script."""

        return action_presenter.get_presenter()

    def get_sleep_mode_manager(self) -> sleep_mode_manager.SleepModeManager:
        """Returns the sleep mode manager for this script."""

        return sleep_mode_manager.get_manager()

    def get_mouse_reviewer(self) -> mouse_review.MouseReviewer:
        """Returns the mouse reviewer for this script."""

        return mouse_review.get_reviewer()

    def get_event_synthesizer(self) -> ax_event_synthesizer.AXEventSynthesizer:
        """Returns the event synthesizer for this script."""

        return ax_event_synthesizer.get_synthesizer()

    def get_bookmarks(self) -> bookmarks.Bookmarks:
        """Returns the bookmarks support for this script."""

        try:
            return self.bookmarks
        except AttributeError:
            # Base Script doesn't have all methods that Bookmarks expects from default.Script
            self.bookmarks = bookmarks.Bookmarks(self)  # type: ignore[arg-type]
            return self.bookmarks

    def _get_queued_event(
        self,
        event_type: str,
        detail1: int | None = None,
        detail2: int | None = None,
        any_data=None
    ) -> Atspi.Event | None:
        cached_event = self.event_cache.get(event_type, [None, 0])[0]
        if not cached_event:
            tokens = ["SCRIPT: No queued event of type", event_type]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return None

        if detail1 is not None and detail1 != cached_event.detail1:
            tokens = ["SCRIPT: Queued event's detail1 (", str(cached_event.detail1),
                      ") doesn't match", str(detail1)]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return None

        if detail2 is not None and detail2 != cached_event.detail2:
            tokens = ["SCRIPT: Queued event's detail2 (", str(cached_event.detail2),
                      ") doesn't match", str(detail2)]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return None

        if any_data is not None and any_data != cached_event.any_data:
            tokens = ["SCRIPT: Queued event's any_data (",
                      cached_event.any_data, ") doesn't match", any_data]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return None

        tokens = ["SCRIPT: Found matching queued event:", cached_event]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return cached_event

    def locus_of_focus_changed(
        self,
        event: Atspi.Event | None,
        old_focus: Atspi.Accessible | None,
        new_focus: Atspi.Accessible | None
    ) -> bool:
        """Handles changes of focus of interest. Returns True if this script did all needed work."""

        return True

    def is_activatable_event(self, event: Atspi.Event) -> bool:
        """Returns True if event should cause this script to become active."""

        return True

    def force_script_activation(self, event: Atspi.Event) -> bool:
        """Allows scripts to insist that they should become active."""

        return False

    def activate(self) -> None:
        """Called when this script is activated."""

    def deactivate(self) -> None:
        """Called when this script is deactivated."""
