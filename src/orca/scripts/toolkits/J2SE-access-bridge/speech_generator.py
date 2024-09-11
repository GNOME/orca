# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
# Copyright 2010 Joanmarie Diggs
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

# pylint: disable=wrong-import-position

"""Produces speech presentation for accessible objects."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc., " \
                "Copyright (c) 2010 Joanmarie Diggs"
__license__   = "LGPL"

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from orca import debug
from orca import messages
from orca import settings
from orca import settings_manager
from orca import speech_generator
from orca.ax_object import AXObject
from orca.ax_utilities import AXUtilities

class SpeechGenerator(speech_generator.SpeechGenerator):
    """Produces speech presentation for accessible objects."""

    @staticmethod
    def log_generator_output(func):
        """Decorator for logging."""

        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            tokens = [f"JAVA SPEECH GENERATOR: {func.__name__}:", result]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return result
        return wrapper

    @log_generator_output
    def _generate_number_of_children(self, obj, **args):
        if settings_manager.get_manager().get_setting('onlySpeakDisplayedText') \
           or settings_manager.get_manager().get_setting('speechVerbosityLevel') \
               == settings.VERBOSITY_LEVEL_BRIEF:
            return []

        result = []
        child_count = AXObject.get_child_count(obj)
        if child_count and AXUtilities.is_label(obj) and AXUtilities.is_expanded(obj):
            result.append(messages.itemCount(child_count))
            result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))
        else:
            result.extend(super()._generate_number_of_children(obj, **args))

        return result

    def generate_speech(self, obj, **args):
        if AXUtilities.is_check_box(obj) and AXUtilities.is_menu(AXObject.get_parent(obj)):
            args["role"] = Atspi.Role.CHECK_MENU_ITEM
        elif args.get('formatType', 'unfocused') == 'basicWhereAmI' and AXUtilities.is_text(obj):
            spinbox = AXObject.find_ancestor(obj, AXUtilities.is_spin_button)
            if spinbox is not None:
                obj = spinbox
        return super().generate_speech( obj, **args)
