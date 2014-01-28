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

"""Custom script for gedit."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi

import orca.debug as debug
import orca.orca_state as orca_state
import orca.scripts.toolkits.gtk as gtk

from orca.orca_i18n import _

class Script(gtk.Script):

    def __init__(self, app):
        """Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """

        gtk.Script.__init__(self, app)

        # Set the debug level for all the methods in this script.
        #
        self.debugLevel = debug.LEVEL_FINEST

        # This will be used to cache a handle to the gedit text area for
        # spell checking purposes.

        self.textArea = None

        # The following variables will be used to try to determine if we've
        # already handled this misspelt word (see readMisspeltWord() for
        # more details.

        self.lastCaretPosition = -1
        self.lastBadWord = ''
        self.lastEventType = ''

    def readMisspeltWord(self, event, panel):
        """Speak/braille the current misspelt word plus its context.
           The spell check dialog contains a "paragraph" which shows the
           context for the current spelling mistake. After speaking/brailling
           the default action for this component, that a selection of the
           surronding text from that paragraph with the misspelt word is also
           spoken.

        Arguments:
        - event: the event.
        - panel: the panel in the check spelling dialog containing the label
                 with the misspelt word.
        """

        # Braille the default action for this component.
        #
        self.updateBraille(orca_state.locusOfFocus)

        # Look for the label containing the misspelled word.
        # There will be three labels in the top panel in the Check
        # Spelling dialog. Look for the one that isn't a label to
        # another component.
        #
        allLabels = self.utilities.descendantsWithRole(
            panel, pyatspi.ROLE_LABEL)
        for label in allLabels:
            # Translators: these are labels from the gedit spell checking
            # dialog and must be the same strings gedit uses.  We hate
            # keying off stuff like this, but we're forced to do so in
            # in this case.
            #
            if label.name.startswith(_("Change to:")) or \
               label.name.startswith(_("Misspelled word:")):
                continue
            else:
                badWord = label.name
                break

        # Note that we often get two or more of these focus or property-change
        # events each time there is a new misspelt word. We extract the
        # current text caret position and the misspelt word and compare
        # them against the values saved from the last time this routine
        # was called. If they are the same then we ignore it.

        if self.textArea != None:
            allText = self.utilities.descendantsWithRole(
                self.textArea, pyatspi.ROLE_TEXT)
            caretPosition = allText[0].queryText().caretOffset

            debug.println(self.debugLevel, \
                "gedit.readMisspeltWord: type=%s  word=%s caret position=%d" \
                % (event.type, badWord, caretPosition))

            if (caretPosition == self.lastCaretPosition) and \
               (badWord == self.lastBadWord) and \
               (event.type == self.lastEventType):
                return

            # The indication that spell checking is complete is when the
            # "misspelt" word is set to "Completed spell checking". Ugh!
            # Try to detect this and let the user know.
            #
            # Translators: this string must be the same that is used by
            # gedit.  We hate keying off stuff like this, but we're
            # forced to do so in this case.
            #
            if badWord == _("Completed spell checking"):
                utterance = _("Spell checking is complete.")
                self.presentMessage(utterance)
                utterance = _("Press Tab and Return to terminate.")
                self.presentMessage(utterance)
                return

            # If we have a handle to the gedit text area, then extract out
            # all the text objects, and create a list of all the words found
            # in them.
            #
            allTokens = []
            for i in range(0, len(allText)):
                text = self.utilities.substring(allText[i], 0, -1)
                tokens = text.split()
                allTokens += tokens

            self.speakMisspeltWord(allTokens, badWord)

            # Save misspelt word information for comparison purposes
            # next time around.
            #
            self.lastCaretPosition = caretPosition
            self.lastBadWord = badWord
            self.lastEventType = event.type

    def locusOfFocusChanged(self, event, oldLocusOfFocus, newLocusOfFocus):
        """Called when the visual object with focus changes.

        Arguments:
        - event: if not None, the Event that caused the change
        - oldLocusOfFocus: Accessible that is the old locus of focus
        - newLocusOfFocus: Accessible that is the new locus of focus
        """

        details = debug.getAccessibleDetails(self.debugLevel, event.source)
        debug.printObjectEvent(self.debugLevel, event, details)

        # 1) Text area (for caching handle for spell checking purposes).
        #
        # This works in conjunction with code in section 2). Check to see if
        # focus is currently in the gedit text area. If it is, then, if this
        # is the first time, save a pointer to the scroll pane which contains
        # the text being editted.
        #
        # Note that this drops through to then use the default event
        # processing in the parent class for this "focus:" event.

        rolesList = [pyatspi.ROLE_TEXT,
                     pyatspi.ROLE_SCROLL_PANE,
                     pyatspi.ROLE_FILLER,
                     pyatspi.ROLE_PAGE_TAB,
                     pyatspi.ROLE_PAGE_TAB_LIST,
                     pyatspi.ROLE_SPLIT_PANE]
        if self.utilities.hasMatchingHierarchy(event.source, rolesList):
            debug.println(self.debugLevel,
                          "gedit.locusOfFocusChanged - text area.")

            self.textArea = event.source.parent
            # Fall-thru to process the event with the default handler.

        # 2) check spelling dialog.
        #
        # Check to see if the Spell Check dialog has just appeared and got
        # focus. If it has, then speak/braille the current misspelt word
        # plus its context.
        #
        # Note that in order to make sure that this focus event is for the
        # check spelling dialog, a check is made of the localized name of the
        # option pane. Translators for other locales will need to ensure that
        # their translation of this string matches what gedit uses in
        # that locale.

        rolesList = [pyatspi.ROLE_TEXT,
                     pyatspi.ROLE_FILLER,
                     pyatspi.ROLE_PANEL,
                     pyatspi.ROLE_FILLER,
                     pyatspi.ROLE_FRAME]
        if self.utilities.hasMatchingHierarchy(event.source, rolesList):
            tmp = event.source.parent.parent
            frame = tmp.parent.parent
            # Translators: this is the name of the "Check Spelling" window
            # in gedit and must be the same as what gedit uses.  We hate
            # keying off stuff like this, but we're forced to do so in this
            # case.
            #
            if frame.name.startswith(_("Check Spelling")):
                debug.println(self.debugLevel,
                        "gedit.locusOfFocusChanged - check spelling dialog.")

                self.readMisspeltWord(event, event.source.parent.parent)
                # Fall-thru to process the event with the default handler.

        # For everything else, pass the focus event onto the parent class
        # to be handled in the default way.

        gtk.Script.locusOfFocusChanged(self, event,
                                           oldLocusOfFocus, newLocusOfFocus)

        # If we are doing a Print Preview and we are focused on the
        # page number text area, also speak the "of n" labels to the
        # right of this area. See bug #133275 for more details.
        #
        rolesList = [pyatspi.ROLE_TEXT,
                     pyatspi.ROLE_FILLER,
                     pyatspi.ROLE_PANEL,
                     pyatspi.ROLE_TOOL_BAR,
                     pyatspi.ROLE_FILLER,
                     pyatspi.ROLE_FILLER,
                     pyatspi.ROLE_PAGE_TAB,
                     pyatspi.ROLE_PAGE_TAB_LIST]
        if self.utilities.hasMatchingHierarchy(event.source, rolesList):
            parent = event.source.parent
            label1 = self.utilities.displayedText(parent[1])
            label2 = self.utilities.displayedText(parent[2])
            items = [label1, label2]
            self.presentItemsInSpeech(items)
            self.presentItemsInBraille(items)

    # This method tries to detect and handle the following cases:
    # 1) check spelling dialog.

    def onNameChanged(self, event):
        """Called whenever a property on an object changes.

        Arguments:
        - event: the Event
        """

        details = debug.getAccessibleDetails(self.debugLevel, event.source)
        debug.printObjectEvent(self.debugLevel, event, details)

        # 1) check spelling dialog.
        #
        # Check to see if if we've had a property-change event for the
        # accessible name for the label containing the current misspelt
        # word in the check spelling dialog.
        # This (hopefully) means that the user has just corrected a
        # spelling mistake, in which case, speak/braille the current
        # misspelt word plus its context.
        #
        # Note that in order to make sure that this event is for the
        # check spelling dialog, a check is made of the localized name of the
        # frame. Translators for other locales will need to ensure that
        # their translation of this string matches what gedit uses in
        # that locale.

        rolesList = [pyatspi.ROLE_LABEL,
                     pyatspi.ROLE_PANEL,
                     pyatspi.ROLE_FILLER,
                     pyatspi.ROLE_FRAME]
        if self.utilities.hasMatchingHierarchy(event.source, rolesList):
            frame = event.source.parent.parent.parent
            # Translators: this is the name of the "Check Spelling" window
            # in gedit and must be the same as what gedit uses.  We hate
            # keying off stuff like this, but we're forced to do so in this
            # case.
            #
            if frame.name.startswith(_("Check Spelling")):
                debug.println(self.debugLevel,
                      "gedit.onNameChanged - check spelling dialog.")

                self.readMisspeltWord(event, event.source.parent)
                # Fall-thru to process the event with the default handler.

        gtk.Script.onNameChanged(self, event)

    def onTextSelectionChanged(self, event):
        """Callback for object:text-selection-changed accessibility events."""

        if event.source == orca_state.locusOfFocus:
            gtk.Script.onTextSelectionChanged(self, event)
            return

        if not self.utilities.isSearchEntry(orca_state.locusOfFocus, True):
            return

        # To avoid extreme chattiness.
        keyString, mods = self.utilities.lastKeyAndModifiers()
        if keyString in ["BackSpace", "Delete"]:
            return

        self.sayLine(event.source)
