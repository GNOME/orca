# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
# Copyright 2013 Igalia, S.L.
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


"""Custom script for Evolution."""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc." \
                "Copyright (c) 2013 Igalia, S.L."
__license__   = "LGPL"

from typing import TYPE_CHECKING

from orca import debug
from orca.ax_utilities import AXUtilities
from orca.scripts.toolkits import gtk
from orca.scripts.toolkits import WebKitGTK
from .braille_generator import BrailleGenerator
from .speech_generator import SpeechGenerator
from .script_utilities import Utilities

if TYPE_CHECKING:
    import gi
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

class Script(WebKitGTK.Script, gtk.Script):
    """Custom script for Evolution."""

    # For the no-such-function when the function is only in the subclass.
    utilities: Utilities

    def get_braille_generator(self) -> BrailleGenerator:
        """Returns the braille generator for this script."""

        return BrailleGenerator(self)

    def get_speech_generator(self) -> SpeechGenerator:
        """Returns the speech generator for this script."""

        return SpeechGenerator(self)

    def get_utilities(self) -> Utilities:
        """Returns the utilities for this script."""

        return Utilities(self)

    def on_busy_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:busy accessibility events."""

        if self.utilities.is_ignorable_event_from_document_preview(event):
            msg = "EVOLUTION: Ignoring event from document preview"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        msg = "EVOLUTION: Passing event to super class for processing."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return super().on_busy_changed(event)

    def on_caret_moved(self, event: Atspi.Event) -> bool:
        """Callback for object:text-caret-moved accessibility events."""

        if self.utilities.is_ignorable_event_from_document_preview(event):
            msg = "EVOLUTION: Ignoring event from document preview"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        msg = "EVOLUTION: Passing event to super class for processing."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return super().on_caret_moved(event)

    def on_focused_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:focused accessibility events."""

        if self.utilities.is_ignorable_event_from_document_preview(event):
            msg = "EVOLUTION: Ignoring event from document preview"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        # TODO - JD: Figure out what's causing this in Evolution or WebKit and file a bug.
        # When the selected message changes and the preview panel is showing, a panel with the
        # `iframe` tag claims focus. We don't want to update our location in response.
        if AXUtilities.is_internal_frame(event.source):
            tokens = ["EVOLUTION: Ignoring event from internal frame", event.source]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        msg = "EVOLUTION: Passing event to super class for processing."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return super().on_focused_changed(event)
