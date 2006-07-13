# Orca
#
# Copyright 2004-2006 Sun Microsystems Inc.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

"""Custom script for gaim.  This provides the ability for Orca to
monitor both the IM input and IM output text areas at the same
time."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2006 Sun Microsystems Inc."
__license__   = "LGPL"

import orca.atspi as atspi
import orca.braille as braille
import orca.debug as debug
import orca.default as default
import orca.input_event as input_event
import orca.keybindings as keybindings
import orca.orca as orca
import orca.rolenames as rolenames
import orca.speech as speech
import orca.util as util

from orca.orca_i18n import _

########################################################################
#                                                                      #
# The Gaim script class.                                               #
#                                                                      #
########################################################################

class Script(default.Script):

    def __init__(self, app):
        """Creates a new script for the given application.
        
        Arguments:
        - app: the application to create a script for.
        """

        # Set the debug level for all the methods in this script.
        #
        self.debugLevel = debug.LEVEL_FINEST

        # Whether we prefix chat room messages with the name of the chat room.
        #
        self.prefixChatMessage = False

        default.Script.__init__(self, app)

    def setupInputEventHandlers(self):
        """Defines InputEventHandler fields for this script that can be
        called by the key and braille bindings. In this particular case,
        we just want to be able to add a handler to toggle whether we
        prefix chat room messages with the name of the chat room.
        """

        debug.println(self.debugLevel, "gaim.setupInputEventHandlers.")

        default.Script.setupInputEventHandlers(self)
        self.togglePrefixHandler = input_event.InputEventHandler(
            Script.togglePrefix,
            _("Toggle whether we prefix chat room messages with the name of the chat room."))

    def getKeyBindings(self):
        """Defines the key bindings for this script. Setup the default
        key bindings, then add one in for toggling whether we prefix 
        chat room messages with the name of the chat room.

        Returns an instance of keybindings.KeyBindings.
        """

        debug.println(self.debugLevel, "gaim.getKeyBindings.")

        keyBindings = default.Script.getKeyBindings(self)
        keyBindings.add(
            keybindings.KeyBinding(
                "h",
                1 << orca.MODIFIER_ORCA,
                1 << orca.MODIFIER_ORCA,
                self.togglePrefixHandler))

        return keyBindings

    def togglePrefix(self, inputEvent):
        """ Toggle whether we prefix chat room messages with the name of 
        the chat room.

        Arguments:
        - inputEvent: if not None, the input event that caused this action.
        """

        debug.println(self.debugLevel, "gaim.togglePrefix.")

        line = _("speak chat room name.")
        self.prefixChatMessage = not self.prefixChatMessage
        if not self.prefixChatMessage:
            line = _("Don't ") + line

        speech.speak(line)

        return True

    def getChatRoomName(self, obj):
        """Walk up the hierarchy until we've found the page tab for this
        chat room, and return the label of that object.

        Arguments:
        - obj: the accessible component to start from.

        Returns the label of the page tab component (the name of the 
        chat room).
        """

        while True:
            if obj and (obj.role != rolenames.ROLE_PAGE_TAB):
                obj = obj.parent
            else:
                return obj.name

        return None

    def onTextInserted(self, event):
        """Called whenever text is inserted into one of Gaim's text
        objects.  If the object is an instant message or chat, speak
        the text. If we're not watching anything, do the default
        behavior.

        Arguments:
        - event: the text inserted Event
        """

        # util.printAncestry(event.source)

        # Check to see if something has changed in a chat room. If it has,
        # then we get the previous contents of the chat room message area
        # and speak/braille anything new that has arrived.
        #
        rolesList = [rolenames.ROLE_TEXT, \
                     rolenames.ROLE_SCROLL_PANE, \
                     rolenames.ROLE_FILLER, \
                     rolenames.ROLE_PANEL]
        if util.isDesiredFocusedItem(event.source, rolesList):
            debug.println(self.debugLevel,
                          "gaim.onTextInserted - chat room text.")

            # We always automatically go back to focus tracking mode when
            # someone sends us a message.
            #
            if self.flatReviewContext:
                self.toggleFlatReviewMode()

            text = ""
            if self.prefixChatMessage:
                chatRoomName = self.getChatRoomName(event.source)
                text += _("Message from chat room ") + chatRoomName
            text += event.source.text.getText(event.detail1, 
                                              event.detail1 + event.detail2)

            braille.displayMessage(text)
            speech.speak(text)
            return

        if not event.source.state.count(atspi.Accessibility.STATE_FOCUSED):
            # [[[TODO: WDW - HACK to handle the case where the
            # area where the user types loses focus and never
            # regains it with respect to the AT-SPI regardless if
            # it really gets it with respect to the toolkit.  The
            # way we are guessing we are really in the area where
            # you type is because the text does not end in a
            # "\n".  This is related to bug
            # http://bugzilla.gnome.org/show_bug.cgi?id=325917]]]
            #
            debug.println(debug.LEVEL_WARNING,
                          "WARNING in gaim.py: "
                          + "the text area has not regained focus")
            orca.setLocusOfFocus(event, event.source, False)

        # Pass the event onto the parent class to be handled in the 
        # default way.
        #
        default.Script.onTextInserted(self, event)
