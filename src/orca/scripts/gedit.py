# Orca
#
# Copyright 2004-2005 Sun Microsystems Inc.
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

"""Custom script for gedit.  [[[TODO: WDW - HACK because tickling gedit
when it is starting can cause gedit to issue the following message:

     (gedit:31434): GLib-GObject-WARNING **: invalid cast from `SpiAccessible' to `BonoboControlAccessible'

It seems as though whenever this message is issued, gedit will hang when
you try to exit it.  Debugging has shown that the iconfied state in
particular seems to indicate that an object is telling all assistive
technologies to just leave it alone or it will pull the trigger on the
application.]]]
"""

import orca.debug as debug
import orca.atspi as atspi
import orca.braille as braille
import orca.default as default
import orca.orca as orca
import orca.rolenames as rolenames
import orca.speech as speech
import orca.speechgenerator as speechgenerator
import orca.util as util

from orca.orca_i18n import _
from orca.rolenames import getRoleName

########################################################################
#                                                                      #
# The GEdit script class.                                              #
#                                                                      #
########################################################################

class SpeechGenerator(speechgenerator.SpeechGenerator):
    """Overrides _getSpeechForFrame so as to avoid digging into the
    gedit hierarchy and tickling a bug in gedit.
    """

    def _getSpeechForFrame(self, obj, already_focused):
        """Get the speech for a frame.  [[[TODO: WDW - This avoids
        digging into the component hierarchy so as to avoid tickling
        a bug in GEdit (see module comment above).]]]

        Arguments:
        - obj: the frame
        - already_focused: if False, the obj just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getDefaultSpeech(obj, already_focused)

        # This will dig deep into the hierarchy, causing issues with
        # gedit.  So, we won't do this.
        #
        #utterances = self._getSpeechForAlert(obj, already_focused)

        self._debugGenerator("GEditSpeechGenerator._getSpeechForFrame",
                             obj,
                             already_focused,
                             utterances)

        return utterances

class Script(default.Script):

    def __init__(self, app):
        """Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """

        default.Script.__init__(self, app)

        # This will be used to cache a handle to the gedit text area for
        # spell checking purposes.

        self.textArea = None

        # The following variables will be used to try to determine if we've
        # already handled this misspelt word (see readMisspeltWord() for
        # more details.

        self.lastCaretPosition = -1
        self.lastBadWord = ''
        self.lastEventType = ''


    def getSpeechGenerator(self):
        """Returns the speech generator for this script.
        """
        return SpeechGenerator()


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
        orca.setLocusOfFocus(event, event.source, False)
        self.updateBraille(orca.locusOfFocus)

        # Look for the label containing the misspelled word.
        # There will be three labels in the top panel in the Check
        # Spelling dialog. Look for the one that isn't a label to
        # another component.
        #
        allLabels = atspi.findByRole(panel, rolenames.ROLE_LABEL)
        for i in range(0, len(allLabels)):
            if allLabels[i].name.startswith(_("Change to:")) or \
               allLabels[i].name.startswith(_("Misspelled word:")):
                continue
            else:
                badWord = allLabels[i].name
                break

        # Note that we often get two or more of these focus or property-change
        # events each time there is a new misspelt word. We extract the
        # current text caret position and the misspelt word and compare 
        # them against the values saved from the last time this routine 
        # was called. If they are the same then we ignore it.

        if self.textArea != None:
            allText = atspi.findByRole(self.textArea, rolenames.ROLE_TEXT)
            caretPosition = allText[0].text.caretOffset

            debug.println(debug.LEVEL_FINEST, \
                "gedit.readMisspeltWord: type=%s  word=%s caret position=%d" % \
                (event.type, badWord, caretPosition))

            if (caretPosition == self.lastCaretPosition) and \
               (badWord == self.lastBadWord) and \
               (event.type == self.lastEventType):
                return

            # The indication that spell checking is complete is when the
            # "misspelt" word is set to "Completed spell checking". Ugh!
            # Try to detect this and let the user know.

            if badWord == _("Completed spell checking"):
                utterance = _("Spell checking is complete.")
                speech.speak(utterance)
                utterance = _("Press Tab and Return to terminate.")
                speech.speak(utterance)
                return

            # If we have a handle to the gedit text area, then extract out
            # all the text objects, and create a list of all the words found
            # in them.
            #
            allTokens = []
            for i in range(0, len(allText)):
                text = allText[i].text.getText(0, -1)
                tokens = text.split()
                allTokens += tokens

            util.speakMisspeltWord(allTokens, badWord)

            # Save misspelt word information for comparison purposes
            # next time around.
            #
            self.lastCaretPosition = caretPosition
            self.lastBadWord = badWord
            self.lastEventType = event.type


    # This method tries to detect and handle the following cases:
    # 1) Text area (for caching handle for spell checking purposes).
    # 2) Check Spelling Dialog.

    def onFocus(self, event):
        """Called whenever an object gets focus.

        Arguments:
        - event: the Event
        """

        brailleGen = self.brailleGenerator
        speechGen = self.speechGenerator

        debug.printObjectEvent(debug.LEVEL_FINEST,
                               event,
                               event.source.toString())

        # atspi.printAncestry(event.source)

        # 1) Text area (for caching handle for spell checking purposes).
        #
        # This works in conjunction with code in section 2). Check to see if
        # focus is currently in the gedit text area. If it is, then, if this 
        # is the first time, save a pointer to the scroll pane which contains
        # the text being editted.
        #
        # Note that this drops through to then use the default event
        # processing in the parent class for this "focus:" event.

        rolesList = [rolenames.ROLE_TEXT, \
                     rolenames.ROLE_SCROLL_PANE, \
                     rolenames.ROLE_FILLER, \
                     rolenames.ROLE_PAGE_TAB, \
                     rolenames.ROLE_PAGE_TAB_LIST, \
                     rolenames.ROLE_SPLIT_PANE]
        if util.isDesiredFocusedItem(event.source, rolesList):
            debug.println(debug.LEVEL_FINEST,
                      "gedit.onFocus - text area.")

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

        rolesList = [rolenames.ROLE_TEXT, \
                     rolenames.ROLE_FILLER, \
                     rolenames.ROLE_PANEL, \
                     rolenames.ROLE_FILLER, \
                     rolenames.ROLE_FRAME]
        if util.isDesiredFocusedItem(event.source, rolesList):
            frame = event.source.parent.parent.parent.parent
            if frame.name.startswith(_("Check Spelling")):
                debug.println(debug.LEVEL_FINEST,
                      "gedit.onFocus - check spelling dialog.")

                self.readMisspeltWord(event, event.source.parent.parent)
                # Fall-thru to process the event with the default handler.


        # For everything else, pass the focus event onto the parent class
        # to be handled in the default way.

        default.Script.onFocus(self, event)


    # This method tries to detect and handle the following cases:
    # 1) check spelling dialog.

    def onNameChanged(self, event):
        """Called whenever a property on an object changes.

        Arguments:
        - event: the Event
        """

        brailleGen = self.brailleGenerator
        speechGen = self.speechGenerator

        debug.printObjectEvent(debug.LEVEL_FINEST,
                               event,
                               event.source.toString())

        # atspi.printAncestry(event.source)

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

        rolesList = [rolenames.ROLE_LABEL, \
                     rolenames.ROLE_PANEL, \
                     rolenames.ROLE_FILLER, \
                     rolenames.ROLE_FRAME]
        if util.isDesiredFocusedItem(event.source, rolesList):
            frame = event.source.parent.parent.parent
            if frame.name.startswith(_("Check Spelling")):
                debug.println(debug.LEVEL_FINEST,
                      "gedit.onNameChanged - check spelling dialog.")

                self.readMisspeltWord(event, event.source.parent)
                # Fall-thru to process the event with the default handler.

        # Pass the event onto the parent class to be handled in the default way.
        default.Script.onNameChanged(self, event)

