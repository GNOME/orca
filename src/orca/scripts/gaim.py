# Orca
#
# Copyright 2004-2007 Sun Microsystems Inc.
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
monitor both the IM input and IM output text areas at the same time.

The following script specific key sequences are supported:

  Insert-h      -  Toggle whether we prefix chat room messages with
                   the name of the chat room.
  Insert-[1-9]  -  Speak and braille a previous chat room message.
"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2007 Sun Microsystems Inc."
__license__   = "LGPL"

import gtk
import pyatspi

import orca.braille as braille
import orca.debug as debug
import orca.default as default
import orca.input_event as input_event
import orca.keybindings as keybindings
import orca.orca_state as orca_state
import orca.rolenames as rolenames
import orca.settings as settings
import orca.speech as speech
import orca.speechgenerator as speechgenerator
import orca.where_am_I as where_am_I

from orca.orca_i18n import _
from orca.orca_i18n import ngettext  # for ngettext support

# Whether we prefix chat room messages with the name of the chat room.
#
prefixChatMessage = False

# Whether we announce when a buddy is typing.
#
announceBuddyTyping = False

# Possible ways of how Orca should speak pidgin chat messages.
#
SPEAK_ALL_MESSAGES              = 0
SPEAK_CHANNEL_WITH_FOCUS        = 1
SPEAK_ALL_CHANNELS_WHEN_FOCUSED = 2

# Indicates how pidgin chat messages should be spoken.
#
speakMessages = SPEAK_ALL_MESSAGES

########################################################################
#                                                                      #
# Ring List. A fixed size circular list by Flavio Catalani             #
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/435902       #
#                                                                      #
########################################################################

class RingList:
    def __init__(self, length):
        self.__data__ = []
        self.__full__ = 0
        self.__max__ = length
        self.__cur__ = 0

    def append(self, x):
        if self.__full__ == 1:
            for i in range (0, self.__cur__ - 1):
                self.__data__[i] = self.__data__[i + 1]
            self.__data__[self.__cur__ - 1] = x
        else:
            self.__data__.append(x)
            self.__cur__ += 1
            if self.__cur__ == self.__max__:
                self.__full__ = 1

    def get(self):
        return self.__data__

    def remove(self):
        if (self.__cur__ > 0):
            del self.__data__[self.__cur__ - 1]
            self.__cur__ -= 1

    def size(self):
        return self.__cur__

    def maxsize(self):
        return self.__max__

    def __str__(self):
        return ''.join(self.__data__)

########################################################################
#                                                                      #
# Custom SpeechGenerator                                               #
#                                                                      #
########################################################################

