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

import pyatspi

import orca.chat as chat

########################################################################
#                                                                      #
# The Instantbird chat class.                                          #
#                                                                      #
########################################################################

class Chat(chat.Chat):

    def __init__(self, script, buddyListAncestries):
        # IMs get inserted as embedded object characters in these roles.
        #
        self._messageParentRoles = [pyatspi.ROLE_DOCUMENT_FRAME,
                                    pyatspi.ROLE_SECTION,
                                    pyatspi.ROLE_PARAGRAPH]

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
        if event.source.getRole() == pyatspi.ROLE_DOCUMENT_FRAME:
            bubble = event.source[event.detail1]
            hasRole = lambda x: x and x.getRole() == pyatspi.ROLE_PARAGRAPH
            paragraphs = pyatspi.findAllDescendants(bubble, hasRole)

            # If the user opted the non-default, "simple" appearance, then this
            # might not be a bubble at all, but a paragraph.
            #
            if not paragraphs and bubble.getRole() == pyatspi.ROLE_PARAGRAPH:
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
        if event.source.getRole() == pyatspi.ROLE_SECTION:
            obj = event.source[event.detail1]
            if obj and obj.getRole() == pyatspi.ROLE_PARAGRAPH:
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

        # We might need to refine this later. For now, just get things
        # working.
        #
        if obj and obj.getRole() in self._messageParentRoles:
            return True

        return False

    def getChatRoomName(self, obj):
        """Attempts to find the name of the current chat room.

        Arguments:
        - obj: The accessible of interest

        Returns a string containing what we think is the chat room name.
        """

        name = ""
        ancestor = self._script.utilities.ancestorWithRole(
            obj,
            [pyatspi.ROLE_SCROLL_PANE, pyatspi.ROLE_FRAME],
            [pyatspi.ROLE_APPLICATION])

        if ancestor and ancestor.getRole() == pyatspi.ROLE_SCROLL_PANE:
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
        if obj and obj.getState().contains(pyatspi.STATE_SHOWING) \
           and self._script.utilities.isInActiveApp(obj) \
           and not self.isInBuddyList(obj):
            return True

        return False
