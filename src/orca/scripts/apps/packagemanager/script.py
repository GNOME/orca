# Orca
#
# Copyright 2009-2010 Sun Microsystems Inc.
# Copyright 2010 Joanmarie Diggs
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

"""Custom script for Packagemanager."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2009-2010 Sun Microsystems Inc."  \
                "Copyright (c) 2010 Joanmarie Diggs"
__license__   = "LGPL"

from gi.repository import Gtk
import pyatspi

import orca.scripts.default as default
import orca.orca as orca
import orca.orca_state as orca_state
import orca.settings as settings
import orca.speech as speech

from orca.orca_i18n import _

from .braille_generator import BrailleGenerator
from .speech_generator import SpeechGenerator
from .tutorialgenerator import TutorialGenerator
from .script_utilities import Utilities

from . import script_settings

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
        self._presentedStatusBarIcon = False

        # Initialize variable to None to make pylint happy.
        #
        self.presentLoggedErrorsCheckButton = None

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

    def getUtilities(self):
        """Returns the utilites for this script."""

        return Utilities(self)

    def getAppPreferencesGUI(self):
        """Return a GtkGrid containing the application unique configuration
        GUI items for the current application."""

        grid = Gtk.Grid()
        grid.set_border_width(12)

        # Translators: The Package Manager application notifies the
        # user of minor errors by displaying an icon in the status
        # bar and adding them to an error log rather than displaying
        # the error in a dialog box. This string is the label for a
        # checkbox. If it is checked, Orca will inform the user when
        # the notification icon has appeared.
        #
        label = _("Notify me when errors have been logged.")
        value = script_settings.presentLoggedErrors
        self.presentLoggedErrorsCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.presentLoggedErrorsCheckButton.set_active(value)
        grid.attach(self.presentLoggedErrorsCheckButton, 0, 0, 1, 1)

        grid.show_all()

        return grid

    def setAppPreferences(self, prefs):
        """Write out the application specific preferences lines and set the
        new values.

        Arguments:
        - prefs: file handle for application preferences.
        """

        prefs.writelines("\n")
        script_settings.presentLoggedErrors = \
                 self.presentLoggedErrorsCheckButton.get_active()
        prefs.writelines("%s.presentLoggedErrors = %s\n" % \
                         ("orca.scripts.apps.packagemanager.script_settings",
                          script_settings.presentLoggedErrors))

    def locusOfFocusChanged(self, event, oldLocusOfFocus, newLocusOfFocus):
        """Called when the visual object with focus changes.

        Arguments:
        - event: if not None, the Event that caused the change
        - oldLocusOfFocus: Accessible that is the old locus of focus
        - newLocusOfFocus: Accessible that is the new locus of focus
        """

        # Prevent chattiness when arrowing out of or into a link.
        #
        lastKey, mods = self.utilities.lastKeyAndModifiers()
        if lastKey in ["Left", "Right", "Up", "Down"] \
           and event and event.type.startswith("focus:") \
           and (self.utilities.isLink(oldLocusOfFocus) \
           or self.utilities.isLink(newLocusOfFocus)):
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
           and self.utilities.ancestorWithRole(
            event.source, [pyatspi.ROLE_HTML_CONTAINER], [pyatspi.ROLE_FRAME]):
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
                msg = _("Loading.  Please wait.")
                speech.speak(msg)
                self.displayBrailleMessage(
                    msg, flashTime=settings.brailleFlashTime)
                self._isBusy = True
            elif event.detail1 == 0 and self._isBusy:
                # Translators: this is in reference to loading a web page
                # or some other content.
                #
                msg = _("Finished loading.")
                speech.speak(msg)
                self.displayBrailleMessage(
                    msg, flashTime=settings.brailleFlashTime)
                self._isBusy = False
            return

        if script_settings.presentLoggedErrors \
           and not self._presentedStatusBarIcon \
           and event.source.getRole() == pyatspi.ROLE_PANEL \
           and event.type.startswith("object:state-changed:showing") \
           and event.detail1:
            obj = self.findStatusBarIcon()
            while obj and not self.utilities.isSameObject(obj, event.source):
                obj = obj.parent
            if obj:
                # Translators: The Package Manager application notifies the
                # user of minor errors by displaying an icon in the status
                # bar and adding them to an error log rather than displaying
                # the error in a dialog box. This is the message Orca will
                # present to inform the user that this has occurred.
                #
                msg = _("An error occurred. View the error log for details.")
                speech.speak(msg)
                self.displayBrailleMessage(
                    msg, flashTime=settings.brailleFlashTime)
                self._presentedStatusBarIcon = True

        default.Script.onStateChanged(self, event)

    def onWindowActivated(self, event):
        """Called whenever a toplevel window is activated.

        Arguments:
        - event: the Event
        """

        if self._presentedStatusBarIcon and not self.findStatusBarIcon():
            self._presentedStatusBarIcon = False

        default.Script.onWindowActivated(self, event)

    def findStatusBarIcon(self, statusBar=None):
        """Locates the icon which is sometimes found to the left of the
        packagemanager status bar.

        Arguments:
        - statusBar: packagemanager's status bar

        Returns the accessible for the icon if the icon is found and
        showing.
        """

        icon = None
        if not statusBar and self.app.childCount:
            # Be sure we're looking in PM's main window.
            #
            statusBar = self.utilities.statusBar(self.app[0])

        if statusBar:
            i = statusBar.getIndexInParent()
            if i > 0:
                icons = self.utilities.descendantsWithRole(
                    statusBar.parent[i - 1], pyatspi.ROLE_ICON)
                if icons:
                    icon = icons[0]

        return icon

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
        """Updates braille and outputs speech for the event.source or the
        otherObj. Overridden here to force the braille display to be updated
        when the user arrows left/right into another object."""

        default.Script._presentTextAtNewCaretPosition(self, event, otherObj)

        if not self.utilities.isSameObject(
            event.source, self._lastObjectPresented) \
           and self.utilities.ancestorWithRole(
            event.source, [pyatspi.ROLE_HTML_CONTAINER], [pyatspi.ROLE_FRAME]):
            self.updateBraille(event.source)

        self._lastObjectPresented = event.source

    def updateBraille(self, obj, extraRegion=None):
        """Updates the braille display to show the given object.

        Arguments:
        - obj: the Accessible
        - extra: extra Region to add to the end
        """

        if not self.utilities.ancestorWithRole(
           obj, [pyatspi.ROLE_HTML_CONTAINER], [pyatspi.ROLE_FRAME]):
            return default.Script.updateBraille(self, obj, extraRegion)

        try:
            text = obj.queryText()
        except:
            return default.Script.updateBraille(self, obj, extraRegion)

        line = self.getNewBrailleLine(clearBraille=True, addLine=True)
        focusedRegion = None
        contents = self.getLineContentsAtOffset(obj, text.caretOffset)
        for i, content in enumerate(contents):
            child, startOffset, endOffset, string = content
            isFocusedObj = self.utilities.isSameObject(child, obj)
            regions = [self.getNewBrailleText(child,
                                              startOffset=startOffset,
                                              endOffset=endOffset)]
            if isFocusedObj:
                focusedRegion = regions[0]

            self.addBrailleRegionsToLine(regions, line)

        if extraRegion:
            self.addBrailleRegionToLine(extraRegion, line)

        self.setBrailleFocus(focusedRegion, getLinkMask=False)
        self.refreshBraille(panToCursor=True, getLinkMask=False)

    def sayCharacter(self, obj):
        """Speak the character at the caret. Overridden here because the
        event we get when crossing object boundaries is for the object
        being left.

        Arguments:
        - obj: an Accessible object that implements the AccessibleText
               interface
        """

        if not self.utilities.ancestorWithRole(
           obj, [pyatspi.ROLE_HTML_CONTAINER], [pyatspi.ROLE_FRAME]):
            return default.Script.sayCharacter(self, obj)

        try:
            text = obj.queryText()
        except:
            return

        lastKey, mods = self.utilities.lastKeyAndModifiers()
        if text.caretOffset == text.characterCount and lastKey == "Right":
            nextObj = self.getRelationTarget(obj, pyatspi.RELATION_FLOWS_TO)
            if nextObj and nextObj.getRole() == pyatspi.ROLE_TEXT:
                obj = nextObj

        default.Script.sayCharacter(self, obj)

    def sayLine(self, obj):
        """Speaks the line at the current caret position."""

        if not self.utilities.ancestorWithRole(
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

            isLink = self.utilities.isLink(child)

            if len(line) and line != "\n":
                if line.decode("UTF-8").isupper():
                    voice = self.voices[settings.UPPERCASE_VOICE]
                elif isLink:
                    voice = self.voices[settings.HYPERLINK_VOICE]
                else:
                    voice = self.voices[settings.DEFAULT_VOICE]

                line = self.utilities.adjustForRepeats(line)
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
        return abs(verticalCenter1 - verticalCenter2) <= 5

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
           and self.utilities.ancestorWithRole(
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
                            index = self.utilities.cellIndex(obj)
                            col = table.getColumnAtIndex(index)
                        if col == 0:
                            top = self.utilities.topLevelObject(obj)
                            if top and top.getRole() == pyatspi.ROLE_FRAME:
                                return True
                        return False

        return False
