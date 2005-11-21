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

"""The Default Script for presenting information to the user using
both speech and Braille.

This module also provides a number of presenter functions that display
Accessible object information to the user based upon the object's role."""

import atspi
import braille
import braillegenerator
import debug
import flat_review
import input_event
import keybindings
#import mag - [[[TODO: WDW - disable until I can figure out how to
#             resolve the GNOME reference in mag.py.]]]
import orca
import rolenames
import script
import settings
import speech
import speechgenerator

from orca_i18n import _                          # for gettext support

########################################################################
#                                                                      #
# The Default script class.                                            #
#                                                                      #
########################################################################

class Script(script.Script):

    def __init__(self, app):
        """Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """

        script.Script.__init__(self, app)

        self.flatReviewContext = None

        ################################################################
        #                                                              #
        # Keyboard bindings                                            #
        #                                                              #
        ################################################################
        #self.keybindings.add(
        #    keybindings.KeyBinding(
        #        "F9", \
        #        1 << orca.MODIFIER_ORCA, \
        #        1 << orca.MODIFIER_ORCA,
        #        input_eventInputEventHandler(\
        #            Script.sayAgain,
        #            _("Repeats last utterance sent to speech."))))

        self.keybindings.add(
            keybindings.KeyBinding(
                "KP_Divide", \
                0, \
                0, \
                input_event.InputEventHandler(\
                    Script.leftClickReviewItem,
                    _("Performs left click on current flat review item."))))

        self.keybindings.add(
            keybindings.KeyBinding(
                "KP_Multiply", \
                0, \
                0, \
                input_event.InputEventHandler(\
                    Script.rightClickReviewItem,
                    _("Performs right click on current flat review item."))))

        #self.keybindings.add(
        #    keybindings.KeyBinding(
        #        "KP_Add", \
        #        0, \
        #        0, \
        #        input_event.InputEventHandler(\
        #            Script.sayAll,
        #            _("Speaks entire document."))))

        self.keybindings.add(
            keybindings.KeyBinding(
                "KP_Enter", \
                0, \
                0, \
                input_event.InputEventHandler(\
                    Script.whereAmI,
                    _("Performs the where am I operation."))))

        self.keybindings.add(
            keybindings.KeyBinding(
                "Num_Lock", \
                1 << orca.MODIFIER_ORCA, \
                1 << orca.MODIFIER_ORCA, \
                input_event.InputEventHandler(\
                    Script.showZones,
                    _("Paints and prints the visible zones in the active window."))))

        self.keybindings.add(
            keybindings.KeyBinding(
                "KP_Subtract", \
                0, \
                0, \
                input_event.InputEventHandler(\
                    Script.toggleFlatReviewMode,
                    _("Enters and exits flat review mode."))))

        reviewPreviousLineHandler = \
            input_event.InputEventHandler(\
                Script.reviewPreviousLine,
                _("Moves flat review to the beginning of the previous line."))

        self.keybindings.add(
            keybindings.KeyBinding(
                "KP_7", \
                1 << orca.MODIFIER_ORCA, \
                0, \
                reviewPreviousLineHandler))

        reviewHomeHandler = input_event.InputEventHandler(\
            Script.reviewHome,
            _("Moves flat review to the home position."))

        self.keybindings.add(
            keybindings.KeyBinding(
                "KP_7", \
                1 << orca.MODIFIER_ORCA, \
                1 << orca.MODIFIER_ORCA, \
                reviewHomeHandler))

        self.keybindings.add(
            keybindings.KeyBinding(
                "KP_8", \
                0, \
                0, \
                input_event.InputEventHandler(\
                    Script.reviewCurrentLine,
                    _("Speaks the current flat review line."))))

        reviewNextLineHandler = \
            input_event.InputEventHandler(\
                Script.reviewNextLine,
                _("Moves flat review to the beginning of the next line."))

        self.keybindings.add(
            keybindings.KeyBinding(
                "KP_9", \
                1 << orca.MODIFIER_ORCA, \
                0, \
                reviewNextLineHandler))

        self.keybindings.add(
            keybindings.KeyBinding(
                "KP_9", \
                1 << orca.MODIFIER_ORCA, \
                1 << orca.MODIFIER_ORCA, \
                input_event.InputEventHandler(\
                    Script.reviewEnd,
                    _("Moves flat review to the end position."))))

        self.keybindings.add(
            keybindings.KeyBinding(
                "KP_4", \
                1 << orca.MODIFIER_ORCA, \
                0, \
                input_event.InputEventHandler(\
                    Script.reviewPreviousItem,
                    _("Moves flat review to the previous item or word."))))

        reviewAboveHandler = \
            input_event.InputEventHandler(\
                Script.reviewAbove,
                _("Moves flat review to the word above the current word."))

        self.keybindings.add(
            keybindings.KeyBinding(
                "KP_4", \
                1 << orca.MODIFIER_ORCA, \
                1 << orca.MODIFIER_ORCA, \
                reviewAboveHandler))

        self.keybindings.add(
            keybindings.KeyBinding(
                "KP_5", \
                1 << orca.MODIFIER_ORCA, \
                0, \
                input_event.InputEventHandler(\
                    Script.reviewCurrentItem,
                    _("Speaks the current flat review item or word."))))

        self.keybindings.add(
            keybindings.KeyBinding(
                "KP_5", \
                1 << orca.MODIFIER_ORCA, \
                1 << orca.MODIFIER_ORCA, \
                input_event.InputEventHandler(\
                    Script.reviewCurrentAccessible,
                    _("Speaks the current flat review object."))))

        self.keybindings.add(
            keybindings.KeyBinding(
                "KP_6", \
                1 << orca.MODIFIER_ORCA, \
                0, \
                input_event.InputEventHandler(\
                    Script.reviewNextItem,
                    _("Moves flat review to the next item or word."))))

        reviewBelowHandler = \
            input_event.InputEventHandler(\
                Script.reviewBelow,
                _("Moves flat review to the word below the current word."))

        self.keybindings.add(
            keybindings.KeyBinding(
                "KP_6", \
                1 << orca.MODIFIER_ORCA, \
                1 << orca.MODIFIER_ORCA, \
                reviewBelowHandler))

        reviewPreviousCharacterHandler = \
            input_event.InputEventHandler( \
                Script.reviewPreviousCharacter,
                _("Moves flat review to the previous character."))

        self.keybindings.add(
            keybindings.KeyBinding(
                "KP_1", \
                1 << orca.MODIFIER_ORCA, \
                0, \
                reviewPreviousCharacterHandler))

        self.keybindings.add(
            keybindings.KeyBinding(
                "KP_1", \
                1 << orca.MODIFIER_ORCA, \
                1 << orca.MODIFIER_ORCA, \
                input_event.InputEventHandler(\
                    Script.reviewEndOfLine,
                    _("Moves flat review to the end of the line."))))

        self.keybindings.add(
            keybindings.KeyBinding(
                "KP_2", \
                0, \
                0, \
                input_event.InputEventHandler(\
                    Script.reviewCurrentCharacter,
                    _("Speaks the current flat review character."))))

        reviewNextCharacterHandler = \
            input_event.InputEventHandler(\
            Script.reviewNextCharacter,
            _("Moves flat review to the next character."))

        self.keybindings.add(
            keybindings.KeyBinding(
                "KP_3", \
                0, \
                0, \
                reviewNextCharacterHandler))

        ################################################################
        #                                                              #
        # Braille bindings                                             #
        #                                                              #
        ################################################################
        self.braillebindings[braille.CMD_FWINLT] = \
            input_event.InputEventHandler(
                Script.panBrailleLeft,
                _("Pans the braille display to the left."))

        self.braillebindings[braille.CMD_FWINRT] = \
            input_event.InputEventHandler(
                Script.panBrailleRight,
                _("Pans the braille display to the right."))

        #self.braillebindings[braille.CMD_CHRLT] = \
        #    input_event.InputEventHandler(
        #        Script.panBrailleLeftOneChar,
        #        _("Pans the braille display to the left by one character."))

        #self.braillebindings[braille.CMD_CHRRT] = \
        #    input_event.InputEventHandler(
        #        Script.panBrailleRightOneChar,
        #        _("Pans the braille display to the right by one character."))

        self.braillebindings[braille.CMD_LNUP] = reviewAboveHandler
        self.braillebindings[braille.CMD_LNDN] = reviewBelowHandler

        self.braillebindings[braille.CMD_TOP_LEFT] = reviewHomeHandler
        self.braillebindings[braille.CMD_BOT_LEFT] = \
            input_event.InputEventHandler(
                Script.reviewBottomLeft,
                _("Moves flat review to the bottom left."))

        self.braillebindings[braille.CMD_HOME] = \
            input_event.InputEventHandler(
                Script.goBrailleHome,
                _("Returns to object with keyboard focus."))

        ################################################################
        #                                                              #
        # AT-SPI object event handlers                                 #
        #                                                              #
        ################################################################
        self.listeners["focus:"]                                 = \
            self.onFocus

        #self.listeners["keyboard:modifiers"]                     = \
        #    self.noOp

        self.listeners["object:property-change:accessible-name"] = \
            self.onNameChanged

        self.listeners["object:text-caret-moved"]                = \
            self.onCaretMoved
        self.listeners["object:text-changed:delete"]             = \
            self.onTextDeleted
        self.listeners["object:text-changed:insert"]             = \
            self.onTextInserted
        self.listeners["object:text-selection-changed"]          = \
            self.noOp

        self.listeners["object:active-descendant-changed"]       = \
            self.onActiveDescendantChanged
        self.listeners["object:children-changed:"]               = \
            self.noOp
        self.listeners["object:link-selected"]                   = \
            self.onLinkSelected
        self.listeners["object:state-changed:"]                  = \
            self.onStateChanged
        self.listeners["object:selection-changed"]               = \
            self.onSelectionChanged
        self.listeners["object:property-change:accessible-value"] = \
            self.onValueChanged
        self.listeners["object:property-change"] = \
            self.noOp

        self.listeners["object:value-changed:"]                  = \
            self.onValueChanged
        self.listeners["object:visible-changed"]                 = \
            self.noOp

        self.listeners["window:activate"]                        = \
            self.onWindowActivated
        self.listeners["window:create"]                          = \
            self.noOp
        self.listeners["window:deactivate"]                      = \
            self.onWindowDeactivated
        self.listeners["window:destroy"]                         = \
            self.noOp
        self.listeners["window:maximize"]                        = \
            self.noOp
        self.listeners["window:minimize"]                        = \
            self.noOp
        self.listeners["window:rename"]                          = \
            self.noOp
        self.listeners["window:restore"]                         = \
            self.noOp
        self.listeners["window:switch"]                          = \
            self.noOp
        self.listeners["window:titlelize"]                       = \
            self.noOp

        self.brailleGenerator = self.getBrailleGenerator()
        self.speechGenerator = self.getSpeechGenerator()
        self.voices = settings.getSetting(settings.VOICES, None)

    def processObjectEvent(self, event):
        """Processes all object events of interest to this script.  Note
        that this script may be passed events it doesn't care about, so
        it needs to react accordingly.

        Arguments:
        - event: the Event
        """

        # [[[TODO: WDW - HACK to set Orca's locusOfFocus if we've somehow
        # gotten out of whack.  This typically happens when going into an
        # application and we only get a window activated event for it, even
        # if one of its children has focus.  Since we're doing this, we'll
        # tell Orca to not propagate this event to us.]]]
        #
        # [[[TODO: WDW - additional info - this really isn't necessary because
        # we typically only run into this problem when Orca is started after
        # the desktop applications are running.  In real life, this will
        # most likely not be the case, and a simple "make the world right"
        # user action can be to just Alt+Tab to force the apps to give us
        # the events we care about.]]]
        #
        #if (event.type.find("focus") == -1) \
        #   and (event.type.find("state-changed:selected") == -1) \
        #   and (event.type.find("object:selection-changed") == -1) \
        #   and (event.type.find("active-descendant") == -1) \
        #   and event.source.state.count(atspi.Accessibility.STATE_FOCUSED):
        #    orca.setLocusOfFocus(event, event.source, False)

        script.Script.processObjectEvent(self, event)

    def getBrailleGenerator(self):
        """Returns the braille generator for this script.
        """

        return braillegenerator.BrailleGenerator()

    def getSpeechGenerator(self):
        """Returns the speech generator for this script.
        """

        return speechgenerator.SpeechGenerator()

    def whereAmI(self, inputEvent):
        self.updateBraille(orca.locusOfFocus)

        verbosity = settings.getSetting(settings.SPEECH_VERBOSITY_LEVEL,
                                        settings.VERBOSITY_LEVEL_VERBOSE)

        utterances = []

        utterances.extend(
            self.speechGenerator.getSpeechContext(orca.locusOfFocus))

        # Now, we'll treat table row and column headers as context
        # as well.  This requires special handling because we're
        # making headers seem hierarchical in the context, but they
        # are not hierarchical in the containment hierarchicy.
        # We also only want to speak the one that changed.  If both
        # changed, first speak the row header, then the column header.
        #
        # We also keep track of tree level depth and only announce
        # that if it changes.
        #
        if orca.locusOfFocus.role == rolenames.ROLE_TABLE_CELL:
            parent = orca.locusOfFocus.parent
            if parent and parent.table:
                table = parent.table
                row = table.getRowAtIndex(orca.locusOfFocus.index)
                col = table.getColumnAtIndex(orca.locusOfFocus.index)

                desc = parent.table.getRowDescription(row)
                if desc and len(desc):
                    text = desc
                    if verbosity == settings.VERBOSITY_LEVEL_VERBOSE:
                        text += " " \
                                + rolenames.rolenames[\
                                        rolenames.ROLE_ROW_HEADER].speech
                        utterances.append(text)

                desc = parent.table.getColumnDescription(col)
                if desc and len(desc):
                    text = desc
                    if verbosity == settings.VERBOSITY_LEVEL_VERBOSE:
                        text += " " \
                                + rolenames.rolenames[\
                                        rolenames.ROLE_COLUMN_HEADER].speech
                        utterances.append(text)

        # Get the text for the object itself.
        #
        utterances.extend(
            self.speechGenerator.getSpeech(orca.locusOfFocus, False))

        # Now speak the tree node level.
        #
        level = atspi.getNodeLevel(orca.locusOfFocus)
        if level >= 0:
            utterances.append(_("tree level %d") % (level + 1))

        if orca.locusOfFocus.state.count(\
                    atspi.Accessibility.STATE_SENSITIVE) == 0:
            message = _("No focus")
            utterances.extend(message)

        speech.speakUtterances(utterances)

        return True

    def findCommonAncestor(self, a, b):
        """Finds the common ancestor between Accessible a and Accessible b.

        Arguments:
        - a: Accessible
        - b: Accessible
        """

        debug.println(debug.LEVEL_FINEST,
                      "default.findCommonAncestor...")

        if (not a) or (not b):
            return None

        if a == b:
            return a

        aParents = [a]
        try:
            parent = a.parent
            while parent and (parent.parent != parent):
                aParents.append(parent)
                parent = parent.parent
            aParents.reverse()
        except:
            debug.printException(debug.LEVEL_FINEST)
            pass

        bParents = [b]
        try:
            parent = b.parent
            while parent and (parent.parent != parent):
                bParents.append(parent)
                parent = parent.parent
            bParents.reverse()
        except:
            debug.printException(debug.LEVEL_FINEST)
            pass

        commonAncestor = None

        maxSearch = min(len(aParents), len(bParents))
        i = 0
        while i < maxSearch:
            if aParents[i] == bParents[i]:
                commonAncestor = aParents[i]
                i += 1
            else:
                break

        debug.println(debug.LEVEL_FINEST,
                      "...default.findCommonAncestor")

        return commonAncestor

    def locusOfFocusChanged(self, event, oldLocusOfFocus, newLocusOfFocus):
        """Called when the visual object with focus changes.

        Arguments:
        - event: if not None, the Event that caused the change
        - oldLocusOfFocus: Accessible that is the old locus of focus
        - newLocusOfFocus: Accessible that is the new locus of focus
        """

        # We always automatically go back to focus tracking mode when
        # the focus changes.
        #
        if self.flatReviewContext:
            self.toggleFlatReviewMode()

        # [[[TODO: WDW - HACK because parents that manage their descendants
        # can give us a different object each time we ask for the same
        # exact child.  So...we do a check here to see if the old object
        # and new object have the same index in the parent and if they
        # have the same name.  If so, then they are likely to be the same
        # object.  The reason we check for the name here is a small sanity
        # check.  This whole algorithm could fail because one might be
        # deleting/adding identical elements from/to a list or table, thus
        # the objects really could be different even though they seem the
        # same.  Logged as bug 319675.]]]
        #
        if oldLocusOfFocus:
            oldParent = oldLocusOfFocus.parent
        else:
            oldParent = None

        if newLocusOfFocus:
            newParent = newLocusOfFocus.parent
        else:
            newParent = None

        if newParent and (oldParent == newParent):
            state = newParent.state
            if state.count(atspi.Accessibility.STATE_MANAGES_DESCENDANTS) \
                and (oldLocusOfFocus.index == newLocusOfFocus.index) \
                and (oldLocusOfFocus.name == newLocusOfFocus.name):
                    return

        # Well...now that we got that behind us, let's do what we're supposed
        # to do.
        #
        if newLocusOfFocus:
            self.updateBraille(newLocusOfFocus)

            verbosity = settings.getSetting(settings.SPEECH_VERBOSITY_LEVEL,
                                            settings.VERBOSITY_LEVEL_VERBOSE)

            utterances = []

            # Now figure out how of the container context changed and
            # speech just what is different.
            #
            commonAncestor = self.findCommonAncestor(oldLocusOfFocus,
                                                     newLocusOfFocus)
            if commonAncestor:
                utterances.extend(
                    self.speechGenerator.getSpeechContext(newLocusOfFocus,
                                                          commonAncestor))

            # Now, we'll treat table row and column headers as context
            # as well.  This requires special handling because we're
            # making headers seem hierarchical in the context, but they
            # are not hierarchical in the containment hierarchicy.
            # We also only want to speak the one that changed.  If both
            # changed, first speak the row header, then the column header.
            #
            # We also keep track of tree level depth and only announce
            # that if it changes.
            #
            oldNodeLevel = -1
            newNodeLevel = -1
            if newLocusOfFocus.role == rolenames.ROLE_TABLE_CELL:
                if oldParent and oldParent.table:
                    table = oldParent.table
                    oldRow = table.getRowAtIndex(oldLocusOfFocus.index)
                    oldCol = table.getColumnAtIndex(oldLocusOfFocus.index)
                else:
                    oldRow = -1
                    oldCol = -1

                if newParent and newParent.table:
                    table = newParent.table
                    newRow = table.getRowAtIndex(newLocusOfFocus.index)
                    newCol = table.getColumnAtIndex(newLocusOfFocus.index)

                    if newRow != oldRow:
                        desc = newParent.table.getRowDescription(newRow)
                        if desc and len(desc):
                            text = desc
                            if verbosity == settings.VERBOSITY_LEVEL_VERBOSE:
                                text += " " \
                                        + rolenames.rolenames[\
                                        rolenames.ROLE_ROW_HEADER].speech
                            utterances.append(text)
                    if newCol != oldCol:
                        desc = newParent.table.getColumnDescription(newCol)
                        if desc and len(desc):
                            text = desc
                            if verbosity == settings.VERBOSITY_LEVEL_VERBOSE:
                                text += " " \
                                        + rolenames.rolenames[\
                                        rolenames.ROLE_COLUMN_HEADER].speech
                            utterances.append(text)

                oldNodeLevel = atspi.getNodeLevel(oldLocusOfFocus)
                newNodeLevel = atspi.getNodeLevel(newLocusOfFocus)

            # Get the text for the object itself.
            #
            utterances.extend(
                self.speechGenerator.getSpeech(newLocusOfFocus, False))

            # Now speak the new tree node level if it has changed.
            #
            if (oldNodeLevel != newNodeLevel) \
               and (newNodeLevel >= 0):
                utterances.append(_("tree level %d") % (newNodeLevel + 1))

            speech.speakUtterances(utterances)
        else:
            message = _("No focus")
            braille.displayMessage(message)
            speech.speak(message)

    def visualAppearanceChanged(self, event, obj):
        """Called when the visual appearance of an object changes.  This
        method should not be called for objects whose visual appearance
        changes solely because of focus -- setLocusOfFocus is used for that.
        Instead, it is intended mostly for objects whose notional 'value' has
        changed, such as a checkbox changing state, a progress bar advancing,
        a slider moving, text inserted, caret moved, etc.

        Arguments:
        - event: if not None, the Event that caused this to happen
        - obj: the Accessible whose visual appearance changed.
        """

        # We care if panels are suddenly showing.  The reason for this
        # is that some applications, such as Evolution, will bring up
        # a wizard dialog that uses "Forward" and "Backward" buttons
        # that change the contents of the dialog.  We only discover
        # this through showing events. [[[TODO: WDW - perhaps what we
        # really want is to speak unbound labels that are suddenly
        # showing?  event.detail == 1 means object is showing.]]]
        #
        if (obj.role == rolenames.ROLE_PANEL) \
               and (event.detail1 == 1) \
               and orca.isInActiveApp(obj):

            # It's only showing if its parent is showing. [[[TODO: WDW -
            # HACK we stop at the application level because applications
            # never seem to have their showing state set.]]]
            #
            reallyShowing = True
            parent = obj.parent
            while reallyShowing \
                      and parent \
                      and (parent != parent.parent) \
                      and (parent.role != rolenames.ROLE_APPLICATION):
                debug.println(debug.LEVEL_FINEST,
                              "default.visualAppearanceChanged - " \
                              + "checking parent")
                reallyShowing = parent.state.count(\
                    atspi.Accessibility.STATE_SHOWING)
                parent = parent.parent

            # Find all the unrelated labels in the dialog and speak them.
            #
            if reallyShowing:
                utterances = []
                labels = atspi.findUnrelatedLabels(obj)
                for label in labels:
                    utterances.append(label.name)

                # [[[TODO: WDW - HACK to account for the way applications
                # such as Evolution handle their wizards.  They will set
                # the "Forward" and "Back" buttons insensitive as appropriate,
                # which has the side effect of nothing having focus.  So,
                # we let users know this via speech and braille.  For now,
                # this awful hack is isolated to when a panel starts showing
                # in the active application, which is the situation where
                # these types of poor application behavior has been found
                # to exist.]]]
                #
                if orca.locusOfFocus \
                   and (orca.locusOfFocus.state.count(\
                    atspi.Accessibility.STATE_SENSITIVE) == 0):
                    message = _("No focus")
                    utterances.append(message)
                    self.updateBraille(orca.locusOfFocus.parent,
                                       braille.Region(" " + message))

                speech.speakUtterances(utterances)

                return

        if obj != orca.locusOfFocus:
            return

        if event:
            debug.println(debug.LEVEL_FINE,
                          "VISUAL CHANGE: '%s' '%s' (event='%s')" \
                          % (obj.name, obj.role, event.type))
        else:
            debug.println(debug.LEVEL_FINE,
                          "VISUAL CHANGE: '%s' '%s' (event=None)" \
                          % (obj.name, obj.role))

        self.updateBraille(obj)
        speech.speakUtterances(
            self.speechGenerator.getSpeech(event.source, True))

    def getVisualParent(self, obj):
        """Returns the logical visual container for the given object or None
        if no such object exists.  The logical visual container differs from
        the component hierarchy in that it eliminates non-visual layout
        elements (e.g., panels without names or borders) from the hierarchy.
        """

        visualParent = None
        while obj.parent:
            if len(obj.parent.label) > 0:
                visualParent = obj.parent
            obj = obj.parent
            debug.println(debug.LEVEL_FINEST,
                          "default.getVisualParent - finding parent")

        return visualParent

    def updateBraille(self, obj, extraRegion=None):
        """Updates the braille display to show the give object.

        Arguments:
        - obj: the Accessible
        - extra: extra Region to add to the end
        """

        if not obj:
            message = _("No focus")
            braille.displayMessage(message)
            return

        braille.clear()

        line = braille.Line()
        braille.addLine(line)

        # For multiline text areas, we only show the context if we
        # are on the very first line.  Otherwise, we show only the
        # line.
        #
        if obj.role == rolenames.ROLE_TEXT:
            text = obj.text
            [string, startOffset, endOffset] = text.getTextAtOffset(
                text.caretOffset,
                atspi.Accessibility.TEXT_BOUNDARY_LINE_START)
            if startOffset == 0:
                line.addRegions(self.brailleGenerator.getBrailleContext(obj))
        else:
            line.addRegions(self.brailleGenerator.getBrailleContext(obj))

        result = self.brailleGenerator.getBrailleRegions(obj)
        line.addRegions(result[0])

        if extraRegion:
            line.addRegion(extraRegion)

        if extraRegion:
            braille.setFocus(extraRegion)
        else:
            braille.setFocus(result[1])

        braille.refresh(True)

    ########################################################################
    #                                                                      #
    # AT-SPI OBJECT EVENT HANDLERS                                         #
    #                                                                      #
    ########################################################################

    def onFocus(self, event):
        """Called whenever an object gets focus.

        Arguments:
        - event: the Event
        """

        # [[[TODO: WDW - HACK to deal with quirky GTK+ menu behavior.
        # The problem is that when moving to submenus in a menu, the
        # menu gets focus first and then the submenu gets focus all
        # with a single keystroke.  So...focus in menus really means
        # that the object has focus *and* it is selected.  Now, this
        # assumes the selected state will be set before focus is given,
        # which appears to be the case from empirical analysis of the
        # event stream.  But of course, all menu items and menus in
        # the complete menu path will have their selected state set,
        # so, we really only care about the leaf menu or menu item
        # that it selected.]]]
        #
        role = event.source.role
        if (role == rolenames.ROLE_MENU) \
           or (role == rolenames.ROLE_MENU_ITEM) \
           or (role == rolenames.ROLE_CHECK_MENU_ITEM) \
           or (role == rolenames.ROLE_RADIO_MENU_ITEM):
            selection = event.source.selection
            if selection and selection.nSelectedChildren > 0:
                return

        # [[[TODO: WDW - HACK to deal with the fact that active cells
        # may or may not get focus.  Their parents, however, do tend to
        # get focus, but when the parent gets focus, it really means
        # that the selected child in it has focus.  Of course, this all
        # breaks when more than one child is selected.  Then, we really
        # need to depend upon the model where focus really works.]]]
        #
        newFocus = event.source

        if (event.source.role == rolenames.ROLE_LAYERED_PANE) \
            or (event.source.role == rolenames.ROLE_TABLE) \
            or (event.source.role == rolenames.ROLE_TREE_TABLE) \
            or (event.source.role == rolenames.ROLE_TREE):
            if event.source.childCount:
                selection = event.source.selection
                if selection and selection.nSelectedChildren > 0:
                    child = selection.getSelectedChild(0)
                    if child:
                        newFocus = atspi.Accessible.makeAccessible(child)

        orca.setLocusOfFocus(event, newFocus)

    def onNameChanged(self, event):
        """Called whenever a property on an object changes.

        Arguments:
        - event: the Event
        """

        # [[[TODO: WDW - HACK because gnome-terminal issues a name changed
        # event for the edit preferences dialog even though the name really
        # didn't change.  I'm guessing this is going to be a vagary in all
        # of GTK+.]]]
        #
        if event.source and (event.source.role == rolenames.ROLE_DIALOG) \
           and (event.source == orca.locusOfFocus):
            return

        orca.visualAppearanceChanged(event, event.source)

    def onCaretMoved(self, event):
        """Called whenever the caret moves.

        Arguments:
        - event: the Event
        """

        # Ignore text deletions from non-focused objects, unless the
        # currently focused object is the parent of the object from which
        # text was deleted
        #
        if (event.source != orca.locusOfFocus) \
               and (event.source.parent != orca.locusOfFocus):
            return

        # We always automatically go back to focus tracking mode when
        # the caret moves in the focused object.
        #
        if self.flatReviewContext:
            self.toggleFlatReviewMode()

        # Magnify the object.  [[[TODO: WDW - this is a hack for now.]]]
        #
        #mag.magnifyAccessible(event.source)

        # Update the Braille display - if we can just reposition
        # the cursor, then go for it.
        #
        brailleNeedsRepainting = True
        line = braille.getShowingLine()
        for region in line.regions:
            if isinstance(region, braille.Text) \
               and (region.accessible == event.source):
                if region.repositionCursor():
                    braille.refresh(True)
                    brailleNeedsRepainting = False
                break

        if brailleNeedsRepainting:
            self.updateBraille(event.source)

        if (not orca.lastInputEvent) \
            or \
            (not isinstance(orca.lastInputEvent, input_event.KeyboardEvent)):
            return

        # Guess why the caret moved and say something appropriate.
        # [[[TODO: WDW - this motion assumes traditional GUI
        # navigation gestures.  In an editor such as vi, line up and
        # down is done via other actions such as "i" or "j".  We may
        # need to think about this a little harder.]]]
        #
        string = orca.lastInputEvent.event_string
        mods = orca.lastInputEvent.modifiers
        controlMask = 1 << atspi.Accessibility.MODIFIER_CONTROL

        if (string == "Up") or (string == "Down"):
            sayLine(event.source)
        elif (string == "Left") or (string == "Right"):
            if (mods & controlMask):
                sayWord(event.source)
            else:
                sayCharacter(event.source)
        elif string == "Page_Up":
            if (mods & controlMask):
                sayCharacter(event.source)
            else:
                sayLine(event.source)
        elif string == "Page_Down":
            sayLine(event.source)
        elif (string == "Home") or (string == "End"):
            if (mods & controlMask):
                sayLine(event.source)
            else:
                sayCharacter(event.source)

    def onTextDeleted(self, event):
        """Called whenever text is deleted from an object.

        Arguments:
        - event: the Event
        """

        # Ignore text deletions from non-focused objects, unless the
        # currently focused object is the parent of the object from which
        # text was deleted
        #
        if (event.source != orca.locusOfFocus) \
               and (event.source.parent != orca.locusOfFocus):
            return

        self.updateBraille(event.source)

        # The any_data member of the event object has the deleted text in
        # it - If the last key pressed was a backspace or delete key,
        # speak the deleted text.  [[[TODO: WDW - again, need to think
        # about the ramifications of this when it comes to editors such
        # as vi or emacs.
        #
        if (not orca.lastInputEvent) \
            or \
            (not isinstance(orca.lastInputEvent, input_event.KeyboardEvent)):
            return

        string = orca.lastInputEvent.event_string
        text = event.any_data.value()
        if (string == "BackSpace") or (string == "Delete"):
            if text.isupper():
                speech.speak(text, self.voices["uppercase"])
            else:
                speech.speak(text)

    def onTextInserted(self, event):
        """Called whenever text is inserted into an object.

        Arguments:
        - event: the Event
        """

        # Ignore text deletions from non-focused objects, unless the
        # currently focused object is the parent of the object from which
        # text was deleted
        #
        if (event.source != orca.locusOfFocus) \
               and (event.source.parent != orca.locusOfFocus):
            return

        self.updateBraille(event.source)
        text = event.any_data.value()

        if text.isupper():
            speech.speak(text, self.voices["uppercase"])
        else:
            speech.speak(text)

    def onActiveDescendantChanged(self, event):
        """Called when an object who manages its own descendants detects a
        change in one of its children.

        Arguments:
        - event: the Event
        """

        child = atspi.Accessible.makeAccessible(event.any_data.value())

        if child.childCount:
            orca.setLocusOfFocus(event, child.child(1))
        else:
            orca.setLocusOfFocus(event, child)

    def onLinkSelected(self, event):
        """Called when a hyperlink is selected in a text area.

        Arguments:
        - event: the Event
        """

        # [[[TODO: WDW - HACK one might think we could expect an
        # application to keep its name, but it appears as though
        # yelp has an identity problem and likes to start calling
        # itself "yelp," but then changes its name to "Mozilla"
        # on Fedora Core 4 after the user selects a link.  So, we'll
        # just assume that link-selected events always come from the
        # application with focus.]]]
        #
        #if orca.locusOfFocus \
        #   and (orca.locusOfFocus.app == event.source.app):
        #    orca.setLocusOfFocus(event, event.source)
        orca.setLocusOfFocus(event, event.source)

    def onStateChanged(self, event):
        """Called whenever an object's state changes.  Currently, the
        state changes for non-focused objects are ignored.

        Arguments:
        - event: the Event
        """

        # Do we care?
        #
        if state_change_notifiers.has_key(event.source.role):
            notifiers = state_change_notifiers[event.source.role]
            found = False
            for state in notifiers:
                if state and event.type.endswith(state):
                    found = True
                    break
            if found:
                orca.visualAppearanceChanged(event, event.source)

        # [[[TODO: WDW - HACK we'll handle this in the visual appearance
        # changed handler.]]]
        #
        # The object with focus might become insensitive, so we need to
        # flag that.  This typically occurs in wizard dialogs such as
        # the account setup assistant in Evolution.
        #
        #if event.type.endswith("sensitive") \
        #   and (event.detail1 == 0) \
        #   and event.source == orca.locusOfFocus:
        #    print "FOO INSENSITIVE"
        #    #orca.setLocusOfFocus(event, None)

    def onSelectionChanged(self, event):
        """Called when an object's selection changes.

        Arguments:
        - event: the Event
        """

        # [[[TODO: WDW - HACK layered panes are nutty in that they
        # will change the selection and tell the selected child it is
        # focused, but the child will not issue a focus changed event.]]]
        #
        if event.source \
           and (event.source.role == rolenames.ROLE_LAYERED_PANE):
