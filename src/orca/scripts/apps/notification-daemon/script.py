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

from __future__ import annotations

from typing import TYPE_CHECKING

from orca import messages, notification_presenter, presentation_manager
from orca.ax_text import AXText
from orca.ax_utilities import AXUtilities
from orca.scripts import default

if TYPE_CHECKING:
    import gi

    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi


class Script(default.Script):
    """Custom script for The notification daemon."""

    def _on_window_created(self, event: Atspi.Event) -> bool:
        """Callback for window:create accessibility events."""

        texts = [AXText.get_all_text(acc) for acc in AXUtilities.find_all_labels(event.source)]
        text = f"{messages.NOTIFICATION} {' '.join(texts)}"

        presenter = presentation_manager.get_manager()
        presenter.speak_accessible_text(event.source, text)
        presenter.present_braille_message(text)
        notification_presenter.get_presenter().save_notification(text)
