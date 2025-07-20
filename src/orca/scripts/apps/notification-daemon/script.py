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

# pylint: disable=duplicate-code

"""Custom script for The notification daemon."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

from orca import messages
from orca.scripts import default
from orca import settings
from orca.ax_text import AXText
from orca.ax_utilities import AXUtilities

class Script(default.Script):
    """Custom script for The notification daemon."""

    def on_window_created(self, event):
        """Callback for window:create accessibility events."""

        texts = [AXText.get_all_text(acc) for acc in AXUtilities.find_all_labels(event.source)]
        text = f"{messages.NOTIFICATION} {' '.join(texts)}"

        voice = self.speech_generator.voice(obj=event.source, string=text)
        self.speak_message(text, voice=voice)
        self.display_message(text, flash_time=settings.brailleFlashTime)
        self.get_notification_presenter().save_notification(text)
