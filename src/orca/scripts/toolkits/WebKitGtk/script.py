# Orca
#
# Copyright (C) 2010-2011 The Orca Team
# Copyright (C) 2011-2012 Igalia, S.L.
#
# Author: Joanmarie Diggs <jdiggs@igalia.com>
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

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (C) 2010-2011 The Orca Team" \
                "Copyright (C) 2011-2012 Igalia, S.L."
__license__   = "LGPL"

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

import orca.scripts.default as default
import orca.cmdnames as cmdnames
import orca.debug as debug
import orca.focus_manager as focus_manager
import orca.input_event_manager as input_event_manager
import orca.guilabels as guilabels
import orca.input_event as input_event
import orca.messages as messages
import orca.settings as settings
import orca.settings_manager as settings_manager
import orca.speech as speech
import orca.structural_navigation as structural_navigation

from orca.ax_component import AXComponent
from orca.ax_object import AXObject
from orca.ax_utilities import AXUtilities

from .braille_generator import BrailleGenerator
from .speech_generator import SpeechGenerator
from .script_utilities import Utilities

########################################################################
#                                                                      #
# The WebKitGtk script class.                                          #
#                                                                      #
########################################################################

class Script(default.Script):

    def __init__(self, app):
        """Creates a new script for WebKitGtk applications.

        Arguments:
        - app: the application to create a script for.
        """

        super().__init__(app)
        self._loadingDocumentContent = False
        self._lastCaretContext = None, -1
        self.sayAllOnLoadCheckButton = None

        if settings_manager.getManager().getSetting('sayAllOnLoad') is None:
            settings_manager.getManager().setSetting('sayAllOnLoad', True)

    def setupInputEventHandlers(self):
        """Defines InputEventHandler fields for this script that can be
        called by the key and braille bindings."""

        default.Script.setupInputEventHandlers(self)
        self.inputEventHandlers.update(self.structuralNavigation.get_handlers(True))

        self.inputEventHandlers["panBrailleLeftHandler"] = \
            input_event.InputEventHandler(
                Script.panBrailleLeft,
                cmdnames.PAN_BRAILLE_LEFT,
                False) # Do not enable learn mode for this action

        self.inputEventHandlers["panBrailleRightHandler"] = \
            input_event.InputEventHandler(
                Script.panBrailleRight,
                cmdnames.PAN_BRAILLE_RIGHT,
                False) # Do not enable learn mode for this action

    def getToolkitKeyBindings(self):
        """Returns the toolkit-specific keybindings for this script."""

        layout = settings_manager.getManager().getSetting('keyboardLayout')
        isDesktop = layout == settings.GENERAL_KEYBOARD_LAYOUT_DESKTOP
        return self.structuralNavigation.get_bindings(refresh=True, is_desktop=isDesktop)

    def getAppPreferencesGUI(self):
        """Return a GtkGrid containing the application unique configuration
        GUI items for the current application."""

        from gi.repository import Gtk

        grid = Gtk.Grid()
        grid.set_border_width(12)

        label = guilabels.READ_PAGE_UPON_LOAD
        self.sayAllOnLoadCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.sayAllOnLoadCheckButton.set_active(
            settings_manager.getManager().getSetting('sayAllOnLoad'))
        grid.attach(self.sayAllOnLoadCheckButton, 0, 0, 1, 1)

        grid.show_all()

        return grid

    def getPreferencesFromGUI(self):
        """Returns a dictionary with the app-specific preferences."""

        return {'sayAllOnLoad': self.sayAllOnLoadCheckButton.get_active()}

    def getBrailleGenerator(self):
        """Returns the braille generator for this script."""

        return BrailleGenerator(self)

    def getSpeechGenerator(self):
        """Returns the speech generator for this script."""

        return SpeechGenerator(self)

    def getEnabledStructuralNavigationTypes(self):
        """Returns a list of the structural navigation object types
        enabled in this script."""

        return [structural_navigation.StructuralNavigation.BLOCKQUOTE,
                structural_navigation.StructuralNavigation.BUTTON,
                structural_navigation.StructuralNavigation.CHECK_BOX,
                structural_navigation.StructuralNavigation.CHUNK,
                structural_navigation.StructuralNavigation.CLICKABLE,
                structural_navigation.StructuralNavigation.COMBO_BOX,
                structural_navigation.StructuralNavigation.CONTAINER,
                structural_navigation.StructuralNavigation.ENTRY,
                structural_navigation.StructuralNavigation.FORM_FIELD,
                structural_navigation.StructuralNavigation.HEADING,
                structural_navigation.StructuralNavigation.IFRAME,
                structural_navigation.StructuralNavigation.IMAGE,
                structural_navigation.StructuralNavigation.LANDMARK,
                structural_navigation.StructuralNavigation.LINK,
                structural_navigation.StructuralNavigation.LIST,
                structural_navigation.StructuralNavigation.LIST_ITEM,
                structural_navigation.StructuralNavigation.LIVE_REGION,
                structural_navigation.StructuralNavigation.PARAGRAPH,
                structural_navigation.StructuralNavigation.RADIO_BUTTON,
                structural_navigation.StructuralNavigation.SEPARATOR,
                structural_navigation.StructuralNavigation.TABLE,
                structural_navigation.StructuralNavigation.UNVISITED_LINK,
                structural_navigation.StructuralNavigation.VISITED_LINK]

    def getUtilities(self):
        """Returns the utilities for this script."""

        return Utilities(self)

    def onCaretMoved(self, event):
        """Callback for object:text-caret-moved accessibility events."""

        if self._inSayAll:
            return

        if not self.utilities.isWebKitGtk(event.source):
            super().onCaretMoved(event)
            return

        manager = input_event_manager.getManager()
        if manager.last_event_was_tab_navigation():
            return

        focus = focus_manager.getManager().get_locus_of_focus()
        if manager.last_event_was_down() \
           and AXObject.get_index_in_parent(event.source) == 0 \
           and focus == AXObject.get_parent(event.source) \
           and AXUtilities.is_link(focus):
            self.updateBraille(event.source)
            return

        self.utilities.setCaretContext(event.source, event.detail1)
        super().onCaretMoved(event)

    def onDocumentReload(self, event):
        """Callback for document:reload accessibility events."""

        if self.utilities.treatAsBrowser(event.source):
            self._loadingDocumentContent = True

    def onDocumentLoadComplete(self, event):
        """Callback for document:load-complete accessibility events."""

        if not self.utilities.treatAsBrowser(event.source):
            return

        self._loadingDocumentContent = False

        # TODO: We need to see what happens in Epiphany on pages where focus
        # is grabbed rather than set the caret at the start. But for simple
        # content in both Yelp and Epiphany this is alright for now.
        obj, offset = self.utilities.setCaretAtStart(event.source)
        self.utilities.setCaretContext(obj, offset)

        self.updateBraille(obj)
        if settings_manager.getManager().getSetting('sayAllOnLoad') \
           and settings_manager.getManager().getSetting('enableSpeech'):
            self.sayAll(None)

    def onDocumentLoadStopped(self, event):
        """Callback for document:load-stopped accessibility events."""

        if self.utilities.treatAsBrowser(event.source):
            self._loadingDocumentContent = False

    def onFocusedChanged(self, event):
        """Callback for object:state-changed:focused accessibility events."""

        if self._inSayAll or not event.detail1:
            return

        if not self.utilities.isWebKitGtk(event.source):
            super().onFocusedChanged(event)
            return

        contextObj, offset = self.utilities.getCaretContext()
        if event.source == contextObj:
            return

        obj = event.source
        role = AXObject.get_role(obj)
        textRoles = [Atspi.Role.HEADING,
                     Atspi.Role.PANEL,
                     Atspi.Role.PARAGRAPH,
                     Atspi.Role.SECTION,
                     Atspi.Role.TABLE_CELL]
        if role in textRoles \
           or (role == Atspi.Role.LIST_ITEM and AXObject.get_child_count(obj)):
            return

        super().onFocusedChanged(event)

    def onBusyChanged(self, event):
        """Callback for object:state-changed:busy accessibility events."""

        if not self.utilities.treatAsBrowser(event.source):
            return

        if event.detail1:
            self.presentMessage(messages.PAGE_LOADING_START)
            return

        name = AXObject.get_name(event.source)
        if name:
            self.presentMessage(messages.PAGE_LOADING_END_NAMED % name)
        else:
            self.presentMessage(messages.PAGE_LOADING_END)

    def sayCharacter(self, obj):
        """Speak the character at the caret.

        Arguments:
        - obj: an Accessible object that implements the AccessibleText interface
        """

        if AXUtilities.is_entry(obj):
            default.Script.sayCharacter(self, obj)
            return

        boundary = Atspi.TextBoundaryType.CHAR
        objects = self.utilities.getObjectsFromEOCs(obj, boundary=boundary)
        for (obj, start, end, string) in objects:
            if string:
                self.speakCharacter(string)
            else:
                speech.speak(self.speechGenerator.generateSpeech(obj))

        self.pointOfReference["lastTextUnitSpoken"] = "char"

    def sayWord(self, obj):
        """Speaks the word at the caret.

        Arguments:
        - obj: an Accessible object that implements the AccessibleText interface
        """

        if AXUtilities.is_entry(obj):
            default.Script.sayWord(self, obj)
            return

        boundary = Atspi.TextBoundaryType.WORD_START
        objects = self.utilities.getObjectsFromEOCs(obj, boundary=boundary)
        for (obj, start, end, string) in objects:
            self.sayPhrase(obj, start, end)

        self.pointOfReference["lastTextUnitSpoken"] = "word"

    def sayLine(self, obj):
        """Speaks the line at the caret.

        Arguments:
        - obj: an Accessible object that implements the AccessibleText interface
        """

        if AXUtilities.is_entry(obj):
            default.Script.sayLine(self, obj)
            return

        boundary = Atspi.TextBoundaryType.LINE_START
        objects = self.utilities.getObjectsFromEOCs(obj, boundary=boundary)
        for (obj, start, end, string) in objects:
            self.sayPhrase(obj, start, end)

            # TODO: Move these next items into the speech generator.
            if AXUtilities.is_panel(obj) and AXObject.get_index_in_parent(obj) == 0:
                obj = AXObject.get_parent(obj)

            rolesToSpeak = [Atspi.Role.HEADING, Atspi.Role.LINK]
            if AXObject.get_role(obj) in rolesToSpeak:
                speech.speak(self.speechGenerator.getRoleName(obj))

        self.pointOfReference["lastTextUnitSpoken"] = "line"

    def sayPhrase(self, obj, startOffset, endOffset):
        """Speaks the text of an Accessible object between the given offsets.

        Arguments:
        - obj: an Accessible object that implements the AccessibleText interface
        - startOffset: the start text offset.
        - endOffset: the end text offset.
        """

        if AXUtilities.is_entry(obj):
            default.Script.sayPhrase(self, obj, startOffset, endOffset)
            return

        phrase = self.utilities.substring(obj, startOffset, endOffset)
        if len(phrase) and phrase != "\n":
            voice = self.speechGenerator.voice(obj=obj, string=phrase)
            phrase = self.utilities.adjustForRepeats(phrase)
            links = [x for x in AXObject.iter_children(obj, AXUtilities.is_link)]
            if links:
                phrase = self.utilities.adjustForLinks(obj, phrase, startOffset)
            speech.speak(phrase, voice)
        else:
            # Speak blank line if appropriate.
            #
            self.sayCharacter(obj)

        self.pointOfReference["lastTextUnitSpoken"] = "phrase"

    def skipObjectEvent(self, event):
        """Gives us, and scripts, the ability to decide an event isn't
        worth taking the time to process under the current circumstances.

        Arguments:
        - event: the Event

        Returns True if we shouldn't bother processing this object event.
        """

        if event.type.startswith('object:state-changed:focused') and event.detail1 \
           and AXUtilities.is_link(event.source):
                return False

        return default.Script.skipObjectEvent(self, event)

    def panBrailleLeft(self, inputEvent=None, panAmount=0):
        """In document content, we want to use the panning keys to browse the
        entire document.
        """

        focus = focus_manager.getManager().get_locus_of_focus()
        if self.flatReviewPresenter.is_active() \
           or not self.isBrailleBeginningShowing() \
           or not self.utilities.isWebKitGtk(focus):
            return default.Script.panBrailleLeft(self, inputEvent, panAmount)

        obj = self.utilities.findPreviousObject(focus)
        focus_manager.getManager().set_locus_of_focus(None, obj, notify_script=False)
        self.updateBraille(obj)

        # Hack: When panning to the left in a document, we want to start at
        # the right/bottom of each new object. For now, we'll pan there.
        # When time permits, we'll give our braille code some smarts.
        while self.panBrailleInDirection(panToLeft=False):
            pass
        self.refreshBraille(False)

        return True

    def panBrailleRight(self, inputEvent=None, panAmount=0):
        """In document content, we want to use the panning keys to browse the
        entire document.
        """

        focus = focus_manager.getManager().get_locus_of_focus()
        if self.flatReviewPresenter.is_active() \
           or not self.isBrailleEndShowing() \
           or not self.utilities.isWebKitGtk(focus):
            return default.Script.panBrailleRight(self, inputEvent, panAmount)

        obj = self.utilities.findNextObject(focus)
        focus_manager.getManager().set_locus_of_focus(None, obj, notify_script=False)
        self.updateBraille(obj)

        # Hack: When panning to the right in a document, we want to start at
        # the left/top of each new object. For now, we'll pan there. When time
        # permits, we'll give our braille code some smarts.
        while self.panBrailleInDirection(panToLeft=True):
            pass
        self.refreshBraille(False)

        return True

    def updateBraille(self, obj, **args):
        """Updates the braille display to show the given object.

        Arguments:
        - obj: the Accessible
        """

        if not settings_manager.getManager().getSetting('enableBraille') \
           and not settings_manager.getManager().getSetting('enableBrailleMonitor'):
            debug.printMessage(debug.LEVEL_INFO, "BRAILLE: update disabled", True)
            return

        if not obj:
            return

        if not self.utilities.isWebKitGtk(obj) \
           or (not self.utilities.isInlineContainer(obj) \
               and not self.utilities.isTextListItem(obj)):
            default.Script.updateBraille(self, obj, **args)
            return

        brailleLine = self.getNewBrailleLine(clearBraille=True, addLine=True)
        for child in AXObject.iter_children(obj):
            if not AXComponent.on_same_line(child, AXObject.get_child(obj, 0)):
                break
            [regions, fRegion] = self.brailleGenerator.generateBraille(child)
            self.addBrailleRegionsToLine(regions, brailleLine)

        if not brailleLine.regions:
            [regions, fRegion] = self.brailleGenerator.generateBraille(
                obj, role=Atspi.Role.PARAGRAPH)
            self.addBrailleRegionsToLine(regions, brailleLine)
            self.setBrailleFocus(fRegion)

        extraRegion = args.get('extraRegion')
        if extraRegion:
            self.addBrailleRegionToLine(extraRegion, brailleLine)

        self.refreshBraille()
