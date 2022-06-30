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

import functools
import pyatspi
import re
import time
import urllib

from orca import debug
from orca import input_event
from orca import messages
from orca import mouse_review
from orca import orca
from orca import orca_state
from orca import script_utilities
from orca import script_manager
from orca import settings
from orca import settings_manager

_scriptManager = script_manager.getManager()
_settingsManager = settings_manager.getManager()


class Utilities(script_utilities.Utilities):

    def __init__(self, script):
        super().__init__(script)

        self._objectAttributes = {}
        self._currentTextAttrs = {}
        self._caretContexts = {}
        self._priorContexts = {}
        self._canHaveCaretContextDecision = {}
        self._contextPathsRolesAndNames = {}
        self._paths = {}
        self._inDocumentContent = {}
        self._inTopLevelWebApp = {}
        self._isTextBlockElement = {}
        self._isContentEditableWithEmbeddedObjects = {}
        self._isCodeDescendant = {}
        self._isEntryDescendant = {}
        self._isGridDescendant = {}
        self._isLabelDescendant = {}
        self._isMenuDescendant = {}
        self._isNavigableToolTipDescendant = {}
        self._isToolBarDescendant = {}
        self._isWebAppDescendant = {}
        self._isLayoutOnly = {}
        self._isFocusableWithMathChild = {}
        self._mathNestingLevel = {}
        self._isOffScreenLabel = {}
        self._labelIsAncestorOfLabelled = {}
        self._elementLinesAreSingleChars= {}
        self._elementLinesAreSingleWords= {}
        self._hasNoSize = {}
        self._hasLongDesc = {}
        self._hasVisibleCaption = {}
        self._hasDetails = {}
        self._isDetails = {}
        self._isNonInteractiveDescendantOfControl = {}
        self._hasUselessCanvasDescendant = {}
        self._isClickableElement = {}
        self._isAnchor = {}
        self._isEditableComboBox = {}
        self._isErrorMessage = {}
        self._isInlineIframeDescendant = {}
        self._isInlineListItem = {}
        self._isInlineListDescendant = {}
        self._isLandmark = {}
        self._isLink = {}
        self._isListDescendant = {}
        self._isNonNavigablePopup = {}
        self._isNonEntryTextWidget = {}
        self._isCustomImage = {}
        self._isUselessImage = {}
        self._isRedundantSVG = {}
        self._isUselessEmptyElement = {}
        self._hasNameAndActionAndNoUsefulChildren = {}
        self._isNonNavigableEmbeddedDocument = {}
        self._isParentOfNullChild = {}
        self._inferredLabels = {}
        self._labelsForObject = {}
        self._labelTargets = {}
        self._displayedLabelText = {}
        self._mimeType = {}
        self._preferDescriptionOverName = {}
        self._shouldFilter = {}
        self._shouldInferLabelFor = {}
        self._treatAsTextObject = {}
        self._treatAsDiv = {}
        self._currentObjectContents = None
        self._currentSentenceContents = None
        self._currentLineContents = None
        self._currentWordContents = None
        self._currentCharacterContents = None
        self._lastQueuedLiveRegionEvent = None
        self._findContainer = None
        self._statusBar = None
        self._validChildRoles = {pyatspi.ROLE_LIST: [pyatspi.ROLE_LIST_ITEM]}

    def _cleanupContexts(self):
        toRemove = []
        for key, [obj, offset] in self._caretContexts.items():
            if self.isZombie(obj):
                toRemove.append(key)

        for key in toRemove:
            self._caretContexts.pop(key, None)

    def dumpCache(self, documentFrame=None, preserveContext=False):
        if not documentFrame or self.isZombie(documentFrame):
            documentFrame = self.documentFrame()

        context = self._caretContexts.get(hash(documentFrame.parent))

        msg = "WEB: Clearing all cached info for %s" % documentFrame
        debug.println(debug.LEVEL_INFO, msg, True)

        self._script.structuralNavigation.clearCache(documentFrame)
        self.clearCaretContext(documentFrame)
        self.clearCachedObjects()

        if preserveContext and context:
            msg = "WEB: Preserving context of %s, %i" % (context[0], context[1])
            debug.println(debug.LEVEL_INFO, msg, True)
            self._caretContexts[hash(documentFrame.parent)] = context

    def clearCachedObjects(self):
        debug.println(debug.LEVEL_INFO, "WEB: cleaning up cached objects", True)
        self._objectAttributes = {}
        self._inDocumentContent = {}
        self._inTopLevelWebApp = {}
        self._isTextBlockElement = {}
        self._isContentEditableWithEmbeddedObjects = {}
        self._isCodeDescendant = {}
        self._isEntryDescendant = {}
        self._isGridDescendant = {}
        self._isLabelDescendant = {}
        self._isMenuDescendant = {}
        self._isNavigableToolTipDescendant = {}
        self._isToolBarDescendant = {}
        self._isWebAppDescendant = {}
        self._isLayoutOnly = {}
        self._isFocusableWithMathChild = {}
        self._mathNestingLevel = {}
        self._isOffScreenLabel = {}
        self._labelIsAncestorOfLabelled = {}
        self._elementLinesAreSingleChars= {}
        self._elementLinesAreSingleWords= {}
        self._hasNoSize = {}
        self._hasLongDesc = {}
        self._hasVisibleCaption = {}
        self._hasDetails = {}
        self._isDetails = {}
        self._hasUselessCanvasDescendant = {}
        self._isNonInteractiveDescendantOfControl = {}
        self._isClickableElement = {}
        self._isAnchor = {}
        self._isEditableComboBox = {}
        self._isErrorMessage = {}
        self._isInlineIframeDescendant = {}
        self._isInlineListItem = {}
        self._isInlineListDescendant = {}
        self._isLandmark = {}
        self._isLink = {}
        self._isListDescendant = {}
        self._isNonNavigablePopup = {}
        self._isNonEntryTextWidget = {}
        self._isCustomImage = {}
        self._isUselessImage = {}
        self._isRedundantSVG = {}
        self._isUselessEmptyElement = {}
        self._hasNameAndActionAndNoUsefulChildren = {}
        self._isNonNavigableEmbeddedDocument = {}
        self._isParentOfNullChild = {}
        self._inferredLabels = {}
        self._labelsForObject = {}
        self._labelTargets = {}
        self._displayedLabelText = {}
        self._mimeType = {}
        self._preferDescriptionOverName = {}
        self._shouldFilter = {}
        self._shouldInferLabelFor = {}
        self._treatAsTextObject = {}
        self._treatAsDiv = {}
        self._paths = {}
        self._contextPathsRolesAndNames = {}
        self._canHaveCaretContextDecision = {}
        self._cleanupContexts()
        self._priorContexts = {}
        self._lastQueuedLiveRegionEvent = None
        self._findContainer = None
        self._statusBar = None

    def clearContentCache(self):
        self._currentObjectContents = None
        self._currentSentenceContents = None
        self._currentLineContents = None
        self._currentWordContents = None
        self._currentCharacterContents = None
        self._currentTextAttrs = {}

    def isDocument(self, obj):
        if not obj:
            return False

        roles = [pyatspi.ROLE_DOCUMENT_FRAME, pyatspi.ROLE_DOCUMENT_WEB, pyatspi.ROLE_EMBEDDED]

        try:
            rv = obj.getRole() in roles
        except:
            msg = "WEB: Exception getting role for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            rv = False

        return rv

    def inDocumentContent(self, obj=None):
        if not obj:
            obj = orca_state.locusOfFocus

        if self.isDocument(obj):
            return True

        rv = self._inDocumentContent.get(hash(obj))
        if rv is not None:
            return rv

        document = self.getDocumentForObject(obj)
        rv = document is not None
        self._inDocumentContent[hash(obj)] = rv
        return rv

    def _getDocumentsEmbeddedBy(self, frame):
        if not frame:
            return []

        isEmbeds = lambda r: r.getRelationType() == pyatspi.RELATION_EMBEDS
        try:
            relations = list(filter(isEmbeds, frame.getRelationSet()))
        except:
            msg = "ERROR: Exception getting embeds relation for %s" % frame
            debug.println(debug.LEVEL_INFO, msg, True)
            return []

        if not relations:
            return []

        relation = relations[0]
        targets = [relation.getTarget(i) for i in range(relation.getNTargets())]
        if not targets:
            return []

        return list(filter(self.isDocument, targets))

    def sanityCheckActiveWindow(self):
        app = self._script.app
        try:
            windowInApp = orca_state.activeWindow in app
        except:
            msg = "ERROR: Exception checking if %s is in %s" % (orca_state.activeWindow, app)
            debug.println(debug.LEVEL_INFO, msg, True)
            windowInApp = False

        if windowInApp:
            return True

        msg = "WARNING: %s is not in %s" % (orca_state.activeWindow, app)
        debug.println(debug.LEVEL_INFO, msg, True)

        try:
            script = _scriptManager.getScript(app, orca_state.activeWindow)
            msg = "WEB: Script for active Window is %s" % script
            debug.println(debug.LEVEL_INFO, msg, True)
        except:
            msg = "ERROR: Exception getting script for active window"
            debug.println(debug.LEVEL_INFO, msg, True)
        else:
            if type(script) == type(self._script):
                attrs = script.getTransferableAttributes()
                for attr, value in attrs.items():
                    msg = "WEB: Setting %s to %s" % (attr, value)
                    debug.println(debug.LEVEL_INFO, msg, True)
                    setattr(self._script, attr, value)

        window = self.activeWindow(app)
        try:
            self._script.app = window.getApplication()
            msg = "WEB: updating script's app to %s" % self._script.app
            debug.println(debug.LEVEL_INFO, msg, True)
        except:
            msg = "ERROR: Exception getting app for %s" % window
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        orca_state.activeWindow = window
        return True

    def activeDocument(self, window=None):
        isShowing = lambda x: x and x.getState().contains(pyatspi.STATE_SHOWING)
        documents = self._getDocumentsEmbeddedBy(window or orca_state.activeWindow)
        documents = list(filter(isShowing, documents))
        if len(documents) == 1:
            return documents[0]
        return None

    def documentFrame(self, obj=None):
        if not obj and self.sanityCheckActiveWindow():
            document = self.activeDocument()
            if document:
                return document

        return self.getDocumentForObject(obj or orca_state.locusOfFocus)

    def documentFrameURI(self, documentFrame=None):
        documentFrame = documentFrame or self.documentFrame()
        if documentFrame:
            try:
                document = documentFrame.queryDocument()
            except NotImplementedError:
                msg = "WEB: %s does not implement document interface" % documentFrame
                debug.println(debug.LEVEL_INFO, msg, True)
            except:
                msg = "ERROR: Exception querying document interface of %s" % documentFrame
                debug.println(debug.LEVEL_INFO, msg, True)
            else:
                return document.getAttributeValue('DocURL') or document.getAttributeValue('URI')

        return ""

    def isPlainText(self, documentFrame=None):
        return self.mimeType(documentFrame) == "text/plain"

    def mimeType(self, documentFrame=None):
        documentFrame = documentFrame or self.documentFrame()
        rv = self._mimeType.get(hash(documentFrame))
        if rv is not None:
            return rv

        try:
            document = documentFrame.queryDocument()
            attrs = dict([attr.split(":", 1) for attr in document.getAttributes()])
        except NotImplementedError:
            msg = "WEB: %s does not implement document interface" % documentFrame
            debug.println(debug.LEVEL_INFO, msg, True)
        except:
            msg = "ERROR: Exception getting document attributes of %s" % documentFrame
            debug.println(debug.LEVEL_INFO, msg, True)
        else:
            rv = attrs.get("MimeType")
            msg = "WEB: MimeType of %s is '%s'" % (documentFrame, rv)
            self._mimeType[hash(documentFrame)] = rv

        return rv

    def grabFocusWhenSettingCaret(self, obj):
        try:
            role = obj.getRole()
            state = obj.getState()
            childCount = obj.childCount
        except:
            msg = "WEB: Exception getting role, state, and childCount for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        # To avoid triggering popup lists.
        if role == pyatspi.ROLE_ENTRY:
            return False

        if role == pyatspi.ROLE_IMAGE:
            isLink = lambda x: x and x.getRole() == pyatspi.ROLE_LINK
            return pyatspi.utils.findAncestor(obj, isLink) is not None

        if role == pyatspi.ROLE_HEADING and childCount == 1:
            return self.isLink(obj[0])

        return state.contains(pyatspi.STATE_FOCUSABLE)

    def grabFocus(self, obj):
        try:
            obj.queryComponent().grabFocus()
        except NotImplementedError:
            msg = "WEB: %s does not implement the component interface" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
        except:
            msg = "WEB: Exception grabbing focus on %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)

    def setCaretPosition(self, obj, offset, documentFrame=None):
        if self._script.flatReviewContext:
            self._script.toggleFlatReviewMode()

        grabFocus = self.grabFocusWhenSettingCaret(obj)

        obj, offset = self.findFirstCaretContext(obj, offset)
        self.setCaretContext(obj, offset, documentFrame)
        if self._script.focusModeIsSticky():
            return

        oldFocus = orca_state.locusOfFocus
        self.clearTextSelection(oldFocus)
        orca.setLocusOfFocus(None, obj, notifyScript=False)
        if grabFocus:
            self.grabFocus(obj)

        # Don't use queryNonEmptyText() because we need to try to force-update focus.
        if "Text" in pyatspi.listInterfaces(obj):
            try:
                obj.queryText().setCaretOffset(offset)
            except:
                msg = "WEB: Exception setting caret to %i in %s" % (offset, obj)
                debug.println(debug.LEVEL_INFO, msg, True)
            else:
                msg = "WEB: Caret set to %i in %s" % (offset, obj)
                debug.println(debug.LEVEL_INFO, msg, True)

        if self._script.useFocusMode(obj, oldFocus) != self._script.inFocusMode():
            self._script.togglePresentationMode(None)

        if obj:
            obj.clearCache()

        # TODO - JD: This is private.
        self._script._saveFocusedObjectInfo(obj)

    def getNextObjectInDocument(self, obj, documentFrame):
        if not obj:
            return None

        for relation in obj.getRelationSet():
            if relation.getRelationType() == pyatspi.RELATION_FLOWS_TO:
                return relation.getTarget(0)

        if obj == documentFrame:
            obj, offset = self.getCaretContext(documentFrame)
            for child in documentFrame:
                if self.characterOffsetInParent(child) > offset:
                    return child

        if obj and obj.childCount:
            return obj[0]

        nextObj = None
        while obj and not nextObj:
            index = obj.getIndexInParent() + 1
            if 0 < index < obj.parent.childCount:
                nextObj = obj.parent[index]
            elif obj.parent != documentFrame:
                obj = obj.parent
            else:
                break

        return nextObj

    def getPreviousObjectInDocument(self, obj, documentFrame):
        if not obj:
            return None

        for relation in obj.getRelationSet():
            if relation.getRelationType() == pyatspi.RELATION_FLOWS_FROM:
                return relation.getTarget(0)

        if obj == documentFrame:
            obj, offset = self.getCaretContext(documentFrame)
            for child in documentFrame:
                if self.characterOffsetInParent(child) < offset:
                    return child

        index = obj.getIndexInParent() - 1
        if not 0 <= index < obj.parent.childCount:
            obj = obj.parent
            index = obj.getIndexInParent() - 1

        previousObj = obj.parent[index]
        while previousObj and previousObj.childCount:
            previousObj = previousObj[previousObj.childCount - 1]

        return previousObj

    def getTopOfFile(self):
        return self.findFirstCaretContext(self.documentFrame(), 0)

    def getBottomOfFile(self):
        obj = self.getLastObjectInDocument(self.documentFrame())
        offset = 0
        text = self.queryNonEmptyText(obj)
        if text:
            offset = text.characterCount - 1

        while obj:
            lastobj, lastoffset = self.nextContext(obj, offset)
            if not lastobj:
                break
            obj, offset = lastobj, lastoffset

        return [obj, offset]

    def getLastObjectInDocument(self, documentFrame):
        try:
            lastChild = documentFrame[documentFrame.childCount - 1]
        except:
            lastChild = documentFrame
        while lastChild:
            lastObj = self.getNextObjectInDocument(lastChild, documentFrame)
            if lastObj and lastObj != lastChild:
                lastChild = lastObj
            else:
                break

        return lastChild

    def objectAttributes(self, obj, useCache=True):
        if not (obj and self.inDocumentContent(obj)):
            return super().objectAttributes(obj)

        if useCache:
            rv = self._objectAttributes.get(hash(obj))
            if rv is not None:
                return rv

        try:
            rv = dict([attr.split(':', 1) for attr in obj.getAttributes()])
        except:
            rv = {}

        self._objectAttributes[hash(obj)] = rv
        return rv

    def getRoleDescription(self, obj, isBraille=False):
        attrs = self.objectAttributes(obj)
        rv = attrs.get('roledescription', '')
        if isBraille:
            rv = attrs.get('brailleroledescription', rv)

        return rv

    def nodeLevel(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return super().nodeLevel(obj)

        rv = -1
        if not (self.inMenu(obj) or obj.getRole() == pyatspi.ROLE_HEADING):
            attrs = self.objectAttributes(obj)
            # ARIA levels are 1-based; non-web content is 0-based. Be consistent.
            rv = int(attrs.get('level', 0)) -1

        return rv

    def _shouldCalculatePositionAndSetSize(self, obj):
        return True

    def getPositionAndSetSize(self, obj, **args):
        posinset = self.getPositionInSet(obj)
        setsize = self.getSetSize(obj)
        if posinset is not None and setsize is not None:
            # ARIA posinset is 1-based
            return posinset - 1, setsize

        if self._shouldCalculatePositionAndSetSize(obj):
            return super().getPositionAndSetSize(obj, **args)

        return -1, -1

    def getPositionInSet(self, obj):
        attrs = self.objectAttributes(obj, False)
        position = attrs.get('posinset')
        if position is not None:
            return int(position)

        if obj.getRole() == pyatspi.ROLE_TABLE_ROW:
            rowindex = attrs.get('rowindex')
            if rowindex is None and obj.childCount:
                roles = self._cellRoles()
                cell = pyatspi.findDescendant(obj, lambda x: x and x.getRole() in roles)
                rowindex = self.objectAttributes(cell, False).get('rowindex')

            if rowindex is not None:
                return int(rowindex)

        return None

    def getSetSize(self, obj):
        attrs = self.objectAttributes(obj, False)
        setsize = attrs.get('setsize')
        if setsize is not None:
            return int(setsize)

        if obj.getRole() == pyatspi.ROLE_TABLE_ROW:
            rows, cols = self.rowAndColumnCount(self.getTable(obj))
            if rows != -1:
                return rows

        return None

    def _getID(self, obj):
        attrs = self.objectAttributes(obj)
        return attrs.get('id')

    def _getDisplayStyle(self, obj):
        attrs = self.objectAttributes(obj)
        return attrs.get('display')

    def _getTag(self, obj):
        attrs = self.objectAttributes(obj)
        return attrs.get('tag')

    def _getXMLRoles(self, obj):
        attrs = self.objectAttributes(obj)
        return attrs.get('xml-roles', '').split()

    def inFindContainer(self, obj=None):
        if not obj:
            obj = orca_state.locusOfFocus

        if self.inDocumentContent(obj):
            return False

        return super().inFindContainer(obj)

    def isEmpty(self, obj):
        if not self.isTextBlockElement(obj):
            return False

        if obj.name:
            return False

        return self.queryNonEmptyText(obj, False) is None

    def isHidden(self, obj):
        attrs = self.objectAttributes(obj)
        return attrs.get('hidden', False)

    def _isOrIsIn(self, child, parent):
        if not (child and parent):
            return False

        if child == parent:
            return True

        return pyatspi.findAncestor(child, lambda x: x == parent)

    def isShowingAndVisible(self, obj):
        rv = super().isShowingAndVisible(obj)
        if rv or not self.inDocumentContent(obj):
            return rv

        if not mouse_review.reviewer.inMouseEvent:
            if not self._isOrIsIn(orca_state.locusOfFocus, obj):
                return rv

            msg = "WEB: %s contains locusOfFocus but not showing and visible" % obj
            debug.println(debug.LEVEL_INFO, msg, True)

        obj.clearCache()
        rv = super().isShowingAndVisible(obj)
        if rv:
            msg = "WEB: Clearing cache fixed state of %s. Missing event?" % obj
            debug.println(debug.LEVEL_INFO, msg, True)

        return rv

    def isTextArea(self, obj):
        if not self.inDocumentContent(obj):
            return super().isTextArea(obj)

        if self.isLink(obj):
            return False

        try:
            role = obj.getRole()
            state = obj.getState()
        except:
            msg = "WEB: Exception getting role and state for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if role == pyatspi.ROLE_COMBO_BOX \
           and state.contains(pyatspi.STATE_EDITABLE) \
           and not obj.childCount:
            return True

        if role in self._textBlockElementRoles():
            document = self.getDocumentForObject(obj)
            if document and document.getState().contains(pyatspi.STATE_EDITABLE):
                return True

        return super().isTextArea(obj)

    def isReadOnlyTextArea(self, obj):
        # NOTE: This method is deliberately more conservative than isTextArea.
        if obj.getRole() != pyatspi.ROLE_ENTRY:
            return False

        state = obj.getState()
        readOnly = state.contains(pyatspi.STATE_FOCUSABLE) \
                   and not state.contains(pyatspi.STATE_EDITABLE)

        return readOnly

    def setCaretOffset(self, obj, characterOffset):
        self.setCaretPosition(obj, characterOffset)
        self._script.updateBraille(obj)

    def nextContext(self, obj=None, offset=-1, skipSpace=False):
        if not obj:
            obj, offset = self.getCaretContext()

        nextobj, nextoffset = self.findNextCaretInOrder(obj, offset)
        if skipSpace:
            text = self.queryNonEmptyText(nextobj)
            while text and text.getText(nextoffset, nextoffset + 1) in [" ", "\xa0"]:
                nextobj, nextoffset = self.findNextCaretInOrder(nextobj, nextoffset)
                text = self.queryNonEmptyText(nextobj)

        return nextobj, nextoffset

    def previousContext(self, obj=None, offset=-1, skipSpace=False):
        if not obj:
            obj, offset = self.getCaretContext()

        prevobj, prevoffset = self.findPreviousCaretInOrder(obj, offset)
        if skipSpace:
            text = self.queryNonEmptyText(prevobj)
            while text and text.getText(prevoffset, prevoffset + 1) in [" ", "\xa0"]:
                prevobj, prevoffset = self.findPreviousCaretInOrder(prevobj, prevoffset)
                text = self.queryNonEmptyText(prevobj)

        return prevobj, prevoffset

    def lastContext(self, root):
        offset = 0
        text = self.queryNonEmptyText(root)
        if text:
            offset = text.characterCount - 1

        def _isInRoot(o):
            return o == root or pyatspi.utils.findAncestor(o, lambda x: x == root)

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

    @staticmethod
    def getExtents(obj, startOffset, endOffset):
        if not obj:
            return [0, 0, 0, 0]

        result = [0, 0, 0, 0]
        try:
            text = obj.queryText()
            if text.characterCount and 0 <= startOffset < endOffset:
                result = list(text.getRangeExtents(startOffset, endOffset, 0))
        except NotImplementedError:
            pass
        except:
            msg = "WEB: Exception getting range extents for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return [0, 0, 0, 0]
        else:
            if result[0] and result[1] and result[2] == 0 and result[3] == 0 \
               and text.getText(startOffset, endOffset).strip():
                msg = "WEB: Suspected bogus range extents for %s (chars: %i, %i): %s" % \
                    (obj, startOffset, endOffset, result)
                debug.println(debug.LEVEL_INFO, msg, True)
            elif text.characterCount:
                return result

        role = obj.getRole()
        try:
            parentRole = obj.parent.getRole()
        except:
            msg = "WEB: Exception getting role of parent (%s) of %s" % (obj.parent, obj)
            debug.println(debug.LEVEL_INFO, msg, True)
            parentRole = None

        if role in [pyatspi.ROLE_MENU, pyatspi.ROLE_LIST_ITEM] \
           and parentRole in [pyatspi.ROLE_COMBO_BOX, pyatspi.ROLE_LIST_BOX]:
            try:
                ext = obj.parent.queryComponent().getExtents(0)
            except NotImplementedError:
                msg = "WEB: %s does not implement the component interface" % obj.parent
                debug.println(debug.LEVEL_INFO, msg, True)
                return [0, 0, 0, 0]
            except:
                msg = "WEB: Exception getting extents for %s" % obj.parent
                debug.println(debug.LEVEL_INFO, msg, True)
                return [0, 0, 0, 0]
        else:
            try:
                ext = obj.queryComponent().getExtents(0)
            except NotImplementedError:
                msg = "WEB: %s does not implement the component interface" % obj
                debug.println(debug.LEVEL_INFO, msg, True)
                return [0, 0, 0, 0]
            except:
                msg = "WEB: Exception getting extents for %s" % obj
                debug.println(debug.LEVEL_INFO, msg, True)
                return [0, 0, 0, 0]

        return [ext.x, ext.y, ext.width, ext.height]

    def descendantAtPoint(self, root, x, y, coordType=None):
        if coordType is None:
            coordType = pyatspi.DESKTOP_COORDS

        result = None
        if self.isDocument(root):
            result = self.accessibleAtPoint(root, x, y, coordType)

        if result is None:
            result = super().descendantAtPoint(root, x, y, coordType)

        if self.isListItemMarker(result) or self.isStaticTextLeaf(result):
            return result.parent

        return result

    def _preserveTree(self, obj):
        if not (obj and obj.childCount):
            return False

        if self.isMathTopLevel(obj):
            return True

        return False

    def expandEOCs(self, obj, startOffset=0, endOffset=-1):
        if not self.inDocumentContent(obj):
            return super().expandEOCs(obj, startOffset, endOffset)

        text = self.queryNonEmptyText(obj)
        if not text:
            return ""

        if self._preserveTree(obj):
            utterances = self._script.speechGenerator.generateSpeech(obj)
            return self._script.speechGenerator.utterancesToString(utterances)

        return super().expandEOCs(obj, startOffset, endOffset).strip()

    def substring(self, obj, startOffset, endOffset):
        if not self.inDocumentContent(obj):
            return super().substring(obj, startOffset, endOffset)

        text = self.queryNonEmptyText(obj)
        if text:
            return text.getText(startOffset, endOffset)

        return ""

    def textAttributes(self, acc, offset, get_defaults=False):
        attrsForObj = self._currentTextAttrs.get(hash(acc)) or {}
        if offset in attrsForObj:
            return attrsForObj.get(offset)

        attrs = super().textAttributes(acc, offset, get_defaults)
        objAttributes = self.objectAttributes(acc, False)
        for key in self._script.attributeNamesDict.keys():
            value = objAttributes.get(key)
            if value is not None:
                attrs[0][key] = value

        self._currentTextAttrs[hash(acc)] = {offset:attrs}
        return attrs

    def localizeTextAttribute(self, key, value):
        if key == "justification" and value == "justify":
            value = "fill"

        return super().localizeTextAttribute(key, value)

    def adjustContentsForLanguage(self, contents):
        rv = []
        for content in contents:
            split = self.splitSubstringByLanguage(*content[0:3])
            for start, end, string, language, dialect in split:
                rv.append([content[0], start, end, string])

        return rv

    def getLanguageAndDialectFromTextAttributes(self, obj, startOffset=0, endOffset=-1):
        rv = super().getLanguageAndDialectFromTextAttributes(obj, startOffset, endOffset)

        # Embedded objects such as images and certain widgets won't implement the text interface
        # and thus won't expose text attributes. Therefore try to get the info from the parent.
        if not rv and obj and obj.parent:
            start, end = self.getHyperlinkRange(obj)
            language, dialect = self.getLanguageAndDialectForSubstring(obj.parent, start, end)
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

        child = self.getChildAtOffset(obj, offset)
        if child and not self.isTextBlockElement(child):
            matches = [x for x in contents if x[0] == child]
            if len(matches) == 1:
                return contents.index(matches[0])

        return -1

    def findPreviousObject(self, obj):
        result = super().findPreviousObject(obj)
        if not (obj and self.inDocumentContent(obj)):
            return result

        if not (result and self.inDocumentContent(result)):
            return None

        if self.getTopLevelDocumentForObject(result) != self.getTopLevelDocumentForObject(obj):
            return None

        msg = "WEB: Previous object for %s is %s." % (obj, result)
        debug.println(debug.LEVEL_INFO, msg, True)
        return result

    def findNextObject(self, obj):
        result = super().findNextObject(obj)
        if not (obj and self.inDocumentContent(obj)):
            return result

        if not (result and self.inDocumentContent(result)):
            return None

        if self.getTopLevelDocumentForObject(result) != self.getTopLevelDocumentForObject(obj):
            return None

        msg = "WEB: Next object for %s is %s." % (obj, result)
        debug.println(debug.LEVEL_INFO, msg, True)
        return result

    def isNonEntryTextWidget(self, obj):
        rv = self._isNonEntryTextWidget.get(hash(obj))
        if rv is not None:
            return rv

        roles = [pyatspi.ROLE_CHECK_BOX,
                 pyatspi.ROLE_CHECK_MENU_ITEM,
                 pyatspi.ROLE_MENU,
                 pyatspi.ROLE_MENU_ITEM,
                 pyatspi.ROLE_PAGE_TAB,
                 pyatspi.ROLE_RADIO_MENU_ITEM,
                 pyatspi.ROLE_RADIO_BUTTON,
                 pyatspi.ROLE_PUSH_BUTTON,
                 pyatspi.ROLE_TOGGLE_BUTTON]

        role = obj.getRole()
        if role in roles:
            rv = True
        elif role == pyatspi.ROLE_LIST_ITEM:
            rv = obj.parent.getRole() != pyatspi.ROLE_LIST
        elif role == pyatspi.ROLE_TABLE_CELL:
            if obj.getState().contains(pyatspi.STATE_EDITABLE):
                rv = False
            else:
                rv = not self.isTextBlockElement(obj)

        self._isNonEntryTextWidget[hash(obj)] = rv
        return rv

    def treatAsTextObject(self, obj, excludeNonEntryTextWidgets=True):
        if not obj or self.isDead(obj):
            return False

        rv = self._treatAsTextObject.get(hash(obj))
        if rv is not None:
            return rv

        rv = "Text" in pyatspi.listInterfaces(obj)
        if not rv:
            msg = "WEB: %s does not implement text interface" % obj
            debug.println(debug.LEVEL_INFO, msg, True)

        if not self.inDocumentContent(obj):
            return rv

        if rv and self._treatObjectAsWhole(obj, -1) and obj.name and not self.isCellWithNameFromHeader(obj):
            msg = "WEB: Treating %s as non-text: named object treated as whole." % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            rv = False

        elif rv and not self.isLiveRegion(obj):
            doNotQuery = [pyatspi.ROLE_LIST_BOX]
            role = obj.getRole()
            if rv and role in doNotQuery:
                msg = "WEB: Treating %s as non-text due to role." % obj
                debug.println(debug.LEVEL_INFO, msg, True)
                rv = False
            if rv and excludeNonEntryTextWidgets and self.isNonEntryTextWidget(obj):
                msg = "WEB: Treating %s as non-text: is non-entry text widget." % obj
                debug.println(debug.LEVEL_INFO, msg, True)
                rv = False
            if rv and (self.isHidden(obj) or self.isOffScreenLabel(obj)):
                msg = "WEB: Treating %s as non-text: is hidden or off-screen label." % obj
                debug.println(debug.LEVEL_INFO, msg, True)
                rv = False
            if rv and self.isNonNavigableEmbeddedDocument(obj):
                msg = "WEB: Treating %s as non-text: is non-navigable embedded document." % obj
                debug.println(debug.LEVEL_INFO, msg, True)
                rv = False
            if rv and self.isFakePlaceholderForEntry(obj):
                msg = "WEB: Treating %s as non-text: is fake placeholder for entry." % obj
                debug.println(debug.LEVEL_INFO, msg, True)
                rv = False

        self._treatAsTextObject[hash(obj)] = rv
        return rv

    def queryNonEmptyText(self, obj, excludeNonEntryTextWidgets=True):
        if self._script.browseModeIsSticky():
            return super().queryNonEmptyText(obj)

        if not self.treatAsTextObject(obj, excludeNonEntryTextWidgets):
            return None

        return super().queryNonEmptyText(obj)

    def hasNameAndActionAndNoUsefulChildren(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return False

        rv = self._hasNameAndActionAndNoUsefulChildren.get(hash(obj))
        if rv is not None:
            return rv

        rv = False
        if self.hasExplicitName(obj) and "Action" in pyatspi.listInterfaces(obj):
            for child in obj:
                if not self.isUselessEmptyElement(child) or self.isUselessImage(child):
                    break
            else:
                rv = True

        if rv:
            msg = "WEB: %s has name and action and no useful children" % obj
            debug.println(debug.LEVEL_INFO, msg, True)

        self._hasNameAndActionAndNoUsefulChildren[hash(obj)] = rv
        return rv

    def isNonInteractiveDescendantOfControl(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return False

        rv = self._isNonInteractiveDescendantOfControl.get(hash(obj))
        if rv is not None:
            return rv

        try:
            role = obj.getRole()
            state = obj.getState()
        except:
            msg = "WEB: Exception getting role and state for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        rv = False
        roles = self._textBlockElementRoles()
        roles.extend([pyatspi.ROLE_IMAGE, pyatspi.ROLE_CANVAS])
        if role in roles and not state.contains(pyatspi.STATE_FOCUSABLE):
            controls = [pyatspi.ROLE_CHECK_BOX,
                        pyatspi.ROLE_CHECK_MENU_ITEM,
                        pyatspi.ROLE_LIST_BOX,
                        pyatspi.ROLE_MENU_ITEM,
                        pyatspi.ROLE_RADIO_MENU_ITEM,
                        pyatspi.ROLE_RADIO_BUTTON,
                        pyatspi.ROLE_PUSH_BUTTON,
                        pyatspi.ROLE_TOGGLE_BUTTON,
                        pyatspi.ROLE_TREE_ITEM]
            rv = pyatspi.findAncestor(obj, lambda x: x and x.getRole() in controls)

        self._isNonInteractiveDescendantOfControl[hash(obj)] = rv
        return rv

    def _treatObjectAsWhole(self, obj, offset=None):
        always = [pyatspi.ROLE_CHECK_BOX,
                  pyatspi.ROLE_CHECK_MENU_ITEM,
                  pyatspi.ROLE_LIST_BOX,
                  pyatspi.ROLE_MENU_ITEM,
                  pyatspi.ROLE_RADIO_MENU_ITEM,
                  pyatspi.ROLE_RADIO_BUTTON,
                  pyatspi.ROLE_PUSH_BUTTON,
                  pyatspi.ROLE_TOGGLE_BUTTON]

        descendable = [pyatspi.ROLE_MENU,
                       pyatspi.ROLE_MENU_BAR,
                       pyatspi.ROLE_TOOL_BAR,
                       pyatspi.ROLE_TREE_ITEM]

        role = obj.getRole()
        if role in always:
            return True

        if role in descendable:
            if self._script.inFocusMode():
                return True

            # This should cause us to initially stop at the large containers before
            # allowing the user to drill down into them in browse mode.
            return offset == -1

        if role == pyatspi.ROLE_ENTRY:
            if obj.childCount == 1 and self.isFakePlaceholderForEntry(obj[0]):
                return True
            return False

        state = obj.getState()
        if state.contains(pyatspi.STATE_EDITABLE):
            return False

        if role == pyatspi.ROLE_TABLE_CELL:
            if self.isFocusModeWidget(obj):
                return not self._script.browseModeIsSticky()
            if self.hasNameAndActionAndNoUsefulChildren(obj):
                return True

        if role in [pyatspi.ROLE_COLUMN_HEADER, pyatspi.ROLE_ROW_HEADER] \
           and self.hasExplicitName(obj):
            return True

        if role == pyatspi.ROLE_COMBO_BOX:
            return True

        if role in [pyatspi.ROLE_EMBEDDED, pyatspi.ROLE_TREE, pyatspi.ROLE_TREE_TABLE]:
            return not self._script.browseModeIsSticky()

        if role == pyatspi.ROLE_LINK:
            return self.hasExplicitName(obj) or self.hasUselessCanvasDescendant(obj)

        if self.isNonNavigableEmbeddedDocument(obj):
            return True

        if self.isFakePlaceholderForEntry(obj):
            return True

        if self.isCustomImage(obj):
            return True

        return False

    def __findRange(self, text, offset, start, end, boundary):
        # We should not have to do any of this. Seriously. This is why
        # We can't have nice things.

        allText = text.getText(0, -1)
        if boundary == pyatspi.TEXT_BOUNDARY_CHAR:
            try:
                string = allText[offset]
            except IndexError:
                string = ""

            return string, offset, offset + 1

        extents = list(text.getRangeExtents(offset, offset + 1, 0))

        def _inThisSpan(span):
            return span[0] <= offset <= span[1]

        def _onThisLine(span):
            start, end = span
            startExtents = list(text.getRangeExtents(start, start + 1, 0))
            endExtents = list(text.getRangeExtents(end - 1, end, 0))
            delta = max(startExtents[3], endExtents[3])
            if not self.extentsAreOnSameLine(startExtents, endExtents, delta):
                msg = "FAIL: Start %s and end %s of '%s' not on same line" \
                      % (startExtents, endExtents, allText[start:end])
                debug.println(debug.LEVEL_INFO, msg, True)
                startExtents = endExtents

            return self.extentsAreOnSameLine(extents, startExtents)

        spans = []
        charCount = text.characterCount
        if boundary == pyatspi.TEXT_BOUNDARY_SENTENCE_START:
            spans = [m.span() for m in re.finditer(r"\S*[^\.\?\!]+((?<!\w)[\.\?\!]+(?!\w)|\S*)", allText)]
        elif boundary is not None:
            spans = [m.span() for m in re.finditer("[^\n\r]+", allText)]
        if not spans:
            spans = [(0, charCount)]

        rangeStart, rangeEnd = 0, charCount
        for span in spans:
            if _inThisSpan(span):
                rangeStart, rangeEnd = span[0], span[1] + 1
                break

        string = allText[rangeStart:rangeEnd]
        if string and boundary in [pyatspi.TEXT_BOUNDARY_SENTENCE_START, None]:
            return string, rangeStart, rangeEnd

        words = [m.span() for m in re.finditer("[^\\s\ufffc]+", string)]
        words = list(map(lambda x: (x[0] + rangeStart, x[1] + rangeStart), words))
        if boundary == pyatspi.TEXT_BOUNDARY_WORD_START:
            spans = list(filter(_inThisSpan, words))
        if boundary == pyatspi.TEXT_BOUNDARY_LINE_START:
            spans = list(filter(_onThisLine, words))
        if spans:
            rangeStart, rangeEnd = spans[0][0], spans[-1][1] + 1
            string = allText[rangeStart:rangeEnd]

        if not (rangeStart <= offset <= rangeEnd):
            return allText[start:end], start, end

        return string, rangeStart, rangeEnd

    def _attemptBrokenTextRecovery(self, obj, **args):
        return False

    def _getTextAtOffset(self, obj, offset, boundary):
        if not obj:
            msg = "WEB: Results for text at offset %i for %s using %s:\n" \
                  "     String: '', Start: 0, End: 0. (obj is None)" % (offset, obj, boundary)
            debug.println(debug.LEVEL_INFO, msg, True)
            return '', 0, 0

        text = self.queryNonEmptyText(obj)
        if not text:
            msg = "WEB: Results for text at offset %i for %s using %s:\n" \
                  "     String: '', Start: 0, End: 1. (queryNonEmptyText() returned None)" \
                  % (offset, obj, boundary)
            debug.println(debug.LEVEL_INFO, msg, True)
            return '', 0, 1

        if boundary is None:
            string, start, end = text.getText(0, -1), 0, text.characterCount
            s = string.replace(self.EMBEDDED_OBJECT_CHARACTER, "[OBJ]").replace("\n", "\\n")
            msg = "WEB: Results for text at offset %i for %s using %s:\n" \
                  "     String: '%s', Start: %i, End: %i." % (offset, obj, boundary, s, start, end)
            debug.println(debug.LEVEL_INFO, msg, True)
            return string, start, end

        if boundary == pyatspi.TEXT_BOUNDARY_SENTENCE_START \
            and not obj.getState().contains(pyatspi.STATE_EDITABLE):
            allText = text.getText(0, -1)
            if obj.getRole() in [pyatspi.ROLE_LIST_ITEM, pyatspi.ROLE_HEADING] \
               or not (re.search(r"\w", allText) and self.isTextBlockElement(obj)):
                string, start, end = allText, 0, text.characterCount
                s = string.replace(self.EMBEDDED_OBJECT_CHARACTER, "[OBJ]").replace("\n", "\\n")
                msg = "WEB: Results for text at offset %i for %s using %s:\n" \
                      "     String: '%s', Start: %i, End: %i." % (offset, obj, boundary, s, start, end)
                debug.println(debug.LEVEL_INFO, msg, True)
                return string, start, end

        if boundary == pyatspi.TEXT_BOUNDARY_LINE_START and self.treatAsEndOfLine(obj, offset):
            offset -= 1
            msg = "WEB: Line sought for %s at end of text. Adjusting offset to %i." % (obj, offset)
            debug.println(debug.LEVEL_INFO, msg, True)

        offset = max(0, offset)
        string, start, end = text.getTextAtOffset(offset, boundary)

        # The above should be all that we need to do, but....
        if not self._attemptBrokenTextRecovery(obj, boundary=boundary):
            s = string.replace(self.EMBEDDED_OBJECT_CHARACTER, "[OBJ]").replace("\n", "\\n")
            msg = "WEB: Results for text at offset %i for %s using %s:\n" \
                  "     String: '%s', Start: %i, End: %i.\n" \
                  "     Not checking for broken text." % (offset, obj, boundary, s, start, end)
            debug.println(debug.LEVEL_INFO, msg, True)
            return string, start, end

        needSadHack = False
        testString, testStart, testEnd = text.getTextAtOffset(start, boundary)
        if (string, start, end) != (testString, testStart, testEnd):
            s1 = string.replace(self.EMBEDDED_OBJECT_CHARACTER, "[OBJ]").replace("\n", "\\n")
            s2 = testString.replace(self.EMBEDDED_OBJECT_CHARACTER, "[OBJ]").replace("\n", "\\n")
            msg = "FAIL: Bad results for text at offset for %s using %s.\n" \
                  "      For offset %i - String: '%s', Start: %i, End: %i.\n" \
                  "      For offset %i - String: '%s', Start: %i, End: %i.\n" \
                  "      The bug is the above results should be the same.\n" \
                  "      This very likely needs to be fixed by the toolkit." \
                  % (obj, boundary, offset, s1, start, end, start, s2, testStart, testEnd)
            debug.println(debug.LEVEL_INFO, msg, True)
            needSadHack = True
        elif not string and 0 <= offset < text.characterCount:
            s1 = string.replace(self.EMBEDDED_OBJECT_CHARACTER, "[OBJ]").replace("\n", "\\n")
            s2 = text.getText(0, -1).replace(self.EMBEDDED_OBJECT_CHARACTER, "[OBJ]").replace("\n", "\\n")
            msg = "FAIL: Bad results for text at offset %i for %s using %s:\n" \
                  "      String: '%s', Start: %i, End: %i.\n" \
                  "      The bug is no text reported for a valid offset.\n" \
                  "      Character count: %i, Full text: '%s'.\n" \
                  "      This very likely needs to be fixed by the toolkit." \
                  % (offset, obj, boundary, s1, start, end, text.characterCount, s2)
            debug.println(debug.LEVEL_INFO, msg, True)
            needSadHack = True
        elif not (start <= offset < end) and not (self.isPlainText() or self.elementIsPreformattedText(obj)):
            s1 = string.replace(self.EMBEDDED_OBJECT_CHARACTER, "[OBJ]").replace("\n", "\\n")
            msg = "FAIL: Bad results for text at offset %i for %s using %s:\n" \
                  "      String: '%s', Start: %i, End: %i.\n" \
                  "      The bug is the range returned is outside of the offset.\n" \
                  "      This very likely needs to be fixed by the toolkit." \
                  % (offset, obj, boundary, s1, start, end)
            debug.println(debug.LEVEL_INFO, msg, True)
            needSadHack = True
        elif len(string) < end - start:
            s1 = string.replace(self.EMBEDDED_OBJECT_CHARACTER, "[OBJ]").replace("\n", "\\n")
            msg = "FAIL: Bad results for text at offset %i for %s using %s:\n" \
                  "      String: '%s', Start: %i, End: %i.\n" \
                  "      The bug is that the length of string is less than the text range.\n" \
                  "      This very likely needs to be fixed by the toolkit." \
                  % (offset, obj, boundary, s1, start, end)
            debug.println(debug.LEVEL_INFO, msg, True)
            needSadHack = True
        elif boundary == pyatspi.TEXT_BOUNDARY_CHAR and string == "\ufffd":
            msg = "FAIL: Bad results for text at offset %i for %s using %s:\n" \
                  "      String: '%s', Start: %i, End: %i.\n" \
                  "      The bug is that we didn't seem to get a valid character.\n" \
                  "      This very likely needs to be fixed by the toolkit." \
                  % (offset, obj, boundary, string, start, end)
            debug.println(debug.LEVEL_INFO, msg, True)
            needSadHack = True

        if needSadHack:
            sadString, sadStart, sadEnd = self.__findRange(text, offset, start, end, boundary)
            s = sadString.replace(self.EMBEDDED_OBJECT_CHARACTER, "[OBJ]").replace("\n", "\\n")
            msg = "HACK: Attempting to recover from above failure.\n" \
                  "      String: '%s', Start: %i, End: %i." % (s, sadStart, sadEnd)
            debug.println(debug.LEVEL_INFO, msg, True)
            return sadString, sadStart, sadEnd

        s = string.replace(self.EMBEDDED_OBJECT_CHARACTER, "[OBJ]").replace("\n", "\\n")
        msg = "WEB: Results for text at offset %i for %s using %s:\n" \
              "     String: '%s', Start: %i, End: %i." % (offset, obj, boundary, s, start, end)
        debug.println(debug.LEVEL_INFO, msg, True)
        return string, start, end

    def _getContentsForObj(self, obj, offset, boundary):
        if not obj:
            return []

        if boundary == pyatspi.TEXT_BOUNDARY_SENTENCE_START and self.isTime(obj):
            text = self.queryNonEmptyText(obj)
            if text:
                return [[obj, 0, text.characterCount, text.getText(0, -1)]]

        if boundary == pyatspi.TEXT_BOUNDARY_LINE_START:
            if self.isMath(obj):
                if self.isMathTopLevel(obj):
                    math = obj
                else:
                    math = self.getMathAncestor(obj)
                return [[math, 0, 1, '']]

            text = self.queryNonEmptyText(obj)

            if self.elementLinesAreSingleChars(obj):
                if obj.name and text:
                    msg = "WEB: Returning name as contents for %s (single-char lines)" % obj
                    debug.println(debug.LEVEL_INFO, msg, True)
                    return [[obj, 0, text.characterCount, obj.name]]

                msg = "WEB: Returning all text as contents for %s (single-char lines)" % obj
                debug.println(debug.LEVEL_INFO, msg, True)
                boundary = None

            if self.elementLinesAreSingleWords(obj):
                if obj.name and text:
                    msg = "WEB: Returning name as contents for %s (single-word lines)" % obj
                    debug.println(debug.LEVEL_INFO, msg, True)
                    return [[obj, 0, text.characterCount, obj.name]]

                msg = "WEB: Returning all text as contents for %s (single-word lines)" % obj
                debug.println(debug.LEVEL_INFO, msg, True)
                boundary = None

        role = obj.getRole()
        if role == pyatspi.ROLE_INTERNAL_FRAME and obj.childCount == 1:
            return self._getContentsForObj(obj[0], 0, boundary)

        string, start, end = self._getTextAtOffset(obj, offset, boundary)
        if not string:
            return [[obj, start, end, string]]

        stringOffset = offset - start
        try:
            char = string[stringOffset]
        except:
            pass
        else:
            if char == self.EMBEDDED_OBJECT_CHARACTER:
                child = self.getChildAtOffset(obj, offset)
                if child:
                    return self._getContentsForObj(child, 0, boundary)

        ranges = [m.span() for m in re.finditer("[^\ufffc]+", string)]
        strings = list(filter(lambda x: x[0] <= stringOffset <= x[1], ranges))
        if len(strings) == 1:
            rangeStart, rangeEnd = strings[0]
            start += rangeStart
            string = string[rangeStart:rangeEnd]
            end = start + len(string)

        if boundary in [pyatspi.TEXT_BOUNDARY_WORD_START, pyatspi.TEXT_BOUNDARY_CHAR]:
            return [[obj, start, end, string]]

        return self.adjustContentsForLanguage([[obj, start, end, string]])

    def getSentenceContentsAtOffset(self, obj, offset, useCache=True):
        if not obj:
            return []

        offset = max(0, offset)

        if useCache:
            if self.findObjectInContents(obj, offset, self._currentSentenceContents, usingCache=True) != -1:
                return self._currentSentenceContents

        boundary = pyatspi.TEXT_BOUNDARY_SENTENCE_START
        objects = self._getContentsForObj(obj, offset, boundary)
        state = obj.getState()
        if state.contains(pyatspi.STATE_EDITABLE):
            if state.contains(pyatspi.STATE_FOCUSED):
                return objects
            if self.isContentEditableWithEmbeddedObjects(obj):
                return objects

        def _treatAsSentenceEnd(x):
            xObj, xStart, xEnd, xString = x
            if not self.isTextBlockElement(xObj):
                return False

            text = self.queryNonEmptyText(xObj)
            if text and 0 < text.characterCount <= xEnd:
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
            elif self.isTextBlockElement(firstObj.parent):
                if self.characterOffsetInParent(firstObj) == 0:
                    break

            prevObj, pOffset = self.findPreviousCaretInOrder(firstObj, firstStart)
            onLeft = self._getContentsForObj(prevObj, pOffset, boundary)
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
            onRight = self._getContentsForObj(nextObj, nOffset, boundary)
            onRight = list(filter(lambda x: x not in objects, onRight))
            if not onRight:
                break

            objects.extend(onRight)

        if useCache:
            self._currentSentenceContents = objects

        return objects

    def getCharacterContentsAtOffset(self, obj, offset, useCache=True):
        if not obj:
            return []

        offset = max(0, offset)

        if useCache:
            if self.findObjectInContents(obj, offset, self._currentCharacterContents, usingCache=True) != -1:
                return self._currentCharacterContents

        boundary = pyatspi.TEXT_BOUNDARY_CHAR
        objects = self._getContentsForObj(obj, offset, boundary)
        if useCache:
            self._currentCharacterContents = objects

        return objects

    def getWordContentsAtOffset(self, obj, offset, useCache=True):
        if not obj:
            return []

        offset = max(0, offset)

        if useCache:
            if self.findObjectInContents(obj, offset, self._currentWordContents, usingCache=True) != -1:
                self._debugContentsInfo(obj, offset, self._currentWordContents, "Word (cached)")
                return self._currentWordContents

        boundary = pyatspi.TEXT_BOUNDARY_WORD_START
        objects = self._getContentsForObj(obj, offset, boundary)
        extents = self.getExtents(obj, offset, offset + 1)

        def _include(x):
            if x in objects:
                return False

            xObj, xStart, xEnd, xString = x
            if xStart == xEnd or not xString:
                return False

            xExtents = self.getExtents(xObj, xStart, xStart + 1)
            return self.extentsAreOnSameLine(extents, xExtents)

        # Check for things in the same word to the left of this object.
        firstObj, firstStart, firstEnd, firstString = objects[0]
        prevObj, pOffset = self.findPreviousCaretInOrder(firstObj, firstStart)
        while prevObj and firstString and prevObj != firstObj:
            text = self.queryNonEmptyText(prevObj)
            if not text or text.getText(pOffset, pOffset + 1).isspace():
                break

            onLeft = self._getContentsForObj(prevObj, pOffset, boundary)
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

            onRight = self._getContentsForObj(nextObj, nOffset, boundary)
            if onRight and self._contentIsSubsetOf(objects[0], onRight[-1]):
                onRight = onRight[0:-1]

            onRight = list(filter(_include, onRight))
            if not onRight:
                break

            objects.extend(onRight)
            lastObj, lastStart, lastEnd, lastString = objects[-1]

        # We want to treat the list item marker as its own word.
        firstObj, firstStart, firstEnd, firstString = objects[0]
        if firstStart == 0 and firstObj.getRole() == pyatspi.ROLE_LIST_ITEM:
            objects = [objects[0]]

        if useCache:
            self._currentWordContents = objects

        self._debugContentsInfo(obj, offset, objects, "Word (not cached)")
        return objects

    def getObjectContentsAtOffset(self, obj, offset=0, useCache=True):
        if not obj:
            return []

        if self.isDead(obj):
            msg = "ERROR: Cannot get object contents at offset for dead object."
            debug.println(debug.LEVEL_INFO, msg, True)
            return []

        offset = max(0, offset)

        if useCache:
            if self.findObjectInContents(obj, offset, self._currentObjectContents, usingCache=True) != -1:
                self._debugContentsInfo(obj, offset, self._currentObjectContents, "Object (cached)")
                return self._currentObjectContents

        objIsLandmark = self.isLandmark(obj)

        def _isInObject(x):
            if not x:
                return False
            if x == obj:
                return True
            return _isInObject(x.parent)

        def _include(x):
            if x in objects:
                return False

            xObj, xStart, xEnd, xString = x
            if xStart == xEnd:
                return False

            if objIsLandmark and self.isLandmark(xObj) and obj != xObj:
                return False

            return _isInObject(xObj)

        objects = self._getContentsForObj(obj, offset, None)
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

        msg = "WEB: %s for %s at offset %i:" % (contentsMsg, obj, offset)
        debug.println(debug.LEVEL_INFO, msg, True)

        indent = " " * 8
        for i, (acc, start, end, string) in enumerate(contents):
            try:
                extents = self.getExtents(acc, start, end)
            except:
                extents = "(exception)"
            msg = "     %i. chars: %i-%i: '%s' extents=%s\n" % (i, start, end, string, extents)
            msg += debug.getAccessibleDetails(debug.LEVEL_INFO, acc, indent)
            debug.println(debug.LEVEL_INFO, msg, True)

    def treatAsEndOfLine(self, obj, offset):
        if not self.isContentEditableWithEmbeddedObjects(obj):
            return False

        if "Text" not in pyatspi.listInterfaces(obj):
            return False

        if self.isDocument(obj):
            return False

        text = obj.queryText()
        if offset == text.characterCount:
            msg = "WEB: %s offset %i is end of line: offset is characterCount" % (obj, offset)
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        # Do not treat a literal newline char as the end of line. When there is an
        # actual newline character present, user agents should give us the right value
        # for the line at that offset. Here we are trying to figure out where asking
        # for the line at offset will give us the next line rather than the line where
        # the cursor is physically blinking.

        char = text.getText(offset, offset + 1)
        if char == self.EMBEDDED_OBJECT_CHARACTER:
            prevExtents = self.getExtents(obj, offset - 1, offset)
            thisExtents = self.getExtents(obj, offset, offset + 1)
            sameLine = self.extentsAreOnSameLine(prevExtents, thisExtents)
            msg = "WEB: %s offset %i is [obj]. Same line: %s Is end of line: %s" % \
                (obj, offset, sameLine, not sameLine)
            debug.println(debug.LEVEL_INFO, msg, True)
            return not sameLine

        return False

    def getLineContentsAtOffset(self, obj, offset, layoutMode=None, useCache=True):
        startTime = time.time()
        if not obj:
            return []

        if self.isDead(obj):
            msg = "ERROR: Cannot get line contents at offset for dead object."
            debug.println(debug.LEVEL_INFO, msg, True)
            return []

        offset = max(0, offset)
        if obj.getRole() == pyatspi.ROLE_TOOL_BAR and not self._treatObjectAsWhole(obj):
            child = self.getChildAtOffset(obj, offset)
            if child:
                obj = child
                offset = 0

        if useCache:
            if self.findObjectInContents(obj, offset, self._currentLineContents, usingCache=True) != -1:
                self._debugContentsInfo(obj, offset, self._currentLineContents, "Line (cached)")
                return self._currentLineContents

        if layoutMode is None:
            layoutMode = _settingsManager.getSetting('layoutMode') or self._script.inFocusMode()

        objects = []
        if offset > 0 and self.treatAsEndOfLine(obj, offset):
            extents = self.getExtents(obj, offset - 1, offset)
        else:
            extents = self.getExtents(obj, offset, offset + 1)

        if self.isInlineListDescendant(obj):
            container = self.listForInlineListDescendant(obj)
            if container:
                extents = self.getExtents(container, 0, 1)

        objBanner = pyatspi.findAncestor(obj, self.isLandmarkBanner)

        def _include(x):
            if x in objects:
                return False

            xObj, xStart, xEnd, xString = x
            if xStart == xEnd:
                return False

            xExtents = self.getExtents(xObj, xStart, xStart + 1)

            if obj != xObj:
                if self.isLandmark(obj) and self.isLandmark(xObj):
                    return False
                if self.isLink(obj) and self.isLink(xObj):
                    xObjBanner =  pyatspi.findAncestor(xObj, self.isLandmarkBanner)
                    if (objBanner or xObjBanner) and objBanner != xObjBanner:
                        return False
                    if abs(extents[0] - xExtents[0]) <= 1 and abs(extents[1] - xExtents[1]) <= 1:
                        # This happens with dynamic skip links such as found on Wikipedia.
                        return False
                elif self.isBlockListDescendant(obj) != self.isBlockListDescendant(xObj):
                    return False
                elif obj.getRole() in [pyatspi.ROLE_TREE, pyatspi.ROLE_TREE_ITEM] \
                     and xObj.getRole() in [pyatspi.ROLE_TREE, pyatspi.ROLE_TREE_ITEM]:
                    return False
                elif obj.getRole() == pyatspi.ROLE_HEADING and self.hasNoSize(obj):
                    return False
                elif xObj.getRole() == pyatspi.ROLE_HEADING and self.hasNoSize(xObj):
                    return False

            if self.isMathTopLevel(xObj) or self.isMath(obj):
                onSameLine = self.extentsAreOnSameLine(extents, xExtents, extents[3])
            elif self.isTextSubscriptOrSuperscript(xObj):
                onSameLine = self.extentsAreOnSameLine(extents, xExtents, xExtents[3])
            else:
                onSameLine = self.extentsAreOnSameLine(extents, xExtents)
            return onSameLine

        boundary = pyatspi.TEXT_BOUNDARY_LINE_START
        objects = self._getContentsForObj(obj, offset, boundary)
        if not layoutMode:
            if useCache:
                self._currentLineContents = objects

            self._debugContentsInfo(obj, offset, objects, "Line (not layout mode)")
            return objects

        firstObj, firstStart, firstEnd, firstString = objects[0]
        if (extents[2] == 0 and extents[3] == 0) or self.isMath(firstObj):
            extents = self.getExtents(firstObj, firstStart, firstEnd)

        lastObj, lastStart, lastEnd, lastString = objects[-1]
        if self.isMathTopLevel(lastObj):
            lastObj, lastEnd = self.lastContext(lastObj)
            lastEnd += 1

        document = self.getDocumentForObject(obj)
        prevObj, pOffset = self.findPreviousCaretInOrder(firstObj, firstStart)
        nextObj, nOffset = self.findNextCaretInOrder(lastObj, lastEnd - 1)

        # Check for things on the same line to the left of this object.
        prevStartTime = time.time()
        while prevObj and self.getDocumentForObject(prevObj) == document:
            text = self.queryNonEmptyText(prevObj)
            if text and text.getText(pOffset, pOffset + 1) in [" ", "\xa0"]:
                prevObj, pOffset = self.findPreviousCaretInOrder(prevObj, pOffset)

            if text and text.getText(pOffset, pOffset + 1) == "\n" and firstObj == prevObj:
                break

            onLeft = self._getContentsForObj(prevObj, pOffset, boundary)
            onLeft = list(filter(_include, onLeft))
            if not onLeft:
                break

            if self._contentIsSubsetOf(objects[0], onLeft[-1]):
                objects.pop(0)

            objects[0:0] = onLeft
            firstObj, firstStart = objects[0][0], objects[0][1]
            prevObj, pOffset = self.findPreviousCaretInOrder(firstObj, firstStart)

        prevEndTime = time.time()
        msg = "INFO: Time needed to get line contents on left: %.4fs" % (prevEndTime - prevStartTime)
        debug.println(debug.LEVEL_INFO, msg, True)

        # Check for things on the same line to the right of this object.
        nextStartTime = time.time()
        while nextObj and self.getDocumentForObject(nextObj) == document:
            text = self.queryNonEmptyText(nextObj)
            if text and text.getText(nOffset, nOffset + 1) in [" ", "\xa0"]:
                nextObj, nOffset = self.findNextCaretInOrder(nextObj, nOffset)

            if text and text.getText(nOffset, nOffset + 1) == "\n" and lastObj == nextObj:
                break

            onRight = self._getContentsForObj(nextObj, nOffset, boundary)
            if onRight and self._contentIsSubsetOf(objects[0], onRight[-1]):
                onRight = onRight[0:-1]

            onRight = list(filter(_include, onRight))
            if not onRight:
                break

            objects.extend(onRight)
            lastObj, lastEnd = objects[-1][0], objects[-1][2]
            if self.isMathTopLevel(lastObj):
                lastObj, lastEnd = self.lastContext(lastObj)
                lastEnd += 1

            nextObj, nOffset = self.findNextCaretInOrder(lastObj, lastEnd - 1)

        nextEndTime = time.time()
        msg = "INFO: Time needed to get line contents on right: %.4fs" % (nextEndTime - nextStartTime)
        debug.println(debug.LEVEL_INFO, msg, True)

        firstObj, firstStart, firstEnd, firstString = objects[0]
        if firstString == "\n" and len(objects) > 1:
            objects.pop(0)

        if useCache:
            self._currentLineContents = objects

        msg = "INFO: Time needed to get line contents: %.4fs" % (time.time() - startTime)
        debug.println(debug.LEVEL_INFO, msg, True)

        self._debugContentsInfo(obj, offset, objects, "Line (layout mode)")
        return objects

    def getPreviousLineContents(self, obj=None, offset=-1, layoutMode=None, useCache=True):
        if obj is None:
            obj, offset = self.getCaretContext()

        msg = "WEB: Current context is: %s, %i (focus: %s)" \
              % (obj, offset, orca_state.locusOfFocus)
        debug.println(debug.LEVEL_INFO, msg, True)

        if obj and self.isZombie(obj):
            msg = "WEB: Current context obj %s is zombie. Clearing cache." % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            self.clearCachedObjects()

            obj, offset = self.getCaretContext()
            msg = "WEB: Now Current context is: %s, %i" % (obj, offset)
            debug.println(debug.LEVEL_INFO, msg, True)

        line = self.getLineContentsAtOffset(obj, offset, layoutMode, useCache)
        if not (line and line[0]):
            return []

        firstObj, firstOffset = line[0][0], line[0][1]
        msg = "WEB: First context on line is: %s, %i" % (firstObj, firstOffset)
        debug.println(debug.LEVEL_INFO, msg, True)

        skipSpace = not self.elementIsPreformattedText(firstObj)
        obj, offset = self.previousContext(firstObj, firstOffset, skipSpace)
        if not obj and firstObj:
            msg = "WEB: Previous context is: %s, %i. Trying again." % (obj, offset)
            debug.println(debug.LEVEL_INFO, msg, True)
            self.clearCachedObjects()
            obj, offset = self.previousContext(firstObj, firstOffset, skipSpace)

        msg = "WEB: Previous context is: %s, %i" % (obj, offset)
        debug.println(debug.LEVEL_INFO, msg, True)

        contents = self.getLineContentsAtOffset(obj, offset, layoutMode, useCache)
        if not contents:
            msg = "WEB: Could not get line contents for %s, %i" % (obj, offset)
            debug.println(debug.LEVEL_INFO, msg, True)
            return []

        if line == contents:
            obj, offset = self.previousContext(obj, offset, True)
            msg = "WEB: Got same line. Trying again with %s, %i" % (obj, offset)
            debug.println(debug.LEVEL_INFO, msg, True)
            contents = self.getLineContentsAtOffset(obj, offset, layoutMode, useCache)

        if line == contents:
            start, end = self.getHyperlinkRange(obj)
            msg = "WEB: Got same line. %s has range in %s of %i-%i" % (obj, obj.parent, start, end)
            debug.println(debug.LEVEL_INFO, msg, True)
            if start >= 0:
                obj, offset = self.previousContext(obj.parent, start, True)
                msg = "WEB: Trying again with %s, %i" % (obj, offset)
                debug.println(debug.LEVEL_INFO, msg, True)
                contents = self.getLineContentsAtOffset(obj, offset, layoutMode, useCache)

        return contents

    def getNextLineContents(self, obj=None, offset=-1, layoutMode=None, useCache=True):
        if obj is None:
            obj, offset = self.getCaretContext()

        msg = "WEB: Current context is: %s, %i (focus: %s)" \
              % (obj, offset, orca_state.locusOfFocus)
        debug.println(debug.LEVEL_INFO, msg, True)

        if obj and self.isZombie(obj):
            msg = "WEB: Current context obj %s is zombie. Clearing cache." % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            self.clearCachedObjects()

            obj, offset = self.getCaretContext()
            msg = "WEB: Now Current context is: %s, %i" % (obj, offset)
            debug.println(debug.LEVEL_INFO, msg, True)

        line = self.getLineContentsAtOffset(obj, offset, layoutMode, useCache)
        if not (line and line[0]):
            return []

        lastObj, lastOffset = line[-1][0], line[-1][2] - 1
        math = self.getMathAncestor(lastObj)
        if math:
            lastObj, lastOffset = self.lastContext(math)

        msg = "WEB: Last context on line is: %s, %i" % (lastObj, lastOffset)
        debug.println(debug.LEVEL_INFO, msg, True)

        skipSpace = not self.elementIsPreformattedText(lastObj)
        obj, offset = self.nextContext(lastObj, lastOffset, skipSpace)
        if not obj and lastObj:
            msg = "WEB: Next context is: %s, %i. Trying again." % (obj, offset)
            debug.println(debug.LEVEL_INFO, msg, True)
            self.clearCachedObjects()
            obj, offset = self.nextContext(lastObj, lastOffset, skipSpace)

        msg = "WEB: Next context is: %s, %i" % (obj, offset)
        debug.println(debug.LEVEL_INFO, msg, True)

        contents = self.getLineContentsAtOffset(obj, offset, layoutMode, useCache)
        if line == contents:
            obj, offset = self.nextContext(obj, offset, True)
            msg = "WEB: Got same line. Trying again with %s, %i" % (obj, offset)
            debug.println(debug.LEVEL_INFO, msg, True)
            contents = self.getLineContentsAtOffset(obj, offset, layoutMode, useCache)

        if line == contents:
            start, end = self.getHyperlinkRange(obj)
            msg = "WEB: Got same line. %s has range in %s of %i-%i" % (obj, obj.parent, start, end)
            debug.println(debug.LEVEL_INFO, msg, True)
            if end >= 0:
                obj, offset = self.nextContext(obj.parent, end, True)
                msg = "WEB: Trying again with %s, %i" % (obj, offset)
                debug.println(debug.LEVEL_INFO, msg, True)
                contents = self.getLineContentsAtOffset(obj, offset, layoutMode, useCache)

        if not contents:
            msg = "WEB: Could not get line contents for %s, %i" % (obj, offset)
            debug.println(debug.LEVEL_INFO, msg, True)
            return []

        return contents

    def updateCachedTextSelection(self, obj):
        if not self.inDocumentContent(obj):
            super().updateCachedTextSelection(obj)
            return

        if self.hasPresentableText(obj):
            super().updateCachedTextSelection(obj)

    def handleTextSelectionChange(self, obj, speakMessage=True):
        if not self.inDocumentContent(obj):
            return super().handleTextSelectionChange(obj)

        oldStart, oldEnd = self._script.pointOfReference.get('selectionAnchorAndFocus', (None, None))
        start, end = self._getSelectionAnchorAndFocus(obj)
        self._script.pointOfReference['selectionAnchorAndFocus'] = (start, end)

        def _cmp(obj1, obj2):
            return self.pathComparison(pyatspi.getPath(obj1), pyatspi.getPath(obj2))

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
               and pyatspi.findAncestor(descendant, lambda x: x in descendants):
                super().updateCachedTextSelection(descendant)
            else:
                super().handleTextSelectionChange(descendant, speakMessage)

        return True

    def inPDFViewer(self, obj=None):
        uri = self.documentFrameURI()
        return uri.lower().endswith(".pdf")

    def inTopLevelWebApp(self, obj=None):
        if not obj:
            obj = orca_state.locusOfFocus

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
        try:
            role = obj.getRole()
        except:
            msg = "WEB: Exception getting role for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if role == pyatspi.ROLE_EMBEDDED and not self.getDocumentForObject(obj.parent):
            uri = self.documentFrameURI()
            rv = bool(uri and uri.startswith("http"))
            msg = "WEB: %s is top-level web application: %s (URI: %s)" % (obj, rv, uri)
            debug.println(debug.LEVEL_INFO, msg, True)
            return rv

        return False

    def forceBrowseModeForWebAppDescendant(self, obj):
        if not self.isWebAppDescendant(obj):
            return False

        role = obj.getRole()
        if role == pyatspi.ROLE_TOOL_TIP:
            return obj.getState().contains(pyatspi.STATE_FOCUSED)

        if role == pyatspi.ROLE_DOCUMENT_WEB:
            return not self.isFocusModeWidget(obj)

        return False

    def isFocusModeWidget(self, obj):
        try:
            role = obj.getRole()
            state = obj.getState()
        except:
            msg = "WEB: Exception getting role and state for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if state.contains(pyatspi.STATE_EDITABLE):
            msg = "WEB: %s is focus mode widget because it's editable" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if state.contains(pyatspi.STATE_EXPANDABLE) and state.contains(pyatspi.STATE_FOCUSABLE):
            msg = "WEB: %s is focus mode widget because it's expandable and focusable" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        alwaysFocusModeRoles = [pyatspi.ROLE_COMBO_BOX,
                                pyatspi.ROLE_ENTRY,
                                pyatspi.ROLE_LIST_BOX,
                                pyatspi.ROLE_MENU,
                                pyatspi.ROLE_MENU_ITEM,
                                pyatspi.ROLE_CHECK_MENU_ITEM,
                                pyatspi.ROLE_RADIO_MENU_ITEM,
                                pyatspi.ROLE_PAGE_TAB,
                                pyatspi.ROLE_PASSWORD_TEXT,
                                pyatspi.ROLE_PROGRESS_BAR,
                                pyatspi.ROLE_SLIDER,
                                pyatspi.ROLE_SPIN_BUTTON,
                                pyatspi.ROLE_TOOL_BAR,
                                pyatspi.ROLE_TREE_ITEM,
                                pyatspi.ROLE_TREE_TABLE,
                                pyatspi.ROLE_TREE]

        if role in alwaysFocusModeRoles:
            msg = "WEB: %s is focus mode widget due to its role" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if role in [pyatspi.ROLE_TABLE_CELL, pyatspi.ROLE_TABLE] \
           and self.isLayoutOnly(self.getTable(obj)):
            msg = "WEB: %s is not focus mode widget because it's layout only" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if role == pyatspi.ROLE_LIST_ITEM:
            rv = pyatspi.findAncestor(obj, lambda x: x and x.getRole() == pyatspi.ROLE_LIST_BOX)
            if rv:
                msg = "WEB: %s is focus mode widget because it's a listbox descendant" % obj
                debug.println(debug.LEVEL_INFO, msg, True)
            return rv

        if self.isButtonWithPopup(obj):
            msg = "WEB: %s is focus mode widget because it's a button with popup" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        focusModeRoles = [pyatspi.ROLE_EMBEDDED,
                          pyatspi.ROLE_TABLE_CELL,
                          pyatspi.ROLE_TABLE]

        if role in focusModeRoles \
           and not self.isTextBlockElement(obj) \
           and not self.hasNameAndActionAndNoUsefulChildren(obj) \
           and not self.inPDFViewer(obj):
            msg = "WEB: %s is focus mode widget based on presumed functionality" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if self.isGridDescendant(obj):
            msg = "WEB: %s is focus mode widget because it's a grid descendant" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if self.isMenuDescendant(obj):
            msg = "WEB: %s is focus mode widget because it's a menu descendant" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if self.isToolBarDescendant(obj):
            msg = "WEB: %s is focus mode widget because it's a toolbar descendant" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        if self.isContentEditableWithEmbeddedObjects(obj):
            msg = "WEB: %s is focus mode widget because it's content editable" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        return False

    def _cellRoles(self):
        roles = [pyatspi.ROLE_TABLE_CELL,
                 pyatspi.ROLE_TABLE_COLUMN_HEADER,
                 pyatspi.ROLE_TABLE_ROW_HEADER,
                 pyatspi.ROLE_ROW_HEADER,
                 pyatspi.ROLE_COLUMN_HEADER]

        return roles

    def _textBlockElementRoles(self):
        roles = [pyatspi.ROLE_ARTICLE,
                 pyatspi.ROLE_CAPTION,
                 pyatspi.ROLE_COLUMN_HEADER,
                 pyatspi.ROLE_COMMENT,
                 pyatspi.ROLE_DEFINITION,
                 pyatspi.ROLE_DESCRIPTION_LIST,
                 pyatspi.ROLE_DESCRIPTION_TERM,
                 pyatspi.ROLE_DESCRIPTION_VALUE,
                 pyatspi.ROLE_DOCUMENT_FRAME,
                 pyatspi.ROLE_DOCUMENT_WEB,
                 pyatspi.ROLE_FOOTER,
                 pyatspi.ROLE_FORM,
                 pyatspi.ROLE_HEADING,
                 pyatspi.ROLE_LIST,
                 pyatspi.ROLE_LIST_ITEM,
                 pyatspi.ROLE_PARAGRAPH,
                 pyatspi.ROLE_ROW_HEADER,
                 pyatspi.ROLE_SECTION,
                 pyatspi.ROLE_STATIC,
                 pyatspi.ROLE_TEXT,
                 pyatspi.ROLE_TABLE_CELL]

        # Remove this check when we bump dependencies to 2.34
        try:
            roles.append(pyatspi.ROLE_CONTENT_DELETION)
            roles.append(pyatspi.ROLE_CONTENT_INSERTION)
        except:
            pass

        # Remove this check when we bump dependencies to 2.36
        try:
            roles.append(pyatspi.ROLE_MARK)
            roles.append(pyatspi.ROLE_SUGGESTION)
        except:
            pass

        return roles

    def mnemonicShortcutAccelerator(self, obj):
        attrs = self.objectAttributes(obj)
        keys = map(lambda x: x.replace("+", " "), attrs.get("keyshortcuts", "").split(" "))
        keys = map(lambda x: x.replace(" ", "+"), map(self.labelFromKeySequence, keys))
        rv = ["", " ".join(keys), ""]
        if list(filter(lambda x: x, rv)):
            return rv

        return super().mnemonicShortcutAccelerator(obj)

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

        try:
            state = obj.getState()
        except:
            msg = "WEB: Exception getting state for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        rv = False
        if state.contains(pyatspi.STATE_FOCUSABLE) and not self.isDocument(obj):
            for child in obj:
                if self.isMathTopLevel(child):
                    rv = True
                    break

        self._isFocusableWithMathChild[hash(obj)] = rv
        return rv

    def isFocusedWithMathChild(self, obj):
        if not self.isFocusableWithMathChild(obj):
            return False

        try:
            state = obj.getState()
        except:
            msg = "WEB: Exception getting state for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        return state.contains(pyatspi.STATE_FOCUSED)

    def isTextBlockElement(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return False

        rv = self._isTextBlockElement.get(hash(obj))
        if rv is not None:
            return rv

        try:
            role = obj.getRole()
            state = obj.getState()
            interfaces = pyatspi.listInterfaces(obj)
        except:
            msg = "WEB: Exception getting role and state for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        textBlockElements = self._textBlockElementRoles()
        if not role in textBlockElements:
            rv = False
        elif not "Text" in interfaces:
            rv = False
        elif state.contains(pyatspi.STATE_EDITABLE):
            rv = False
        elif self.isGridCell(obj):
            rv = False
        elif role in [pyatspi.ROLE_DOCUMENT_FRAME, pyatspi.ROLE_DOCUMENT_WEB]:
            rv = True
        elif self.isCustomImage(obj):
            rv = False
        elif not state.contains(pyatspi.STATE_FOCUSABLE) and not state.contains(pyatspi.STATE_FOCUSED):
            rv = not self.hasNameAndActionAndNoUsefulChildren(obj)
        else:
            rv = False

        self._isTextBlockElement[hash(obj)] = rv
        return rv

    def _advanceCaretInEmptyObject(self, obj):
        role = obj.getRole()
        if role == pyatspi.ROLE_TABLE_CELL and not self.queryNonEmptyText(obj):
            return not self._script._lastCommandWasStructNav

        return True

    def textAtPoint(self, obj, x, y, coordType=None, boundary=None):
        if coordType is None:
            coordType = pyatspi.DESKTOP_COORDS

        if boundary is None:
            boundary = pyatspi.TEXT_BOUNDARY_LINE_START

        string, start, end = super().textAtPoint(obj, x, y, coordType, boundary)
        if string == self.EMBEDDED_OBJECT_CHARACTER:
            child = self.getChildAtOffset(obj, start)
            if child:
                return self.textAtPoint(child, x, y, coordType, boundary)

        return string, start, end

    def _treatAlertsAsDialogs(self):
        return False

    def treatAsDiv(self, obj, offset=None):
        if not (obj and self.inDocumentContent(obj)):
            return False

        if self.isDescriptionList(obj):
            return False

        try:
            role = obj.getRole()
            childCount = obj.childCount
        except:
            msg = "WEB: Exception getting role and childCount for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if role == pyatspi.ROLE_LIST and offset is not None:
            string = self.substring(obj, offset, offset + 1)
            if string and string != self.EMBEDDED_OBJECT_CHARACTER:
                return True

        if role == pyatspi.ROLE_PANEL and not childCount:
            return True

        rv = self._treatAsDiv.get(hash(obj))
        if rv is not None:
            return rv

        validRoles = self._validChildRoles.get(role)
        if validRoles:
            if not childCount:
                rv = True
            else:
                rv = bool([x for x in obj if x and x.getRole() not in validRoles])

        if not rv:
            validRoles = self._validChildRoles.get(obj.parent)
            if validRoles:
                rv = bool([x for x in obj.parent if x and x.getRole() not in validRoles])

        self._treatAsDiv[hash(obj)] = rv
        return rv

    def isAriaAlert(self, obj):
        return 'alert' in self._getXMLRoles(obj)

    def isBlockquote(self, obj):
        if super().isBlockquote(obj):
            return True

        return self._getTag(obj) == 'blockquote'

    def isComment(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return super().isComment(obj)

        if obj.getRole() == pyatspi.ROLE_COMMENT:
            return True

        return 'comment' in self._getXMLRoles(obj)

    def isContentDeletion(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return super().isContentDeletion(obj)

        # Remove this check when we bump dependencies to 2.34
        try:
            if obj.getRole() == pyatspi.ROLE_CONTENT_DELETION:
                return True
        except:
            pass

        return 'deletion' in self._getXMLRoles(obj) or 'del' == self._getTag(obj)

    def isContentError(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return super().isContentError(obj)

        if obj.getRole() not in self._textBlockElementRoles():
            return False

        return obj.getState().contains(pyatspi.STATE_INVALID_ENTRY)

    def isContentInsertion(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return super().isContentInsertion(obj)

        # Remove this check when we bump dependencies to 2.34
        try:
            if obj.getRole() == pyatspi.ROLE_CONTENT_INSERTION:
                return True
        except:
            pass

        return 'insertion' in self._getXMLRoles(obj) or 'ins' == self._getTag(obj)

    def isContentMarked(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return super().isContentMarked(obj)

        # Remove this check when we bump dependencies to 2.36
        try:
            if obj.getRole() == pyatspi.ROLE_MARK:
                return True
        except:
            pass

        return 'mark' in self._getXMLRoles(obj) or 'mark' == self._getTag(obj)

    def isContentSuggestion(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return super().isContentSuggestion(obj)

        # Remove this check when we bump dependencies to 2.36
        try:
            if obj.getRole() == pyatspi.ROLE_SUGGESTION:
                return True
        except:
            pass

        return 'suggestion' in self._getXMLRoles(obj)

    def isCustomElement(self, obj):
        tag = self._getTag(obj)
        return tag and '-' in tag

    def isInlineIframe(self, obj):
        if not (obj and obj.getRole() == pyatspi.ROLE_INTERNAL_FRAME):
            return False

        displayStyle = self._getDisplayStyle(obj)
        if "inline" not in displayStyle:
            return False

        return self.documentForObject(obj) is not None

    def isInlineIframeDescendant(self, obj):
        if not obj:
            return False

        rv = self._isInlineIframeDescendant.get(hash(obj))
        if rv is not None:
            return rv

        ancestor = pyatspi.findAncestor(obj, self.isInlineIframe)
        rv = ancestor is not None
        self._isInlineIframeDescendant[hash(obj)] = rv
        return rv

    def isInlineSuggestion(self, obj):
        if not self.isContentSuggestion(obj):
            return False

        displayStyle = self._getDisplayStyle(obj)
        return "inline" in displayStyle

    def isFirstItemInInlineContentSuggestion(self, obj):
        suggestion = pyatspi.findAncestor(obj, self.isInlineSuggestion)
        if not (suggestion and suggestion.childCount):
            return False

        return suggestion[0] == obj

    def isLastItemInInlineContentSuggestion(self, obj):
        suggestion = pyatspi.findAncestor(obj, self.isInlineSuggestion)
        if not (suggestion and suggestion.childCount):
            return False

        return suggestion[-1] == obj

    def speakMathSymbolNames(self, obj=None):
        obj = obj or orca_state.locusOfFocus
        return self.isMath(obj)

    def isInMath(self):
        return self.isMath(orca_state.locusOfFocus)

    def isMath(self, obj):
        tag = self._getTag(obj)
        rv = tag in ['math',
                     'maction',
                     'maligngroup',
                     'malignmark',
                     'menclose',
                     'merror',
                     'mfenced',
                     'mfrac',
                     'mglyph',
                     'mi',
                     'mlabeledtr',
                     'mlongdiv',
                     'mmultiscripts',
                     'mn',
                     'mo',
                     'mover',
                     'mpadded',
                     'mphantom',
                     'mprescripts',
                     'mroot',
                     'mrow',
                     'ms',
                     'mscarries',
                     'mscarry',
                     'msgroup',
                     'msline',
                     'mspace',
                     'msqrt',
                     'msrow',
                     'mstack',
                     'mstyle',
                     'msub',
                     'msup',
                     'msubsup',
                     'mtable',
                     'mtd',
                     'mtext',
                     'mtr',
                     'munder',
                     'munderover']

        return rv

    def isNoneElement(self, obj):
        return self._getTag(obj) == 'none'

    def isMathLayoutOnly(self, obj):
        return self._getTag(obj) in ['mrow', 'mstyle', 'merror', 'mpadded']

    def isMathMultiline(self, obj):
        return self._getTag(obj) in ['mtable', 'mstack', 'mlongdiv']

    def isMathEnclose(self, obj):
        return self._getTag(obj) == 'menclose'

    def isMathFenced(self, obj):
        return self._getTag(obj) == 'mfenced'

    def isMathFractionWithoutBar(self, obj):
        try:
            role = obj.getRole()
        except:
            msg = "ERROR: Exception getting role for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)

        if role != pyatspi.ROLE_MATH_FRACTION:
            return False

        attrs = self.objectAttributes(obj)
        linethickness = attrs.get('linethickness')
        if not linethickness:
            return False

        for char in linethickness:
            if char.isnumeric() and char != '0':
                return False

        return True

    def isMathPhantom(self, obj):
        return self._getTag(obj) == 'mphantom'

    def isMathMultiScript(self, obj):
        return self._getTag(obj) == 'mmultiscripts'

    def _isMathPrePostScriptSeparator(self, obj):
        return self._getTag(obj) == 'mprescripts'

    def isMathSubOrSuperScript(self, obj):
        return self._getTag(obj) in ['msub', 'msup', 'msubsup']

    def isMathTable(self, obj):
        return self._getTag(obj) == 'mtable'

    def isMathTableRow(self, obj):
        return self._getTag(obj) in ['mtr', 'mlabeledtr']

    def isMathTableCell(self, obj):
        return self._getTag(obj) == 'mtd'

    def isMathUnderOrOverScript(self, obj):
        return self._getTag(obj) in ['mover', 'munder', 'munderover']

    def _isMathSubElement(self, obj):
        return self._getTag(obj) == 'msub'

    def _isMathSupElement(self, obj):
        return self._getTag(obj) == 'msup'

    def _isMathSubsupElement(self, obj):
        return self._getTag(obj) == 'msubsup'

    def _isMathUnderElement(self, obj):
        return self._getTag(obj) == 'munder'

    def _isMathOverElement(self, obj):
        return self._getTag(obj) == 'mover'

    def _isMathUnderOverElement(self, obj):
        return self._getTag(obj) == 'munderover'

    def isMathSquareRoot(self, obj):
        return self._getTag(obj) == 'msqrt'

    def isMathToken(self, obj):
        return self._getTag(obj) in ['mi', 'mn', 'mo', 'mtext', 'ms', 'mspace']

    def isMathTopLevel(self, obj):
        return obj.getRole() == pyatspi.ROLE_MATH

    def getMathAncestor(self, obj):
        if not self.isMath(obj):
            return None

        if self.isMathTopLevel(obj):
            return obj

        return pyatspi.findAncestor(obj, self.isMathTopLevel)

    def getMathDenominator(self, obj):
        try:
            return obj[1]
        except:
            pass

        return None

    def getMathNumerator(self, obj):
        try:
            return obj[0]
        except:
            pass

        return None

    def getMathRootBase(self, obj):
        if self.isMathSquareRoot(obj):
            return obj

        try:
            return obj[0]
        except:
            pass

        return None

    def getMathRootIndex(self, obj):
        try:
            return obj[1]
        except:
            pass

        return None

    def getMathScriptBase(self, obj):
        if self.isMathSubOrSuperScript(obj) \
           or self.isMathUnderOrOverScript(obj) \
           or self.isMathMultiScript(obj):
            return obj[0]

        return None

    def getMathScriptSubscript(self, obj):
        if self._isMathSubElement(obj) or self._isMathSubsupElement(obj):
            return obj[1]

        return None

    def getMathScriptSuperscript(self, obj):
        if self._isMathSupElement(obj):
            return obj[1]

        if self._isMathSubsupElement(obj):
            return obj[2]

        return None

    def getMathScriptUnderscript(self, obj):
        if self._isMathUnderElement(obj) or self._isMathUnderOverElement(obj):
            return obj[1]

        return None

    def getMathScriptOverscript(self, obj):
        if self._isMathOverElement(obj):
            return obj[1]

        if self._isMathUnderOverElement(obj):
            return obj[2]

        return None

    def _getMathPrePostScriptSeparator(self, obj):
        for child in obj:
            if self._isMathPrePostScriptSeparator(child):
                return child

        return None

    def getMathPrescripts(self, obj):
        separator = self._getMathPrePostScriptSeparator(obj)
        if not separator:
            return []

        index = separator.getIndexInParent()
        return [obj[i] for i in range(index+1, obj.childCount)]

    def getMathPostscripts(self, obj):
        separator = self._getMathPrePostScriptSeparator(obj)
        if separator:
            index = separator.getIndexInParent()
        else:
            index = obj.childCount

        return [obj[i] for i in range(1, index)]

    def getMathEnclosures(self, obj):
        if not self.isMathEnclose(obj):
            return []

        attrs = self.objectAttributes(obj)
        return attrs.get('notation', 'longdiv').split()

    def getMathFencedSeparators(self, obj):
        if not self.isMathFenced(obj):
            return ['']

        attrs = self.objectAttributes(obj)
        return list(attrs.get('separators', ','))

    def getMathFences(self, obj):
        if not self.isMathFenced(obj):
            return ['', '']

        attrs = self.objectAttributes(obj)
        return [attrs.get('open', '('), attrs.get('close', ')')]

    def getMathNestingLevel(self, obj, test=None):
        rv = self._mathNestingLevel.get(hash(obj))
        if rv is not None:
            return rv

        if not test:
            test = lambda x: self._getTag(x) == self._getTag(obj)

        rv = -1
        ancestor = obj
        while ancestor:
            ancestor = pyatspi.findAncestor(ancestor, test)
            rv += 1

        self._mathNestingLevel[hash(obj)] = rv
        return rv

    def filterContentsForPresentation(self, contents, inferLabels=False):
        def _include(x):
            obj, start, end, string = x
            if not obj or self.isDead(obj):
                return False

            rv = self._shouldFilter.get(hash(obj))
            if rv is not None:
                return rv

            displayedText = string or obj.name
            rv = True
            if ((self.isTextBlockElement(obj) or self.isLink(obj)) and not displayedText) \
               or (self.isContentEditableWithEmbeddedObjects(obj) and not string.strip()) \
               or self.isEmptyAnchor(obj) \
               or (self.hasNoSize(obj) and not displayedText) \
               or self.isHidden(obj) \
               or self.isOffScreenLabel(obj) \
               or self.isUselessImage(obj) \
               or self.isErrorForContents(obj, contents) \
               or self.isLabellingContents(obj, contents):
                rv = False
            elif obj.getRole() == pyatspi.ROLE_TABLE_ROW:
                rv = self.hasExplicitName(obj)
            else:
                widget = self.isInferredLabelForContents(x, contents)
                alwaysFilter = [pyatspi.ROLE_RADIO_BUTTON, pyatspi.ROLE_CHECK_BOX]
                if widget and (inferLabels or widget.getRole() in alwaysFilter):
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

    def supportsSelectionAndTable(self, obj):
        interfaces = pyatspi.listInterfaces(obj)
        return 'Table' in interfaces and 'Selection' in interfaces

    def isGridDescendant(self, obj):
        if not obj:
            return False

        rv = self._isGridDescendant.get(hash(obj))
        if rv is not None:
            return rv

        rv = pyatspi.findAncestor(obj, self.supportsSelectionAndTable) is not None
        self._isGridDescendant[hash(obj)] = rv
        return rv

    def isSorted(self, obj):
        attrs = self.objectAttributes(obj, False)
        return not attrs.get("sort") in ("none", None)

    def isAscending(self, obj):
        attrs = self.objectAttributes(obj, False)
        return attrs.get("sort") == "ascending"

    def isDescending(self, obj):
        attrs = self.objectAttributes(obj, False)
        return attrs.get("sort") == "descending"

    def _rowAndColumnIndices(self, obj):
        rowindex = colindex = None

        attrs = self.objectAttributes(obj)
        rowindex = attrs.get('rowindex')
        colindex = attrs.get('colindex')
        if rowindex is not None and colindex is not None:
            return rowindex, colindex

        isRow = lambda x: x and x.getRole() == pyatspi.ROLE_TABLE_ROW
        row = pyatspi.findAncestor(obj, isRow)
        if not row:
            return rowindex, colindex

        attrs = self.objectAttributes(row)
        rowindex = attrs.get('rowindex', rowindex)
        colindex = attrs.get('colindex', colindex)
        return rowindex, colindex

    def isCellWithNameFromHeader(self, obj):
        role = obj.getRole()
        if role != pyatspi.ROLE_TABLE_CELL:
            return False

        header = self.columnHeaderForCell(obj)
        if header and header.name and header.name == obj.name:
            return True

        header = self.rowHeaderForCell(obj)
        if header and header.name and header.name == obj.name:
            return True

        return False

    def labelForCellCoordinates(self, obj):
        attrs = self.objectAttributes(obj)

        # The ARIA feature is still in the process of being discussed.
        collabel = attrs.get('colindextext', attrs.get('coltext'))
        rowlabel = attrs.get('rowindextext', attrs.get('rowtext'))
        if collabel is not None and rowlabel is not None:
            return '%s%s' % (collabel, rowlabel)

        isRow = lambda x: x and x.getRole() == pyatspi.ROLE_TABLE_ROW
        row = pyatspi.findAncestor(obj, isRow)
        if not row:
            return ''

        attrs = self.objectAttributes(row)
        collabel = attrs.get('colindextext', attrs.get('coltext', collabel))
        rowlabel = attrs.get('rowindextext', attrs.get('rowtext', rowlabel))
        if collabel is not None and rowlabel is not None:
            return '%s%s' % (collabel, rowlabel)

        return ''

    def coordinatesForCell(self, obj, preferAttribute=True, findCellAncestor=False):
        roles = [pyatspi.ROLE_TABLE_CELL,
                 pyatspi.ROLE_TABLE_COLUMN_HEADER,
                 pyatspi.ROLE_TABLE_ROW_HEADER,
                 pyatspi.ROLE_COLUMN_HEADER,
                 pyatspi.ROLE_ROW_HEADER]
        if not (obj and obj.getRole() in roles):
            if not findCellAncestor:
                return -1, -1

            cell = pyatspi.findAncestor(obj, lambda x: x and x.getRole() in roles)
            return self.coordinatesForCell(cell, preferAttribute, False)

        if preferAttribute:
            rowindex, colindex = self._rowAndColumnIndices(obj)
            if rowindex is not None and colindex is not None:
                return int(rowindex) - 1, int(colindex) - 1

        return super().coordinatesForCell(obj, preferAttribute)

    def rowAndColumnCount(self, obj, preferAttribute=True):
        rows, cols = super().rowAndColumnCount(obj)
        if not preferAttribute:
            return rows, cols

        attrs = self.objectAttributes(obj)
        rows = attrs.get('rowcount', rows)
        cols = attrs.get('colcount', cols)
        return int(rows), int(cols)

    def shouldReadFullRow(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return super().shouldReadFullRow(obj)

        if not super().shouldReadFullRow(obj):
            return False

        if self.isGridDescendant(obj):
            return not self._script.inFocusMode()

        if self.lastInputEventWasLineNav():
            return False

        if self.lastInputEventWasMouseButton():
            return False

        return True

    def isEntryDescendant(self, obj):
        if not obj:
            return False

        rv = self._isEntryDescendant.get(hash(obj))
        if rv is not None:
            return rv

        isEntry = lambda x: x and x.getRole() == pyatspi.ROLE_ENTRY
        rv = pyatspi.findAncestor(obj, isEntry) is not None
        self._isEntryDescendant[hash(obj)] = rv
        return rv

    def isLabelDescendant(self, obj):
        if not obj:
            return False

        rv = self._isLabelDescendant.get(hash(obj))
        if rv is not None:
            return rv

        isLabel = lambda x: x and x.getRole() in [pyatspi.ROLE_LABEL, pyatspi.ROLE_CAPTION]
        rv = pyatspi.findAncestor(obj, isLabel) is not None
        self._isLabelDescendant[hash(obj)] = rv
        return rv

    def isMenuInCollapsedSelectElement(self, obj):
        return False

    def isMenuDescendant(self, obj):
        if not obj:
            return False

        rv = self._isMenuDescendant.get(hash(obj))
        if rv is not None:
            return rv

        isMenu = lambda x: x and x.getRole() == pyatspi.ROLE_MENU
        rv = pyatspi.findAncestor(obj, isMenu) is not None
        self._isMenuDescendant[hash(obj)] = rv
        return rv

    def isNavigableToolTipDescendant(self, obj):
        if not obj:
            return False

        rv = self._isNavigableToolTipDescendant.get(hash(obj))
        if rv is not None:
            return rv

        isToolTip = lambda x: x and x.getRole() == pyatspi.ROLE_TOOL_TIP
        if isToolTip(obj):
            ancestor = obj
        else:
            ancestor = pyatspi.findAncestor(obj, isToolTip)
        rv = ancestor and not self.isNonNavigablePopup(ancestor)
        self._isNavigableToolTipDescendant[hash(obj)] = rv
        return rv

    def isTime(self, obj):
        return 'time' in self._getXMLRoles(obj) or 'time' == self._getTag(obj)

    def isToolBarDescendant(self, obj):
        if not obj:
            return False

        rv = self._isToolBarDescendant.get(hash(obj))
        if rv is not None:
            return rv

        isToolBar = lambda x: x and x.getRole() == pyatspi.ROLE_TOOL_BAR
        rv = pyatspi.findAncestor(obj, isToolBar) is not None
        self._isToolBarDescendant[hash(obj)] = rv
        return rv

    def isWebAppDescendant(self, obj):
        if not obj:
            return False

        rv = self._isWebAppDescendant.get(hash(obj))
        if rv is not None:
            return rv

        isEmbedded = lambda x: x and x.getRole() == pyatspi.ROLE_EMBEDDED
        rv = pyatspi.findAncestor(obj, isEmbedded) is not None
        self._isWebAppDescendant[hash(obj)] = rv
        return rv

    def isLayoutOnly(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return super().isLayoutOnly(obj)

        rv = self._isLayoutOnly.get(hash(obj))
        if rv is not None:
            if rv:
                msg = "WEB: %s is deemed to be layout only" % obj
                debug.println(debug.LEVEL_INFO, msg, True)
            return rv

        try:
            role = obj.getRole()
            state = obj.getState()
        except:
            msg = "ERROR: Exception getting role and state for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if role == pyatspi.ROLE_LIST:
            rv = self.treatAsDiv(obj)
        elif self.isDescriptionList(obj):
            rv = False
        elif self.isDescriptionListTerm(obj):
            rv = False
        elif self.isDescriptionListDescription(obj):
            rv = False
        elif self.isMath(obj):
            rv = False
        elif self.isLandmark(obj):
            rv = False
        elif self.isContentDeletion(obj):
            rv = False
        elif self.isContentInsertion(obj):
            rv = False
        elif self.isContentMarked(obj):
            rv = False
        elif self.isContentSuggestion(obj):
            rv = False
        elif self.isDPub(obj):
            rv = False
        elif self.isFeed(obj):
            rv = False
        elif self.isFigure(obj):
            rv = False
        elif self.isGrid(obj):
            rv = False
        elif role in [pyatspi.ROLE_COLUMN_HEADER, pyatspi.ROLE_ROW_HEADER]:
            rv = False
        elif role == pyatspi.ROLE_SEPARATOR:
            rv = False
        elif role == pyatspi.ROLE_PANEL:
            rv = not self.hasExplicitName(obj)
        elif role == pyatspi.ROLE_TABLE_ROW and not state.contains(pyatspi.STATE_EXPANDABLE):
            rv = not self.hasExplicitName(obj)
        elif self.isCustomImage(obj):
            rv = False
        else:
            rv = super().isLayoutOnly(obj)

        if rv:
            msg = "WEB: %s is deemed to be layout only" % obj
            debug.println(debug.LEVEL_INFO, msg, True)

        self._isLayoutOnly[hash(obj)] = rv
        return rv

    def elementIsPreformattedText(self, obj):
        if self._getTag(obj) in ["pre", "code"]:
            return True

        if "code" in self._getXMLRoles(obj):
            return True

        return False

    def elementLinesAreSingleWords(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return False

        if self.elementIsPreformattedText(obj):
            return False

        rv = self._elementLinesAreSingleWords.get(hash(obj))
        if rv is not None:
            return rv

        text = self.queryNonEmptyText(obj)
        if not text:
            return False

        try:
            nChars = text.characterCount
        except:
            return False

        if not nChars:
            return False

        # If we have a series of embedded object characters, there's a reasonable chance
        # they'll look like the one-word-per-line CSSified text we're trying to detect.
        # We don't want that false positive. By the same token, the one-word-per-line
        # CSSified text we're trying to detect can have embedded object characters. So
        # if we have more than 30% EOCs, don't use this workaround. (The 30% is based on
        # testing with problematic text.)
        eocs = re.findall(self.EMBEDDED_OBJECT_CHARACTER, text.getText(0, -1))
        if len(eocs)/nChars > 0.3:
            return False

        try:
            obj.clearCache()
            state = obj.getState()
        except:
            msg = "ERROR: Exception getting state for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        tokens = list(filter(lambda x: x, re.split(r"[\s\ufffc]", text.getText(0, -1))))

        # Note: We cannot check for the editable-text interface, because Gecko
        # seems to be exposing that for non-editable things. Thanks Gecko.
        rv = not state.contains(pyatspi.STATE_EDITABLE) and len(tokens) > 1
        if rv:
            boundary = pyatspi.TEXT_BOUNDARY_LINE_START
            i = 0
            while i < nChars:
                string, start, end = text.getTextAtOffset(i, boundary)
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

        text = self.queryNonEmptyText(obj)
        if not text:
            return False

        try:
            nChars = text.characterCount
        except:
            return False

        if not nChars:
            return False

        # If we have a series of embedded object characters, there's a reasonable chance
        # they'll look like the one-char-per-line CSSified text we're trying to detect.
        # We don't want that false positive. By the same token, the one-char-per-line
        # CSSified text we're trying to detect can have embedded object characters. So
        # if we have more than 30% EOCs, don't use this workaround. (The 30% is based on
        # testing with problematic text.)
        eocs = re.findall(self.EMBEDDED_OBJECT_CHARACTER, text.getText(0, -1))
        if len(eocs)/nChars > 0.3:
            return False

        try:
            obj.clearCache()
            state = obj.getState()
        except:
            msg = "ERROR: Exception getting state for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        # Note: We cannot check for the editable-text interface, because Gecko
        # seems to be exposing that for non-editable things. Thanks Gecko.
        rv = not state.contains(pyatspi.STATE_EDITABLE)
        if rv:
            boundary = pyatspi.TEXT_BOUNDARY_LINE_START
            for i in range(nChars):
                char = text.getText(i, i + 1)
                if char.isspace() or char in ["\ufffc", "\ufffd"]:
                    continue

                string, start, end = text.getTextAtOffset(i, boundary)
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
        for target in self.targetsForLabel(obj):
            if pyatspi.findAncestor(target, lambda x: x == obj):
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
        targets = self.labelTargets(obj)
        if targets:
            try:
                text = obj.queryText()
                end = text.characterCount
            except:
                end = 1
            x, y, width, height = self.getExtents(obj, 0, end)
            if x < 0 or y < 0:
                rv = True

        self._isOffScreenLabel[hash(obj)] = rv
        return rv

    def isDetachedDocument(self, obj):
        docRoles = [pyatspi.ROLE_DOCUMENT_FRAME, pyatspi.ROLE_DOCUMENT_WEB]
        if (obj and obj.getRole() in docRoles):
            if obj.parent is None or self.isZombie(obj.parent):
                msg = "WEB: %s is a detached document" % obj
                debug.println(debug.LEVEL_INFO, msg, True)
                return True

        return False

    def iframeForDetachedDocument(self, obj, root=None):
        root = root or self.documentFrame()
        isIframe = lambda x: x and x.getRole() == pyatspi.ROLE_INTERNAL_FRAME
        iframes = self.findAllDescendants(root, isIframe)
        for iframe in iframes:
            if obj in iframe:
                # We won't change behavior, but we do want to log all bogosity.
                self._isBrokenChildParentTree(obj, iframe)

                msg = "WEB: Returning %s as iframe parent of detached %s" % (iframe, obj)
                debug.println(debug.LEVEL_INFO, msg, True)
                return iframe

        return None

    def _objectBoundsMightBeBogus(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return super()._objectBoundsMightBeBogus(obj)

        if obj.getRole() != pyatspi.ROLE_LINK or "Text" not in pyatspi.listInterfaces(obj):
            return False

        text = obj.queryText()
        start = list(text.getRangeExtents(0, 1, 0))
        end = list(text.getRangeExtents(text.characterCount - 1, text.characterCount, 0))
        if self.extentsAreOnSameLine(start, end):
            return False

        if not self.hasPresentableText(obj.parent):
            return False

        msg = "WEB: Objects bounds of %s might be bogus" % obj
        debug.println(debug.LEVEL_INFO, msg, True)
        return True

    def _isBrokenChildParentTree(self, child, parent):
        if not (child and parent):
            return False

        try:
            childIsChildOfParent = child in parent
        except:
            msg = "WEB: Exception checking if %s is in %s" % (child, parent)
            debug.println(debug.LEVEL_INFO, msg, True)
            childIsChildOfParent = False
        else:
            msg = "WEB: %s is child of %s: %s" % (child, parent, childIsChildOfParent)
            debug.println(debug.LEVEL_INFO, msg, True)

        try:
            parentIsParentOfChild = child.parent == parent
        except:
            msg = "WEB: Exception getting parent of %s" % child
            debug.println(debug.LEVEL_INFO, msg, True)
            parentIsParentOfChild = False
        else:
            msg = "WEB: %s is parent of %s: %s" % (parent, child, parentIsParentOfChild)
            debug.println(debug.LEVEL_INFO, msg, True)

        if parentIsParentOfChild != childIsChildOfParent:
            msg = "FAIL: The above is broken and likely needs to be fixed by the toolkit."
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        return False

    def targetsForLabel(self, obj):
        isLabel = lambda r: r.getRelationType() == pyatspi.RELATION_LABEL_FOR
        try:
            relations = list(filter(isLabel, obj.getRelationSet()))
        except:
            msg = "WEB: Exception getting relations of %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return []

        if not relations:
            return []

        r = relations[0]
        rv = set([r.getTarget(i) for i in range(r.getNTargets())])

        if obj in rv:
            msg = 'WARNING: %s claims to be a label for itself' % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            rv.remove(obj)

        return list(filter(lambda x: x is not None, rv))

    def labelTargets(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return []

        rv = self._labelTargets.get(hash(obj))
        if rv is not None:
            return rv

        rv = [hash(t) for t in self.targetsForLabel(obj)]
        self._labelTargets[hash(obj)] = rv
        return rv

    def isLinkAncestorOfImageInContents(self, link, contents):
        if not self.isLink(link):
            return False

        for obj, start, end, string in contents:
            if obj.getRole() != pyatspi.ROLE_IMAGE:
                continue
            if pyatspi.findAncestor(obj, lambda x: x == link):
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
        if self._labelTargets.get(hash(obj)) == []:
            return False

        targets = self.targetsForLabel(obj)
        for target in targets:
            if target.getState().contains(pyatspi.STATE_FOCUSABLE):
                return True

        return False

    def isLabellingContents(self, obj, contents=[]):
        if self.isFocusModeWidget(obj):
            return False

        targets = self.labelTargets(obj)
        if not contents:
            return bool(targets) or self.isLabelDescendant(obj)

        for acc, start, end, string in contents:
            if hash(acc) in targets:
                return True

        if not self.isTextBlockElement(obj):
            return False

        if not self.isLabelDescendant(obj):
            return False

        for acc, start, end, string in contents:
            if not self.isLabelDescendant(acc) or self.isTextBlockElement(acc):
                continue

            ancestor = self.commonAncestor(acc, obj)
            if ancestor and ancestor.getRole() in [pyatspi.ROLE_LABEL, pyatspi.ROLE_CAPTION]:
                return True

        return False

    def isAnchor(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return False

        rv = self._isAnchor.get(hash(obj))
        if rv is not None:
            return rv

        rv = False
        if obj.getRole() == pyatspi.ROLE_LINK \
           and not obj.getState().contains(pyatspi.STATE_FOCUSABLE) \
           and not 'jump' in self._getActionNames(obj) \
           and not self._getXMLRoles(obj):
            rv = True

        self._isAnchor[hash(obj)] = rv
        return rv

    def isEmptyAnchor(self, obj):
        if not self.isAnchor(obj):
            return False

        return self.queryNonEmptyText(obj) is None

    def isEmptyToolTip(self, obj):
        return obj and obj.getRole() == pyatspi.ROLE_TOOL_TIP \
            and self.queryNonEmptyText(obj) is None

    def isBrowserUIAlert(self, obj):
        if not (obj and obj.getRole() == pyatspi.ROLE_ALERT):
            return False

        if self.inDocumentContent(obj):
            return False

        return True

    def isTopLevelBrowserUIAlert(self, obj):
        if not self.isBrowserUIAlert(obj):
            return False

        parent = obj.parent
        while parent and self.isLayoutOnly(parent):
            parent = parent.parent

        return parent.getRole() == pyatspi.ROLE_FRAME

    def _getActionNames(self, obj):
        try:
            action = obj.queryAction()
            names = [action.getName(i).lower() for i in range(action.nActions)]
        except NotImplementedError:
            return []
        except:
            msg = "WEB: Exception getting actions for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return []

        return list(filter(lambda x: x, names))

    def isClickableElement(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return False

        rv = self._isClickableElement.get(hash(obj))
        if rv is not None:
            return rv

        if self.labelIsAncestorOfLabelled(obj):
            return False

        rv = False
        if not obj.getState().contains(pyatspi.STATE_FOCUSABLE) \
           and not self.isFocusModeWidget(obj):
            names = self._getActionNames(obj)
            rv = "click" in names

        if rv and not obj.name and "Text" in pyatspi.listInterfaces(obj):
            string = obj.queryText().getText(0, -1)
            if not string.strip():
                rv = obj.getRole() not in [pyatspi.ROLE_STATIC, pyatspi.ROLE_LINK]

        self._isClickableElement[hash(obj)] = rv
        return rv

    def isCodeDescendant(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return super().isCodeDescendant(obj)

        rv = self._isCodeDescendant.get(hash(obj))
        if rv is not None:
            return rv

        rv = pyatspi.findAncestor(obj, self.isCode) is not None
        self._isCodeDescendant[hash(obj)] = rv
        return rv

    def isCode(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return super().isCode(obj)

        return self._getTag(obj) == "code" or "code" in self._getXMLRoles(obj)

    def isDescriptionList(self, obj):
        if super().isDescriptionList(obj):
            return True

        return self._getTag(obj) == "dl"

    def isDescriptionListTerm(self, obj):
        if super().isDescriptionListTerm(obj):
            return True

        return self._getTag(obj) == "dt"

    def isDescriptionListDescription(self, obj):
        if super().isDescriptionListDescription(obj):
            return True

        return self._getTag(obj) == "dd"

    def getComboBoxValue(self, obj):
        attrs = self.objectAttributes(obj, False)
        return attrs.get("valuetext", super().getComboBoxValue(obj))

    def isEditableComboBox(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return super().isEditableComboBox(obj)

        rv = self._isEditableComboBox.get(hash(obj))
        if rv is not None:
            return rv

        try:
            role = obj.getRole()
            state = obj.getState()
        except:
            msg = "ERROR: Exception getting role and state for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        rv = False
        if role == pyatspi.ROLE_COMBO_BOX:
            rv = state.contains(pyatspi.STATE_EDITABLE)

        self._isEditableComboBox[hash(obj)] = rv
        return rv

    def isDPub(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return False

        roles = self._getXMLRoles(obj)
        rv = bool(list(filter(lambda x: x.startswith("doc-"), roles)))
        return rv

    def isDPubAbstract(self, obj):
        return 'doc-abstract' in self._getXMLRoles(obj)

    def isDPubAcknowledgments(self, obj):
        return 'doc-acknowledgments' in self._getXMLRoles(obj)

    def isDPubAfterword(self, obj):
        return 'doc-afterword' in self._getXMLRoles(obj)

    def isDPubAppendix(self, obj):
        return 'doc-appendix' in self._getXMLRoles(obj)

    def isDPubBacklink(self, obj):
        return 'doc-backlink' in self._getXMLRoles(obj)

    def isDPubBiblioref(self, obj):
        return 'doc-biblioref' in self._getXMLRoles(obj)

    def isDPubBibliography(self, obj):
        return 'doc-bibliography' in self._getXMLRoles(obj)

    def isDPubChapter(self, obj):
        return 'doc-chapter' in self._getXMLRoles(obj)

    def isDPubColophon(self, obj):
        return 'doc-colophon' in self._getXMLRoles(obj)

    def isDPubConclusion(self, obj):
        return 'doc-conclusion' in self._getXMLRoles(obj)

    def isDPubCover(self, obj):
        return 'doc-cover' in self._getXMLRoles(obj)

    def isDPubCredit(self, obj):
        return 'doc-credit' in self._getXMLRoles(obj)

    def isDPubCredits(self, obj):
        return 'doc-credits' in self._getXMLRoles(obj)

    def isDPubDedication(self, obj):
        return 'doc-dedication' in self._getXMLRoles(obj)

    def isDPubEndnote(self, obj):
        return 'doc-endnote' in self._getXMLRoles(obj)

    def isDPubEndnotes(self, obj):
        return 'doc-endnotes' in self._getXMLRoles(obj)

    def isDPubEpigraph(self, obj):
        return 'doc-epigraph' in self._getXMLRoles(obj)

    def isDPubEpilogue(self, obj):
        return 'doc-epilogue' in self._getXMLRoles(obj)

    def isDPubErrata(self, obj):
        return 'doc-errata' in self._getXMLRoles(obj)

    def isDPubExample(self, obj):
        return 'doc-example' in self._getXMLRoles(obj)

    def isDPubFootnote(self, obj):
        return 'doc-footnote' in self._getXMLRoles(obj)

    def isDPubForeword(self, obj):
        return 'doc-foreword' in self._getXMLRoles(obj)

    def isDPubGlossary(self, obj):
        return 'doc-glossary' in self._getXMLRoles(obj)

    def isDPubGlossref(self, obj):
        return 'doc-glossref' in self._getXMLRoles(obj)

    def isDPubIndex(self, obj):
        return 'doc-index' in self._getXMLRoles(obj)

    def isDPubIntroduction(self, obj):
        return 'doc-introduction' in self._getXMLRoles(obj)

    def isDPubNoteref(self, obj):
        return 'doc-noteref' in self._getXMLRoles(obj)

    def isDPubPagelist(self, obj):
        return 'doc-pagelist' in self._getXMLRoles(obj)

    def isDPubPagebreak(self, obj):
        return 'doc-pagebreak' in self._getXMLRoles(obj)

    def isDPubPart(self, obj):
        return 'doc-part' in self._getXMLRoles(obj)

    def isDPubPreface(self, obj):
        return 'doc-preface' in self._getXMLRoles(obj)

    def isDPubPrologue(self, obj):
        return 'doc-prologue' in self._getXMLRoles(obj)

    def isDPubPullquote(self, obj):
        return 'doc-pullquote' in self._getXMLRoles(obj)

    def isDPubQna(self, obj):
        return 'doc-qna' in self._getXMLRoles(obj)

    def isDPubSubtitle(self, obj):
        return 'doc-subtitle' in self._getXMLRoles(obj)

    def isDPubToc(self, obj):
        return 'doc-toc' in self._getXMLRoles(obj)

    def isErrorMessage(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return super().isErrorMessage(obj)

        rv = self._isErrorMessage.get(hash(obj))
        if rv is not None:
            return rv

        try:
            relations = obj.getRelationSet()
        except:
            msg = 'ERROR: Exception getting relationset for %s' % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        # Remove this when we bump dependencies to 2.26
        try:
            relationType = pyatspi.RELATION_ERROR_FOR
        except:
            rv = False
        else:
            isMessage = lambda r: r.getRelationType() == relationType
            rv = bool(list(filter(isMessage, relations)))

        self._isErrorMessage[hash(obj)] = rv
        return rv

    def isFakePlaceholderForEntry(self, obj):
        if not (obj and self.inDocumentContent(obj) and obj.parent):
            return False

        if obj.getState().contains(pyatspi.STATE_EDITABLE):
            return False

        entry = pyatspi.findAncestor(obj, lambda x: x and x.getRole() == pyatspi.ROLE_ENTRY)
        if not (entry and entry.name):
            return False

        def _isMatch(x):
            try:
                role = x.getRole()
                string = x.queryText().getText(0, -1).strip()
            except:
                return False
            return role in [pyatspi.ROLE_SECTION, pyatspi.ROLE_STATIC] and entry.name == string

        if _isMatch(obj):
            return True

        return pyatspi.findDescendant(obj, _isMatch) is not None

    def isGrid(self, obj):
        return 'grid' in self._getXMLRoles(obj)

    def isGridCell(self, obj):
        return 'gridcell' in self._getXMLRoles(obj)

    def isInlineListItem(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return False

        rv = self._isInlineListItem.get(hash(obj))
        if rv is not None:
            return rv

        if obj.getRole() != pyatspi.ROLE_LIST_ITEM:
            rv = False
        else:
            displayStyle = self._getDisplayStyle(obj)
            rv = displayStyle and "inline" in displayStyle

        self._isInlineListItem[hash(obj)] = rv
        return rv

    def isBlockListDescendant(self, obj):
        if not self.isListDescendant(obj):
            return False

        return not self.isInlineListDescendant(obj)

    def isListDescendant(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return False

        rv = self._isListDescendant.get(hash(obj))
        if rv is not None:
            return rv

        isList = lambda x: x and x.getRole() == pyatspi.ROLE_LIST
        ancestor = pyatspi.findAncestor(obj, isList)
        rv = ancestor is not None

        self._isListDescendant[hash(obj)] = rv
        return rv

    def isInlineListDescendant(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return False

        rv = self._isInlineListDescendant.get(hash(obj))
        if rv is not None:
            return rv

        if self.isInlineListItem(obj):
            rv = True
        else:
            ancestor = pyatspi.findAncestor(obj, self.isInlineListItem)
            rv = ancestor is not None

        self._isInlineListDescendant[hash(obj)] = rv
        return rv

    def listForInlineListDescendant(self, obj):
        if not self.isInlineListDescendant(obj):
            return None

        isList = lambda x: x and x.getRole() == pyatspi.ROLE_LIST
        return pyatspi.findAncestor(obj, isList)

    def isFeed(self, obj):
        return 'feed' in self._getXMLRoles(obj)

    def isFigure(self, obj):
        return 'figure' in self._getXMLRoles(obj) or self._getTag(obj) == 'figure'

    def isLandmark(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return False

        rv = self._isLandmark.get(hash(obj))
        if rv is not None:
            return rv

        if obj.getRole() == pyatspi.ROLE_LANDMARK:
            rv = True
        elif self.isLandmarkRegion(obj):
            rv = bool(obj.name)
        else:
            roles = self._getXMLRoles(obj)
            rv = bool(list(filter(lambda x: x in self.getLandmarkTypes(), roles)))

        self._isLandmark[hash(obj)] = rv
        return rv

    def isLandmarkWithoutType(self, obj):
        roles = self._getXMLRoles(obj)
        return not roles

    def isLandmarkBanner(self, obj):
        return 'banner' in self._getXMLRoles(obj)

    def isLandmarkComplementary(self, obj):
        return 'complementary' in self._getXMLRoles(obj)

    def isLandmarkContentInfo(self, obj):
        return 'contentinfo' in self._getXMLRoles(obj)

    def isLandmarkForm(self, obj):
        return 'form' in self._getXMLRoles(obj)

    def isLandmarkMain(self, obj):
        return 'main' in self._getXMLRoles(obj)

    def isLandmarkNavigation(self, obj):
        return 'navigation' in self._getXMLRoles(obj)

    def isLandmarkRegion(self, obj):
        return 'region' in self._getXMLRoles(obj)

    def isLandmarkSearch(self, obj):
        return 'search' in self._getXMLRoles(obj)

    def isLiveRegion(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return False

        attrs = self.objectAttributes(obj)
        return 'container-live' in attrs

    def isLink(self, obj):
        if not obj:
            return False

        rv = self._isLink.get(hash(obj))
        if rv is not None:
            return rv

        role = obj.getRole()
        if role == pyatspi.ROLE_LINK and not self.isAnchor(obj):
            rv = True
        elif role == pyatspi.ROLE_STATIC \
           and obj.parent.getRole() == pyatspi.ROLE_LINK \
           and obj.name and obj.name == obj.parent.name:
            rv = True
        else:
            rv = False

        self._isLink[hash(obj)] = rv
        return rv

    def isNonNavigablePopup(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return False

        rv = self._isNonNavigablePopup.get(hash(obj))
        if rv is not None:
            return rv

        rv = obj.getRole() == pyatspi.ROLE_TOOL_TIP \
            and not obj.getState().contains(pyatspi.STATE_FOCUSABLE)

        self._isNonNavigablePopup[hash(obj)] = rv
        return rv

    def hasUselessCanvasDescendant(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return False

        rv = self._hasUselessCanvasDescendant.get(hash(obj))
        if rv is not None:
            return rv

        isCanvas = lambda x: x and x.getRole() == pyatspi.ROLE_CANVAS
        canvases = self.findAllDescendants(obj, isCanvas)
        rv = len(list(filter(self.isUselessImage, canvases))) > 0

        self._hasUselessCanvasDescendant[hash(obj)] = rv
        return rv

    def isTextSubscriptOrSuperscript(self, obj):
        if self.isMath(obj):
            return False

        return obj.getRole() in [pyatspi.ROLE_SUBSCRIPT, pyatspi.ROLE_SUPERSCRIPT]

    def isSwitch(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return super().isSwitch(obj)

        return 'switch' in self._getXMLRoles(obj)

    def isNonNavigableEmbeddedDocument(self, obj):
        rv = self._isNonNavigableEmbeddedDocument.get(hash(obj))
        if rv is not None:
            return rv

        rv = False
        if self.isDocument(obj) and self.getDocumentForObject(obj):
            try:
                name = obj.name
            except:
                rv = True
            else:
                rv = "doubleclick" in name

        self._isNonNavigableEmbeddedDocument[hash(obj)] = rv
        return rv

    def isRedundantSVG(self, obj):
        if self._getTag(obj) != 'svg' or obj.parent.childCount == 1:
            return False

        rv = self._isRedundantSVG.get(hash(obj))
        if rv is not None:
            return rv

        rv = False
        children = [x for x in obj.parent if self._getTag(x) == 'svg']
        if len(children) == obj.parent.childCount:
            sortedChildren = sorted(children, key=functools.cmp_to_key(self.sizeComparison))
            if obj != sortedChildren[-1]:
                objExtents = self.getExtents(obj, 0, -1)
                largestExtents = self.getExtents(sortedChildren[-1], 0, -1)
                rv = self.intersection(objExtents, largestExtents) == tuple(objExtents)

        self._isRedundantSVG[hash(obj)] = rv
        return rv

    def isCustomImage(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return False

        rv = self._isCustomImage.get(hash(obj))
        if rv is not None:
            return rv

        rv = False
        if self.isCustomElement(obj) and self.hasExplicitName(obj) \
           and 'Text' in pyatspi.listInterfaces(obj) \
           and not re.search(r'[^\s\ufffc]', obj.queryText().getText(0, -1)):
            for child in obj:
                if child.getRole() not in [pyatspi.ROLE_IMAGE, pyatspi.ROLE_CANVAS] \
                   and self._getTag(child) != 'svg':
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
        if obj.getRole() not in [pyatspi.ROLE_IMAGE, pyatspi.ROLE_CANVAS] \
           and self._getTag(obj) != 'svg':
            rv = False
        if rv and (obj.name or obj.description or self.hasLongDesc(obj)):
            rv = False
        if rv and (self.isClickableElement(obj) and not self.hasExplicitName(obj)):
            rv = False
        if rv and obj.getState().contains(pyatspi.STATE_FOCUSABLE):
            rv = False
        if rv and obj.parent.getRole() == pyatspi.ROLE_LINK and not self.hasExplicitName(obj):
            uri = self.uri(obj.parent)
            if uri and not uri.startswith('javascript'):
                rv = False
        if rv and 'Image' in pyatspi.listInterfaces(obj):
            image = obj.queryImage()
            if image.imageDescription:
                rv = False
            elif not self.hasExplicitName(obj) and not self.isRedundantSVG(obj):
                width, height = image.getImageSize()
                if width > 25 and height > 25:
                    rv = False
        if rv and 'Text' in pyatspi.listInterfaces(obj):
            rv = self.queryNonEmptyText(obj) is None
        if rv and obj.childCount:
            for i in range(min(obj.childCount, 50)):
                if not self.isUselessImage(obj[i]):
                    rv = False
                    break

        self._isUselessImage[hash(obj)] = rv
        return rv

    def hasValidName(self, obj):
        if not (obj and obj.name):
            return False

        if len(obj.name.split()) > 1:
            return True

        parsed = urllib.parse.parse_qs(obj.name)
        if len(parsed) > 2:
            msg = "WEB: name of %s is suspected query string" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if len(obj.name) == 1 and ord(obj.name) in range(0xe000, 0xf8ff):
            msg = "WEB: name of %s is in unicode private use area" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        return True

    def isUselessEmptyElement(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return False

        rv = self._isUselessEmptyElement.get(hash(obj))
        if rv is not None:
            return rv

        try:
            role = obj.getRole()
            state = obj.getState()
            interfaces = pyatspi.listInterfaces(obj)
        except:
            msg = "WEB: Exception getting role, state, and interfaces for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        roles = [pyatspi.ROLE_PARAGRAPH,
                 pyatspi.ROLE_SECTION,
                 pyatspi.ROLE_STATIC,
                 pyatspi.ROLE_TABLE_ROW]

        if role not in roles and not self.isAriaAlert(obj):
            rv = False
        elif state.contains(pyatspi.STATE_FOCUSABLE) or state.contains(pyatspi.STATE_FOCUSED):
            rv = False
        elif state.contains(pyatspi.STATE_EDITABLE):
            rv = False
        elif self.hasValidName(obj) or obj.description or obj.childCount:
            rv = False
        elif "Text" in interfaces and obj.queryText().characterCount \
             and obj.queryText().getText(0, -1) != obj.name:
            rv = False
        elif "Action" in interfaces and self._getActionNames(obj):
            rv = False
        else:
            rv = True

        self._isUselessEmptyElement[hash(obj)] = rv
        return rv

    def isParentOfNullChild(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return False

        rv = self._isParentOfNullChild.get(hash(obj))
        if rv is not None:
            return rv

        rv = False
        try:
            childCount = obj.childCount
        except:
            msg = "WEB: Exception getting childCount for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            childCount = 0
        if childCount and obj[0] is None:
            msg = "ERROR: %s reports %i children, but obj[0] is None" % (obj, childCount)
            debug.println(debug.LEVEL_INFO, msg, True)
            rv = True

        self._isParentOfNullChild[hash(obj)] = rv
        return rv

    def hasExplicitName(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return False

        attrs = self.objectAttributes(obj)
        return attrs.get('explicit-name') == 'true'

    def hasLongDesc(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return False

        rv = self._hasLongDesc.get(hash(obj))
        if rv is not None:
            return rv

        names = self._getActionNames(obj)
        rv = "showlongdesc" in names

        self._hasLongDesc[hash(obj)] = rv
        return rv

    def hasVisibleCaption(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return super().hasVisibleCaption(obj)

        if not (self.isFigure(obj) or "Table" in pyatspi.listInterfaces(obj)):
            return False

        rv = self._hasVisibleCaption.get(hash(obj))
        if rv is not None:
            return rv

        labels = self.labelsForObject(obj)
        pred = lambda x: x and x.getRole() == pyatspi.ROLE_CAPTION and self.isShowingAndVisible(x)
        rv = bool(list(filter(pred, labels)))
        self._hasVisibleCaption[hash(obj)] = rv
        return rv

    def hasDetails(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return super().hasDetails(obj)

        rv = self._hasDetails.get(hash(obj))
        if rv is not None:
            return rv

        try:
            relations = obj.getRelationSet()
        except:
            msg = 'ERROR: Exception getting relationset for %s' % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        rv = False
        relation = filter(lambda x: x.getRelationType() == pyatspi.RELATION_DETAILS, relations)
        for r in relation:
            if r.getNTargets() > 0:
                rv = True
                break

        self._hasDetails[hash(obj)] = rv
        return rv

    def detailsIn(self, obj):
        if not self.hasDetails(obj):
            return []

        try:
            relations = obj.getRelationSet()
        except:
            msg = 'ERROR: Exception getting relationset for %s' % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return []

        rv = []
        relation = filter(lambda x: x.getRelationType() == pyatspi.RELATION_DETAILS, relations)
        for r in relation:
            for i in range(r.getNTargets()):
                rv.append(r.getTarget(i))

        return rv

    def isDetails(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return super().isDetails(obj)

        rv = self._isDetails.get(hash(obj))
        if rv is not None:
            return rv

        try:
            relations = obj.getRelationSet()
        except:
            msg = 'ERROR: Exception getting relationset for %s' % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        rv = False
        relation = filter(lambda x: x.getRelationType() == pyatspi.RELATION_DETAILS_FOR, relations)
        for r in relation:
            if r.getNTargets() > 0:
                rv = True
                break

        self._isDetails[hash(obj)] = rv
        return rv

    def detailsFor(self, obj):
        if not self.isDetails(obj):
            return []

        try:
            relations = obj.getRelationSet()
        except:
            msg = 'ERROR: Exception getting relationset for %s' % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return []

        rv = []
        relation = filter(lambda x: x.getRelationType() == pyatspi.RELATION_DETAILS_FOR, relations)
        for r in relation:
            for i in range(r.getNTargets()):
                rv.append(r.getTarget(i))

        return rv

    def popupType(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return 'false'

        attrs = self.objectAttributes(obj)
        return attrs.get('haspopup', 'false').lower()

    def inferLabelFor(self, obj):
        if not self.shouldInferLabelFor(obj):
            return None, []

        rv = self._inferredLabels.get(hash(obj))
        if rv is not None:
            return rv

        rv = self._script.labelInference.infer(obj, False)
        self._inferredLabels[hash(obj)] = rv
        return rv

    def shouldInferLabelFor(self, obj):
        if not self.inDocumentContent() or self.isWebAppDescendant(obj):
            return False

        rv = self._shouldInferLabelFor.get(hash(obj))
        if rv and not self._script._lastCommandWasCaretNav:
            return not self._script.inSayAll()
        if rv == False:
            return rv

        try:
            role = obj.getRole()
            name = obj.name
        except:
            msg = "WEB: Exception getting role and name for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            rv = False
        else:
            if name:
                rv = False
            elif self._getXMLRoles(obj):
                rv = False
            elif not rv:
                roles =  [pyatspi.ROLE_CHECK_BOX,
                          pyatspi.ROLE_COMBO_BOX,
                          pyatspi.ROLE_ENTRY,
                          pyatspi.ROLE_LIST_BOX,
                          pyatspi.ROLE_PASSWORD_TEXT,
                          pyatspi.ROLE_RADIO_BUTTON]
                rv = role in roles and not self.displayedLabel(obj)

        self._shouldInferLabelFor[hash(obj)] = rv

        # TODO - JD: This is private.
        if self._script._lastCommandWasCaretNav \
           and role not in [pyatspi.ROLE_RADIO_BUTTON, pyatspi.ROLE_CHECK_BOX]:
            return False

        return rv

    def displayedLabel(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return super().displayedLabel(obj)

        rv = self._displayedLabelText.get(hash(obj))
        if rv is not None:
            return rv

        labels = self.labelsForObject(obj)
        strings = [l.name or self.displayedText(l) for l in labels if l is not None]
        rv = " ".join(strings)

        self._displayedLabelText[hash(obj)] = rv
        return rv

    def labelsForObject(self, obj):
        if not obj:
            return []

        rv = self._labelsForObject.get(hash(obj))
        if rv is not None:
            return rv

        rv = super().labelsForObject(obj)
        if not self.inDocumentContent(obj):
            return rv

        self._labelsForObject[hash(obj)] = rv
        return rv

    def isSpinnerEntry(self, obj):
        if not self.inDocumentContent(obj):
            return False

        if not obj.getState().contains(pyatspi.STATE_EDITABLE):
            return False

        if pyatspi.ROLE_SPIN_BUTTON in [obj.getRole(), obj.parent.getRole()]:
            return True

        return False

    def eventIsSpinnerNoise(self, event):
        if not self.isSpinnerEntry(event.source):
            return False

        if event.type.startswith("object:text-changed") \
           or event.type.startswith("object:text-selection-changed"):
            lastKey, mods = self.lastKeyAndModifiers()
            if lastKey in ["Down", "Up"]:
                return True

        return False

    def treatEventAsSpinnerValueChange(self, event):
        if event.type.startswith("object:text-caret-moved") and self.isSpinnerEntry(event.source):
            lastKey, mods = self.lastKeyAndModifiers()
            if lastKey in ["Down", "Up"]:
                obj, offset = self.getCaretContext()
                return event.source == obj

        return False

    def eventIsBrowserUINoise(self, event):
        if self.inDocumentContent(event.source):
            return False

        try:
            role = event.source.getRole()
        except:
            msg = "WEB: Exception getting role for %s" % event.source
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        eType = event.type
        if eType.startswith("object:text-") and self.isSingleLineAutocompleteEntry(event.source):
            lastKey, mods = self.lastKeyAndModifiers()
            return lastKey == "Return"
        if eType.startswith("object:text-") or eType.endswith("accessible-name"):
            return role in [pyatspi.ROLE_STATUS_BAR, pyatspi.ROLE_LABEL]
        if eType.startswith("object:children-changed"):
            return True

        return False

    def eventIsAutocompleteNoise(self, event, documentFrame=None):
        inContent = documentFrame or self.inDocumentContent(event.source)
        if not inContent:
            return False

        isListBoxItem = lambda x: x and x.parent and x.parent.getRole() == pyatspi.ROLE_LIST_BOX
        isMenuItem = lambda x: x and x.parent and x.parent.getRole() == pyatspi.ROLE_MENU
        isComboBoxItem = lambda x: x and x.parent and x.parent.getRole() == pyatspi.ROLE_COMBO_BOX

        if event.source.getState().contains(pyatspi.STATE_EDITABLE) \
           and event.type.startswith("object:text-"):
            obj, offset = self.getCaretContext(documentFrame)
            if isListBoxItem(obj) or isMenuItem(obj):
                return True

            if obj == event.source and isComboBoxItem(obj):
                lastKey, mods = self.lastKeyAndModifiers()
                if lastKey in ["Down", "Up"]:
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
        if not event.type in selection:
            return False

        try:
            focusRole = orca_state.locusOfFocus.getRole()
            focusState = orca_state.locusOfFocus.getState()
        except:
            msg = "WEB: Exception getting role and state for %s" % orca_state.locusOfFocus
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        try:
            role = event.source.getRole()
        except:
            msg = "WEB: Exception getting role for %s" % event.source
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if role in [pyatspi.ROLE_MENU, pyatspi.ROLE_MENU_ITEM] \
           and focusRole == pyatspi.ROLE_ENTRY \
           and focusState.contains(pyatspi.STATE_FOCUSED):
            lastKey, mods = self.lastKeyAndModifiers()
            if lastKey not in ["Down", "Up"]:
                return True

        return False

    def _eventIsBrowserUIAutocompleteTextNoise(self, event):
        if not event.type.startswith("object:text-") \
           or not orca_state.locusOfFocus \
           or not self.isSingleLineAutocompleteEntry(event.source):
            return False

        roles = [pyatspi.ROLE_MENU_ITEM,
                 pyatspi.ROLE_CHECK_MENU_ITEM,
                 pyatspi.ROLE_RADIO_MENU_ITEM,
                 pyatspi.ROLE_LIST_ITEM]

        if orca_state.locusOfFocus.getRole() in roles \
           and orca_state.locusOfFocus.getState().contains(pyatspi.STATE_SELECTABLE):
            lastKey, mods = self.lastKeyAndModifiers()
            return lastKey in ["Down", "Up"]

        return False

    def eventIsBrowserUIPageSwitch(self, event):
        selection = ["object:selection-changed", "object:state-changed:selected"]
        if not event.type in selection:
            return False

        roles = [pyatspi.ROLE_PAGE_TAB, pyatspi.ROLE_PAGE_TAB_LIST]
        if not event.source.getRole() in roles:
            return False

        if self.inDocumentContent(event.source):
            return False

        if not self.inDocumentContent(orca_state.locusOfFocus):
            return False

        return True

    def eventIsFromLocusOfFocusDocument(self, event):
        if orca_state.locusOfFocus == orca_state.activeWindow:
            focus = self.activeDocument()
            source = self.getTopLevelDocumentForObject(event.source)
        else:
            focus = self.getDocumentForObject(orca_state.locusOfFocus)
            source = self.getDocumentForObject(event.source)

        msg = "WEB: Event doc: %s. Focus doc: %s." % (source, focus)
        debug.println(debug.LEVEL_INFO, msg, True)

        if not (source and focus):
            return False

        if source == focus:
            return True

        if self.isZombie(focus) and not self.isZombie(source):
            if self.activeDocument() == source:
                msg = "WEB: Treating active doc as locusOfFocus doc"
                debug.println(debug.LEVEL_INFO, msg, True)
                return True

        return False

    def textEventIsDueToDeletion(self, event):
        if not self.inDocumentContent(event.source) \
           or not event.source.getState().contains(pyatspi.STATE_EDITABLE):
            return False

        if self.isDeleteCommandTextDeletionEvent(event) \
           or self.isBackSpaceCommandTextDeletionEvent(event):
            return True

        return False

    def textEventIsDueToInsertion(self, event):
        if not event.type.startswith("object:text-"):
            return False

        if not self.inDocumentContent(event.source) \
           or not event.source.getState().contains(pyatspi.STATE_EDITABLE) \
           or not event.source == orca_state.locusOfFocus:
            return False

        if isinstance(orca_state.lastInputEvent, input_event.KeyboardEvent):
            inputEvent = orca_state.lastNonModifierKeyEvent
            return inputEvent and inputEvent.isPrintableKey() and not inputEvent.modifiers

        return False

    def textEventIsForNonNavigableTextObject(self, event):
        if not event.type.startswith("object:text-"):
            return False

        return self._treatObjectAsWhole(event.source)

    def eventIsEOCAdded(self, event):
        if not self.inDocumentContent(event.source):
            return False

        if event.type.startswith("object:text-changed:insert") \
           and self.EMBEDDED_OBJECT_CHARACTER in event.any_data:
            return not re.match("[^\s\ufffc]", event.any_data)

        return False

    def caretMovedOutsideActiveGrid(self, event, oldFocus=None):
        if not (event and event.type.startswith("object:text-caret-moved")):
            return False

        oldFocus = oldFocus or orca_state.locusOfFocus
        if not self.isGridDescendant(oldFocus):
            return False

        return not self.isGridDescendant(event.source)

    def caretMovedToSamePageFragment(self, event, oldFocus=None):
        if not (event and event.type.startswith("object:text-caret-moved")):
            return False

        if event.source.getState().contains(pyatspi.STATE_EDITABLE):
            return False

        docURI = self.documentFrameURI()
        fragment = urllib.parse.urlparse(docURI).fragment
        if not fragment:
            return False

        sourceID = self._getID(event.source)
        if sourceID and fragment == sourceID:
            return True

        oldFocus = oldFocus or orca_state.locusOfFocus
        if self.isLink(oldFocus):
            link = oldFocus
        else:
            link = pyatspi.findAncestor(oldFocus, self.isLink)

        return link and self.uri(link) == docURI

    def isChildOfCurrentFragment(self, obj):
        parseResult = urllib.parse.urlparse(self.documentFrameURI())
        if not parseResult.fragment:
            return False

        isSameFragment = lambda x: self._getID(x) == parseResult.fragment
        return pyatspi.findAncestor(obj, isSameFragment) is not None

    def documentFragment(self, documentFrame):
        parseResult = urllib.parse.urlparse(self.documentFrameURI(documentFrame))
        return parseResult.fragment

    def isContentEditableWithEmbeddedObjects(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return False

        rv = self._isContentEditableWithEmbeddedObjects.get(hash(obj))
        if rv is not None:
            return rv

        rv = False
        try:
            state = obj.getState()
            role = obj.getRole()
        except:
            msg = "WEB: Exception getting state and role for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return rv

        hasTextBlockRole = lambda x: x and x.getRole() in self._textBlockElementRoles() \
            and not self.isFakePlaceholderForEntry(x) and not self.isStaticTextLeaf(x)

        if self._getTag(obj) in ["input", "textarea"]:
            rv = False
        elif role == pyatspi.ROLE_ENTRY and state.contains(pyatspi.STATE_MULTI_LINE):
            rv = pyatspi.findDescendant(obj, hasTextBlockRole)
        elif state.contains(pyatspi.STATE_EDITABLE):
            rv = hasTextBlockRole(obj) or self.isLink(obj)
        elif not self.isDocument(obj):
            document = self.getDocumentForObject(obj)
            rv = self.isContentEditableWithEmbeddedObjects(document)

        self._isContentEditableWithEmbeddedObjects[hash(obj)] = rv
        return rv

    def characterOffsetInParent(self, obj):
        start, end, length = self._rangeInParentWithLength(obj)
        return start

    def _rangeInParentWithLength(self, obj):
        if not obj:
            return -1, -1, 0

        text = self.queryNonEmptyText(obj.parent)
        if not text:
            return -1, -1, 0

        start, end = self.getHyperlinkRange(obj)
        return start, end, text.characterCount

    def getError(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return super().getError(obj)

        try:
            state = obj.getState()
        except:
            msg = "ERROR: Exception getting state for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if not state.contains(pyatspi.STATE_INVALID_ENTRY):
            return False

        try:
            self._currentTextAttrs.pop(hash(obj))
        except:
            pass

        attrs, start, end = self.textAttributes(obj, 0, True)
        error = attrs.get("invalid")
        if error == "false":
            return False
        if error not in ["spelling", "grammar"]:
            return True

        return error

    def _getErrorMessageContainer(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return None

        if not self.getError(obj):
            return None

        # Remove this when we bump dependencies to 2.26
        try:
            relationType = pyatspi.RELATION_ERROR_MESSAGE
        except:
            return None

        isMessage = lambda r: r.getRelationType() == relationType
        relations = list(filter(isMessage, obj.getRelationSet()))
        if not relations:
            return None

        return relations[0].getTarget(0)

    def getErrorMessage(self, obj):
        return self.expandEOCs(self._getErrorMessageContainer(obj))

    def isErrorForContents(self, obj, contents=[]):
        if not self.isErrorMessage(obj):
            return False

        for acc, start, end, string in contents:
            if self._getErrorMessageContainer(acc) == obj:
                return True

        return False

    def hasNoSize(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return super().hasNoSize(obj)

        rv = self._hasNoSize.get(hash(obj))
        if rv is not None:
            return rv

        rv = super().hasNoSize(obj)
        self._hasNoSize[hash(obj)] = rv
        return rv

    def _canHaveCaretContext(self, obj):
        rv = self._canHaveCaretContextDecision.get(hash(obj))
        if rv is not None:
            return rv

        startTime = time.time()
        if not obj:
            return False
        if self.isDead(obj):
            msg = "WEB: Dead object cannot have caret context %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False
        if self.isZombie(obj):
            msg = "WEB: Zombie object cannot have caret context %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False
        if self.isHidden(obj):
            msg = "WEB: Hidden object cannot have caret context %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False
        if self.isOffScreenLabel(obj):
            msg = "WEB: Off-screen label cannot have caret context %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False
        if self.isNonNavigablePopup(obj):
            msg = "WEB: Non-navigable popup cannot have caret context %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False
        if self.isUselessImage(obj):
            msg = "WEB: Useless image cannot have caret context %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False
        if self.isUselessEmptyElement(obj):
            msg = "WEB: Useless empty element cannot have caret context %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False
        if self.isEmptyAnchor(obj):
            msg = "WEB: Empty anchor cannot have caret context %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False
        if self.isEmptyToolTip(obj):
            msg = "WEB: Empty tool tip cannot have caret context %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False
        if self.hasNoSize(obj):
            msg = "WEB: Allowing sizeless object to have caret context %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return True
        if self.isParentOfNullChild(obj):
            msg = "WEB: Parent of null child cannot have caret context %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False
        if self.isPseudoElement(obj):
            msg = "WEB: Pseudo element cannot have caret context %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False
        if self.isStaticTextLeaf(obj):
            msg = "WEB: Static text leaf cannot have caret context %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False
        if self.isFakePlaceholderForEntry(obj):
            msg = "WEB: Fake placeholder for entry cannot have caret context %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False
        if self.isNonInteractiveDescendantOfControl(obj):
            msg = "WEB: Non interactive descendant of control cannot have caret context %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        msg = "INFO: Verified %s can have caret context. (%.4fs)" % (obj, time.time() - startTime)
        debug.println(debug.LEVEL_INFO, msg, True)
        self._canHaveCaretContextDecision[hash(obj)] = True
        return True

    def isPseudoElement(self, obj):
        return False

    def searchForCaretContext(self, obj):
        msg = "WEB: Searching for caret context in %s" % obj
        debug.println(debug.LEVEL_INFO, msg, True)

        container = obj
        contextObj, contextOffset = None, -1
        while obj:
            try:
                offset = obj.queryText().caretOffset
            except:
                msg = "WEB: Exception getting caret offset of %s" % obj
                debug.println(debug.LEVEL_INFO, msg, True)
                obj = None
            else:
                contextObj, contextOffset = obj, offset
                child = self.getChildAtOffset(obj, offset)
                if child:
                    obj = child
                else:
                    break

        if contextObj and not self.isHidden(contextObj):
            return self.findNextCaretInOrder(contextObj, max(-1, contextOffset - 1))

        if self.isDocument(container):
            return container, 0

        return None, -1

    def _getCaretContextViaLocusOfFocus(self):
        obj = orca_state.locusOfFocus
        if not self.inDocumentContent(obj):
            return None, -1

        try:
            offset = obj.queryText().caretOffset
        except NotImplementedError:
            offset = 0
        except:
            offset = -1

        return obj, offset

    def getCaretContext(self, documentFrame=None, getZombieReplicant=False, searchIfNeeded=True):
        msg = "WEB: Getting caret context for %s" % documentFrame
        debug.println(debug.LEVEL_INFO, msg, True)

        if not documentFrame or self.isZombie(documentFrame):
            documentFrame = self.documentFrame()

        if not documentFrame:
            if not searchIfNeeded:
                msg = "WEB: Returning None, -1: No document and no search requested."
                debug.println(debug.LEVEL_INFO, msg, True)
                return None, -1

            obj, offset = self._getCaretContextViaLocusOfFocus()
            msg = "WEB: Returning %s, %i (from locusOfFocus)" % (obj, offset)
            debug.println(debug.LEVEL_INFO, msg, True)
            return obj, offset

        context = self._caretContexts.get(hash(documentFrame.parent))
        if not context or not self.isTopLevelDocument(documentFrame):
            if not searchIfNeeded:
                return None, -1
            obj, offset = self.searchForCaretContext(documentFrame)
        elif not getZombieReplicant:
            return context
        elif self.isZombie(context[0]):
            msg = "WEB: Context is Zombie. Searching for replicant."
            debug.println(debug.LEVEL_INFO, msg, True)
            obj, offset = self.findContextReplicant()
            if obj:
                caretObj, caretOffset = self.searchForCaretContext(obj.parent)
                if caretObj and not self.isZombie(caretObj):
                    obj, offset = caretObj, caretOffset
        else:
            obj, offset = context

        self.setCaretContext(obj, offset, documentFrame)

        return obj, offset

    def getCaretContextPathRoleAndName(self, documentFrame=None):
        documentFrame = documentFrame or self.documentFrame()
        if not documentFrame:
            return [-1], None, None

        rv = self._contextPathsRolesAndNames.get(hash(documentFrame.parent))
        if not rv:
            return [-1], None, None

        return rv

    def clearCaretContext(self, documentFrame=None):
        self.clearContentCache()
        documentFrame = documentFrame or self.documentFrame()
        if not documentFrame:
            return

        parent = documentFrame.parent
        self._caretContexts.pop(hash(parent), None)
        self._priorContexts.pop(hash(parent), None)

    def handleEventFromContextReplicant(self, event, replicant):
        if self.isDead(replicant):
            msg = "WEB: Context replicant is dead."
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if not self.isDead(orca_state.locusOfFocus):
            msg = "WEB: Not event from context replicant. locusOfFocus %s is not dead." \
                % orca_state.locusOfFocus
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        path, role, name = self.getCaretContextPathRoleAndName()
        replicantPath = pyatspi.getPath(replicant)
        if path != replicantPath:
            msg = "WEB: Not event from context replicant. Path %s != replicant path %s." \
                % (path, replicantPath)
            return False

        replicantRole = replicant.getRole()
        if role != replicantRole:
            msg = "WEB: Not event from context replicant. Role %s != replicant role %s." \
                % (role, replicantRole)
            return False

        notify = replicant.name != name
        documentFrame = self.documentFrame()
        obj, offset = self._caretContexts.get(hash(documentFrame.parent))

        msg = "WEB: Is event from context replicant. Notify: %s" % notify
        debug.println(debug.LEVEL_INFO, msg, True)

        orca.setLocusOfFocus(event, replicant, notify)
        self.setCaretContext(replicant, offset, documentFrame)
        return True

    def handleEventForRemovedChild(self, event):
        if event.any_data == orca_state.locusOfFocus:
            msg = "WEB: Removed child is locusOfFocus."
            debug.println(debug.LEVEL_INFO, msg, True)
        elif pyatspi.findAncestor(orca_state.locusOfFocus, lambda x: x == event.any_data):
            msg = "WEB: Removed child is ancestor of locusOfFocus."
            debug.println(debug.LEVEL_INFO, msg, True)
        else:
            return False

        if event.detail1 == -1:
            msg = "WEB: Event detail1 is useless."
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        obj, offset = None, -1
        notify = True
        keyString, mods = self.lastKeyAndModifiers()
        if keyString == "Up":
            if event.detail1 >= event.source.childCount:
                msg = "WEB: Last child removed. Getting new location from end of parent."
                debug.println(debug.LEVEL_INFO, msg, True)
                obj, offset = self.previousContext(event.source, -1)
            elif 0 <= event.detail1 - 1 < event.source.childCount:
                child = event.source[event.detail1 - 1]
                msg = "WEB: Getting new location from end of previous child %s." % child
                debug.println(debug.LEVEL_INFO, msg, True)
                obj, offset = self.previousContext(child, -1)
            else:
                prevObj = self.findPreviousObject(event.source)
                msg = "WEB: Getting new location from end of source's previous object %s." % prevObj
                debug.println(debug.LEVEL_INFO, msg, True)
                obj, offset = self.previousContext(prevObj, -1)

        elif keyString == "Down":
            if event.detail1 == 0:
                msg = "WEB: First child removed. Getting new location from start of parent."
                debug.println(debug.LEVEL_INFO, msg, True)
                obj, offset = self.nextContext(event.source, -1)
            elif 0 < event.detail1 < event.source.childCount:
                child = event.source[event.detail1]
                msg = "WEB: Getting new location from start of child %i %s." % (event.detail1, child)
                debug.println(debug.LEVEL_INFO, msg, True)
                obj, offset = self.nextContext(child, -1)
            else:
                nextObj = self.findNextObject(event.source)
                msg = "WEB: Getting new location from start of source's next object %s." % nextObj
                debug.println(debug.LEVEL_INFO, msg, True)
                obj, offset = self.nextContext(nextObj, -1)

        else:
            notify = False
            obj, offset = self.searchForCaretContext(event.source)
            # Risk "chattiness" if the locusOfFocus is dead and the object we've found is
            # focused.
            if obj and self.isDead(orca_state.locusOfFocus) \
               and obj.getState().contains(pyatspi.STATE_FOCUSED):
                notify = True

        if obj:
            msg = "WEB: Setting locusOfFocus and context to: %s, %i" % (obj, offset)
            orca.setLocusOfFocus(event, obj, notify)
            self.setCaretContext(obj, offset)
            return True

        msg = "WEB: Unable to find context for child removed from %s" % event.source
        debug.println(debug.LEVEL_INFO, msg, True)
        return False

    def findContextReplicant(self, documentFrame=None, matchRole=True, matchName=True):
        path, oldRole, oldName = self.getCaretContextPathRoleAndName(documentFrame)
        obj = self.getObjectFromPath(path)
        if obj and matchRole:
            if obj.getRole() != oldRole:
                obj = None
        if obj and matchName:
            if obj.name != oldName:
                obj = None
        if not obj:
            return None, -1

        obj, offset = self.findFirstCaretContext(obj, 0)
        msg = "WEB: Context replicant is %s, %i" % (obj, offset)
        debug.println(debug.LEVEL_INFO, msg, True)
        return obj, offset

    def getPriorContext(self, documentFrame=None):
        if not documentFrame or self.isZombie(documentFrame):
            documentFrame = self.documentFrame()

        if documentFrame:
            context = self._priorContexts.get(hash(documentFrame.parent))
            if context:
                return context

        return None, -1

    def _getPath(self, obj):
        rv = self._paths.get(hash(obj))
        if rv is not None:
            return rv

        try:
            rv = pyatspi.getPath(obj)
        except:
            msg = "WEB: Exception getting path for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            rv = [-1]

        self._paths[hash(obj)] = rv
        return rv

    def setCaretContext(self, obj=None, offset=-1, documentFrame=None):
        documentFrame = documentFrame or self.documentFrame()
        if not documentFrame:
            return

        parent = documentFrame.parent
        oldObj, oldOffset = self._caretContexts.get(hash(parent), (obj, offset))
        self._priorContexts[hash(parent)] = oldObj, oldOffset
        self._caretContexts[hash(parent)] = obj, offset

        path = self._getPath(obj)
        try:
            role = obj.getRole()
            name = obj.name
        except:
            msg = "WEB: Exception getting role and name for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            role = None
            name = None

        self._contextPathsRolesAndNames[hash(parent)] = path, role, name

    def findFirstCaretContext(self, obj, offset):
        msg = "WEB: Looking for first caret context for %s, %i" % (obj, offset)
        debug.println(debug.LEVEL_INFO, msg, True)

        try:
            role = obj.getRole()
        except:
            msg = "WEB: Exception getting first caret context for %s %i" % (obj, offset)
            debug.println(debug.LEVEL_INFO, msg, True)
            return None, -1

        lookInChild = [pyatspi.ROLE_LIST,
                       pyatspi.ROLE_INTERNAL_FRAME,
                       pyatspi.ROLE_TABLE,
                       pyatspi.ROLE_TABLE_ROW]
        if role in lookInChild and obj.childCount and not self.treatAsDiv(obj, offset):
            msg = "WEB: First caret context for %s, %i will look in child %s" % (obj, offset, obj[0])
            debug.println(debug.LEVEL_INFO, msg, True)
            return self.findFirstCaretContext(obj[0], 0)

        text = self.queryNonEmptyText(obj)
        if not text and self._canHaveCaretContext(obj):
            msg = "WEB: First caret context for non-text context %s, %i is %s, %i" % (obj, offset, obj, 0)
            debug.println(debug.LEVEL_INFO, msg, True)
            return obj, 0

        if text and offset >= text.characterCount:
            if self.isContentEditableWithEmbeddedObjects(obj) and self.lastInputEventWasCharNav():
                nextObj, nextOffset = self.nextContext(obj, text.characterCount)
                if not nextObj:
                    msg = "WEB: No next object found at end of contenteditable %s" % obj
                    debug.println(debug.LEVEL_INFO, msg, True)
                elif not self.isContentEditableWithEmbeddedObjects(nextObj):
                    msg = "WEB: Next object found at end of contenteditable %s is not editable %s" % (obj, nextObj)
                    debug.println(debug.LEVEL_INFO, msg, True)
                else:
                    msg = "WEB: First caret context at end of contenteditable %s is next context %s, %i" % \
                        (obj, nextObj, nextOffset)
                    debug.println(debug.LEVEL_INFO, msg, True)
                    return nextObj, nextOffset

            msg = "WEB: First caret context at end of %s, %i is %s, %i" % (obj, offset, obj, text.characterCount)
            debug.println(debug.LEVEL_INFO, msg, True)
            return obj, text.characterCount

        offset = max (0, offset)
        if text:
            allText = text.getText(0, -1)
            if allText[offset] != self.EMBEDDED_OBJECT_CHARACTER or role == pyatspi.ROLE_ENTRY:
                msg = "WEB: First caret context for %s, %i is unchanged" % (obj, offset)
                debug.println(debug.LEVEL_INFO, msg, True)
                return obj, offset

            # Descending an element that we're treating as a whole can lead to looping/getting stuck.
            if self.elementLinesAreSingleChars(obj):
                msg = "WEB: EOC in single-char-lines element. Returning %s, %i unchanged." % (obj, offset)
                debug.println(debug.LEVEL_INFO, msg, True)
                return obj, offset

        child = self.getChildAtOffset(obj, offset)
        if not child:
            msg = "WEB: Child at offset is null. Returning %s, %i unchanged." % (obj, offset)
            debug.println(debug.LEVEL_INFO, msg, True)
            return obj, offset

        if self.isDocument(obj):
            while self.isUselessEmptyElement(child):
                msg = "WEB: Child %s of %s at offset %i cannot be context." % (child, obj, offset)
                debug.println(debug.LEVEL_INFO, msg, True)
                offset += 1
                child = self.getChildAtOffset(obj, offset)

        if self.isListItemMarker(child):
            msg = "WEB: First caret context for %s, %i is %s, %i (skip list item marker child)" % \
                (obj, offset, obj, offset + 1)
            debug.println(debug.LEVEL_INFO, msg, True)
            return obj, offset + 1

        if self.isEmptyAnchor(child):
            nextObj, nextOffset = self.nextContext(obj, offset)
            if nextObj:
                msg = "WEB: First caret context at end of empty anchor %s is next context %s, %i" % \
                    (obj, nextObj, nextOffset)
                debug.println(debug.LEVEL_INFO, msg, True)
                return nextObj, nextOffset

        if not self._canHaveCaretContext(child):
            msg = "WEB: Child cannot be context. Returning %s, %i." % (obj, offset)
            debug.println(debug.LEVEL_INFO, msg, True)
            return obj, offset

        msg = "WEB: Looking in child %s for first caret context for %s, %i" % (child, obj, offset)
        debug.println(debug.LEVEL_INFO, msg, True)
        return self.findFirstCaretContext(child, 0)

    def findNextCaretInOrder(self, obj=None, offset=-1):
        startTime = time.time()
        rv = self._findNextCaretInOrder(obj, offset)
        msg = "INFO: Next caret in order for %s, %i: %s, %i (%.4fs)" % \
            (obj, offset, rv[0], rv[1], time.time() - startTime)
        debug.println(debug.LEVEL_INFO, msg, True)
        return rv

    def _findNextCaretInOrder(self, obj=None, offset=-1):
        if not obj:
            obj, offset = self.getCaretContext()

        if not obj or not self.inDocumentContent(obj):
            return None, -1

        if self._canHaveCaretContext(obj):
            text = self.queryNonEmptyText(obj)
            if text:
                allText = text.getText(0, -1)
                for i in range(offset + 1, len(allText)):
                    child = self.getChildAtOffset(obj, i)
                    if child and allText[i] != self.EMBEDDED_OBJECT_CHARACTER:
                        msg = "ERROR: Child %s found at offset with char '%s'" % \
                            (child, allText[i].replace("\n", "\\n"))
                        debug.println(debug.LEVEL_INFO, msg, True)
                    if self._canHaveCaretContext(child):
                        if self._treatObjectAsWhole(child, -1):
                            return child, 0
                        return self._findNextCaretInOrder(child, -1)
                    if allText[i] not in (self.EMBEDDED_OBJECT_CHARACTER, self.ZERO_WIDTH_NO_BREAK_SPACE):
                        return obj, i
            elif obj.childCount and not self._treatObjectAsWhole(obj, offset):
                return self._findNextCaretInOrder(obj[0], -1)
            elif offset < 0 and not self.isTextBlockElement(obj):
                return obj, 0

        # If we're here, start looking up the tree, up to the document.
        if self.isTopLevelDocument(obj):
            return None, -1

        while obj and obj.parent:
            if self.isDetachedDocument(obj.parent):
                obj = self.iframeForDetachedDocument(obj.parent)
                continue

            parent = obj.parent
            if self.isZombie(parent):
                msg = "WEB: Finding next caret in order. Parent is Zombie."
                debug.println(debug.LEVEL_INFO, msg, True)
                replicant = self.findReplicant(self.documentFrame(), parent)
                if replicant and not self.isZombie(replicant):
                    parent = replicant
                elif parent.parent:
                    obj = parent
                    continue
                else:
                    break

            start, end, length = self._rangeInParentWithLength(obj)
            if start + 1 == end and 0 <= start < end <= length:
                return self._findNextCaretInOrder(parent, start)

            index = obj.getIndexInParent() + 1
            try:
                parentChildCount = parent.childCount
            except:
                msg = "WEB: Exception getting childCount for %s" % parent
                debug.println(debug.LEVEL_INFO, msg, True)
            else:
                if 0 < index < parentChildCount:
                    return self._findNextCaretInOrder(parent[index], -1)
            obj = parent

        return None, -1

    def findPreviousCaretInOrder(self, obj=None, offset=-1):
        startTime = time.time()
        rv = self._findPreviousCaretInOrder(obj, offset)
        msg = "INFO: Previous caret in order for %s, %i: %s, %i (%.4fs)" % \
            (obj, offset, rv[0], rv[1], time.time() - startTime)
        debug.println(debug.LEVEL_INFO, msg, True)
        return rv

    def _findPreviousCaretInOrder(self, obj=None, offset=-1):
        if not obj:
            obj, offset = self.getCaretContext()

        if not obj or not self.inDocumentContent(obj):
            return None, -1

        if self._canHaveCaretContext(obj):
            text = self.queryNonEmptyText(obj)
            if text:
                allText = text.getText(0, -1)
                if offset == -1 or offset > len(allText):
                    offset = len(allText)
                for i in range(offset - 1, -1, -1):
                    child = self.getChildAtOffset(obj, i)
                    if child and allText[i] != self.EMBEDDED_OBJECT_CHARACTER:
                        msg = "ERROR: Child %s found at offset with char '%s'" % \
                            (child, allText[i].replace("\n", "\\n"))
                        debug.println(debug.LEVEL_INFO, msg, True)
                    if self._canHaveCaretContext(child):
                        if self._treatObjectAsWhole(child, -1):
                            return child, 0
                        return self._findPreviousCaretInOrder(child, -1)
                    if allText[i] not in (self.EMBEDDED_OBJECT_CHARACTER, self.ZERO_WIDTH_NO_BREAK_SPACE):
                        return obj, i
            elif obj.childCount and not self._treatObjectAsWhole(obj, offset):
                return self._findPreviousCaretInOrder(obj[obj.childCount - 1], -1)
            elif offset < 0 and not self.isTextBlockElement(obj):
                return obj, 0

        # If we're here, start looking up the tree, up to the document.
        if self.isTopLevelDocument(obj):
            return None, -1

        while obj and obj.parent:
            if self.isDetachedDocument(obj.parent):
                obj = self.iframeForDetachedDocument(obj.parent)
                continue

            parent = obj.parent
            if self.isZombie(parent):
                msg = "WEB: Finding previous caret in order. Parent is Zombie."
                debug.println(debug.LEVEL_INFO, msg, True)
                replicant = self.findReplicant(self.documentFrame(), parent)
                if replicant and not self.isZombie(replicant):
                    parent = replicant
                elif parent.parent:
                    obj = parent
                    continue
                else:
                    break

            start, end, length = self._rangeInParentWithLength(obj)
            if start + 1 == end and 0 <= start < end <= length:
                return self._findPreviousCaretInOrder(parent, start)

            index = obj.getIndexInParent() - 1
            try:
                parentChildCount = parent.childCount
            except:
                msg = "WEB: Exception getting childCount for %s" % parent
                debug.println(debug.LEVEL_INFO, msg, True)
            else:
                if 0 <= index < parentChildCount:
                    return self._findPreviousCaretInOrder(parent[index], -1)
            obj = parent

        return None, -1

    def lastQueuedLiveRegion(self):
        if self._lastQueuedLiveRegionEvent is None:
            return None

        if self._lastQueuedLiveRegionEvent.type.startswith("object:text-changed:insert"):
            return self._lastQueuedLiveRegionEvent.source

        if self._lastQueuedLiveRegionEvent.type.startswith("object:children-changed:add"):
            return self._lastQueuedLiveRegionEvent.any_data

        return None

    def handleAsLiveRegion(self, event):
        if not _settingsManager.getSetting('inferLiveRegions'):
            return False

        if not self.isLiveRegion(event.source):
            return False

        if not _settingsManager.getSetting('presentLiveRegionFromInactiveTab') \
           and self.getTopLevelDocumentForObject(event.source) != self.activeDocument():
            msg = "WEB: Live region source is not in active tab."
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if event.type.startswith("object:text-changed:insert"):
            alert = pyatspi.findAncestor(event.source, self.isAriaAlert)
            if alert and self.focusedObject(alert) == event.source:
                msg = "WEB: Focused source will be presented as part of alert"
                debug.println(debug.LEVEL_INFO, msg, True)
                return False

            if self._lastQueuedLiveRegionEvent \
               and self._lastQueuedLiveRegionEvent.type == event.type \
               and self._lastQueuedLiveRegionEvent.any_data == event.any_data:
                msg = "WEB: Event is believed to be duplicate message"
                debug.println(debug.LEVEL_INFO, msg, True)
                return False

        if isinstance(event.any_data, pyatspi.Accessible):
            try:
                role = event.any_data.getRole()
            except:
                msg = "WEB: Exception getting role for %s" % event.any_data
                debug.println(debug.LEVEL_INFO, msg, True)
                return False

            if role in [pyatspi.ROLE_UNKNOWN, pyatspi.ROLE_REDUNDANT_OBJECT] \
               and self._getTag(event.any_data) in ["", None, "br"]:
                msg = "WEB: Child has unknown role and no tag %s" % event.any_data
                debug.println(debug.LEVEL_INFO, msg, True)
                return False

            if self.lastQueuedLiveRegion() == event.any_data \
               and self._lastQueuedLiveRegionEvent.type != event.type:
                msg = "WEB: Event is believed to be redundant live region notification"
                debug.println(debug.LEVEL_INFO, msg, True)
                return False

        self._lastQueuedLiveRegionEvent = event
        return True

    def statusBar(self, obj):
        if self._statusBar and not self.isZombie(self._statusBar):
            msg = "WEB: Returning cached status bar: %s" % self._statusBar
            debug.println(debug.LEVEL_INFO, msg, True)
            return self._statusBar

        self._statusBar = super().statusBar(obj)
        return self._statusBar

    def getPageObjectCount(self, obj):
        result = {'landmarks': 0,
                  'headings': 0,
                  'forms': 0,
                  'tables': 0,
                  'visitedLinks': 0,
                  'unvisitedLinks': 0}

        docframe = self.documentFrame(obj)
        msg = "WEB: Document frame for %s is %s" % (obj, docframe)
        debug.println(debug.LEVEL_INFO, msg, True)

        col = docframe.queryCollection()
        stateset = pyatspi.StateSet()
        roles = [pyatspi.ROLE_HEADING,
                 pyatspi.ROLE_LINK,
                 pyatspi.ROLE_TABLE,
                 pyatspi.ROLE_FORM,
                 pyatspi.ROLE_LANDMARK]

        if not self.supportsLandmarkRole():
            roles.append(pyatspi.ROLE_SECTION)

        rule = col.createMatchRule(stateset.raw(), col.MATCH_NONE,
                                   "", col.MATCH_NONE,
                                   roles, col.MATCH_ANY,
                                   "", col.MATCH_NONE,
                                   False)

        matches = col.getMatches(rule, col.SORT_ORDER_CANONICAL, 0, True)
        col.freeMatchRule(rule)
        for obj in matches:
            role = obj.getRole()
            if role == pyatspi.ROLE_HEADING:
                result['headings'] += 1
            elif role == pyatspi.ROLE_FORM:
                result['forms'] += 1
            elif role == pyatspi.ROLE_TABLE and not self.isLayoutOnly(obj):
                result['tables'] += 1
            elif role == pyatspi.ROLE_LINK:
                if self.isLink(obj):
                    if obj.getState().contains(pyatspi.STATE_VISITED):
                        result['visitedLinks'] += 1
                    else:
                        result['unvisitedLinks'] += 1
            elif self.isLandmark(obj):
                result['landmarks'] += 1

        return result

    def getPageSummary(self, obj, onlyIfFound=True):
        result = []
        counts = self.getPageObjectCount(obj)
        result.append(messages.landmarkCount(counts.get('landmarks', 0), onlyIfFound))
        result.append(messages.headingCount(counts.get('headings', 0), onlyIfFound))
        result.append(messages.formCount(counts.get('forms', 0), onlyIfFound))
        result.append(messages.tableCount(counts.get('tables', 0), onlyIfFound))
        result.append(messages.visitedLinkCount(counts.get('visitedLinks', 0), onlyIfFound))
        result.append(messages.unvisitedLinkCount(counts.get('unvisitedLinks', 0), onlyIfFound))
        result = list(filter(lambda x: x, result))
        if not result:
            return ""

        return messages.PAGE_SUMMARY_PREFIX % ", ".join(result)

    def preferDescriptionOverName(self, obj):
        if not self.inDocumentContent(obj):
            return super().preferDescriptionOverName(obj)

        rv = self._preferDescriptionOverName.get(hash(obj))
        if rv is not None:
            return rv

        try:
            role = obj.getRole()
            name = obj.name
            description = obj.description
        except:
            msg = "WEB: Exception getting name, description, and role for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            rv = False
        else:
            if len(obj.name) == 1 and ord(obj.name) in range(0xe000, 0xf8ff):
                msg = "WEB: name of %s is in unicode private use area" % obj
                debug.println(debug.LEVEL_INFO, msg, True)
                rv = True
            else:
                roles = [pyatspi.ROLE_PUSH_BUTTON]
                rv = role in roles and len(name) == 1 and description

        self._preferDescriptionOverName[hash(obj)] = rv
        return rv

    def _getCtrlShiftSelectionsStrings(self):
        """Hacky and to-be-obsoleted method."""
        return [messages.LINE_SELECTED_DOWN,
                messages.LINE_UNSELECTED_DOWN,
                messages.LINE_SELECTED_UP,
                messages.LINE_UNSELECTED_UP]

    def lastInputEventWasCopy(self):
        if super().lastInputEventWasCopy():
            return True

        if not self.inDocumentContent():
            return False

        if not self.topLevelObjectIsActiveAndCurrent():
            return False

        if 'Action' in pyatspi.listInterfaces(orca_state.locusOfFocus):
            msg = "WEB: Treating %s as source of copy" % orca_state.locusOfFocus
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        return False
