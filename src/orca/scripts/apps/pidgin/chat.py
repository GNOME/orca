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

"""Custom chat module for Pidgin."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2010 Joanmarie Diggs."
__license__   = "LGPL"

import orca.chat as chat

########################################################################
#                                                                      #
# The Pidgin chat class.                                               #
#                                                                      #
########################################################################

class Chat(chat.Chat):

    def __init__(self, script, buddyListAncestries):

        chat.Chat.__init__(self, script, buddyListAncestries)

    def isTypingStatusChangedEvent(self, event):
        """Returns True if event is associated with a change in typing status.

        Arguments:
        - event: the accessible event being examined
        """

        if not event.type.startswith("object:text-changed:insert"):
            return False

        # Bit of a hack. Pidgin inserts text into the chat history when the
        # user is typing. We seem able to (more or less) reliably distinguish
        # this text via its attributes because these attributes are absent
        # from user inserted text -- no matter how that text is formatted.
        #
        attr, start, end = \
            self._script.utilities.textAttributes(event.source, event.detail1)

        if float(attr.get('scale', '1')) < 1 \
           or int(attr.get('weight', '400')) < 400:
            return True

        return False
