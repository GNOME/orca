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

"""Custom chat module for Instantbird."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2010 Joanmarie Diggs."
__license__   = "LGPL"

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

import orca.chat as chat
from orca.ax_object import AXObject

########################################################################
#                                                                      #
# The Instantbird chat class.                                          #
#                                                                      #
########################################################################

class Chat(chat.Chat):

    def __init__(self, script, buddyListAncestries):
        chat.Chat.__init__(self, script, buddyListAncestries)

    ########################################################################
    #                                                                      #
    # InputEvent handlers and supporting utilities                         #
    #                                                                      #
    ########################################################################

    def getMessageFromEvent(self, event):
        """Get the actual displayed message. This will almost always be the
        unaltered any_data from an event of type object:text-changed:insert.

        Arguments:
        - event: the Event from which to take the text.

        Returns the string which should be presented as the newly-inserted
        text. (Things like chatroom name prefacing get handled elsewhere.)
        """

        string = ""

        # IMs are written in areas that look like bubbles. When a new bubble
        # is inserted, we see an embedded object character inserted into the
        # document frame. The first paragraph is the bubble title; the
        # rest (usually just one) are the message itself.
        #
        if self._script.utilities.isDocument(event.source):
            bubble = event.source[event.detail1]
            hasRole = lambda x: x and AXObject.get_role(x) == Atspi.Role.PARAGRAPH
            paragraphs = self._script.utilities.findAllDescendants(bubble, hasRole)

            # If the user opted the non-default, "simple" appearance, then this
            # might not be a bubble at all, but a paragraph.
            #
            if not paragraphs and AXObject.get_role(bubble) == Atspi.Role.PARAGRAPH:
                paragraphs.append(bubble)

            for paragraph in paragraphs:
                msg = self._script.utilities.substring(paragraph, 0, -1)
                if msg == self._script.EMBEDDED_OBJECT_CHARACTER:
                    # This seems to occur for non-focused conversations.
                    #
                    msg = self._script.utilities.substring(paragraph[0], 0, -1)
                string = self._script.utilities.appendString(string, msg)

            return string

        # If we instead have a section, we are writing another message into
        # the existing bubble. In this case, we get three separate items
        # inserted: a separator, a paragraph with the desired text, and an
        # empty section.
        #
        if AXObject.get_role(event.source) == Atspi.Role.SECTION:
            obj = event.source[event.detail1]
            if obj and AXObject.get_role(obj) == Atspi.Role.PARAGRAPH:
                try:
                    text = obj.queryText()
                except:
                    pass
                else:
                    string = text.getText(0, -1)

        return string

    ########################################################################
    #                                                                      #
    # Convenience methods for identifying, locating different accessibles  #
    #                                                                      #
    ########################################################################

    def isChatRoomMsg(self, obj):
        """Returns True if the given accessible is the text object for
        associated with a chat room conversation.

        Arguments:
        - obj: the accessible object to examine.
        """

        if not obj:
            return False

        if self._script.utilities.isDocument(obj):
            return True

        return AXObject.get_role(obj) in [Atspi.Role.SECTION, Atspi.Role.PARAGRAPH]

    def getChatRoomName(self, obj):
        """Attempts to find the name of the current chat room.

        Arguments:
        - obj: The accessible of interest

        Returns a string containing what we think is the chat room name.
        """

        name = ""
        ancestor = self._script.utilities.ancestorWithRole(
            obj,
            [Atspi.Role.SCROLL_PANE, Atspi.Role.FRAME],
            [Atspi.Role.APPLICATION])

        if ancestor and AXObject.get_role(ancestor) == Atspi.Role.SCROLL_PANE:
            # The scroll pane has a proper labelled by relationship set.
            #
            name = self._script.utilities.displayedLabel(ancestor)

        if not name:
            try:
                text = self._script.utilities.displayedText(ancestor)
                if text.lower().strip() != self._script.name.lower().strip():
                    name = text
            except:
                pass

        return name

    def isFocusedChat(self, obj):
        """Returns True if we plan to treat this chat as focused for
        the purpose of deciding whether or not a message should be
        presented to the user.

        Arguments:
        - obj: the accessible object to examine.
        """

        # Normally, we'd see if the top level window associated
        # with this object had STATE_ACTIVE. That doesn't work
        # here. So see if the script for the locusOfFocus is
        # this script. If so, the only other possibility is that
        # we're in the buddy list instead.
        #
        if obj and obj.getState().contains(Atspi.StateType.SHOWING) \
           and self._script.utilities.isInActiveApp(obj) \
           and not self.isInBuddyList(obj):
            return True

        return False