class SpeechGenerator(speechgenerator.SpeechGenerator):
    """Overrides _getSpeechForTableCell() so that we can provide access
    to the expanded/collapsed state and node count for the buddy list.
    """

    def __init__(self, script):
        speechgenerator.SpeechGenerator.__init__(self, script)

    def _getSpeechForTableCell(self, obj, already_focused):
        """Get the speech utterances for a single table cell

        Arguments:
        - obj: the table cell
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = speechgenerator.SpeechGenerator._getSpeechForTableCell( \
            self, obj, already_focused)

        if not self._script.isInBuddyList(obj):
            return utterances

        # The Pidgin buddy list consists of two columns. The column which
        # is set as the expander column and which also contains the node
        # relationship is hidden.  Hidden columns are not included among
        # a table's columns.  The hidden object of interest seems to always
        # immediately precede the visible object.
        #
        expanderCell = obj.parent[obj.getIndexInParent() - 1]
        if not expanderCell:
            return utterances

        state = expanderCell.getState()
        if state.contains(pyatspi.STATE_EXPANDABLE):
            if state.contains(pyatspi.STATE_EXPANDED):
                # Translators: this represents the state of a node in a tree.
                # 'expanded' means the children are showing.
                # 'collapsed' means the children are not showing.
                #
                utterances.append(_("expanded"))
                childNodes = self._script.getChildNodes(expanderCell)
                children = len(childNodes)

                if not children \
                   or (settings.speechVerbosityLevel == \
                       settings.VERBOSITY_LEVEL_VERBOSE):
                    # Translators: this is the number of items in a layered
                    # pane or table.
                    #
                    itemString = ngettext("%d item",
                                          "%d items",
                                          children) % children
                    utterances.append(itemString)
            else:
                # Translators: this represents the state of a node in a tree.
                # 'expanded' means the children are showing.
                # 'collapsed' means the children are not showing.
                #
                utterances.append(_("collapsed"))

        self._debugGenerator("gaim._getSpeechForTableCell",
                             obj,
                             already_focused,
                             utterances)

        return utterances

########################################################################
#                                                                      #
# Custom WhereAmI                                                      #
#                                                                      #
######################################################################## 

class WhereAmI(where_am_I.WhereAmI):
    """Overrides _speakTableCell() so that we can provide access
    to the expanded/collapsed state for items in the buddy list.
    """

    def __init__(self, script):
        where_am_I.WhereAmI.__init__(self, script)
        self._script = script
        
    def _speakTableCell(self, obj, doubleClick):
        """Tree Tables present the following information (an example is
        'Tree table, Mike Pedersen, row 8 of 10, tree level 2'):

        1. label, if any
        2. role
        3. current row (regardless of speak cell/row setting)
        4. relative position
        5. if expandable/collapsible: expanded/collapsed
        6. if applicable, the level

        """

        if not self._script.isInBuddyList(obj):
            return where_am_I.WhereAmI._speakTableCell(self, obj, doubleClick)

        # Speak the first two items (and possibly the position)
        #
        utterances = []
        if obj.parent.getRole() == pyatspi.ROLE_TABLE_CELL:
            obj = obj.parent
        parent = obj.parent

        text = self._getObjLabel(obj)
        utterances.append(text)

        text = rolenames.getSpeechForRoleName(obj)
        utterances.append(text)
        debug.println(self._debugLevel, "first table cell utterances=%s" % \
                      utterances)
        speech.speakUtterances(utterances)

        utterances = []
        if doubleClick:
            table = parent.queryTable()
            row = table.getRowAtIndex(
              orca_state.locusOfFocus.getIndexInParent())
            # Translators: this in reference to a row in a table.
            #
            text = _("row %d of %d") % ((row+1), table.nRows)
            utterances.append(text)
            speech.speakUtterances(utterances)

        # Speak the current row
        #
        utterances = self._getTableRow(obj)
        debug.println(self._debugLevel, "second table cell utterances=%s" % \
                      utterances)
        speech.speakUtterances(utterances)

        # Speak the remaining items.
        #
        utterances = []

        if not doubleClick:
            try:
                table = parent.queryTable()
            except NotImplementedError:
                debug.println(self._debugLevel, 
                              "??? parent=%s" % parent.getRoleName())
                return
            else:
                row = \
                    table.getRowAtIndex(
                       orca_state.locusOfFocus.getIndexInParent())
                # Translators: this in reference to a row in a table.
                #
                text = _("row %d of %d") % ((row+1), table.nRows)
                utterances.append(text)

        # The difference/reason for overriding:  We obtain the expanded
        # state from the hidden object that immediately precedes obj.
        #
        try:
            state = obj.parent[obj.getIndexInParent() - 1].getState()
        except:
            state = obj.getState()

        if state.contains(pyatspi.STATE_EXPANDABLE):
            if state.contains(pyatspi.STATE_EXPANDED):
                # Translators: this represents the state of a node in a tree.
                # 'expanded' means the children are showing.
                # 'collapsed' means the children are not showing.
                #
                text = _("expanded")
            else:
                # Translators: this represents the state of a node in a tree.
                # 'expanded' means the children are showing.
                # 'collapsed' means the children are not showing.
                #
                text = _("collapsed")
            utterances.append(text)

        level = self._script.getNodeLevel(orca_state.locusOfFocus)
        if level >= 0:
            # Translators: this represents the depth of a node in a tree
            # view (i.e., how many ancestors a node has).
            #
            utterances.append(_("tree level %d") % (level + 1))

        debug.println(self._debugLevel, "third table cell utterances=%s" % \
                      utterances)
        speech.speakUtterances(utterances)

########################################################################
#                                                                      #
# The Gaim script class.                                               #
#                                                                      #
########################################################################

class Script(default.Script):

    MESSAGE_LIST_LENGTH = 9

    def __init__(self, app):
        """Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """

        # Set the debug level for all the methods in this script.
        #
        self.debugLevel = debug.LEVEL_FINEST

        # Create two cyclic lists; one that will contain the previous
        # chat room messages and the other that will contain the names
        # of the associated chat rooms.
        #
        self.previousMessages = RingList(Script.MESSAGE_LIST_LENGTH)
        self.previousChatRoomNames = RingList(Script.MESSAGE_LIST_LENGTH)

        # Initially populate the cyclic lists with empty strings.
        #
        i = 0
        while i < self.previousMessages.maxsize():
            self.previousMessages.append("")
            i += 1

        i = 0
        while i < self.previousChatRoomNames.maxsize():
            self.previousChatRoomNames.append("")
            i += 1

        # Keep track of the various text areas for chatting.
        # The key is the tab and the value is the text area where
        # the chat occurs.
        #
        self.chatAreas = {}

        # Button to handle preferences setting saying whether we want to 
        # prefix the chat room name for our messages.
        #
        self.speakNameCheckButton = None

        # Keep track of the last status message to see if it's changed.
        #
        self.lastStatus = None

        # To make pylint happy.
        #
        self.focusedChannelRadioButton = None
        self.allChannelsRadioButton = None
        self.allMessagesRadioButton = None
        self.buddyTypingCheckButton = None

        default.Script.__init__(self, app)

    def getListeners(self):
        """Add in an AT-SPI event listener "object:children-changed:"
        events, for this script.
        """

        listeners = default.Script.getListeners(self)
        listeners["object:children-changed:"] = self.onChildrenChanged

        return listeners

    def setupInputEventHandlers(self):
        """Defines InputEventHandler fields for this script that can be
        called by the key and braille bindings. In this particular case,
        we just want to be able to add a handler to toggle whether we
        prefix chat room messages with the name of the chat room.
        """

        debug.println(self.debugLevel, "gaim.setupInputEventHandlers.")

        default.Script.setupInputEventHandlers(self)
        self.inputEventHandlers["togglePrefixHandler"] = \
            input_event.InputEventHandler(
                Script.togglePrefix,
                _("Toggle whether we prefix chat room messages with " \
                  "the name of the chat room."))

        self.inputEventHandlers["toggleBuddyTypingHandler"] = \
            input_event.InputEventHandler(
                Script.toggleBuddyTyping,
                _("Toggle whether we announce when our buddies are typing."))

        # Add the chat room message history event handler.
        #
        self.inputEventHandlers["reviewMessage"] = \
            input_event.InputEventHandler(
                Script.readPreviousMessage,
                _("Speak and braille a previous chat room message."))

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
                1 << settings.MODIFIER_ORCA,
                1 << settings.MODIFIER_ORCA,
                self.inputEventHandlers["togglePrefixHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "",
                None,
                None,
                self.inputEventHandlers["toggleBuddyTypingHandler"]))

        # keybindings to provide chat room message history.
        #
        messageKeys = [ "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9" ]
        for messageKey in messageKeys:
            keyBindings.add(
                keybindings.KeyBinding(
                    messageKey,
                    1 << settings.MODIFIER_ORCA,
                    1 << settings.MODIFIER_ORCA,
                    self.inputEventHandlers["reviewMessage"]))

        return keyBindings

    def getSpeechGenerator(self):
        """Returns the speech generator for this script.
        """

        return SpeechGenerator(self)

    def getWhereAmI(self):
        """Returns the 'where am I' class for this script.
        """
        
        return WhereAmI(self)

    def getAppPreferencesGUI(self):
        """Return a GtkVBox contain the application unique configuration
        GUI items for the current application.
        """

        vbox = gtk.VBox(False, 0)
        vbox.set_border_width(12)
        gtk.Widget.show(vbox)

        # Translators: If this checkbox is checked, then Orca will speak
        # the name of the chat room.
        #
        label = _("_Speak Chat Room name")
        self.speakNameCheckButton = gtk.CheckButton(label)
        gtk.Widget.show(self.speakNameCheckButton)
        gtk.Box.pack_start(vbox, self.speakNameCheckButton, False, False, 0)
        gtk.ToggleButton.set_active(self.speakNameCheckButton,
                                    prefixChatMessage)

        # Translators: If this checkbox is checked, then Orca will tell
        # you when one of your buddies is typing a message.
        #
        label = _("Announce when your _buddies are typing")
        self.buddyTypingCheckButton = gtk.CheckButton(label)
        gtk.Widget.show(self.buddyTypingCheckButton)
        gtk.Box.pack_start(vbox, self.buddyTypingCheckButton, False, False, 0)
        gtk.ToggleButton.set_active(self.buddyTypingCheckButton,
                                    announceBuddyTyping)

        # "Speak Messages" frame.
        #
        messagesFrame = gtk.Frame()
        gtk.Widget.show(messagesFrame)
        gtk.Box.pack_start(vbox, messagesFrame, False, False, 5)

        messagesAlignment = gtk.Alignment(0.5, 0.5, 1, 1)
        gtk.Widget.show(messagesAlignment)
        gtk.Container.add(messagesFrame, messagesAlignment)
        gtk.Alignment.set_padding(messagesAlignment, 0, 0, 12, 0)

        messagesVBox = gtk.VBox(False, 0)
        gtk.Widget.show(messagesVBox)
        gtk.Container.add(messagesAlignment, messagesVBox)

        # Translators: Orca will speak all new chat messages as they appear
        # irrespective of whether the pidgin application currently has focus.
        # This is the default behaviour.
        #
        self.allMessagesRadioButton = gtk.RadioButton(None, _("All cha_nnels"))
        gtk.Widget.show(self.allMessagesRadioButton)
        gtk.Box.pack_start(messagesVBox, self.allMessagesRadioButton,
                           False, False, 0)
        gtk.ToggleButton.set_active(self.allMessagesRadioButton,
                                    (speakMessages == SPEAK_ALL_MESSAGES))


        # Translators: Orca will speak only new chat messages for the channel
        # that currently has focus, irrespective of whether the pidgin
        # application has focus.
        #
        self.focusedChannelRadioButton = gtk.RadioButton( \
                             self.allMessagesRadioButton, \
                             _("A channel only if its _window is active"))
        gtk.Widget.show(self.focusedChannelRadioButton)
        gtk.Box.pack_start(messagesVBox, self.focusedChannelRadioButton,
                           False, False, 0)
        gtk.ToggleButton.set_active(self.focusedChannelRadioButton,
                              (speakMessages == SPEAK_CHANNEL_WITH_FOCUS))

        # Translators: Orca will speak new chat messages for all channels 
        # only when the pidgin application has focus.
        #
        self.allChannelsRadioButton = gtk.RadioButton( \
                        self.allMessagesRadioButton,
                       _("All channels when an_y Pidgin window is active"))
        gtk.Widget.show(self.allChannelsRadioButton)
        gtk.Box.pack_start(messagesVBox, self.allChannelsRadioButton,
                           False, False, 0)
        gtk.ToggleButton.set_active(self.allChannelsRadioButton,
                       (speakMessages == SPEAK_ALL_CHANNELS_WHEN_FOCUSED))

        # Translators: this is the title of a panel holding options for
        # how messages in the pidgin chat rooms should be spoken.
        #
        messagesLabel = gtk.Label("<b>%s</b>" % _("Speak messages from"))
        gtk.Widget.show(messagesLabel)
        gtk.Frame.set_label_widget(messagesFrame, messagesLabel)
        messagesFrame.set_shadow_type(gtk.SHADOW_NONE)
        gtk.Label.set_use_markup(messagesLabel, True)

        return vbox

    def setAppPreferences(self, prefs):
        """Write out the application specific preferences lines and set the
        new values.

        Arguments:
        - prefs: file handle for application preferences.
        """

        global announceBuddyTyping, prefixChatMessage, speakMessages

        prefixChatMessage = self.speakNameCheckButton.get_active()
        prefs.writelines("\n")
        prefs.writelines("orca.scripts.gaim.prefixChatMessage = %s\n" % \
                         prefixChatMessage)

        announceBuddyTyping = self.buddyTypingCheckButton.get_active()
        prefs.writelines("orca.scripts.gaim.announceBuddyTyping = %s\n" % \
                         announceBuddyTyping)

        if self.allMessagesRadioButton.get_active():
            speakMessages = SPEAK_ALL_MESSAGES
            option = "orca.scripts.gaim.SPEAK_ALL_MESSAGES"
        elif self.focusedChannelRadioButton.get_active():
            speakMessages = SPEAK_CHANNEL_WITH_FOCUS
            option = "orca.scripts.gaim.SPEAK_CHANNEL_WITH_FOCUS"
        elif self.allChannelsRadioButton.get_active():
            speakMessages = SPEAK_ALL_CHANNELS_WHEN_FOCUSED
            option = "orca.scripts.gaim.SPEAK_ALL_CHANNELS_WHEN_FOCUSED"
        prefs.writelines("\n")
        prefs.writelines("orca.scripts.gaim.speakMessages = %s\n" % option)

    def getAppState(self):
        """Returns an object that can be passed to setAppState.  This
        object will be use by setAppState to restore any state information
        that was being maintained by the script."""
        return [default.Script.getAppState(self),
                self.previousMessages,
                self.previousChatRoomNames,
                self.chatAreas]

    def setAppState(self, appState):
        """Sets the application state using the given appState object.

        Arguments:
        - appState: an object obtained from getAppState
        """
        try:
            [defaultAppState,
             self.previousMessages,
             self.previousChatRoomNames,
             self.chatAreas] = appState
            default.Script.setAppState(self, defaultAppState)
        except:
            debug.printException(debug.LEVEL_WARNING)

    def togglePrefix(self, inputEvent):
        """ Toggle whether we prefix chat room messages with the name of
        the chat room.

        Arguments:
        - inputEvent: if not None, the input event that caused this action.
        """

        global prefixChatMessage

        debug.println(self.debugLevel, "gaim.togglePrefix.")

        line = _("speak chat room name.")
        prefixChatMessage = not prefixChatMessage
        if not prefixChatMessage:
            line = _("Do not speak chat room name.")

        speech.speak(line)

        return True

    def toggleBuddyTyping(self, inputEvent):
        """ Toggle whether we announce when our buddies are typing a message.

        Arguments:
        - inputEvent: if not None, the input event that caused this action.
        """

        global announceBuddyTyping

        debug.println(self.debugLevel, "gaim.toggleBuddyTyping.")

        line = _("announce when your buddies are typing.")
        announceBuddyTyping = not announceBuddyTyping
        if not announceBuddyTyping:
            line = _("Do not announce when your buddies are typing.")

        speech.speak(line)

        return True

    def utterMessage(self, chatRoomName, message, hasFocus=True):
        """ Speak/braille a chat room message.

        Arguments:
        - chatRoomName: name of the chat room this message came from.
        - message: the chat room message.
        """

        # Only speak/braille the new message if it matches how the user 
        # wants chat messages spoken.
        #
        if speakMessages == SPEAK_ALL_CHANNELS_WHEN_FOCUSED and \
           orca_state.activeScript != self:
            return
        elif speakMessages == SPEAK_CHANNEL_WITH_FOCUS and not hasFocus:
            return

        text = ""
        if prefixChatMessage:
            if chatRoomName and chatRoomName != "":
                text += _("Message from chat room %s") % chatRoomName + " "
        if message and message != "":
            text += message

        if len(text.strip()):
            speech.speak(text)
        braille.displayMessage(text)

    def readPreviousMessage(self, inputEvent):
        """ Speak/braille a previous chat room message. Up to nine
        previous messages are kept.

        Arguments:
        - inputEvent: if not None, the input event that caused this action.
        """

        debug.println(self.debugLevel, "gaim.readPreviousMessage.")

        i = int(inputEvent.event_string[1:])
        messageNo = Script.MESSAGE_LIST_LENGTH - i

        chatRoomNames = self.previousChatRoomNames.get()
        chatRoomName = chatRoomNames[messageNo]

        messages = self.previousMessages.get()
        message = messages[messageNo]

        self.utterMessage(chatRoomName, message)

    def getChatRoomTab(self, obj):
        """Walk up the hierarchy until we've found the page tab for this
        chat room, and return that object.

        Arguments:
        - obj: the accessible component to start from.

        Returns the page tab component for the chat room.
        """

        if obj:
            while True:
                if obj:
                    if obj.getRole() == pyatspi.ROLE_APPLICATION:
                        break
                    elif obj.getRole() == pyatspi.ROLE_PAGE_TAB:
                        return obj
                    else:
                        obj = obj.parent
                else:
                    break

        return None

    def onChildrenChanged(self, event):
        """Called whenever a child object changes in some way.

        Arguments:
        - event: the text inserted Event
        """

        # Check to see if a new chat room tab has been created and if it
        # has, then announce its name. See bug #469098 for more details.
        #
        if event.type.startswith("object:children-changed:add"):
            rolesList = [pyatspi.ROLE_PAGE_TAB_LIST, \
                         pyatspi.ROLE_FILLER, \
                         pyatspi.ROLE_FRAME]
            if self.isDesiredFocusedItem(event.source, rolesList):
                # As it's possible to get this component hierarchy in other
                # places than the chat room (i.e. the Preferences dialog),
                # we check to see if the name of the frame is the same as one
                # of its children. If it is, then it's a chat room tab event.
                # For a final check, we only announce the new chat tab if the
                # last child has a name.
                #
                nameFound = False
                frameName = event.source.parent.parent.name
                for child in event.source:
                    if frameName and (frameName == child.name):
                        nameFound = True
                if nameFound:
                    child = event.source[-1]
                    if child.name:
                        line = _("New chat tab %s") % child.name
                        speech.speak(line)

    def isBuddyListEvent(self, event):
        """If pidgin gets a status changed message for one of the users
        buddies then just ignore it. See bug #525644 for more details.

        Arguments:
        - event: the Event

        Return an indication of whether this is a buddy list event.
        """

        isBuddyListEvent = False
        rolesList = [pyatspi.ROLE_TABLE_CELL, \
                     pyatspi.ROLE_TABLE_CELL, \
                     pyatspi.ROLE_TREE_TABLE, \
                     pyatspi.ROLE_SCROLL_PANE, \
                     pyatspi.ROLE_FILLER, \
                     pyatspi.ROLE_PAGE_TAB, \
                     pyatspi.ROLE_PAGE_TAB_LIST]
        if self.isDesiredFocusedItem(event.source, rolesList):
            isBuddyListEvent = True

        return isBuddyListEvent

    def onTextDeleted(self, event):
        """Called whenever text is deleted from an object.

        Arguments:
        - event: the Event
        """

        if self.isBuddyListEvent(event):
            return
        else:
            default.Script.onTextDeleted(self, event)

    def onNameChanged(self, event):
        """Called whenever a property on an object changes.

        Arguments:
        - event: the Event
        """

        if self.isBuddyListEvent(event):
            return
        else:
            default.Script.onNameChanged(self, event)

    def onValueChanged(self, event):
        """Called whenever an object's value changes.  Currently, the
        value changes for non-focused objects are ignored.

        Arguments:
        - event: the Event
        """

        if self.isBuddyListEvent(event):
            return
        else:
            default.Script.onValueChanged(self, event)

    def onTextInserted(self, event):
        """Called whenever text is inserted into one of Gaim's text
        objects.  If the object is an instant message or chat, speak
        the text. If we're not watching anything, do the default
        behavior.

        Arguments:
        - event: the text inserted Event
        """

        if self.isBuddyListEvent(event):
            return

        chatRoomTab = self.getChatRoomTab(event.source)
        if not chatRoomTab:
            default.Script.onTextInserted(self, event)
            return

        # [[[TODO: HACK - it looks as though the GAIM chat area may
        # not start emitting text inserted events until we tickle it
        # by looking at it in the hierarchy.  The simple workaround of
        # entering flat review and exiting does this.  So, we tickle
        # the hierarchy here.  We probably should be trying somewhere
        # else since we may miss the first message in a chat area.  In
        # addition, this is a source of a very small memory leak since
        # we do not free up the entries when the tab goes away.  One
        # would have to engage in hundreds of chats with hundreds of
        # different people from the same instance of gaim for that
        # memory leak to have an issue here.  One thing we could do if
        # that is deemed a severe enough problem is to check for
        # children-changed events and clean up in that.]]]
        #
        chatArea = None
        if not self.chatAreas.has_key(chatRoomTab):
            # Different message types (AIM, IRC ...) have a different
            # component hierarchy for their chat rooms. By testing
            # with AIM and IRC, we've found that the messages area for
            # those two type of chats has an index that is the penultimate
            # text field. Hopefully this is true for other types of chat
            # as well, but is currently untested.
            #
            allTextFields = self.findByRole(chatRoomTab,
                                            pyatspi.ROLE_TEXT,
                                            False)
            index = len(allTextFields) - 2
            if index >= 0:
                self.chatAreas[chatRoomTab] = allTextFields[index]
                chatArea = self.chatAreas[chatRoomTab]
        else:
            chatArea = self.chatAreas[chatRoomTab]

        if event.source and (event.source == chatArea):
            # We always automatically go back to focus tracking mode when
            # someone sends us a message.
            #
            if self.flatReviewContext:
                self.toggleFlatReviewMode()

            message = self.getText(event.source,
                                   event.detail1,
                                   event.detail1 + event.detail2)
            if message and message[0] == "\n":
                message = message[1:]

            chatRoomName = self.getDisplayedText(chatRoomTab)

            # If the user doesn't want announcements for when their buddies
            # are typing (or have stopped typing), and this is such a message,
            # then just return. The only reliable way to identify such text
            # is by the scale.  We also want to store the last message because
            # msn seems to be sending a constant stream of "is typing" updates.
            #
            attr, start, end = \
                self.getTextAttributes(event.source, event.detail1)
            if float(attr.get('scale', '1')) < 1:
                if not announceBuddyTyping or self.lastStatus == message:
                    return
                self.lastStatus = message
            else:
                self.lastStatus = None

            # If the new message came from the room with focus, we don't
            # want to speak its name even if prefixChatMessage is enabled.
            #
            state = event.source.getState()
            hasFocus = state.contains(pyatspi.STATE_SHOWING)
            if hasFocus:
                chatRoomName = ""
            self.utterMessage(chatRoomName, message, hasFocus)

            # Add the latest message to the list of saved ones. For each
            # one added, the oldest one automatically gets dropped off.
            # We don't want to do this for the status messages however.
            #
            if not self.lastStatus:
                self.previousMessages.append(message)
                self.previousChatRoomNames.append(chatRoomName)

        elif isinstance(orca_state.lastInputEvent, input_event.KeyboardEvent) \
             and orca_state.lastNonModifierKeyEvent \
             and (orca_state.lastNonModifierKeyEvent.event_string == "Tab") \
             and event.any_data and (event.any_data != "\t"):
            # This is autocompleted text (the name of a user in an IRC
            # chatroom).  The default script isn't announcing it because
            # it's not selected.
            #
            text = event.any_data
            if text.isupper():
                speech.speak(text, self.voices[settings.UPPERCASE_VOICE])
            else:
                speech.speak(text)

        else:
            # Pass the event onto the parent class to be handled in the
            # default way.
            #
            default.Script.onTextInserted(self, event)

    def isInBuddyList(self, obj):
        """Determines whether or not this object is in the buddy list.

        Arguments:
        -obj: the Accessible object
        """

        rolesList = [pyatspi.ROLE_TABLE_CELL,
                     pyatspi.ROLE_TREE_TABLE,
                     pyatspi.ROLE_SCROLL_PANE,
                     pyatspi.ROLE_FILLER,
                     pyatspi.ROLE_PAGE_TAB]

        return self.isDesiredFocusedItem(obj, rolesList)
        
    def getNodeLevel(self, obj):
        """Determines the node level of this object if it is in a tree
        relation, with 0 being the top level node.  If this object is
        not in a tree relation, then -1 will be returned. Overridden
        here because the accessible we need is in a hidden column.

        Arguments:
        -obj: the Accessible object
        """

        if not obj:
            return -1

        if not self.isInBuddyList(obj):
            return default.Script.getNodeLevel(self, obj)

        obj = obj.parent[obj.getIndexInParent() - 1]

        try:
            table = obj.parent.queryTable()
        except:
            return -1

        nodes = []
        node = obj
        done = False
        while not done:
            relations = node.getRelationSet()
            node = None
            for relation in relations:
                if relation.getRelationType() \
                       == pyatspi.RELATION_NODE_CHILD_OF:
                    node = relation.getTarget(0)
                    break

            # We want to avoid situations where something gives us an
            # infinite cycle of nodes.  Bon Echo has been seen to do
            # this (see bug 351847).
            #
            if (len(nodes) > 100) or nodes.count(node):
                debug.println(debug.LEVEL_WARNING,
                              "gaim.getNodeLevel detected a cycle!!!")
                done = True
            elif node:
                nodes.append(node)
                debug.println(debug.LEVEL_FINEST,
                              "gaim.getNodeLevel %d" % len(nodes))
            else:
                done = True

        return len(nodes) - 1

    def getChildNodes(self, obj):
        """Gets all of the children that have RELATION_NODE_CHILD_OF pointing
        to this expanded table cell. Overridden here because the object
        which contains the relation is in a hidden column and thus doesn't
        have a column number (necessary for using getAccessibleAt()).

        Arguments:
        -obj: the Accessible Object

        Returns: a list of all the child nodes
        """

        if not self.isInBuddyList(obj):
            return default.Script.getChildNodes(self, obj)

        try:
            table = obj.parent.queryTable()
        except:
            return []
        else:
            if not obj.getState().contains(pyatspi.STATE_EXPANDED):
                return []

        nodes = []        
        row = table.getRowAtIndex(obj.getIndexInParent())
        col = table.getColumnAtIndex(obj.getIndexInParent() + 1)
        nodeLevel = self.getNodeLevel(obj)
        done = False

        # Candidates will be in the rows beneath the current row.
        # Only check in the current column and stop checking as
        # soon as the node level of a candidate is equal or less
        # than our current level.
        #
        for i in range(row+1, table.nRows):
            cell = table.getAccessibleAt(i, col)
            nodeCell = cell.parent[cell.getIndexInParent() - 1]
            relations = nodeCell.getRelationSet()
            for relation in relations:
                if relation.getRelationType() \
                       == pyatspi.RELATION_NODE_CHILD_OF:
                    nodeOf = relation.getTarget(0)
                    if self.isSameObject(obj, nodeOf):
                        nodes.append(cell)
                    else:
                        currentLevel = self.getNodeLevel(nodeOf)
                        if currentLevel <= nodeLevel:
                            done = True
                    break
            if done:
                break

        return nodes

    def visualAppearanceChanged(self, event, obj):
        """Called when the visual appearance of an object changes.
        Overridden here because we get object:state-changed:expanded
        events for the buddy list, but the obj is in a hidden column.

        Arguments:
        - event: if not None, the Event that caused this to happen
        - obj: the Accessible whose visual appearance changed.
        """

        if self.isInBuddyList(obj) \
           and event.type.startswith("object:state-changed:expanded"):

            # The event is associated with the invisible cell. Set it
            # to the visible cell and then let the default script do
            # its thing.
            #
            obj = obj.parent[obj.getIndexInParent() + 1]
            
        default.Script.visualAppearanceChanged(self, event, obj)

