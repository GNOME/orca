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

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc."
__license__   = "LGPL"

from . import ax_event_synthesizer
from . import bypass_mode_manager
from . import action_presenter
from . import braille_generator
from . import clipboard
from . import debug
from . import debugging_tools_manager
from . import flat_review_finder
from . import flat_review_presenter
from . import keybindings
from . import label_inference
from . import learn_mode_presenter
from . import mouse_review
from . import notification_presenter
from . import object_navigator
from . import script_utilities
from . import sleep_mode_manager
from . import sound_generator
from . import speech_and_verbosity_manager
from . import speech_generator
from . import structural_navigator
from . import system_information_presenter
from . import table_navigator
from . import bookmarks
from . import where_am_i_presenter
from .ax_object import AXObject


class Script:
    """The base Script class."""

    def __init__(self, app):
        self.app = app
        self.name = f"{AXObject.get_name(self.app) or 'default'} (module={self.__module__})"
        self.present_if_inactive = True
        self.run_find_command_on = None
        self.input_event_handlers = {}
        self.point_of_reference = {}
        self.event_cache = {}
        self.key_bindings = keybindings.KeyBindings()

        self.listeners = self.get_listeners()
        self.utilities = self.get_utilities()

        self.braille_generator = self.get_braille_generator()
        self.sound_generator = self.get_sound_generator()
        self.speech_generator = self.get_speech_generator()

        self.bookmarks = self.get_bookmarks()
        self.label_inference = self.get_label_inference()

        # pylint:disable=assignment-from-none
        self.caret_navigation = self.get_caret_navigation()
        self.live_region_manager = self.get_live_region_manager()
        self.chat = self.get_chat()
        self.spellcheck = self.get_spellcheck()

        self.setup_input_event_handlers()
        self.braille_bindings = self.get_braille_bindings()

        self._default_sn_mode = structural_navigator.NavigationMode.OFF

        msg = f"SCRIPT: {self.name} initialized"
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def __str__(self):
        return f"{self.name}"

    def get_listeners(self):
        """Returns a dictionary of the event listeners for this script."""

        return {}

    def setup_input_event_handlers(self):
        """Defines the input event handlers for this script."""

    def get_key_bindings(self, enabled_only=True):
        """Returns the key bindings for this script."""

        return keybindings.KeyBindings()

    def get_app_key_bindings(self):
        """Returns the application-specific keybindings for this script."""

        return keybindings.KeyBindings()

    def get_braille_bindings(self):
        """Returns the braille bindings for this script."""

        return {}

    def get_braille_generator(self):
        """Returns the braille generator for this script."""

        return braille_generator.BrailleGenerator(self)

    def get_sound_generator(self):
        """Returns the sound generator for this script."""

        return sound_generator.SoundGenerator(self)

    def get_speech_generator(self):
        """Returns the speech generator for this script."""

        return speech_generator.SpeechGenerator(self)

    def get_chat(self):
        """Returns the 'chat' class for this script."""

        return None

    def get_spellcheck(self):
        """Returns the spellcheck support for this script."""

        return None

    def get_caret_navigation(self):
        """Returns the caret navigation support for this script."""

        return None

    def get_clipboard_presenter(self):
        """Returns the clipboard presenter for this script."""

        return clipboard.get_presenter()

    def get_debugging_tools_manager(self):
        """Returns the debugging tools manager for this script."""

        return debugging_tools_manager.get_manager()

    def get_utilities(self):
        """Returns the utilities for this script."""

        return script_utilities.Utilities(self)

    def get_label_inference(self):
        """Returns the label inference functionality for this script."""

        return label_inference.LabelInference(self)

    def get_structural_navigator(self):
        """Returns the 'structural navigator' class for this script."""

        return structural_navigator.get_navigator()

    def get_live_region_manager(self):
        """Returns the live region manager for this script."""

        return None

    def get_notification_presenter(self):
        """Returns the notification presenter for this script."""

        return notification_presenter.get_presenter()

    def get_flat_review_finder(self):
        """Returns the flat review finder for this script."""

        return flat_review_finder.get_finder()

    def get_flat_review_presenter(self):
        """Returns the flat review presenter for this script."""

        return flat_review_presenter.get_presenter()

    def get_system_information_presenter(self):
        """Returns the system information presenter for this script."""

        return system_information_presenter.get_presenter()

    def get_object_navigator(self):
        """Returns the object navigator for this script."""

        return object_navigator.get_navigator()

    def get_table_navigator(self):
        """Returns the table navigator for this script."""

        return table_navigator.get_navigator()

    def get_speech_and_verbosity_manager(self):
        """Returns the speech and verbosity manager for this script."""

        return speech_and_verbosity_manager.get_manager()

    def get_bypass_mode_manager(self):
        """Returns the bypass mode manager for this script."""

        return bypass_mode_manager.get_manager()

    def get_where_am_i_presenter(self):
        """Returns the where-am-I presenter for this script."""

        return where_am_i_presenter.get_presenter()

    def get_learn_mode_presenter(self):
        """Returns the learn-mode presenter for this script."""

        return learn_mode_presenter.get_presenter()

    def get_action_presenter(self):
        """Returns the action presenter for this script."""

        return action_presenter.get_presenter()

    def get_sleep_mode_manager(self):
        """Returns the sleep mode manager for this script."""

        return sleep_mode_manager.get_manager()

    def get_mouse_reviewer(self):
        """Returns the mouse reviewer for this script."""

        return mouse_review.get_reviewer()

    def get_event_synthesizer(self):
        """Returns the event synthesizer for this script."""

        return ax_event_synthesizer.get_synthesizer()

    def get_bookmarks(self):
        """Returns the bookmarks support for this script."""

        try:
            return self.bookmarks
        except AttributeError:
            self.bookmarks = bookmarks.Bookmarks(self)
            return self.bookmarks

    def _get_queued_event(self, event_type, detail1=None, detail2=None, any_data=None):
        cached_event = self.event_cache.get(event_type, [None, 0])[0]
        if not cached_event:
            tokens = ["SCRIPT: No queued event of type", event_type]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return None

        if detail1 is not None and detail1 != cached_event.detail1:
            tokens = ["SCRIPT: Queued event's detail1 (", cached_event.detail1,
                      ") doesn't match", detail1]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return None

        if detail2 is not None and detail2 != cached_event.detail2:
            tokens = ["SCRIPT: Queued event's detail2 (", cached_event.detail2,
                      ") doesn't match", detail2]
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

    def locus_of_focus_changed(self, event, old_focus, new_focus):
        """Handles changes of focus of interest to the script."""

    def is_activatable_event(self, event):
        """Returns True if event should cause this script to become active."""

        return True

    def force_script_activation(self, event):
        """Allows scripts to insist that they should become active."""

        return False

    def activate(self):
        """Called when this script is activated."""

    def deactivate(self):
        """Called when this script is deactivated."""
