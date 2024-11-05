# Orca
#
# Copyright 2010 Joanmarie Diggs.
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

"""Custom chat module for Pidgin."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2010 Joanmarie Diggs."
__license__   = "LGPL"

from orca import chat
from orca.ax_text import AXText

class Chat(chat.Chat):
    """Custom chat module for Pidgin."""

    def isTypingStatusChangedEvent(self, event):
        """Returns True if event is associated with a change in typing status."""

        if not event.type.startswith("object:text-changed:insert"):
            return False

        # Bit of a hack. Pidgin inserts text into the chat history when the
        # user is typing. We seem able to (more or less) reliably distinguish
        # this text via its attributes because these attributes are absent
        # from user inserted text -- no matter how that text is formatted.
        attr = AXText.get_text_attributes_at_offset(event.source, event.detail1)[0]
        return float(attr.get("scale", "1")) < 1 or int(attr.get("weight", "400")) < 400
