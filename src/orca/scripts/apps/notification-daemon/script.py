# Orca
#
# Copyright 2004-2008 Sun Microsystems Inc.
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


"""Custom script for The notification daemon."""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

from typing import TYPE_CHECKING

from orca import messages
from orca.scripts import default
from orca.ax_text import AXText
from orca.ax_utilities import AXUtilities

if TYPE_CHECKING:
    import gi
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

class Script(default.Script):
    """Custom script for The notification daemon."""

    def on_window_created(self, event: Atspi.Event) -> bool:
        """Callback for window:create accessibility events."""

        texts = [AXText.get_all_text(acc) for acc in AXUtilities.find_all_labels(event.source)]
        text = f"{messages.NOTIFICATION} {' '.join(texts)}"

        voice = self.speech_generator.voice(obj=event.source, string=text)
        self.present_message(text, voice=voice)
        self.get_notification_presenter().save_notification(text)
