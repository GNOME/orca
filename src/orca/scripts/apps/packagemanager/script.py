# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
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

"""Custom script for Packagemanager."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi

import orca.braille as braille
import orca.default as default
import orca.input_event as input_event
import orca.orca as orca
import orca.orca_state as orca_state
import orca.settings as settings
import orca.speech as speech

from orca.orca_i18n import _

from braille_generator import BrailleGenerator
from speech_generator import SpeechGenerator
from tutorialgenerator import TutorialGenerator

########################################################################
#                                                                      #
# The Packagemanager script class.                                     #
#                                                                      #
########################################################################

class Script(default.Script):

    def __init__(self, app):
        """Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """

        default.Script.__init__(self, app)
        self._isBusy = False
        self._lastObjectPresented = None

    def getListeners(self):
        """Sets up the AT-SPI event listeners for this script."""

        listeners = default.Script.getListeners(self)
        listeners["object:state-changed:busy"] = self.onStateChanged

        return listeners

    def getBrailleGenerator(self):
        """Returns the braille generator for this script."""

        return BrailleGenerator(self)

    def getSpeechGenerator(self):
        """Returns the speech generator for this script."""

        return SpeechGenerator(self)

    def getTutorialGenerator(self):
        """Returns the tutorial generator for this script."""

        return TutorialGenerator(self)

    def locusOfFocusChanged(self, event, oldLocusOfFocus, newLocusOfFocus):
        """Called when the visual object with focus changes.

        Arguments:
        - event: if not None, the Event that caused the change
        - oldLocusOfFocus: Accessible that is the old locus of focus
        - newLocusOfFocus: Accessible that is the new locus of focus
        """

        # Prevent chattiness when arrowing out of or into a link.
        #
        if isinstance(orca_state.lastInputEvent, input_event.KeyboardEvent) \
           and orca_state.lastNonModifierKeyEvent.event_string in \
               ["Left", "Right", "Up", "Down"] \
           and event and event.type.startswith("focus:") \
           and (self.isLink(oldLocusOfFocus) or self.isLink(newLocusOfFocus)):
            orca.setLocusOfFocus(event, newLocusOfFocus, False)
            return

        default.Script.locusOfFocusChanged(
            self, event, oldLocusOfFocus, newLocusOfFocus)

    def onCaretMoved(self, event):
        """Called whenever the caret moves.

        Arguments:
        - event: the Event
        """

        # When arrowing into a link, we get a focus: event followed by two
        # identical caret-moved events.
        #
        lastPos = self.pointOfReference.get("lastCursorPosition")
        if lastPos and lastPos[0] == event.source \
           and lastPos[1] == event.detail1:
            return

        # Quietly set the locusOfFocus in HTML containers so that the default
        # script doesn't ignore this event.
        #
        if event.source != orca_state.locusOfFocus \
           and self.getAncestor(event.source,
                                [pyatspi.ROLE_HTML_CONTAINER],
                                [pyatspi.ROLE_FRAME]):
            orca.setLocusOfFocus(event, event.source, False)

        default.Script.onCaretMoved(self, event)

    def onFocus(self, event):
        """Called whenever an object gets focus.

        Arguments:
        - event: the Event
        """

        # For some reason we're getting quite a few claims of focus from
        # nameless page tabs. This seems to occur in conjunction with PM's
        # new Recent Searches feature. We need to ignore these events.
        #
        if event and event.source and not event.source.name \
           and event.source.getRole() == pyatspi.ROLE_PAGE_TAB:
            return

        default.Script.onFocus(self, event)

    def onStateChanged(self, event):
        """Called whenever an object's state changes.

        Arguments:
        - event: the Event
        """

        # TODO - JD: This might be a good candidate for a braille "flash
        # message."
        #
        if event.source.getRole() == pyatspi.ROLE_FRAME \
           and event.type.startswith("object:state-changed:busy"):
            # The busy cursor gets set/unset frequently. It's only worth
            # presenting if we're in the Search entry (handles both search
            # and catalog refreshes).
            #
            if not self.isSearchEntry(orca_state.locusOfFocus):
                return

            if event.detail1 == 1 and not self._isBusy:
                # Translators: this is in reference to loading a web page
                # or some other content.
                #
                speech.speak(_("Loading.  Please wait."))
                self._isBusy = True
            elif event.detail1 == 0 and self._isBusy:
                # Translators: this is in reference to loading a web page
                # or some other content.
                #
                speech.speak(_("Finished loading."))
                self._isBusy = False
            return

        default.Script.onStateChanged(self, event)

    def findStatusBar(self, obj):
        """Returns the status bar in the window which contains obj.
        Overridden here because Packagemanager seems to have multiple
        status bars which claim to be SHOWING and VISIBLE. The one we
        want should be displaying text, whereas the others are not.
        """

        # There are some objects which are not worth descending.
        #
        skipRoles = [pyatspi.ROLE_TREE,
                     pyatspi.ROLE_TREE_TABLE,
                     pyatspi.ROLE_TABLE]

        if obj.getState().contains(pyatspi.STATE_MANAGES_DESCENDANTS) \
           or obj.getRole() in skipRoles:
            return

        statusBar = None
        for i in range(obj.childCount - 1, -1, -1):
            if obj[i].getRole() == pyatspi.ROLE_STATUS_BAR:
                statusBar = obj[i]
            elif not obj[i] in skipRoles:
                statusBar = self.findStatusBar(obj[i])

            if statusBar:
                try:
                    text = statusBar.queryText()
                except:
                    pass
                else:
                    if text.characterCount:
                        break

        return statusBar

    def stopSpeechOnActiveDescendantChanged(self, event):
        """Whether or not speech should be stopped prior to setting the
        locusOfFocus in onActiveDescendantChanged.

        Arguments:
        - event: the Event

        Returns True if speech should be stopped; False otherwise.
        """

        # Intentionally doing an equality check for performance
        # purposes.
        #
        if event.any_data == orca_state.locusOfFocus:
            return False

        return True

    def onActiveDescendantChanged(self, event):
        """Called when an object who manages its own descendants detects a
        change in one of its children.

        Arguments:
        - event: the Event
        """

        # If the user arrows into the "recent searches" portion of the
        # categories tree, the tree will stop claiming STATE_FOCUSED,
        # but continue to emit active-descendant-changed events. (Doing
        # an equality check seems to be safe here.)
        #
        if not event.source.getState().contains(pyatspi.STATE_FOCUSED) \
           and orca_state.locusOfFocus \
           and orca_state.locusOfFocus.parent != event.source:
            return

        # There can be cases when the object that fires an
        # active-descendant-changed event has no children. In this case,
        # use the object that fired the event, otherwise, use the child.
        #
        child = event.any_data
        if child:
            if self.stopSpeechOnActiveDescendantChanged(event):
                speech.stop()
            orca.setLocusOfFocus(event, child)
        else:
            orca.setLocusOfFocus(event, event.source)

        # We'll tuck away the activeDescendant information for future
        # reference since the AT-SPI gives us little help in finding
        # this.
        #
        if orca_state.locusOfFocus \
           and (orca_state.locusOfFocus != event.source):
            self.pointOfReference['activeDescendantInfo'] = \
                [orca_state.locusOfFocus.parent,
                 orca_state.locusOfFocus.getIndexInParent()]

    def _presentTextAtNewCaretPosition(self, event, otherObj=None):
        """Updates braille, magnification, and outputs speech for the
        event.source or the otherObj. Overridden here to force the braille
        display to be updated when the user arrows left/right into another
        object."""

        default.Script._presentTextAtNewCaretPosition(self, event, otherObj)

        if not self.isSameObject(event.source, self._lastObjectPresented) \
           and self.getAncestor(
            event.source, [pyatspi.ROLE_HTML_CONTAINER], [pyatspi.ROLE_FRAME]):
            self.updateBraille(event.source)

        self._lastObjectPresented = event.source

    def updateBraille(self, obj, extraRegion=None):
        """Updates the braille display to show the given object.

        Arguments:
        - obj: the Accessible
        - extra: extra Region to add to the end
        """

        if not self.getAncestor(
           obj, [pyatspi.ROLE_HTML_CONTAINER], [pyatspi.ROLE_FRAME]):
            return default.Script.updateBraille(self, obj, extraRegion)

        try:
            text = obj.queryText()
        except:
            return default.Script.updateBraille(self, obj, extraRegion)

        braille.clear()
        line = braille.Line()
        braille.addLine(line)

        focusedRegion = None
        contents = self.getLineContentsAtOffset(obj, text.caretOffset)
        for i, content in enumerate(contents):
            child, startOffset, endOffset, string = content
            isFocusedObj = self.isSameObject(child, obj)
            regions = [braille.Text(child,
                                    startOffset=startOffset,
                                    endOffset=endOffset)]

            if isFocusedObj:
                focusedRegion = regions[0]

            line.addRegions(regions)

        if extraRegion:
            line.addRegion(extraRegion)

        braille.setFocus(focusedRegion, getLinkMask=False)
        braille.refresh(panToCursor=True, getLinkMask=False)

    def sayCharacter(self, obj):
        """Speak the character at the caret. Overridden here because the
        event we get when crossing object boundaries is for the object
        being left.

        Arguments:
        - obj: an Accessible object that implements the AccessibleText
               interface
        """

        if not self.getAncestor(
           obj, [pyatspi.ROLE_HTML_CONTAINER], [pyatspi.ROLE_FRAME]):
            return default.Script.sayCharacter(self, obj)

        try:
            text = obj.queryText()
        except:
            return

        if text.caretOffset == text.characterCount \
           and isinstance(orca_state.lastInputEvent,
                          input_event.KeyboardEvent) \
           and orca_state.lastNonModifierKeyEvent.event_string == "Right":
            nextObj = self.getRelationTarget(obj, pyatspi.RELATION_FLOWS_TO)
            if nextObj and nextObj.getRole() == pyatspi.ROLE_TEXT:
                obj = nextObj

        default.Script.sayCharacter(self, obj)

    def sayLine(self, obj):
        """Speaks the line at the current caret position."""

        if not self.getAncestor(
           obj, [pyatspi.ROLE_HTML_CONTAINER], [pyatspi.ROLE_FRAME]):
            return default.Script.sayLine(self, obj)

        try:
            text = obj.queryText()
        except:
            return default.Script.sayLine(self, obj)

        contents = self.getLineContentsAtOffset(obj, text.caretOffset)
        for content in contents:
            child, startOffset, endOffset, line = content
            if len(contents) > 1 and not line.strip():
                continue

            isLink = self.isLink(child)

            if len(line) and line != "\n":
                if line.decode("UTF-8").isupper():
                    voice = self.voices[settings.UPPERCASE_VOICE]
                elif isLink:
                    voice = self.voices[settings.HYPERLINK_VOICE]
                else:
                    voice = self.voices[settings.DEFAULT_VOICE]

                line = self.adjustForRepeats(line)
                speech.speak(line, voice)
                if isLink:
                    speech.speak(self.speechGenerator.getRoleName(
                            child, role=pyatspi.ROLE_LINK))

            else:
                self.sayCharacter(child)

    def getRelationTarget(self, obj, relationType):
        """Gets the target of the specified relation for obj.

        Arguments:
        - obj: the current object
        - relationType: the pyatspi relation type

        Returns the target that relation points to; otherwise, None.
        """

        for relation in obj.getRelationSet():
            if relation.getRelationType() == relationType:
                return relation.getTarget(0)

        return None

    def getLineContentsAtOffset(self, obj, offset):
        """Returns an ordered list where each element is composed of an
        [obj, startOffset, endOffset, string] tuple.  The list is created
        via an in-order traversal of the document contents starting at
        the given object and characterOffset.  The first element in
        the list represents the beginning of the line.  The last
        element in the list represents the character just before the
        beginning of the next line.

        Arguments:
        -obj: the object to start at
        -offset: the character offset in the object
        """

        try:
            text = obj.queryText()
        except:
            return []

        contents = []

        # Get the line contents with respect to this object.
        #
        line = text.getTextAtOffset(offset, pyatspi.TEXT_BOUNDARY_LINE_START)
        contents.append([obj, line[1], line[2], line[0]])

        extents = text.getCharacterExtents(offset, 0)
        index = obj.getIndexInParent()

        # Get the line contents for all objects to the left.
        #
        prevObj = self.getRelationTarget(obj, pyatspi.RELATION_FLOWS_FROM)
        while prevObj:
            try:
                text = prevObj.queryText()
            except:
                break

            line = text.getTextAtOffset(
                text.characterCount - 1, pyatspi.TEXT_BOUNDARY_LINE_START)
            newExtents = text.getCharacterExtents(line[1], 0)
            if extents != newExtents and self.onSameLine(extents, newExtents):
                content = [prevObj, line[1], line[2], line[0]]

                # Sanity check due to some circular FLOWS_TO/FROM relations.
                #
                if contents.count(content):
                    break

                # Sanity check due to gtkhtml2 flat out lying about the value
                # of y.
                #
                if extents[0] <= newExtents[0]:
                    break

                contents[0:0] = [content]
                prevObj = self.getRelationTarget(
                    prevObj, pyatspi.RELATION_FLOWS_FROM)
            else:
                break

        # Get the line contents for all objects to the right.
        #
        nextObj = self.getRelationTarget(obj, pyatspi.RELATION_FLOWS_TO)
        while nextObj:
            try:
                text = nextObj.queryText()
            except:
                break

            line = text.getTextAtOffset(0, pyatspi.TEXT_BOUNDARY_LINE_START)
            newExtents = text.getCharacterExtents(line[1], 0)
            if extents != newExtents and self.onSameLine(extents, newExtents):
                content = [nextObj, line[1], line[2], line[0]]

                # Sanity check due to some circular FLOWS_TO/FROM relations.
                #
                if contents.count(content):
                    break

                # Sanity check due to gtkhtml2 flat out lying about the value
                # of y.
                #
                if extents[0] >= newExtents[0]:
                    break

                contents.append(content)
                nextObj = \
                    self.getRelationTarget(nextObj, pyatspi.RELATION_FLOWS_TO)
            else:
                break

        return contents

    def onSameLine(self, extents1, extents2):
        """Determine if extents1 and extents2 are on the same line.

        Arguments:
        -extents1: [x, y, width, height]
        -extents2: [x, y, width, height]

        Returns True if extents1 and extents2 are on the same line.
        """

        verticalCenter1 = extents1[1] + extents1[3] / 2
        verticalCenter2 = extents2[1] + extents2[3] / 2
        return abs(verticalCenter1 - verticalCenter2) <= 1

    def isLink(self, obj):
        """Returns True if this is a text object serving as a link.

        Arguments:
        - obj: an accessible
        """

        if not obj:
            return False

        # Images seem to be exposed as ROLE_PANEL and implement very few of
        # the accessibility interfaces.
        #
        if obj.getRole() == pyatspi.ROLE_PANEL and not obj.childCount \
           and obj.getState().contains(pyatspi.STATE_FOCUSABLE) \
           and self.getAncestor(obj,
                                [pyatspi.ROLE_HTML_CONTAINER],
                                [pyatspi.ROLE_FRAME]):
            return True

        try:
            text = obj.queryText()
        except:
            return False
        else:
            return self.getLinkIndex(obj, text.caretOffset) >= 0

    def isTextArea(self, obj):
        """Returns True if obj is a GUI component that is for entering text.

        Arguments:
        - obj: an accessible
        """

        if self.isLink(obj):
            return False

        return default.Script.isTextArea(self, obj)

    def isSearchEntry(self, obj):
        """Attempts to distinguish the Search entry from other accessibles.

        Arguments:
        -obj: the accessible being examined

        Returns True if we think obj is the Search entry.
        """

        # The Search entry is the only entry inside a toolbar. If that
        # should change, we'll need to make our criteria more specific.
        #
        if obj and obj.getRole() == pyatspi.ROLE_TEXT \
           and self.getAncestor( \
            obj, [pyatspi.ROLE_TOOL_BAR], [pyatspi.ROLE_FRAME]):
            return True

        return False

    def isPackageListToggle(self, obj):
        """Attempts to identify the toggle-able cell in the package list.

        Arguments:
        -obj: the accessible being examined

        Returns True if we think obj is the toggle-able cell in the package
        list.
        """

        if obj and obj.getRole() == pyatspi.ROLE_TABLE_CELL:
            try:
                action = obj.queryAction()
            except NotImplementedError:
                action = None
            if action:
                for i in range(action.nActions):
                    # Translators: this is the action name for
                    # the 'toggle' action. It must be the same
                    # string used in the *.po file for gail.
                    #
                    if action.getName(i) in ["toggle", _("toggle")]:
                        try:
                            table = obj.parent.queryTable()
                        except:
                            col = -1
                        else:
                            index = self.getCellIndex(obj)
                            col = table.getColumnAtIndex(index)
                        if col == 0:
                            top = self.getTopLevel(obj)
                            if top and top.getRole() == pyatspi.ROLE_FRAME:
                                return True
                        return False

        return False
