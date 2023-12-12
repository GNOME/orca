# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
# Copyright 2010 Orca Team.
# Copyright 2014-2015 Igalia, S.L.
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
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc." \
                "Copyright (c) 2010 Orca Team." \
                "Copyright (c) 2014-2015 Igalia, S.L."
__license__   = "LGPL"

import time
from gi.repository import Gtk

from orca import caret_navigation
from orca import cmdnames
from orca import keybindings
from orca import debug
from orca import focus_manager
from orca import guilabels
from orca import input_event
from orca import liveregions
from orca import messages
from orca import orca_state
from orca import settings
from orca import settings_manager
from orca import speech
from orca import speechserver
from orca import structural_navigation
from orca.acss import ACSS
from orca.scripts import default
from orca.ax_object import AXObject
from orca.ax_table import AXTable
from orca.ax_utilities import AXUtilities

from .bookmarks import Bookmarks
from .braille_generator import BrailleGenerator
from .sound_generator import SoundGenerator
from .speech_generator import SpeechGenerator
from .tutorial_generator import TutorialGenerator
from .script_utilities import Utilities


class Script(default.Script):

    def __init__(self, app):
        super().__init__(app)

        self._sayAllContents = []
        self._inSayAll = False
        self._sayAllIsInterrupted = False
        self._loadingDocumentContent = False
        self._madeFindAnnouncement = False
        self._lastMouseButtonContext = None, -1
        self._lastMouseOverObject = None
        self._preMouseOverContext = None, -1
        self._inMouseOverObject = False
        self._inFocusMode = False
        self._focusModeIsSticky = False
        self._browseModeIsSticky = False

        if settings_manager.getManager().getSetting('caretNavigationEnabled') is None:
            settings_manager.getManager().setSetting('caretNavigationEnabled', True)
        if settings_manager.getManager().getSetting('sayAllOnLoad') is None:
            settings_manager.getManager().setSetting('sayAllOnLoad', True)
        if settings_manager.getManager().getSetting('pageSummaryOnLoad') is None:
            settings_manager.getManager().setSetting('pageSummaryOnLoad', True)

        self._changedLinesOnlyCheckButton = None
        self._controlCaretNavigationCheckButton = None
        self._minimumFindLengthAdjustment = None
        self._minimumFindLengthLabel = None
        self._minimumFindLengthSpinButton = None
        self._pageSummaryOnLoadCheckButton = None
        self._sayAllOnLoadCheckButton = None
        self._skipBlankCellsCheckButton = None
        self._speakCellCoordinatesCheckButton = None
        self._speakCellHeadersCheckButton = None
        self._speakCellSpanCheckButton = None
        self._speakResultsDuringFindCheckButton = None
        self._structuralNavigationCheckButton = None
        self._autoFocusModeStructNavCheckButton = None
        self._autoFocusModeCaretNavCheckButton = None
        self._autoFocusModeNativeNavCheckButton = None
        self._layoutModeCheckButton = None

        self.attributeNamesDict["invalid"] = "text-spelling"
        self.attributeNamesDict["text-align"] = "justification"
        self.attributeNamesDict["text-indent"] = "indent"

    def deactivate(self):
        """Called when this script is deactivated."""

        self._sayAllContents = []
        self._inSayAll = False
        self._sayAllIsInterrupted = False
        self._loadingDocumentContent = False
        self._madeFindAnnouncement = False
        self._lastMouseButtonContext = None, -1
        self._lastMouseOverObject = None
        self._preMouseOverContext = None, -1
        self._inMouseOverObject = False
        self.utilities.clearCachedObjects()
        self.removeKeyGrabs("script deactivation")

    def getAppKeyBindings(self):
        """Returns the application-specific keybindings for this script."""

        keyBindings = keybindings.KeyBindings()

        layout = settings_manager.getManager().getSetting('keyboardLayout')
        isDesktop = layout == settings.GENERAL_KEYBOARD_LAYOUT_DESKTOP

        structNavBindings = self.structuralNavigation.get_bindings(
            refresh=True, is_desktop=isDesktop)
        for keyBinding in structNavBindings.keyBindings:
            keyBindings.add(keyBinding)

        caretNavBindings = self.caretNavigation.get_bindings(
            refresh=True, is_desktop=isDesktop)
        for keyBinding in caretNavBindings.keyBindings:
            keyBindings.add(keyBinding)

        liveRegionBindings = self.liveRegionManager.get_bindings(
            refresh=True, is_desktop=isDesktop)
        for keyBinding in liveRegionBindings.keyBindings:
            keyBindings.add(keyBinding)

        keyBindings.add(
            keybindings.KeyBinding(
                "a",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers.get("togglePresentationModeHandler")))

        keyBindings.add(
            keybindings.KeyBinding(
                "a",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers.get("enableStickyFocusModeHandler"),
                2))

        keyBindings.add(
            keybindings.KeyBinding(
                "a",
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers.get("enableStickyBrowseModeHandler"),
                3))

        keyBindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.defaultModifierMask,
                keybindings.NO_MODIFIER_MASK,
                self.inputEventHandlers.get("toggleLayoutModeHandler")))


        layout = settings_manager.getManager().getSetting('keyboardLayout')
        if layout == settings.GENERAL_KEYBOARD_LAYOUT_DESKTOP:
            key = "KP_Multiply"
        else:
            key = "0"

        keyBindings.add(
            keybindings.KeyBinding(
                key,
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers.get("moveToMouseOverHandler")))

        return keyBindings

    def setupInputEventHandlers(self):
        """Defines InputEventHandlers for this script."""

        super().setupInputEventHandlers()
        self.inputEventHandlers.update(self.structuralNavigation.get_handlers(True))
        self.inputEventHandlers.update(self.caretNavigation.get_handlers(True))
        self.inputEventHandlers.update(self.liveRegionManager.get_handlers(True))

        self.inputEventHandlers["sayAllHandler"] = \
            input_event.InputEventHandler(
                Script.sayAll,
                cmdnames.SAY_ALL)

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

        self.inputEventHandlers["moveToMouseOverHandler"] = \
            input_event.InputEventHandler(
                Script.moveToMouseOver,
                cmdnames.MOUSE_OVER_MOVE)

        self.inputEventHandlers["togglePresentationModeHandler"] = \
            input_event.InputEventHandler(
                Script.togglePresentationMode,
                cmdnames.TOGGLE_PRESENTATION_MODE)

        self.inputEventHandlers["enableStickyFocusModeHandler"] = \
            input_event.InputEventHandler(
                Script.enableStickyFocusMode,
                cmdnames.SET_FOCUS_MODE_STICKY)

        self.inputEventHandlers["enableStickyBrowseModeHandler"] = \
            input_event.InputEventHandler(
                Script.enableStickyBrowseMode,
                cmdnames.SET_BROWSE_MODE_STICKY)

        self.inputEventHandlers["toggleLayoutModeHandler"] = \
            input_event.InputEventHandler(
                Script.toggleLayoutMode,
                cmdnames.TOGGLE_LAYOUT_MODE)

    def getBookmarks(self):
        """Returns the "bookmarks" class for this script."""

        try:
            return self.bookmarks
        except AttributeError:
            self.bookmarks = Bookmarks(self)
            return self.bookmarks

    def getBrailleGenerator(self):
        """Returns the braille generator for this script."""

        return BrailleGenerator(self)

    def getCaretNavigation(self):
        """Returns the caret navigation support for this script."""

        return caret_navigation.CaretNavigation(self)

    def getEnabledStructuralNavigationTypes(self):
        """Returns the structural navigation object types for this script."""

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
                structural_navigation.StructuralNavigation.TABLE_CELL,
                structural_navigation.StructuralNavigation.UNVISITED_LINK,
                structural_navigation.StructuralNavigation.VISITED_LINK]

    def getLiveRegionManager(self):
        """Returns the live region support for this script."""

        return liveregions.LiveRegionManager(self)

    def getSoundGenerator(self):
        """Returns the sound generator for this script."""

        return SoundGenerator(self)

    def getSpeechGenerator(self):
        """Returns the speech generator for this script."""

        return SpeechGenerator(self)

    def getTutorialGenerator(self):
        """Returns the tutorial generator for this script."""

        return TutorialGenerator(self)

    def getUtilities(self):
        """Returns the utilities for this script."""

        return Utilities(self)

    def getAppPreferencesGUI(self):
        """Return a GtkGrid containing app-unique configuration items."""

        grid = Gtk.Grid()
        grid.set_border_width(12)

        generalFrame = Gtk.Frame()
        grid.attach(generalFrame, 0, 0, 1, 1)

        label = Gtk.Label(label=f"<b>{guilabels.PAGE_NAVIGATION}</b>")
        label.set_use_markup(True)
        generalFrame.set_label_widget(label)

        generalAlignment = Gtk.Alignment.new(0.5, 0.5, 1, 1)
        generalAlignment.set_padding(0, 0, 12, 0)
        generalFrame.add(generalAlignment)
        generalGrid = Gtk.Grid()
        generalAlignment.add(generalGrid)

        label = guilabels.USE_CARET_NAVIGATION
        value = settings_manager.getManager().getSetting('caretNavigationEnabled')
        self._controlCaretNavigationCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self._controlCaretNavigationCheckButton.set_active(value)
        generalGrid.attach(self._controlCaretNavigationCheckButton, 0, 0, 1, 1)

        label = guilabels.AUTO_FOCUS_MODE_CARET_NAV
        value = settings_manager.getManager().getSetting('caretNavTriggersFocusMode')
        self._autoFocusModeCaretNavCheckButton = Gtk.CheckButton.new_with_mnemonic(label)
        self._autoFocusModeCaretNavCheckButton.set_active(value)
        generalGrid.attach(self._autoFocusModeCaretNavCheckButton, 0, 1, 1, 1)

        label = guilabels.USE_STRUCTURAL_NAVIGATION
        value = self.structuralNavigation.enabled
        self._structuralNavigationCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self._structuralNavigationCheckButton.set_active(value)
        generalGrid.attach(self._structuralNavigationCheckButton, 0, 2, 1, 1)

        label = guilabels.AUTO_FOCUS_MODE_STRUCT_NAV
        value = settings_manager.getManager().getSetting('structNavTriggersFocusMode')
        self._autoFocusModeStructNavCheckButton = Gtk.CheckButton.new_with_mnemonic(label)
        self._autoFocusModeStructNavCheckButton.set_active(value)
        generalGrid.attach(self._autoFocusModeStructNavCheckButton, 0, 3, 1, 1)

        label = guilabels.AUTO_FOCUS_MODE_NATIVE_NAV
        value = settings_manager.getManager().getSetting('nativeNavTriggersFocusMode')
        self._autoFocusModeNativeNavCheckButton = Gtk.CheckButton.new_with_mnemonic(label)
        self._autoFocusModeNativeNavCheckButton.set_active(value)
        generalGrid.attach(self._autoFocusModeNativeNavCheckButton, 0, 4, 1, 1)

        label = guilabels.READ_PAGE_UPON_LOAD
        value = settings_manager.getManager().getSetting('sayAllOnLoad')
        self._sayAllOnLoadCheckButton = Gtk.CheckButton.new_with_mnemonic(label)
        self._sayAllOnLoadCheckButton.set_active(value)
        generalGrid.attach(self._sayAllOnLoadCheckButton, 0, 5, 1, 1)

        label = guilabels.PAGE_SUMMARY_UPON_LOAD
        value = settings_manager.getManager().getSetting('pageSummaryOnLoad')
        self._pageSummaryOnLoadCheckButton = Gtk.CheckButton.new_with_mnemonic(label)
        self._pageSummaryOnLoadCheckButton.set_active(value)
        generalGrid.attach(self._pageSummaryOnLoadCheckButton, 0, 6, 1, 1)

        label = guilabels.CONTENT_LAYOUT_MODE
        value = settings_manager.getManager().getSetting('layoutMode')
        self._layoutModeCheckButton = Gtk.CheckButton.new_with_mnemonic(label)
        self._layoutModeCheckButton.set_active(value)
        generalGrid.attach(self._layoutModeCheckButton, 0, 7, 1, 1)

        tableFrame = Gtk.Frame()
        grid.attach(tableFrame, 0, 1, 1, 1)

        label = Gtk.Label(label=f"<b>{guilabels.TABLE_NAVIGATION}</b>")
        label.set_use_markup(True)
        tableFrame.set_label_widget(label)

        tableAlignment = Gtk.Alignment.new(0.5, 0.5, 1, 1)
        tableAlignment.set_padding(0, 0, 12, 0)
        tableFrame.add(tableAlignment)
        tableGrid = Gtk.Grid()
        tableAlignment.add(tableGrid)

        label = guilabels.TABLE_SPEAK_CELL_COORDINATES
        value = settings_manager.getManager().getSetting('speakCellCoordinates')
        self._speakCellCoordinatesCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self._speakCellCoordinatesCheckButton.set_active(value)
        tableGrid.attach(self._speakCellCoordinatesCheckButton, 0, 0, 1, 1)

        label = guilabels.TABLE_SPEAK_CELL_SPANS
        value = settings_manager.getManager().getSetting('speakCellSpan')
        self._speakCellSpanCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self._speakCellSpanCheckButton.set_active(value)
        tableGrid.attach(self._speakCellSpanCheckButton, 0, 1, 1, 1)

        label = guilabels.TABLE_ANNOUNCE_CELL_HEADER
        value = settings_manager.getManager().getSetting('speakCellHeaders')
        self._speakCellHeadersCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self._speakCellHeadersCheckButton.set_active(value)
        tableGrid.attach(self._speakCellHeadersCheckButton, 0, 2, 1, 1)

        label = guilabels.TABLE_SKIP_BLANK_CELLS
        value = settings_manager.getManager().getSetting('skipBlankCells')
        self._skipBlankCellsCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self._skipBlankCellsCheckButton.set_active(value)
        tableGrid.attach(self._skipBlankCellsCheckButton, 0, 3, 1, 1)

        findFrame = Gtk.Frame()
        grid.attach(findFrame, 0, 2, 1, 1)

        label = Gtk.Label(label=f"<b>{guilabels.FIND_OPTIONS}</b>")
        label.set_use_markup(True)
        findFrame.set_label_widget(label)

        findAlignment = Gtk.Alignment.new(0.5, 0.5, 1, 1)
        findAlignment.set_padding(0, 0, 12, 0)
        findFrame.add(findAlignment)
        findGrid = Gtk.Grid()
        findAlignment.add(findGrid)

        verbosity = settings_manager.getManager().getSetting('findResultsVerbosity')

        label = guilabels.FIND_SPEAK_RESULTS
        value = verbosity != settings.FIND_SPEAK_NONE
        self._speakResultsDuringFindCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self._speakResultsDuringFindCheckButton.set_active(value)
        findGrid.attach(self._speakResultsDuringFindCheckButton, 0, 0, 1, 1)

        label = guilabels.FIND_ONLY_SPEAK_CHANGED_LINES
        value = verbosity == settings.FIND_SPEAK_IF_LINE_CHANGED
        self._changedLinesOnlyCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self._changedLinesOnlyCheckButton.set_active(value)
        findGrid.attach(self._changedLinesOnlyCheckButton, 0, 1, 1, 1)

        hgrid = Gtk.Grid()
        findGrid.attach(hgrid, 0, 2, 1, 1)

        self._minimumFindLengthLabel = \
              Gtk.Label(label=guilabels.FIND_MINIMUM_MATCH_LENGTH)
        self._minimumFindLengthLabel.set_alignment(0, 0.5)
        hgrid.attach(self._minimumFindLengthLabel, 0, 0, 1, 1)

        self._minimumFindLengthAdjustment = \
            Gtk.Adjustment(settings_manager.getManager().getSetting(
                'findResultsMinimumLength'), 0, 20, 1)
        self._minimumFindLengthSpinButton = Gtk.SpinButton()
        self._minimumFindLengthSpinButton.set_adjustment(
            self._minimumFindLengthAdjustment)
        hgrid.attach(self._minimumFindLengthSpinButton, 1, 0, 1, 1)
        self._minimumFindLengthLabel.set_mnemonic_widget(
            self._minimumFindLengthSpinButton)

        grid.show_all()
        return grid

    def getPreferencesFromGUI(self):
        """Returns a dictionary with the app-specific preferences."""

        if not self._speakResultsDuringFindCheckButton.get_active():
            verbosity = settings.FIND_SPEAK_NONE
        elif self._changedLinesOnlyCheckButton.get_active():
            verbosity = settings.FIND_SPEAK_IF_LINE_CHANGED
        else:
            verbosity = settings.FIND_SPEAK_ALL

        return {
            'findResultsVerbosity': verbosity,
            'findResultsMinimumLength': self._minimumFindLengthSpinButton.get_value(),
            'sayAllOnLoad': self._sayAllOnLoadCheckButton.get_active(),
            'pageSummaryOnLoad': self._pageSummaryOnLoadCheckButton.get_active(),
            'structuralNavigationEnabled': self._structuralNavigationCheckButton.get_active(),
            'structNavTriggersFocusMode': self._autoFocusModeStructNavCheckButton.get_active(),
            'caretNavigationEnabled': self._controlCaretNavigationCheckButton.get_active(),
            'caretNavTriggersFocusMode': self._autoFocusModeCaretNavCheckButton.get_active(),
            'nativeNavTriggersFocusMode': self._autoFocusModeNativeNavCheckButton.get_active(),
            'speakCellCoordinates': self._speakCellCoordinatesCheckButton.get_active(),
            'layoutMode': self._layoutModeCheckButton.get_active(),
            'speakCellSpan': self._speakCellSpanCheckButton.get_active(),
            'speakCellHeaders': self._speakCellHeadersCheckButton.get_active(),
            'skipBlankCells': self._skipBlankCellsCheckButton.get_active()
        }

    def skipObjectEvent(self, event):
        """Returns True if this object event should be skipped."""

        if event.type.startswith('object:state-changed:focused') and event.detail1:
            if AXUtilities.is_link(event.source):
                return False
        elif event.type.startswith('object:children-changed'):
            if AXUtilities.is_dialog(event.any_data):
                return False

        return super().skipObjectEvent(event)

    def presentationInterrupt(self, killFlash=True):
        super().presentationInterrupt(killFlash)
        msg = "WEB: Flushing live region messages"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        self.liveRegionManager.flushMessages()

    def consumesBrailleEvent(self, brailleEvent):
        """Returns True if the script will consume this braille event."""

        return super().consumesBrailleEvent(brailleEvent)

    # TODO - JD: This needs to be moved out of the scripts.
    def textLines(self, obj, offset=None):
        """Creates a generator that can be used to iterate document content."""

        if not self.utilities.inDocumentContent():
            tokens = ["WEB: textLines called for non-document content", obj]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            super().textLines(obj, offset)
            return

        self._sayAllIsInterrupted = False

        sayAllStyle = settings_manager.getManager().getSetting('sayAllStyle')
        sayAllBySentence = sayAllStyle == settings.SAYALL_STYLE_SENTENCE
        if offset is None:
            obj, characterOffset = self.utilities.getCaretContext()
        else:
            characterOffset = offset
        priorObj, priorOffset = self.utilities.getPriorContext()

        # TODO - JD: This is sad, but it's better than the old, broken
        # clumpUtterances(). We really need to fix the speechservers'
        # SayAll support. In the meantime, the generators should be
        # providing one ACSS per string.
        def _parseUtterances(utterances):
            elements, voices = [], []
            for u in utterances:
                if isinstance(u, list):
                    e, v = _parseUtterances(u)
                    elements.extend(e)
                    voices.extend(v)
                elif isinstance(u, str):
                    elements.append(u)
                elif isinstance(u, ACSS):
                    voices.append(u)
            return elements, voices

        self._inSayAll = True
        done = False
        while not done:
            if sayAllBySentence:
                contents = self.utilities.getSentenceContentsAtOffset(obj, characterOffset)
            else:
                contents = self.utilities.getLineContentsAtOffset(obj, characterOffset)
            self._sayAllContents = contents
            for i, content in enumerate(contents):
                obj, startOffset, endOffset, text = content
                tokens = ["WEB SAY ALL CONTENT:",
                          i, ". ", obj, "'", text, "' (", startOffset, "-", endOffset, ")"]
                debug.printTokens(debug.LEVEL_INFO, tokens, True)

                if self.utilities.isInferredLabelForContents(content, contents):
                    continue

                if startOffset == endOffset:
                    continue

                if self.utilities.isLabellingInteractiveElement(obj):
                    continue

                if self.utilities.isLinkAncestorOfImageInContents(obj, contents):
                    continue

                utterances = self.speechGenerator.generateContents(
                    [content], eliminatePauses=True, priorObj=priorObj)
                priorObj = obj

                elements, voices = _parseUtterances(utterances)
                if len(elements) != len(voices):
                    continue

                for i, element in enumerate(elements):
                    context = speechserver.SayAllContext(
                        obj, element, startOffset, endOffset)
                    tokens = ["WEB", context]
                    debug.printTokens(debug.LEVEL_INFO, tokens, True)
                    self._sayAllContexts.append(context)
                    self.eventSynthesizer.scroll_into_view(obj, startOffset, endOffset)
                    yield [context, voices[i]]

            lastObj, lastOffset = contents[-1][0], contents[-1][2]
            obj, characterOffset = self.utilities.findNextCaretInOrder(lastObj, lastOffset - 1)
            if obj == lastObj and characterOffset <= lastOffset:
                obj, characterOffset = self.utilities.findNextCaretInOrder(lastObj, lastOffset)
            if obj == lastObj and characterOffset <= lastOffset:
                tokens = ["WEB: Cycle within object detected in textLines. Last:",
                          lastObj, ", ", lastOffset, "Next:", obj, ", ", characterOffset]
                debug.printTokens(debug.LEVEL_INFO, tokens, True)
                break

            done = obj is None

        self._inSayAll = False
        self._sayAllContents = []
        self._sayAllContexts = []

        msg = "WEB: textLines complete. Verifying SayAll status"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        self.inSayAll()

    def presentFindResults(self, obj, offset):
        """Updates the context and presents the find results if appropriate."""

        text = self.utilities.queryNonEmptyText(obj)
        if not (text and text.getNSelections() > 0):
            return

        document = self.utilities.getDocumentForObject(obj)
        if not document:
            return

        context = self.utilities.getCaretContext(documentFrame=document)
        start, end = text.getSelection(0)
        offset = max(offset, start)
        self.utilities.setCaretContext(obj, offset, documentFrame=document)
        if end - start < settings_manager.getManager().getSetting('findResultsMinimumLength'):
            return

        verbosity = settings_manager.getManager().getSetting('findResultsVerbosity')
        if verbosity == settings.FIND_SPEAK_NONE:
            return

        if self._madeFindAnnouncement \
           and verbosity == settings.FIND_SPEAK_IF_LINE_CHANGED \
           and self.utilities.contextsAreOnSameLine(context, (obj, offset)):
            return

        contents = self.utilities.getLineContentsAtOffset(obj, offset)
        self.speakContents(contents)
        self.updateBraille(obj)

        resultsCount = self.utilities.getFindResultsCount()
        if resultsCount:
            self.presentMessage(resultsCount)

        self._madeFindAnnouncement = True

    def sayAll(self, inputEvent, obj=None, offset=None):
        """Speaks the contents of the document beginning with the present
        location.  Overridden in this script because the sayAll could have
        been started on an object without text (such as an image).
        """

        if not self.utilities.inDocumentContent():
            tokens = ["WEB: SayAll called for non-document content", obj]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return super().sayAll(inputEvent, obj, offset)

        obj = obj or focus_manager.getManager().get_locus_of_focus()
        tokens = ["WEB: SayAll called for document content", obj]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        speech.sayAll(self.textLines(obj, offset), self.__sayAllProgressCallback)
        return True

    def _rewindSayAll(self, context, minCharCount=10):
        if not self.utilities.inDocumentContent():
            return super()._rewindSayAll(context, minCharCount)

        if not settings_manager.getManager().getSetting('rewindAndFastForwardInSayAll'):
            return False

        try:
            obj, start, end, string = self._sayAllContents[0]
        except IndexError:
            return False

        focus_manager.getManager().set_locus_of_focus(None, obj, notify_script=False)
        self.utilities.setCaretContext(obj, start)

        prevObj, prevOffset = self.utilities.findPreviousCaretInOrder(obj, start)
        self.sayAll(None, prevObj, prevOffset)
        return True

    def _fastForwardSayAll(self, context):
        if not self.utilities.inDocumentContent():
            return super()._fastForwardSayAll(context)

        if not settings_manager.getManager().getSetting('rewindAndFastForwardInSayAll'):
            return False

        try:
            obj, start, end, string = self._sayAllContents[-1]
        except IndexError:
            return False

        focus_manager.getManager().set_locus_of_focus(None, obj, notify_script=False)
        self.utilities.setCaretContext(obj, end)

        nextObj, nextOffset = self.utilities.findNextCaretInOrder(obj, end)
        self.sayAll(None, nextObj, nextOffset)
        return True

    def __sayAllProgressCallback(self, context, progressType):
        if not self.utilities.inDocumentContent():
            super().__sayAllProgressCallback(context, progressType)
            return

        if progressType == speechserver.SayAllContext.INTERRUPTED:
            if isinstance(orca_state.lastInputEvent, input_event.KeyboardEvent):
                self._sayAllIsInterrupted = True
                lastKey = orca_state.lastInputEvent.event_string
                if lastKey == "Down" and self._fastForwardSayAll(context):
                    return
                elif lastKey == "Up" and self._rewindSayAll(context):
                    return
                elif not self.structuralNavigation.last_input_event_was_navigation_command():
                    focus_manager.getManager().emit_region_changed(
                        context.obj, context.currentOffset)
                    self.utilities.setCaretPosition(context.obj, context.currentOffset)
                    self.updateBraille(context.obj)

            self._inSayAll = False
            self._sayAllContents = []
            self._sayAllContexts = []
            return

        focus_manager.getManager().set_locus_of_focus(None, context.obj, notify_script=False)
        focus_manager.getManager().emit_region_changed(
            context.obj, context.currentOffset, context.currentEndOffset,
            focus_manager.SAY_ALL)
        self.utilities.setCaretContext(context.obj, context.currentOffset)

    def inFocusMode(self):
        """ Returns True if we're in focus mode."""

        return self._inFocusMode

    def focusModeIsSticky(self):
        """Returns True if we're in 'sticky' focus mode."""

        return self._focusModeIsSticky

    def browseModeIsSticky(self):
        """Returns True if we're in 'sticky' browse mode."""

        return self._browseModeIsSticky

    def useFocusMode(self, obj, prevObj=None):
        """Returns True if we should use focus mode in obj."""

        if self._focusModeIsSticky:
            msg = "WEB: Using focus mode because focus mode is sticky"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if self._browseModeIsSticky:
            msg = "WEB: Not using focus mode because browse mode is sticky"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        if self.inSayAll():
            msg = "WEB: Not using focus mode because we're in SayAll."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        lastCommandWasStructNav = \
            self.structuralNavigation.last_input_event_was_navigation_command()
        if not settings_manager.getManager().getSetting('structNavTriggersFocusMode') \
           and lastCommandWasStructNav:
            msg = "WEB: Not using focus mode due to struct nav settings"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        if prevObj and AXObject.is_dead(prevObj):
            prevObj = None

        lastCommandWasCaretNav = self.caretNavigation.last_input_event_was_navigation_command()
        if not settings_manager.getManager().getSetting('caretNavTriggersFocusMode') \
           and  lastCommandWasCaretNav \
           and not self.utilities.isNavigableToolTipDescendant(prevObj):
            msg = "WEB: Not using focus mode due to caret nav settings"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        if not settings_manager.getManager().getSetting('nativeNavTriggersFocusMode') \
           and not (lastCommandWasStructNav or lastCommandWasCaretNav):
            msg = "WEB: Not changing focus/browse mode due to native nav settings"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return self._inFocusMode

        if self.utilities.isFocusModeWidget(obj):
            tokens = ["WEB: Using focus mode because", obj, "is a focus mode widget"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return True

        doNotToggle = AXUtilities.is_link(obj) or AXUtilities.is_radio_button(obj)
        if self._inFocusMode and doNotToggle and self.utilities.lastInputEventWasUnmodifiedArrow():
            tokens = ["WEB: Staying in focus mode due to arrowing in role of", obj]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return True

        if self._inFocusMode and self.utilities.isWebAppDescendant(obj):
            if self.utilities.forceBrowseModeForWebAppDescendant(obj):
                tokens = ["WEB: Forcing browse mode for web app descendant", obj]
                debug.printTokens(debug.LEVEL_INFO, tokens, True)
                return False

            msg = "WEB: Staying in focus mode because we're inside a web application"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        tokens = ["WEB: Not using focus mode for", obj, "due to lack of cause"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return False

    def speakContents(self, contents, **args):
        """Speaks the specified contents."""

        utterances = self.speechGenerator.generateContents(contents, **args)
        speech.speak(utterances)

    def sayCharacter(self, obj):
        """Speaks the character at the current caret position."""

        if not self.caretNavigation.last_input_event_was_navigation_command() \
           and not self.utilities.isContentEditableWithEmbeddedObjects(obj):
            super().sayCharacter(obj)
            return

        document = self.utilities.getTopLevelDocumentForObject(obj)
        obj, offset = self.utilities.getCaretContext(documentFrame=document)
        if not obj:
            return

        contents = None
        if self.utilities.treatAsEndOfLine(obj, offset) and AXObject.supports_text(obj):
            char = obj.queryText().getText(offset, offset + 1)
            if char == self.EMBEDDED_OBJECT_CHARACTER:
                char = ""
            contents = [[obj, offset, offset + 1, char]]
        else:
            contents = self.utilities.getCharacterContentsAtOffset(obj, offset)

        if not contents:
            return

        obj, start, end, string = contents[0]
        if start > 0:
            string = string or "\n"

        if string:
            self.speakMisspelledIndicator(obj, start)
            self.speakCharacter(string)
        else:
            self.speakContents(contents)

        self.pointOfReference["lastTextUnitSpoken"] = "char"

    def sayWord(self, obj):
        """Speaks the word at the current caret position."""

        isEditable = self.utilities.isContentEditableWithEmbeddedObjects(obj)
        if not self.caretNavigation.last_input_event_was_navigation_command() and not isEditable:
            super().sayWord(obj)
            return

        document = self.utilities.getTopLevelDocumentForObject(obj)
        obj, offset = self.utilities.getCaretContext(documentFrame=document)
        keyString, mods = self.utilities.lastKeyAndModifiers()
        if keyString == "Right":
            offset -= 1

        wordContents = self.utilities.getWordContentsAtOffset(obj, offset, useCache=True)
        textObj, startOffset, endOffset, word = wordContents[0]
        self.speakMisspelledIndicator(textObj, startOffset)
        self.speakContents(wordContents)
        self.pointOfReference["lastTextUnitSpoken"] = "word"

    def sayLine(self, obj):
        """Speaks the line at the current caret position."""

        lastCommandWasCaretNav = self.caretNavigation.last_input_event_was_navigation_command()
        lastCommandWasStructNav = \
            self.structuralNavigation.last_input_event_was_navigation_command()

        isEditable = self.utilities.isContentEditableWithEmbeddedObjects(obj)
        if not (lastCommandWasCaretNav or lastCommandWasStructNav) and not isEditable:
            super().sayLine(obj)
            return

        document = self.utilities.getTopLevelDocumentForObject(obj)
        priorObj = None
        if lastCommandWasCaretNav or isEditable:
            priorObj, priorOffset = self.utilities.getPriorContext(documentFrame=document)

        obj, offset = self.utilities.getCaretContext(documentFrame=document)
        contents = self.utilities.getLineContentsAtOffset(obj, offset, useCache=True)
        self.speakContents(contents, priorObj=priorObj)
        self.pointOfReference["lastTextUnitSpoken"] = "line"

    def presentObject(self, obj, **args):
        if not self.utilities.inDocumentContent(obj):
            super().presentObject(obj, **args)
            return

        if AXUtilities.is_status_bar(obj):
            super().presentObject(obj, **args)
            return

        priorObj = args.get("priorObj")
        if self.caretNavigation.last_input_event_was_navigation_command() \
           or args.get("includeContext") or AXTable.get_table(obj):
            priorObj, priorOffset = self.utilities.getPriorContext()
            args["priorObj"] = priorObj

        if AXUtilities.is_entry(obj):
            super().presentObject(obj, **args)
            return

        interrupt = args.get("interrupt", False)
        tokens = ["WEB: Presenting object", obj, ". Interrupt:", interrupt]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        # We shouldn't use cache in this method, because if the last thing we presented
        # included this object and offset (e.g. a Say All or Mouse Review), we're in
        # danger of presented irrelevant context.
        useCache = False
        offset = args.get("offset", 0)
        contents = self.utilities.getObjectContentsAtOffset(obj, offset, useCache)
        self.displayContents(contents)
        self.speakContents(contents, **args)

    def updateBrailleForNewCaretPosition(self, obj):
        """Try to reposition the cursor without having to do a full update."""

        text = self.utilities.queryNonEmptyText(obj)
        if text and self.EMBEDDED_OBJECT_CHARACTER in text.getText(0, -1):
            self.updateBraille(obj)
            return

        super().updateBrailleForNewCaretPosition(obj)

    def updateBraille(self, obj, **args):
        """Updates the braille display to show the given object."""

        if not settings_manager.getManager().getSetting('enableBraille') \
           and not settings_manager.getManager().getSetting('enableBrailleMonitor'):
            debug.printMessage(debug.LEVEL_INFO, "BRAILLE: disabled", True)
            return

        if self._inFocusMode:
            tokens = ["WEB: updating braille in focus mode", obj]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            super().updateBraille(obj, **args)
            return

        document = args.get("documentFrame", self.utilities.getTopLevelDocumentForObject(obj))
        if not document:
            tokens = ["WEB: updating braille for non-document object", obj]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            super().updateBraille(obj, **args)
            return

        isContentEditable = self.utilities.isContentEditableWithEmbeddedObjects(obj)

        if not self.caretNavigation.last_input_event_was_navigation_command() \
           and not self.structuralNavigation.last_input_event_was_navigation_command() \
           and not isContentEditable \
           and not self.utilities.isPlainText() \
           and not self.utilities.lastInputEventWasCaretNavWithSelection():
            tokens = ["WEB: updating braille for unhandled navigation type", obj]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            super().updateBraille(obj, **args)
            return

        obj, offset = self.utilities.getCaretContext(
            documentFrame=document, getZombieReplicant=True)
        if offset > 0 and isContentEditable:
            text = self.utilities.queryNonEmptyText(obj)
            if text:
                offset = min(offset, text.characterCount)

        contents = self.utilities.getLineContentsAtOffset(obj, offset)
        self.displayContents(contents, documentFrame=document)

    def displayContents(self, contents, **args):
        """Displays contents in braille."""

        if not settings_manager.getManager().getSetting('enableBraille') \
           and not settings_manager.getManager().getSetting('enableBrailleMonitor'):
            debug.printMessage(debug.LEVEL_INFO, "BRAILLE: disabled", True)
            return

        line = self.getNewBrailleLine(clearBraille=True, addLine=True)
        document = args.get("documentFrame")
        contents = self.brailleGenerator.generateContents(contents, documentFrame=document)
        if not contents:
            return

        regions, focusedRegion = contents
        for region in regions:
            self.addBrailleRegionsToLine(region, line)

        if line.regions:
            line.regions[-1].string = line.regions[-1].string.rstrip(" ")

        self.setBrailleFocus(focusedRegion, getLinkMask=False)
        self.refreshBraille(panToCursor=True, getLinkMask=False)

    def panBrailleLeft(self, inputEvent=None, panAmount=0):
        """Pans braille to the left."""

        if self.flatReviewPresenter.is_active() \
           or not self.utilities.inDocumentContent() \
           or not self.isBrailleBeginningShowing():
            super().panBrailleLeft(inputEvent, panAmount)
            return

        contents = self.utilities.getPreviousLineContents()
        if not contents:
            return

        obj, start, end, string = contents[0]
        self.utilities.setCaretPosition(obj, start)
        self.updateBraille(obj)

        # Hack: When panning to the left in a document, we want to start at
        # the right/bottom of each new object. For now, we'll pan there.
        # When time permits, we'll give our braille code some smarts.
        while self.panBrailleInDirection(panToLeft=False):
            pass

        self.refreshBraille(False)
        return True

    def panBrailleRight(self, inputEvent=None, panAmount=0):
        """Pans braille to the right."""

        if self.flatReviewPresenter.is_active() \
           or not self.utilities.inDocumentContent() \
           or not self.isBrailleEndShowing():
            super().panBrailleRight(inputEvent, panAmount)
            return

        contents = self.utilities.getNextLineContents()
        if not contents:
            return

        obj, start, end, string = contents[0]
        self.utilities.setCaretPosition(obj, start)
        self.updateBraille(obj)

        # Hack: When panning to the right in a document, we want to start at
        # the left/top of each new object. For now, we'll pan there. When time
        # permits, we'll give our braille code some smarts.
        while self.panBrailleInDirection(panToLeft=True):
            pass

        self.refreshBraille(False)
        return True

    def useCaretNavigationModel(self, keyboardEvent, debugOutput=True, focus=None):
        """Returns True if caret navigation should be used."""

        if not settings_manager.getManager().getSetting('caretNavigationEnabled'):
            if debugOutput:
                msg = "WEB: Not using caret navigation: it's not enabled."
                debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        if self._inFocusMode:
            if debugOutput:
                msg = "WEB: Not using caret navigation: focus mode is active."
                debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        if not self.utilities.inDocumentContent(focus):
            if debugOutput:
                msg = "WEB: Not using caret navigation: not in document content."
                debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        if keyboardEvent and keyboardEvent.modifiers & keybindings.SHIFT_MODIFIER_MASK:
            if debugOutput:
                msg = "WEB: Not using caret navigation: shift was used."
                debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        if debugOutput:
            msg = "WEB: Using caret navigation: browse mode active in document content."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
        return True

    def useStructuralNavigationModel(self, debugOutput=True, focus=None):
        """Returns True if structural navigation should be used."""

        if not self.structuralNavigation.enabled:
            if debugOutput:
                msg = "WEB: Not using structural navigation: it's not enabled."
                debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        if self._inFocusMode:
            if debugOutput:
                msg = "WEB: Not using structural navigation: focus mode is active."
                debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        if not self.utilities.inDocumentContent(focus):
            if debugOutput:
                msg = "WEB: Not using structural navigation: not in document content."
                debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        if debugOutput:
            msg = "WEB: Using structural navigation: browse mode active in document content."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
        return True

    def getTextLineAtCaret(self, obj, offset=None, startOffset=None, endOffset=None):
        """To-be-removed. Returns the string, caretOffset, startOffset."""

        if self._inFocusMode or not self.utilities.inDocumentContent(obj) \
           or self.utilities.isFocusModeWidget(obj):
            return super().getTextLineAtCaret(obj, offset, startOffset, endOffset)

        text = self.utilities.queryNonEmptyText(obj)
        if offset is None:
            try:
                offset = max(0, text.caretOffset)
            except Exception:
                offset = 0

        if text and startOffset is not None and endOffset is not None:
            return text.getText(startOffset, endOffset), offset, startOffset

        contextObj, contextOffset = self.utilities.getCaretContext(documentFrame=None)
        if contextObj == obj:
            caretOffset = contextOffset
        else:
            caretOffset = offset

        contents = self.utilities.getLineContentsAtOffset(obj, offset)
        contents = list(filter(lambda x: x[0] == obj, contents))
        if len(contents) == 1:
            index = 0
        else:
            index = self.utilities.findObjectInContents(obj, offset, contents)

        if index > -1:
            candidate, startOffset, endOffset, string = contents[index]
            if self.EMBEDDED_OBJECT_CHARACTER not in string:
                return string, caretOffset, startOffset

        return "", 0, 0

    def moveToMouseOver(self, inputEvent):
        """Moves the context to/from the mouseover which has just appeared."""

        if not self._lastMouseOverObject:
            self.presentMessage(messages.MOUSE_OVER_NOT_FOUND)
            return

        if self._inMouseOverObject:
            x, y = self.oldMouseCoordinates
            self.eventSynthesizer.route_to_point(x, y)
            self.restorePreMouseOverContext()
            return

        obj = self._lastMouseOverObject
        obj, offset = self.utilities.findFirstCaretContext(obj, 0)
        if not obj:
            return

        if AXUtilities.is_focusable(obj):
            obj.queryComponent().grabFocus()

        contents = self.utilities.getObjectContentsAtOffset(obj, offset)
        self.utilities.setCaretPosition(obj, offset)
        self.speakContents(contents)
        self.updateBraille(obj)
        self._inMouseOverObject = True

    def restorePreMouseOverContext(self):
        """Cleans things up after a mouse-over object has been hidden."""

        obj, offset = self._preMouseOverContext
        self.utilities.setCaretPosition(obj, offset)
        self.speakContents(self.utilities.getObjectContentsAtOffset(obj, offset))
        self.updateBraille(obj)
        self._inMouseOverObject = False
        self._lastMouseOverObject = None

    def enableStickyBrowseMode(self, inputEvent, forceMessage=False):
        if not self._browseModeIsSticky or forceMessage:
            self.presentMessage(messages.MODE_BROWSE_IS_STICKY)

        self._inFocusMode = False
        self._focusModeIsSticky = False
        self._browseModeIsSticky = True
        self.caretNavigation.suspend_commands(self._inFocusMode)
        self.structuralNavigation.suspend_commands(self._inFocusMode)
        self.liveRegionManager.suspend_commands(self._inFocusMode)
        self.refreshKeyGrabs("enable sticky browse mode")

    def enableStickyFocusMode(self, inputEvent, forceMessage=False):
        if not self._focusModeIsSticky or forceMessage:
            self.presentMessage(messages.MODE_FOCUS_IS_STICKY)

        self._inFocusMode = True
        self._focusModeIsSticky = True
        self._browseModeIsSticky = False
        self.caretNavigation.suspend_commands(self._inFocusMode)
        self.structuralNavigation.suspend_commands(self._inFocusMode)
        self.liveRegionManager.suspend_commands(self._inFocusMode)
        self.refreshKeyGrabs("enable sticky focus mode")

    def toggleLayoutMode(self, inputEvent):
        layoutMode = not settings_manager.getManager().getSetting('layoutMode')
        if layoutMode:
            self.presentMessage(messages.MODE_LAYOUT)
        else:
            self.presentMessage(messages.MODE_OBJECT)
        settings_manager.getManager().setSetting('layoutMode', layoutMode)

    def togglePresentationMode(self, inputEvent, documentFrame=None):
        [obj, characterOffset] = self.utilities.getCaretContext(documentFrame)
        if self._inFocusMode:
            parent = AXObject.get_parent(obj)
            if AXUtilities.is_list_box(parent):
                self.utilities.setCaretContext(parent, -1)
            elif AXUtilities.is_menu(parent):
                self.utilities.setCaretContext(AXObject.get_parent(parent), -1)
            if not self._loadingDocumentContent:
                self.presentMessage(messages.MODE_BROWSE)
        else:
            if not self.utilities.grabFocusWhenSettingCaret(obj) \
               and (self.caretNavigation.last_input_event_was_navigation_command() \
                    or self.structuralNavigation.last_input_event_was_navigation_command() \
                    or inputEvent):
                self.utilities.grabFocus(obj)

            self.presentMessage(messages.MODE_FOCUS)
        self._inFocusMode = not self._inFocusMode
        self._focusModeIsSticky = False
        self._browseModeIsSticky = False

        self.caretNavigation.suspend_commands(self._inFocusMode)
        self.structuralNavigation.suspend_commands(self._inFocusMode)
        self.liveRegionManager.suspend_commands(self._inFocusMode)
        self.refreshKeyGrabs("toggling focus/browse mode")

    def locusOfFocusChanged(self, event, oldFocus, newFocus):
        """Handles changes of focus of interest to the script."""

        if newFocus and self.utilities.isZombie(newFocus):
            tokens = ["WEB: New focus is Zombie:", newFocus]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return True

        if newFocus and AXObject.is_dead(newFocus):
            msg = "WEB: New focus is dead"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        document = self.utilities.getTopLevelDocumentForObject(newFocus)
        if not document and self.utilities.isDocument(newFocus):
            document = newFocus

        if not document:
            msg = "WEB: Locus of focus changed to non-document obj"
            self._madeFindAnnouncement = False
            self._inFocusMode = False
            msg = "locus of focus no longer in document"
            debug.printMessage(debug.LEVEL_INFO, msg, True)

            self.caretNavigation.suspend_commands(True)
            self.structuralNavigation.suspend_commands(True)
            self.liveRegionManager.suspend_commands(True)
            self.refreshKeyGrabs(msg)
            return False

        if self.flatReviewPresenter.is_active():
            self.flatReviewPresenter.quit()

        caretOffset = 0
        if self.utilities.inFindContainer(oldFocus) \
           or (self.utilities.isDocument(newFocus) \
               and oldFocus == focus_manager.getManager().get_active_window()):
            contextObj, contextOffset = self.utilities.getCaretContext(documentFrame=document)
            if contextObj and not self.utilities.isZombie(contextObj):
                newFocus, caretOffset = contextObj, contextOffset

        if AXUtilities.is_unknown_or_redundant(newFocus):
            msg = "WEB: Event source has bogus role. Likely browser bug."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            newFocus, offset = self.utilities.findFirstCaretContext(newFocus, 0)

        text = self.utilities.queryNonEmptyText(newFocus)
        if text and (0 <= text.caretOffset <= text.characterCount):
            caretOffset = text.caretOffset

        self.utilities.setCaretContext(newFocus, caretOffset, document)
        self.updateBraille(newFocus, documentFrame=document)

        contents = None
        args = {}
        lastCommandWasCaretNav = self.caretNavigation.last_input_event_was_navigation_command()
        lastCommandWasStructNav = \
            self.structuralNavigation.last_input_event_was_navigation_command()
        if self.utilities.lastInputEventWasMouseButton() and event \
             and event.type.startswith("object:text-caret-moved"):
            msg = "WEB: Last input event was mouse button. Generating line."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            contents = self.utilities.getLineContentsAtOffset(newFocus, caretOffset)
            args['priorObj'] = oldFocus
        elif self.utilities.isContentEditableWithEmbeddedObjects(newFocus) \
           and (lastCommandWasCaretNav or lastCommandWasStructNav) \
           and not (AXUtilities.is_table_cell(newFocus) and AXObject.get_name(newFocus)):
            tokens = ["WEB: New focus", newFocus, "content editable. Generating line."]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            contents = self.utilities.getLineContentsAtOffset(newFocus, caretOffset)
        elif self.utilities.isAnchor(newFocus):
            tokens = ["WEB: New focus", newFocus, "is anchor. Generating line."]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            contents = self.utilities.getLineContentsAtOffset(newFocus, 0)
        elif self.utilities.lastInputEventWasPageNav() \
             and not AXTable.get_table(newFocus) \
             and not self.utilities.isFeedArticle(newFocus):
            tokens = ["WEB: New focus", newFocus, "was scrolled to. Generating line."]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            contents = self.utilities.getLineContentsAtOffset(newFocus, caretOffset)
        elif self.utilities.isFocusedWithMathChild(newFocus):
            tokens = ["WEB: New focus", newFocus, "has math child. Generating line."]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            contents = self.utilities.getLineContentsAtOffset(newFocus, caretOffset)
        elif AXUtilities.is_heading(newFocus):
            tokens = ["WEB: New focus", newFocus, "is heading. Generating object."]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            contents = self.utilities.getObjectContentsAtOffset(newFocus, 0)
        elif self.utilities.caretMovedToSamePageFragment(event, oldFocus):
            tokens = ["WEB: Source", event.source, "is same page fragment. Generating line."]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            contents = self.utilities.getLineContentsAtOffset(newFocus, 0)
        elif event and event.type.startswith("object:children-changed:remove") \
             and self.utilities.isFocusModeWidget(newFocus):
            tokens = ["WEB: New focus", newFocus,
                      "is recovery from removed child. Generating speech."]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
        elif self.utilities.lastInputEventWasLineNav() and self.utilities.isZombie(oldFocus):
            msg = "WEB: Last input event was line nav; oldFocus is zombie. Generating line."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            contents = self.utilities.getLineContentsAtOffset(newFocus, caretOffset)
        elif self.utilities.lastInputEventWasLineNav() and event \
             and event.type.startswith("object:children-changed"):
            msg = "WEB: Last input event was line nav and children changed. Generating line."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            contents = self.utilities.getLineContentsAtOffset(newFocus, caretOffset)
        else:
            tokens = ["WEB: New focus", newFocus, "is not a special case. Generating speech."]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            args['priorObj'] = oldFocus

        if newFocus and AXObject.is_dead(newFocus):
            msg = "WEB: New focus has since died"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            if self._getQueuedEvent("object:state-changed:focused", True):
                msg = "WEB: Have matching focused event. Not speaking contents"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                return True

        if contents:
            self.speakContents(contents, **args)
        else:
            utterances = self.speechGenerator.generateSpeech(newFocus, **args)
            speech.speak(utterances)

        self._saveFocusedObjectInfo(newFocus)

        if self.utilities.inTopLevelWebApp(newFocus) and not self._browseModeIsSticky:
            announce = not self.utilities.inDocumentContent(oldFocus)
            self.enableStickyFocusMode(None, announce)
            return True

        if not self._focusModeIsSticky \
           and not self._browseModeIsSticky \
           and self.useFocusMode(newFocus, oldFocus) != self._inFocusMode:
            self.togglePresentationMode(None, document)

        if not self.utilities.inDocumentContent(oldFocus):
            self.caretNavigation.suspend_commands(self._inFocusMode)
            self.structuralNavigation.suspend_commands(self._inFocusMode)
            self.liveRegionManager.suspend_commands(self._inFocusMode)
            self.refreshKeyGrabs("locus of focus now in document")

        return True

    def onActiveChanged(self, event):
        """Callback for object:state-changed:active accessibility events."""

        if not self.utilities.inDocumentContent(event.source):
            msg = "WEB: Event source is not in document content"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        if not event.detail1:
            msg = "WEB: Ignoring because event source is now inactive"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if AXUtilities.is_dialog_or_alert(event.source):
            msg = "WEB: Event handled: Setting locusOfFocus to event source"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            focus_manager.getManager().set_locus_of_focus(event, event.source)
            return True

        return False

    def onActiveDescendantChanged(self, event):
        """Callback for object:active-descendant-changed accessibility events."""

        if not self.utilities.inDocumentContent(event.source):
            msg = "WEB: Event source is not in document content"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        return True

    def onBusyChanged(self, event):
        """Callback for object:state-changed:busy accessibility events."""

        if event.detail1 and self._loadingDocumentContent:
            msg = "WEB: Ignoring: Already loading document content"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if not self.utilities.inDocumentContent(event.source):
            msg = "WEB: Event source is not in document content"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        focus = focus_manager.getManager().get_locus_of_focus()
        if not AXUtilities.is_document_web(event.source) \
           and not self.utilities.isOrDescendsFrom(focus, event.source):
            msg = "WEB: Ignoring: Not document and not something we're in"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        self.structuralNavigation.clearCache()

        if self.utilities.getDocumentForObject(AXObject.get_parent(event.source)):
            msg = "WEB: Ignoring: Event source is nested document"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        obj, offset = self.utilities.getCaretContext()
        if not obj or self.utilities.isZombie(obj):
            self.utilities.clearCaretContext()

        shouldPresent = True
        if not (AXUtilities.is_showing(event.source) or AXUtilities.is_visible(event.source)):
            shouldPresent = False
            msg = "WEB: Not presenting because source is not showing or visible"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
        elif not self.utilities.documentFrameURI(event.source):
            shouldPresent = False
            msg = "WEB: Not presenting because source lacks URI"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
        elif not event.detail1 and self._inFocusMode and not self.utilities.isZombie(obj):
            shouldPresent = False
            tokens = ["WEB: Not presenting due to focus mode for", obj]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)

        if not settings_manager.getManager().getSetting('onlySpeakDisplayedText') and shouldPresent:
            if event.detail1:
                self.presentMessage(messages.PAGE_LOADING_START)
            elif AXObject.get_name(event.source):
                msg = messages.PAGE_LOADING_END_NAMED % AXObject.get_name(event.source)
                self.presentMessage(msg, resetStyles=False)
            else:
                self.presentMessage(messages.PAGE_LOADING_END)

        activeDocument = self.utilities.activeDocument()
        if activeDocument and activeDocument != event.source:
            msg = "WEB: Ignoring: Event source is not active document"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        self._loadingDocumentContent = event.detail1
        if event.detail1:
            return True

        self.utilities.clearCachedObjects()
        if AXObject.is_dead(obj):
            obj = None

        if not focus_manager.getManager().focus_is_dead() \
           and not self.utilities.inDocumentContent(focus) \
           and AXUtilities.is_focused(focus):
            msg = "WEB: Not presenting content, focus is outside of document"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if settings_manager.getManager().getSetting('pageSummaryOnLoad') and shouldPresent:
            obj = obj or event.source
            tokens = ["WEB: Getting page summary for obj", obj]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            summary = self.utilities.getPageSummary(obj)
            if summary:
                self.presentMessage(summary)

        obj, offset = self.utilities.getCaretContext()
        if not AXUtilities.is_busy(event.source) \
           and self.utilities.isTopLevelWebApp(event.source):
            tokens = ["WEB: Setting locusOfFocus to", obj, "with sticky focus mode"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            focus_manager.getManager().set_locus_of_focus(event, obj)
            self.enableStickyFocusMode(None, True)
            return True

        if self.useFocusMode(obj) != self._inFocusMode:
            self.togglePresentationMode(None)

        if not obj:
            msg = "WEB: Could not get caret context"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.isFocusModeWidget(obj):
            tokens = ["WEB: Setting locus of focus to focusModeWidget", obj]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            focus_manager.getManager().set_locus_of_focus(event, obj)
            return True

        if self.utilities.isLink(obj) and AXUtilities.is_focused(obj):
            tokens = ["WEB: Setting locus of focus to focused link", obj, ". No SayAll."]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            focus_manager.getManager().set_locus_of_focus(event, obj)
            return True

        if offset > 0:
            tokens = ["WEB: Setting locus of focus to context obj", obj, ". No SayAll"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            focus_manager.getManager().set_locus_of_focus(event, obj)
            return True

        if not AXUtilities.is_focused(focus_manager.getManager().get_locus_of_focus()):
            tokens = ["WEB: Setting locus of focus to context obj", obj, "(no notification)"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            focus_manager.getManager().set_locus_of_focus(event, obj, False)

        self.updateBraille(obj)
        if self.utilities.documentFragment(event.source):
            msg = "WEB: Not doing SayAll due to page fragment"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
        elif not settings_manager.getManager().getSetting('sayAllOnLoad'):
            msg = "WEB: Not doing SayAll due to sayAllOnLoad being False"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self.speakContents(self.utilities.getLineContentsAtOffset(obj, offset))
        elif settings_manager.getManager().getSetting('enableSpeech'):
            msg = "WEB: Doing SayAll"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self.sayAll(None)
        else:
            msg = "WEB: Not doing SayAll due to enableSpeech being False"
            debug.printMessage(debug.LEVEL_INFO, msg, True)

        return True

    def onCaretMoved(self, event):
        """Callback for object:text-caret-moved accessibility events."""

        self.utilities.sanityCheckActiveWindow()

        if self.utilities.isZombie(event.source):
            msg = "WEB: Event source is Zombie"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        document = self.utilities.getTopLevelDocumentForObject(event.source)
        if not document:
            if self.utilities.eventIsBrowserUINoise(event):
                msg = "WEB: Ignoring event believed to be browser UI noise"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                return True

            if self.utilities.eventIsBrowserUIAutocompleteNoise(event):
                msg = "WEB: Ignoring event believed to be browser UI autocomplete noise"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                return True

            msg = "WEB: Event source is not in document content"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        obj, offset = self.utilities.getCaretContext(document, False, False)
        tokens = ["WEB: Context: ", obj, ", ", offset]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        if self.caretNavigation.last_input_event_was_navigation_command():
            msg = "WEB: Event ignored: Last command was caret nav"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if self.structuralNavigation.last_input_event_was_navigation_command():
            msg = "WEB: Event ignored: Last command was struct nav"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.lastInputEventWasMouseButton():
            msg = "WEB: Last input event was mouse button"
            debug.printMessage(debug.LEVEL_INFO, msg, True)

            if (event.source, event.detail1) == (obj, offset):
                msg = "WEB: Event is for current caret context."
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                return True

            if (event.source, event.detail1) == self._lastMouseButtonContext:
                msg = "WEB: Event is for last mouse button context."
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                return True

            self._lastMouseButtonContext = event.source, event.detail1

            msg = "WEB: Event handled: Last command was mouse button"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self.utilities.setCaretContext(event.source, event.detail1)
            notify = not self.utilities.isEntryDescendant(event.source)
            focus_manager.getManager().set_locus_of_focus(event, event.source, notify, True)
            return True

        if self.utilities.lastInputEventWasTab():
            msg = "WEB: Last input event was Tab."
            debug.printMessage(debug.LEVEL_INFO, msg, True)

            if self.utilities.isDocument(event.source):
                msg = "WEB: Event ignored: Caret moved in document due to Tab."
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                return True

        if self.utilities.inFindContainer():
            msg = "WEB: Event handled: Presenting find results"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self.presentFindResults(event.source, event.detail1)
            self._saveFocusedObjectInfo(focus_manager.getManager().get_locus_of_focus())
            return True

        if not self.utilities.eventIsFromLocusOfFocusDocument(event):
            msg = "WEB: Event ignored: Not from locus of focus document"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.textEventIsDueToInsertion(event):
            msg = "WEB: Event handled: Updating position due to insertion"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self._saveLastCursorPosition(event.source, event.detail1)
            return True

        if self.utilities.textEventIsDueToDeletion(event):
            msg = "WEB: Event handled: Updating position due to deletion"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self._saveLastCursorPosition(event.source, event.detail1)
            return True

        focus = focus_manager.getManager().get_locus_of_focus()
        if self.utilities.isItemForEditableComboBox(focus, event.source) \
           and not self.utilities.lastInputEventWasCharNav() \
           and not self.utilities.lastInputEventWasLineBoundaryNav():
            msg = "WEB: Event ignored: Editable combobox noise"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.eventIsAutocompleteNoise(event, document):
            msg = "WEB: Event ignored: Autocomplete noise"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if self._inFocusMode and self.utilities.caretMovedOutsideActiveGrid(event):
            msg = "WEB: Event ignored: Caret moved outside active grid during focus mode"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.treatEventAsSpinnerValueChange(event):
            msg = "WEB: Event handled as the value-change event we wish we'd get"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self.updateBraille(event.source)
            self._presentTextAtNewCaretPosition(event)
            return True

        if not self.utilities.queryNonEmptyText(event.source) \
           and not AXUtilities.is_editable(event.source):
            msg = "WEB: Event ignored: Was for non-editable object we're treating as textless"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        obj, offset = self.utilities.findFirstCaretContext(event.source, event.detail1)
        notify = force = handled = False
        AXObject.clear_cache(event.source)

        if self.utilities.lastInputEventWasPageNav():
            msg = "WEB: Caret moved due to scrolling."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            notify = force = handled = True

        elif self.utilities.caretMovedToSamePageFragment(event):
            msg = "WEB: Caret moved to fragment."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            notify = force = handled = True

        elif self.utilities.lastInputEventWasCaretNav():
            msg = "WEB: Caret moved due to native caret navigation."
            debug.printMessage(debug.LEVEL_INFO, msg, True)

        elif self.utilities.isTextField(event.source) \
           and AXUtilities.is_focused(event.source) \
           and event.source != focus:
            msg = "WEB: Focused text field is not (yet) the locus of focus."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            notify = force = handled = True

        tokens = ["WEB: Setting context and focus to: ", obj, ", ", offset]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        self.utilities.setCaretContext(obj, offset, document)
        focus_manager.getManager().set_locus_of_focus(event, obj, notify, force)
        return handled

    def onCheckedChanged(self, event):
        """Callback for object:state-changed:checked accessibility events."""

        if not self.utilities.inDocumentContent(event.source):
            msg = "WEB: Event source is not in document content"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        obj, offset = self.utilities.getCaretContext()
        if obj != event.source:
            msg = "WEB: Event source is not context object"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        oldObj, oldState = self.pointOfReference.get('checkedChange', (None, 0))
        if hash(oldObj) == hash(obj) and oldState == event.detail1:
            msg = "WEB: Ignoring event, state hasn't changed"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if not (self.caretNavigation.last_input_event_was_navigation_command() \
           and AXUtilities.is_radio_button(obj)):
            msg = "WEB: Event is something default can handle"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        self.presentObject(obj, alreadyFocused=True, interrupt=True)
        self.pointOfReference['checkedChange'] = hash(obj), event.detail1
        return True

    def onChildrenAdded(self, event):
        """Callback for object:children-changed:add accessibility events."""

        AXObject.clear_cache_now("children-changed event.")
        if AXUtilities.is_table_related(event.source):
            AXTable.clear_cache_now("children-changed event.")

        if self.utilities.eventIsBrowserUINoise(event):
            msg = "WEB: Ignoring event believed to be browser UI noise"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        isLiveRegion = self.utilities.isLiveRegion(event.source)
        document = self.utilities.getTopLevelDocumentForObject(event.source)
        if document and not isLiveRegion:
            focus = focus_manager.getManager().get_locus_of_focus()
            if event.source == focus:
                msg = "WEB: Dumping cache and context: source is focus"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                self.utilities.dumpCache(document, preserveContext=False)
            elif focus_manager.getManager().focus_is_dead():
                msg = "WEB: Dumping cache: dead focus"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                self.utilities.dumpCache(document, preserveContext=True)
            elif AXObject.find_ancestor(focus, lambda x: x == event.source):
                msg = "WEB: Dumping cache and context: source is ancestor of focus"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                self.utilities.dumpCache(document, preserveContext=True)
            else:
                msg = "WEB: Not dumping full cache"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                self.utilities.clearCachedObjects()

        elif isLiveRegion:
            if self.utilities.handleAsLiveRegion(event):
                msg = "WEB: Event to be handled as live region"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                self.liveRegionManager.handleEvent(event)
            else:
                msg = "WEB: Ignoring because live region event not to be handled."
                debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True
        else:
            msg = "WEB: Could not get document for event source"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        if self._loadingDocumentContent:
            msg = "WEB: Ignoring because document content is being loaded."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.isZombie(document):
            tokens = ["WEB: Ignoring because", document, "is zombified."]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return True

        if AXUtilities.is_busy(document):
            tokens = ["WEB: Ignoring because", document, "is busy."]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return True

        if not event.any_data or self.utilities.isZombie(event.any_data):
            msg = "WEB: Ignoring because any data is null or zombified."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.handleEventFromContextReplicant(event, event.any_data):
            msg = "WEB: Event handled by updating locusOfFocus and context to child."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if AXUtilities.is_alert(event.any_data):
            if event.any_data == self.utilities.lastQueuedLiveRegion():
                tokens = ["WEB: Ignoring", event.any_data, "(is last queued live region)"]
                debug.printTokens(debug.LEVEL_INFO, tokens, True)
                return True

            msg = "WEB: Presenting event.any_data"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self.presentObject(event.any_data, interrupt=True)

            focused = AXUtilities.get_focused_object(event.any_data)
            if focused:
                notify = self.utilities.queryNonEmptyText(focused) is None
                tokens = ["WEB: Setting locusOfFocus and caret context to", focused]
                debug.printTokens(debug.LEVEL_INFO, tokens, True)
                focus_manager.getManager().set_locus_of_focus(event, focused, notify)
                self.utilities.setCaretContext(focused, 0)
            return True

        if self.lastMouseRoutingTime and 0 < time.time() - self.lastMouseRoutingTime < 1:
            utterances = []
            utterances.append(messages.NEW_ITEM_ADDED)
            utterances.extend(self.speechGenerator.generateSpeech(event.any_data, force=True))
            speech.speak(utterances)
            self._lastMouseOverObject = event.any_data
            self.preMouseOverContext = self.utilities.getCaretContext()
            return True

        return False

    def onChildrenRemoved(self, event):
        """Callback for object:children-changed:removed accessibility events."""

        AXObject.clear_cache_now("children-changed event.")
        if AXUtilities.is_table_related(event.source):
            AXTable.clear_cache_now("children-changed event.")

        if not self.utilities.inDocumentContent(event.source):
            msg = "WEB: Event source is not in document content."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        if self._loadingDocumentContent:
            msg = "WEB: Ignoring because document content is being loaded."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.isLiveRegion(event.source):
            if self.utilities.handleEventForRemovedChild(event):
                msg = "WEB: Event handled for removed live-region child."
                debug.printMessage(debug.LEVEL_INFO, msg, True)
            else:
                msg = "WEB: Ignoring removal from live region."
                debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        document = self.utilities.getTopLevelDocumentForObject(event.source)
        if document:
            focus = focus_manager.getManager().get_locus_of_focus()
            if event.source == focus:
                msg = "WEB: Dumping cache and context: source is focus"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                self.utilities.dumpCache(document, preserveContext=False)
            elif focus_manager.getManager().focus_is_dead():
                msg = "WEB: Dumping cache: dead focus"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                self.utilities.dumpCache(document, preserveContext=True)
            elif AXObject.find_ancestor(focus, lambda x: x == event.source):
                msg = "WEB: Dumping cache and context: source is ancestor of focus"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                self.utilities.dumpCache(document, preserveContext=True)
            else:
                msg = "WEB: Not dumping full cache"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                self.utilities.clearCachedObjects()

        if self.utilities.handleEventForRemovedChild(event):
            msg = "WEB: Event handled for removed child."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        return False

    def onColumnReordered(self, event):
        """Callback for object:column-reordered accessibility events."""

        if not self.utilities.inDocumentContent(event.source):
            msg = "WEB: Event source is not in document content"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        focus = focus_manager.getManager().get_locus_of_focus()
        if event.source != AXTable.get_table(focus):
            msg = "WEB: focus is not in this table"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        self.pointOfReference['last-table-sort-time'] = time.time()
        self.presentMessage(messages.TABLE_REORDERED_COLUMNS)
        header = self.utilities.containingTableHeader(focus)
        if header:
            self.presentMessage(self.utilities.getSortOrderDescription(header, True))

        return True

    def onDocumentLoadComplete(self, event):
        """Callback for document:load-complete accessibility events."""

        if self.utilities.getDocumentForObject(AXObject.get_parent(event.source)):
            msg = "WEB: Ignoring: Event source is nested document"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        msg = "WEB: Updating loading state and resetting live regions"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        self._loadingDocumentContent = False
        self.liveRegionManager.reset()
        return True

    def onDocumentLoadStopped(self, event):
        """Callback for document:load-stopped accessibility events."""

        if self.utilities.getDocumentForObject(AXObject.get_parent(event.source)):
            msg = "WEB: Ignoring: Event source is nested document"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        msg = "WEB: Updating loading state"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        self._loadingDocumentContent = False
        return True

    def onDocumentReload(self, event):
        """Callback for document:reload accessibility events."""

        if self.utilities.getDocumentForObject(AXObject.get_parent(event.source)):
            msg = "WEB: Ignoring: Event source is nested document"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        msg = "WEB: Updating loading state"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        self._loadingDocumentContent = True
        return True

    def onExpandedChanged(self, event):
        """Callback for object:state-changed:expanded accessibility events."""

        if self.utilities.isZombie(event.source):
            msg = "WEB: Event source is Zombie"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if not self.utilities.inDocumentContent(event.source):
            msg = "WEB: Event source is not in document content"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        focus = focus_manager.getManager().get_locus_of_focus()
        obj, offset = self.utilities.getCaretContext(searchIfNeeded=False)
        tokens = ["WEB: Caret context is", obj, ", ", offset]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        if not obj or self.utilities.isZombie(obj) and event.source == focus:
            msg = "WEB: Setting caret context to event source"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self.utilities.setCaretContext(event.source, 0)

        return False

    def onFocus(self, event):
        """Callback for focus: accessibility events."""

        # We should get proper state-changed events for these.
        if self.utilities.inDocumentContent(event.source):
            msg = "WEB: Ignoring because object:state-changed-focused expected."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        return False

    def onFocusedChanged(self, event):
        """Callback for object:state-changed:focused accessibility events."""

        if not event.detail1:
            msg = "WEB: Ignoring because event source lost focus"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.isZombie(event.source):
            msg = "WEB: Event source is Zombie"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        document = self.utilities.getDocumentForObject(event.source)
        if not document:
            msg = "WEB: Could not get document for event source"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        focus = focus_manager.getManager().get_locus_of_focus()
        prevDocument = self.utilities.getDocumentForObject(focus)
        if prevDocument != document:
            tokens = ["WEB: document changed from", prevDocument, "to", document]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)

        if self.utilities.isWebAppDescendant(event.source):
            if self._browseModeIsSticky:
                msg = "WEB: Web app descendant claimed focus, but browse mode is sticky"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
            elif AXUtilities.is_tool_tip(event.source) \
              and AXObject.find_ancestor(focus, lambda x: x == event.source):
                msg = "WEB: Event believed to be side effect of tooltip navigation."
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                return True
            else:
                msg = "WEB: Event handled: Setting locusOfFocus to web app descendant"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                focus_manager.getManager().set_locus_of_focus(event, event.source)
                return True

        if AXUtilities.is_editable(event.source):
            msg = "WEB: Event source is editable"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        if AXUtilities.is_dialog_or_alert(event.source):
            msg = "WEB: Event handled: Setting locusOfFocus to event source"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            focus_manager.getManager().set_locus_of_focus(event, event.source)
            return True

        if self.utilities.handleEventFromContextReplicant(event, event.source):
            msg = "WEB: Event handled by updating locusOfFocus and context to source."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        obj, offset = self.utilities.getCaretContext()
        tokens = ["WEB: Caret context is", obj, ", ", offset]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        if not obj or self.utilities.isZombie(obj) or prevDocument != document:
            tokens = ["WEB: Clearing context - obj", obj, "is null or zombie or document changed"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            self.utilities.clearCaretContext()

            obj, offset = self.utilities.searchForCaretContext(event.source)
            if obj:
                notify = self.utilities.inFindContainer(focus)
                tokens = ["WEB: Updating focus and context to", obj, ", ", offset]
                debug.printTokens(debug.LEVEL_INFO, tokens, True)
                focus_manager.getManager().set_locus_of_focus(event, obj, notify)
                if not notify and prevDocument is None:
                    self.caretNavigation.suspend_commands(self._inFocusMode)
                    self.structuralNavigation.suspend_commands(self._inFocusMode)
                    self.liveRegionManager.suspend_commands(self._inFocusMode)
                    self.refreshKeyGrabs("updating locus of focus without notification")
                self.utilities.setCaretContext(obj, offset)
            else:
                msg = "WEB: Search for caret context failed"
                debug.printMessage(debug.LEVEL_INFO, msg, True)

        if self.caretNavigation.last_input_event_was_navigation_command():
            msg = "WEB: Event ignored: Last command was caret nav"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if self.structuralNavigation.last_input_event_was_navigation_command():
            msg = "WEB: Event ignored: Last command was struct nav"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if not (AXUtilities.is_focusable(event.source) and AXUtilities.is_focused(event.source)):
            msg = "WEB: Event ignored: Source is not focusable or focused"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if not AXUtilities.is_document(event.source):
            msg = "WEB: Deferring to other scripts for handling non-document source"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        if not obj:
            msg = "WEB: Unable to get non-null, non-zombie context object"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        if self.utilities.lastInputEventWasPageNav():
            msg = "WEB: Event handled: Focus changed due to scrolling"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            focus_manager.getManager().set_locus_of_focus(event, obj)
            self.utilities.setCaretContext(obj, offset)
            return True

        wasFocused = AXUtilities.is_focused(obj)
        AXObject.clear_cache(obj)
        isFocused = AXUtilities.is_focused(obj)
        if wasFocused != isFocused:
            tokens = ["WEB: Focused state of", obj, "changed to", isFocused]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return False

        if self.utilities.isAnchor(obj):
            cause = "Context is anchor"
        elif not (self.utilities.isLink(obj) and not isFocused):
            cause = "Context is not a non-focused link"
        elif self.utilities.isChildOfCurrentFragment(obj):
            cause = "Context is child of current fragment"
        elif document == event.source and self.utilities.documentFragment(event.source):
            cause = "Document URI is fragment"
        else:
            return False

        tokens = ["WEB: Event handled: Setting locusOfFocus to", obj, "(", cause, ")"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        focus_manager.getManager().set_locus_of_focus(event, obj)
        return True

    def onMouseButton(self, event):
        """Callback for mouse:button accessibility events."""

        return False

    def onNameChanged(self, event):
        """Callback for object:property-change:accessible-name events."""

        if self.utilities.eventIsBrowserUINoise(event):
            msg = "WEB: Ignoring event believed to be browser UI noise"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        return True

    def onRowReordered(self, event):
        """Callback for object:row-reordered accessibility events."""

        if not self.utilities.inDocumentContent(event.source):
            msg = "WEB: Event source is not in document content"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        focus = focus_manager.getManager().get_locus_of_focus()
        if event.source != AXTable.get_table(focus):
            msg = "WEB: focus is not in this table"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        self.pointOfReference['last-table-sort-time'] = time.time()
        self.presentMessage(messages.TABLE_REORDERED_ROWS)
        header = self.utilities.containingTableHeader(focus)
        if header:
            self.presentMessage(self.utilities.getSortOrderDescription(header, True))

        return True

    def onSelectedChanged(self, event):
        """Callback for object:state-changed:selected accessibility events."""

        if self.utilities.eventIsBrowserUIAutocompleteNoise(event):
            msg = "WEB: Ignoring event believed to be browser UI autocomplete noise"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        focus = focus_manager.getManager().get_locus_of_focus()
        if self.utilities.eventIsBrowserUIPageSwitch(event):
            msg = "WEB: Event believed to be browser UI page switch"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            if event.detail1:
                self.presentObject(event.source, priorObj=focus, interrupt=True)
            return True

        if not self.utilities.inDocumentContent(event.source):
            msg = "WEB: Event source is not in document content"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        if focus != event.source:
            msg = "WEB: Ignoring because event source is not locusOfFocus"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        return False

    def onSelectionChanged(self, event):
        """Callback for object:selection-changed accessibility events."""

        if self.utilities.eventIsBrowserUIAutocompleteNoise(event):
            msg = "WEB: Ignoring event believed to be browser UI autocomplete noise"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.eventIsBrowserUIPageSwitch(event):
            msg = "WEB: Ignoring event believed to be browser UI page switch"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if not self.utilities.inDocumentContent(event.source):
            msg = "WEB: Event source is not in document content"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        if not self.utilities.inDocumentContent(focus_manager.getManager().get_locus_of_focus()):
            msg = "WEB: Event ignored: locusOfFocus is not in document content"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if not self.utilities.eventIsFromLocusOfFocusDocument(event):
            msg = "WEB: Event ignored: Not from locus of focus document"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.isWebAppDescendant(event.source):
            if self._inFocusMode:
                # Because we cannot count on the app firing the right state-changed events
                # for descendants.
                AXObject.clear_cache(event.source)
                msg = "WEB: Event source is web app descendant and we're in focus mode"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                return False

            msg = "WEB: Event source is web app descendant and we're in browse mode"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.eventIsIrrelevantSelectionChangedEvent(event):
            msg = "WEB: Event ignored: Irrelevant"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        obj, offset = self.utilities.getCaretContext()
        ancestor = self.utilities.commonAncestor(obj, event.source)
        if ancestor and self.utilities.isTextBlockElement(ancestor):
            msg = "WEB: Ignoring: Common ancestor of context and event source is text block"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        return False

    def onShowingChanged(self, event):
        """Callback for object:state-changed:showing accessibility events."""

        if event.detail1 and self.utilities.isTopLevelBrowserUIAlert(event.source):
            msg = "WEB: Event handled: Presenting event source"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self.presentObject(event.source, interrupt=True)
            return True

        if not self.utilities.inDocumentContent(event.source):
            msg = "WEB: Event source is not in document content"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        return True

    def onTextAttributesChanged(self, event):
        """Callback for object:text-attributes-changed accessibility events."""

        msg = "WEB: Clearing cached text attributes"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        self._currentTextAttrs = {}
        return False

    def onTextDeleted(self, event):
        """Callback for object:text-changed:delete accessibility events."""

        if self.utilities.isZombie(event.source):
            msg = "WEB: Event source is Zombie"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.lastInputEventWasPageSwitch():
            msg = "WEB: Deletion is believed to be due to page switch"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.isLiveRegion(event.source):
            msg = "WEB: Ignoring deletion from live region"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.eventIsBrowserUINoise(event):
            msg = "WEB: Ignoring event believed to be browser UI noise"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if not self.utilities.inDocumentContent(event.source):
            msg = "WEB: Event source is not in document content"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        if self.utilities.eventIsSpinnerNoise(event):
            msg = "WEB: Ignoring: Event believed to be spinner noise"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.eventIsAutocompleteNoise(event):
            msg = "WEB: Ignoring event believed to be autocomplete noise"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        msg = "WEB: Clearing content cache due to text deletion"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        self.utilities.clearContentCache()

        if self.utilities.textEventIsDueToDeletion(event):
            msg = "WEB: Event believed to be due to editable text deletion"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        if self.utilities.textEventIsDueToInsertion(event):
            msg = "WEB: Ignoring event believed to be due to text insertion"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        obj, offset = self.utilities.getCaretContext(getZombieReplicant=False)
        if obj and obj != event.source \
           and not AXObject.find_ancestor(obj, lambda x: x == event.source):
            tokens = ["WEB: Ignoring event because it isn't", obj, "or its ancestor"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return True

        if self.utilities.isZombie(obj):
            if self.utilities.isLink(obj):
                msg = "WEB: Focused link deleted. Taking no further action."
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                return True

            obj, offset = self.utilities.getCaretContext(getZombieReplicant=True)
            if obj:
                focus_manager.getManager().set_locus_of_focus(event, obj, notify_script=False)

        if self.utilities.isZombie(obj):
            msg = "WEB: Unable to get non-null, non-zombie context object"
            debug.printMessage(debug.LEVEL_INFO, msg, True)

        document = self.utilities.getDocumentForObject(event.source)
        if document:
            tokens = ["WEB: Clearing structural navigation cache for", document]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            self.structuralNavigation.clearCache(document)

        if not AXUtilities.is_editable(event.source) \
           and not self.utilities.isContentEditableWithEmbeddedObjects(event.source):
            if self._inMouseOverObject \
               and self.utilities.isZombie(self._lastMouseOverObject):
                msg = "WEB: Restoring pre-mouseover context"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                self.restorePreMouseOverContext()

            msg = "WEB: Done processing non-editable source"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        return False

    def onTextInserted(self, event):
        """Callback for object:text-changed:insert accessibility events."""

        if self.utilities.isZombie(event.source):
            msg = "WEB: Event source is Zombie"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.lastInputEventWasPageSwitch():
            msg = "WEB: Insertion is believed to be due to page switch"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.handleAsLiveRegion(event):
            msg = "WEB: Event to be handled as live region"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self.liveRegionManager.handleEvent(event)
            return True

        if self.utilities.isLiveRegion(event.source):
            msg = "WEB: Ignoring because live region event not to be handled."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.eventIsEOCAdded(event):
            msg = "WEB: Ignoring: Event was for embedded object char"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.eventIsBrowserUINoise(event):
            msg = "WEB: Ignoring event believed to be browser UI noise"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if not self.utilities.inDocumentContent(event.source):
            msg = "WEB: Event source is not in document content"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        if self.utilities.eventIsSpinnerNoise(event):
            msg = "WEB: Ignoring: Event believed to be spinner noise"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.eventIsAutocompleteNoise(event):
            msg = "WEB: Ignoring: Event believed to be autocomplete noise"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        msg = "WEB: Clearing content cache due to text insertion"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        self.utilities.clearContentCache()

        document = self.utilities.getTopLevelDocumentForObject(event.source)
        if focus_manager.getManager().focus_is_dead():
            msg = "WEB: Dumping cache: dead focus"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self.utilities.dumpCache(document, preserveContext=True)

            if AXUtilities.is_focused(event.source):
                msg = "WEB: Event handled: Setting locusOfFocus to event source"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                focus_manager.getManager().set_locus_of_focus(None, event.source, force=True)
                return True

        else:
            tokens = ["WEB: Clearing structural navigation cache for", document]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            self.structuralNavigation.clearCache(document)

        text = self.utilities.queryNonEmptyText(event.source)
        if not text:
            msg = "WEB: Ignoring: Event source is not a text object"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        sourceIsFocus = event.source == focus_manager.getManager().get_locus_of_focus()
        if not AXUtilities.is_editable(event.source):
            if not sourceIsFocus:
                msg = "WEB: Done processing non-editable, non-locusOfFocus source"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                return True

            if self.utilities.isClickableElement(event.source):
                msg = "WEB: Event handled: Re-setting locusOfFocus to changed clickable"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                focus_manager.getManager().set_locus_of_focus(None, event.source, force=True)
                return True

        if not sourceIsFocus and AXUtilities.is_text_input(event.source) \
           and AXUtilities.is_focused(event.source):
            msg = "WEB: Focused entry is not the locus of focus. Waiting for focus event."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        return False

    def onTextSelectionChanged(self, event):
        """Callback for object:text-selection-changed accessibility events."""

        if self.utilities.isZombie(event.source):
            msg = "WEB: Event source is Zombie"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.eventIsBrowserUINoise(event):
            msg = "WEB: Ignoring event believed to be browser UI noise"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if not self.utilities.inDocumentContent(event.source):
            msg = "WEB: Event source is not in document content"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        focus = focus_manager.getManager().get_locus_of_focus()
        if not self.utilities.inDocumentContent(focus):
            msg = "WEB: Locus of focus is not in document content"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.eventIsAutocompleteNoise(event):
            msg = "WEB: Ignoring: Event believed to be autocomplete noise"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.eventIsSpinnerNoise(event):
            msg = "WEB: Ignoring: Event believed to be spinner noise"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.textEventIsForNonNavigableTextObject(event):
            msg = "WEB: Ignoring event for non-navigable text object"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        text = self.utilities.queryNonEmptyText(event.source)
        if not text:
            msg = "WEB: Ignoring: Event source is not a text object"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if event.source != focus and AXUtilities.is_text_input(event.source) \
           and AXUtilities.is_focused(event.source):
            msg = "WEB: Focused entry is not the locus of focus. Waiting for focus event."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.isContentEditableWithEmbeddedObjects(event.source):
            msg = "WEB: In content editable with embedded objects"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        offset = text.caretOffset
        char = text.getText(offset, offset+1)
        if char == self.EMBEDDED_OBJECT_CHARACTER \
           and not self.utilities.lastInputEventWasCaretNavWithSelection() \
           and not self.utilities.lastInputEventWasCommand():
            msg = "WEB: Ignoring: Not selecting and event offset is at embedded object"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        return False

    def onWindowActivated(self, event):
        """Callback for window:activate accessibility events."""

        msg = "WEB: Deferring to app/toolkit script"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        return False

    def onWindowDeactivated(self, event):
        """Callback for window:deactivate accessibility events."""

        msg = "WEB: Clearing command state"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        self._lastMouseButtonContext = None, -1
        return False

    def getTransferableAttributes(self):
        return {"_inFocusMode": self._inFocusMode,
                "_focusModeIsSticky": self._focusModeIsSticky,
                "_browseModeIsSticky": self._browseModeIsSticky,
        }
