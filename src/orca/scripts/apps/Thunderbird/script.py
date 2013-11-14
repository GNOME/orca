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

""" Custom script for Thunderbird 3."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2004-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi

import orca.orca as orca
import orca.debug as debug
import orca.scripts.default as default
import orca.settings_manager as settings_manager
import orca.orca_state as orca_state
import orca.speech as speech
import orca.scripts.toolkits.Gecko as Gecko
from orca.orca_i18n import _

from .formatting import Formatting
from .speech_generator import SpeechGenerator
from .script_utilities import Utilities
from . import script_settings

_settingsManager = settings_manager.getManager()

########################################################################
#                                                                      #
# The Thunderbird script class.                                        #
#                                                                      #
########################################################################

class Script(Gecko.Script):
    """The script for Thunderbird."""

    def __init__(self, app):
        """ Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """

        # Store the last autocompleted string for the address fields
        # so that we're not too 'chatty'.  See bug #533042.
        #
        self._lastAutoComplete = ""

        Gecko.Script.__init__(self, app)

        # This will be used to cache a handle to the Thunderbird text area for
        # spell checking purposes.

        self.textArea = None

    def getFormatting(self):
        """Returns the formatting strings for this script."""
        return Formatting(self)

    def getSpeechGenerator(self):
        """Returns the speech generator for this script."""

        return SpeechGenerator(self)

    def getUtilities(self):
        """Returns the utilites for this script."""

        return Utilities(self)

    def getAppPreferencesGUI(self):
        """Return a GtkGrid containing the application unique configuration
        GUI items for the current application."""

        grid = Gecko.Script.getAppPreferencesGUI(self)

        # Reapply "say all on load" using the Thunderbird specific setting.
        #
        self.sayAllOnLoadCheckButton.set_active(script_settings.sayAllOnLoad)

        return grid

    def setAppPreferences(self, prefs):
        """Write out the application specific preferences lines and set the
        new values.

        Arguments:
        - prefs: file handle for application preferences.
        """

        Gecko.Script.setAppPreferences(self, prefs)

        # Write the Thunderbird specific settings.
        #
        prefix = "orca.scripts.apps.Thunderbird.script_settings"
        prefs.writelines("import %s\n\n" % prefix)

        value = self.sayAllOnLoadCheckButton.get_active()
        prefs.writelines("%s.sayAllOnLoad = %s\n" % (prefix, value))
        script_settings.sayAllOnLoad = value

    def onFocusedChanged(self, event):
        """Callback for object:state-changed:focused accessibility events."""

        if not event.detail1:
            return

        self._lastAutoComplete = ""

        obj = event.source
        if not self.inDocumentContent(obj):
            default.Script.onFocusedChanged(self, event)
            return

        if self.isEditableMessage(obj):
            self.textArea = obj
            default.Script.onFocusedChanged(self, event)
            return

        role = obj.getRole()
        if role != pyatspi.ROLE_DOCUMENT_FRAME:
            Gecko.Script.onFocusedChanged(self, event)
            return

        contextObj, contextOffset = self.getCaretContext()
        if contextObj:
            return

        orca.setLocusOfFocus(event, obj, notifyScript=False)

    def onBusyChanged(self, event):
        """Callback for object:state-changed:busy accessibility events."""

        obj = event.source
        if obj.getRole() == pyatspi.ROLE_DOCUMENT_FRAME and not event.detail1:
            if self.inDocumentContent():
                self.speakMessage(obj.name)
                self._presentMessage(obj)

    def onShowingChanged(self, event):
        """Callback for object:state-changed:showing accessibility events."""

        # TODO - JD: Once there are separate scripts for the Gecko toolkit
        # and the Firefox browser, this method can be deleted. It's here
        # right now just to prevent the Gecko script from presenting non-
        # existent browsery autocompletes for Thunderbird.

        default.Script.onShowingChanged(self, event)

    def onTextDeleted(self, event):
        """Called whenever text is from an an object.

        Arguments:
        - event: the Event
        """

        obj = event.source
        parent = obj.parent

        try:
            role = event.source.getRole()
            parentRole = parent.getRole()
        except:
            return

        if role == pyatspi.ROLE_LABEL and parentRole == pyatspi.ROLE_STATUS_BAR:
            return

        Gecko.Script.onTextDeleted(self, event)

    def onTextInserted(self, event):
        """Called whenever text is inserted into an object.

        Arguments:
        - event: the Event
        """
        obj = event.source
        parent = obj.parent

        try:
            role = event.source.getRole()
            parentRole = parent.getRole()
        except:
            return

        if role == pyatspi.ROLE_LABEL and parentRole == pyatspi.ROLE_STATUS_BAR:
            return

        # Try to stop unwanted chatter when a new message is being
        # replied to. See bgo#618484.
        #
        if role == pyatspi.ROLE_DOCUMENT_FRAME \
           and event.source.getState().contains(pyatspi.STATE_EDITABLE) \
           and event.type.endswith("system"):
            return

        # Speak the autocompleted text, but only if it is different
        # address so that we're not too "chatty." See bug #533042.
        #
        if parentRole == pyatspi.ROLE_AUTOCOMPLETE:
            if len(event.any_data) == 1:
                default.Script.onTextInserted(self, event)
                return

            # Mozilla cannot seem to get their ":system" suffix right
            # to save their lives, so we'll add yet another sad hack.
            try:
                text = event.source.queryText()
            except:
                hasSelection = False
            else:
                hasSelection = text.getNSelections() > 0

            if (hasSelection or event.type.endswith("system")) and event.any_data:
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

        Gecko.Script.onTextInserted(self, event)

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
        rolesList = [pyatspi.ROLE_DOCUMENT_FRAME,
                     pyatspi.ROLE_INTERNAL_FRAME,
                     pyatspi.ROLE_FRAME,
                     pyatspi.ROLE_APPLICATION]
        if self.utilities.hasMatchingHierarchy(event.source, rolesList):
            lastKey, mods = self.utilities.lastKeyAndModifiers()
            if lastKey == "Delete":
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
        rolesList = [pyatspi.ROLE_LIST_ITEM,
                     pyatspi.ROLE_LIST,
                     pyatspi.ROLE_DIALOG,
                     pyatspi.ROLE_APPLICATION]
        if self.utilities.hasMatchingHierarchy(obj, rolesList):
            dialog = obj.parent.parent

            # Translators: this is what the name of the spell checking 
            # dialog in Thunderbird begins with. The translated form
            # has to match what Thunderbird is using.  We hate keying
            # off stuff like this, but we're forced to do so in this case.
            #
            if dialog.name.startswith(_("Check Spelling")):
                if obj.getIndexInParent() == 0:
                    badWord = self.utilities.displayedText(dialog[1])

                    if self.textArea != None:
                        # If we have a handle to the Thunderbird message text
                        # area, then extract out all the text objects, and
                        # create a list of all the words found in them.
                        #
                        allTokens = []
                        text = self.utilities.substring(self.textArea, 0, -1)
                        tokens = text.split()
                        allTokens += tokens
                        self.speakMisspeltWord(allTokens, badWord)

    def _presentMessage(self, documentFrame):
        """Presents the first line of the message, or the entire message,
        depending on the user's sayAllOnLoad setting."""

        [obj, offset] = self.findFirstCaretContext(documentFrame, 0)
        self.setCaretPosition(obj, offset)
        if not script_settings.sayAllOnLoad:
            self.presentLine(obj, offset)
        elif _settingsManager.getSetting('enableSpeech'):
            self.sayAll(None)

    def sayCharacter(self, obj):
        """Speaks the character at the current caret position."""

        if self.isEditableMessage(obj):
            text = self.utilities.queryNonEmptyText(obj)
            if text and text.caretOffset + 1 >= text.characterCount:
                default.Script.sayCharacter(self, obj)
                return

        Gecko.Script.sayCharacter(self, obj)

    def getBottomOfFile(self):
        """Returns the object and last caret offset at the bottom of the
        document frame. Overridden here to handle editable messages.
        """

        # Pylint thinks that obj is an instance of a list. It most
        # certainly is not. Silly pylint.
        #
        # pylint: disable-msg=E1103
        #
        [obj, offset] = Gecko.Script.getBottomOfFile(self)
        if obj and obj.getState().contains(pyatspi.STATE_EDITABLE):
            offset += 1

        return [obj, offset]

    def toggleFlatReviewMode(self, inputEvent=None):
        """Toggles between flat review mode and focus tracking mode."""

        # If we're leaving flat review dump the cache. See bug 568658.
        #
        if self.flatReviewContext:
            pyatspi.clearCache()

        return default.Script.toggleFlatReviewMode(self, inputEvent)

    def isNonHTMLEntry(self, obj):
        """Checks for ROLE_ENTRY areas that are not part of an HTML
        document.  See bug #607414.

        Returns True is this is something like the Subject: entry
        """
        result = obj and obj.getRole() == pyatspi.ROLE_ENTRY \
            and not self.utilities.ancestorWithRole(
                obj, [pyatspi.ROLE_DOCUMENT_FRAME], [pyatspi.ROLE_FRAME])
        return result

    def isEditableMessage(self, obj):
        """Returns True if this is a editable message."""

        # For now, look specifically to see if this object is the
        # document frame. If it's not, we cannot be sure how complex
        # this message is and should let the Gecko code kick in.
        #
        if obj \
           and obj.getRole() == pyatspi.ROLE_DOCUMENT_FRAME \
           and obj.getState().contains(pyatspi.STATE_EDITABLE):
            return True

        return False

    def useCaretNavigationModel(self, keyboardEvent):
        """Returns True if we should do our own caret navigation."""

        if self.isEditableMessage(orca_state.locusOfFocus) \
           or self.isNonHTMLEntry(orca_state.locusOfFocus):
            return False

        return Gecko.Script.useCaretNavigationModel(self, keyboardEvent)