#               or (event.source.role == rolenames.ROLE_TABLE) \
#               or (event.source.role == rolenames.ROLE_TREE_TABLE) \
#               or (event.source.role == rolenames.ROLE_TREE)):
            if event.source.childCount:
                selection = event.source.selection
                if selection and selection.nSelectedChildren > 0:
                    child = selection.getSelectedChild(0)
                    if child:
                        orca.setLocusOfFocus(event,
                                             atspi.Accessible.makeAccessible(child))

    def onValueChanged(self, event):
        """Called whenever an object's value changes.  Currently, the
        value changes for non-focused objects are ignored.

        Arguments:
        - event: the Event
        """

        orca.visualAppearanceChanged(event, event.source)

    def onWindowActivated(self, event):
        """Called whenever a toplevel window is activated.

        Arguments:
        - event: the Event
        """

        orca.setLocusOfFocus(event, event.source)

    def onWindowDeactivated(self, event):
        """Called whenever a toplevel window is deactivated.

        Arguments:
        - event: the Event
        """

        orca.setLocusOfFocus(event, None)

    def noOp(self, event):
        """Just here to capture events.

        Arguments:
        - event: the Event
        """
        pass

    ########################################################################
    #                                                                      #
    # Flat review mode support.  [[[TODO: WDW - still under development,   #
    # but the idea is that a script should be able to provide custom       #
    # information about layout as well.]]]                                 #
    #                                                                      #
    ########################################################################

    def getShowingZones(self):
        """Returns a list of all interesting, non-intersecting,
        regions that are drawn in the currently active window.  Each
        element of the list is the Accessible object associated with a
        given region.  The term 'zone' here is inherited from OCR
        algorithms and techniques.

        The objects are returned in no particular order.

        Arguments:
        - root: the Accessible object to traverse

        Returns: a list of all objects under the specified object
        """
        if (not orca.locusOfFocus) or (orca.locusOfFocus.app != self.app):
            return []

        # We want to stop at the window or frame or equivalent level.
        #
        obj = orca.locusOfFocus
        while obj \
                  and obj.parent \
                  and (obj.parent.role != rolenames.ROLE_APPLICATION) \
                  and (obj != obj.parent):
            obj = obj.parent

        if obj:
            return flat_review.getShowingZones(obj)
        else:
            return []

    def clusterZonesByLine(self, zones):
        """Given a list of interesting accessible objects (the zones),
        returns a list of lines in order from the top to bottom, where
        each line is a list of accessible objects in order from left
        to right.  """

        return flat_review.clusterZonesByLine(zones)

    def getFlatReviewContext(self):
        """Returns the flat review context, creating one if necessary."""

        if not self.flatReviewContext:
            # The first thing we try to do is find which Zone has the
            # Accessible object with focus.
            #
            currentLineIndex = 0
            currentZoneIndex = 0
            currentWordIndex = 0
            currentCharIndex = 0
            lines = self.clusterZonesByLine(self.getShowingZones())
            foundZoneWithFocus = False
            while currentLineIndex < len(lines):
                line = lines[currentLineIndex]
                currentZoneIndex = 0
                while currentZoneIndex < len(line.zones):
                    zone = line.zones[currentZoneIndex]
                    if zone.accessible == orca.locusOfFocus:
                        foundZoneWithFocus = True
                        break
                    else:
                        currentZoneIndex += 1
                if foundZoneWithFocus:
                    break
                else:
                    currentLineIndex += 1

            # Fallback to the first Zone if we didn't find anything.
            #
            if not foundZoneWithFocus:
                currentLineIndex = 0
                currentZoneIndex = 0
            elif isinstance(zone, flat_review.TextZone):
                # If we're on an accessible text object, try to set the
                # review cursor to the caret position of that object.
                #
                accessible  = zone.accessible
                lineIndex   = currentLineIndex
                zoneIndex   = currentZoneIndex
                caretOffset = zone.accessible.text.caretOffset
                foundZoneWithCaret = False
                while lineIndex < len(lines):
                    line = lines[lineIndex]
                    while zoneIndex < len(line.zones):
                        zone = line.zones[zoneIndex]
                        if zone.accessible == accessible:
                            if (caretOffset >= zone.startOffset) \
                                   and (caretOffset \
                                        < (zone.startOffset + zone.length)):
                                foundZoneWithCaret = True
                                break
                        zoneIndex += 1
                    if foundZoneWithCaret:
                        currentLineIndex = lineIndex
                        currentZoneIndex = zoneIndex
                        currentWordIndex = 0
                        currentCharIndex = 0
                        offset = zone.startOffset
                        while currentWordIndex < len(zone.words):
                            word = zone.words[currentWordIndex]
                            if (word.length + offset) > caretOffset:
                                currentCharIndex = caretOffset - offset
                                break
                            else:
                                currentWordIndex += 1
                                offset += word.length
                        break
                    else:
                        zoneIndex = 0
                        lineIndex += 1

            self.flatReviewContext = flat_review.Context(lines,
                                                         currentLineIndex,
                                                         currentZoneIndex,
                                                         currentWordIndex,
                                                         currentCharIndex)

            self.justEnteredFlatReviewMode = True

            # Also, we want to remember where the cursor currently was
            # when the user was in focus tracking mode.  We'll try to
            # keep the position the same as we move to characters above
            # and below us.
            #
            self.targetCursorCell = braille.cursorCell

        return self.flatReviewContext

    def toggleFlatReviewMode(self, inputEvent=None):
        """Toggles between flat review mode and focus tracking mode."""

        if self.flatReviewContext:
            orca.drawOutline(-1, 0, 0, 0)
            self.flatReviewContext = None
            self.updateBraille(orca.locusOfFocus)
        else:
            context = self.getFlatReviewContext()
            [string, x, y, width, height] = \
                     context.getCurrent(flat_review.Context.WORD)
            orca.drawOutline(x, y, width, height)
            self.reviewCurrentItem(inputEvent, self.targetCursorCell)

        return True

    def updateBrailleReview(self, targetCursorCell=0):
        """Obtains the braille regions for the current flat review line
        and displays them on the braille display.  If the targetCursorCell
        is non-0, then an attempt will be made to postion the review cursor
        at that cell.  Otherwise, we will pan in display-sized increments
        to show the review cursor."""

        context = self.getFlatReviewContext()

        [regions, regionWithFocus] = context.getCurrentBrailleRegions()

        line = braille.Line()
        line.addRegions(regions)
        braille.setLines([line])
        braille.setFocus(regionWithFocus, False)
        braille.panToOffset(regionWithFocus.brailleOffset \
                            + regionWithFocus.cursorOffset)

        if self.justEnteredFlatReviewMode:
            braille.refresh(True, self.targetCursorCell)
            self.justEnteredFlatReviewMode = False
        else:
            braille.refresh(True, targetCursorCell)

    def _setFlatReviewContextToBeginningOfBrailleDisplay(self):
        """Sets the character of interest to be the first character showing
        at the beginning of the braille display."""

        context = self.getFlatReviewContext()
        [regions, regionWithFocus] = context.getCurrentBrailleRegions()
        for region in regions:
            if ((region.brailleOffset + len(region.string)) \
                   > braille._viewport[0]) \
                and (isinstance(region, braille.ReviewText) \
                     or isinstance(region, braille.ReviewComponent)):
                position = max(region.brailleOffset, braille._viewport[0])
                offset = position - region.brailleOffset
                self.targetCursorCell = region.brailleOffset \
                                        - braille._viewport[0]
                [word, charOffset] = region.zone.getWordAtOffset(offset)
                if word:
                    self.flatReviewContext.setCurrent(
                        word.zone.line.index,
                        word.zone.index,
                        word.index,
                        charOffset)
                else:
                    self.flatReviewContext.setCurrent(
                        region.zone.line.index,
                        region.zone.index,
                        0, # word index
                        0) # character index
                break

    def panBrailleLeft(self, inputEvent=None, panAmount=0):
        """Pans the braille display to the left.  If panAmount is non-zero,
        the display is panned by that many cells.  If it is 0, the display
        is panned one full display width.  In flat review mode, panning
        beyond the beginning will take you to the end of the previous line.

        In focus tracking mode, the cursor stays at its logical position.
        In flat review mode, the review cursor moves to character
        associated with cell 0."""

        if self.flatReviewContext:
            if braille.beginningIsShowing:
                self.flatReviewContext.goBegin(flat_review.Context.LINE)
                self.reviewPreviousCharacter(inputEvent)
            else:
                braille.panLeft(panAmount)

            # This will update our target cursor cell
            #
            self._setFlatReviewContextToBeginningOfBrailleDisplay()

            [string, x, y, width, height] = \
                self.flatReviewContext.getCurrent(flat_review.Context.CHAR)
            orca.drawOutline(x, y, width, height)

            self.targetCursorCell = 1
            self.updateBrailleReview(self.targetCursorCell)
        elif braille.beginningIsShowing and orca.locusOfFocus \
             and (orca.locusOfFocus.role == rolenames.ROLE_TEXT):
            # If we're at the beginning of a line of a multiline text
            # area, then force it's caret to the end of the previous
            # line.  The assumption here is that we're currently
            # viewing the line that has the caret -- which is a pretty
            # good assumption for focus tacking mode.  When we set the
            # caret position, we will get a caret event, which will
            # then update the braille.
            #
            text = orca.locusOfFocus.text
            [string, startOffset, endOffset] = text.getTextAtOffset(
                text.caretOffset,
                atspi.Accessibility.TEXT_BOUNDARY_LINE_START)
            if startOffset > 0:
                text.setCaretOffset(startOffset - 1)
        else:
            braille.panLeft(panAmount)
            braille.refresh(False)

        return True

    def panBrailleLeftOneChar(self, inputEvent=None):
        """Nudges the braille display one character to the left.

        In focus tracking mode, the cursor stays at its logical position.
        In flat review mode, the review cursor moves to character
        associated with cell 0."""

        self.panBrailleLeft(inputEvent, 1)

    def panBrailleRight(self, inputEvent=None, panAmount=0):
        """Pans the braille display to the right.  If panAmount is non-zero,
        the display is panned by that many cells.  If it is 0, the display
        is panned one full display width.  In flat review mode, panning
        beyond the end will take you to the begininng of the next line.

        In focus tracking mode, the cursor stays at its logical position.
        In flat review mode, the review cursor moves to character
        associated with cell 0."""

        if self.flatReviewContext:
            if braille.endIsShowing:
                self.flatReviewContext.goEnd(flat_review.Context.LINE)
                self.reviewNextCharacter(inputEvent)
            else:
                braille.panRight(panAmount)

            # This will update our target cursor cell
            #
            self._setFlatReviewContextToBeginningOfBrailleDisplay()

            [string, x, y, width, height] = \
                self.flatReviewContext.getCurrent(flat_review.Context.CHAR)

            orca.drawOutline(x, y, width, height)

            self.targetCursorCell = 1
            self.updateBrailleReview(self.targetCursorCell)
        elif braille.endIsShowing and orca.locusOfFocus \
             and (orca.locusOfFocus.role == rolenames.ROLE_TEXT):
            # If we're at the end of a line of a multiline text area, then
            # force it's caret to the beginning of the next line.  The
            # assumption here is that we're currently viewing the line that
            # has the caret -- which is a pretty good assumption for focus
            # tacking mode.  When we set the caret position, we will get a
            # caret event, which will then update the braille.
            #
            text = orca.locusOfFocus.text
            [string, startOffset, endOffset] = text.getTextAtOffset(
                text.caretOffset,
                atspi.Accessibility.TEXT_BOUNDARY_LINE_START)
            if endOffset < text.characterCount:
                text.setCaretOffset(endOffset)
        else:
            braille.panRight(panAmount)
            braille.refresh(False)

        return True

    def panBrailleRightOneChar(self, inputEvent=None):
        """Nudges the braille display one character to the right.

        In focus tracking mode, the cursor stays at its logical position.
        In flat review mode, the review cursor moves to character
        associated with cell 0."""

        self.panBrailleRight(inputEvent, 1)

    def goBrailleHome(self, inputEvent=None):
        """Returns to the component with focus."""

        if self.flatReviewContext:
            return self.toggleFlatReviewMode(inputEvent)
        else:
            return braille.returnToRegionWithFocus(inputEvent)

    def leftClickReviewItem(self, inputEvent=None):
        """Performs a left mouse button click on the current item."""

        self.getFlatReviewContext().clickCurrent(1)
        return True

    def rightClickReviewItem(self, inputEvent=None):
        """Performs a right mouse button click on the current item."""

        self.getFlatReviewContext().clickCurrent(3)
        return True

    def reviewCurrentLine(self, inputEvent):
        """Presents the current flat review line via braille and speech."""

        context = self.getFlatReviewContext()

        [string, x, y, width, height] = \
                 context.getCurrent(flat_review.Context.LINE)
        orca.drawOutline(x, y, width, height)

        # Don't announce anything from speech if the user used
        # the Braille display as an input device.
        #
        if not isinstance(inputEvent, input_event.BrailleEvent):
            if (not string) or (len(string) == 0) or (string == "\n"):
                speech.speak(_("blank"))
            elif string.isspace():
                speech.speak(_("white space"))
            else:
                speech.speak(string)

        self.updateBrailleReview()

        return True

    def reviewPreviousLine(self, inputEvent):
        """Moves the flat review context to the beginning of the
        previous line."""

        context = self.getFlatReviewContext()

        moved = context.goPrevious(flat_review.Context.LINE,
                                   flat_review.Context.WRAP_LINE)

        if moved:
            self.reviewCurrentLine(inputEvent)
            self.targetCursorCell = braille.cursorCell

        return True

    def reviewHome(self, inputEvent):
        """Moves the flat review context to the top left of the current
        window."""

        context = self.getFlatReviewContext()

        context.goBegin()

        self.reviewCurrentLine(inputEvent)
        self.targetCursorCell = braille.cursorCell

        return True

    def reviewNextLine(self, inputEvent):
        """Moves the flat review context to the beginning of the
        next line.  Places the flat review cursor at the beginning
        of the line."""

        context = self.getFlatReviewContext()

        moved = context.goNext(flat_review.Context.LINE,
                               flat_review.Context.WRAP_LINE)

        if moved:
            self.reviewCurrentLine(inputEvent)
            self.targetCursorCell = braille.cursorCell

        return True

    def reviewBottomLeft(self, inputEvent):
        """Moves the flat review context to the beginning of the
        last line in the window.  Places the flat review cursor at
        the beginning of the line."""

        context = self.getFlatReviewContext()

        context.goEnd(flat_review.Context.WINDOW)
        context.goBegin(flat_review.Context.LINE)
        self.reviewCurrentLine(inputEvent)
        self.targetCursorCell = braille.cursorCell

        return True

    def reviewEnd(self, inputEvent):
        """Moves the flat review context to the end of the
        last line in the window.  Places the flat review cursor
        at the end of the line."""

        context = self.getFlatReviewContext()
        context.goEnd()

        self.reviewCurrentLine(inputEvent)
        self.targetCursorCell = braille.cursorCell

        return True

    def reviewCurrentItem(self, inputEvent, targetCursorCell=0):
        """Presents the current item to the user."""

        context = self.getFlatReviewContext()
        [string, x, y, width, height] = \
                 context.getCurrent(flat_review.Context.WORD)
        orca.drawOutline(x, y, width, height)

        # Don't announce anything from speech if the user used
        # the Braille display as an input device.
        #
        if not isinstance(inputEvent, input_event.BrailleEvent):
            if (len(string) == 0) or (string == "\n"):
                speech.speak(_("blank"))
            else:
                [lineString, x, y, width, height] = \
                         context.getCurrent(flat_review.Context.LINE)
                if lineString == "\n":
                    speech.speak(_("blank"))
                elif string.isspace():
                    speech.speak(_("white space"))
                elif string.isupper():
                    speech.speak(string, self.voices["uppercase"])
                else:
                    speech.speak(string)

        self.updateBrailleReview(targetCursorCell)

        return True

    def reviewCurrentAccessible(self, inputEvent):
        context = self.getFlatReviewContext()
        [string, x, y, width, height] = \
                 context.getCurrent(flat_review.Context.ZONE)
        orca.drawOutline(x, y, width, height)

        # Don't announce anything from speech if the user used
        # the Braille display as an input device.
        #
        if not isinstance(inputEvent, input_event.BrailleEvent):
            speech.speakUtterances(
                self.speechGenerator.getSpeech(
                    context.getCurrentAccessible(), False))

        return True

    def reviewPreviousItem(self, inputEvent):
        """Moves the flat review context to the previous item.  Places
        the flat review cursor at the beginning of the item."""

        context = self.getFlatReviewContext()

        moved = context.goPrevious(flat_review.Context.WORD,
                                   flat_review.Context.WRAP_LINE)

        if moved:
            self.reviewCurrentItem(inputEvent)
            self.targetCursorCell = braille.cursorCell

        return True

    def reviewNextItem(self, inputEvent):
        """Moves the flat review context to the next item.  Places
        the flat review cursor at the beginning of the item."""

        context = self.getFlatReviewContext()

        moved = context.goNext(flat_review.Context.WORD,
                               flat_review.Context.WRAP_LINE)

        if moved:
            self.reviewCurrentItem(inputEvent)
            self.targetCursorCell = braille.cursorCell

        return True

    def reviewCurrentCharacter(self, inputEvent):
        context = self.getFlatReviewContext()

        [string, x, y, width, height] = \
                 context.getCurrent(flat_review.Context.CHAR)
        orca.drawOutline(x, y, width, height)

        # Don't announce anything from speech if the user used
        # the Braille display as an input device.
        #
        if not isinstance(inputEvent, input_event.BrailleEvent):
            if (len(string) == 0):
                speech.speak(_("blank"))
            else:
                [lineString, x, y, width, height] = \
                         context.getCurrent(flat_review.Context.LINE)
                if lineString == "\n":
                    speech.speak(_("blank"))
                elif string.isupper():
                    speech.speak(string, self.voices["uppercase"])
                else:
                    speech.speak(string)

        self.updateBrailleReview()

        return True

    def reviewPreviousCharacter(self, inputEvent):
        """Moves the flat review context to the previous character.  Places
        the flat review cursor at character."""

        context = self.getFlatReviewContext()

        moved = context.goPrevious(flat_review.Context.CHAR,
                                   flat_review.Context.WRAP_LINE)

        if moved:
            self.reviewCurrentCharacter(inputEvent)
            self.targetCursorCell = braille.cursorCell

        return True

    def reviewEndOfLine(self, inputEvent):
        """Moves the flat review context to the end of the line.  Places
        the flat review cursor at the end of the line."""

        context = self.getFlatReviewContext()
        context.goEnd(flat_review.Context.LINE)

        self.reviewCurrentCharacter(inputEvent)
        self.targetCursorCell = braille.cursorCell

        return True

    def reviewNextCharacter(self, inputEvent):
        """Moves the flat review context to the next character.  Places
        the flat review cursor at character."""

        context = self.getFlatReviewContext()

        moved = context.goNext(flat_review.Context.CHAR,
                               flat_review.Context.WRAP_LINE)

        if moved:
            self.reviewCurrentCharacter(inputEvent)
            self.targetCursorCell = braille.cursorCell

        return True

    def reviewAbove(self, inputEvent):
        """Moves the flat review context to the character most directly
        above the current flat review cursor.  Places the flat review
        cursor at character."""

        context = self.getFlatReviewContext()

        moved = context.goAbove(flat_review.Context.CHAR,
                                flat_review.Context.WRAP_LINE)

        if moved:
            self.reviewCurrentItem(inputEvent, self.targetCursorCell)

        return True

    def reviewBelow(self, inputEvent):
        """Moves the flat review context to the character most directly
        below the current flat review cursor.  Places the flat review
        cursor at character."""

        context = self.getFlatReviewContext()

        moved = context.goBelow(flat_review.Context.CHAR,
                                flat_review.Context.WRAP_LINE)

        if moved:
            self.reviewCurrentItem(inputEvent, self.targetCursorCell)

        return True

    def showZones(self, inputEvent):
        """Debug routine to paint rectangles around the discrete
        interesting (e.g., text)  zones in the active window for
        this application.
        """

        flatReviewContext = self.getFlatReviewContext()
        lines = flatReviewContext.lines
        print "Number of lines:", len(lines)
        for line in lines:
            string = ""
            for zone in line.zones:
                string += " '%s' [%s]" % (zone.string, zone.accessible.role)
                orca.drawOutline(zone.x, zone.y, zone.width, zone.height,
                                 False)
            debug.println(debug.LEVEL_OFF, string)
        self.flatReviewContext = None

