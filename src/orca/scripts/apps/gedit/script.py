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
import orca.scripts.default as default
import orca.orca as orca
import orca.orca_state as orca_state
import orca.settings as settings
import orca.speech as speech
import orca.speechserver as speechserver

from orca.orca_i18n import _

class Script(default.Script):

    def __init__(self, app):
        """Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """

        default.Script.__init__(self, app)

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

    def getListeners(self):
        """Sets up the AT-SPI event listeners for this script.
        """
        listeners = default.Script.getListeners(self)

        listeners["object:state-changed:focused"]           = \
            self.onStateChanged

        return listeners

    def __sayAllProgressCallback(self, context, progressType):
        """Provide feedback during the sayAll operation.
        """

        if progressType == speechserver.SayAllContext.PROGRESS:
            #print "PROGRESS", context.utterance, context.currentOffset
            pass
        elif progressType == speechserver.SayAllContext.INTERRUPTED:
            #print "INTERRUPTED", context.utterance, context.currentOffset
            offset = context.currentOffset
            for i in range(0, len(context.obj)):
                obj = context.obj[i]
                text = obj.queryText()
                charCount = text.characterCount
                if offset > charCount:
                    offset -= charCount
                else:
                    text.setCaretOffset(offset)
                    break
        elif progressType == speechserver.SayAllContext.COMPLETED:
            #print "COMPLETED", context.utterance, context.currentOffset
            obj = context.obj[len(context.obj)-1]
            obj.queryText().setCaretOffset(context.currentOffset)
            orca.setLocusOfFocus(None, obj, notifyScript=False)

    def textLines(self, obj):
        """Creates a generator that can be used to iterate over each line
        of a text object, starting at the caret offset.

        Arguments:
        - obj: an Accessible that has a text specialization

        Returns an iterator that produces elements of the form:
        [SayAllContext, acss], where SayAllContext has the text to be
        spoken and acss is an ACSS instance for speaking the text.
        """

        try:
            text = obj.queryText()
        except:
            return

        length = text.characterCount
        offset = text.caretOffset
        string = ""
        textObjs = []
        textObjs.append(obj)
        startOffset = text.caretOffset

        # Determine the correct "say all by" mode to use.
        #        
        if settings.sayAllStyle == settings.SAYALL_STYLE_SENTENCE:
            mode = pyatspi.TEXT_BOUNDARY_SENTENCE_END
        elif settings.sayAllStyle == settings.SAYALL_STYLE_LINE:
            mode = pyatspi.TEXT_BOUNDARY_LINE_START
        else:
            mode = pyatspi.TEXT_BOUNDARY_LINE_START

        # Get the next line of text to read
        #
        done = False
        while not done:
            while offset < length:
                [mystr, start, end] = text.getTextAtOffset(offset, mode)
                endOffset = end

                if len(mystr) != 0:
                    string += mystr

                if mode == pyatspi.TEXT_BOUNDARY_LINE_START or \
                   len(mystr) == 0 or mystr[len(mystr)-1] in '.?!':
                    string = self.utilities.adjustForRepeats(string)
                    if string.decode("UTF-8").isupper():
                        voice = settings.voices[settings.UPPERCASE_VOICE]
                    else:
                        voice = settings.voices[settings.DEFAULT_VOICE]

                    yield [speechserver.SayAllContext(textObjs, string,
                                                      startOffset, endOffset),
                           voice]
                    string = ""
                    startOffset = endOffset

                if len(mystr) == 0:
                    break
                else:
                    offset = end

            moreLines = False
            relations = obj.getRelationSet()
            for relation in relations:
                if relation.getRelationType()  \
                       == pyatspi.RELATION_FLOWS_TO:
                    obj = relation.getTarget(0)
                    try:
                        text = obj.queryText()
                    except:
                        return
                    textObjs.append(obj)
                    length = text.characterCount
                    offset = 0
                    moreLines = True
                    break
            if not moreLines:
                done = True

        # If there is anything left unspoken, speak it now.
        #
        if len(string) != 0:
            string = self.utilities.adjustForRepeats(string)
            if string.decode("UTF-8").isupper():
                voice = settings.voices[settings.UPPERCASE_VOICE]
            else:
                voice = settings.voices[settings.DEFAULT_VOICE]

            yield [speechserver.SayAllContext(textObjs, string,
                                              startOffset, endOffset),
                   voice]

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

    def isFocusOnFindDialog(self):
        """Return an indication of whether the current locus of focus is on
        the Find button or the combo box in the Find dialog.
        """

        obj = orca_state.locusOfFocus
        if not obj:
            return False

        rolesList1 = [pyatspi.ROLE_PUSH_BUTTON,
                      pyatspi.ROLE_FILLER,
                      pyatspi.ROLE_FILLER,
                      pyatspi.ROLE_DIALOG,
                      pyatspi.ROLE_APPLICATION]

        rolesList2 = [pyatspi.ROLE_TEXT,
                      pyatspi.ROLE_COMBO_BOX,
                      pyatspi.ROLE_PANEL,
                      pyatspi.ROLE_FILLER,
                      pyatspi.ROLE_FILLER,
                      pyatspi.ROLE_DIALOG,
                      pyatspi.ROLE_APPLICATION]

        # Translators: this is used to tell us if the focus is on the
        # "Find" button in gedit's Find dialog.  It must match what
        # gedit is using.  We hate keying off stuff like this, but
        # we're forced to do so in this case.
        #
        tmp = obj.parent.parent
        if (self.utilities.hasMatchingHierarchy(obj, rolesList1) \
            and obj.name == _("Find")) \
            or (self.utilities.hasMatchingHierarchy(obj, rolesList2) \
                and tmp.parent.parent.parent.name == _("Find")):
            return True
        else:
            return False

    # This method tries to detect and handle the following cases:
    # 1) Text area (for caching handle for spell checking purposes).
    # 2) Check Spelling Dialog.

    def locusOfFocusChanged(self, event, oldLocusOfFocus, newLocusOfFocus):
        """Called when the visual object with focus changes.

        Arguments:
        - event: if not None, the Event that caused the change
        - oldLocusOfFocus: Accessible that is the old locus of focus
        - newLocusOfFocus: Accessible that is the new locus of focus
        """

        details = debug.getAccessibleDetails(self.debugLevel, event.source)
        debug.printObjectEvent(self.debugLevel, event, details)

        # self.printAncestry(event.source)

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

        default.Script.locusOfFocusChanged(self, event,
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
            debug.println(self.debugLevel,
                          "gedit.onStateChanged - print preview - page #.")
            parent = event.source.parent
            label1 = self.utilities.displayedText(parent[1])
            label2 = self.utilities.displayedText(parent[2])
            items = [label1, label2]
            self.presentItemsInSpeech(items)
            self.presentItemsInBraille(items)

    # This method tries to detect and handle the following cases:
    # 1) check spelling dialog.
    # 2) find dialog - phrase not found.

    def onNameChanged(self, event):
        """Called whenever a property on an object changes.

        Arguments:
        - event: the Event
        """

        details = debug.getAccessibleDetails(self.debugLevel, event.source)
        debug.printObjectEvent(self.debugLevel, event, details)

        # self.printAncestry(event.source)

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

        # 2) find dialog - phrase not found.
        #
        # If we've received an "object:property-change:accessible-name" for
        # the status bar and the current locus of focus is on the Find
        # button on the Find dialog or the combo box in the Find dialog
        # and the last input event was a Return and the name for the current
        # event source is "Phrase not found", then speak it.
        #
        # [[[TODO: richb - "Phrase not found" is spoken twice because we
        # apparently get two identical "object:property-change:accessible-name"
        # events.]]]

        lastKey, mods = self.utilities.lastKeyAndModifiers()

        # Translators: the "Phrase not found" is the result of a failed
        # find command.  It must be the same as what gedit uses.  We hate
        # keying off stuff like this, but we're forced to do so in this
        # case.
        #
        if event.source.getRole() == pyatspi.ROLE_STATUS_BAR \
           and self.isFocusOnFindDialog() \
           and lastKey == "Return" \
           and event.source.name == _("Phrase not found"):
            debug.println(self.debugLevel,
                          "gedit.onNameChanged - phrase not found.")
            speech.speak(event.source.name)

        # Pass the event onto the parent class to be handled in the default way.
        default.Script.onNameChanged(self, event)

    def onStateChanged(self, event):
        """Called whenever an object's state changes.

        Arguments:
        - event: the Event
        """

        # Sometimes an object will tell us it is focused this
        # way versus issuing a focus event.  GEdit's edit area,
        # for example, will do this: when you use metacity's
        # window menu to do things like maximize or unmaximize
        # a window, you will only get a state-changed event
        # from the text area when it regains focus.
        # (See bug #350854 for more details).
        #
        if event.type.startswith("object:state-changed:focused") \
           and (event.detail1):
            orca.setLocusOfFocus(event, event.source)

        default.Script.onStateChanged(self, event)

    # This method tries to detect and handle the following cases:
    # 1) find dialog - phrase found.

    def onCaretMoved(self, event):
        """Called whenever the caret moves.

        Arguments:
        - event: the Event
        """

        details = debug.getAccessibleDetails(self.debugLevel, event.source)
        debug.printObjectEvent(self.debugLevel, event, details)

        # self.printAncestry(event.source)

        # If we've received a text caret moved event and the current locus
        # of focus is on the Find button on the Find dialog or the combo
        # box in the Find dialog and the last input event was a Return,
        # and if the current line contains the phrase we were looking for,
        # then speak the current text line, to give an indication of what
        # we've just found.
        #
        lastKey, mods = self.utilities.lastKeyAndModifiers()
        if self.isFocusOnFindDialog() and lastKey == "Return":
            debug.println(self.debugLevel, "gedit.onCaretMoved - find dialog.")
            allComboBoxes = self.utilities.descendantsWithRole(
                orca_state.locusOfFocus.getApplication(),
                pyatspi.ROLE_COMBO_BOX)
            phrase = self.utilities.displayedText(allComboBoxes[0])
            [text, caretOffset, startOffset] = \
                self.getTextLineAtCaret(event.source)
            if text.lower().find(phrase) != -1:
                # Translators: this indicates a find command succeeded in
                # finding something.
                #
                self.presentMessage(_("Phrase found."))
                utterances = self.speechGenerator.generateSpeech(
                    event.source, alreadyFocused=True)
                speech.speak(utterances)

        # If Ctrl+G was used to repeat a find command, speak the line that
        # the caret moved to.
        #
        if lastKey == 'G' and mods & settings.CTRL_MODIFIER_MASK:
            self.sayLine(event.source)

        # For everything else, pass the caret moved event onto the parent
        # class to be handled in the default way.

        default.Script.onCaretMoved(self, event)
