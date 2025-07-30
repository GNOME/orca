# Orca
#
# Copyright (C) 2013-2019 Igalia, S.L.
#
# Author: Joanmarie Diggs <jdiggs@igalia.com>
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

"""Custom script for Qt."""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2013-2019 Igalia, S.L."
__license__   = "LGPL"

from typing import TYPE_CHECKING

from orca import debug
from orca import focus_manager
from orca.scripts import default
from orca.ax_object import AXObject
from orca.ax_utilities import AXUtilities

from .script_utilities import Utilities

if TYPE_CHECKING:
    import gi
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

class Script(default.Script):
    """Custom script for Qt."""

    def get_utilities(self) -> Utilities:
        return Utilities(self)

    def on_caret_moved(self, event: Atspi.Event) -> bool:
        """Callback for object:text-caret-moved accessibility events."""

        if AXUtilities.is_accelerator_label(event.source):
            msg = "QT: Ignoring event due to role."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        return super().on_caret_moved(event)

    def on_focused_changed(self, event: Atspi.Event) -> bool:
        """Callback for object:state-changed:focused accessibility events."""

        if not event.detail1:
            return True

        if AXUtilities.is_accelerator_label(event.source):
            msg = "QT: Ignoring event due to role."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        frame = self.utilities.top_level_object(event.source)
        if not frame:
            msg = "QT: Ignoring event because we couldn't find an ancestor window."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        is_active = AXUtilities.is_active(frame)
        if not is_active:
            tokens = ["QT: Event came from inactive top-level object", frame]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

            AXObject.clear_cache(frame, False, "Ensuring we have correct active state.")
            is_active = AXUtilities.is_active(frame)
            tokens = ["QT: Cleared cache of", frame, ". Frame is now active:", is_active]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if AXUtilities.is_focused(event.source):
            return super().on_focused_changed(event)

        msg = "QT: WARNING - source lacks focused state. Setting focus anyway."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        focus_manager.get_manager().set_locus_of_focus(event, event.source)
        return True
