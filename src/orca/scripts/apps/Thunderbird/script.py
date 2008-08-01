# Orca
#
# Copyright 2004-2008 Sun Microsystems Inc.
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
# Free Software Foundation, Inc., Franklin Street, Fifth Floor,
# Boston MA  02110-1301 USA.

""" Custom script for Thunderbird 3.
"""

__id__        = "$Id: $"
__version__   = "$Revision: $"
__date__      = "$Date: $"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import gtk
import pyatspi

import orca.orca as orca
import orca.debug as debug
import orca.default as default
import orca.input_event as input_event
import orca.orca_state as orca_state
import orca.settings as settings
import orca.speech as speech
import orca.scripts.toolkits.Gecko as Gecko

from orca.orca_i18n import _

from speech_generator import SpeechGenerator
import script_settings

########################################################################
#                                                                      #
# The Thunderbird script class.                                        #
#                                                                      #
########################################################################

class Script(Gecko.Script):
    """The script for Thunderbird."""

    _containingPanelName = ""

    def __init__(self, app):
        """ Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """

        # Set the debug level for all the methods in this script.
        self.debugLevel = debug.LEVEL_FINEST

        # Store the last autocompleted string for the address fields
        # so that we're not too 'chatty'.  See bug #533042.
        #
        self._lastAutoComplete = ""

        # When a mail message gets focus, we'll get a window:activate event
        # followed by two focus events for the document frame.  We want to
        # present the message if it was just opened; we don't if it was
        # already opened and the user has just returned focus to it. Store
        # the fact that a message was loaded which we should present once
        # the document frame claims focus. See bug #541018.
        #
        self._messageLoaded = False

        Gecko.Script.__init__(self, app)

        # This will be used to cache a handle to the Thunderbird text area for
        # spell checking purposes.

        self.textArea = None

    def getSpeechGenerator(self):
        """Returns the speech generator for this script.
        """
        return SpeechGenerator(self)

    def getAppPreferencesGUI(self):
        """Return a GtkVBox contain the application unique configuration
        GUI items for the current application.
        """

        vbox = Gecko.Script.getAppPreferencesGUI(self)

        # Reapply "say all on load" using the Thunderbird specific setting.
        #
        gtk.ToggleButton.set_active(self.sayAllOnLoadCheckButton,
                                    script_settings.sayAllOnLoad)

        return vbox

    def setAppPreferences(self, prefs):
        """Write out the application specific preferences lines and set the
        new values.

        Arguments:
        - prefs: file handle for application preferences.
        """

        Gecko.Script.setAppPreferences(self, prefs)

        # Write the Thunderbird specific setting.
        #
        prefix = "orca.scripts.apps.Thunderbird.script_settings"
        value = self.sayAllOnLoadCheckButton.get_active()
        prefs.writelines("%s.sayAllOnLoad = %s\n" % (prefix, value))
        script_settings.sayAllOnLoad = value

    def _debug(self, msg):
        """ Convenience method for printing debug messages
        """
        debug.println(self.debugLevel, "Thunderbird.py: "+msg)

    def _isSpellCheckListItemFocus(self, event):
        """Check if this event is for a list item in the spell checking
        dialog and whether it has a FOCUSED state.

        Arguments:
        - event: the Event

        Return True is this event is for a list item in the spell checking 
        dialog and it doesn't have a FOCUSED state, Otherwise return False.
        """

        rolesList = [pyatspi.ROLE_LIST_ITEM, \
                     pyatspi.ROLE_LIST, \
                     pyatspi.ROLE_DIALOG, \
                     pyatspi.ROLE_APPLICATION]
        if self.isDesiredFocusedItem(event.source, rolesList):
            dialog = event.source.parent.parent

            # Translators: this is what the name of the spell checking
            # dialog in Thunderbird begins with. The translated form
            # has to match what Thunderbird is using.  We hate keying
            # off stuff like this, but we're forced to do so in this case.
            #
            if dialog.name.startswith(_("Check Spelling")):
                state = event.source.getState()
                if not state.contains(pyatspi.STATE_FOCUSED):
                    return True

        return False

    def onFocus(self, event):
        """ Called whenever an object gets focus.

        Arguments:
        - event: the Event

        """
        obj = event.source
        parent = obj.parent
        top = self.getTopLevel(obj)
        consume = False

        # Clear the stored autocomplete string.
        #
        self._lastAutoComplete = ""

        # Don't speak chrome URLs.
        #
        if obj.name.startswith("chrome://"):
            return

        # This is a better fix for bug #405541. Thunderbird gives
        # focus to the cell in the column that is being sorted
        # (e.g., Date). Braille should show the row from the begining.
        # This fix calls orca.setLocusOfFocus to give focus to the
        # cell at the beginning of the row. It consume the event
        # so Gecko.py doesn't reset the focus.
        #
        if obj.getRole() == pyatspi.ROLE_TABLE_CELL:
            table = parent.queryTable()
            index = self.getCellIndex(obj)
            row = table.getRowAtIndex(index)
            acc = table.getAccessibleAt(row, 0)
            orca.setLocusOfFocus(event, acc)
            consume = True

        # Text area (for caching handle for spell checking purposes).
        #
        # This works in conjunction with code in the onNameChanged()
        # method. Check to see if focus is currently in the Thunderbird
        # message area. If it is, then, if this is the first time, save
        # a pointer to the document frame which contains the text being
        # edited.
        #
        # Note that this drops through to then use the default event
        # processing in the parent class for this "focus:" event.

        rolesList = [pyatspi.ROLE_DOCUMENT_FRAME,
                     pyatspi.ROLE_INTERNAL_FRAME,
                     pyatspi.ROLE_FRAME,
                     pyatspi.ROLE_APPLICATION]
        if self.isDesiredFocusedItem(event.source, rolesList):
            self._debug("onFocus - message text area.")

            self.textArea = event.source
            # Fall-thru to process the event with the default handler.

        if event.type.startswith("focus:"):
            # If we get a "focus:" event for the "Replace with:" entry in the
            # spell checking dialog, then clear the current locus of focus so
            # that this item will be spoken and brailled. See bug #535192 for
            # more details.
            #
            rolesList = [pyatspi.ROLE_ENTRY, \
                         pyatspi.ROLE_DIALOG, \
                         pyatspi.ROLE_APPLICATION]
            if self.isDesiredFocusedItem(obj, rolesList):
                dialog = obj.parent

                # Translators: this is what the name of the spell checking
                # dialog in Thunderbird begins with. The translated form
                # has to match what Thunderbird is using.  We hate keying
                # off stuff like this, but we're forced to do so in this case.
                #
                if dialog.name.startswith(_("Check Spelling")):
                    orca_state.locusOfFocus = None
                    orca.setLocusOfFocus(event, obj)

            # If we get a "focus:" event for a list item in the spell
            # checking dialog, and it doesn't have a FOCUSED state (i.e.
            # we didn't navigate to it), then ignore it. See bug #535192
            # for more details.
            #
            if self._isSpellCheckListItemFocus(event):
                return

        # Handle dialogs.
        #
        if top and top.getRole() == pyatspi.ROLE_DIALOG:
            self._speakEnclosingPanel(obj)

        # Handle a newly-opened message.
        #
        if event.source.getRole() == pyatspi.ROLE_DOCUMENT_FRAME \
           and orca_state.locusOfFocus.getRole() == pyatspi.ROLE_FRAME \
           and self._messageLoaded:
            consume = True
            self._presentMessage(event.source)

        if not consume:
            Gecko.Script.onFocus(self, event)

    def locusOfFocusChanged(self, event, oldLocusOfFocus, newLocusOfFocus):
        """Called when the visual object with focus changes.

        Arguments:
        - event: if not None, the Event that caused the change
        - oldLocusOfFocus: Accessible that is the old locus of focus
        - newLocusOfFocus: Accessible that is the new locus of focus
        """

        # If the user has just deleted a message from the middle of the 
        # message header list, then we want to speak the newly focused 
        # message in the header list (even though it has the same row 
        # number as the previously deleted message).
        # See bug #536451 for more details.
        #
        rolesList = [pyatspi.ROLE_TABLE_CELL, \
                     pyatspi.ROLE_TREE_TABLE, \
                     pyatspi.ROLE_SCROLL_PANE, \
                     pyatspi.ROLE_SCROLL_PANE, \
                     pyatspi.ROLE_FRAME, \
                     pyatspi.ROLE_APPLICATION]
        if self.isDesiredFocusedItem(event.source, rolesList):
            if isinstance(orca_state.lastInputEvent, input_event.KeyboardEvent):
                string = orca_state.lastNonModifierKeyEvent.event_string
                if string == "Delete":
                    oldLocusOfFocus = None

        # If the user has just deleted an open mail message, then we want to
        # try to speak the new name of the open mail message frame.
        # See bug #540039 for more details.
        #
        rolesList = [pyatspi.ROLE_DOCUMENT_FRAME, \
                     pyatspi.ROLE_INTERNAL_FRAME, \
                     pyatspi.ROLE_FRAME, \
                     pyatspi.ROLE_APPLICATION]
        if self.isDesiredFocusedItem(event.source, rolesList):
            if isinstance(orca_state.lastInputEvent, input_event.KeyboardEvent):
                string = orca_state.lastNonModifierKeyEvent.event_string
                if string == "Delete":
                    oldLocusOfFocus = None
                    state = newLocusOfFocus.getState()
                    if state.contains(pyatspi.STATE_DEFUNCT):
                        newLocusOfFocus = event.source

        # Pass the event onto the parent class to be handled in the default way.

        Gecko.Script.locusOfFocusChanged(self, event,
                                         oldLocusOfFocus, newLocusOfFocus)

    def onStateChanged(self, event):
        """Called whenever an object's state changes.

        Arguments:
        - event: the Event
        """

        if event.type.startswith("object:state-changed:busy"):
            if event.source.getRole() == pyatspi.ROLE_DOCUMENT_FRAME \
               and not event.detail1:
                self._messageLoaded = True
                if self.inDocumentContent():
                    self._presentMessage(event.source)
            return

        default.Script.onStateChanged(self, event)

    def onStateFocused(self, event):
        """Called whenever an object's state changes focus.

        Arguments:
        - event: the Event
        """

        # If we get an "object:state-changed:focused" event for a list
        # item in the spell checking dialog, and it doesn't have a
        # FOCUSED state (i.e. we didn't navigate to it), then ignore it.
        # See bug #535192 for more details.
        #
        if self._isSpellCheckListItemFocus(event):
            return

        Gecko.Script.onStateChanged(self, event)

    def onTextInserted(self, event):
        """Called whenever text is inserted into an object.

        Arguments:
        - event: the Event
        """
        obj = event.source
        parent = obj.parent

        # Speak the autocompleted text, but only if it is different
        # address so that we're not too "chatty." See bug #533042.
        #
        if parent.getRole() == pyatspi.ROLE_AUTOCOMPLETE:
            if event.type.endswith("system") and event.any_data:
                # The autocompleted address may start with the name,
                # or it might start with the text typed by the user
                # followed by ">>" followed by the address. Therefore
                # we'll look at whatever follows the ">>" should it
                # exist.
                #
                address = event.any_data.split(">>")[-1]
                if self._lastAutoComplete != address:
                    speech.speak(address)
                self._lastAutoComplete = address
                return

        Gecko.Script.onTextInserted(self, event)

    def onVisibleDataChanged(self, event):
        """Called when the visible data of an object changes."""

        # [[[TODO: JD - In Gecko.py, we need onVisibleDataChanged() to
        # to detect when the user switches between the tabs holding
        # different URLs in Firefox.  Thunderbird issues very similar-
        # looking events as the user types a subject in the message
        # composition window. For now, rather than trying to distinguish
        # them  in Gecko.py, we'll simply prevent Gecko.py from seeing when
        # Thunderbird issues such an event.]]]
        #
        return

    def onNameChanged(self, event):
        """Called whenever a property on an object changes.

        Arguments:
        - event: the Event
        """

        obj = event.source

        # If the user has just deleted an open mail message, then we want to
        # try to speak the new name of the open mail message frame and also
        # present the first line of that message to be consistent with what
        # we do when a new message window is opened. See bug #540039 for more
        # details.
        #
        rolesList = [pyatspi.ROLE_DOCUMENT_FRAME, \
                     pyatspi.ROLE_INTERNAL_FRAME, \
                     pyatspi.ROLE_FRAME, \
                     pyatspi.ROLE_APPLICATION]
        if self.isDesiredFocusedItem(event.source, rolesList):
            if isinstance(orca_state.lastInputEvent, input_event.KeyboardEvent):
                string = orca_state.lastNonModifierKeyEvent.event_string
                if string == "Delete":
                    speech.speak(obj.name)
                    [obj, offset] = self.findFirstCaretContext(obj, 0)
                    self.setCaretPosition(obj, offset)
                    return

        # If we get a "object:property-change:accessible-name" event for 
        # the first item in the Suggestions lists for the spell checking
        # dialog, then speak the first two labels in that dialog. These
        # will by the "Misspelled word:" label and the currently misspelled
        # word. See bug #535192 for more details.
        #
        rolesList = [pyatspi.ROLE_LIST_ITEM, \
                     pyatspi.ROLE_LIST, \
                     pyatspi.ROLE_DIALOG, \
                     pyatspi.ROLE_APPLICATION]
        if self.isDesiredFocusedItem(obj, rolesList):
            dialog = obj.parent.parent

            # Translators: this is what the name of the spell checking 
            # dialog in Thunderbird begins with. The translated form
            # has to match what Thunderbird is using.  We hate keying
            # off stuff like this, but we're forced to do so in this case.
            #
            if dialog.name.startswith(_("Check Spelling")):
                if obj.getIndexInParent() == 0:
                    badWord = self.getDisplayedText(dialog[1])

                    if self.textArea != None:
                        # If we have a handle to the Thunderbird message text
                        # area, then extract out all the text objects, and
                        # create a list of all the words found in them.
                        #
                        allTokens = []
                        text = self.getText(self.textArea, 0, -1)
                        tokens = text.split()
                        allTokens += tokens
                        self.speakMisspeltWord(allTokens, badWord)

    def _speakEnclosingPanel(self, obj):
        """Speak the enclosing panel for the object, if it is
        named. Going two containers up the hierarchy appears to be far
        enough to find a named panel, if there is one.  Don't speak
        panels whose name begins with 'chrome://'"""

        self._debug("_speakEnclosingPanel")

        parent = obj.parent
        if not parent:
            return

        if parent.name != "" \
            and (not parent.name.startswith("chrome://")) \
            and (parent.getRole() == pyatspi.ROLE_PANEL):

            # Speak the parent panel name, but only once.
            #
            if parent.name != self._containingPanelName:
                self._containingPanelName = parent.name
                utterances = []
                # Translators: this is the name of a panel in Thunderbird.
                #
                text = _("%s panel") % parent.name
                utterances.append(text)
                speech.speakUtterances(utterances)
        else:
            grandparent = parent.parent
            if grandparent \
                and (grandparent.name != "") \
                and (not grandparent.name.startswith("chrome://")) \
                and (grandparent.getRole() == pyatspi.ROLE_PANEL):

                # Speak the grandparent panel name, but only once.
                #
                if grandparent.name != self._containingPanelName:
                    self._containingPanelName = grandparent.name
                    utterances = []
                    # Translators: this is the name of a panel in Thunderbird.
                    #
                    text = _("%s panel") % grandparent.name
                    utterances.append(text)
                    speech.speakUtterances(utterances)

    def _presentMessage(self, documentFrame):
        """Presents the first line of the message, or the entire message,
        depending on the user's sayAllOnLoad setting."""

        [obj, offset] = self.findFirstCaretContext(documentFrame, 0)
        self.setCaretPosition(obj, offset)
        if not script_settings.sayAllOnLoad:
            self.presentLine(obj, offset)
        elif settings.enableSpeech:
            self.sayAll(None)
        self._messageLoaded = False

    def getDocumentFrame(self):
        """Returns the document frame that holds the content being shown.
        Overridden here because multiple open messages are not arranged
        in tabs like they are in Firefox."""

        obj = orca_state.locusOfFocus
        while obj:
            role = obj.getRole()
            if role in [pyatspi.ROLE_DOCUMENT_FRAME, pyatspi.ROLE_EMBEDDED]:
                return obj
            else:
                obj = obj.parent

        return None
