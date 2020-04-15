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

from gi.repository import Gtk
import pyatspi
import time

from orca import caret_navigation
from orca import cmdnames
from orca import keybindings
from orca import debug
from orca import eventsynthesizer
from orca import guilabels
from orca import input_event
from orca import liveregions
from orca import messages
from orca import object_properties
from orca import orca
from orca import orca_state
from orca import settings
from orca import settings_manager
from orca import speech
from orca import speechserver
from orca import structural_navigation
from orca.acss import ACSS
from orca.scripts import default

from .bookmarks import Bookmarks
from .braille_generator import BrailleGenerator
from .sound_generator import SoundGenerator
from .speech_generator import SpeechGenerator
from .tutorial_generator import TutorialGenerator
from .script_utilities import Utilities

_settingsManager = settings_manager.getManager()


class Script(default.Script):

    def __init__(self, app):
        super().__init__(app)

        self._sayAllContents = []
        self._inSayAll = False
        self._sayAllIsInterrupted = False
        self._loadingDocumentContent = False
        self._madeFindAnnouncement = False
        self._lastCommandWasCaretNav = False
        self._lastCommandWasStructNav = False
        self._lastCommandWasMouseButton = False
        self._lastMouseOverObject = None
        self._preMouseOverContext = None, -1
        self._inMouseOverObject = False
        self._inFocusMode = False
        self._focusModeIsSticky = False
        self._browseModeIsSticky = False

        if _settingsManager.getSetting('caretNavigationEnabled') is None:
            _settingsManager.setSetting('caretNavigationEnabled', True)
        if _settingsManager.getSetting('sayAllOnLoad') is None:
            _settingsManager.setSetting('sayAllOnLoad', True)
        if _settingsManager.getSetting('pageSummaryOnLoad') is None:
            _settingsManager.setSetting('pageSummaryOnLoad', True)

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
        self._layoutModeCheckButton = None

    def deactivate(self):
        """Called when this script is deactivated."""

        self._sayAllContents = []
        self._inSayAll = False
        self._sayAllIsInterrupted = False
        self._loadingDocumentContent = False
        self._madeFindAnnouncement = False
        self._lastCommandWasCaretNav = False
        self._lastCommandWasStructNav = False
        self._lastCommandWasMouseButton = False
        self._lastMouseOverObject = None
        self._preMouseOverContext = None, -1
        self._inMouseOverObject = False
        self.utilities.clearCachedObjects()

    def getAppKeyBindings(self):
        """Returns the application-specific keybindings for this script."""

        keyBindings = keybindings.KeyBindings()

        structNavBindings = self.structuralNavigation.keyBindings
        for keyBinding in structNavBindings.keyBindings:
            keyBindings.add(keyBinding)

        caretNavBindings = self.caretNavigation.get_bindings()
        for keyBinding in caretNavBindings.keyBindings:
            keyBindings.add(keyBinding)

        liveRegionBindings = self.liveRegionManager.keyBindings
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


        layout = _settingsManager.getSetting('keyboardLayout')
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
        self.inputEventHandlers.update(
            self.structuralNavigation.inputEventHandlers)

        self.inputEventHandlers.update(
            self.caretNavigation.get_handlers())

        self.inputEventHandlers.update(
            self.liveRegionManager.inputEventHandlers)

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
        """Returns the utilites for this script."""

        return Utilities(self)

    def getAppPreferencesGUI(self):
        """Return a GtkGrid containing app-unique configuration items."""

        grid = Gtk.Grid()
        grid.set_border_width(12)

        generalFrame = Gtk.Frame()
        grid.attach(generalFrame, 0, 0, 1, 1)

        label = Gtk.Label(label="<b>%s</b>" % guilabels.PAGE_NAVIGATION)
        label.set_use_markup(True)
        generalFrame.set_label_widget(label)

        generalAlignment = Gtk.Alignment.new(0.5, 0.5, 1, 1)
        generalAlignment.set_padding(0, 0, 12, 0)
        generalFrame.add(generalAlignment)
        generalGrid = Gtk.Grid()
        generalAlignment.add(generalGrid)

        label = guilabels.USE_CARET_NAVIGATION
        value = _settingsManager.getSetting('caretNavigationEnabled')
        self._controlCaretNavigationCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self._controlCaretNavigationCheckButton.set_active(value)
        generalGrid.attach(self._controlCaretNavigationCheckButton, 0, 0, 1, 1)

        label = guilabels.AUTO_FOCUS_MODE_CARET_NAV
        value = _settingsManager.getSetting('caretNavTriggersFocusMode')
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
        value = _settingsManager.getSetting('structNavTriggersFocusMode')
        self._autoFocusModeStructNavCheckButton = Gtk.CheckButton.new_with_mnemonic(label)
        self._autoFocusModeStructNavCheckButton.set_active(value)
        generalGrid.attach(self._autoFocusModeStructNavCheckButton, 0, 3, 1, 1)

        label = guilabels.READ_PAGE_UPON_LOAD
        value = _settingsManager.getSetting('sayAllOnLoad')
        self._sayAllOnLoadCheckButton = Gtk.CheckButton.new_with_mnemonic(label)
        self._sayAllOnLoadCheckButton.set_active(value)
        generalGrid.attach(self._sayAllOnLoadCheckButton, 0, 4, 1, 1)

        label = guilabels.PAGE_SUMMARY_UPON_LOAD
        value = _settingsManager.getSetting('pageSummaryOnLoad')
        self._pageSummaryOnLoadCheckButton = Gtk.CheckButton.new_with_mnemonic(label)
        self._pageSummaryOnLoadCheckButton.set_active(value)
        generalGrid.attach(self._pageSummaryOnLoadCheckButton, 0, 5, 1, 1)

        label = guilabels.CONTENT_LAYOUT_MODE
        value = _settingsManager.getSetting('layoutMode')
        self._layoutModeCheckButton = Gtk.CheckButton.new_with_mnemonic(label)
        self._layoutModeCheckButton.set_active(value)
        generalGrid.attach(self._layoutModeCheckButton, 0, 6, 1, 1)

        tableFrame = Gtk.Frame()
        grid.attach(tableFrame, 0, 1, 1, 1)

        label = Gtk.Label(label="<b>%s</b>" % guilabels.TABLE_NAVIGATION)
        label.set_use_markup(True)
        tableFrame.set_label_widget(label)

        tableAlignment = Gtk.Alignment.new(0.5, 0.5, 1, 1)
        tableAlignment.set_padding(0, 0, 12, 0)
        tableFrame.add(tableAlignment)
        tableGrid = Gtk.Grid()
        tableAlignment.add(tableGrid)

        label = guilabels.TABLE_SPEAK_CELL_COORDINATES
        value = _settingsManager.getSetting('speakCellCoordinates')
        self._speakCellCoordinatesCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self._speakCellCoordinatesCheckButton.set_active(value)
        tableGrid.attach(self._speakCellCoordinatesCheckButton, 0, 0, 1, 1)

        label = guilabels.TABLE_SPEAK_CELL_SPANS
        value = _settingsManager.getSetting('speakCellSpan')
        self._speakCellSpanCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self._speakCellSpanCheckButton.set_active(value)
        tableGrid.attach(self._speakCellSpanCheckButton, 0, 1, 1, 1)

        label = guilabels.TABLE_ANNOUNCE_CELL_HEADER
        value = _settingsManager.getSetting('speakCellHeaders')
        self._speakCellHeadersCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self._speakCellHeadersCheckButton.set_active(value)
        tableGrid.attach(self._speakCellHeadersCheckButton, 0, 2, 1, 1)

        label = guilabels.TABLE_SKIP_BLANK_CELLS
        value = _settingsManager.getSetting('skipBlankCells')
        self._skipBlankCellsCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self._skipBlankCellsCheckButton.set_active(value)
        tableGrid.attach(self._skipBlankCellsCheckButton, 0, 3, 1, 1)

        findFrame = Gtk.Frame()
        grid.attach(findFrame, 0, 2, 1, 1)

        label = Gtk.Label(label="<b>%s</b>" % guilabels.FIND_OPTIONS)
        label.set_use_markup(True)
        findFrame.set_label_widget(label)

        findAlignment = Gtk.Alignment.new(0.5, 0.5, 1, 1)
        findAlignment.set_padding(0, 0, 12, 0)
        findFrame.add(findAlignment)
        findGrid = Gtk.Grid()
        findAlignment.add(findGrid)

        verbosity = _settingsManager.getSetting('findResultsVerbosity')

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
            Gtk.Adjustment(_settingsManager.getSetting(
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
            'speakCellCoordinates': self._speakCellCoordinatesCheckButton.get_active(),
            'layoutMode': self._layoutModeCheckButton.get_active(),
            'speakCellSpan': self._speakCellSpanCheckButton.get_active(),
            'speakCellHeaders': self._speakCellHeadersCheckButton.get_active(),
            'skipBlankCells': self._skipBlankCellsCheckButton.get_active()
        }

    def skipObjectEvent(self, event):
        """Returns True if this object event should be skipped."""

        if event.type.startswith('object:state-changed:focused') \
           and event.detail1:
            if event.source.getRole() == pyatspi.ROLE_LINK:
                return False

        if event.type.startswith('object:children-changed'):
            try:
                role = event.any_data.getRole()
            except:
                pass
            else:
                if role == pyatspi.ROLE_DIALOG:
                    return False

        return super().skipObjectEvent(event)

    def presentationInterrupt(self):
        super().presentationInterrupt()
        msg = "WEB: Flushing live region messages"
        debug.println(debug.LEVEL_INFO, msg, True)
        self.liveRegionManager.flushMessages()

    def consumesKeyboardEvent(self, keyboardEvent):
        """Returns True if the script will consume this keyboard event."""

        # We need to do this here. Orca caret and structural navigation
        # often result in the user being repositioned without our getting
        # a corresponding AT-SPI event. Without an AT-SPI event, script.py
        # won't know to dump the generator cache. See bgo#618827.
        self.generatorCache = {}

        handler = self.keyBindings.getInputHandler(keyboardEvent)
        if handler and self.caretNavigation.handles_navigation(handler):
            consumes = self.useCaretNavigationModel(keyboardEvent)
            self._lastCommandWasCaretNav = consumes
            self._lastCommandWasStructNav = False
            self._lastCommandWasMouseButton = False
            return consumes

        if handler and handler.function in self.structuralNavigation.functions:
            consumes = self.useStructuralNavigationModel()
            self._lastCommandWasCaretNav = False
            self._lastCommandWasStructNav = consumes
            self._lastCommandWasMouseButton = False
            return consumes

        if handler and handler.function in self.liveRegionManager.functions:
            # This is temporary.
            consumes = self.useStructuralNavigationModel()
            self._lastCommandWasCaretNav = False
            self._lastCommandWasStructNav = consumes
            self._lastCommandWasMouseButton = False
            return consumes

        self._lastCommandWasCaretNav = False
        self._lastCommandWasStructNav = False
        self._lastCommandWasMouseButton = False
        return super().consumesKeyboardEvent(keyboardEvent)

    # TODO - JD: This needs to be moved out of the scripts.
    def textLines(self, obj, offset=None):
        """Creates a generator that can be used to iterate document content."""

        if not self.utilities.inDocumentContent():
            msg = "WEB: textLines called for non-document content %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            super().textLines(obj, offset)
            return

        self._sayAllIsInterrupted = False

        sayAllStyle = _settingsManager.getSetting('sayAllStyle')
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
            for content in contents:
                if self.utilities.isInferredLabelForContents(content, contents):
                    continue

                obj, startOffset, endOffset, text = content
                if startOffset == endOffset:
                    continue

                if self.utilities.isLabellingContents(obj):
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
                    self._sayAllContexts.append(context)
                    eventsynthesizer.scrollIntoView(obj, startOffset, endOffset)
                    yield [context, voices[i]]

            lastObj, lastOffset = contents[-1][0], contents[-1][2]
            obj, characterOffset = self.utilities.findNextCaretInOrder(lastObj, lastOffset - 1)
            if obj == lastObj and characterOffset <= lastOffset:
                obj, characterOffset = self.utilities.findNextCaretInOrder(lastObj, lastOffset)
            if obj == lastObj and characterOffset <= lastOffset:
                msg = "WEB: Cycle within object detected in textLines. Last: %s, %i Next: %s, %i" \
                    % (lastObj, lastOffset, obj, characterOffset)
                debug.println(debug.LEVEL_INFO, msg, True)
                break

            done = obj is None

        self._inSayAll = False
        self._sayAllContents = []
        self._sayAllContexts = []

        msg = "WEB: textLines complete. Verifying SayAll status"
        debug.println(debug.LEVEL_INFO, msg, True)
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
        if end - start < _settingsManager.getSetting('findResultsMinimumLength'):
            return

        verbosity = _settingsManager.getSetting('findResultsVerbosity')
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
            msg = "WEB: SayAll called for non-document content %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return super().sayAll(inputEvent, obj, offset)

        obj = obj or orca_state.locusOfFocus
        msg = "WEB: SayAll called for document content %s" % obj
        debug.println(debug.LEVEL_INFO, msg, True)
        speech.sayAll(self.textLines(obj, offset), self.__sayAllProgressCallback)
        return True

    def _rewindSayAll(self, context, minCharCount=10):
        if not self.utilities.inDocumentContent():
            return super()._rewindSayAll(context, minCharCount)

        if not _settingsManager.getSetting('rewindAndFastForwardInSayAll'):
            return False

        try:
            obj, start, end, string = self._sayAllContents[0]
        except IndexError:
            return False

        orca.setLocusOfFocus(None, obj, notifyScript=False)
        self.utilities.setCaretContext(obj, start)

        prevObj, prevOffset = self.utilities.findPreviousCaretInOrder(obj, start)
        self.sayAll(None, prevObj, prevOffset)
        return True

    def _fastForwardSayAll(self, context):
        if not self.utilities.inDocumentContent():
            return super()._fastForwardSayAll(context)

        if not _settingsManager.getSetting('rewindAndFastForwardInSayAll'):
            return False

        try:
            obj, start, end, string = self._sayAllContents[-1]
        except IndexError:
            return False

        orca.setLocusOfFocus(None, obj, notifyScript=False)
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
                elif not self._lastCommandWasStructNav:
                    self.utilities.setCaretPosition(context.obj, context.currentOffset)
                    self.updateBraille(context.obj)

            self._inSayAll = False
            self._sayAllContents = []
            self._sayAllContexts = []
            return

        orca.setLocusOfFocus(None, context.obj, notifyScript=False)
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

    def useFocusMode(self, obj):
        """Returns True if we should use focus mode in obj."""

        if self._focusModeIsSticky:
            msg = "WEB: Using focus mode because focus mode is sticky"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if self._browseModeIsSticky:
            msg = "WEB: Not using focus mode because browse mode is sticky"
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if not _settingsManager.getSetting('structNavTriggersFocusMode') \
           and self._lastCommandWasStructNav:
            msg = "WEB: Not using focus mode due to struct nav settings"
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if not _settingsManager.getSetting('caretNavTriggersFocusMode') \
           and self._lastCommandWasCaretNav:
            msg = "WEB: Not using focus mode due to caret nav settings"
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if self.utilities.isFocusModeWidget(obj):
            msg = "WEB: Using focus mode because %s is a focus mode widget" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if self._inFocusMode and obj and obj.getRole() == pyatspi.ROLE_RADIO_BUTTON:
            msg = "WEB: Staying in focus mode due to role of %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if self._inFocusMode and self.utilities.isWebAppDescendant(obj):
            msg = "WEB: Staying in focus mode because we're inside a web application"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        msg = "WEB: Not using focus mode for %s due to lack of cause" % obj
        debug.println(debug.LEVEL_INFO, msg, True)
        return False

    def speakContents(self, contents, **args):
        """Speaks the specified contents."""

        utterances = self.speechGenerator.generateContents(contents, **args)
        speech.speak(utterances)

    def sayCharacter(self, obj):
        """Speaks the character at the current caret position."""

        if not self._lastCommandWasCaretNav \
           and not self.utilities.isContentEditableWithEmbeddedObjects(obj):
            super().sayCharacter(obj)
            return

        obj, offset = self.utilities.getCaretContext(documentFrame=None)
        if not obj:
            return

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

    def sayWord(self, obj):
        """Speaks the word at the current caret position."""

        if not self._lastCommandWasCaretNav \
           and not self.utilities.isContentEditableWithEmbeddedObjects(obj):
            super().sayWord(obj)
            return

        obj, offset = self.utilities.getCaretContext(documentFrame=None)
        text = self.utilities.queryNonEmptyText(obj)
        if text and offset == text.characterCount:
            offset -= 1

        wordContents = self.utilities.getWordContentsAtOffset(obj, offset)
        textObj, startOffset, endOffset, word = wordContents[0]
        self.speakMisspelledIndicator(textObj, startOffset)
        self.speakContents(wordContents)

    def sayLine(self, obj):
        """Speaks the line at the current caret position."""

        isEditable = self.utilities.isContentEditableWithEmbeddedObjects(obj)
        if not (self._lastCommandWasCaretNav or self._lastCommandWasStructNav) and not isEditable:
            super().sayLine(obj)
            return

        priorObj = None
        if self._lastCommandWasCaretNav or isEditable:
            priorObj, priorOffset = self.utilities.getPriorContext()

        obj, offset = self.utilities.getCaretContext(documentFrame=None)
        contents = self.utilities.getLineContentsAtOffset(obj, offset, useCache=not isEditable)
        self.speakContents(contents, priorObj=priorObj)

    def presentObject(self, obj, **args):
        if not self.utilities.inDocumentContent(obj):
            super().presentObject(obj, **args)
            return

        priorObj = args.get("priorObj")
        if self._lastCommandWasCaretNav or args.get("includeContext"):
            priorObj, priorOffset = self.utilities.getPriorContext()
            args["priorObj"] = priorObj

        if obj.getRole() == pyatspi.ROLE_ENTRY:
            utterances = self.speechGenerator.generateSpeech(obj, **args)
            speech.speak(utterances)
            self.updateBraille(obj)
            return

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

        if not _settingsManager.getSetting('enableBraille') \
           and not _settingsManager.getSetting('enableBrailleMonitor'):
            debug.println(debug.LEVEL_INFO, "BRAILLE: disabled", True)
            return

        if not self.utilities.inDocumentContent(obj):
            msg = "WEB: updating braille for non-document object %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            super().updateBraille(obj, **args)
            return

        isContentEditable = self.utilities.isContentEditableWithEmbeddedObjects(obj)

        if not self._lastCommandWasCaretNav \
           and not self._lastCommandWasStructNav \
           and not isContentEditable \
           and not self.utilities.isPlainText() \
           and not self.utilities.lastInputEventWasCaretNavWithSelection():
            msg = "WEB: updating braille for unhandled navigation type %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            super().updateBraille(obj, **args)
            return

        obj, offset = self.utilities.getCaretContext(documentFrame=None)
        if offset > 0 and isContentEditable:
            text = self.utilities.queryNonEmptyText(obj)
            if text:
                offset = min(offset, text.characterCount)

        contents = self.utilities.getLineContentsAtOffset(obj, offset)
        self.displayContents(contents)

    def displayContents(self, contents):
        """Displays contents in braille."""

        if not _settingsManager.getSetting('enableBraille') \
           and not _settingsManager.getSetting('enableBrailleMonitor'):
            debug.println(debug.LEVEL_INFO, "BRAILLE: disabled", True)
            return

        line = self.getNewBrailleLine(clearBraille=True, addLine=True)
        contents = self.brailleGenerator.generateContents(contents)
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

        if self.flatReviewContext \
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

        if self.flatReviewContext \
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

    def useCaretNavigationModel(self, keyboardEvent):
        """Returns True if caret navigation should be used."""

        if not _settingsManager.getSetting('caretNavigationEnabled') \
           or self._inFocusMode:
            return False

        if not self.utilities.inDocumentContent():
            return False

        if keyboardEvent.modifiers & keybindings.SHIFT_MODIFIER_MASK:
            return False

        return True

    def useStructuralNavigationModel(self):
        """Returns True if structural navigation should be used."""

        if not self.structuralNavigation.enabled or self._inFocusMode:
            return False

        if not self.utilities.inDocumentContent():
            return False

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
            except:
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
            if not self.EMBEDDED_OBJECT_CHARACTER in string:
                return string, caretOffset, startOffset

        return "", 0, 0

    def moveToMouseOver(self, inputEvent):
        """Moves the context to/from the mouseover which has just appeared."""

        if not self._lastMouseOverObject:
            self.presentMessage(messages.MOUSE_OVER_NOT_FOUND)
            return

        if self._inMouseOverObject:
            x, y = self.oldMouseCoordinates
            eventsynthesizer.routeToPoint(x, y)
            self.restorePreMouseOverContext()
            return

        obj = self._lastMouseOverObject
        obj, offset = self.utilities.findFirstCaretContext(obj, 0)
        if not obj:
            return

        if obj.getState().contains(pyatspi.STATE_FOCUSABLE):
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

    def enableStickyFocusMode(self, inputEvent, forceMessage=False):
        if not self._focusModeIsSticky or forceMessage:
            self.presentMessage(messages.MODE_FOCUS_IS_STICKY)

        self._inFocusMode = True
        self._focusModeIsSticky = True
        self._browseModeIsSticky = False

    def toggleLayoutMode(self, inputEvent):
        layoutMode = not _settingsManager.getSetting('layoutMode')
        if layoutMode:
            self.presentMessage(messages.MODE_LAYOUT)
        else:
            self.presentMessage(messages.MODE_OBJECT)
        _settingsManager.setSetting('layoutMode', layoutMode)

    def togglePresentationMode(self, inputEvent):
        [obj, characterOffset] = self.utilities.getCaretContext()
        if self._inFocusMode:
            try:
                parentRole = obj.parent.getRole()
            except:
                parentRole = None
            if parentRole == pyatspi.ROLE_LIST_BOX:
                self.utilities.setCaretContext(obj.parent, -1)
            elif parentRole == pyatspi.ROLE_MENU:
                self.utilities.setCaretContext(obj.parent.parent, -1)

            self.presentMessage(messages.MODE_BROWSE)
        else:
            if not self.utilities.grabFocusWhenSettingCaret(obj) \
               and (self._lastCommandWasCaretNav \
                    or self._lastCommandWasStructNav \
                    or inputEvent):
                self.utilities.grabFocus(obj)

            self.presentMessage(messages.MODE_FOCUS)
        self._inFocusMode = not self._inFocusMode
        self._focusModeIsSticky = False
        self._browseModeIsSticky = False

    def locusOfFocusChanged(self, event, oldFocus, newFocus):
        """Handles changes of focus of interest to the script."""

        if newFocus and self.utilities.isZombie(newFocus):
            msg = "WEB: New focus is Zombie: %s" % newFocus
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if not self.utilities.inDocumentContent(newFocus):
            msg = "WEB: Locus of focus changed to non-document obj"
            self._madeFindAnnouncement = False
            self._inFocusMode = False
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        caretOffset = 0
        if self.utilities.inFindContainer(oldFocus) \
           or (self.utilities.isDocument(newFocus) and oldFocus == orca_state.activeWindow):
            contextObj, contextOffset = self.utilities.getCaretContext()
            if contextObj and not self.utilities.isZombie(contextObj):
                newFocus, caretOffset = contextObj, contextOffset

        if newFocus.getRole() in [pyatspi.ROLE_UNKNOWN, pyatspi.ROLE_REDUNDANT_OBJECT]:
            msg = "WEB: Event source has bogus role. Likely browser bug."
            debug.println(debug.LEVEL_INFO, msg, True)
            newFocus, offset = self.utilities.findFirstCaretContext(newFocus, 0)

        text = self.utilities.queryNonEmptyText(newFocus)
        if text and (0 <= text.caretOffset <= text.characterCount):
            caretOffset = text.caretOffset

        self.utilities.setCaretContext(newFocus, caretOffset)
        self.updateBraille(newFocus)

        if self.utilities.isContentEditableWithEmbeddedObjects(newFocus) \
           and not (newFocus.getRole() == pyatspi.ROLE_TABLE_CELL and newFocus.name):
            msg = "WEB: New focus %s content editable. Generating line contents." % newFocus
            debug.println(debug.LEVEL_INFO, msg, True)
            contents = self.utilities.getLineContentsAtOffset(newFocus, caretOffset)
            utterances = self.speechGenerator.generateContents(contents)
        elif self.utilities.isAnchor(newFocus):
            msg = "WEB: New focus %s is anchor. Generating line contents." % newFocus
            debug.println(debug.LEVEL_INFO, msg, True)
            contents = self.utilities.getLineContentsAtOffset(newFocus, 0)
            utterances = self.speechGenerator.generateContents(contents)
        elif self.utilities.lastInputEventWasPageNav() and not self.utilities.getTable(newFocus):
            msg = "WEB: New focus %s was scrolled to. Generating line contents." % newFocus
            debug.println(debug.LEVEL_INFO, msg, True)
            contents = self.utilities.getLineContentsAtOffset(newFocus, caretOffset)
            utterances = self.speechGenerator.generateContents(contents)
        elif self.utilities.isFocusedWithMathChild(newFocus):
            msg = "WEB: New focus %s has math child. Generating line contents." % newFocus
            debug.println(debug.LEVEL_INFO, msg, True)
            contents = self.utilities.getLineContentsAtOffset(newFocus, caretOffset)
            utterances = self.speechGenerator.generateContents(contents)
        elif newFocus.getRole() == pyatspi.ROLE_HEADING:
            msg = "WEB: New focus %s is heading. Generating object contents." % newFocus
            debug.println(debug.LEVEL_INFO, msg, True)
            contents = self.utilities.getObjectContentsAtOffset(newFocus, 0)
            utterances = self.speechGenerator.generateContents(contents)
        elif self.utilities.caretMovedToSamePageFragment(event, oldFocus):
            msg = "WEB: Event source %s is same page fragment. Generating line contents." % event.source
            debug.println(debug.LEVEL_INFO, msg, True)
            contents = self.utilities.getLineContentsAtOffset(newFocus, 0)
            utterances = self.speechGenerator.generateContents(contents)
        else:
            msg = "WEB: New focus %s is not a special case. Generating speech." % newFocus
            debug.println(debug.LEVEL_INFO, msg, True)
            utterances = self.speechGenerator.generateSpeech(newFocus, priorObj=oldFocus)

        speech.speak(utterances)
        self._saveFocusedObjectInfo(newFocus)

        if self.utilities.inTopLevelWebApp(newFocus) and not self._browseModeIsSticky:
            announce = not self.utilities.inDocumentContent(oldFocus)
            self.enableStickyFocusMode(None, announce)
            return True

        if not self._focusModeIsSticky \
           and not self._browseModeIsSticky \
           and self.useFocusMode(newFocus) != self._inFocusMode:
            self.togglePresentationMode(None)

        return True

    def onActiveChanged(self, event):
        """Callback for object:state-changed:active accessibility events."""

        if not self.utilities.inDocumentContent(event.source):
            msg = "WEB: Event source is not in document content"
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if not event.detail1:
            msg = "WEB: Ignoring because event source is now inactive"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        role = event.source.getRole()
        if role in [pyatspi.ROLE_DIALOG, pyatspi.ROLE_ALERT]:
            msg = "WEB: Event handled: Setting locusOfFocus to event source"
            debug.println(debug.LEVEL_INFO, msg, True)
            orca.setLocusOfFocus(event, event.source)
            return True

        return False

    def onActiveDescendantChanged(self, event):
        """Callback for object:active-descendant-changed accessibility events."""

        if not self.utilities.inDocumentContent(event.source):
            msg = "WEB: Event source is not in document content"
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        return True

    def onBusyChanged(self, event):
        """Callback for object:state-changed:busy accessibility events."""

        if event.detail1 and self._loadingDocumentContent:
            msg = "WEB: Ignoring: Already loading document content"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if not self.utilities.inDocumentContent(event.source):
            msg = "WEB: Event source is not in document content"
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if event.source.getRole() != pyatspi.ROLE_DOCUMENT_WEB \
           and not self.utilities.isOrDescendsFrom(orca_state.locusOfFocus, event.source):
            msg = "WEB: Ignoring: Not document and not something we're in"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        self.structuralNavigation.clearCache()

        if self.utilities.getDocumentForObject(event.source.parent):
            msg = "WEB: Ignoring: Event source is nested document"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        obj, offset = self.utilities.getCaretContext()
        if not obj or self.utilities.isZombie(obj):
            self.utilities.clearCaretContext()

        shouldPresent = True
        if not self.utilities.isShowingOrVisible(event.source):
            shouldPresent = False
            msg = "WEB: Not presenting because source is not showing or visible"
            debug.println(debug.LEVEL_INFO, msg, True)
        elif not self.utilities.documentFrameURI(event.source):
            shouldPresent = False
            msg = "WEB: Not presenting because source lacks URI"
            debug.println(debug.LEVEL_INFO, msg, True)
        elif not event.detail1 and self._inFocusMode and not self.utilities.isZombie(obj):
            shouldPresent = False
            msg = "WEB: Not presenting due to focus mode for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)

        if not _settingsManager.getSetting('onlySpeakDisplayedText') and shouldPresent:
            if event.detail1:
                self.presentMessage(messages.PAGE_LOADING_START)
            elif event.source.name:
                msg = messages.PAGE_LOADING_END_NAMED % event.source.name
                self.presentMessage(msg, resetStyles=False)
            else:
                self.presentMessage(messages.PAGE_LOADING_END)

        activeDocument = self.utilities.activeDocument()
        if activeDocument and activeDocument != event.source:
            msg = "WEB: Ignoring: Event source is not active document"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        self._loadingDocumentContent = event.detail1
        if event.detail1:
            return True

        self.utilities.clearCachedObjects()

        if _settingsManager.getSetting('pageSummaryOnLoad') and shouldPresent:
            obj = obj or event.source
            msg = "WEB: Getting page summary for obj %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            summary = self.utilities.getPageSummary(obj)
            if summary:
                self.presentMessage(summary)

        obj, offset = self.utilities.getCaretContext()

        try:
            sourceIsBusy = event.souce.getState().contains(pyatspi.STATE_BUSY)
        except:
            sourceIsBusy = False

        if not sourceIsBusy and self.utilities.isTopLevelWebApp(event.source):
            msg = "WEB: Setting locusOfFocus to %s with sticky focus mode" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            orca.setLocusOfFocus(event, obj)
            self.enableStickyFocusMode(None, True)
            return True

        if self.useFocusMode(obj) != self._inFocusMode:
            self.togglePresentationMode(None)

        if not obj:
            msg = "WEB: Could not get caret context"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.isFocusModeWidget(obj):
            msg = "WEB: Setting locus of focus to focusModeWidget %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            orca.setLocusOfFocus(event, obj)
            return True

        state = obj.getState()
        if self.utilities.isLink(obj) and state.contains(pyatspi.STATE_FOCUSED):
            msg = "WEB: Setting locus of focus to focused link %s. No SayAll." % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            orca.setLocusOfFocus(event, obj)
            return True

        if offset > 0:
            msg = "WEB: Setting locus of focus to context obj %s. No SayAll" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            orca.setLocusOfFocus(event, obj)
            return True

        try:
            focusState = orca_state.locusOfFocus.getState()
        except:
            inFocusedObject = False
        else:
            inFocusedObject = focusState.contains(pyatspi.STATE_FOCUSED)

        if not inFocusedObject:
            msg = "WEB: Setting locus of focus to context obj %s (no notification)" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            orca.setLocusOfFocus(event, obj, False)

        self.updateBraille(obj)
        if self.utilities.documentFragment(event.source):
            msg = "WEB: Not doing SayAll due to page fragment"
            debug.println(debug.LEVEL_INFO, msg, True)
        elif not _settingsManager.getSetting('sayAllOnLoad'):
            msg = "WEB: Not doing SayAll due to sayAllOnLoad being False"
            debug.println(debug.LEVEL_INFO, msg, True)
            self.speakContents(self.utilities.getLineContentsAtOffset(obj, offset))
        elif _settingsManager.getSetting('enableSpeech'):
            msg = "WEB: Doing SayAll"
            debug.println(debug.LEVEL_INFO, msg, True)
            self.sayAll(None)
        else:
            msg = "WEB: Not doing SayAll due to enableSpeech being False"
            debug.println(debug.LEVEL_INFO, msg, True)

        return True

    def onCaretMoved(self, event):
        """Callback for object:text-caret-moved accessibility events."""

        self.utilities.sanityCheckActiveWindow()

        if self.utilities.isZombie(event.source):
            msg = "WEB: Event source is Zombie"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if not self.utilities.inDocumentContent(event.source):
            msg = "WEB: Event source is not in document content"
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if self._lastCommandWasCaretNav:
            msg = "WEB: Event ignored: Last command was caret nav"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if self._lastCommandWasStructNav:
            msg = "WEB: Event ignored: Last command was struct nav"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if self._lastCommandWasMouseButton:
            if (event.source, event.detail1) == self.utilities.getCaretContext():
                msg = "WEB: Event is for current caret context."
                debug.println(debug.LEVEL_INFO, msg, True)
                return True

            msg = "WEB: Event handled: Last command was mouse button"
            debug.println(debug.LEVEL_INFO, msg, True)
            self.utilities.setCaretContext(event.source, event.detail1)
            notify = not self.utilities.isEntryDescendant(event.source)
            orca.setLocusOfFocus(event, event.source, notify, True)
            if orca_state.locusOfFocus == event.source:
                self.updateBraille(event.source)
            return True

        if self.utilities.inFindContainer():
            msg = "WEB: Event handled: Presenting find results"
            debug.println(debug.LEVEL_INFO, msg, True)
            self.presentFindResults(event.source, event.detail1)
            self._saveFocusedObjectInfo(orca_state.locusOfFocus)
            return True

        if self.utilities.inContextMenu():
            msg = "WEB: Event ignored: In context menu"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.eventIsAutocompleteNoise(event):
            msg = "WEB: Event ignored: Autocomplete noise"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.textEventIsDueToInsertion(event):
            msg = "WEB: Event handled: Updating position due to insertion"
            debug.println(debug.LEVEL_INFO, msg, True)
            self._saveLastCursorPosition(event.source, event.detail1)
            return True

        obj, offset = self.utilities.findFirstCaretContext(event.source, event.detail1)

        if self.utilities.caretMovedToSamePageFragment(event):
            msg = "WEB: Event handled: Caret moved to fragment"
            debug.println(debug.LEVEL_INFO, msg, True)
            self.utilities.setCaretContext(obj, offset)
            orca.setLocusOfFocus(event, obj)
            return True

        # We want to do this check after the same-page-fragment check because some
        # fragments start with non-navigable text objects.
        if self.utilities.textEventIsForNonNavigableTextObject(event):
            msg = "WEB: Event ignored: Event source is non-navigable text object"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.lastInputEventWasPageNav() \
           and not self.utilities.isLink(event.source) \
           and not event.source.getRole() == pyatspi.ROLE_COMBO_BOX:
            msg = "WEB: Event handled: Caret moved due to scrolling"
            debug.println(debug.LEVEL_INFO, msg, True)
            self.utilities.setCaretContext(obj, offset)
            orca.setLocusOfFocus(event, obj, force=True)
            return True

        if self.utilities.isContentEditableWithEmbeddedObjects(event.source):
            msg = "WEB: In content editable with embedded objects"
            debug.println(debug.LEVEL_INFO, msg, True)
            if not self.utilities.eventIsFromLocusOfFocusDocument(event):
                msg = "WEB: Event ignored: Not from locus of focus document"
                debug.println(debug.LEVEL_INFO, msg, True)
                return True

            self.utilities.setCaretContext(obj, offset)
            notify = not self.utilities.lastInputEventWasCharNav() \
                     and not self.utilities.isEntryDescendant(obj)
            orca.setLocusOfFocus(event, event.source, notify)
            return False

        text = self.utilities.queryNonEmptyText(event.source)
        if not text:
            if event.source.getRole() == pyatspi.ROLE_LINK:
                msg = "WEB: Event handled: Was for non-text link"
                debug.println(debug.LEVEL_INFO, msg, True)
                self.utilities.setCaretContext(event.source, event.detail1)
                orca.setLocusOfFocus(event, event.source)
            else:
                msg = "WEB: Event ignored: Was for non-text non-link"
                debug.println(debug.LEVEL_INFO, msg, True)
            return True

        char = text.getText(event.detail1, event.detail1+1)
        try:
            isEditable = obj.getState().contains(pyatspi.STATE_EDITABLE)
        except:
            isEditable = False

        if not char and not isEditable:
            msg = "WEB: Event ignored: Was for empty char in non-editable text"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if char == self.EMBEDDED_OBJECT_CHARACTER:
            if not self.utilities.isTextBlockElement(obj):
                msg = "WEB: Event ignored: Was for embedded non-textblock"
                debug.println(debug.LEVEL_INFO, msg, True)
                return True

            msg = "WEB: Setting locusOfFocus, context to: %s, %i" % (obj, offset)
            debug.println(debug.LEVEL_INFO, msg, True)
            self.utilities.setCaretContext(obj, offset)
            orca.setLocusOfFocus(event, obj)
            return True

        if self.utilities.treatEventAsSpinnerValueChange(event):
            msg = "WEB: Event handled as the value-change event we wish we'd get"
            debug.println(debug.LEVEL_INFO, msg, True)
            self.updateBraille(event.source)
            self._presentTextAtNewCaretPosition(event)
            return True

        if not _settingsManager.getSetting('caretNavigationEnabled') \
           or self._inFocusMode or isEditable:
            msg = "WEB: Setting locusOfFocus, context to: %s, %i" % (event.source, event.detail1)
            debug.println(debug.LEVEL_INFO, msg, True)
            self.utilities.setCaretContext(event.source, event.detail1)
            notify = event.source.getState().contains(pyatspi.STATE_FOCUSED)
            orca.setLocusOfFocus(event, event.source, notify)
            return False

        self.utilities.setCaretContext(obj, offset)
        msg = "WEB: Setting context to: %s, %i" % (obj, offset)
        debug.println(debug.LEVEL_INFO, msg, True)
        return False

    def onCheckedChanged(self, event):
        """Callback for object:state-changed:checked accessibility events."""

        if not self.utilities.inDocumentContent(event.source):
            msg = "WEB: Event source is not in document content"
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        obj, offset = self.utilities.getCaretContext()
        if obj != event.source:
            msg = "WEB: Event source is not context object"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        oldObj, oldState = self.pointOfReference.get('checkedChange', (None, 0))
        if hash(oldObj) == hash(obj) and oldState == event.detail1:
            msg = "WEB: Ignoring event, state hasn't changed"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        role = obj.getRole()
        if not (self._lastCommandWasCaretNav and role == pyatspi.ROLE_RADIO_BUTTON):
            msg = "WEB: Event is something default can handle"
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        self.updateBraille(obj)
        speech.speak(self.speechGenerator.generateSpeech(obj, alreadyFocused=True))
        self.pointOfReference['checkedChange'] = hash(obj), event.detail1
        return True

    def onChildrenChanged(self, event):
        """Callback for object:children-changed accessibility events."""

        if self.utilities.eventIsBrowserUINoise(event):
            msg = "WEB: Ignoring event believed to be browser UI noise"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        document = self.utilities.getDocumentForObject(event.source)
        if document:
            msg = "WEB: Clearing structural navigation cache for %s" % document
            debug.println(debug.LEVEL_INFO, msg, True)
            self.structuralNavigation.clearCache(document)
        else:
            msg = "WEB: Could not get document for event source"
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if self.utilities.handleAsLiveRegion(event):
            msg = "WEB: Event to be handled as live region"
            debug.println(debug.LEVEL_INFO, msg, True)
            self.liveRegionManager.handleEvent(event)
            return True

        if self._loadingDocumentContent:
            msg = "WEB: Ignoring because document content is being loaded."
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.isZombie(document):
            msg = "WEB: Ignoring because %s is zombified." % document
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        try:
            docIsBusy = document.getState().contains(pyatspi.STATE_BUSY)
        except:
            docIsBusy = False
            msg = "WEB: Exception getting state of %s" % document
            debug.println(debug.LEVEL_INFO, msg, True)
        if docIsBusy:
            msg = "WEB: Ignoring because %s is busy." % document
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if not event.any_data or self.utilities.isZombie(event.any_data):
            msg = "WEB: Ignoring because any data is null or zombified."
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.handleEventFromContextReplicant(event, event.any_data):
            msg = "WEB: Event handled by updating locusOfFocus and context to child."
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        obj, offset = self.utilities.getCaretContext(getZombieReplicant=False)
        msg = "WEB: Context: %s, %i (focus: %s)" % (obj, offset, orca_state.locusOfFocus)
        debug.println(debug.LEVEL_INFO, msg, True)

        if self.utilities.isZombie(obj):
            obj, offset = self.utilities.getCaretContext(getZombieReplicant=True)
            if not obj:
                if self._inFocusMode:
                    if event.source.getState().contains(pyatspi.STATE_FOCUSED) \
                       and not self.utilities.isTextBlockElement(event.source):
                        msg = "WEB: Event handled by updating locusOfFocus and context"
                        debug.println(debug.LEVEL_INFO, msg, True)
                        orca.setLocusOfFocus(event, event.source, False)
                        self.utilities.setCaretContext(event.source, 0)
                        return True

                    msg = "WEB: Not looking for replicant due to focus mode."
                    debug.println(debug.LEVEL_INFO, msg, True)
                    return False

                obj = self.utilities.findReplicant(event.source, obj)
                if obj:
                    # Refrain from actually touching the replicant by grabbing
                    # focus or setting the caret in it. Doing so will only serve
                    # to anger it.
                    msg = "WEB: Event handled by updating locusOfFocus and context"
                    debug.println(debug.LEVEL_INFO, msg, True)
                    orca.setLocusOfFocus(event, obj, False)
                    self.utilities.setCaretContext(obj, offset)
                    return True

        childRole = event.any_data.getRole()
        if childRole == pyatspi.ROLE_ALERT:
            if event.any_data == self.utilities.lastQueuedLiveRegion():
                msg = "WEB: Ignoring %s (is last queued live region)" % event.any_data
                debug.println(debug.LEVEL_INFO, msg, True)
                return True

            msg = "WEB: Presenting event.any_data"
            debug.println(debug.LEVEL_INFO, msg, True)
            self.presentObject(event.any_data)

            focused = self.utilities.focusedObject(event.any_data)
            if focused:
                notify = self.utilities.queryNonEmptyText(focused) is None
                msg = "WEB: Setting locusOfFocus and caret context to %s" % focused
                debug.println(debug.LEVEL_INFO, msg)
                orca.setLocusOfFocus(event, focused, notify)
                self.utilities.setCaretContext(focused, 0)
            return True

        if childRole == pyatspi.ROLE_DIALOG:
            msg = "WEB: Setting locusOfFocus to event.any_data"
            debug.println(debug.LEVEL_INFO, msg, True)
            orca.setLocusOfFocus(event, event.any_data)
            return True

        if self.lastMouseRoutingTime and 0 < time.time() - self.lastMouseRoutingTime < 1:
            utterances = []
            utterances.append(messages.NEW_ITEM_ADDED)
            utterances.extend(self.speechGenerator.generateSpeech(child, force=True))
            speech.speak(utterances)
            self._lastMouseOverObject = event.any_data
            self.preMouseOverContext = self.utilities.getCaretContext()
            return True

        return False

    def onDocumentLoadComplete(self, event):
        """Callback for document:load-complete accessibility events."""

        if self.utilities.getDocumentForObject(event.source.parent):
            msg = "WEB: Ignoring: Event source is nested document"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        msg = "WEB: Updating loading state and resetting live regions"
        debug.println(debug.LEVEL_INFO, msg, True)
        self._loadingDocumentContent = False
        self.liveRegionManager.reset()
        return True

    def onDocumentLoadStopped(self, event):
        """Callback for document:load-stopped accessibility events."""

        if self.utilities.getDocumentForObject(event.source.parent):
            msg = "WEB: Ignoring: Event source is nested document"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        msg = "WEB: Updating loading state"
        debug.println(debug.LEVEL_INFO, msg, True)
        self._loadingDocumentContent = False
        return True

    def onDocumentReload(self, event):
        """Callback for document:reload accessibility events."""

        if self.utilities.getDocumentForObject(event.source.parent):
            msg = "WEB: Ignoring: Event source is nested document"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        msg = "WEB: Updating loading state"
        debug.println(debug.LEVEL_INFO, msg, True)
        self._loadingDocumentContent = True
        return True

    def onExpandedChanged(self, event):
        """Callback for object:state-changed:expanded accessibility events."""

        if self.utilities.isZombie(event.source):
            msg = "WEB: Event source is Zombie"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if not self.utilities.inDocumentContent(event.source):
            msg = "WEB: Event source is not in document content"
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        return False

    def onFocus(self, event):
        """Callback for focus: accessibility events."""

        # We should get proper state-changed events for these.
        if self.utilities.inDocumentContent(event.source):
            msg = "WEB: Ignoring because object:state-changed-focused expected."
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        return False

    def onFocusedChanged(self, event):
        """Callback for object:state-changed:focused accessibility events."""

        if not event.detail1:
            msg = "WEB: Ignoring because event source lost focus"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.isZombie(event.source):
            msg = "WEB: Event source is Zombie"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        document = self.utilities.getDocumentForObject(event.source)
        if not document:
            msg = "WEB: Could not get document for event source"
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if self.utilities.isTopLevelWebApp(document):
            if self._browseModeIsSticky:
                msg = "WEB: Web app claimed focus, but browse mode is sticky"
                debug.println(debug.LEVEL_INFO, msg, True)
            else:
                msg = "WEB: Event handled: Setting locusOfFocus to event source"
                debug.println(debug.LEVEL_INFO, msg, True)
                orca.setLocusOfFocus(event, event.source)
                return True

        state = event.source.getState()
        if state.contains(pyatspi.STATE_EDITABLE):
            msg = "WEB: Event source is editable"
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        role = event.source.getRole()
        if role in [pyatspi.ROLE_DIALOG, pyatspi.ROLE_ALERT]:
            msg = "WEB: Event handled: Setting locusOfFocus to event source"
            debug.println(debug.LEVEL_INFO, msg, True)
            orca.setLocusOfFocus(event, event.source)
            return True

        if self.utilities.handleEventFromContextReplicant(event, event.source):
            msg = "WEB: Event handled by updating locusOfFocus and context to source."
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        obj, offset = self.utilities.getCaretContext()
        msg = "WEB: Caret context is %s, %i (focus: %s)" \
              % (obj, offset, orca_state.locusOfFocus)
        debug.println(debug.LEVEL_INFO, msg, True)

        if not obj or self.utilities.isZombie(obj):
            msg = "WEB: Clearing context - obj is null or zombie"
            debug.println(debug.LEVEL_INFO, msg, True)
            self.utilities.clearCaretContext()

            obj, offset = self.utilities.searchForCaretContext(event.source)
            if obj:
                notify = self.utilities.inFindContainer(orca_state.locusOfFocus)
                msg = "WEB: Updating focus and context to %s, %i" % (obj, offset)
                debug.println(debug.LEVEL_INFO, msg, True)
                orca.setLocusOfFocus(event, obj, notify)
                self.utilities.setCaretContext(obj, offset)
            else:
                msg = "WEB: Search for caret context failed"
                debug.println(debug.LEVEL_INFO, msg, True)

        if self._lastCommandWasCaretNav:
            msg = "WEB: Event ignored: Last command was caret nav"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if self._lastCommandWasStructNav:
            msg = "WEB: Event ignored: Last command was struct nav"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if not state.contains(pyatspi.STATE_FOCUSABLE) \
           and not state.contains(pyatspi.STATE_FOCUSED):
            msg = "WEB: Event ignored: Source is not focusable or focused"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if not role in [pyatspi.ROLE_DOCUMENT_FRAME, pyatspi.ROLE_DOCUMENT_WEB]:
            msg = "WEB: Deferring to other scripts for handling non-document source"
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if not obj:
            msg = "WEB: Unable to get non-null, non-zombie context object"
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if self.utilities.lastInputEventWasPageNav():
            msg = "WEB: Event handled: Focus changed due to scrolling"
            debug.println(debug.LEVEL_INFO, msg, True)
            orca.setLocusOfFocus(event, obj)
            self.utilities.setCaretContext(obj, offset)
            return True

        wasFocused = obj.getState().contains(pyatspi.STATE_FOCUSED)
        obj.clearCache()
        isFocused = obj.getState().contains(pyatspi.STATE_FOCUSED)
        if wasFocused != isFocused:
            msg = "WEB: Focused state of %s changed to %s" % (obj, isFocused)
            debug.println(debug.LEVEL_INFO, msg, True)
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

        msg = "WEB: Event handled: Setting locusOfFocus to %s (%s)" % (obj, cause)
        debug.println(debug.LEVEL_INFO, msg, True)
        orca.setLocusOfFocus(event, obj)
        return True

    def onMouseButton(self, event):
        """Callback for mouse:button accessibility events."""

        self._lastCommandWasCaretNav = False
        self._lastCommandWasStructNav = False
        self._lastCommandWasMouseButton = True
        return False

    def onNameChanged(self, event):
        """Callback for object:property-change:accessible-name events."""

        if self.utilities.eventIsBrowserUINoise(event):
            msg = "WEB: Ignoring event believed to be browser UI noise"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        return True

    def onSelectedChanged(self, event):
        """Callback for object:state-changed:selected accessibility events."""

        if self.utilities.eventIsBrowserUIAutocompleteNoise(event):
            msg = "WEB: Ignoring event believed to be browser UI autocomplete noise"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.eventIsBrowserUIPageSwitch(event):
            msg = "WEB: Event believed to be browser UI page switch"
            debug.println(debug.LEVEL_INFO, msg, True)
            if event.detail1:
                self.presentObject(event.source, priorObj=orca_state.locusOfFocus)
            return True

        if not self.utilities.inDocumentContent(event.source):
            msg = "WEB: Event source is not in document content"
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if orca_state.locusOfFocus != event.source:
            msg = "WEB: Ignoring because event source is not locusOfFocus"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        return False

    def onSelectionChanged(self, event):
        """Callback for object:selection-changed accessibility events."""

        if self.utilities.eventIsBrowserUIAutocompleteNoise(event):
            msg = "WEB: Ignoring event believed to be browser UI autocomplete noise"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.eventIsBrowserUIPageSwitch(event):
            msg = "WEB: Ignoring event believed to be browser UI page switch"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if not self.utilities.inDocumentContent(event.source):
            msg = "WEB: Event source is not in document content"
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if not self.utilities.inDocumentContent(orca_state.locusOfFocus):
            msg = "WEB: Event ignored: locusOfFocus (%s) is not in document content" \
                  % orca_state.locusOfFocus
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if not self.utilities.eventIsFromLocusOfFocusDocument(event):
            msg = "WEB: Event ignored: Not from locus of focus document"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        obj, offset = self.utilities.getCaretContext()
        ancestor = self.utilities.commonAncestor(obj, event.source)
        if ancestor and self.utilities.isTextBlockElement(ancestor):
            msg = "WEB: Ignoring: Common ancestor of context and event source is text block"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        return False

    def onShowingChanged(self, event):
        """Callback for object:state-changed:showing accessibility events."""

        if event.detail1 and self.utilities.isTopLevelBrowserUIAlert(event.source):
            msg = "WEB: Event handled: Presenting event source"
            debug.println(debug.LEVEL_INFO, msg, True)
            self.presentObject(event.source)
            return True

        if not self.utilities.inDocumentContent(event.source):
            msg = "WEB: Event source is not in document content"
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        return True

    def onTextDeleted(self, event):
        """Callback for object:text-changed:delete accessibility events."""

        if self.utilities.isZombie(event.source):
            msg = "WEB: Event source is Zombie"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.eventIsBrowserUINoise(event):
            msg = "WEB: Ignoring event believed to be browser UI noise"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if not self.utilities.inDocumentContent(event.source):
            msg = "WEB: Event source is not in document content"
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if self.utilities.eventIsAutocompleteNoise(event):
            msg = "WEB: Ignoring event believed to be autocomplete noise"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.eventIsSpinnerNoise(event):
            msg = "WEB: Ignoring: Event believed to be spinner noise"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.textEventIsDueToDeletion(event):
            msg = "WEB: Event believed to be due to editable text deletion"
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if self.utilities.textEventIsDueToInsertion(event):
            msg = "WEB: Ignoring event believed to be due to text insertion"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        obj, offset = self.utilities.getCaretContext(getZombieReplicant=False)
        if obj and obj != event.source \
           and not pyatspi.findAncestor(obj, lambda x: x == event.source):
            msg = "WEB: Ignoring event because it isn't %s or its ancestor" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.isZombie(obj):
            if self.utilities.isLink(obj):
                msg = "WEB: Focused link deleted. Taking no further action."
                debug.println(debug.LEVEL_INFO, msg, True)
                return True

            obj, offset = self.utilities.getCaretContext(getZombieReplicant=True)
            if obj:
                orca.setLocusOfFocus(event, obj, notifyScript=False)

        if self.utilities.isZombie(obj):
            msg = "WEB: Unable to get non-null, non-zombie context object"
            debug.println(debug.LEVEL_INFO, msg, True)

        msg = "WEB: Clearing content cache due to text deletion"
        debug.println(debug.LEVEL_INFO, msg, True)
        self.utilities.clearContentCache()

        document = self.utilities.getDocumentForObject(event.source)
        if document:
            msg = "WEB: Clearing structural navigation cache for %s" % document
            debug.println(debug.LEVEL_INFO, msg, True)
            self.structuralNavigation.clearCache(document)

        if not event.source.getState().contains(pyatspi.STATE_EDITABLE) \
           and not self.utilities.isContentEditableWithEmbeddedObjects(event.source):
            if self._inMouseOverObject \
               and self.utilities.isZombie(self._lastMouseOverObject):
                msg = "WEB: Restoring pre-mouseover context"
                debug.println(debug.LEVEL_INFO, msg, True)
                self.restorePreMouseOverContext()

            msg = "WEB: Done processing non-editable source"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        return False

    def onTextInserted(self, event):
        """Callback for object:text-changed:insert accessibility events."""

        if self.utilities.isZombie(event.source):
            msg = "WEB: Event source is Zombie"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.eventIsBrowserUINoise(event):
            msg = "WEB: Ignoring event believed to be browser UI noise"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if not self.utilities.inDocumentContent(event.source):
            msg = "WEB: Event source is not in document content"
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if self.utilities.eventIsAutocompleteNoise(event):
            msg = "WEB: Ignoring: Event believed to be autocomplete noise"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.eventIsSpinnerNoise(event):
            msg = "WEB: Ignoring: Event believed to be spinner noise"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.eventIsEOCAdded(event):
            msg = "WEB: Ignoring: Event was for embedded object char"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        msg = "WEB: Clearing content cache due to text insertion"
        debug.println(debug.LEVEL_INFO, msg, True)
        self.utilities.clearContentCache()

        if self.utilities.handleAsLiveRegion(event):
            msg = "WEB: Event to be handled as live region"
            debug.println(debug.LEVEL_INFO, msg, True)
            self.liveRegionManager.handleEvent(event)
            return True

        document = self.utilities.getDocumentForObject(event.source)
        if document:
            msg = "WEB: Clearing structural navigation cache for %s" % document
            debug.println(debug.LEVEL_INFO, msg, True)
            self.structuralNavigation.clearCache(document)

        text = self.utilities.queryNonEmptyText(event.source)
        if not text:
            msg = "WEB: Ignoring: Event source is not a text object"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        state = event.source.getState()
        if not state.contains(pyatspi.STATE_EDITABLE):
            if event.source != orca_state.locusOfFocus:
                msg = "WEB: Done processing non-editable, non-locusOfFocus source"
                debug.println(debug.LEVEL_INFO, msg, True)
                return True

            if self.utilities.isClickableElement(event.source):
                msg = "WEB: Event handled: Re-setting locusOfFocus to changed clickable"
                debug.println(debug.LEVEL_INFO, msg, True)
                orca.setLocusOfFocus(None, event.source, force=True)
                return True

        return False

    def onTextSelectionChanged(self, event):
        """Callback for object:text-selection-changed accessibility events."""

        if self.utilities.isZombie(event.source):
            msg = "WEB: Event source is Zombie"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if not self.utilities.inDocumentContent(event.source):
            msg = "WEB: Event source is not in document content"
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if not self.utilities.inDocumentContent(orca_state.locusOfFocus):
            msg = "WEB: Event ignored: locusOfFocus (%s) is not in document content" \
                  % orca_state.locusOfFocus
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.eventIsAutocompleteNoise(event):
            msg = "WEB: Ignoring: Event believed to be autocomplete noise"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.eventIsSpinnerNoise(event):
            msg = "WEB: Ignoring: Event believed to be spinner noise"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.textEventIsForNonNavigableTextObject(event):
            msg = "WEB: Ignoring event for non-navigable text object"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        text = self.utilities.queryNonEmptyText(event.source)
        if not text:
            msg = "WEB: Ignoring: Event source is not a text object"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.isContentEditableWithEmbeddedObjects(event.source):
            msg = "WEB: In content editable with embedded objects"
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        offset = text.caretOffset
        char = text.getText(offset, offset+1)
        if char == self.EMBEDDED_OBJECT_CHARACTER \
           and not self.utilities.lastInputEventWasCaretNavWithSelection() \
           and not self.utilities.lastInputEventWasCommand():
            msg = "WEB: Ignoring: Not selecting and event offset is at embedded object"
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        return False

    def onWindowActivated(self, event):
        """Callback for window:activate accessibility events."""

        msg = "WEB: Deferring to app/toolkit script"
        debug.println(debug.LEVEL_INFO, msg, True)
        return False

    def onWindowDeactivated(self, event):
        """Callback for window:deactivate accessibility events."""

        msg = "WEB: Clearing command state"
        debug.println(debug.LEVEL_INFO, msg, True)
        self._lastCommandWasCaretNav = False
        self._lastCommandWasStructNav = False
        self._lastCommandWasMouseButton = False
        return False

    def getTransferableAttributes(self):
        return {"_lastCommandWasCaretNav": self._lastCommandWasCaretNav,
                "_lastCommandWasStructNav": self._lastCommandWasStructNav,
                "_lastCommandWasMouseButton": self._lastCommandWasMouseButton,
                "_inFocusMode": self._inFocusMode,
                "_focusModeIsSticky": self._focusModeIsSticky,
                "_browseModeIsSticky": self._browseModeIsSticky,
        }
