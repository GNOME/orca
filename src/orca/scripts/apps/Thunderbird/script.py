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

    _containingPanelName = ""

    def __init__(self, app):
        """ Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """

        # Set the debug level for all the methods in this script.
        self.debugLevel = debug.LEVEL_FINEST

        # http://bugzilla.mozilla.org/show_bug.cgi?id=659018
        if app.toolkitVersion < "7.0":
            app.setCacheMask(pyatspi.cache.ALL ^ pyatspi.cache.NAME)

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

        # We need to maintain a separate setting for grabFocusOnAncestor
        # because the version of Gecko used by the Thunderbird might be
        # different from that used by Firefox. See bug 608149.
        #
        self.grabFocusOnAncestorCheckButton.set_active(
            script_settings.grabFocusOnAncestor)

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

        value = self.grabFocusOnAncestorCheckButton.get_active()
        prefs.writelines("%s.grabFocusOnAncestor = %s\n" % (prefix, value))
        script_settings.grabFocusOnAncestor = value

    def _debug(self, msg):
        """ Convenience method for printing debug messages"""

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
        if self.utilities.hasMatchingHierarchy(event.source, rolesList):
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

    def onCaretMoved(self, event):
        """Called whenever the caret moves.

        Arguments:
        - event: the Event
        """

        # Much of the Gecko code is designed to handle Gecko's broken
        # caret navigation. This is not needed in -- and can sometimes
        # interfere with our presentation of -- a simple message being
        # composed by the user. Surely we can count on Thunderbird to
        # handle navigation in that case.
        #
        if self.isEditableMessage(event.source) \
           or self.isNonHTMLEntry(event.source):
            self.setCaretContext(event.source, event.detail1)
            return default.Script.onCaretMoved(self, event)

        # Page_Up/Page_Down are not used by Orca. However, users report
        # using these keys in Thunderbird without success. The default
        # script is sometimes rejecting the resulting caret-moved events
        # based on the locusOfFocus other times Gecko is because of the
        # caret context.
        #
        lastKey, mods = self.utilities.lastKeyAndModifiers()
        updatePosition = lastKey in ["Page_Up", "Page_Down"]

        # Unlike the unpredictable wild, wild web, odds are good that a
        # caret-moved event in a message composition window is valid. But
        # depending upon the locusOfFocus at the time this event is issued
        # the default Gecko toolkit script might not do the right thing.
        #
        if not updatePosition and event.detail1 >= 0:
            updatePosition = \
                event.source.getState().contains(pyatspi.STATE_EDITABLE)

        if updatePosition:
            orca.setLocusOfFocus(event, event.source, notifyScript=False)
            self.setCaretContext(event.source, event.detail1)

            # The Gecko script, should it be about to pass along this
            # event to the default script, will set the locusOfFocus to
            # the object returned by findFirstCaretContext(). If that
            # object is not the same as the event source or the event
            # source's parent, the default script will reject the event.
            # As a result, if the user presses Page_Up or Page_Down and
            # just so happens to land on an object whose sole contents
            # is an image, we'll say nothing. Ultimately this should
            # probably be handled elsewhere, but this close to the next
            # major (2.24) release, I (JD) am not risking it. :-)
            #
            [obj, offset] = \
                self.findFirstCaretContext(event.source, event.detail1)
            if obj.getRole() == pyatspi.ROLE_IMAGE:
                return default.Script.onCaretMoved(self, event)

        return Gecko.Script.onCaretMoved(self, event)

    def onFocus(self, event):
        """ Called whenever an object gets focus.

        Arguments:
        - event: the Event

        """
        obj = event.source
        parent = obj.parent
        top = self.utilities.topLevelObject(obj)
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
        # (e.g., Date). Braille should show the row beginning with
        # the first populated cell. Set the locusOfFocus to that
        # cell and consume the event so that the Gecko script
        # doesn't reset it.
        #
        if obj.getRole() == pyatspi.ROLE_TABLE_CELL \
           and parent.getRole() != pyatspi.ROLE_LIST_ITEM:
            table = parent.queryTable()
            row = table.getRowAtIndex(self.utilities.cellIndex(obj))
            for i in range(0, table.nColumns):
                acc = table.getAccessibleAt(row, i)
                if acc.name:
                    # For some reason orca.py's check to see if the
                    # object we're setting the locusOfFocus to is the
                    # same as the current locusOfFocus is returning
                    # True when it's not actually True. Therefore,
                    # we'll force the propagation as a precaution.
                    #
                    force = event.type.startswith("focus:")
                    orca.setLocusOfFocus(event, acc, force=force)
                    consume = True
                    break

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
        if self.utilities.hasMatchingHierarchy(event.source, rolesList):
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
            if self.utilities.hasMatchingHierarchy(obj, rolesList):
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
           and orca_state.locusOfFocus \
           and orca_state.locusOfFocus.getRole() == pyatspi.ROLE_FRAME:
            if self._messageLoaded:
                consume = True
                self._presentMessage(event.source)

            # If the user just gave focus to the message window (e.g. by
            # Alt+Tabbing back into it), we might have an existing caret
            # context. But we'll need the document frame in order to verify
            # this. Therefore try to find the document frame.
            #
            elif self.getCaretContext() == [None, -1]:
                documentFrame = None
                for child in orca_state.locusOfFocus:
                    if child.getRole() == pyatspi.ROLE_INTERNAL_FRAME \
                       and child.childCount \
                       and child[0].getRole() == pyatspi.ROLE_DOCUMENT_FRAME:
                        documentFrame = child[0]
                        break
                try:
                    contextObj, contextOffset = \
                        self._documentFrameCaretContext[hash(documentFrame)]
                    if contextObj:
                        orca.setLocusOfFocus(event, contextObj)
                except:
                    pass

        if not consume:
            # Much of the Gecko code is designed to handle Gecko's broken
            # caret navigation. This is not needed in -- and can sometimes
            # interfere with our presentation of -- a simple message being
            # composed by the user. Surely we can count on Thunderbird to
            # handle navigation in that case.
            #
            if self.isEditableMessage(event.source):
                default.Script.onFocus(self, event)
            else:
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
        rolesList = [pyatspi.ROLE_TABLE_CELL,
                     pyatspi.ROLE_TREE_TABLE,
                     pyatspi.ROLE_SCROLL_PANE,
                     pyatspi.ROLE_SCROLL_PANE]
        if self.utilities.hasMatchingHierarchy(event.source, rolesList):
            lastKey, mods = self.utilities.lastKeyAndModifiers()
            if lastKey == "Delete":
                oldLocusOfFocus = None

        # If the user has just deleted an open mail message, then we want to
        # try to speak the new name of the open mail message frame.
        # See bug #540039 for more details.
        #
        rolesList = [pyatspi.ROLE_DOCUMENT_FRAME, \
                     pyatspi.ROLE_INTERNAL_FRAME, \
                     pyatspi.ROLE_FRAME, \
                     pyatspi.ROLE_APPLICATION]
        if self.utilities.hasMatchingHierarchy(event.source, rolesList):
            lastKey, mods = self.utilities.lastKeyAndModifiers()
            if lastKey == "Delete":
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

        # Try to stop unwanted chatter when a new message is being
        # replied to. See bgo#618484.
        #
        if event.source.getRole() == pyatspi.ROLE_DOCUMENT_FRAME \
           and event.source.getState().contains(pyatspi.STATE_EDITABLE) \
           and event.type.endswith("system"):
            return

        # Speak the autocompleted text, but only if it is different
        # address so that we're not too "chatty." See bug #533042.
        #
        if parent.getRole() == pyatspi.ROLE_AUTOCOMPLETE:
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
                speech.speak(utterances)
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
                    speech.speak(utterances)

    def _presentMessage(self, documentFrame):
        """Presents the first line of the message, or the entire message,
        depending on the user's sayAllOnLoad setting."""

        [obj, offset] = self.findFirstCaretContext(documentFrame, 0)
        self.setCaretPosition(obj, offset)
        if not script_settings.sayAllOnLoad:
            self.presentLine(obj, offset)
        elif _settingsManager.getSetting('enableSpeech'):
            self.sayAll(None)
        self._messageLoaded = False

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
