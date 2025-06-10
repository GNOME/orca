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
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from orca import caret_navigation
from orca import cmdnames
from orca import keybindings
from orca import debug
from orca import focus_manager
from orca import guilabels
from orca import input_event
from orca import input_event_manager
from orca import liveregions
from orca import messages
from orca import settings
from orca import settings_manager
from orca import speech
from orca import speechserver
from orca import structural_navigation
from orca.acss import ACSS
from orca.scripts import default
from orca.ax_document import AXDocument
from orca.ax_event_synthesizer import AXEventSynthesizer
from orca.ax_object import AXObject
from orca.ax_table import AXTable
from orca.ax_text import AXText
from orca.ax_utilities import AXUtilities

from .bookmarks import Bookmarks
from .braille_generator import BrailleGenerator
from .speech_generator import SpeechGenerator
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

        if settings_manager.get_manager().get_setting('caretNavigationEnabled') is None:
            settings_manager.get_manager().set_setting('caretNavigationEnabled', True)
        if settings_manager.get_manager().get_setting('sayAllOnLoad') is None:
            settings_manager.get_manager().set_setting('sayAllOnLoad', True)
        if settings_manager.get_manager().get_setting('pageSummaryOnLoad') is None:
            settings_manager.get_manager().set_setting('pageSummaryOnLoad', True)

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

    def activate(self):
        """Called when this script is activated."""

        tokens = ["WEB: Activating script for", self.app]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        in_doc = self.utilities.inDocumentContent()
        reason = f"script activation, in document content: {in_doc}"
        self.caret_navigation.suspend_commands(self, not in_doc, reason)
        self.structural_navigation.suspend_commands(self, not in_doc, reason)
        self.live_region_manager.suspend_commands(self, not in_doc, reason)
        self.get_table_navigator().suspend_commands(self, not in_doc, reason)
        super().activate()

    def deactivate(self):
        """Called when this script is deactivated."""

        self._sayAllContents = []
        self._loadingDocumentContent = False
        self._madeFindAnnouncement = False
        self._lastMouseButtonContext = None, -1
        self._lastMouseOverObject = None
        self._preMouseOverContext = None, -1
        self._inMouseOverObject = False
        self.utilities.clearCachedObjects()
        reason = "script deactivation"
        self.caret_navigation.suspend_commands(self, False, reason)
        self.structural_navigation.suspend_commands(self, False, reason)
        self.live_region_manager.suspend_commands(self, False, reason)
        self.get_table_navigator().suspend_commands(self, False, reason)
        super().deactivate()

    def get_app_key_bindings(self):
        """Returns the application-specific keybindings for this script."""

        keyBindings = keybindings.KeyBindings()

        layout = settings_manager.get_manager().get_setting('keyboardLayout')
        isDesktop = layout == settings.GENERAL_KEYBOARD_LAYOUT_DESKTOP

        structNavBindings = self.structural_navigation.get_bindings(
            refresh=True, is_desktop=isDesktop)
        for keyBinding in structNavBindings.key_bindings:
            keyBindings.add(keyBinding)

        caretNavBindings = self.caret_navigation.get_bindings(
            refresh=True, is_desktop=isDesktop)
        for keyBinding in caretNavBindings.key_bindings:
            keyBindings.add(keyBinding)

        liveRegionBindings = self.live_region_manager.get_bindings(
            refresh=True, is_desktop=isDesktop)
        for keyBinding in liveRegionBindings.key_bindings:
            keyBindings.add(keyBinding)

        keyBindings.add(
            keybindings.KeyBinding(
                "a",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self.input_event_handlers.get("togglePresentationModeHandler")))

        keyBindings.add(
            keybindings.KeyBinding(
                "a",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self.input_event_handlers.get("enableStickyFocusModeHandler"),
                2))

        keyBindings.add(
            keybindings.KeyBinding(
                "a",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self.input_event_handlers.get("enableStickyBrowseModeHandler"),
                3))

        keyBindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self.input_event_handlers.get("toggleLayoutModeHandler")))


        layout = settings_manager.get_manager().get_setting('keyboardLayout')
        if layout == settings.GENERAL_KEYBOARD_LAYOUT_DESKTOP:
            key = "KP_Multiply"
        else:
            key = "0"

        keyBindings.add(
            keybindings.KeyBinding(
                key,
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self.input_event_handlers.get("moveToMouseOverHandler")))

        return keyBindings

    def setup_input_event_handlers(self):
        """Defines the input event handlers for this script."""

        super().setup_input_event_handlers()
        self.input_event_handlers.update(self.structural_navigation.get_handlers(True))
        self.input_event_handlers.update(self.caret_navigation.get_handlers(True))
        self.input_event_handlers.update(self.live_region_manager.get_handlers(True))

        self.input_event_handlers["panBrailleLeftHandler"] = \
            input_event.InputEventHandler(
                Script.pan_braille_left,
                cmdnames.PAN_BRAILLE_LEFT,
                False) # Do not enable learn mode for this action

        self.input_event_handlers["panBrailleRightHandler"] = \
            input_event.InputEventHandler(
                Script.pan_braille_right,
                cmdnames.PAN_BRAILLE_RIGHT,
                False) # Do not enable learn mode for this action

        self.input_event_handlers["moveToMouseOverHandler"] = \
            input_event.InputEventHandler(
                Script.moveToMouseOver,
                cmdnames.MOUSE_OVER_MOVE)

        self.input_event_handlers["togglePresentationModeHandler"] = \
            input_event.InputEventHandler(
                Script.togglePresentationMode,
                cmdnames.TOGGLE_PRESENTATION_MODE)

        self.input_event_handlers["enableStickyFocusModeHandler"] = \
            input_event.InputEventHandler(
                Script.enableStickyFocusMode,
                cmdnames.SET_FOCUS_MODE_STICKY)

        self.input_event_handlers["enableStickyBrowseModeHandler"] = \
            input_event.InputEventHandler(
                Script.enableStickyBrowseMode,
                cmdnames.SET_BROWSE_MODE_STICKY)

        self.input_event_handlers["toggleLayoutModeHandler"] = \
            input_event.InputEventHandler(
                Script.toggleLayoutMode,
                cmdnames.TOGGLE_LAYOUT_MODE)

    def get_bookmarks(self):
        """Returns the "bookmarks" class for this script."""

        try:
            return self.bookmarks
        except AttributeError:
            self.bookmarks = Bookmarks(self)
            return self.bookmarks

    def get_braille_generator(self):
        """Returns the braille generator for this script."""

        return BrailleGenerator(self)

    def get_caret_navigation(self):
        """Returns the caret navigation support for this script."""

        return caret_navigation.CaretNavigation()

    def get_enabled_structural_navigation_types(self):
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
                structural_navigation.StructuralNavigation.UNVISITED_LINK,
                structural_navigation.StructuralNavigation.VISITED_LINK]

    def get_live_region_manager(self):
        """Returns the live region support for this script."""

        return liveregions.LiveRegionManager(self)

    def get_speech_generator(self):
        """Returns the speech generator for this script."""

        return SpeechGenerator(self)

    def get_utilities(self):
        """Returns the utilities for this script."""

        return Utilities(self)

    def get_app_preferences_gui(self):
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
        value = settings_manager.get_manager().get_setting('caretNavigationEnabled')
        self._controlCaretNavigationCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self._controlCaretNavigationCheckButton.set_active(value)
        generalGrid.attach(self._controlCaretNavigationCheckButton, 0, 0, 1, 1)

        label = guilabels.AUTO_FOCUS_MODE_CARET_NAV
        value = settings_manager.get_manager().get_setting('caretNavTriggersFocusMode')
        self._autoFocusModeCaretNavCheckButton = Gtk.CheckButton.new_with_mnemonic(label)
        self._autoFocusModeCaretNavCheckButton.set_active(value)
        generalGrid.attach(self._autoFocusModeCaretNavCheckButton, 0, 1, 1, 1)

        label = guilabels.USE_STRUCTURAL_NAVIGATION
        value = self.structural_navigation.enabled
        self._structuralNavigationCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self._structuralNavigationCheckButton.set_active(value)
        generalGrid.attach(self._structuralNavigationCheckButton, 0, 2, 1, 1)

        label = guilabels.AUTO_FOCUS_MODE_STRUCT_NAV
        value = settings_manager.get_manager().get_setting('structNavTriggersFocusMode')
        self._autoFocusModeStructNavCheckButton = Gtk.CheckButton.new_with_mnemonic(label)
        self._autoFocusModeStructNavCheckButton.set_active(value)
        generalGrid.attach(self._autoFocusModeStructNavCheckButton, 0, 3, 1, 1)

        label = guilabels.AUTO_FOCUS_MODE_NATIVE_NAV
        value = settings_manager.get_manager().get_setting('nativeNavTriggersFocusMode')
        self._autoFocusModeNativeNavCheckButton = Gtk.CheckButton.new_with_mnemonic(label)
        self._autoFocusModeNativeNavCheckButton.set_active(value)
        generalGrid.attach(self._autoFocusModeNativeNavCheckButton, 0, 4, 1, 1)

        label = guilabels.READ_PAGE_UPON_LOAD
        value = settings_manager.get_manager().get_setting('sayAllOnLoad')
        self._sayAllOnLoadCheckButton = Gtk.CheckButton.new_with_mnemonic(label)
        self._sayAllOnLoadCheckButton.set_active(value)
        generalGrid.attach(self._sayAllOnLoadCheckButton, 0, 5, 1, 1)

        label = guilabels.PAGE_SUMMARY_UPON_LOAD
        value = settings_manager.get_manager().get_setting('pageSummaryOnLoad')
        self._pageSummaryOnLoadCheckButton = Gtk.CheckButton.new_with_mnemonic(label)
        self._pageSummaryOnLoadCheckButton.set_active(value)
        generalGrid.attach(self._pageSummaryOnLoadCheckButton, 0, 6, 1, 1)

        label = guilabels.CONTENT_LAYOUT_MODE
        value = settings_manager.get_manager().get_setting('layoutMode')
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
        value = settings_manager.get_manager().get_setting('speakCellCoordinates')
        self._speakCellCoordinatesCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self._speakCellCoordinatesCheckButton.set_active(value)
        tableGrid.attach(self._speakCellCoordinatesCheckButton, 0, 0, 1, 1)

        label = guilabels.TABLE_SPEAK_CELL_SPANS
        value = settings_manager.get_manager().get_setting('speakCellSpan')
        self._speakCellSpanCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self._speakCellSpanCheckButton.set_active(value)
        tableGrid.attach(self._speakCellSpanCheckButton, 0, 1, 1, 1)

        label = guilabels.TABLE_ANNOUNCE_CELL_HEADER
        value = settings_manager.get_manager().get_setting('speakCellHeaders')
        self._speakCellHeadersCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self._speakCellHeadersCheckButton.set_active(value)
        tableGrid.attach(self._speakCellHeadersCheckButton, 0, 2, 1, 1)

        label = guilabels.TABLE_SKIP_BLANK_CELLS
        value = settings_manager.get_manager().get_setting('skipBlankCells')
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

        verbosity = settings_manager.get_manager().get_setting('findResultsVerbosity')

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
            Gtk.Adjustment(settings_manager.get_manager().get_setting(
                'findResultsMinimumLength'), 0, 20, 1)
        self._minimumFindLengthSpinButton = Gtk.SpinButton()
        self._minimumFindLengthSpinButton.set_adjustment(
            self._minimumFindLengthAdjustment)
        hgrid.attach(self._minimumFindLengthSpinButton, 1, 0, 1, 1)
        self._minimumFindLengthLabel.set_mnemonic_widget(
            self._minimumFindLengthSpinButton)

        grid.show_all()
        return grid

    def get_preferences_from_gui(self):
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

    def presentationInterrupt(self, killFlash=True):
        super().presentationInterrupt(killFlash)
        msg = "WEB: Flushing live region messages"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        self.live_region_manager.flushMessages()

    # TODO - JD: This needs to be moved out of the scripts.
    def textLines(self, obj, offset=None):
        """Creates a generator that can be used to iterate document content."""

        if not self.utilities.inDocumentContent():
            tokens = ["WEB: textLines called for non-document content", obj]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            super().textLines(obj, offset)
            return

        self._sayAllIsInterrupted = False

        sayAllStyle = settings_manager.get_manager().get_setting('sayAllStyle')
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

                utterances = self.speech_generator.generate_contents(
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
                    self.get_event_synthesizer().scroll_into_view(obj, startOffset, endOffset)
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

        document = self.utilities.getDocumentForObject(obj)
        if not document:
            return

        start = AXText.get_selection_start_offset(obj)
        if start < 0:
            return

        offset = max(offset, start)
        context = self.utilities.getCaretContext(documentFrame=document)
        self.utilities.setCaretContext(obj, offset, documentFrame=document)

        end = AXText.get_selection_end_offset(obj)
        if end - start < settings_manager.get_manager().get_setting('findResultsMinimumLength'):
            return

        verbosity = settings_manager.get_manager().get_setting('findResultsVerbosity')
        if verbosity == settings.FIND_SPEAK_NONE:
            return

        if self._madeFindAnnouncement \
           and verbosity == settings.FIND_SPEAK_IF_LINE_CHANGED \
           and self.utilities.contextsAreOnSameLine(context, (obj, offset)):
            return

        contents = self.utilities.getLineContentsAtOffset(obj, offset)
        self.speakContents(contents)
        self.update_braille(obj)

        resultsCount = self.utilities.getFindResultsCount()
        if resultsCount:
            self.presentMessage(resultsCount)

        self._madeFindAnnouncement = True

    def _rewindSayAll(self, context, minCharCount=10):
        if not self.utilities.inDocumentContent():
            return super()._rewindSayAll(context, minCharCount)

        if not settings_manager.get_manager().get_setting('rewindAndFastForwardInSayAll'):
            return False

        try:
            obj, start, end, string = self._sayAllContents[0]
        except IndexError:
            return False

        focus_manager.get_manager().set_locus_of_focus(None, obj, notify_script=False)
        self.utilities.setCaretContext(obj, start)

        prevObj, prevOffset = self.utilities.findPreviousCaretInOrder(obj, start)
        self.say_all(None, prevObj, prevOffset)
        return True

    def _fastForwardSayAll(self, context):
        if not self.utilities.inDocumentContent():
            return super()._fastForwardSayAll(context)

        if not settings_manager.get_manager().get_setting('rewindAndFastForwardInSayAll'):
            return False

        try:
            obj, start, end, string = self._sayAllContents[-1]
        except IndexError:
            return False

        focus_manager.get_manager().set_locus_of_focus(None, obj, notify_script=False)
        self.utilities.setCaretContext(obj, end)

        nextObj, nextOffset = self.utilities.findNextCaretInOrder(obj, end)
        self.say_all(None, nextObj, nextOffset)
        return True

    def __sayAllProgressCallback(self, context, progressType):
        if not self.utilities.inDocumentContent():
            super().__sayAllProgressCallback(context, progressType)
            return

        if progressType == speechserver.SayAllContext.INTERRUPTED:
            manager = input_event_manager.get_manager()
            if manager.last_event_was_keyboard():
                self._sayAllIsInterrupted = True
                if manager.last_event_was_down() and self._fastForwardSayAll(context):
                    return
                if manager.last_event_was_up() and self._rewindSayAll(context):
                    return
                if not self.structural_navigation.last_input_event_was_navigation_command() \
                   and not self.get_table_navigator().last_input_event_was_navigation_command():
                    focus_manager.get_manager().emit_region_changed(
                        context.obj, context.currentOffset)
                    self.utilities.setCaretPosition(context.obj, context.currentOffset)
                    self.update_braille(context.obj)

            self._inSayAll = False
            self._sayAllContents = []
            self._sayAllContexts = []
            return

        focus_manager.get_manager().set_locus_of_focus(None, context.obj, notify_script=False)
        focus_manager.get_manager().emit_region_changed(
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
            self.structural_navigation.last_input_event_was_navigation_command() \
            or self.get_table_navigator().last_input_event_was_navigation_command()
        if not settings_manager.get_manager().get_setting('structNavTriggersFocusMode') \
           and lastCommandWasStructNav:
            msg = "WEB: Not using focus mode due to struct nav settings"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        if prevObj and AXObject.is_dead(prevObj):
            prevObj = None

        lastCommandWasCaretNav = self.caret_navigation.last_input_event_was_navigation_command()
        if not settings_manager.get_manager().get_setting('caretNavTriggersFocusMode') \
           and  lastCommandWasCaretNav \
           and not self.utilities.isNavigableToolTipDescendant(prevObj):
            msg = "WEB: Not using focus mode due to caret nav settings"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        if not settings_manager.get_manager().get_setting('nativeNavTriggersFocusMode') \
           and not (lastCommandWasStructNav or lastCommandWasCaretNav):
            msg = "WEB: Not changing focus/browse mode due to native nav settings"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return self._inFocusMode

        if self.utilities.isFocusModeWidget(obj):
            tokens = ["WEB: Using focus mode because", obj, "is a focus mode widget"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return True

        doNotToggle = AXUtilities.is_link(obj) or AXUtilities.is_radio_button(obj)
        if self._inFocusMode and doNotToggle \
           and input_event_manager.get_manager().last_event_was_unmodified_arrow():
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

        utterances = self.speech_generator.generate_contents(contents, **args)
        speech.speak(utterances)

    def sayCharacter(self, obj):
        """Speaks the character at the current caret position."""

        tokens = ["WEB: Say character for", obj]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        if not self.utilities.inDocumentContent(obj):
            msg = "WEB: Object is not in document content."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            super().sayCharacter(obj)
            return

        document = self.utilities.getTopLevelDocumentForObject(obj)
        obj, offset = self.utilities.getCaretContext(documentFrame=document)
        tokens = ["WEB: Adjusted object and offset for say character to", obj, offset]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        if not obj:
            return

        contents = None
        if self.utilities.treatAsEndOfLine(obj, offset) and AXObject.supports_text(obj):
            char = AXText.get_character_at_offset(offset)[0]
            if char == self.EMBEDDED_OBJECT_CHARACTER:
                char = ""
            contents = [[obj, offset, offset + 1, char]]
        else:
            contents = self.utilities.getCharacterContentsAtOffset(obj, offset)

        if not contents:
            return

        obj, start, end, string = contents[0]
        if start > 0 and string == "\n":
            if settings_manager.get_manager().get_setting("speakBlankLines"):
                self.speakMessage(messages.BLANK, interrupt=False)
                return

        if string:
            self.speakMisspelledIndicator(obj, start)
            self.speak_character(string)
        else:
            self.speakContents(contents)

        self.point_of_reference["lastTextUnitSpoken"] = "char"

    def sayWord(self, obj):
        """Speaks the word at the current caret position."""

        tokens = ["WEB: Say word for", obj]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        if not self.utilities.inDocumentContent(obj):
            msg = "WEB: Object is not in document content."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            super().sayWord(obj)
            return

        document = self.utilities.getTopLevelDocumentForObject(obj)
        obj, offset = self.utilities.getCaretContext(documentFrame=document)
        if input_event_manager.get_manager().last_event_was_right():
            offset -= 1

        tokens = ["WEB: Adjusted object and offset for say word to", obj, offset]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        wordContents = self.utilities.getWordContentsAtOffset(obj, offset, useCache=True)
        textObj, startOffset, endOffset, word = wordContents[0]
        self.speakMisspelledIndicator(textObj, startOffset)
        # TODO - JD: Clean up the focused + alreadyFocused mess which by side effect is causing
        # the content of some objects (e.g. table cells) to not be generated.
        self.speakContents(wordContents, alreadyFocused=AXUtilities.is_text_input(textObj))
        self.point_of_reference["lastTextUnitSpoken"] = "word"

    def sayLine(self, obj, offset=None):
        """Speaks the line at the current caret position."""

        tokens = ["WEB: Say line for", obj]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        if not self.utilities.inDocumentContent(obj):
            msg = "WEB: Object is not in document content."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            super().sayLine(obj)
            return

        # TODO - JD: We're making an exception here because the default script's sayLine()
        # handles verbalized punctuation, indentation, repeats, etc. That adjustment belongs
        # in the generators, but that's another potentially non-trivial change.
        if AXUtilities.is_editable(obj) and "\ufffc" not in AXText.get_line_at_offset(obj)[0]:
            msg = "WEB: Object is editable and line has no EOCs."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            if not self._inFocusMode:
                self.utilities.setCaretPosition(obj, 0)
            super().sayLine(obj)
            return

        document = self.utilities.getTopLevelDocumentForObject(obj)
        priorObj, _priorOffset = self.utilities.getPriorContext(documentFrame=document)

        if offset is None:
            obj, offset = self.utilities.getCaretContext(documentFrame=document)
            tokens = ["WEB: Adjusted object and offset for say line to", obj, offset]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)

        contents = self.utilities.getLineContentsAtOffset(obj, offset, useCache=True)
        if contents and contents[0] and not self._inFocusMode:
            self.utilities.setCaretPosition(contents[0][0], contents[0][1])

        self.speakContents(contents, priorObj=priorObj)
        self.point_of_reference["lastTextUnitSpoken"] = "line"

    def presentObject(self, obj, **args):
        if obj is None:
            return

        if not self.utilities.inDocumentContent(obj) or AXUtilities.is_document(obj):
            super().presentObject(obj, **args)
            return

        mode, _obj = focus_manager.get_manager().get_active_mode_and_object_of_interest()
        if mode in [focus_manager.OBJECT_NAVIGATOR, focus_manager.MOUSE_REVIEW]:
            super().presentObject(obj, **args)
            return

        if AXUtilities.is_status_bar(obj) or AXUtilities.is_alert(obj):
            if not self._inFocusMode:
                self.utilities.setCaretPosition(obj, 0)
            super().presentObject(obj, **args)
            return

        priorObj = args.get("priorObj")
        if self.caret_navigation.last_input_event_was_navigation_command() \
           or self.structural_navigation.last_input_event_was_navigation_command() \
           or self.get_table_navigator().last_input_event_was_navigation_command() \
           or args.get("includeContext") or AXTable.get_table(obj):
            priorObj, priorOffset = self.utilities.getPriorContext()
            args["priorObj"] = priorObj

        AXEventSynthesizer.scroll_to_center(obj, start_offset=0)

        if AXUtilities.is_entry(obj):
            if not self._inFocusMode:
                self.utilities.setCaretPosition(obj, 0)
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
        if contents and contents[0] and not self._inFocusMode:
            self.utilities.setCaretPosition(contents[0][0], contents[0][1])
        self.displayContents(contents)
        self.speakContents(contents, **args)

    def updateBrailleForNewCaretPosition(self, obj):
        """Try to reposition the cursor without having to do a full update."""

        if "\ufffc" in AXText.get_all_text(obj):
            self.update_braille(obj)
            return

        super().updateBrailleForNewCaretPosition(obj)

    def update_braille(self, obj, **args):
        """Updates the braille display to show the given object."""

        tokens = ["WEB: updating braille for", obj, args]
        debug.printTokens(debug.LEVEL_INFO, tokens, True, True)

        if not settings_manager.get_manager().get_setting('enableBraille') \
           and not settings_manager.get_manager().get_setting('enableBrailleMonitor'):
            debug.printMessage(debug.LEVEL_INFO, "BRAILLE: disabled", True)
            return

        if self._inFocusMode and "\ufffc" not in AXText.get_all_text(obj):
            tokens = ["WEB: updating braille in focus mode", obj]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            super().update_braille(obj, **args)
            return

        document = args.get("documentFrame", self.utilities.getTopLevelDocumentForObject(obj))
        if not document:
            tokens = ["WEB: updating braille for non-document object", obj]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            super().update_braille(obj, **args)
            return

        isContentEditable = self.utilities.isContentEditableWithEmbeddedObjects(obj)

        if not self.caret_navigation.last_input_event_was_navigation_command() \
           and not self.structural_navigation.last_input_event_was_navigation_command() \
           and not self.get_table_navigator().last_input_event_was_navigation_command() \
           and not isContentEditable \
           and not AXDocument.is_plain_text(document) \
           and not input_event_manager.get_manager().last_event_was_caret_selection():
            tokens = ["WEB: updating braille for unhandled navigation type", obj]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            super().update_braille(obj, **args)
            return

        # TODO - JD: Getting the caret context can, by side effect, update it. This in turn
        # can prevent us from presenting table column headers when braille is enabled because
        # we think they are not "new." Commit bd877203f0 addressed that, but we need to stop
        # such side effects from happening in the first place.
        offset = args.get("offset")
        if offset is None:
            obj, offset = self.utilities.getCaretContext(documentFrame=document, getReplicant=True)
        if offset > 0 and isContentEditable and self.utilities.treatAsTextObject(obj):
            offset = min(offset, AXText.get_character_count(obj))

        contents = self.utilities.getLineContentsAtOffset(obj, offset)
        self.displayContents(contents, documentFrame=document)

    def displayContents(self, contents, **args):
        """Displays contents in braille."""

        tokens = ["WEB: Displaying", contents, args]
        debug.printTokens(debug.LEVEL_INFO, tokens, True, True)

        if not settings_manager.get_manager().get_setting('enableBraille') \
           and not settings_manager.get_manager().get_setting('enableBrailleMonitor'):
            debug.printMessage(debug.LEVEL_INFO, "WEB: Braille disabled", True)
            return

        line = self.getNewBrailleLine(clearBraille=True, addLine=True)
        document = args.get("documentFrame")
        result = self.braille_generator.generate_contents(contents, documentFrame=document)
        if not result:
            msg = "WEB: Generating braille contents failed"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return

        regions, focusedRegion = result
        tokens = ["WEB: Generated result", regions, "focused region", focusedRegion]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        for region in regions:
            self.addBrailleRegionsToLine(region, line)

        if line.regions:
            line.regions[-1].string = line.regions[-1].string.rstrip(" ")

        self.setBrailleFocus(focusedRegion, getLinkMask=False)
        self.refreshBraille(panToCursor=True, getLinkMask=False)

    def pan_braille_left(self, inputEvent=None, pan_amount=0):
        """Pans braille to the left."""

        if self.get_flat_review_presenter().is_active() \
           or not self.utilities.inDocumentContent() \
           or not self.isBrailleBeginningShowing():
            super().pan_braille_left(inputEvent, pan_amount)
            return

        contents = self.utilities.getPreviousLineContents()
        if not contents:
            return

        obj, start, end, string = contents[0]
        self.utilities.setCaretPosition(obj, start)
        self.update_braille(obj)

        # Hack: When panning to the left in a document, we want to start at
        # the right/bottom of each new object. For now, we'll pan there.
        # When time permits, we'll give our braille code some smarts.
        while self.panBrailleInDirection(panToLeft=False):
            pass

        self.refreshBraille(False)
        return True

    def pan_braille_right(self, inputEvent=None, pan_amount=0):
        """Pans braille to the right."""

        if self.get_flat_review_presenter().is_active() \
           or not self.utilities.inDocumentContent() \
           or not self.isBrailleEndShowing():
            super().pan_braille_right(inputEvent, pan_amount)
            return

        contents = self.utilities.getNextLineContents()
        if not contents:
            return

        obj, start, end, string = contents[0]
        self.utilities.setCaretPosition(obj, start)
        self.update_braille(obj)

        # Hack: When panning to the right in a document, we want to start at
        # the left/top of each new object. For now, we'll pan there. When time
        # permits, we'll give our braille code some smarts.
        while self.panBrailleInDirection(panToLeft=True):
            pass

        self.refreshBraille(False)
        return True

    def moveToMouseOver(self, inputEvent):
        """Moves the context to/from the mouseover which has just appeared."""

        if not self._lastMouseOverObject:
            self.presentMessage(messages.MOUSE_OVER_NOT_FOUND)
            return

        if self._inMouseOverObject:
            self.restorePreMouseOverContext()
            return

        obj = self._lastMouseOverObject
        obj, offset = self.utilities.findFirstCaretContext(obj, 0)
        if not obj:
            return

        if AXUtilities.is_focusable(obj):
            AXObject.grab_focus(obj)

        contents = self.utilities.getObjectContentsAtOffset(obj, offset)
        self.utilities.setCaretPosition(obj, offset)
        self.speakContents(contents)
        self.update_braille(obj)
        self._inMouseOverObject = True

    def restorePreMouseOverContext(self):
        """Cleans things up after a mouse-over object has been hidden."""

        obj, offset = self._preMouseOverContext
        self.get_event_synthesizer().route_to_object(obj)
        self.utilities.setCaretPosition(obj, offset)
        self.speakContents(self.utilities.getObjectContentsAtOffset(obj, offset))
        self.update_braille(obj)
        self._inMouseOverObject = False
        self._lastMouseOverObject = None

    def enableStickyBrowseMode(self, inputEvent, forceMessage=False):
        if not self._browseModeIsSticky or forceMessage:
            self.presentMessage(messages.MODE_BROWSE_IS_STICKY)

        self._inFocusMode = False
        self._focusModeIsSticky = False
        self._browseModeIsSticky = True
        reason = "enable sticky browse mode"
        self.caret_navigation.suspend_commands(self, self._inFocusMode, reason)
        self.structural_navigation.suspend_commands(self, self._inFocusMode, reason)
        self.live_region_manager.suspend_commands(self, self._inFocusMode, reason)
        self.get_table_navigator().suspend_commands(self, self._inFocusMode, reason)

    def enableStickyFocusMode(self, inputEvent, forceMessage=False):
        if not self._focusModeIsSticky or forceMessage:
            self.presentMessage(messages.MODE_FOCUS_IS_STICKY)

        self._inFocusMode = True
        self._focusModeIsSticky = True
        self._browseModeIsSticky = False
        reason = "enable sticky focus mode"
        self.caret_navigation.suspend_commands(self, self._inFocusMode, reason)
        self.structural_navigation.suspend_commands(self, self._inFocusMode, reason)
        self.live_region_manager.suspend_commands(self, self._inFocusMode, reason)
        self.get_table_navigator().suspend_commands(self, self._inFocusMode, reason)

    def toggleLayoutMode(self, inputEvent):
        layoutMode = not settings_manager.get_manager().get_setting('layoutMode')
        if layoutMode:
            self.presentMessage(messages.MODE_LAYOUT)
        else:
            self.presentMessage(messages.MODE_OBJECT)
        settings_manager.get_manager().set_setting('layoutMode', layoutMode)

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
               and (self.caret_navigation.last_input_event_was_navigation_command() \
                    or self.structural_navigation.last_input_event_was_navigation_command() \
                    or self.get_table_navigator().last_input_event_was_navigation_command() \
                    or inputEvent):
                AXObject.grab_focus(obj)

            self.presentMessage(messages.MODE_FOCUS)
        self._inFocusMode = not self._inFocusMode
        self._focusModeIsSticky = False
        self._browseModeIsSticky = False

        reason = "toggling focus/browse mode"
        self.caret_navigation.suspend_commands(self, self._inFocusMode, reason)
        self.structural_navigation.suspend_commands(self, self._inFocusMode, reason)
        self.live_region_manager.suspend_commands(self, self._inFocusMode, reason)
        self.get_table_navigator().suspend_commands(self, self._inFocusMode, reason)

    def locus_of_focus_changed(self, event, old_focus, new_focus):
        """Handles changes of focus of interest to the script."""

        tokens = ["WEB: Focus changing from", old_focus, "to", new_focus]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        if new_focus and not AXObject.is_valid(new_focus):
            return True

        if new_focus and AXObject.is_dead(new_focus):
            return True

        document = self.utilities.getTopLevelDocumentForObject(new_focus)
        if not document and self.utilities.isDocument(new_focus):
            document = new_focus

        if not document:
            msg = "WEB: Locus of focus changed to non-document obj"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self._madeFindAnnouncement = False
            self._inFocusMode = False

            oldDocument = self.utilities.getTopLevelDocumentForObject(old_focus)
            if not document and self.utilities.isDocument(old_focus):
                oldDocument = old_focus

            if old_focus and not oldDocument:
                msg = "WEB: Not refreshing grabs because we weren't in a document before"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                return False

            tokens = ["WEB: Refreshing grabs because we left document", oldDocument]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)

            reason = "locus of focus no longer in document"
            self.caret_navigation.suspend_commands(self, True, reason)
            self.structural_navigation.suspend_commands(self, True, reason)
            self.live_region_manager.suspend_commands(self, True, reason)
            self.get_table_navigator().suspend_commands(self, True, reason)
            return False

        if self.get_flat_review_presenter().is_active():
            self.get_flat_review_presenter().quit()

        caretOffset = 0
        if self.utilities.inFindContainer(old_focus) \
           or (self.utilities.isDocument(new_focus) \
               and old_focus == focus_manager.get_manager().get_active_window()):
            contextObj, contextOffset = self.utilities.getCaretContext(documentFrame=document)
            if contextObj and AXObject.is_valid(contextObj):
                new_focus, caretOffset = contextObj, contextOffset

        if AXUtilities.is_unknown_or_redundant(new_focus):
            msg = "WEB: Event source has bogus role. Likely browser bug."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            new_focus, offset = self.utilities.findFirstCaretContext(new_focus, 0)

        if self.utilities.treatAsTextObject(new_focus):
            textOffset = AXText.get_caret_offset(new_focus)
            if 0 <= textOffset <= AXText.get_character_count(new_focus):
                caretOffset = textOffset

        self.utilities.setCaretContext(new_focus, caretOffset, document)
        self.update_braille(new_focus, documentFrame=document)

        contents = None
        args = {}
        lastCommandWasCaretNav = self.caret_navigation.last_input_event_was_navigation_command()
        lastCommandWasStructNav = \
            self.structural_navigation.last_input_event_was_navigation_command() \
            or self.get_table_navigator().last_input_event_was_navigation_command()
        manager = input_event_manager.get_manager()
        lastCommandWasLineNav = manager.last_event_was_line_navigation() \
            and not lastCommandWasCaretNav

        args["priorObj"] = old_focus
        if manager.last_event_was_mouse_button() and event \
             and event.type.startswith("object:text-caret-moved"):
            msg = "WEB: Last input event was mouse button. Generating line."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            contents = self.utilities.getLineContentsAtOffset(new_focus, caretOffset)
        elif self.utilities.isContentEditableWithEmbeddedObjects(new_focus) \
           and (lastCommandWasCaretNav or lastCommandWasStructNav or lastCommandWasLineNav) \
           and not (AXUtilities.is_table_cell(new_focus) and AXObject.get_name(new_focus)):
            tokens = ["WEB: New focus", new_focus, "content editable. Generating line."]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            contents = self.utilities.getLineContentsAtOffset(new_focus, caretOffset)
        elif self.utilities.isAnchor(new_focus):
            tokens = ["WEB: New focus", new_focus, "is anchor. Generating line."]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            contents = self.utilities.getLineContentsAtOffset(new_focus, 0)
        elif input_event_manager.get_manager().last_event_was_page_navigation() \
             and not AXTable.get_table(new_focus) \
             and not AXUtilities.is_feed_article(new_focus):
            tokens = ["WEB: New focus", new_focus, "was scrolled to. Generating line."]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            contents = self.utilities.getLineContentsAtOffset(new_focus, caretOffset)
        elif self.utilities.isFocusedWithMathChild(new_focus):
            tokens = ["WEB: New focus", new_focus, "has math child. Generating line."]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            contents = self.utilities.getLineContentsAtOffset(new_focus, caretOffset)
        elif AXUtilities.is_heading(new_focus):
            tokens = ["WEB: New focus", new_focus, "is heading. Generating object."]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            contents = self.utilities.getObjectContentsAtOffset(new_focus, 0)
        elif self.utilities.caretMovedToSamePageFragment(event, old_focus):
            tokens = ["WEB: Source", event.source, "is same page fragment. Generating line."]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            contents = self.utilities.getLineContentsAtOffset(new_focus, 0)
        elif event and event.type.startswith("object:children-changed:remove") \
             and self.utilities.isFocusModeWidget(new_focus):
            tokens = ["WEB: New focus", new_focus,
                      "is recovery from removed child. Generating speech."]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
        elif lastCommandWasLineNav and not AXObject.is_valid(old_focus):
            msg = "WEB: Last input event was line nav; old_focus is invalid. Generating line."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            contents = self.utilities.getLineContentsAtOffset(new_focus, caretOffset)
        elif lastCommandWasLineNav and event and event.type.startswith("object:children-changed"):
            msg = "WEB: Last input event was line nav and children changed. Generating line."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            contents = self.utilities.getLineContentsAtOffset(new_focus, caretOffset)
        else:
            tokens = ["WEB: New focus", new_focus, "is not a special case. Generating speech."]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)

        if new_focus and AXObject.is_dead(new_focus):
            msg = "WEB: New focus has since died"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            if self._get_queued_event("object:state-changed:focused", True):
                msg = "WEB: Have matching focused event. Not speaking contents"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                return True

        if self.utilities.shouldInterruptForLocusOfFocusChange(old_focus, new_focus, event):
            self.presentationInterrupt()

        if contents:
            self.speakContents(contents, **args)
        else:
            utterances = self.speech_generator.generate_speech(new_focus, **args)
            speech.speak(utterances)

        self._save_focused_object_info(new_focus)

        if self.utilities.inTopLevelWebApp(new_focus) and not self._browseModeIsSticky:
            announce = not self.utilities.inDocumentContent(old_focus)
            self.enableStickyFocusMode(None, announce)
            return True

        if not self._focusModeIsSticky \
           and not self._browseModeIsSticky \
           and self.useFocusMode(new_focus, old_focus) != self._inFocusMode:
            self.togglePresentationMode(None, document)

        if not self.utilities.inDocumentContent(old_focus):
            reason = "locus of focus now in document"
            self.caret_navigation.suspend_commands(self, self._inFocusMode, reason)
            self.structural_navigation.suspend_commands(self, self._inFocusMode, reason)
            self.live_region_manager.suspend_commands(self, self._inFocusMode, reason)
            self.get_table_navigator().suspend_commands(self, self._inFocusMode, reason)

        return True

    def on_active_changed(self, event):
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
            focus_manager.get_manager().set_locus_of_focus(event, event.source)
            return True

        return False

    def on_busy_changed(self, event):
        """Callback for object:state-changed:busy accessibility events."""

        AXUtilities.clear_all_cache_now(event.source, "busy-changed event.")

        if event.detail1 and self._loadingDocumentContent:
            msg = "WEB: Ignoring: Already loading document content"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if not self.utilities.inDocumentContent(event.source):
            msg = "WEB: Event source is not in document content"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        activeDocument = self.utilities.activeDocument()
        if activeDocument and activeDocument != event.source:
            msg = "WEB: Ignoring: Event source is not active document"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        focus = focus_manager.get_manager().get_locus_of_focus()
        if not AXUtilities.is_document_web(event.source) \
           and not self.utilities.isOrDescendsFrom(focus, event.source):
            msg = "WEB: Ignoring: Not document and not something we're in"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        self.structural_navigation.clearCache()

        if self.utilities.getDocumentForObject(AXObject.get_parent(event.source)):
            msg = "WEB: Ignoring: Event source is nested document"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        obj, offset = self.utilities.getCaretContext()
        if not AXObject.is_valid(obj):
            self.utilities.clearCaretContext()

        shouldPresent = True
        mgr = settings_manager.get_manager()
        if mgr.get_setting('onlySpeakDisplayedText'):
            shouldPresent = False
            msg = "WEB: Not presenting due to settings"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
        elif not (AXUtilities.is_showing(event.source) or AXUtilities.is_visible(event.source)):
            shouldPresent = False
            msg = "WEB: Not presenting because source is not showing or visible"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
        elif not AXDocument.get_uri(event.source):
            shouldPresent = False
            msg = "WEB: Not presenting because source lacks URI"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
        elif not event.detail1 and self._inFocusMode and AXObject.is_valid(obj):
            shouldPresent = False
            tokens = ["WEB: Not presenting due to focus mode for", obj]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
        elif mgr.get_setting('speechVerbosityLevel') != settings.VERBOSITY_LEVEL_VERBOSE:
            shouldPresent = not event.detail1
            tokens = ["WEB: Brief verbosity set. Should present", obj, f": {shouldPresent}"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)

        if shouldPresent:
            if event.detail1:
                self.presentMessage(messages.PAGE_LOADING_START)
            elif AXObject.get_name(event.source):
                if mgr.get_setting('speechVerbosityLevel') != settings.VERBOSITY_LEVEL_VERBOSE:
                    msg = AXObject.get_name(event.source)
                else:
                    msg = messages.PAGE_LOADING_END_NAMED % AXObject.get_name(event.source)
                self.presentMessage(msg, resetStyles=False)
            else:
                self.presentMessage(messages.PAGE_LOADING_END)

        self._loadingDocumentContent = event.detail1
        if event.detail1:
            return True

        self.utilities.clearCachedObjects()
        if AXObject.is_dead(obj):
            obj = None

        if not focus_manager.get_manager().focus_is_dead() \
           and not self.utilities.inDocumentContent(focus) \
           and AXUtilities.is_focused(focus):
            msg = "WEB: Not presenting content, focus is outside of document"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if settings_manager.get_manager().get_setting('pageSummaryOnLoad') and shouldPresent:
            tokens = ["WEB: Getting page summary for", event.source]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            summary = AXDocument.get_document_summary(event.source)
            if summary:
                self.presentMessage(summary)

        obj, offset = self.utilities.getCaretContext()
        if not AXUtilities.is_busy(event.source) \
           and self.utilities.isTopLevelWebApp(event.source):
            tokens = ["WEB: Setting locusOfFocus to", obj, "with sticky focus mode"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            focus_manager.get_manager().set_locus_of_focus(event, obj)
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
            focus_manager.get_manager().set_locus_of_focus(event, obj)
            return True

        if self.utilities.isLink(obj) and AXUtilities.is_focused(obj):
            tokens = ["WEB: Setting locus of focus to focused link", obj, ". No SayAll."]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            focus_manager.get_manager().set_locus_of_focus(event, obj)
            return True

        if offset > 0:
            tokens = ["WEB: Setting locus of focus to context obj", obj, ". No SayAll"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            focus_manager.get_manager().set_locus_of_focus(event, obj)
            return True

        if not AXUtilities.is_focused(focus_manager.get_manager().get_locus_of_focus()):
            tokens = ["WEB: Setting locus of focus to context obj", obj, "(no notification)"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            focus_manager.get_manager().set_locus_of_focus(event, obj, False)

        self.update_braille(obj)
        if AXDocument.get_document_uri_fragment(event.source):
            msg = "WEB: Not doing SayAll due to page fragment"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
        elif not settings_manager.get_manager().get_setting('sayAllOnLoad'):
            msg = "WEB: Not doing SayAll due to sayAllOnLoad being False"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self.speakContents(self.utilities.getLineContentsAtOffset(obj, offset))
        elif settings_manager.get_manager().get_setting('enableSpeech'):
            msg = "WEB: Doing SayAll"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self.say_all(None)
        else:
            msg = "WEB: Not doing SayAll due to enableSpeech being False"
            debug.printMessage(debug.LEVEL_INFO, msg, True)

        return True

    def on_caret_moved(self, event):
        """Callback for object:text-caret-moved accessibility events."""

        if not AXObject.is_valid(event.source):
            msg = "WEB: Event source is not valid"
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

        if self.caret_navigation.last_input_event_was_navigation_command():
            msg = "WEB: Event ignored: Last command was caret nav"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if self.structural_navigation.last_input_event_was_navigation_command():
            msg = "WEB: Event ignored: Last command was struct nav"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if self.get_table_navigator().last_input_event_was_navigation_command():
            msg = "WEB: Event ignored: Last command was table nav"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if input_event_manager.get_manager().last_event_was_mouse_button():
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
            focus_manager.get_manager().set_locus_of_focus(event, event.source, notify, True)
            return True

        if input_event_manager.get_manager().last_event_was_tab_navigation():
            if self.utilities.isDocument(event.source):
                msg = "WEB: Event ignored: Caret moved in document due to Tab."
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                return True
            if self.utilities.isLink(event.source):
                msg = "WEB: Event ignored: Caret moved in link due to Tab."
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                return True

        if self.utilities.inFindContainer():
            msg = "WEB: Event handled: Presenting find results"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self.presentFindResults(event.source, event.detail1)
            self._save_focused_object_info(focus_manager.get_manager().get_locus_of_focus())
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

        focus = focus_manager.get_manager().get_locus_of_focus()
        if self.utilities.isItemForEditableComboBox(focus, event.source) \
           and not input_event_manager.get_manager().last_event_was_character_navigation() \
           and not input_event_manager.get_manager().last_event_was_line_boundary_navigation():
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
            self.update_braille(event.source)
            self._presentTextAtNewCaretPosition(event)
            return True

        if not self.utilities.treatAsTextObject(event.source) \
           and not AXUtilities.is_editable(event.source):
            msg = "WEB: Event ignored: Was for non-editable object we're treating as textless"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        notify = force = handled = False
        AXObject.clear_cache(event.source, False, "Updating state for caret moved event.")

        if self._inFocusMode:
            obj, offset = event.source, event.detail1
        else:
            obj, offset = self.utilities.findFirstCaretContext(event.source, event.detail1)

        if input_event_manager.get_manager().last_event_was_page_navigation():
            msg = "WEB: Caret moved due to scrolling."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            notify = force = handled = True

        elif self.utilities.caretMovedToSamePageFragment(event):
            msg = "WEB: Caret moved to fragment."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            notify = force = handled = True

        elif event.source != focus and AXUtilities.is_editable(event.source) and \
             (AXUtilities.is_focused(event.source) or not AXUtilities.is_focusable(event.source)):
            msg = "WEB: Editable object is not (yet) the locus of focus."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            notify = force = handled = \
                input_event_manager.get_manager().last_event_was_line_navigation()

        elif input_event_manager.get_manager().last_event_was_caret_navigation():
            msg = "WEB: Caret moved due to native caret navigation."
            debug.printMessage(debug.LEVEL_INFO, msg, True)

        tokens = ["WEB: Setting context and focus to: ", obj, ", ", offset, f", notify: {notify}"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        self.utilities.setCaretContext(obj, offset, document)
        focus_manager.get_manager().set_locus_of_focus(event, obj, notify, force)
        return handled

    def on_checked_changed(self, event):
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

        if not (self.caret_navigation.last_input_event_was_navigation_command() \
           and AXUtilities.is_radio_button(obj)):
            msg = "WEB: Event is something default can handle"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        self.presentObject(obj, alreadyFocused=True, interrupt=True)
        return True

    def on_children_added(self, event):
        """Callback for object:children-changed:add accessibility events."""

        AXUtilities.clear_all_cache_now(event.source, "children-changed event.")

        if self.utilities.eventIsBrowserUINoise(event):
            msg = "WEB: Ignoring event believed to be browser UI noise"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        isLiveRegion = self.utilities.isLiveRegion(event.source)
        document = self.utilities.getTopLevelDocumentForObject(event.source)
        if document and not isLiveRegion:
            focus = focus_manager.get_manager().get_locus_of_focus()
            if event.source == focus:
                msg = "WEB: Dumping cache: source is focus"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                self.utilities.dumpCache(document, preserveContext=True)
            elif focus_manager.get_manager().focus_is_dead():
                msg = "WEB: Dumping cache: dead focus"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                self.utilities.dumpCache(document, preserveContext=True)
            elif AXObject.find_ancestor(focus, lambda x: x == event.source):
                msg = "WEB: Dumping cache: source is ancestor of focus"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                self.utilities.dumpCache(document, preserveContext=True)
            else:
                msg = "WEB: Not dumping full cache"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                self.utilities.clearCachedObjects()
        elif isLiveRegion:
            msg = "WEB: Ignoring event from live region."
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

        if not AXObject.is_valid(document):
            tokens = ["WEB: Ignoring because", document, "is not valid."]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return True

        if AXUtilities.is_busy(document):
            tokens = ["WEB: Ignoring because", document, "is busy."]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return True

        if not AXObject.is_valid(event.any_data):
            msg = "WEB: Ignoring because any data is not valid."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.handleEventFromContextReplicant(event, event.any_data):
            msg = "WEB: Event handled by updating locusOfFocus and context to child."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if AXUtilities.is_alert(event.any_data):
            msg = "WEB: Presenting event.any_data"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self.presentObject(event.any_data, interrupt=True)

            focused = AXUtilities.get_focused_object(event.any_data)
            if focused:
                notify = not self.utilities.treatAsTextObject(focused)
                tokens = ["WEB: Setting locusOfFocus and caret context to", focused]
                debug.printTokens(debug.LEVEL_INFO, tokens, True)
                focus_manager.get_manager().set_locus_of_focus(event, focused, notify)
                self.utilities.setCaretContext(focused, 0)
            return True

        if self.lastMouseRoutingTime and 0 < time.time() - self.lastMouseRoutingTime < 1:
            utterances = []
            utterances.append(messages.NEW_ITEM_ADDED)
            utterances.extend(self.speech_generator.generate_speech(event.any_data, force=True))
            speech.speak(utterances)
            self._lastMouseOverObject = event.any_data
            self.preMouseOverContext = self.utilities.getCaretContext()
            return True

        return False

    def on_children_removed(self, event):
        """Callback for object:children-changed:removed accessibility events."""

        AXUtilities.clear_all_cache_now(event.source, "children-changed event.")

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
            focus = focus_manager.get_manager().get_locus_of_focus()
            if event.source == focus:
                msg = "WEB: Dumping cache: source is focus"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                self.utilities.dumpCache(document, preserveContext=True)
            elif focus_manager.get_manager().focus_is_dead():
                msg = "WEB: Dumping cache: dead focus"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                self.utilities.dumpCache(document, preserveContext=True)
            elif AXObject.find_ancestor(focus, lambda x: x == event.source):
                msg = "WEB: Dumping cache: source is ancestor of focus"
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

    def on_column_reordered(self, event):
        """Callback for object:column-reordered accessibility events."""

        if not self.utilities.inDocumentContent(event.source):
            msg = "WEB: Event source is not in document content"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        focus = focus_manager.get_manager().get_locus_of_focus()
        if event.source != AXTable.get_table(focus):
            msg = "WEB: focus is not in this table"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        self.presentMessage(messages.TABLE_REORDERED_COLUMNS)
        header = self.utilities.containingTableHeader(focus)
        if header:
            self.presentMessage(self.utilities.getSortOrderDescription(header, True))

        return True

    def on_document_load_complete(self, event):
        """Callback for document:load-complete accessibility events."""

        AXUtilities.clear_all_cache_now(event.source, "load-complete event.")
        if self.utilities.getDocumentForObject(AXObject.get_parent(event.source)):
            msg = "WEB: Ignoring: Event source is nested document"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        msg = "WEB: Updating loading state and resetting live regions"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        self._loadingDocumentContent = False
        self.live_region_manager.reset()
        return True

    def on_document_load_stopped(self, event):
        """Callback for document:load-stopped accessibility events."""

        if self.utilities.getDocumentForObject(AXObject.get_parent(event.source)):
            msg = "WEB: Ignoring: Event source is nested document"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        msg = "WEB: Updating loading state"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        self._loadingDocumentContent = False
        return True

    def on_document_reload(self, event):
        """Callback for document:reload accessibility events."""

        if self.utilities.getDocumentForObject(AXObject.get_parent(event.source)):
            msg = "WEB: Ignoring: Event source is nested document"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        msg = "WEB: Updating loading state"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        self._loadingDocumentContent = True
        return True

    def on_expanded_changed(self, event):
        """Callback for object:state-changed:expanded accessibility events."""

        if not AXObject.is_valid(event.source):
            msg = "WEB: Event source is not valid"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if not self.utilities.inDocumentContent(event.source):
            msg = "WEB: Event source is not in document content"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        focus = focus_manager.get_manager().get_locus_of_focus()
        obj, offset = self.utilities.getCaretContext(searchIfNeeded=False)
        tokens = ["WEB: Caret context is", obj, ", ", offset]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        if not AXObject.is_valid(obj) and event.source == focus:
            msg = "WEB: Setting caret context to event source"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self.utilities.setCaretContext(event.source, 0)

        return False

    def on_focused_changed(self, event):
        """Callback for object:state-changed:focused accessibility events."""

        if not event.detail1:
            msg = "WEB: Ignoring because event source lost focus"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if not AXObject.is_valid(event.source):
            msg = "WEB: Event source is not valid"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        document = self.utilities.getDocumentForObject(event.source)
        if not document:
            msg = "WEB: Could not get document for event source"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        focus = focus_manager.get_manager().get_locus_of_focus()
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
                focus_manager.get_manager().set_locus_of_focus(event, event.source)
                return True

        if AXUtilities.is_editable(event.source):
            msg = "WEB: Event source is editable"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        if AXUtilities.is_dialog_or_alert(event.source):
            msg = "WEB: Event handled: Setting locusOfFocus to event source"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            focus_manager.get_manager().set_locus_of_focus(event, event.source)
            return True

        if self.utilities.handleEventFromContextReplicant(event, event.source):
            msg = "WEB: Event handled by updating locusOfFocus and context to source."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        obj, offset = self.utilities.getCaretContext()
        tokens = ["WEB: Caret context is", obj, ", ", offset]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        if not AXObject.is_valid(obj) or prevDocument != document:
            tokens = ["WEB: Clearing context - obj", obj, "is not valid or document changed"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            self.utilities.clearCaretContext()

            obj, offset = self.utilities.searchForCaretContext(event.source)
            if obj:
                notify = self.utilities.inFindContainer(focus)
                tokens = ["WEB: Updating focus and context to", obj, ", ", offset]
                debug.printTokens(debug.LEVEL_INFO, tokens, True)
                focus_manager.get_manager().set_locus_of_focus(event, obj, notify)
                if not notify and prevDocument is None:
                    reason = "updating locus of focus without notification"
                    self.caret_navigation.suspend_commands(self, self._inFocusMode, reason)
                    self.structural_navigation.suspend_commands(self, self._inFocusMode, reason)
                    self.live_region_manager.suspend_commands(self, self._inFocusMode, reason)
                    self.get_table_navigator().suspend_commands(self, self._inFocusMode, reason)
                self.utilities.setCaretContext(obj, offset)
            else:
                msg = "WEB: Search for caret context failed"
                debug.printMessage(debug.LEVEL_INFO, msg, True)

        if self.caret_navigation.last_input_event_was_navigation_command():
            msg = "WEB: Event ignored: Last command was caret nav"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if self.structural_navigation.last_input_event_was_navigation_command():
            msg = "WEB: Event ignored: Last command was struct nav"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if self.get_table_navigator().last_input_event_was_navigation_command():
            msg = "WEB: Event ignored: Last command was table nav"
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
            msg = "WEB: Unable to get valid context object"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        if input_event_manager.get_manager().last_event_was_page_navigation():
            msg = "WEB: Event handled: Focus changed due to scrolling"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            focus_manager.get_manager().set_locus_of_focus(event, obj)
            self.utilities.setCaretContext(obj, offset)
            return True

        # TODO - JD: Can this logic be removed?
        wasFocused = AXUtilities.is_focused(obj)
        AXObject.clear_cache(obj, False, "Sanity-checking focused state.")
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
        elif document == event.source and AXDocument.get_document_uri_fragment(event.source):
            cause = "Document URI is fragment"
        else:
            return False

        tokens = ["WEB: Event handled: Setting locusOfFocus to", obj, "(", cause, ")"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        focus_manager.get_manager().set_locus_of_focus(event, obj)
        return True

    def on_mouse_button(self, event):
        """Callback for mouse:button accessibility events."""

        return False

    def on_name_changed(self, event):
        """Callback for object:property-change:accessible-name events."""

        if self.utilities.eventIsBrowserUINoise(event):
            msg = "WEB: Ignoring event believed to be browser UI noise"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        return False

    def on_row_reordered(self, event):
        """Callback for object:row-reordered accessibility events."""

        if not self.utilities.inDocumentContent(event.source):
            msg = "WEB: Event source is not in document content"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        focus = focus_manager.get_manager().get_locus_of_focus()
        if event.source != AXTable.get_table(focus):
            msg = "WEB: focus is not in this table"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return False

        self.presentMessage(messages.TABLE_REORDERED_ROWS)
        header = self.utilities.containingTableHeader(focus)
        if header:
            self.presentMessage(self.utilities.getSortOrderDescription(header, True))

        return True

    def on_selected_changed(self, event):
        """Callback for object:state-changed:selected accessibility events."""

        if self.utilities.eventIsBrowserUIAutocompleteNoise(event):
            msg = "WEB: Ignoring event believed to be browser UI autocomplete noise"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        focus = focus_manager.get_manager().get_locus_of_focus()
        if self.utilities.eventIsBrowserUIPageSwitch(event):
            msg = "WEB: Event believed to be browser UI page switch"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            if event.detail1:
                AXUtilities.clear_all_cache_now(reason=msg)
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

    def on_selection_changed(self, event):
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

        if not self.utilities.inDocumentContent(focus_manager.get_manager().get_locus_of_focus()):
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
                AXObject.clear_cache(event.source,
                                     True,
                                     "Workaround for missing events on descendants.")
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

    def on_showing_changed(self, event):
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

    def on_text_attributes_changed(self, event):
        """Callback for object:text-attributes-changed accessibility events."""

        msg = "WEB: Clearing cached text attributes"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        self._currentTextAttrs = {}
        return False

    def on_text_deleted(self, event):
        """Callback for object:text-changed:delete accessibility events."""

        if not AXObject.is_valid(event.source):
            msg = "WEB: Event source is not valid"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if input_event_manager.get_manager().last_event_was_page_switch():
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

        obj, offset = self.utilities.getCaretContext(getReplicant=False)
        if obj and obj != event.source \
           and not AXObject.find_ancestor(obj, lambda x: x == event.source):
            tokens = ["WEB: Ignoring event because it isn't", obj, "or its ancestor"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return True

        if not AXObject.is_valid(obj):
            if self.utilities.isLink(obj):
                msg = "WEB: Focused link deleted. Taking no further action."
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                return True

            obj, offset = self.utilities.getCaretContext(getReplicant=True)
            if obj:
                focus_manager.get_manager().set_locus_of_focus(event, obj, notify_script=False)

        if not AXObject.is_valid(obj):
            msg = "WEB: Unable to get valid context object"
            debug.printMessage(debug.LEVEL_INFO, msg, True)

        document = self.utilities.getDocumentForObject(event.source)
        if document:
            tokens = ["WEB: Clearing structural navigation cache for", document]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            self.structural_navigation.clearCache(document)

        if not AXUtilities.is_editable(event.source) \
           and not self.utilities.isContentEditableWithEmbeddedObjects(event.source):
            if self._inMouseOverObject and not AXObject.is_valid(self._lastMouseOverObject):
                msg = "WEB: Restoring pre-mouseover context"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                self.restorePreMouseOverContext()

            msg = "WEB: Done processing non-editable source"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        return False

    def on_text_inserted(self, event):
        """Callback for object:text-changed:insert accessibility events."""

        if not AXObject.is_valid(event.source):
            msg = "WEB: Event source is not valid"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if input_event_manager.get_manager().last_event_was_page_switch():
            msg = "WEB: Insertion is believed to be due to page switch"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        if self.utilities.isLiveRegion(event.source):
            if self.utilities.handleAsLiveRegion(event):
                msg = "WEB: Event to be handled as live region"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                self.live_region_manager.handleEvent(event)
                return True
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
        if focus_manager.get_manager().focus_is_dead():
            msg = "WEB: Dumping cache: dead focus"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self.utilities.dumpCache(document, preserveContext=True)

            if AXUtilities.is_focused(event.source):
                msg = "WEB: Event handled: Setting locusOfFocus to event source"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                focus_manager.get_manager().set_locus_of_focus(None, event.source, force=True)
                return True

        else:
            tokens = ["WEB: Clearing structural navigation cache for", document]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            self.structural_navigation.clearCache(document)

        if not self.utilities.treatAsTextObject(event.source):
            msg = "WEB: Ignoring: Event source is not a text object"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        sourceIsFocus = event.source == focus_manager.get_manager().get_locus_of_focus()
        if not AXUtilities.is_editable(event.source):
            if not sourceIsFocus:
                msg = "WEB: Done processing non-editable, non-locusOfFocus source"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                return True

            if self.utilities.isClickableElement(event.source):
                msg = "WEB: Event handled: Re-setting locusOfFocus to changed clickable"
                debug.printMessage(debug.LEVEL_INFO, msg, True)
                focus_manager.get_manager().set_locus_of_focus(None, event.source, force=True)
                return True

        if not sourceIsFocus and AXUtilities.is_text_input(event.source) \
           and AXUtilities.is_focused(event.source):
            msg = "WEB: Focused entry is not the locus of focus. Waiting for focus event."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        return False

    def on_text_selection_changed(self, event):
        """Callback for object:text-selection-changed accessibility events."""

        if not AXObject.is_valid(event.source):
            msg = "WEB: Event source is not valid"
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

        focus = focus_manager.get_manager().get_locus_of_focus()
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

        if not self.utilities.treatAsTextObject(event.source):
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

        if self.structural_navigation.last_input_event_was_navigation_command():
            msg = "WEB: Ignoring: Last input event was structural navigation command."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        char = AXText.get_character_at_offset(event.source)[0]
        manager = input_event_manager.get_manager()
        if char == self.EMBEDDED_OBJECT_CHARACTER \
           and not manager.last_event_was_caret_selection() \
           and not manager.last_event_was_command():
            msg = "WEB: Ignoring: Not selecting and event offset is at embedded object"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        return False

    def on_window_activated(self, event):
        """Callback for window:activate accessibility events."""

        msg = "WEB: Deferring to app/toolkit script"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        return False

    def on_window_deactivated(self, event):
        """Callback for window:deactivate accessibility events."""

        msg = "WEB: Clearing command state"
        debug.printMessage(debug.LEVEL_INFO, msg, True)
        self._lastMouseButtonContext = None, -1
        return False
