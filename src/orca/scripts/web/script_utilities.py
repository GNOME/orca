# Orca
#
# Copyright 2010 Joanmarie Diggs.
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
__copyright__ = "Copyright (c) 2010 Joanmarie Diggs." \
                "Copyright (c) 2014-2015 Igalia, S.L."
__license__   = "LGPL"

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

import functools
import re
import time
import urllib

from orca import debug
from orca import focus_manager
from orca import input_event_manager
from orca import script_utilities
from orca import settings_manager
from orca.ax_component import AXComponent
from orca.ax_document import AXDocument
from orca.ax_hypertext import AXHypertext
from orca.ax_object import AXObject
from orca.ax_table import AXTable
from orca.ax_text import AXText
from orca.ax_utilities import AXUtilities
from orca.ax_utilities_debugging import AXUtilitiesDebugging


class Utilities(script_utilities.Utilities):

    def __init__(self, script):
        super().__init__(script)

        self._caretContexts = {}
        self._priorContexts = {}
        self._canHaveCaretContextDecision = {}
        self._contextPathsRolesAndNames = {}
        self._paths = {}
        self._inDocumentContent = {}
        self._inTopLevelWebApp = {}
        self._isTextBlockElement = {}
        self._isContentEditableWithEmbeddedObjects = {}
        self._hasGridDescendant = {}
        self._isFocusableWithMathChild = {}
        self._isOffScreenLabel = {}
        self._labelIsAncestorOfLabelled = {}
        self._elementLinesAreSingleChars= {}
        self._elementLinesAreSingleWords= {}
        self._hasLongDesc = {}
        self._isClickableElement = {}
        self._isLink = {}
        self._isNonEntryTextWidget = {}
        self._isCustomImage = {}
        self._isUselessImage = {}
        self._isRedundantSVG = {}
        self._isUselessEmptyElement = {}
        self._hasNameAndActionAndNoUsefulChildren = {}
        self._isNonNavigableEmbeddedDocument = {}
        self._inferredLabels = {}
        self._shouldFilter = {}
        self._shouldInferLabelFor = {}
        self._treatAsTextObject = {}
        self._treatAsDiv = {}
        self._currentObjectContents = None
        self._currentSentenceContents = None
        self._currentLineContents = None
        self._currentWordContents = None
        self._currentCharacterContents = None
        self._findContainer = None
        self._validChildRoles = {Atspi.Role.LIST: [Atspi.Role.LIST_ITEM]}

    def _cleanupContexts(self):
        toRemove = []
        for key, [obj, offset] in self._caretContexts.items():
            if not AXObject.is_valid(obj):
                toRemove.append(key)

        for key in toRemove:
            self._caretContexts.pop(key, None)

    def dumpCache(self, documentFrame=None, preserveContext=False):
        if not AXObject.is_valid(documentFrame):
            documentFrame = self.documentFrame()

        documentFrameParent = AXObject.get_parent(documentFrame)
        context = self._caretContexts.get(hash(documentFrameParent))
        tokens = ["WEB: Clearing all cached info for", documentFrame,
                  "Preserving context:", preserveContext, "Context:", context]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self.clearCaretContext(documentFrame)
        self.clearCachedObjects()

        if preserveContext and context:
            tokens = ["WEB: Preserving context of", context[0], ",", context[1]]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            self._caretContexts[hash(documentFrameParent)] = context

    def clearCachedObjects(self):
        debug.print_message(debug.LEVEL_INFO, "WEB: cleaning up cached objects", True)
        self._inDocumentContent = {}
        self._inTopLevelWebApp = {}
        self._isTextBlockElement = {}
        self._isContentEditableWithEmbeddedObjects = {}
        self._hasGridDescendant = {}
        self._isFocusableWithMathChild = {}
        self._isOffScreenLabel = {}
        self._labelIsAncestorOfLabelled = {}
        self._elementLinesAreSingleChars= {}
        self._elementLinesAreSingleWords= {}
        self._hasLongDesc = {}
        self._isClickableElement = {}
        self._isLink = {}
        self._isNonEntryTextWidget = {}
        self._isCustomImage = {}
        self._isUselessImage = {}
        self._isRedundantSVG = {}
        self._isUselessEmptyElement = {}
        self._hasNameAndActionAndNoUsefulChildren = {}
        self._isNonNavigableEmbeddedDocument = {}
        self._inferredLabels = {}
        self._shouldFilter = {}
        self._shouldInferLabelFor = {}
        self._treatAsTextObject = {}
        self._treatAsDiv = {}
        self._paths = {}
        self._contextPathsRolesAndNames = {}
        self._canHaveCaretContextDecision = {}
        self._cleanupContexts()
        self._priorContexts = {}
        self._findContainer = None

    def clearContentCache(self):
        self._currentObjectContents = None
        self._currentSentenceContents = None
        self._currentLineContents = None
        self._currentWordContents = None
        self._currentCharacterContents = None

    def isDocument(self, obj, excludeDocumentFrame=True):
        if AXUtilities.is_document_web(obj) or AXUtilities.is_embedded(obj):
            return True

        if not excludeDocumentFrame:
            return AXUtilities.is_document_frame(obj)

        return False

    def inDocumentContent(self, obj=None):
        if not obj:
            obj = focus_manager.get_manager().get_locus_of_focus()


        if self.isDocument(obj):
            return True

        rv = self._inDocumentContent.get(hash(obj))
        if rv is not None:
            return rv

        document = self.getDocumentForObject(obj)
        rv = document is not None
        self._inDocumentContent[hash(obj)] = rv
        return rv

    def activeDocument(self, window=None):
        window = window or focus_manager.get_manager().get_active_window()
        documents = list(filter(self.isDocument, AXUtilities.get_embeds(window)))
        documents = list(filter(AXUtilities.is_showing, documents))
        if len(documents) == 1:
            return documents[0]
        return None

    def documentFrame(self, obj=None):
        if not obj:
            document = self.activeDocument()
            if document:
                return document

        return self.getDocumentForObject(obj or focus_manager.get_manager().get_locus_of_focus())

    def grabFocusWhenSettingCaret(self, obj):
        # To avoid triggering popup lists.
        if AXUtilities.is_entry(obj):
            return False

        if AXUtilities.is_image(obj):
            return AXObject.find_ancestor(obj, AXUtilities.is_link) is not None

        if AXUtilities.is_heading(obj) and AXObject.get_child_count(obj) == 1:
            return self.isLink(AXObject.get_child(obj, 0))

        return AXUtilities.is_focusable(obj)

    def setCaretPosition(self, obj, offset, documentFrame=None):
        if self._script.get_flat_review_presenter().is_active():
            self._script.get_flat_review_presenter().quit()
        grabFocus = self.grabFocusWhenSettingCaret(obj)

        obj, offset = self.findFirstCaretContext(obj, offset)
        self.setCaretContext(obj, offset, documentFrame)
        if self._script.focusModeIsSticky():
            return

        old_focus = focus_manager.get_manager().get_locus_of_focus()
        AXText.clear_all_selected_text(old_focus)
        focus_manager.get_manager().set_locus_of_focus(None, obj, notify_script=False)
        if grabFocus:
            AXObject.grab_focus(obj)

        AXText.set_caret_offset(obj, offset)
        if self._script.useFocusMode(obj, old_focus) != self._script.inFocusMode():
            self._script.togglePresentationMode(None)

        # TODO - JD: Can we remove this?
        if obj:
            AXObject.clear_cache(obj, False, "Set caret in object.")

        # TODO - JD: This is private.
        self._script._save_focused_object_info(obj)

    def getNextObjectInDocument(self, obj, documentFrame):
        if not obj:
            return None

        targets = AXUtilities.get_flows_to(obj)
        if targets:
            return targets[0]

        if obj == documentFrame:
            obj, offset = self.getCaretContext(documentFrame)
            for child in AXObject.iter_children(documentFrame):
                if AXHypertext.get_character_offset_in_parent(child) > offset:
                    return child

        if AXObject.get_child_count(obj):
            return AXObject.get_child(obj, 0)

        while obj and obj != documentFrame:
            nextObj = AXObject.get_next_sibling(obj)
            if nextObj:
                return nextObj
            obj = AXObject.get_parent(obj)

        return None

    def inFindContainer(self, obj=None):
        if not obj:
            obj = focus_manager.get_manager().get_locus_of_focus()

        if self.inDocumentContent(obj):
            return False

        return super().inFindContainer(obj)

    def setCaretOffset(self, obj, characterOffset):
        self.setCaretPosition(obj, characterOffset)
        self._script.update_braille(obj)

    def nextContext(self, obj=None, offset=-1, skipSpace=False):
        if not obj:
            obj, offset = self.getCaretContext()

        nextobj, nextoffset = self.findNextCaretInOrder(obj, offset)
        if skipSpace:
            while AXText.get_character_at_offset(nextobj, nextoffset)[0].isspace():
                nextobj, nextoffset = self.findNextCaretInOrder(nextobj, nextoffset)

        return nextobj, nextoffset

    def previousContext(self, obj=None, offset=-1, skipSpace=False):
        if not obj:
            obj, offset = self.getCaretContext()

        prevobj, prevoffset = self.findPreviousCaretInOrder(obj, offset)
        if skipSpace:
            while AXText.get_character_at_offset(prevobj, prevoffset)[0].isspace():
                prevobj, prevoffset = self.findPreviousCaretInOrder(prevobj, prevoffset)

        return prevobj, prevoffset

    def lastContext(self, root):
        offset = 0
        if self.treatAsTextObject(root):
            offset = AXText.get_character_count(root) - 1

        def _isInRoot(o):
            return o == root or AXObject.find_ancestor(o, lambda x: x == root)

        obj = root
        while obj:
            lastobj, lastoffset = self.nextContext(obj, offset)
            if not (lastobj and _isInRoot(lastobj)):
                break
            obj, offset = lastobj, lastoffset

        return obj, offset

    def contextsAreOnSameLine(self, a, b):
        if a == b:
            return True

        aObj, aOffset = a
        bObj, bOffset = b
        aExtents = self.getExtents(aObj, aOffset, aOffset + 1)
        bExtents = self.getExtents(bObj, bOffset, bOffset + 1)
        return self.extentsAreOnSameLine(aExtents, bExtents)

    @staticmethod
    def extentsAreOnSameLine(a, b, pixelDelta=5):
        if a == b:
            return True

        aX, aY, aWidth, aHeight = a
        bX, bY, bWidth, bHeight = b

        if aWidth == 0 and aHeight == 0:
            return bY <= aY <= bY + bHeight
        if bWidth == 0 and bHeight == 0:
            return aY <= bY <= aY + aHeight

        highestBottom = min(aY + aHeight, bY + bHeight)
        lowestTop = max(aY, bY)
        if lowestTop >= highestBottom:
            return False

        aMiddle = aY + aHeight / 2
        bMiddle = bY + bHeight / 2
        if abs(aMiddle - bMiddle) > pixelDelta:
            return False

        return True

    def getExtents(self, obj, startOffset, endOffset):
        if not obj:
            return [0, 0, 0, 0]

        result = [0, 0, 0, 0]
        if self.treatAsTextObject(obj) and 0 <= startOffset < endOffset:
            rect = AXText.get_range_rect(obj, startOffset, endOffset)
            result = [rect.x, rect.y, rect.width, rect.height]
            if result[0] and result[1] and result[2] == 0 and result[3] == 0 \
               and AXText.get_substring(obj, startOffset, endOffset).strip():
                tokens = ["WEB: Suspected bogus range extents for",
                          obj, "(chars:", startOffset, ",", endOffset, "):", result]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            else:
                return result

        parent = AXObject.get_parent(obj)
        if (AXUtilities.is_menu(obj) or AXUtilities.is_list_item(obj)) \
            and (AXUtilities.is_combo_box(parent) or AXUtilities.is_list_box(parent)):
            ext = AXComponent.get_rect(parent)
        else:
            ext = AXComponent.get_rect(obj)

        return [ext.x, ext.y, ext.width, ext.height]

    def expandEOCs(self, obj, startOffset=0, endOffset=-1):
        if not self.inDocumentContent(obj):
            return super().expandEOCs(obj, startOffset, endOffset)

        if self.hasGridDescendant(obj):
            tokens = ["WEB: not expanding EOCs:", obj, "has grid descendant"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return ""

        if not self.treatAsTextObject(obj):
            return ""

        if AXUtilities.is_math(obj) and AXObject.get_child_count(obj):
            utterances = self._script.speech_generator.generate_speech(obj)
            return self._script.speech_generator.utterances_to_string(utterances)

        return super().expandEOCs(obj, startOffset, endOffset)

    def adjustContentsForLanguage(self, contents):
        rv = []
        for content in contents:
            split = self.splitSubstringByLanguage(*content[0:3])
            for start, end, string, language, dialect in split:
                rv.append([content[0], start, end, string])

        return rv

    def getLanguageAndDialectFromTextAttributes(self, obj, startOffset=0, endOffset=-1):
        rv = super().getLanguageAndDialectFromTextAttributes(obj, startOffset, endOffset)
        if rv or obj is None:
            return rv

        # Embedded objects such as images and certain widgets won't implement the text interface
        # and thus won't expose text attributes. Therefore try to get the info from the parent.
        parent = AXObject.get_parent(obj)
        if parent is None or not self.inDocumentContent(parent):
            return rv

        start = AXHypertext.get_link_start_offset(obj)
        end = AXHypertext.get_link_end_offset(obj)
        language, dialect = self.getLanguageAndDialectForSubstring(parent, start, end)
        rv.append((0, 1, language, dialect))

        return rv

    def findObjectInContents(self, obj, offset, contents, usingCache=False):
        if not obj or not contents:
            return -1

        offset = max(0, offset)
        matches = [x for x in contents if x[0] == obj]
        match = [x for x in matches if x[1] <= offset < x[2]]
        if match and match[0] and match[0] in contents:
            return contents.index(match[0])
        if not usingCache:
            match = [x for x in matches if offset == x[2]]
            if match and match[0] and match[0] in contents:
                return contents.index(match[0])

        if not self.isTextBlockElement(obj):
            return -1

        child = AXHypertext.get_child_at_offset(obj, offset)
        if child and not self.isTextBlockElement(child):
            matches = [x for x in contents if x[0] == child]
            if len(matches) == 1:
                return contents.index(matches[0])

        return -1

    def isNonEntryTextWidget(self, obj):
        rv = self._isNonEntryTextWidget.get(hash(obj))
        if rv is not None:
            return rv

        roles = [Atspi.Role.CHECK_BOX,
                 Atspi.Role.CHECK_MENU_ITEM,
                 Atspi.Role.MENU,
                 Atspi.Role.MENU_ITEM,
                 Atspi.Role.PAGE_TAB,
                 Atspi.Role.RADIO_MENU_ITEM,
                 Atspi.Role.RADIO_BUTTON,
                 Atspi.Role.PUSH_BUTTON,
                 Atspi.Role.TOGGLE_BUTTON]

        role = AXObject.get_role(obj)
        if role in roles:
            rv = True
        elif role == Atspi.Role.LIST_ITEM:
            rv = not AXUtilities.is_list(AXObject.get_parent(obj))
        elif role == Atspi.Role.TABLE_CELL:
            if AXUtilities.is_editable(obj):
                rv = False
            else:
                rv = not self.isTextBlockElement(obj)

        self._isNonEntryTextWidget[hash(obj)] = rv
        return rv

    def treatAsTextObject(self, obj, excludeNonEntryTextWidgets=True):
        if not obj or AXObject.is_dead(obj):
            return False

        rv = self._treatAsTextObject.get(hash(obj))
        if rv is not None:
            return rv

        if not AXObject.supports_text(obj):
            return False

        if not self.inDocumentContent(obj) or self._script.browseModeIsSticky():
            return True

        rv = AXText.get_character_count(obj) > 0 or AXUtilities.is_editable(obj)
        if rv and self._treatObjectAsWhole(obj, -1) and AXObject.get_name(obj) \
            and not self.isCellWithNameFromHeader(obj):
            tokens = ["WEB: Treating", obj, "as non-text: named object treated as whole."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            rv = False

        elif rv and not AXUtilities.is_live_region(obj):
            doNotQuery = [Atspi.Role.LIST_BOX]
            role = AXObject.get_role(obj)
            if rv and role in doNotQuery:
                tokens = ["WEB: Treating", obj, "as non-text due to role."]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                rv = False
            if rv and excludeNonEntryTextWidgets and self.isNonEntryTextWidget(obj):
                tokens = ["WEB: Treating", obj, "as non-text: is non-entry text widget."]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                rv = False
            if rv and (AXUtilities.is_hidden(obj) or self.isOffScreenLabel(obj)):
                tokens = ["WEB: Treating", obj, "as non-text: is hidden or off-screen label."]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                rv = False
            if rv and self.isNonNavigableEmbeddedDocument(obj):
                tokens = ["WEB: Treating", obj, "as non-text: is non-navigable embedded document."]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                rv = False
            if rv and self.isFakePlaceholderForEntry(obj):
                tokens = ["WEB: Treating", obj, "as non-text: is fake placeholder for entry."]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                rv = False

        self._treatAsTextObject[hash(obj)] = rv
        return rv

    def hasNameAndActionAndNoUsefulChildren(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return False

        rv = self._hasNameAndActionAndNoUsefulChildren.get(hash(obj))
        if rv is not None:
            return rv

        rv = False
        if AXUtilities.has_explicit_name(obj) and AXObject.supports_action(obj):
            for child in AXObject.iter_children(obj):
                if not self.isUselessEmptyElement(child) or self.isUselessImage(child):
                    break
            else:
                rv = True

        if rv:
            tokens = ["WEB:", obj, "has name and action and no useful children"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self._hasNameAndActionAndNoUsefulChildren[hash(obj)] = rv
        return rv

    def _treatObjectAsWhole(self, obj, offset=None):
        always = [Atspi.Role.CHECK_BOX,
                  Atspi.Role.CHECK_MENU_ITEM,
                  Atspi.Role.LIST_BOX,
                  Atspi.Role.MENU_ITEM,
                  Atspi.Role.PAGE_TAB,
                  Atspi.Role.RADIO_MENU_ITEM,
                  Atspi.Role.RADIO_BUTTON,
                  Atspi.Role.PUSH_BUTTON,
                  Atspi.Role.TOGGLE_BUTTON]

        descendable = [Atspi.Role.MENU,
                       Atspi.Role.MENU_BAR,
                       Atspi.Role.TOOL_BAR,
                       Atspi.Role.TREE_ITEM]

        role = AXObject.get_role(obj)
        if role in always:
            return True

        if role in descendable:
            if self._script.inFocusMode():
                return True

            # This should cause us to initially stop at the large containers before
            # allowing the user to drill down into them in browse mode.
            return offset == -1

        if role == Atspi.Role.ENTRY:
            if AXObject.get_child_count(obj) == 1 \
              and self.isFakePlaceholderForEntry(AXObject.get_child(obj, 0)):
                return True
            return False

        if AXUtilities.is_editable(obj):
            return False

        if role == Atspi.Role.TABLE_CELL:
            if self.isFocusModeWidget(obj):
                return not self._script.browseModeIsSticky()
            if self.hasNameAndActionAndNoUsefulChildren(obj):
                return True

        if role in [Atspi.Role.COLUMN_HEADER, Atspi.Role.ROW_HEADER] \
           and AXUtilities.has_explicit_name(obj):
            return True

        if role == Atspi.Role.COMBO_BOX:
            return True

        if role in [Atspi.Role.EMBEDDED, Atspi.Role.TREE, Atspi.Role.TREE_TABLE]:
            return not self._script.browseModeIsSticky()

        if role == Atspi.Role.LINK:
            return AXUtilities.has_explicit_name(obj) or self.hasUselessCanvasDescendant(obj)

        if self.isNonNavigableEmbeddedDocument(obj):
            return True

        if self.isFakePlaceholderForEntry(obj):
            return True

        if self.isCustomImage(obj):
            return True

        # Example: Some StackExchange instances have a focusable "note"/comment role
        # with a name (e.g. "Accepted"), and a single child div which is empty.
        if role in self._textBlockElementRoles() and AXUtilities.is_focusable(obj) \
           and AXUtilities.has_explicit_name(obj):
            for child in AXObject.iter_children(obj):
                if not self.isUselessEmptyElement(child):
                    return False
            return True

        return False

    def __findSentence(self, obj, offset):
        # TODO - JD: Move this sad hack to AXText.
        text = AXText.get_all_text(obj)
        spans = [m.span() for m in re.finditer(r"\S*[^\.\?\!]+((?<!\w)[\.\?\!]+(?!\w)|\S*)", text)]
        rangeStart, rangeEnd = 0, len(text)
        for span in spans:
            if span[0] <= offset <= span[1]:
                rangeStart, rangeEnd = span[0], span[1] + 1
                break
        return text[rangeStart:rangeEnd], rangeStart, rangeEnd

    def _getTextAtOffset(self, obj, offset, granularity):
        def stringForDebug(x):
            return x.replace(self.EMBEDDED_OBJECT_CHARACTER, "[OBJ]").replace("\n", "\\n")

        if not obj:
            tokens = ["WEB:", granularity, f"at offset {offset} for", obj, ":",
                      "'', Start: 0, End: 0. (obj is None)"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return '', 0, 0

        if not self.treatAsTextObject(obj):
            tokens = ["WEB:", granularity, f"at offset {offset} for", obj, ":",
                      "'', Start: 0, End: 1. (treatAsTextObject() returned False)"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return '', 0, 1

        allText = AXText.get_all_text(obj)
        if granularity is None:
            string, start, end = allText, 0, len(allText)
            s = stringForDebug(string)
            tokens = ["WEB:", granularity, f"at offset {offset} for", obj, ":",
                      f"'{s}', Start: {start}, End: {end}."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return string, start, end

        if granularity == Atspi.TextGranularity.SENTENCE and not AXUtilities.is_editable(obj):
            if AXObject.get_role(obj) in [Atspi.Role.LIST_ITEM, Atspi.Role.HEADING] \
               or not (re.search(r"\w", allText) and self.isTextBlockElement(obj)):
                string, start, end = allText, 0, len(allText)
                s = stringForDebug(string)
                tokens = ["WEB:", granularity, f"at offset {offset} for", obj, ":",
                          f"'{s}', Start: {start}, End: {end}."]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                return string, start, end

        if granularity == Atspi.TextGranularity.LINE and self.treatAsEndOfLine(obj, offset):
            offset -= 1
            tokens = ["WEB: Line sought for", obj, "at end of text. Adjusting offset to",
                      offset, "."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        offset = max(0, offset)
        if granularity == Atspi.TextGranularity.LINE:
            string, start, end = AXText.get_line_at_offset(obj, offset)
        elif granularity == Atspi.TextGranularity.SENTENCE:
            string, start, end = AXText.get_sentence_at_offset(obj, offset)
        elif granularity == Atspi.TextGranularity.WORD:
            string, start, end = AXText.get_word_at_offset(obj, offset)
        elif granularity == Atspi.TextGranularity.CHAR:
            string, start, end = AXText.get_character_at_offset(obj, offset)
        else:
            string, start, end = AXText.get_line_at_offset(obj, offset)

        s = stringForDebug(string)
        tokens = ["WEB:", granularity, f"at offset {offset} for", obj, ":",
                  f"'{s}', Start: {start}, End: {end}."]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        # https://bugzilla.mozilla.org/show_bug.cgi?id=1141181
        needSadHack = granularity == Atspi.TextGranularity.SENTENCE and allText \
           and (string, start, end) == ("", 0, 0)

        if needSadHack:
            sadString, sadStart, sadEnd = self.__findSentence(obj, offset)
            s = stringForDebug(sadString)
            tokens = ["HACK: Attempting to recover from above failure. Result:",
                      f"'{s}', Start: {sadStart}, End: {sadEnd}."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return sadString, sadStart, sadEnd

        return string, start, end

    def _getContentsForObj(self, obj, offset, granularity):
        tokens = ["WEB: Attempting to get contents for", obj, granularity]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        if not obj:
            return []

        if granularity == Atspi.TextGranularity.SENTENCE and AXUtilities.is_time(obj):
            string = AXText.get_all_text(obj)
            if string:
                return [[obj, 0, len(string), string]]

        if granularity == Atspi.TextGranularity.LINE:
            if AXUtilities.is_math_related(obj):
                math = AXObject.find_ancestor_inclusive(obj, AXUtilities.is_math)
                return [[math, 0, 1, '']]

            treatAsText = self.treatAsTextObject(obj)
            if self.elementLinesAreSingleChars(obj):
                if AXObject.get_name(obj) and treatAsText:
                    tokens = ["WEB: Returning name as contents for", obj, "(single-char lines)"]
                    debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                    return [[obj, 0, AXText.get_character_count(obj), AXObject.get_name(obj)]]

                tokens = ["WEB: Returning all text as contents for", obj, "(single-char lines)"]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                granularity = None

            if self.elementLinesAreSingleWords(obj):
                if AXObject.get_name(obj) and treatAsText:
                    tokens = ["WEB: Returning name as contents for", obj, "(single-word lines)"]
                    debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                    return [[obj, 0, AXText.get_character_count(obj), AXObject.get_name(obj)]]

                tokens = ["WEB: Returning all text as contents for", obj, "(single-word lines)"]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                granularity = None

        if AXUtilities.is_internal_frame(obj) and AXObject.get_child_count(obj) == 1:
            return self._getContentsForObj(AXObject.get_child(obj, 0), 0, granularity)

        string, start, end = self._getTextAtOffset(obj, offset, granularity)
        if not string:
            return [[obj, start, end, string]]

        stringOffset = offset - start
        try:
            char = string[stringOffset]
        except Exception as error:
            msg = f"WEB: Could not get char {stringOffset} for '{string}': {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
        else:
            if char == self.EMBEDDED_OBJECT_CHARACTER:
                child = AXHypertext.get_child_at_offset(obj, offset)
                if child:
                    return self._getContentsForObj(child, 0, granularity)

        ranges = [m.span() for m in re.finditer("[^\ufffc]+", string)]
        strings = list(filter(lambda x: x[0] <= stringOffset <= x[1], ranges))
        if len(strings) == 1:
            rangeStart, rangeEnd = strings[0]
            start += rangeStart
            string = string[rangeStart:rangeEnd]
            end = start + len(string)

        if granularity in [Atspi.TextGranularity.WORD, Atspi.TextGranularity.CHAR]:
            return [[obj, start, end, string]]

        return self.adjustContentsForLanguage([[obj, start, end, string]])

    def getSentenceContentsAtOffset(self, obj, offset, useCache=True):
        self._canHaveCaretContextDecision = {}
        rv = self._getSentenceContentsAtOffset(obj, offset, useCache)
        self._canHaveCaretContextDecision = {}
        return rv

    def _getSentenceContentsAtOffset(self, obj, offset, useCache=True):
        if not obj:
            return []

        offset = max(0, offset)

        if useCache:
            if self.findObjectInContents(
                    obj, offset, self._currentSentenceContents, usingCache=True) != -1:
                return self._currentSentenceContents

        granularity = Atspi.TextGranularity.SENTENCE
        objects = self._getContentsForObj(obj, offset, granularity)
        if AXUtilities.is_editable(obj):
            if AXUtilities.is_focused(obj):
                return objects
            if self.isContentEditableWithEmbeddedObjects(obj):
                return objects

        def _treatAsSentenceEnd(x):
            xObj, xStart, xEnd, xString = x
            if not self.isTextBlockElement(xObj):
                return False

            if self.treatAsTextObject(xObj) and 0 < AXText.get_character_count(xObj) <= xEnd:
                return True

            if 0 <= xStart <= 5:
                xString = " ".join(xString.split()[1:])

            match = re.search(r"\S[\.\!\?]+(\s|\Z)", xString)
            return match is not None

        # Check for things in the same sentence before this object.
        firstObj, firstStart, firstEnd, firstString = objects[0]
        while firstObj and firstString:
            if self.isTextBlockElement(firstObj):
                if firstStart == 0:
                    break
            elif self.isTextBlockElement(AXObject.get_parent(firstObj)):
                if AXHypertext.get_character_offset_in_parent(firstObj) == 0:
                    break

            prevObj, pOffset = self.findPreviousCaretInOrder(firstObj, firstStart)
            onLeft = self._getContentsForObj(prevObj, pOffset, granularity)
            onLeft = list(filter(lambda x: x not in objects, onLeft))
            endsOnLeft = list(filter(_treatAsSentenceEnd, onLeft))
            if endsOnLeft:
                i = onLeft.index(endsOnLeft[-1])
                onLeft = onLeft[i+1:]

            if not onLeft:
                break

            objects[0:0] = onLeft
            firstObj, firstStart, firstEnd, firstString = objects[0]

        # Check for things in the same sentence after this object.
        while not _treatAsSentenceEnd(objects[-1]):
            lastObj, lastStart, lastEnd, lastString = objects[-1]
            nextObj, nOffset = self.findNextCaretInOrder(lastObj, lastEnd - 1)
            onRight = self._getContentsForObj(nextObj, nOffset, granularity)
            onRight = list(filter(lambda x: x not in objects, onRight))
            if not onRight:
                break

            objects.extend(onRight)

        if useCache:
            self._currentSentenceContents = objects

        return objects

    def getCharacterContentsAtOffset(self, obj, offset, useCache=True):
        self._canHaveCaretContextDecision = {}
        rv = self._getCharacterContentsAtOffset(obj, offset, useCache)
        self._canHaveCaretContextDecision = {}
        return rv

    def _getCharacterContentsAtOffset(self, obj, offset, useCache=True):
        if not obj:
            return []

        offset = max(0, offset)

        if useCache:
            if self.findObjectInContents(
                    obj, offset, self._currentCharacterContents, usingCache=True) != -1:
                return self._currentCharacterContents

        granularity = Atspi.TextGranularity.CHAR
        objects = self._getContentsForObj(obj, offset, granularity)
        if useCache:
            self._currentCharacterContents = objects

        return objects

    def getWordContentsAtOffset(self, obj, offset, useCache=True):
        self._canHaveCaretContextDecision = {}
        rv = self._getWordContentsAtOffset(obj, offset, useCache)
        self._canHaveCaretContextDecision = {}
        return rv

    def _getWordContentsAtOffset(self, obj, offset, useCache=True):
        if not obj:
            return []

        offset = max(0, offset)

        if useCache:
            if self.findObjectInContents(
                    obj, offset, self._currentWordContents, usingCache=True) != -1:
                self._debugContentsInfo(obj, offset, self._currentWordContents, "Word (cached)")
                return self._currentWordContents

        granularity = Atspi.TextGranularity.WORD
        objects = self._getContentsForObj(obj, offset, granularity)
        extents = self.getExtents(obj, offset, offset + 1)

        def _include(x):
            if x in objects:
                return False

            if AXUtilities.is_text_input(obj):
                return False

            xObj, xStart, xEnd, xString = x
            if xStart == xEnd or not xString:
                return False

            if AXUtilities.is_table_cell_or_header(obj) \
               and AXUtilities.is_table_cell_or_header(xObj) and obj != xObj:
                return False

            xExtents = self.getExtents(xObj, xStart, xStart + 1)
            return self.extentsAreOnSameLine(extents, xExtents)

        # Check for things in the same word to the left of this object.
        firstObj, firstStart, firstEnd, firstString = objects[0]
        prevObj, pOffset = self.findPreviousCaretInOrder(firstObj, firstStart)
        while prevObj and firstString and prevObj != firstObj:
            char = AXText.get_character_at_offset(prevObj, pOffset)[0]
            if not char or char.isspace():
                break

            onLeft = self._getContentsForObj(prevObj, pOffset, granularity)
            onLeft = list(filter(_include, onLeft))
            if not onLeft:
                break

            if self._contentIsSubsetOf(objects[0], onLeft[-1]):
                objects.pop(0)

            objects[0:0] = onLeft
            firstObj, firstStart, firstEnd, firstString = objects[0]
            prevObj, pOffset = self.findPreviousCaretInOrder(firstObj, firstStart)

        # Check for things in the same word to the right of this object.
        lastObj, lastStart, lastEnd, lastString = objects[-1]
        while lastObj and lastString and not lastString[-1].isspace():
            nextObj, nOffset = self.findNextCaretInOrder(lastObj, lastEnd - 1)
            if nextObj == lastObj:
                break

            onRight = self._getContentsForObj(nextObj, nOffset, granularity)
            if onRight and self._contentIsSubsetOf(objects[0], onRight[-1]):
                onRight = onRight[0:-1]

            onRight = list(filter(_include, onRight))
            if not onRight:
                break

            objects.extend(onRight)
            lastObj, lastStart, lastEnd, lastString = objects[-1]

        # We want to treat the list item marker as its own word.
        firstObj, firstStart, firstEnd, firstString = objects[0]
        if firstStart == 0 and AXUtilities.is_list_item(firstObj):
            objects = [objects[0]]

        if useCache:
            self._currentWordContents = objects

        self._debugContentsInfo(obj, offset, objects, "Word (not cached)")
        return objects

    def getObjectContentsAtOffset(self, obj, offset=0, useCache=True):
        self._canHaveCaretContextDecision = {}
        rv = self._getObjectContentsAtOffset(obj, offset, useCache)
        self._canHaveCaretContextDecision = {}
        return rv

    def _getObjectContentsAtOffset(self, obj, offset=0, useCache=True):
        if not obj:
            return []

        if AXObject.is_dead(obj):
            msg = "ERROR: Cannot get object contents at offset for dead object."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return []

        offset = max(0, offset)

        if useCache:
            if self.findObjectInContents(
                    obj, offset, self._currentObjectContents, usingCache=True) != -1:
                self._debugContentsInfo(
                    obj, offset, self._currentObjectContents, "Object (cached)")
                return self._currentObjectContents

        objIsLandmark = AXUtilities.is_landmark(obj)

        def _isInObject(x):
            if not x:
                return False
            if x == obj:
                return True
            return _isInObject(AXObject.get_parent(x))

        def _include(x):
            if x in objects:
                return False

            xObj, xStart, xEnd, xString = x
            if xStart == xEnd:
                return False

            if objIsLandmark and AXUtilities.is_landmark(xObj) and obj != xObj:
                return False

            return _isInObject(xObj)

        objects = self._getContentsForObj(obj, offset, None)
        if not objects:
            tokens = ["ERROR: Cannot get object contents for", obj, f"at offset {offset}"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return []

        lastObj, lastStart, lastEnd, lastString = objects[-1]
        nextObj, nOffset = self.findNextCaretInOrder(lastObj, lastEnd - 1)
        while nextObj:
            onRight = self._getContentsForObj(nextObj, nOffset, None)
            onRight = list(filter(_include, onRight))
            if not onRight:
                break

            objects.extend(onRight)
            lastObj, lastEnd = objects[-1][0], objects[-1][2]
            nextObj, nOffset = self.findNextCaretInOrder(lastObj, lastEnd - 1)

        if useCache:
            self._currentObjectContents = objects

        self._debugContentsInfo(obj, offset, objects, "Object (not cached)")
        return objects

    def _contentIsSubsetOf(self, contentA, contentB):
        objA, startA, endA, stringA = contentA
        objB, startB, endB, stringB = contentB
        if objA == objB:
            setA = set(range(startA, endA))
            setB = set(range(startB, endB))
            return setA.issubset(setB)

        return False

    def _debugContentsInfo(self, obj, offset, contents, contentsMsg=""):
        if debug.LEVEL_INFO < debug.debugLevel:
            return

        tokens = ["WEB: ", contentsMsg, "for", obj, "at offset", offset, ":"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        indent = " " * 8
        for i, (acc, start, end, string) in enumerate(contents):
            try:
                extents = self.getExtents(acc, start, end)
            except Exception as error:
                extents = f"(exception: {error})"
            msg = f"     {i}. chars: {start}-{end}: '{string}' extents={extents}\n"
            msg += AXUtilitiesDebugging.object_details_as_string(acc, indent, False)
            debug.print_message(debug.LEVEL_INFO, msg, True)

    def treatAsEndOfLine(self, obj, offset):
        if not self.isContentEditableWithEmbeddedObjects(obj):
            return False

        if not AXObject.supports_text(obj):
            return False

        if self.isDocument(obj):
            return False

        if offset == AXText.get_character_count(obj):
            tokens = ["WEB: ", obj, "offset", offset, "is end of line: offset is characterCount"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        # Do not treat a literal newline char as the end of line. When there is an
        # actual newline character present, user agents should give us the right value
        # for the line at that offset. Here we are trying to figure out where asking
        # for the line at offset will give us the next line rather than the line where
        # the cursor is physically blinking.
        char = AXText.get_character_at_offset(obj, offset)[0]
        if char == self.EMBEDDED_OBJECT_CHARACTER:
            prevExtents = self.getExtents(obj, offset - 1, offset)
            thisExtents = self.getExtents(obj, offset, offset + 1)
            sameLine = self.extentsAreOnSameLine(prevExtents, thisExtents)
            tokens = ["WEB: ", obj, "offset", offset, "is [obj]. Same line: ",
                      sameLine, "Is end of line: ", not sameLine]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return not sameLine

        return False

    def getLineContentsAtOffset(self, obj, offset, layoutMode=None, useCache=True):
        self._canHaveCaretContextDecision = {}
        rv = self._getLineContentsAtOffset(obj, offset, layoutMode, useCache)
        self._canHaveCaretContextDecision = {}
        return rv

    def _getLineContentsAtOffset(self, obj, offset, layoutMode=None, useCache=True):
        start_time = time.time()
        if not obj:
            return []

        if AXObject.is_dead(obj):
            msg = "ERROR: Cannot get line contents at offset for dead object."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return []

        offset = max(0, offset)
        if (AXUtilities.is_tool_bar(obj) or AXUtilities.is_menu_bar(obj)) \
                and not self._treatObjectAsWhole(obj):
            child = AXHypertext.get_child_at_offset(obj, offset)
            if child:
                obj = child
                offset = 0

        if useCache:
            if self.findObjectInContents(
                    obj, offset, self._currentLineContents, usingCache=True) != -1:
                self._debugContentsInfo(
                    obj, offset, self._currentLineContents, "Line (cached)")
                return self._currentLineContents

        if layoutMode is None:
            layoutMode = settings_manager.get_manager().get_setting('layoutMode') \
                or self._script.inFocusMode()

        objects = []
        if offset > 0 and self.treatAsEndOfLine(obj, offset):
            extents = self.getExtents(obj, offset - 1, offset)
        else:
            extents = self.getExtents(obj, offset, offset + 1)

        if AXObject.find_ancestor_inclusive(obj, AXUtilities.is_inline_list_item) is not None:
            container = AXObject.find_ancestor(obj, AXUtilities.is_list)
            if container:
                extents = self.getExtents(container, 0, 1)

        objBanner = AXObject.find_ancestor(obj, AXUtilities.is_landmark_banner)

        def _include(x):
            if x in objects:
                return False

            xObj, xStart, xEnd, xString = x
            if xStart == xEnd:
                return False

            xExtents = self.getExtents(xObj, xStart, xStart + 1)

            if obj != xObj:
                if AXUtilities.is_landmark(obj) and AXUtilities.is_landmark(xObj):
                    return False
                if self.isLink(obj) and self.isLink(xObj):
                    xObjBanner = AXObject.find_ancestor(xObj, AXUtilities.is_landmark_banner)
                    if (objBanner or xObjBanner) and objBanner != xObjBanner:
                        return False
                    if abs(extents[0] - xExtents[0]) <= 1 and abs(extents[1] - xExtents[1]) <= 1:
                        # This happens with dynamic skip links such as found on Wikipedia.
                        return False
                elif self.isBlockListDescendant(obj) != self.isBlockListDescendant(xObj):
                    return False
                elif AXUtilities.is_tree_related(obj) and AXUtilities.is_tree_related(xObj):
                    return False
                elif AXUtilities.is_heading(obj) and AXComponent.has_no_size(obj):
                    return False
                elif AXUtilities.is_heading(xObj) and AXComponent.has_no_size(xObj):
                    return False

            if AXUtilities.is_math(xObj) or AXUtilities.is_math_related(obj):
                onSameLine = self.extentsAreOnSameLine(extents, xExtents, extents[3])
            elif AXUtilities.is_subscript_or_superscript_text(xObj):
                onSameLine = self.extentsAreOnSameLine(extents, xExtents, xExtents[3])
            else:
                onSameLine = self.extentsAreOnSameLine(extents, xExtents)
            return onSameLine

        granularity = Atspi.TextGranularity.LINE
        objects = self._getContentsForObj(obj, offset, granularity)
        if not layoutMode:
            if useCache:
                self._currentLineContents = objects

            self._debugContentsInfo(obj, offset, objects, "Line (not layout mode)")
            return objects

        if not (objects and objects[0]):
            tokens = ["WEB: Error. No objects found for", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return []

        firstObj, firstStart, firstEnd, firstString = objects[0]
        if (extents[2] == 0 and extents[3] == 0) or AXUtilities.is_math_related(firstObj):
            extents = self.getExtents(firstObj, firstStart, firstEnd)

        lastObj, lastStart, lastEnd, lastString = objects[-1]
        if AXUtilities.is_math(lastObj):
            lastObj, lastEnd = self.lastContext(lastObj)
            lastEnd += 1

        document = self.getDocumentForObject(obj)
        prevObj, pOffset = self.findPreviousCaretInOrder(firstObj, firstStart)
        nextObj, nOffset = self.findNextCaretInOrder(lastObj, lastEnd - 1)

        # Check for things on the same line to the left of this object.
        prevStartTime = time.time()
        while prevObj and self.getDocumentForObject(prevObj) == document:
            char = AXText.get_character_at_offset(prevObj, pOffset)[0]
            if char.isspace():
                prevObj, pOffset = self.findPreviousCaretInOrder(prevObj, pOffset)

            char = AXText.get_character_at_offset(prevObj, pOffset)[0]
            if char == "\n" and firstObj == prevObj:
                break

            onLeft = self._getContentsForObj(prevObj, pOffset, granularity)
            onLeft = list(filter(_include, onLeft))
            if not onLeft:
                break

            if self._contentIsSubsetOf(objects[0], onLeft[-1]):
                objects.pop(0)

            objects[0:0] = onLeft
            firstObj, firstStart = objects[0][0], objects[0][1]
            prevObj, pOffset = self.findPreviousCaretInOrder(firstObj, firstStart)

        prevEndTime = time.time()
        msg = f"INFO: Time to get line contents on left: {prevEndTime - prevStartTime:.4f}s"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        # Check for things on the same line to the right of this object.
        nextStartTime = time.time()
        while nextObj and self.getDocumentForObject(nextObj) == document:
            char = AXText.get_character_at_offset(nextObj, nOffset)[0]
            if char.isspace():
                nextObj, nOffset = self.findNextCaretInOrder(nextObj, nOffset)

            char = AXText.get_character_at_offset(nextObj, nOffset)[0]
            if char == "\n" and lastObj == nextObj:
                break

            onRight = self._getContentsForObj(nextObj, nOffset, granularity)
            if onRight and self._contentIsSubsetOf(objects[0], onRight[-1]):
                onRight = onRight[0:-1]

            onRight = list(filter(_include, onRight))
            if not onRight:
                break

            objects.extend(onRight)
            lastObj, lastEnd = objects[-1][0], objects[-1][2]
            if AXUtilities.is_math(lastObj):
                lastObj, lastEnd = self.lastContext(lastObj)
                lastEnd += 1

            nextObj, nOffset = self.findNextCaretInOrder(lastObj, lastEnd - 1)

        nextEndTime = time.time()
        msg = f"INFO: Time to get line contents on right: {nextEndTime - nextStartTime:.4f}s"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        firstObj, firstStart, firstEnd, firstString = objects[0]
        if firstString == "\n" and len(objects) > 1:
            objects.pop(0)

        if useCache:
            self._currentLineContents = objects

        msg = f"INFO: Time to get line contents: {time.time() - start_time:.4f}s"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        self._debugContentsInfo(obj, offset, objects, "Line (layout mode)")

        self._canHaveCaretContextDecision = {}
        return objects

    def getPreviousLineContents(self, obj=None, offset=-1, layoutMode=None, useCache=True):
        if obj is None:
            obj, offset = self.getCaretContext()

        tokens = ["WEB: Current context is: ", obj, ", ", offset]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if not AXObject.is_valid(obj):
            tokens = ["WEB: Current context obj", obj, "is not valid. Clearing cache."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            self.clearCachedObjects()

            obj, offset = self.getCaretContext()
            tokens = ["WEB: Now Current context is: ", obj, ", ", offset]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        line = self.getLineContentsAtOffset(obj, offset, layoutMode, useCache)
        if not (line and line[0]):
            return []

        firstObj, firstOffset = line[0][0], line[0][1]
        tokens = ["WEB: First context on line is: ", firstObj, ", ", firstOffset]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        skipSpace = not settings_manager.get_manager().get_setting("speakBlankLines")
        obj, offset = self.previousContext(firstObj, firstOffset, skipSpace)
        if not obj and firstObj:
            tokens = ["WEB: Previous context is: ", obj, ", ", offset, ". Trying again."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            self.clearCachedObjects()
            obj, offset = self.previousContext(firstObj, firstOffset, skipSpace)

        tokens = ["WEB: Previous context is: ", obj, ", ", offset]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        contents = self.getLineContentsAtOffset(obj, offset, layoutMode, useCache)
        if not contents:
            tokens = ["WEB: Could not get line contents for ", obj, ", ", offset]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return []

        if line == contents:
            obj, offset = self.previousContext(obj, offset, True)
            tokens = ["WEB: Got same line. Trying again with ", obj, ", ", offset]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            contents = self.getLineContentsAtOffset(obj, offset, layoutMode, useCache)

        if line == contents:
            start = AXHypertext.get_link_start_offset(obj)
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            if start >= 0:
                parent = AXObject.get_parent(obj)
                obj, offset = self.previousContext(parent, start, True)
                tokens = ["WEB: Trying again with", obj, ", ", offset]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                contents = self.getLineContentsAtOffset(obj, offset, layoutMode, useCache)

        return contents

    def getNextLineContents(self, obj=None, offset=-1, layoutMode=None, useCache=True):
        if obj is None:
            obj, offset = self.getCaretContext()

        tokens = ["WEB: Current context is: ", obj, ", ", offset]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if not AXObject.is_valid(obj):
            tokens = ["WEB: Current context obj", obj, "is not valid. Clearing cache."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            self.clearCachedObjects()

            obj, offset = self.getCaretContext()
            tokens = ["WEB: Now Current context is: ", obj, ", ", offset]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        line = self.getLineContentsAtOffset(obj, offset, layoutMode, useCache)
        if not (line and line[0]):
            return []

        lastObj, lastOffset = line[-1][0], line[-1][2] - 1
        math = AXObject.find_ancestor_inclusive(lastObj, AXUtilities.is_math)
        if math:
            lastObj, lastOffset = self.lastContext(math)

        tokens = ["WEB: Last context on line is: ", lastObj, ", ", lastOffset]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        skipSpace = not settings_manager.get_manager().get_setting("speakBlankLines")
        obj, offset = self.nextContext(lastObj, lastOffset, skipSpace)
        if not obj and lastObj:
            tokens = ["WEB: Next context is: ", obj, ", ", offset, ". Trying again."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            self.clearCachedObjects()
            obj, offset = self.nextContext(lastObj, lastOffset, skipSpace)

        tokens = ["WEB: Next context is: ", obj, ", ", offset]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        contents = self.getLineContentsAtOffset(obj, offset, layoutMode, useCache)
        if line == contents:
            obj, offset = self.nextContext(obj, offset, True)
            tokens = ["WEB: Got same line. Trying again with ", obj, ", ", offset]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            contents = self.getLineContentsAtOffset(obj, offset, layoutMode, useCache)

        if line == contents:
            end = AXHypertext.get_link_end_offset(obj)
            if end >= 0:
                parent = AXObject.get_parent(obj)
                obj, offset = self.nextContext(parent, end, True)
                tokens = ["WEB: Trying again with", obj, ", ", offset]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                contents = self.getLineContentsAtOffset(obj, offset, layoutMode, useCache)

        if not contents:
            tokens = ["WEB: Could not get line contents for ", obj, ", ", offset]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return []

        return contents

    def _findSelectionBoundaryObject(self, root, findStart=True):
        string = AXText.get_selected_text(root)[0]
        if not string:
            return None

        if findStart and not string.startswith(self.EMBEDDED_OBJECT_CHARACTER):
            return root

        if not findStart and not string.endswith(self.EMBEDDED_OBJECT_CHARACTER):
            return root

        indices = list(range(AXObject.get_child_count(root)))
        if not findStart:
            indices.reverse()

        for i in indices:
            result = self._findSelectionBoundaryObject(AXObject.get_child(root, i), findStart)
            if result:
                return result

        return None

    def _getSelectionAnchorAndFocus(self, root):
        obj1 = self._findSelectionBoundaryObject(root, True)
        obj2 = self._findSelectionBoundaryObject(root, False)
        return obj1, obj2

    def _getSubtree(self, startObj, endObj):
        if not (startObj and endObj):
            return []

        if AXObject.is_dead(startObj):
            msg = "INFO: Cannot get subtree: Start object is dead."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return []

        def _include(x):
            return x is not None

        def _exclude(x):
            return not AXUtilities.is_web_element(x)

        subtree = []
        startObjParent = AXObject.get_parent(startObj)
        for i in range(AXObject.get_index_in_parent(startObj),
                        AXObject.get_child_count(startObjParent)):
            child = AXObject.get_child(startObjParent, i)
            if not AXUtilities.is_web_element(child):
                continue
            subtree.append(child)
            subtree.extend(self.findAllDescendants(child, _include, _exclude))
            if endObj in subtree:
                break

        if endObj == startObj:
            return subtree

        if endObj not in subtree:
            subtree.append(endObj)
            subtree.extend(self.findAllDescendants(endObj, _include, _exclude))

        endObjParent = AXObject.get_parent(endObj)
        endObjIndex = AXObject.get_index_in_parent(endObj)
        lastObj = AXObject.get_child(endObjParent, endObjIndex + 1) or endObj

        try:
            endIndex = subtree.index(lastObj)
        except ValueError:
            pass
        else:
            if lastObj == endObj:
                endIndex += 1
            subtree = subtree[:endIndex]

        return subtree

    def handleTextSelectionChange(self, obj, speakMessage=True):
        if not self.inDocumentContent(obj) or self._script.inFocusMode():
            return super().handleTextSelectionChange(obj)

        oldStart, oldEnd = \
            self._script.point_of_reference.get('selectionAnchorAndFocus', (None, None))
        start, end = self._getSelectionAnchorAndFocus(obj)
        self._script.point_of_reference['selectionAnchorAndFocus'] = (start, end)

        def _cmp(obj1, obj2):
            return self.pathComparison(AXObject.get_path(obj1), AXObject.get_path(obj2))

        oldSubtree = self._getSubtree(oldStart, oldEnd)
        if start == oldStart and end == oldEnd:
            descendants = oldSubtree
        else:
            newSubtree = self._getSubtree(start, end)
            descendants = sorted(set(oldSubtree).union(newSubtree), key=functools.cmp_to_key(_cmp))

        if not descendants:
            return False

        for descendant in descendants:
            if descendant not in (oldStart, oldEnd, start, end) \
               and AXObject.find_ancestor(descendant, lambda x: x in descendants):
                AXText.update_cached_selected_text(descendant)
            else:
                super().handleTextSelectionChange(descendant, speakMessage)

        return True

    def inTopLevelWebApp(self, obj=None):
        if not obj:
            obj = focus_manager.get_manager().get_locus_of_focus()

        rv = self._inTopLevelWebApp.get(hash(obj))
        if rv is not None:
            return rv

        document = self.getDocumentForObject(obj)
        if not document and self.isDocument(obj):
            document = obj

        rv = self.isTopLevelWebApp(document)
        self._inTopLevelWebApp[hash(obj)] = rv
        return rv

    def isTopLevelWebApp(self, obj):
        if AXUtilities.is_embedded(obj) \
           and not self.getDocumentForObject(AXObject.get_parent(obj)):
            uri = AXDocument.get_uri(obj)
            rv = bool(uri and uri.startswith("http"))
            tokens = ["WEB:", obj, "is top-level web application:", rv, "(URI:", uri, ")"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return rv

        return False

    def forceBrowseModeForWebAppDescendant(self, obj):
        if not AXObject.find_ancestor(obj, AXUtilities.is_embedded):
            return False

        if AXUtilities.is_tool_tip(obj):
            return AXUtilities.is_focused(obj)

        if AXUtilities.is_document_web(obj):
            return not self.isFocusModeWidget(obj)

        return False

    def isFocusModeWidget(self, obj):
        if AXUtilities.is_editable(obj):
            tokens = ["WEB:", obj, "is focus mode widget because it's editable"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        if AXUtilities.is_expandable(obj) and AXUtilities.is_focusable(obj) \
           and not AXUtilities.is_link(obj):
            tokens = ["WEB:", obj, "is focus mode widget because it's expandable and focusable"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        alwaysFocusModeRoles = [Atspi.Role.COMBO_BOX,
                                Atspi.Role.ENTRY,
                                Atspi.Role.LIST_BOX,
                                Atspi.Role.MENU,
                                Atspi.Role.MENU_ITEM,
                                Atspi.Role.CHECK_MENU_ITEM,
                                Atspi.Role.RADIO_MENU_ITEM,
                                Atspi.Role.PAGE_TAB,
                                Atspi.Role.PASSWORD_TEXT,
                                Atspi.Role.PROGRESS_BAR,
                                Atspi.Role.SLIDER,
                                Atspi.Role.SPIN_BUTTON,
                                Atspi.Role.TOOL_BAR,
                                Atspi.Role.TREE_ITEM,
                                Atspi.Role.TREE_TABLE,
                                Atspi.Role.TREE]

        role = AXObject.get_role(obj)
        if role in alwaysFocusModeRoles:
            tokens = ["WEB:", obj, "is focus mode widget due to its role"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        if role in [Atspi.Role.TABLE_CELL, Atspi.Role.TABLE] \
           and AXTable.is_layout_table(AXTable.get_table(obj)):
            tokens = ["WEB:", obj, "is not focus mode widget because it's layout only"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        if AXUtilities.is_list_box_item(obj, role):
            tokens = ["WEB:", obj, "is focus mode widget because it's a listbox item"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        if AXUtilities.is_button_with_popup(obj, role):
            tokens = ["WEB:", obj, "is focus mode widget because it's a button with popup"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        focusModeRoles = [Atspi.Role.EMBEDDED,
                          Atspi.Role.TABLE_CELL,
                          Atspi.Role.TABLE]

        if role in focusModeRoles \
           and not self.isTextBlockElement(obj) \
           and not self.hasNameAndActionAndNoUsefulChildren(obj) \
           and not AXDocument.is_pdf(self.documentFrame()):
            tokens = ["WEB:", obj, "is focus mode widget based on presumed functionality"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        if AXObject.find_ancestor(obj, AXUtilities.is_grid) is not None:
            tokens = ["WEB:", obj, "is focus mode widget because it's a grid descendant"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        if AXObject.find_ancestor(obj, AXUtilities.is_menu) is not None:
            tokens = ["WEB:", obj, "is focus mode widget because it's a menu descendant"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if AXObject.find_ancestor(obj, AXUtilities.is_tool_bar) is not None:
            tokens = ["WEB:", obj, "is focus mode widget because it's a toolbar descendant"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        if self.isContentEditableWithEmbeddedObjects(obj):
            tokens = ["WEB:", obj, "is focus mode widget because it's content editable"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        return False

    def _textBlockElementRoles(self):
        roles = [Atspi.Role.ARTICLE,
                 Atspi.Role.CAPTION,
                 Atspi.Role.COLUMN_HEADER,
                 Atspi.Role.COMMENT,
                 Atspi.Role.CONTENT_DELETION,
                 Atspi.Role.CONTENT_INSERTION,
                 Atspi.Role.DEFINITION,
                 Atspi.Role.DESCRIPTION_LIST,
                 Atspi.Role.DESCRIPTION_TERM,
                 Atspi.Role.DESCRIPTION_VALUE,
                 Atspi.Role.DOCUMENT_FRAME,
                 Atspi.Role.DOCUMENT_WEB,
                 Atspi.Role.FOOTER,
                 Atspi.Role.FORM,
                 Atspi.Role.HEADING,
                 Atspi.Role.LIST,
                 Atspi.Role.LIST_ITEM,
                 Atspi.Role.MARK,
                 Atspi.Role.PARAGRAPH,
                 Atspi.Role.ROW_HEADER,
                 Atspi.Role.SECTION,
                 Atspi.Role.STATIC,
                 Atspi.Role.SUGGESTION,
                 Atspi.Role.TEXT,
                 Atspi.Role.TABLE_CELL]

        return roles

    def unrelatedLabels(self, root, onlyShowing=True, minimumWords=3):
        if not (root and self.inDocumentContent(root)):
            return super().unrelatedLabels(root, onlyShowing, minimumWords)

        return []

    def isFocusableWithMathChild(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return False

        rv = self._isFocusableWithMathChild.get(hash(obj))
        if rv is not None:
            return rv

        rv = False
        if AXUtilities.is_focusable(obj) \
            and not self.isDocument(obj):
            for child in AXObject.iter_children(obj, AXUtilities.is_math):
                rv = True
                break

        self._isFocusableWithMathChild[hash(obj)] = rv
        return rv

    def isFocusedWithMathChild(self, obj):
        if not self.isFocusableWithMathChild(obj):
            return False
        return AXUtilities.is_focused(obj)

    def isTextBlockElement(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return False

        rv = self._isTextBlockElement.get(hash(obj))
        if rv is not None:
            return rv

        role = AXObject.get_role(obj)
        textBlockElements = self._textBlockElementRoles()
        if role not in textBlockElements:
            rv = False
        elif not AXObject.supports_text(obj):
            rv = False
        elif AXUtilities.is_editable(obj):
            rv = False
        elif AXUtilities.is_grid_cell(obj):
            rv = False
        elif AXUtilities.is_document(obj):
            rv = True
        elif self.isCustomImage(obj):
            rv = False
        elif not AXUtilities.is_focusable(obj):
            rv = not self.hasNameAndActionAndNoUsefulChildren(obj)
        else:
            rv = False

        self._isTextBlockElement[hash(obj)] = rv
        return rv

    def _advanceCaretInEmptyObject(self, obj):
        if AXUtilities.is_table_cell(obj) and not self.treatAsTextObject(obj):
            return not self._script.caret_navigation.last_input_event_was_navigation_command()

        return True

    def treatAsDiv(self, obj, offset=None):
        if not (obj and self.inDocumentContent(obj)):
            return False

        if AXUtilities.is_description_list(obj):
            return False

        if AXUtilities.is_list(obj) and offset is not None:
            string = AXText.get_substring(obj, offset, offset + 1)
            if string and string != self.EMBEDDED_OBJECT_CHARACTER:
                return True

        childCount = AXObject.get_child_count(obj)
        if AXUtilities.is_panel(obj) and not childCount:
            return True

        rv = self._treatAsDiv.get(hash(obj))
        if rv is not None:
            return rv

        validRoles = self._validChildRoles.get(AXObject.get_role(obj))
        if validRoles:
            if not childCount:
                rv = True
            else:
                def pred1(x):
                    return x is not None and AXObject.get_role(x) not in validRoles

                rv = bool([x for x in AXObject.iter_children(obj, pred1)])

        if not rv:
            parent = AXObject.get_parent(obj)
            validRoles = self._validChildRoles.get(parent)
            if validRoles:
                def pred2(x):
                    return x is not None and AXObject.get_role(x) not in validRoles

                rv = bool([x for x in AXObject.iter_children(parent, pred2)])

        self._treatAsDiv[hash(obj)] = rv
        return rv

    def filterContentsForPresentation(self, contents, inferLabels=False):
        def _include(x):
            obj, start, end, string = x
            if not obj or AXObject.is_dead(obj):
                return False

            rv = self._shouldFilter.get(hash(obj))
            if rv is not None:
                return rv

            text = string or AXObject.get_name(obj)
            rv = True
            # TODO - JD: Audit this to see if they are now redundant.
            if ((self.isTextBlockElement(obj) or self.isLink(obj)) and not text) \
               or (self.isContentEditableWithEmbeddedObjects(obj) and not string.strip()) \
               or self.isEmptyAnchor(obj) \
               or (AXComponent.has_no_size(obj) and not text) \
               or AXUtilities.is_hidden(obj) \
               or self.isOffScreenLabel(obj) \
               or self.isUselessImage(obj) \
               or self.isErrorForContents(obj, contents) \
               or self.isLabellingContents(obj, contents):
                rv = False
            elif AXUtilities.is_table_row(obj):
                rv = AXUtilities.has_explicit_name(obj)
            else:
                widget = self.isInferredLabelForContents(x, contents)
                alwaysFilter = [Atspi.Role.RADIO_BUTTON, Atspi.Role.CHECK_BOX]
                if widget and (inferLabels or AXObject.get_role(widget) in alwaysFilter):
                    rv = False

            self._shouldFilter[hash(obj)] = rv
            return rv

        if len(contents) == 1:
            return contents

        rv = list(filter(_include, contents))
        self._shouldFilter = {}
        return rv

    def needsSeparator(self, lastChar, nextChar):
        if lastChar.isspace() or nextChar.isspace():
            return False

        openingPunctuation = ["(", "[", "{", "<"]
        closingPunctuation = [".", "?", "!", ":", ",", ";", ")", "]", "}", ">"]
        if lastChar in closingPunctuation or nextChar in openingPunctuation:
            return True
        if lastChar in openingPunctuation or nextChar in closingPunctuation:
            return False

        return lastChar.isalnum()

    def hasGridDescendant(self, obj):
        if not obj:
            return False

        rv = self._hasGridDescendant.get(hash(obj))
        if rv is not None:
            return rv

        if not AXObject.get_child_count(obj):
            rv = False
        else:
            document = self.documentFrame(obj)
            if obj != document:
                document_has_grids = self.hasGridDescendant(document)
                if not document_has_grids:
                    rv = False

        if rv is None:
            grids = AXUtilities.find_all_grids(obj)
            rv = bool(grids)

        self._hasGridDescendant[hash(obj)] = rv
        return rv

    def isCellWithNameFromHeader(self, obj):
        if not AXUtilities.is_table_cell(obj):
            return False

        name = AXObject.get_name(obj)
        if not name:
            return False

        headers = AXTable.get_column_headers(obj)
        for header in headers:
            if AXObject.get_name(header) == name:
                return True

        headers = AXTable.get_row_headers(obj)
        for header in headers:
            if AXObject.get_name(header) == name:
                return True

        return False

    def shouldReadFullRow(self, obj, prevObj=None):
        if not (obj and self.inDocumentContent(obj)):
            return super().shouldReadFullRow(obj, prevObj)

        if not super().shouldReadFullRow(obj, prevObj):
            return False

        if AXObject.find_ancestor(obj, AXUtilities.is_grid) is not None:
            return not self._script.inFocusMode()

        if input_event_manager.get_manager().last_event_was_line_navigation():
            return False

        if input_event_manager.get_manager().last_event_was_mouse_button():
            return False

        return True

    def elementLinesAreSingleWords(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return False

        if AXUtilities.is_code(obj):
            return False

        rv = self._elementLinesAreSingleWords.get(hash(obj))
        if rv is not None:
            return rv

        nChars = AXText.get_character_count(obj)
        if not nChars:
            return False

        if not self.treatAsTextObject(obj):
            return False

        # If we have a series of embedded object characters, there's a reasonable chance
        # they'll look like the one-word-per-line CSSified text we're trying to detect.
        # We don't want that false positive. By the same token, the one-word-per-line
        # CSSified text we're trying to detect can have embedded object characters. So
        # if we have more than 30% EOCs, don't use this workaround. (The 30% is based on
        # testing with problematic text.)
        string = AXText.get_all_text(obj)
        eocs = re.findall("\ufffc", string)
        if len(eocs)/nChars > 0.3:
            return False

        # TODO - JD: Can we remove this?
        AXObject.clear_cache(obj, False, "Checking if element lines are single words.")
        tokens = list(filter(lambda x: x, re.split(r"[\s\ufffc]", string)))

        # Note: We cannot check for the editable-text interface, because Gecko
        # seems to be exposing that for non-editable things. Thanks Gecko.
        rv = len(tokens) > 1 \
            and not (AXUtilities.is_editable(obj) or AXUtilities.is_text_input(obj))
        if rv:
            i = 0
            while i < nChars:
                string, start, end = AXText.get_line_at_offset(obj, i)
                if len(string.split()) != 1:
                    rv = False
                    break
                i = max(i+1, end)

        self._elementLinesAreSingleWords[hash(obj)] = rv
        return rv

    def elementLinesAreSingleChars(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return False

        rv = self._elementLinesAreSingleChars.get(hash(obj))
        if rv is not None:
            return rv

        nChars = AXText.get_character_count(obj)
        if not nChars:
            return False

        if not self.treatAsTextObject(obj):
            return False

        # If we have a series of embedded object characters, there's a reasonable chance
        # they'll look like the one-char-per-line CSSified text we're trying to detect.
        # We don't want that false positive. By the same token, the one-char-per-line
        # CSSified text we're trying to detect can have embedded object characters. So
        # if we have more than 30% EOCs, don't use this workaround. (The 30% is based on
        # testing with problematic text.)
        string = AXText.get_all_text(obj)
        eocs = re.findall("\ufffc", string)
        if len(eocs)/nChars > 0.3:
            return False

        # TODO - JD: Can we remove this?
        AXObject.clear_cache(obj, False, "Checking if element lines are single chars.")

        # Note: We cannot check for the editable-text interface, because Gecko
        # seems to be exposing that for non-editable things. Thanks Gecko.
        rv = not (AXUtilities.is_editable(obj) or AXUtilities.is_text_input(obj))
        if rv:
            for i in range(nChars):
                char = AXText.get_character_at_offset(obj, i)[0]
                if char.isspace() or char in ["\ufffc", "\ufffd"]:
                    continue

                string = AXText.get_line_at_offset(obj, i)[0]
                if len(string.strip()) > 1:
                    rv = False
                    break

        self._elementLinesAreSingleChars[hash(obj)] = rv
        return rv

    def labelIsAncestorOfLabelled(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return False

        rv = self._labelIsAncestorOfLabelled.get(hash(obj))
        if rv is not None:
            return rv

        rv = False
        for target in AXUtilities.get_is_label_for(obj):
            if AXObject.find_ancestor(target, lambda x: x == obj):
                rv = True
                break

        self._labelIsAncestorOfLabelled[hash(obj)] = rv
        return rv

    def isOffScreenLabel(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return False

        rv = self._isOffScreenLabel.get(hash(obj))
        if rv is not None:
            return rv

        if self.labelIsAncestorOfLabelled(obj):
            return False

        rv = False
        targets = AXUtilities.get_is_label_for(obj)
        if targets:
            end = max(1, AXText.get_character_count(obj))
            rect = AXText.get_range_rect(obj, 0, end)
            if rect.x < 0 or rect.y < 0:
                rv = True

        self._isOffScreenLabel[hash(obj)] = rv
        return rv

    def isDetachedDocument(self, obj):
        if AXUtilities.is_document(obj) and not AXObject.is_valid(AXObject.get_parent(obj)):
            tokens = ["WEB:", obj, "is a detached document"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        return False

    def iframeForDetachedDocument(self, obj, root=None):
        root = root or self.documentFrame()
        for iframe in AXUtilities.find_all_internal_frames(root):
            if AXObject.get_parent(obj) == iframe:
                tokens = ["WEB: Returning", iframe, "as iframe parent of detached", obj]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                return iframe

        return None

    def isLinkAncestorOfImageInContents(self, link, contents):
        if not self.isLink(link):
            return False

        for obj, start, end, string in contents:
            if not AXUtilities.is_image(obj):
                continue
            if AXObject.find_ancestor(obj, lambda x: x == link):
                return True

        return False

    def isInferredLabelForContents(self, content, contents):
        obj, start, end, string = content
        objs = list(filter(self.shouldInferLabelFor, [x[0] for x in contents]))
        if not objs:
            return None

        for o in objs:
            label, sources = self.inferLabelFor(o)
            if obj in sources and label.strip() == string.strip():
                return o

        return None

    def isLabellingInteractiveElement(self, obj):
        for target in AXUtilities.get_is_label_for(obj):
            if AXUtilities.is_focusable(target):
                return True

        return False

    def isLabellingContents(self, obj, contents=[]):
        if self.isFocusModeWidget(obj):
            return False

        targets = AXUtilities.get_is_label_for(obj)
        if not contents:
            if targets:
                return True
            return AXObject.find_ancestor(obj, AXUtilities.is_label_or_caption) is not None

        for acc, start, end, string in contents:
            if acc in targets:
                return True

        if not self.isTextBlockElement(obj):
            return False

        if AXObject.find_ancestor(obj, AXUtilities.is_label_or_caption) is None:
            return False

        for acc, start, end, string in contents:
            if AXObject.find_ancestor(acc, AXUtilities.is_label_or_caption) is None:
                continue
            if self.isTextBlockElement(acc):
                continue

            if AXUtilities.is_label_or_caption(AXObject.get_common_ancestor(acc, obj)):
                return True

        return False

    def isAnchor(self, obj):
        return AXUtilities.is_link(obj) and not AXUtilities.is_focusable(obj) \
           and not AXObject.has_action(obj, "jump") and not AXUtilities.has_role_from_aria(obj)

    def isEmptyAnchor(self, obj):
        return self.isAnchor(obj) and not self.treatAsTextObject(obj)

    def isEmptyToolTip(self, obj):
        return AXUtilities.is_tool_tip(obj) and not self.treatAsTextObject(obj)

    def isBrowserUIAlert(self, obj):
        if not AXUtilities.is_alert(obj):
            return False

        if self.inDocumentContent(obj):
            return False

        return True

    def isClickableElement(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return False

        rv = self._isClickableElement.get(hash(obj))
        if rv is not None:
            return rv

        if self.labelIsAncestorOfLabelled(obj):
            return False

        if self.hasGridDescendant(obj):
            tokens = ["WEB:", obj, "is not clickable: has grid descendant"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        rv = False
        if not self.isFocusModeWidget(obj):
            if not AXUtilities.is_focusable(obj):
                rv = AXObject.has_action(obj, "click")
            else:
                rv = AXObject.has_action(obj, "click-ancestor")

        if rv and not AXObject.get_name(obj) and AXObject.supports_text(obj):
            text = AXText.get_all_text(obj)
            if not text.replace("\ufffc", ""):
                tokens = ["WEB:", obj, "is not clickable: its text is just EOCs"]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                rv = False
            elif not text.strip():
                rv = not (AXUtilities.is_static(obj) or AXUtilities.is_link(obj))

        self._isClickableElement[hash(obj)] = rv
        return rv

    def isItemForEditableComboBox(self, item, comboBox):
        if not (AXUtilities.is_list_item(item) or AXUtilities.is_menu_item(item)):
            return False
        if not AXUtilities.is_editable_combo_box(comboBox):
            return False
        if AXObject.is_ancestor(item, comboBox):
            return True

        container = AXObject.find_ancestor(
            item, lambda x: AXUtilities.is_list_box(x) or AXUtilities.is_combo_box(x))
        targets = AXUtilities.get_is_controlled_by(container)
        return comboBox in targets

    def isFakePlaceholderForEntry(self, obj):
        if not (obj and self.inDocumentContent(obj) and AXObject.get_parent(obj)):
            return False

        if AXUtilities.is_editable(obj):
            return False

        entryName = AXObject.get_name(AXObject.find_ancestor(obj, AXUtilities.is_entry))
        if not entryName:
            return False

        def _isMatch(x):
            string = AXText.get_all_text(x).strip()
            if entryName != string:
                return False
            return AXUtilities.is_section(x) or AXUtilities.is_static(x)

        if _isMatch(obj):
            return True

        return AXObject.find_descendant(obj, _isMatch) is not None

    def isBlockListDescendant(self, obj):
        if AXObject.find_ancestor(obj, AXUtilities.is_list) is None:
            return False

        return AXObject.find_ancestor_inclusive(obj, AXUtilities.is_inline_list_item) is None

    def isLink(self, obj):
        if not obj:
            return False

        rv = self._isLink.get(hash(obj))
        if rv is not None:
            return rv

        if AXUtilities.is_link(obj) and not self.isAnchor(obj):
            rv = True
        elif AXUtilities.is_static(obj) \
           and AXUtilities.is_link(AXObject.get_parent(obj)) \
           and AXObject.has_same_non_empty_name(obj, AXObject.get_parent(obj)):
            rv = True
        else:
            rv = False

        self._isLink[hash(obj)] = rv
        return rv

    def hasUselessCanvasDescendant(self, obj):
        return len(AXUtilities.find_all_canvases(obj, self.isUselessImage)) > 0

    def isNonNavigableEmbeddedDocument(self, obj):
        rv = self._isNonNavigableEmbeddedDocument.get(hash(obj))
        if rv is not None:
            return rv

        rv = False
        if self.isDocument(obj) and self.getDocumentForObject(obj):
            try:
                name = AXObject.get_name(obj)
            except Exception:
                rv = True
            else:
                rv = "doubleclick" in name

        self._isNonNavigableEmbeddedDocument[hash(obj)] = rv
        return rv

    def isRedundantSVG(self, obj):
        if not AXUtilities.is_svg(obj) or AXObject.get_child_count(AXObject.get_parent(obj)) == 1:
            return False

        rv = self._isRedundantSVG.get(hash(obj))
        if rv is not None:
            return rv

        rv = False
        parent = AXObject.get_parent(obj)
        children = [x for x in AXObject.iter_children(parent, AXUtilities.is_svg)]
        if len(children) == AXObject.get_child_count(parent):
            sortedChildren = AXComponent.sort_objects_by_size(children)
            if obj != sortedChildren[-1]:
                objExtents = AXComponent.get_rect(obj)
                largestExtents = AXComponent.get_rect(sortedChildren[-1])
                intersection = AXComponent.get_rect_intersection(objExtents, largestExtents)
                rv = intersection == objExtents

        self._isRedundantSVG[hash(obj)] = rv
        return rv

    def isCustomImage(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return False

        rv = self._isCustomImage.get(hash(obj))
        if rv is not None:
            return rv

        rv = False
        if AXUtilities.is_web_element_custom(obj) and AXUtilities.has_explicit_name(obj) \
           and AXUtilities.is_section(obj) \
           and AXObject.supports_text(obj) \
           and not re.search(r'[^\s\ufffc]', AXText.get_all_text(obj)):
            for child in AXObject.iter_children(obj):
                if not (AXUtilities.is_image_or_canvas(child) or AXUtilities.is_svg(child)):
                    break
            else:
                rv = True

        self._isCustomImage[hash(obj)] = rv
        return rv

    def isUselessImage(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return False

        rv = self._isUselessImage.get(hash(obj))
        if rv is not None:
            return rv

        rv = True
        has_explicit_name = AXUtilities.has_explicit_name(obj)
        if not (AXUtilities.is_image_or_canvas(obj) or AXUtilities.is_svg(obj)):
            rv = False
        if rv and (AXObject.get_name(obj) \
                   or AXObject.get_description(obj) \
                   or self.hasLongDesc(obj)):
            rv = False
        if rv and self.isClickableElement(obj) and not has_explicit_name:
            rv = False
        if rv and AXUtilities.is_focusable(obj):
            rv = False
        if rv and AXUtilities.is_link(AXObject.get_parent(obj)) and not has_explicit_name:
            uri = AXHypertext.get_link_uri(AXObject.get_parent(obj))
            if uri and not uri.startswith('javascript'):
                rv = False
        if rv and AXObject.supports_image(obj):
            if AXObject.get_image_description(obj):
                rv = False
            elif not has_explicit_name and not self.isRedundantSVG(obj):
                width, height = AXObject.get_image_size(obj)
                if width > 25 and height > 25:
                    rv = False
        if rv and AXObject.supports_text(obj):
            rv = not self.treatAsTextObject(obj)
        if rv and AXObject.get_child_count(obj):
            for i in range(min(AXObject.get_child_count(obj), 50)):
                if not self.isUselessImage(AXObject.get_child(obj, i)):
                    rv = False
                    break

        self._isUselessImage[hash(obj)] = rv
        return rv

    def hasValidName(self, obj):
        name = AXObject.get_name(obj)
        if not name:
            return False

        if len(name.split()) > 1:
            return True

        parsed = urllib.parse.parse_qs(name)
        if len(parsed) > 2:
            tokens = ["WEB: name of", obj, "is suspected query string"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        if len(name) == 1 and ord(name) in range(0xe000, 0xf8ff):
            tokens = ["WEB: name of", obj, "is in unicode private use area"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        return True

    def isUselessEmptyElement(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return False

        rv = self._isUselessEmptyElement.get(hash(obj))
        if rv is not None:
            return rv

        roles = [Atspi.Role.PARAGRAPH,
                 Atspi.Role.SECTION,
                 Atspi.Role.STATIC,
                 Atspi.Role.TABLE_ROW]
        role = AXObject.get_role(obj)
        if role not in roles and not AXUtilities.is_aria_alert(obj):
            rv = False
        elif AXUtilities.is_focusable(obj):
            rv = False
        elif AXUtilities.is_editable(obj):
            rv = False
        elif self.hasValidName(obj) \
                or AXObject.get_description(obj) or AXObject.get_child_count(obj):
            rv = False
        elif AXText.get_character_count(obj) and AXText.get_all_text(obj) != AXObject.get_name(obj):
            rv = False
        elif AXObject.supports_action(obj):
            names = AXObject.get_action_names(obj)
            ignore = ["click-ancestor", "show-context-menu", "do-default"]
            names = list(filter(lambda x: x not in ignore, names))
            rv = not names
        else:
            rv = True

        self._isUselessEmptyElement[hash(obj)] = rv
        return rv

    def hasLongDesc(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return False

        rv = self._hasLongDesc.get(hash(obj))
        if rv is not None:
            return rv

        rv = AXObject.has_action(obj, "showlongdesc")
        self._hasLongDesc[hash(obj)] = rv
        return rv

    def inferLabelFor(self, obj):
        if not self.shouldInferLabelFor(obj):
            return None, []

        rv = self._inferredLabels.get(hash(obj))
        if rv is not None:
            return rv

        rv = self._script.label_inference.infer(obj, False)
        self._inferredLabels[hash(obj)] = rv
        return rv

    def shouldInferLabelFor(self, obj):
        if not self.inDocumentContent() or AXObject.find_ancestor(obj, AXUtilities.is_embedded):
            return False

        rv = self._shouldInferLabelFor.get(hash(obj))
        if rv and not self._script.caret_navigation.last_input_event_was_navigation_command():
            return not focus_manager.get_manager().in_say_all()
        if rv is False:
            return rv

        role = AXObject.get_role(obj)
        name = AXObject.get_name(obj)
        if name:
            rv = False
        elif AXUtilities.has_role_from_aria(obj):
            rv = False
        elif not rv:
            roles = [Atspi.Role.CHECK_BOX,
                     Atspi.Role.COMBO_BOX,
                     Atspi.Role.ENTRY,
                     Atspi.Role.LIST_BOX,
                     Atspi.Role.PASSWORD_TEXT,
                     Atspi.Role.RADIO_BUTTON]
            rv = role in roles and not AXUtilities.get_displayed_label(obj)

        self._shouldInferLabelFor[hash(obj)] = rv

        if self._script.caret_navigation.last_input_event_was_navigation_command() \
           and role not in [Atspi.Role.RADIO_BUTTON, Atspi.Role.CHECK_BOX]:
            return False

        return rv

    def isSpinnerEntry(self, obj):
        if not self.inDocumentContent(obj):
            return False

        if not AXUtilities.is_editable(obj):
            return False

        if AXUtilities.is_spin_button(obj) or AXUtilities.is_spin_button(AXObject.get_parent(obj)):
            return True

        return False

    def eventIsSpinnerNoise(self, event):
        if not self.isSpinnerEntry(event.source):
            return False

        return event.type.startswith("object:text-selection-changed") \
            and input_event_manager.get_manager().last_event_was_up_or_down()

    def treatEventAsSpinnerValueChange(self, event):
        if event.type.startswith("object:text-caret-moved") and self.isSpinnerEntry(event.source):
            if input_event_manager.get_manager().last_event_was_up_or_down():
                obj = self.getCaretContext()[0]
                return event.source == obj

        return False

    def eventIsBrowserUINoise(self, event):
        if self.inDocumentContent(event.source):
            return False

        if event.type.endswith("accessible-name"):
            return AXUtilities.is_status_bar(event.source) or AXUtilities.is_label(event.source) \
                or AXUtilities.is_frame(event.source)
        if event.type.startswith("object:children-changed"):
            return True

        return False

    def eventIsAutocompleteNoise(self, event, documentFrame=None):
        inContent = documentFrame or self.inDocumentContent(event.source)
        if not inContent:
            return False

        def isListBoxItem(x):
            return AXUtilities.is_list_box(AXObject.get_parent(x))

        def isMenuItem(x):
            return AXUtilities.is_menu(AXObject.get_parent(x))

        def isComboBoxItem(x):
            return AXUtilities.is_combo_box(AXObject.get_parent(x))

        if AXUtilities.is_editable(event.source) \
           and event.type.startswith("object:text-"):
            obj, offset = self.getCaretContext(documentFrame)
            if isListBoxItem(obj) or isMenuItem(obj):
                return True

            if obj == event.source and isComboBoxItem(obj) \
               and input_event_manager.get_manager().last_event_was_up_or_down():
                return True

        return False

    def eventIsBrowserUIAutocompleteNoise(self, event):
        if self.inDocumentContent(event.source):
            return False

        if self._eventIsBrowserUIAutocompleteTextNoise(event):
            return True

        return self._eventIsBrowserUIAutocompleteSelectionNoise(event)

    def _eventIsBrowserUIAutocompleteSelectionNoise(self, event):
        selection = ["object:selection-changed", "object:state-changed:selected"]
        if event.type not in selection:
            return False

        if not AXUtilities.is_menu_related(event.source):
            return False

        focus = focus_manager.get_manager().get_locus_of_focus()
        if AXUtilities.is_entry(focus) and AXUtilities.is_focused(focus):
            if not input_event_manager.get_manager().last_event_was_up_or_down():
                return True

        return False

    def _eventIsBrowserUIAutocompleteTextNoise(self, event):
        if not event.type.startswith("object:text-") \
           or not AXUtilities.is_single_line_autocomplete_entry(event.source):
            return False

        focus = focus_manager.get_manager().get_locus_of_focus()
        if not AXUtilities.is_selectable(focus):
            return False

        if AXUtilities.is_menu_item_of_any_kind(focus) or AXUtilities.is_list_item(focus):
            return input_event_manager.get_manager().last_event_was_up_or_down()

        return False

    def eventIsBrowserUIPageSwitch(self, event):
        selection = ["object:selection-changed", "object:state-changed:selected"]
        if event.type not in selection:
            return False

        if not AXUtilities.is_page_tab_list_related(event.source):
            return False

        if self.inDocumentContent(event.source):
            return False

        if not self.inDocumentContent(focus_manager.get_manager().get_locus_of_focus()):
            return False

        return True

    def eventIsFromLocusOfFocusDocument(self, event):
        if focus_manager.get_manager().focus_is_active_window():
            focus = self.activeDocument()
            source = self.getTopLevelDocumentForObject(event.source)
        else:
            focus = self.getDocumentForObject(focus_manager.get_manager().get_locus_of_focus())
            source = self.getDocumentForObject(event.source)

        tokens = ["WEB: Event doc:", source, ". Focus doc:", focus, "."]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if not (source and focus):
            return False

        if source == focus:
            return True

        if not AXObject.is_valid(focus) and AXObject.is_valid(source):
            if self.activeDocument() == source:
                msg = "WEB: Treating active doc as locusOfFocus doc"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return True

        return False

    def eventIsIrrelevantSelectionChangedEvent(self, event):
        if event.type != "object:selection-changed":
            return False

        focus = focus_manager.get_manager().get_locus_of_focus()
        if not focus:
            msg = "WEB: Selection changed event is relevant (no locusOfFocus)"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False
        if event.source == focus:
            msg = "WEB: Selection changed event is relevant (is locusOfFocus)"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False
        if AXObject.find_ancestor(focus, lambda x: x == event.source):
            msg = "WEB: Selection changed event is relevant (ancestor of locusOfFocus)"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        # There may be other roles where we need to do this. For now, solve the known one.
        if AXUtilities.is_page_tab_list(event.source):
            tokens = ["WEB: Selection changed event is irrelevant (unrelated",
                      AXObject.get_role_name(event.source), ")"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        msg = "WEB: Selection changed event is relevant (no reason found to ignore it)"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return False

    def textEventIsForNonNavigableTextObject(self, event):
        if not event.type.startswith("object:text-"):
            return False

        return self._treatObjectAsWhole(event.source)

    def caretMovedOutsideActiveGrid(self, event, old_focus=None):
        if not (event and event.type.startswith("object:text-caret-moved")):
            return False

        old_focus = old_focus or focus_manager.get_manager().get_locus_of_focus()
        if AXObject.find_ancestor(old_focus, AXUtilities.is_grid) is None:
            return False

        return AXObject.find_ancestor(event.source, AXUtilities.is_grid) is None

    def caretMovedToSamePageFragment(self, event, old_focus=None):
        if not (event and event.type.startswith("object:text-caret-moved")):
            return False

        if AXUtilities.is_editable(event.source):
            return False

        fragment = AXDocument.get_document_uri_fragment(self.documentFrame())
        if not fragment:
            return False

        sourceID = AXObject.get_attribute(event.source, "id")
        if sourceID and fragment == sourceID:
            return True

        old_focus = old_focus or focus_manager.get_manager().get_locus_of_focus()
        if self.isLink(old_focus):
            link = old_focus
        else:
            link = AXObject.find_ancestor(old_focus, self.isLink)

        return link and AXHypertext.get_link_uri(link) == AXDocument.get_uri(self.documentFrame())

    def isChildOfCurrentFragment(self, obj):
        fragment = AXDocument.get_document_uri_fragment(self.documentFrame(obj))
        if not fragment:
            return False

        def isSameFragment(x):
            return AXObject.get_attribute(x, "id") == fragment

        return AXObject.find_ancestor(obj, isSameFragment) is not None

    def isContentEditableWithEmbeddedObjects(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return False

        rv = self._isContentEditableWithEmbeddedObjects.get(hash(obj))
        if rv is not None:
            return rv

        rv = False
        def hasTextBlockRole(x):
            return AXObject.get_role(x) in self._textBlockElementRoles() \
                and not self.isFakePlaceholderForEntry(x) and AXUtilities.is_web_element(x)

        if AXUtilities.is_text_input(obj):
            rv = False
        elif AXUtilities.is_multi_line_entry(obj):
            rv = AXObject.find_descendant(obj, hasTextBlockRole)
        elif AXUtilities.is_editable(obj):
            rv = hasTextBlockRole(obj) or self.isLink(obj)
        elif not self.isDocument(obj):
            document = self.getDocumentForObject(obj)
            rv = self.isContentEditableWithEmbeddedObjects(document)

        self._isContentEditableWithEmbeddedObjects[hash(obj)] = rv
        return rv

    def _rangeInParentWithLength(self, obj):
        parent = AXObject.get_parent(obj)
        if not self.treatAsTextObject(parent):
            return -1, -1, 0

        start = AXHypertext.get_link_start_offset(obj)
        end = AXHypertext.get_link_end_offset(obj)
        return start, end, AXText.get_character_count(parent)

    def _canHaveCaretContext(self, obj):
        rv = self._canHaveCaretContextDecision.get(hash(obj))
        if rv is not None:
            return rv

        if obj is None:
            return False
        if AXObject.is_dead(obj):
            msg = "WEB: Dead object cannot have caret context"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False
        if not AXObject.is_valid(obj):
            tokens = ["WEB: Invalid object cannot have caret context", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False
        if not AXUtilities.is_web_element(obj):
            tokens = ["WEB: Non-element cannot have caret context", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        start_time = time.time()
        rv = None
        if AXUtilities.is_focusable(obj):
            tokens = ["WEB: Focusable object can have caret context", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            rv = True
        elif AXUtilities.is_editable(obj):
            tokens = ["WEB: Editable object can have caret context", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            rv = True
        elif AXUtilities.is_landmark(obj):
            tokens = ["WEB: Landmark can have caret context", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            rv = True
        elif AXUtilities.is_tool_tip(obj):
            tokens = ["WEB: Non-focusable tooltip cannot have caret context", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            rv = False
        elif self.isUselessEmptyElement(obj):
            tokens = ["WEB: Useless empty element cannot have caret context", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            rv = False
        elif self.isOffScreenLabel(obj):
            tokens = ["WEB: Off-screen label cannot have caret context", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            rv = False
        elif self.isUselessImage(obj):
            tokens = ["WEB: Useless image cannot have caret context", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            rv = False
        elif self.isEmptyAnchor(obj):
            tokens = ["WEB: Empty anchor cannot have caret context", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            rv = False
        elif self.isEmptyToolTip(obj):
            tokens = ["WEB: Empty tool tip cannot have caret context", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            rv = False
        elif self.isFakePlaceholderForEntry(obj):
            tokens = ["WEB: Fake placeholder for entry cannot have caret context", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            rv = False
        elif AXObject.find_ancestor(obj, AXUtilities.children_are_presentational):
            tokens = ["WEB: Presentational child cannot have caret context", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            rv = False
        elif AXUtilities.is_hidden(obj):
            # We try to do this check only if needed because getting object attributes is
            # not as performant, and we cannot use the cached attribute because aria-hidden
            # can change frequently depending on the app.
            tokens = ["WEB: Hidden object cannot have caret context", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            rv = False
        elif AXComponent.has_no_size(obj):
            tokens = ["WEB: Allowing sizeless object to have caret context", obj]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            rv = True
        else:
            tokens = ["WEB: ", obj, f"can have caret context. ({time.time() - start_time:.4f}s)"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            rv = True

        self._canHaveCaretContextDecision[hash(obj)] = rv
        msg = f"INFO: _canHaveCaretContext took {time.time() - start_time:.4f}s"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return rv

    def searchForCaretContext(self, obj):
        tokens = ["WEB: Searching for caret context in", obj]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        container = obj
        contextObj, contextOffset = None, -1
        while obj:
            offset = AXText.get_caret_offset(obj)
            if offset < 0:
                obj = None
            else:
                contextObj, contextOffset = obj, offset
                child = AXHypertext.get_child_at_offset(obj, offset)
                if child:
                    obj = child
                else:
                    break

        if contextObj and not AXUtilities.is_hidden(contextObj):
            return self.findNextCaretInOrder(contextObj, max(-1, contextOffset - 1))

        if self.isDocument(container):
            return container, 0

        return None, -1

    def _getCaretContextViaLocusOfFocus(self):
        obj = focus_manager.get_manager().get_locus_of_focus()
        msg = "WEB: Getting caret context via locusOfFocus"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        if not self.inDocumentContent(obj):
            return None, -1

        if not AXObject.supports_text(obj):
            return obj, 0

        return obj, AXText.get_caret_offset(obj)

    def getCaretContext(self, documentFrame=None, getReplicant=False, searchIfNeeded=True):
        tokens = ["WEB: Getting caret context for", documentFrame]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if not AXObject.is_valid(documentFrame):
            documentFrame = self.documentFrame()
            tokens = ["WEB: Now getting caret context for", documentFrame]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if not documentFrame:
            if not searchIfNeeded:
                msg = "WEB: Returning None, -1: No document and no search requested."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return None, -1

            obj, offset = self._getCaretContextViaLocusOfFocus()
            tokens = ["WEB: Returning", obj, ", ", offset, "(from locusOfFocus)"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return obj, offset

        context = self._caretContexts.get(hash(AXObject.get_parent(documentFrame)))
        if context is not None:
            tokens = ["WEB: Cached context of", documentFrame, "is", context[0], ", ", context[1]]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        else:
            tokens = ["WEB: No cached context for", documentFrame, "."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            obj, offset = None, -1

        if not context or not self.isTopLevelDocument(documentFrame):
            if not searchIfNeeded:
                msg = "WEB: Returning None, -1: No top-level document with context " \
                      "and no search requested."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return None, -1
            obj, offset = self.searchForCaretContext(documentFrame)
        elif not getReplicant:
            obj, offset = context
        elif not AXObject.is_valid(context[0]):
            msg = "WEB: Context is not valid. Searching for replicant."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            obj, offset = self.findContextReplicant()
            if obj:
                caretObj, caretOffset = self.searchForCaretContext(AXObject.get_parent(obj))
                if caretObj and AXObject.is_valid(caretObj):
                    obj, offset = caretObj, caretOffset
        else:
            obj, offset = context

        tokens = ["WEB: Result context of", documentFrame, "is", obj, ", ", offset, "."]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        self.setCaretContext(obj, offset, documentFrame)
        return obj, offset

    def getCaretContextPathRoleAndName(self, documentFrame=None):
        documentFrame = documentFrame or self.documentFrame()
        if not documentFrame:
            return [-1], None, None

        rv = self._contextPathsRolesAndNames.get(hash(AXObject.get_parent(documentFrame)))
        if not rv:
            return [-1], None, None

        return rv

    def clearCaretContext(self, documentFrame=None):
        self.clearContentCache()
        documentFrame = documentFrame or self.documentFrame()
        if not documentFrame:
            return

        parent = AXObject.get_parent(documentFrame)
        self._caretContexts.pop(hash(parent), None)
        self._priorContexts.pop(hash(parent), None)

    def handleEventFromContextReplicant(self, event, replicant):
        if AXObject.is_dead(replicant):
            msg = "WEB: Context replicant is dead."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if not focus_manager.get_manager().focus_is_dead():
            msg = "WEB: Not event from context replicant, locus of focus is not dead."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        path, role, name = self.getCaretContextPathRoleAndName()
        replicantPath = AXObject.get_path(replicant)
        if path != replicantPath:
            tokens = ["WEB: Not event from context replicant. Path", path,
                      " != replicant path", replicantPath]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        replicantRole = AXObject.get_role(replicant)
        if role != replicantRole:
            tokens = ["WEB: Not event from context replicant. Role", role,
                      " != replicant role", replicantRole]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        notify = AXObject.get_name(replicant) != name
        documentFrame = self.documentFrame()
        obj, offset = self._caretContexts.get(hash(AXObject.get_parent(documentFrame)))

        tokens = ["WEB: Is event from context replicant. Notify:", notify]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        focus_manager.get_manager().set_locus_of_focus(event, replicant, notify)
        self.setCaretContext(replicant, offset, documentFrame)
        return True

    def _handleEventForRemovedSelectableChild(self, event):
        container = None
        if AXUtilities.is_list_box(event.source):
            container = event.source
        elif AXUtilities.is_tree(event.source):
            container = event.source
        else:
            container = AXObject.find_ancestor(event.source, AXUtilities.is_list_box) \
                or AXObject.find_ancestor(event.source, AXUtilities.is_tree)
        if container is None:
            msg = "WEB: Could not find listbox or tree to recover from removed child."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        tokens = ["WEB: Checking", container, "for focused child."]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        # TODO - JD: Can we remove this? If it's needed, should it be recursive?
        AXObject.clear_cache(container, False, "Handling event for removed selectable child.")
        item = AXUtilities.get_focused_object(container)
        if not (AXUtilities.is_list_item(item) or AXUtilities.is_tree_item):
            msg = "WEB: Could not find focused item to recover from removed child."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        names = self._script.point_of_reference.get('names', {})
        oldName = names.get(hash(focus_manager.get_manager().get_locus_of_focus()))
        notify = AXObject.get_name(item) != oldName

        tokens = ["WEB: Recovered from removed child. New focus is: ", item, "0"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        focus_manager.get_manager().set_locus_of_focus(event, item, notify)
        self.setCaretContext(item, 0)
        return True

    def handleEventForRemovedChild(self, event):
        focus = focus_manager.get_manager().get_locus_of_focus()
        if event.any_data == focus:
            msg = "WEB: Removed child is locus of focus."
            debug.print_message(debug.LEVEL_INFO, msg, True)
        elif AXObject.find_ancestor(focus, lambda x: x == event.any_data):
            msg = "WEB: Removed child is ancestor of locus of focus."
            debug.print_message(debug.LEVEL_INFO, msg, True)
        else:
            msg = "WEB: Removed child is not locus of focus nor ancestor of locus of focus."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if event.detail1 == -1:
            msg = "WEB: Event detail1 is useless."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        if self._handleEventForRemovedSelectableChild(event):
            return True

        obj, offset = None, -1
        notify = True
        childCount = AXObject.get_child_count(event.source)
        if input_event_manager.get_manager().last_event_was_up():
            if event.detail1 >= childCount:
                msg = "WEB: Last child removed. Getting new location from end of parent."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                obj, offset = self.previousContext(event.source, -1)
            elif 0 <= event.detail1 - 1 < childCount:
                child = AXObject.get_child(event.source, event.detail1 - 1)
                tokens = ["WEB: Getting new location from end of previous child", child, "."]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                obj, offset = self.previousContext(child, -1)
            else:
                prevObj = self.findPreviousObject(event.source)
                tokens = ["WEB: Getting new location from end of source's previous object",
                          prevObj, "."]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                obj, offset = self.previousContext(prevObj, -1)

        elif input_event_manager.get_manager().last_event_was_down():
            if event.detail1 == 0:
                msg = "WEB: First child removed. Getting new location from start of parent."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                obj, offset = self.nextContext(event.source, -1)
            elif 0 < event.detail1 < childCount:
                child = AXObject.get_child(event.source, event.detail1)
                tokens = ["WEB: Getting new location from start of child", event.detail1,
                          child, "."]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                obj, offset = self.nextContext(child, -1)
            else:
                nextObj = self.findNextObject(event.source)
                tokens = ["WEB: Getting new location from start of source's next object",
                          nextObj, "."]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                obj, offset = self.nextContext(nextObj, -1)

        else:
            notify = False
            # TODO - JD: Can we remove this? Even if it is needed, we now also clear the
            # cache in _handleEventForRemovedSelectableChild. Also, if it is needed, should
            # it be recursive?
            AXObject.clear_cache(event.source, False, "Handling event for removed child.")
            obj, offset = self.searchForCaretContext(event.source)
            if obj is None:
                obj = AXUtilities.get_focused_object(event.source)

            # Risk "chattiness" if the locusOfFocus is dead and the object we've found is
            # focused and has a different name than the last known focused object.
            if obj and focus_manager.get_manager().focus_is_dead() and AXUtilities.is_focused(obj):
                names = self._script.point_of_reference.get('names', {})
                oldName = names.get(hash(focus_manager.get_manager().get_locus_of_focus()))
                notify = AXObject.get_name(obj) != oldName

        if obj:
            msg = "WEB: Setting locusOfFocus and context to: %s, %i" % (obj, offset)
            focus_manager.get_manager().set_locus_of_focus(event, obj, notify)
            self.setCaretContext(obj, offset)
            return True

        tokens = ["WEB: Unable to find context for child removed from", event.source]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return False

    def findContextReplicant(self, documentFrame=None, matchRole=True, matchName=True):
        path, oldRole, oldName = self.getCaretContextPathRoleAndName(documentFrame)
        obj = self.getObjectFromPath(path)
        if obj and matchRole:
            if AXObject.get_role(obj) != oldRole:
                obj = None
        if obj and matchName:
            if AXObject.get_name(obj) != oldName:
                obj = None
        if not obj:
            return None, -1

        obj, offset = self.findFirstCaretContext(obj, 0)
        tokens = ["WEB: Context replicant is", obj, ", ", offset]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return obj, offset

    def getPriorContext(self, documentFrame=None):
        if not AXObject.is_valid(documentFrame):
            documentFrame = self.documentFrame()

        if documentFrame:
            context = self._priorContexts.get(hash(AXObject.get_parent(documentFrame)))
            if context:
                return context

        return None, -1

    def _getPath(self, obj):
        rv = self._paths.get(hash(obj))
        if rv is not None:
            return rv

        rv = AXObject.get_path(obj) or [-1]
        self._paths[hash(obj)] = rv
        return rv

    def setCaretContext(self, obj=None, offset=-1, documentFrame=None):
        documentFrame = documentFrame or self.documentFrame()
        if not documentFrame:
            return

        parent = AXObject.get_parent(documentFrame)
        oldObj, oldOffset = self._caretContexts.get(hash(parent), (obj, offset))
        self._priorContexts[hash(parent)] = oldObj, oldOffset
        self._caretContexts[hash(parent)] = obj, offset

        path = self._getPath(obj)
        role = AXObject.get_role(obj)
        name = AXObject.get_name(obj)
        self._contextPathsRolesAndNames[hash(parent)] = path, role, name

    def findFirstCaretContext(self, obj, offset):
        self._canHaveCaretContextDecision = {}
        rv = self._findFirstCaretContext(obj, offset)
        self._canHaveCaretContextDecision = {}
        return rv

    def _findFirstCaretContext(self, obj, offset):
        tokens = ["WEB: Looking for first caret context for", obj, ", ", offset]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        role = AXObject.get_role(obj)
        lookInChild = [Atspi.Role.LIST,
                       Atspi.Role.INTERNAL_FRAME,
                       Atspi.Role.TABLE,
                       Atspi.Role.TABLE_ROW]
        if role in lookInChild \
           and AXObject.get_child_count(obj) and not self.treatAsDiv(obj, offset):
            firstChild = AXObject.get_child(obj, 0)
            tokens = ["WEB: Will look in child", firstChild, "for first caret context"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return self._findFirstCaretContext(firstChild, 0)

        treatAsText = self.treatAsTextObject(obj)
        if not treatAsText and self._canHaveCaretContext(obj):
            tokens = ["WEB: First caret context for non-text context is", obj, "0"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return obj, 0

        length = AXText.get_character_count(obj)
        if treatAsText and offset >= length:
            if self.isContentEditableWithEmbeddedObjects(obj) \
               and input_event_manager.get_manager().last_event_was_character_navigation():
                nextObj, nextOffset = self.nextContext(obj, length)
                if not nextObj:
                    tokens = ["WEB: No next object found at end of contenteditable", obj]
                    debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                elif not self.isContentEditableWithEmbeddedObjects(nextObj):
                    tokens = ["WEB: Next object", nextObj,
                              "found at end of contenteditable", obj, "is not editable"]
                    debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                else:
                    tokens = ["WEB: First caret context at end of contenteditable", obj,
                              "is next context", nextObj, ", ", nextOffset]
                    debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                    return nextObj, nextOffset

            tokens = ["WEB: First caret context at end of", obj, ", ", offset, "is",
                      obj, ", ", length]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return obj, length

        offset = max(0, offset)
        if treatAsText:
            allText = AXText.get_all_text(obj)
            if (allText and allText[offset] != self.EMBEDDED_OBJECT_CHARACTER) \
               or role == Atspi.Role.ENTRY:
                msg = "WEB: First caret context is unchanged"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return obj, offset

            # Descending an element that we're treating as whole can lead to looping/getting stuck.
            if self.elementLinesAreSingleChars(obj):
                msg = "WEB: EOC in single-char-lines element. Returning context unchanged."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                return obj, offset

        child = AXHypertext.get_child_at_offset(obj, offset)
        if not child:
            msg = "WEB: Child at offset is null. Returning context unchanged."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return obj, offset

        if self.isDocument(obj):
            while self.isUselessEmptyElement(child):
                tokens = ["WEB: Child", child, "of", obj, "at offset", offset, "cannot be context."]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                offset += 1
                child = AXHypertext.get_child_at_offset(obj, offset)

        if self.isEmptyAnchor(child):
            nextObj, nextOffset = self.nextContext(obj, offset)
            if nextObj:
                tokens = ["WEB: First caret context at end of empty anchor", obj,
                          "is next context", nextObj, ", ", nextOffset]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                return nextObj, nextOffset

        if not self._canHaveCaretContext(child):
            tokens = ["WEB: Child", child, "cannot be context. Returning", obj, ", ", offset]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return obj, offset

        tokens = ["WEB: Looking in child", child, "for first caret context for", obj, ", ", offset]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return self._findFirstCaretContext(child, 0)

    def findNextCaretInOrder(self, obj=None, offset=-1):
        start_time = time.time()
        rv = self._findNextCaretInOrder(obj, offset)
        tokens = ["WEB: Next caret in order for", obj, ", ", offset, ":",
                  rv[0], ", ", rv[1], f"({time.time() - start_time:.4f}s)"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return rv

    def _findNextCaretInOrder(self, obj=None, offset=-1):
        if not obj:
            obj, offset = self.getCaretContext()

        if not obj or not self.inDocumentContent(obj):
            return None, -1

        if self._canHaveCaretContext(obj):
            if self.treatAsTextObject(obj) and AXText.get_character_count(obj):
                allText = AXText.get_all_text(obj)
                for i in range(offset + 1, len(allText)):
                    child = AXHypertext.get_child_at_offset(obj, i)
                    if child and allText[i] != self.EMBEDDED_OBJECT_CHARACTER:
                        tokens = ["ERROR: Child", child, "found at offset with char '",
                                  allText[i].replace("\n", "\\n"), "'"]
                        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                    if self._canHaveCaretContext(child):
                        if self._treatObjectAsWhole(child, -1):
                            return child, 0
                        return self._findNextCaretInOrder(child, -1)
                    if allText[i] not in (
                            self.EMBEDDED_OBJECT_CHARACTER, self.ZERO_WIDTH_NO_BREAK_SPACE):
                        return obj, i
            elif AXObject.get_child_count(obj) and not self._treatObjectAsWhole(obj, offset):
                return self._findNextCaretInOrder(AXObject.get_child(obj, 0), -1)
            elif offset < 0 and not self.isTextBlockElement(obj):
                return obj, 0

        # If we're here, start looking up the tree, up to the document.
        if self.isTopLevelDocument(obj):
            return None, -1

        while obj and (parent := AXObject.get_parent(obj)):
            if self.isDetachedDocument(parent):
                obj = self.iframeForDetachedDocument(parent)
                continue

            if not AXObject.is_valid(parent):
                msg = "WEB: Finding next caret in order. Parent is not valid."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                if AXObject.get_parent(parent):
                    obj = parent
                    continue
                else:
                    break

            start, end, length = self._rangeInParentWithLength(obj)
            if start + 1 == end and 0 <= start < end <= length:
                return self._findNextCaretInOrder(parent, start)

            child = AXObject.get_next_sibling(obj)
            if child:
                return self._findNextCaretInOrder(child, -1)
            obj = parent

        return None, -1

    def findPreviousCaretInOrder(self, obj=None, offset=-1):
        start_time = time.time()
        rv = self._findPreviousCaretInOrder(obj, offset)
        tokens = ["WEB: Previous caret in order for", obj, ", ", offset, ":",
                  rv[0], ", ", rv[1], f"({time.time() - start_time:.4f}s)"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return rv

    def _findPreviousCaretInOrder(self, obj=None, offset=-1):
        if not obj:
            obj, offset = self.getCaretContext()

        if not obj or not self.inDocumentContent(obj):
            return None, -1

        if self._canHaveCaretContext(obj):
            if self.treatAsTextObject(obj) and AXText.get_character_count(obj):
                allText = AXText.get_all_text(obj)
                if offset == -1 or offset > len(allText):
                    offset = len(allText)
                for i in range(offset - 1, -1, -1):
                    child = AXHypertext.get_child_at_offset(obj, i)
                    if child and allText[i] != self.EMBEDDED_OBJECT_CHARACTER:
                        tokens = ["ERROR: Child", child, "found at offset with char '",
                                  allText[i].replace("\n", "\\n"), "'"]
                        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                    if self._canHaveCaretContext(child):
                        if self._treatObjectAsWhole(child, -1):
                            return child, 0
                        return self._findPreviousCaretInOrder(child, -1)
                    if allText[i] not in (
                            self.EMBEDDED_OBJECT_CHARACTER, self.ZERO_WIDTH_NO_BREAK_SPACE):
                        return obj, i
            elif AXObject.get_child_count(obj) and not self._treatObjectAsWhole(obj, offset):
                return self._findPreviousCaretInOrder(
                    AXObject.get_child(obj, AXObject.get_child_count(obj) - 1), -1)
            elif offset < 0 and not self.isTextBlockElement(obj):
                return obj, 0

        # If we're here, start looking up the tree, up to the document.
        if self.isTopLevelDocument(obj):
            return None, -1

        while obj and (parent := AXObject.get_parent(obj)):
            if self.isDetachedDocument(parent):
                obj = self.iframeForDetachedDocument(parent)
                continue

            if not AXObject.is_valid(parent):
                msg = "WEB: Finding previous caret in order. Parent is not valid."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                if AXObject.get_parent(parent):
                    obj = parent
                    continue
                else:
                    break

            start, end, length = self._rangeInParentWithLength(obj)
            if start + 1 == end and 0 <= start < end <= length:
                return self._findPreviousCaretInOrder(parent, start)

            child = AXObject.get_previous_sibling(obj)
            if child:
                return self._findPreviousCaretInOrder(child, -1)
            obj = parent

        return None, -1

    def handleAsLiveRegion(self, event):
        if not settings_manager.get_manager().get_setting('inferLiveRegions'):
            return False

        if not AXUtilities.is_live_region(event.source):
            return False

        if not settings_manager.get_manager().get_setting('presentLiveRegionFromInactiveTab') \
           and self.getTopLevelDocumentForObject(event.source) != self.activeDocument():
            msg = "WEB: Live region source is not in active tab."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        alert = AXObject.find_ancestor(event.source, AXUtilities.is_aria_alert)
        if alert and AXUtilities.get_focused_object(alert) == event.source:
            msg = "WEB: Focused source will be presented as part of alert"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        return True