########################################################################
#                                                                      #
# ACCESSIBLE TEXT OUTPUT FUNCTIONS                                     #
#                                                                      #
# Functions for handling output of AccessibleText objects to speech.   #
#                                                                      #
########################################################################

def sayLine(obj):
    """Speaks the line of an AccessibleText object that contains the
    caret. [[[TODO: WDW - what if the line is empty?]]]

    Arguments:
    - obj: an Accessible object that implements the AccessibleText
           interface
    """

    # Get the AccessibleText interface of the provided object
    #
    result = atspi.getTextLineAtCaret(obj)
    speech.speak(result[0])

def sayWord(obj):
    """Speaks the word at the caret.  [[[TODO: WDW - what if there is no
    word at the caret?]]]

    Arguments:
    - obj: an Accessible object that implements the AccessibleText
           interface
    """

    text = obj.text
    offset = text.caretOffset
    word = text.getTextAtOffset(offset,
                                atspi.Accessibility.TEXT_BOUNDARY_WORD_START)
    speech.speak(word[0])

def sayCharacter(obj):
    """Speak the character under the caret.  [[[TODO: WDW - isn't the
    caret between characters?]]]

    Arguments:
    - obj: an Accessible object that implements the AccessibleText
           interface
    """

    text = obj.text
    offset = text.caretOffset
    character = text.getText(offset, offset+1)
    if character.isupper():
        voices = settings.getSetting(settings.VOICES, None)
        speech.speak(character, voices[settings.UPPERCASE_VOICE])
    else:
        speech.speak(character)

# Dictionary that defines the state changes we care about for various
# objects.  The key represents the role and the value represents a list
# of states that we care about.
#
state_change_notifiers = {}

state_change_notifiers[rolenames.ROLE_CHECK_BOX]     = ("checked",
                                                        None)
state_change_notifiers[rolenames.ROLE_PANEL]         = ("showing",
                                                        None)
state_change_notifiers[rolenames.ROLE_LABEL]         = ("showing",
                                                        None)
state_change_notifiers[rolenames.ROLE_TOGGLE_BUTTON] = ("checked",
                                                        None)
state_change_notifiers[rolenames.ROLE_TABLE_CELL]    = ("checked",
                                                        "expanded",
                                                        None)

