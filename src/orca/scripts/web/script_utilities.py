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

import pyatspi
import re
import urllib

from orca import debug
from orca import input_event
from orca import messages
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

        self._currentAttrs = {}
        self._caretContexts = {}
        self._priorContexts = {}
        self._contextPathsRolesAndNames = {}
        self._paths = {}
        self._inDocumentContent = {}
        self._inTopLevelWebApp = {}
        self._isTextBlockElement = {}
        self._isContentEditableWithEmbeddedObjects = {}
        self._isEntryDescendant = {}
        self._isGridDescendant = {}
        self._isLabelDescendant = {}
        self._isMenuDescendant = {}
        self._isToolBarDescendant = {}
        self._isLayoutOnly = {}
        self._isDPub = {}
        self._isMath = {}
        self._mathNestingLevel = {}
        self._isOffScreenLabel = {}
        self._hasExplicitName = {}
        self._hasNoSize = {}
        self._hasLongDesc = {}
        self._hasUselessCanvasDescendant = {}
        self._id = {}
        self._isClickableElement = {}
        self._isAnchor = {}
        self._isEditableComboBox = {}
        self._isEditableDescendantOfComboBox = {}
        self._isErrorMessage = {}
        self._isLandmark = {}
        self._isLiveRegion = {}
        self._isLink = {}
        self._isNonNavigablePopup = {}
        self._isNonEntryTextWidget = {}
        self._isImageMap = {}
        self._isUselessImage = {}
        self._isNonNavigableEmbeddedDocument = {}
        self._isParentOfNullChild = {}
        self._inferredLabels = {}
        self._actualLabels = {}
        self._labelTargets = {}
        self._displayedLabelText = {}
        self._mimeType = {}
        self._roleDescription = {}
        self._shouldFilter = {}
        self._shouldInferLabelFor = {}
        self._text = {}
        self._tag = {}
        self._xmlRoles = {}
        self._treatAsDiv = {}
        self._posinset = {}
        self._setsize = {}
        self._currentObjectContents = None
        self._currentSentenceContents = None
        self._currentLineContents = None
        self._currentWordContents = None
        self._currentCharacterContents = None

        self._validChildRoles = {pyatspi.ROLE_LIST: [pyatspi.ROLE_LIST_ITEM]}

    def _cleanupContexts(self):
        toRemove = []
        for key, [obj, offset] in self._caretContexts.items():
            if self.isZombie(obj):
                toRemove.append(key)

        for key in toRemove:
            self._caretContexts.pop(key, None)

    def clearCachedObjects(self):
        debug.println(debug.LEVEL_INFO, "WEB: cleaning up cached objects", True)
        self._inDocumentContent = {}
        self._inTopLevelWebApp = {}
        self._isTextBlockElement = {}
        self._isContentEditableWithEmbeddedObjects = {}
        self._isEntryDescendant = {}
        self._isGridDescendant = {}
        self._isLabelDescendant = {}
        self._isMenuDescendant = {}
        self._isToolBarDescendant = {}
        self._isLayoutOnly = {}
        self._isDPub = {}
        self._isMath = {}
        self._mathNestingLevel = {}
        self._isOffScreenLabel = {}
        self._hasExplicitName = {}
        self._hasNoSize = {}
        self._hasLongDesc = {}
        self._hasUselessCanvasDescendant = {}
        self._id = {}
        self._isClickableElement = {}
        self._isAnchor = {}
        self._isEditableComboBox = {}
        self._isEditableDescendantOfComboBox = {}
        self._isErrorMessage = {}
        self._isLandmark = {}
        self._isLiveRegion = {}
        self._isLink = {}
        self._isNonNavigablePopup = {}
        self._isNonEntryTextWidget = {}
        self._isImageMap = {}
        self._isUselessImage = {}
        self._isNonNavigableEmbeddedDocument = {}
        self._isParentOfNullChild = {}
        self._inferredLabels = {}
        self._actualLabels = {}
        self._labelTargets = {}
        self._displayedLabelText = {}
        self._mimeType = {}
        self._roleDescription = {}
        self._shouldFilter = {}
        self._shouldInferLabelFor = {}
        self._tag = {}
        self._xmlRoles = {}
        self._treatAsDiv = {}
        self._posinset = {}
        self._setsize = {}
        self._paths = {}
        self._contextPathsRolesAndNames = {}
        self._cleanupContexts()
        self._priorContexts = {}

    def clearContentCache(self):
        self._currentObjectContents = None
        self._currentSentenceContents = None
        self._currentLineContents = None
        self._currentWordContents = None
        self._currentCharacterContents = None
        self._currentAttrs = {}
        self._text = {}

    def isDocument(self, obj):
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

    def getDocumentForObject(self, obj):
        if not obj:
            return None

        if self.isDocument(obj):
            return obj

        return pyatspi.findAncestor(obj, self.isDocument)

    def _getDocumentsEmbeddedBy(self, frame):
        isEmbeds = lambda r: r.getRelationType() == pyatspi.RELATION_EMBEDS
        relations = list(filter(isEmbeds, frame.getRelationSet()))
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

    def documentFrame(self, obj=None):
        if self.sanityCheckActiveWindow():
            isShowing = lambda x: x and x.getState().contains(pyatspi.STATE_SHOWING)
            documents = self._getDocumentsEmbeddedBy(orca_state.activeWindow)
            documents = list(filter(isShowing, documents))
            if len(documents) == 1:
                return documents[0]

        return self.getDocumentForObject(obj or orca_state.locusOfFocus)

    def documentFrameURI(self, documentFrame=None):
        documentFrame = documentFrame or self.documentFrame()
        if documentFrame and not self.isZombie(documentFrame):
            try:
                document = documentFrame.queryDocument()
            except NotImplementedError:
                msg = "WEB: %s does not implement document interface" % documentFrame
                debug.println(debug.LEVEL_INFO, msg, True)
            except:
                msg = "ERROR: Exception querying document interface of %s" % documentFrame
                debug.println(debug.LEVEL_INFO, msg, True)
            else:
                return document.getAttributeValue('DocURL')

        return None

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
        except:
            msg = "WEB: Exception getting role and state for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        # To avoid triggering popup lists.
        if role == pyatspi.ROLE_ENTRY:
            return False

        if role == pyatspi.ROLE_IMAGE:
            isLink = lambda x: x and x.getRole() == pyatspi.ROLE_LINK
            return pyatspi.utils.findAncestor(obj, isLink) is not None

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

        orca.setLocusOfFocus(None, obj, notifyScript=False)
        if grabFocus:
            self.grabFocus(obj)

        text = self.queryNonEmptyText(obj)
        if text:
            text.setCaretOffset(offset)

        if self._script.useFocusMode(obj) != self._script.inFocusMode():
            self._script.togglePresentationMode(None)

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

    def getRoleDescription(self, obj):
        rv = self._roleDescription.get(hash(obj))
        if rv is not None:
            return rv

        try:
            attrs = dict([attr.split(':', 1) for attr in obj.getAttributes()])
        except:
            attrs = {}

        rv = attrs.get('roledescription', '')
        self._roleDescription[hash(obj)] = rv
        return rv

    def getPositionInSet(self, obj):
        rv = self._posinset.get(hash(obj))
        if rv is not None:
            return rv

        try:
            attrs = dict([attr.split(':', 1) for attr in obj.getAttributes()])
        except:
            attrs = {}

        position = attrs.get('posinset')
        if position is not None:
            rv = int(position)

        self._posinset[hash(obj)] = rv
        return rv

    def getSetSize(self, obj):
        rv = self._setsize.get(hash(obj))
        if rv is not None:
            return rv

        try:
            attrs = dict([attr.split(':', 1) for attr in obj.getAttributes()])
        except:
            attrs = {}

        setsize = attrs.get('setsize')
        if setsize is not None:
            rv = int(setsize)

        self._setsize[hash(obj)] = rv
        return rv

    def _getID(self, obj):
        if hash(obj) in self._id:
            return self._id.get(hash(obj))

        try:
            attrs = dict([attr.split(':', 1) for attr in obj.getAttributes()])
        except:
            return None

        rv = attrs.get('id')
        self._id[hash(obj)] = rv
        return rv

    def _getTag(self, obj):
        rv = self._tag.get(hash(obj))
        if rv is not None:
            return rv

        try:
            attrs = dict([attr.split(':', 1) for attr in obj.getAttributes()])
        except:
            return None

        rv = attrs.get('tag')
        self._tag[hash(obj)] = rv
        return rv

    def _getXMLRoles(self, obj):
        rv = self._xmlRoles.get(hash(obj))
        if rv is not None:
            return rv

        try:
            attrs = dict([attr.split(':', 1) for attr in obj.getAttributes()])
        except:
            return None

        rv = attrs.get('xml-roles', '').split()
        self._xmlRoles[hash(obj)] = rv
        return rv

    def inFindToolbar(self, obj=None):
        if not obj:
            obj = orca_state.locusOfFocus

        if self.inDocumentContent(obj):
            return False

        return super().inFindToolbar(obj)

    def isEmpty(self, obj):
        if not self.isTextBlockElement(obj):
            return False

        return self.queryNonEmptyText(obj, False) is None

    def isHidden(self, obj):
        try:
            attrs = dict([attr.split(':', 1) for attr in obj.getAttributes()])
        except:
            return False
        return attrs.get('hidden', False)

    def isTextArea(self, obj):
        if self.isLink(obj):
            return False

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
        if (obj, offset) == (nextobj, nextoffset):
            nextobj, nextoffset = self.findNextCaretInOrder(nextobj, nextoffset)

        if skipSpace:
            text = self.queryNonEmptyText(nextobj)
            while text and text.getText(nextoffset, nextoffset + 1).isspace():
                nextobj, nextoffset = self.findNextCaretInOrder(nextobj, nextoffset)
                text = self.queryNonEmptyText(nextobj)

        return nextobj, nextoffset

    def previousContext(self, obj=None, offset=-1, skipSpace=False):
        if not obj:
            obj, offset = self.getCaretContext()

        prevobj, prevoffset = self.findPreviousCaretInOrder(obj, offset)
        if (obj, offset) == (prevobj, prevoffset):
            prevobj, prevoffset = self.findPreviousCaretInOrder(prevobj, prevoffset)

        if skipSpace:
            text = self.queryNonEmptyText(prevobj)
            while text and text.getText(prevoffset, prevoffset + 1).isspace():
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

        try:
            text = obj.queryText()
            if text.characterCount:
                return list(text.getRangeExtents(startOffset, endOffset, 0))
        except NotImplementedError:
            pass
        except:
            msg = "WEB: Exception getting range extents for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return [0, 0, 0, 0]

        role = obj.getRole()
        parentRole = obj.parent.getRole()
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

    def expandEOCs(self, obj, startOffset=0, endOffset=-1):
        if not self.inDocumentContent(obj):
            return super().expandEOCs(obj, startOffset, endOffset)

        text = self.queryNonEmptyText(obj)
        if not text:
            return ""

        string = text.getText(startOffset, endOffset)

        if self.EMBEDDED_OBJECT_CHARACTER in string:
            # If we're not getting the full text of this object, but
            # rather a substring, we need to figure out the offset of
            # the first child within this substring.
            childOffset = 0
            for child in obj:
                if self.characterOffsetInParent(child) >= startOffset:
                    break
                childOffset += 1

            toBuild = list(string)
            count = toBuild.count(self.EMBEDDED_OBJECT_CHARACTER)
            for i in range(count):
                index = toBuild.index(self.EMBEDDED_OBJECT_CHARACTER)
                try:
                    child = obj[i + childOffset]
                except:
                    continue
                childText = self.expandEOCs(child)
                if not childText:
                    childText = ""
                toBuild[index] = "%s " % childText

            string = "".join(toBuild).strip()

        return string

    def substring(self, obj, startOffset, endOffset):
        if not self.inDocumentContent(obj):
            return super().substring(obj, startOffset, endOffset)

        text = self.queryNonEmptyText(obj)
        if text:
            return text.getText(startOffset, endOffset)

        return ""

    def textAttributes(self, acc, offset, get_defaults=False):
        attrsForObj = self._currentAttrs.get(hash(acc)) or {}
        if offset in attrsForObj:
            return attrsForObj.get(offset)

        attrs = super().textAttributes(acc, offset, get_defaults)
        self._currentAttrs[hash(acc)] = {offset:attrs}

        return attrs

    def findObjectInContents(self, obj, offset, contents):
        if not obj or not contents:
            return -1

        offset = max(0, offset)
        matches = [x for x in contents if x[0] == obj]
        match = [x for x in matches if x[1] <= offset < x[2]]
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
        elif role in [pyatspi.ROLE_LIST_ITEM, pyatspi.ROLE_TABLE_CELL]:
            rv = not self.isTextBlockElement(obj)

        self._isNonEntryTextWidget[hash(obj)] = rv
        return rv

    def queryNonEmptyText(self, obj, excludeNonEntryTextWidgets=True):
        if not (obj and self.inDocumentContent(obj)) or self._script.browseModeIsSticky():
            return super().queryNonEmptyText(obj)

        if hash(obj) in self._text:
            return self._text.get(hash(obj))

        try:
            rv = obj.queryText()
            characterCount = rv.characterCount
        except:
            rv = None
        else:
            if not characterCount:
                rv = None

        if not self.isLiveRegion(obj):
            doNotQuery = [pyatspi.ROLE_TABLE_ROW,
                          pyatspi.ROLE_TOOL_BAR]

            if not self._script.browseModeIsSticky():
                doNotQuery.append(pyatspi.ROLE_EMBEDDED)

            role = obj.getRole()
            if rv and role in doNotQuery:
                rv = None
            if rv and excludeNonEntryTextWidgets and self.isNonEntryTextWidget(obj):
                rv = None
            if rv and (self.isHidden(obj) or self.isOffScreenLabel(obj)):
                rv = None
            if rv and self.isNonNavigableEmbeddedDocument(obj):
                rv = None
            if rv and role == pyatspi.ROLE_LINK \
               and (self.hasExplicitName(obj) or self.hasUselessCanvasDescendant(obj)):
                rv = None

        self._text[hash(obj)] = rv
        return rv

    def _treatTextObjectAsWhole(self, obj):
        roles = [pyatspi.ROLE_CHECK_BOX,
                 pyatspi.ROLE_CHECK_MENU_ITEM,
                 pyatspi.ROLE_MENU,
                 pyatspi.ROLE_MENU_ITEM,
                 pyatspi.ROLE_RADIO_MENU_ITEM,
                 pyatspi.ROLE_RADIO_BUTTON,
                 pyatspi.ROLE_PUSH_BUTTON,
                 pyatspi.ROLE_TOGGLE_BUTTON]

        role = obj.getRole()
        if role in roles:
            return True

        if role == pyatspi.ROLE_TABLE_CELL and self.isFocusModeWidget(obj):
            return True

        return False

    def __findRange(self, text, offset, start, end, boundary):
        # We should not have to do any of this. Seriously. This is why
        # We can't have nice things.

        allText = text.getText(0, -1)
        if boundary == pyatspi.TEXT_BOUNDARY_CHAR:
            string = allText[offset]
            return string, offset, offset + 1

        extents = list(text.getRangeExtents(offset, offset + 1, 0))

        def _inThisSpan(span):
            return span[0] <= offset <= span[1]

        def _onThisLine(span):
            start, end = span
            startExtents = list(text.getRangeExtents(start, start + 1, 0))
            endExtents = list(text.getRangeExtents(end - 1, end, 0))
            if not self.extentsAreOnSameLine(startExtents, endExtents):
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

        words = [m.span() for m in re.finditer("[^\\s\\-\ufffc]+", string)]
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
            string, start, end = text.getText(offset, -1), offset, text.characterCount
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
        elif not (start <= offset < end) and not self.isPlainText():
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

        if boundary == pyatspi.TEXT_BOUNDARY_LINE_START and self.isMath(obj):
            if self.isMathTopLevel(obj):
                math = obj
            else:
                math = self.getMathAncestor(obj)
            return [[math, 0, 1, '']]

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
                childIndex = self.getChildIndex(obj, offset)
                try:
                    child = obj[childIndex]
                except:
                    pass
                else:
                    return self._getContentsForObj(child, 0, boundary)

        ranges = [m.span() for m in re.finditer("[^\ufffc]+", string)]
        strings = list(filter(lambda x: x[0] <= stringOffset <= x[1], ranges))
        if len(strings) == 1:
            rangeStart, rangeEnd = strings[0]
            start += rangeStart
            string = string[rangeStart:rangeEnd]
            end = start + len(string)

        return [[obj, start, end, string]]

    def getSentenceContentsAtOffset(self, obj, offset, useCache=True):
        if not obj:
            return []

        offset = max(0, offset)

        if useCache:
            if self.findObjectInContents(obj, offset, self._currentSentenceContents) != -1:
                return self._currentSentenceContents

        boundary = pyatspi.TEXT_BOUNDARY_SENTENCE_START
        objects = self._getContentsForObj(obj, offset, boundary)
        state = obj.getState()
        if state.contains(pyatspi.STATE_EDITABLE) \
           and state.contains(pyatspi.STATE_FOCUSED):
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
            if firstStart == 0 and self.isTextBlockElement(firstObj):
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
            if self.findObjectInContents(obj, offset, self._currentCharacterContents) != -1:
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
            if self.findObjectInContents(obj, offset, self._currentWordContents) != -1:
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
        while prevObj and firstString:
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

        return objects

    def getObjectContentsAtOffset(self, obj, offset=0, useCache=True):
        if not obj:
            return []

        offset = max(0, offset)

        if useCache:
            if self.findObjectInContents(obj, offset, self._currentObjectContents) != -1:
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

        return objects

    def _contentIsSubsetOf(self, contentA, contentB):
        objA, startA, endA, stringA = contentA
        objB, startB, endB, stringB = contentB
        if objA == objB:
            setA = set(range(startA, endA))
            setB = set(range(startB, endB))
            return setA.issubset(setB)

        return False

    def getLineContentsAtOffset(self, obj, offset, layoutMode=None, useCache=True):
        if not obj:
            return []

        text = self.queryNonEmptyText(obj)
        offset = max(0, offset)

        if useCache:
            if self.findObjectInContents(obj, offset, self._currentLineContents) != -1:
                return self._currentLineContents

        if layoutMode is None:
            layoutMode = _settingsManager.getSetting('layoutMode')

        objects = []
        extents = self.getExtents(obj, offset, offset + 1)

        def _include(x):
            if x in objects:
                return False

            xObj, xStart, xEnd, xString = x
            if xStart == xEnd:
                return False

            xExtents = self.getExtents(xObj, xStart, xStart + 1)
            if self.isMathTopLevel(xObj) or self.isMath(obj):
                onSameLine = self.extentsAreOnSameLine(extents, xExtents, extents[3])
            else:
                onSameLine = self.extentsAreOnSameLine(extents, xExtents)
            return onSameLine

        boundary = pyatspi.TEXT_BOUNDARY_LINE_START
        objects = self._getContentsForObj(obj, offset, boundary)
        if not layoutMode:
            if useCache:
                self._currentLineContents = objects
            return objects

        firstObj, firstStart, firstEnd, firstString = objects[0]
        if (extents[2] == 0 and extents[3] == 0) or self.isMath(firstObj):
            extents = self.getExtents(firstObj, firstStart, firstEnd)

        lastObj, lastStart, lastEnd, lastString = objects[-1]
        if self.isMathTopLevel(lastObj):
            lastObj, lastEnd = self.lastContext(lastObj)
            lastEnd += 1

        prevObj, pOffset = self.findPreviousCaretInOrder(firstObj, firstStart)
        nextObj, nOffset = self.findNextCaretInOrder(lastObj, lastEnd - 1)

        # Check for things on the same line to the left of this object.
        while prevObj:
            text = self.queryNonEmptyText(prevObj)
            if text and text.getText(pOffset, pOffset + 1) in [" ", "\xa0"]:
                prevObj, pOffset = self.findPreviousCaretInOrder(prevObj, pOffset)

            onLeft = self._getContentsForObj(prevObj, pOffset, boundary)
            onLeft = list(filter(_include, onLeft))
            if not onLeft:
                break

            if self._contentIsSubsetOf(objects[0], onLeft[-1]):
                objects.pop(0)

            objects[0:0] = onLeft
            firstObj, firstStart = objects[0][0], objects[0][1]
            prevObj, pOffset = self.findPreviousCaretInOrder(firstObj, firstStart)

        # Check for things on the same line to the right of this object.
        while nextObj:
            text = self.queryNonEmptyText(nextObj)
            if text and text.getText(nOffset, nOffset + 1) in [" ", "\xa0"]:
                nextObj, nOffset = self.findNextCaretInOrder(nextObj, nOffset)

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

        if useCache:
            self._currentLineContents = objects

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
        msg = "WEB: Line contents for %s, %i: %s" % (obj, offset, line)
        debug.println(debug.LEVEL_INFO, msg, True)

        if not (line and line[0]):
            return []

        firstObj, firstOffset = line[0][0], line[0][1]
        msg = "WEB: First context on line is: %s, %i" % (firstObj, firstOffset)
        debug.println(debug.LEVEL_INFO, msg, True)

        obj, offset = self.previousContext(firstObj, firstOffset, True)
        if not obj and firstObj:
            msg = "WEB: Previous context is: %s, %i. Trying again." % (obj, offset)
            debug.println(debug.LEVEL_INFO, msg, True)
            self.clearCachedObjects()
            obj, offset = self.previousContext(firstObj, firstOffset, True)

        msg = "WEB: Previous context is: %s, %i" % (obj, offset)
        debug.println(debug.LEVEL_INFO, msg, True)

        contents = self.getLineContentsAtOffset(obj, offset, layoutMode, useCache)
        if not contents:
            msg = "WEB: Could not get line contents for %s, %i" % (obj, offset)
            debug.println(debug.LEVEL_INFO, msg, True)
            return []

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
        msg = "WEB: Line contents for %s, %i: %s" % (obj, offset, line)
        debug.println(debug.LEVEL_INFO, msg, True)

        if not (line and line[0]):
            return []

        lastObj, lastOffset = line[-1][0], line[-1][2] - 1
        math = self.getMathAncestor(lastObj)
        if math:
            lastObj, lastOffset = self.lastContext(math)

        msg = "WEB: Last context on line is: %s, %i" % (lastObj, lastOffset)
        debug.println(debug.LEVEL_INFO, msg, True)

        obj, offset = self.nextContext(lastObj, lastOffset, True)
        if not obj and lastObj:
            msg = "WEB: Next context is: %s, %i. Trying again." % (obj, offset)
            debug.println(debug.LEVEL_INFO, msg, True)
            self.clearCachedObjects()
            obj, offset = self.nextContext(lastObj, lastOffset, True)

        msg = "WEB: Next context is: %s, %i" % (obj, offset)
        debug.println(debug.LEVEL_INFO, msg, True)

        contents = self.getLineContentsAtOffset(obj, offset, layoutMode, useCache)
        if line == contents:
            obj, offset = self.nextContext(obj, offset, True)
            msg = "WEB: Got same line. Trying again with %s, %i" % (obj, offset)
            debug.println(debug.LEVEL_INFO, msg, True)
            contents = self.getLineContentsAtOffset(obj, offset, layoutMode, useCache)

        if not contents:
            msg = "WEB: Could not get line contents for %s, %i" % (obj, offset)
            debug.println(debug.LEVEL_INFO, msg, True)
            return []

        return contents

    def hasPresentableText(self, obj):
        text = self.queryNonEmptyText(obj)
        if not text:
            return False

        return bool(re.search(r"\w", text.getText(0, -1)))

    def updateCachedTextSelection(self, obj):
        if not self.inDocumentContent(obj):
            super().updateCachedTextSelection(obj)
            return

        if self.hasPresentableText(obj):
            super().updateCachedTextSelection(obj)

    def handleTextSelectionChange(self, obj):
        if not self.inDocumentContent(obj):
            return super().handleTextSelectionChange(obj)

        if self.hasPresentableText(obj) and super().handleTextSelectionChange(obj):
            return True

        handled = False
        descendants = pyatspi.findAllDescendants(obj, lambda x: self.hasPresentableText)
        for descendant in descendants:
            if handled:
                super().updateCachedTextSelection(descendant)
            else:
                handled = handled or super().handleTextSelectionChange(descendant)

        return handled

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

    def isFocusModeWidget(self, obj):
        try:
            role = obj.getRole()
            state = obj.getState()
        except:
            msg = "WEB: Exception getting role and state for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if state.contains(pyatspi.STATE_EDITABLE) \
           or state.contains(pyatspi.STATE_EXPANDABLE):
            return True

        focusModeRoles = [pyatspi.ROLE_COMBO_BOX,
                          pyatspi.ROLE_EMBEDDED,
                          pyatspi.ROLE_ENTRY,
                          pyatspi.ROLE_LIST_BOX,
                          pyatspi.ROLE_LIST_ITEM,
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
                          pyatspi.ROLE_TABLE_CELL,
                          pyatspi.ROLE_TABLE_ROW,
                          pyatspi.ROLE_TABLE,
                          pyatspi.ROLE_TREE_TABLE,
                          pyatspi.ROLE_TREE]

        if role in focusModeRoles \
           and not self.isTextBlockElement(obj):
            return True

        if self.isGridDescendant(obj) \
           or self.isMenuDescendant(obj) \
           or self.isToolBarDescendant(obj):
            return True

        if self.isContentEditableWithEmbeddedObjects(obj):
            return True

        return False

    def _textBlockElementRoles(self):
        roles = [pyatspi.ROLE_ARTICLE,
                 pyatspi.ROLE_CAPTION,
                 pyatspi.ROLE_COLUMN_HEADER,
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

        return roles

    def mnemonicShortcutAccelerator(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return super().mnemonicShortcutAccelerator(obj)

        try:
            attrs = dict([attr.split(":", 1) for attr in obj.getAttributes()])
        except:
            return ["", "", ""]

        keys = map(lambda x: x.replace("+", " "), attrs.get("keyshortcuts", "").split(" "))
        keys = map(lambda x: x.replace(" ", "+"), map(self.labelFromKeySequence, keys))
        return ["", " ".join(keys), ""]

    def unrelatedLabels(self, root, onlyShowing=True):
        if not (root and self.inDocumentContent(root)):
            return super().unrelatedLabels(root, onlyShowing)

        return []

    def isTextBlockElement(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return False

        rv = self._isTextBlockElement.get(hash(obj))
        if rv is not None:
            return rv

        try:
            role = obj.getRole()
            state = obj.getState()
        except:
            msg = "WEB: Exception getting role and state for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        textBlockElements = self._textBlockElementRoles()
        if not role in textBlockElements:
            rv = False
        elif state.contains(pyatspi.STATE_EDITABLE):
            rv = False
        elif role in [pyatspi.ROLE_DOCUMENT_FRAME, pyatspi.ROLE_DOCUMENT_WEB]:
            rv = True
        elif not state.contains(pyatspi.STATE_FOCUSABLE) and not state.contains(pyatspi.STATE_FOCUSED):
            rv = True
        else:
            rv = False

        self._isTextBlockElement[hash(obj)] = rv
        return rv

    def _advanceCaretInEmptyObject(self, obj):
        role = obj.getRole()
        if role == pyatspi.ROLE_TABLE_CELL and not self.queryNonEmptyText(obj):
            return not self._script._lastCommandWasStructNav

        return True

    def _treatAsLeafNode(self, obj):
        if super()._treatAsLeafNode(obj):
            return True

        if not self.isTextBlockElement(obj):
            return False

        for child in obj:
            if self.isTextBlockElement(child):
                return False

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

    def treatAsDiv(self, obj, offset=None):
        if not (obj and self.inDocumentContent(obj)):
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

    def isBlockquote(self, obj):
        if super().isBlockquote(obj):
            return True

        return self._getTag(obj) == 'blockquote'

    def speakMathSymbolNames(self, obj=None):
        obj = obj or orca_state.locusOfFocus
        return self.isMath(obj)

    def isInMath(self):
        return self.isMath(orca_state.locusOfFocus)

    def isMath(self, obj):
        rv = self._isMath.get(hash(obj))
        if rv is not None:
            return rv

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

        self._isMath[hash(obj)] = rv
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

        try:
            attrs = dict([attr.split(':', 1) for attr in obj.getAttributes()])
        except:
            return False

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

        try:
            attrs = dict([attr.split(':', 1) for attr in obj.getAttributes()])
        except:
            return []

        return attrs.get('notation', 'longdiv').split()

    def getMathFencedSeparators(self, obj):
        if not self.isMathFenced(obj):
            return ['']

        try:
            attrs = dict([attr.split(':', 1) for attr in obj.getAttributes()])
        except:
            return ['']

        return list(attrs.get('separators', ','))

    def getMathFences(self, obj):
        if not self.isMathFenced(obj):
            return ['', '']

        try:
            attrs = dict([attr.split(':', 1) for attr in obj.getAttributes()])
        except:
            return ['', '']

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
            if not obj:
                return False

            rv = self._shouldFilter.get(hash(obj))
            if rv is not None:
                return rv

            rv = True
            if (self.isTextBlockElement(obj) and not string.strip()) \
               or self.isEmptyAnchor(obj) \
               or (self.hasNoSize(obj) and not string.strip()) \
               or self.isHidden(obj) \
               or self.isOffScreenLabel(obj) \
               or self.isUselessImage(obj) \
               or self.isErrorForContents(obj, contents) \
               or self.isLabellingContents(obj, contents):
                rv = False

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

        isLabel = lambda x: x and x.getRole() == pyatspi.ROLE_LABEL
        rv = pyatspi.findAncestor(obj, isLabel) is not None
        self._isLabelDescendant[hash(obj)] = rv
        return rv

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

    def isToolBarDescendant(self, obj):
        if not obj:
            return False

        rv = self._isToolBarDescendant.get(hash(obj))
        if rv is not None:
            return rv

        isMenu = lambda x: x and x.getRole() == pyatspi.ROLE_TOOL_BAR
        rv = pyatspi.findAncestor(obj, isMenu) is not None
        self._isToolBarDescendant[hash(obj)] = rv
        return rv

    def isLayoutOnly(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return super().isLayoutOnly(obj)

        rv = self._isLayoutOnly.get(hash(obj))
        if rv is not None:
            return rv

        try:
            role = obj.getRole()
        except:
            msg = "ERROR: Exception getting role for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if role == pyatspi.ROLE_LIST:
            rv = self.treatAsDiv(obj)
        elif self.isMath(obj):
            rv = False
        elif self.isLandmark(obj):
            rv = False
        elif self.isDPub(obj):
            rv = False
        elif self.isFeed(obj):
            rv = False
        elif self.isFigure(obj):
            rv = False
        else:
            rv = super().isLayoutOnly(obj)

        self._isLayoutOnly[hash(obj)] = rv
        return rv

    def isOffScreenLabel(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return False

        rv = self._isOffScreenLabel.get(hash(obj))
        if rv is not None:
            return rv

        rv = False
        isLabelFor = lambda x: x.getRelationType() == pyatspi.RELATION_LABEL_FOR
        try:
            relationSet = obj.getRelationSet()
        except:
            pass
        else:
            relations = list(filter(isLabelFor, relationSet))
            if relations:
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
        try:
            iframes = pyatspi.findAllDescendants(root, isIframe)
        except:
            msg = "WEB: Exception getting descendant iframes of %s" % root
            debug.println(debug.LEVEL_INFO, msg, True)
            return None

        for iframe in iframes:
            if obj in iframe:
                # We won't change behavior, but we do want to log all bogosity.
                self._isBrokenChildParentTree(obj, iframe)

                msg = "WEB: Returning %s as iframe parent of detached %s" % (iframe, obj)
                debug.println(debug.LEVEL_INFO, msg, True)
                return iframe

        return None

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

    def labelTargets(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return False

        rv = self._labelTargets.get(hash(obj))
        if rv is not None:
            return rv

        rv = False

        isLabel = lambda r: r.getRelationType() == pyatspi.RELATION_LABEL_FOR
        relations = list(filter(isLabel, obj.getRelationSet()))
        if not relations:
            return []

        r = relations[0]
        rv = [r.getTarget(i) for i in range(r.getNTargets())]
        rv = [hash(x) for x in rv if x is not None]

        self._labelTargets[hash(obj)] = rv
        return rv

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

    def isLabellingContents(self, obj, contents=[]):
        targets = self.labelTargets(obj)
        if not contents:
            return bool(targets)

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
            if ancestor and ancestor.getRole() == pyatspi.ROLE_LABEL:
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
           and not 'Action' in pyatspi.listInterfaces(obj):
            rv = True

        self._isAnchor[hash(obj)] = rv
        return rv

    def isEmptyAnchor(self, obj):
        if not self.isAnchor(obj):
            return False

        return self.queryNonEmptyText(obj) is None

    def isChromeAlert(self, obj):
        if not (obj and obj.getRole() == pyatspi.ROLE_ALERT):
            return False

        if self.inDocumentContent(obj):
            return False

        return True

    def isTopLevelChromeAlert(self, obj):
        if not self.isChromeAlert(obj):
            return False

        parent = obj.parent
        while parent and self.isLayoutOnly(parent):
            parent = parent.parent

        return parent.getRole() == pyatspi.ROLE_FRAME

    def isClickableElement(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return False

        rv = self._isClickableElement.get(hash(obj))
        if rv is not None:
            return rv

        rv = False
        if not obj.getState().contains(pyatspi.STATE_FOCUSABLE) \
           and not self.isFocusModeWidget(obj):
            try:
                action = obj.queryAction()
                names = [action.getName(i) for i in range(action.nActions)]
            except NotImplementedError:
                rv = False
            else:
                rv = "click" in names

        self._isClickableElement[hash(obj)] = rv
        return rv

    def isEditableDescendantOfComboBox(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return super().isEditableDescendantOfComboBox(obj)

        rv = self._isEditableDescendantOfComboBox.get(hash(obj))
        if rv is not None:
            return rv

        try:
            state = obj.getState()
        except:
            msg = "ERROR: Exception getting state for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if not state.contains(pyatspi.STATE_EDITABLE):
            return False

        isComboBox = lambda x: x and x.getRole() == pyatspi.ROLE_COMBO_BOX
        rv = pyatspi.findAncestor(obj, isComboBox) is not None

        self._isEditableDescendantOfComboBox[hash(obj)] = rv
        return rv

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

        rv = self._isDPub.get(hash(obj))
        if rv is not None:
            return rv

        roles = self._getXMLRoles(obj)
        rv = bool(list(filter(lambda x: x.startswith("doc-"), roles)))
        self._isDPub[hash(obj)] = rv
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

        # Remove this when we bump dependencies to 2.26
        try:
            relationType = pyatspi.RELATION_ERROR_FOR
        except:
            rv = False
        else:
            isMessage = lambda r: r.getRelationType() == relationType
            rv = bool(list(filter(isMessage, obj.getRelationSet())))

        self._isErrorMessage[hash(obj)] = rv
        return rv

    def isFeed(self, obj):
        return 'feed' in self._getXMLRoles(obj)

    def isFigure(self, obj):
        return 'figure' in self._getXMLRoles(obj)

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

        rv = self._isLiveRegion.get(hash(obj))
        if rv is not None:
            return rv

        try:
            attrs = dict([attr.split(':', 1) for attr in obj.getAttributes()])
        except:
            attrs = {}

        rv = 'container-live' in attrs
        self._isLiveRegion[hash(obj)] = rv
        return rv

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

        rv = obj.getRole() == pyatspi.ROLE_TOOL_TIP

        self._isNonNavigablePopup[hash(obj)] = rv
        return rv

    def hasUselessCanvasDescendant(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return False

        rv = self._hasUselessCanvasDescendant.get(hash(obj))
        if rv is not None:
            return rv

        isCanvas = lambda x: x and x.getRole() == pyatspi.ROLE_CANVAS
        try:
            canvases = pyatspi.findAllDescendants(obj, isCanvas)
        except:
            msg = "WEB: Exception getting descendant canvases of %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            rv = False
        else:
            rv = len(list(filter(self.isUselessImage, canvases))) > 0

        self._hasUselessCanvasDescendant[hash(obj)] = rv
        return rv

    def isSwitch(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return super().isSwitch(obj)

        return 'switch' in self._getXMLRoles(obj)

    def isImageMap(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return False

        rv = self._isImageMap.get(hash(obj))
        if rv is not None:
            return rv

        role = obj.getRole()
        rv = role == pyatspi.ROLE_IMAGE_MAP
        if rv == False and role == pyatspi.ROLE_IMAGE:
            rv = obj.childCount and obj[0].getRole() == pyatspi.ROLE_LINK

        self._isImageMap[hash(obj)] = rv
        return rv

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

    def isUselessImage(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return False

        rv = self._isUselessImage.get(hash(obj))
        if rv is not None:
            return rv

        rv = True
        if obj.getRole() not in [pyatspi.ROLE_IMAGE, pyatspi.ROLE_CANVAS]:
            rv = False
        if rv and (obj.name or obj.description or obj.childCount):
            rv = False
        if rv and (self.isClickableElement(obj) or self.hasLongDesc(obj)):
            rv = False
        if rv and obj.parent.getRole() == pyatspi.ROLE_LINK:
            uri = self.uri(obj.parent)
            if uri and not uri.startswith('javascript'):
                rv = False
        if rv and 'Image' in pyatspi.listInterfaces(obj):
            image = obj.queryImage()
            if image.imageDescription:
                rv = False
            elif not self.hasExplicitName(obj):
                width, height = image.getImageSize()
                if width > 25 and height > 25:
                    rv = False
        if rv and 'Text' in pyatspi.listInterfaces(obj):
            rv = self.queryNonEmptyText(obj) is None

        self._isUselessImage[hash(obj)] = rv
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

        rv = self._hasExplicitName.get(hash(obj))
        if rv is not None:
            return rv

        try:
            attrs = dict([attr.split(':', 1) for attr in obj.getAttributes()])
        except:
            attrs = {}

        rv = attrs.get('explicit-name') == 'true'
        self._hasExplicitName[hash(obj)] = rv
        return rv

    def hasLongDesc(self, obj):
        if not (obj and self.inDocumentContent(obj)):
            return False

        rv = self._hasLongDesc.get(hash(obj))
        if rv is not None:
            return rv

        try:
            action = obj.queryAction()
        except NotImplementedError:
            rv = False
        else:
            names = [action.getName(i) for i in range(action.nActions)]
            rv = "showlongdesc" in names

        self._hasLongDesc[hash(obj)] = rv
        return rv

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
        if not self.inDocumentContent() or self.inTopLevelWebApp():
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

        rv = self._actualLabels.get(hash(obj))
        if rv is not None:
            return rv

        rv = super().labelsForObject(obj)
        if not self.inDocumentContent(obj):
            return rv

        rv = list(filter(lambda x: x and x.getRole() == pyatspi.ROLE_LABEL, rv))
        self._actualLabels[hash(obj)] = rv
        return rv

    def isSpinnerEntry(self, obj):
        if not self.inDocumentContent(obj):
            return False

        # TODO - JD: Ideally, things that look and act like spinners (such number inputs)
        # would look and act like platform native spinners. That's not true for Gecko. And
        # the only thing that's funkier is what we get from WebKitGtk. Try to at least get
        # the two engines into alignment before migrating Epiphany support to the web script.
        if obj.getState().contains(pyatspi.STATE_EDITABLE) \
           and obj.parent.getRole() == pyatspi.ROLE_SPIN_BUTTON:
            return True

        return False

    def eventIsSpinnerNoise(self, event):
        if event.type.startswith("object:text-changed") and self.isSpinnerEntry(event.source):
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

    def eventIsChromeNoise(self, event):
        if self.inDocumentContent(event.source):
            return False

        try:
            role = event.source.getRole()
        except:
            msg = "WEB: Exception getting role for %s" % event.source
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        eType = event.type
        if eType.startswith("object:text-") or eType.endswith("accessible-name"):
            return role in [pyatspi.ROLE_STATUS_BAR, pyatspi.ROLE_LABEL]
        if eType.startswith("object:children-changed"):
            return True

        return False

    def eventIsAutocompleteNoise(self, event):
        if not self.inDocumentContent(event.source):
            return False

        isListBoxItem = lambda x: x and x.parent and x.parent.getRole() == pyatspi.ROLE_LIST_BOX
        isMenuItem = lambda x: x and x.parent and x.parent.getRole() == pyatspi.ROLE_MENU
        isComboBoxItem = lambda x: x and x.parent and x.parent.getRole() == pyatspi.ROLE_COMBO_BOX

        if event.source.getState().contains(pyatspi.STATE_EDITABLE) \
           and event.type.startswith("object:text-"):
            obj, offset = self.getCaretContext()
            if isListBoxItem(obj) or isMenuItem(obj):
                return True

            if obj == event.source and isComboBoxItem(obj):
                lastKey, mods = self.lastKeyAndModifiers()
                if lastKey in ["Down", "Up"]:
                    return True

        return False

    def eventIsChromeAutocompleteNoise(self, event):
        if self.inDocumentContent(event.source):
            return False

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

    def eventIsChromePageSwitchNoise(self, event):
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

        return self._treatTextObjectAsWhole(event.source)

    # TODO - JD: As an experiment, we're stopping these at the event manager.
    # If that works, this can be removed.
    def eventIsEOCAdded(self, event):
        if not self.inDocumentContent(event.source):
            return False

        if event.type.startswith("object:text-changed:insert"):
            return self.EMBEDDED_OBJECT_CHARACTER in event.any_data

        return False

    def caretMovedToSamePageFragment(self, event):
        if not event.type.startswith("object:text-caret-moved"):
            return False

        if event.source.getState().contains(pyatspi.STATE_EDITABLE):
            return False

        linkURI = self.uri(orca_state.locusOfFocus)
        docURI = self.documentFrameURI()
        if linkURI == docURI:
            return True

        sourceID = self._getID(event.source)
        if sourceID:
            parseResult = urllib.parse.urlparse(docURI)
            return parseResult.fragment == sourceID

        return False

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

        isTextBlockRole = role in self._textBlockElementRoles() or self.isLink(obj)
        if state.contains(pyatspi.STATE_EDITABLE):
            rv = isTextBlockRole
        elif not self.isDocument(obj):
            document = self.getDocumentForObject(obj)
            rv = self.isContentEditableWithEmbeddedObjects(document)

        self._isContentEditableWithEmbeddedObjects[hash(obj)] = rv
        return rv

    @staticmethod
    def getHyperlinkRange(obj):
        try:
            hyperlink = obj.queryHyperlink()
            start, end = hyperlink.startIndex, hyperlink.endIndex
        except NotImplementedError:
            msg = "WEB: %s does not implement the hyperlink interface" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return -1, -1
        except:
            msg = "WEB: Exception getting hyperlink indices for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return -1, -1

        return start, end

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

    @staticmethod
    def getChildIndex(obj, offset):
        try:
            hypertext = obj.queryHypertext()
        except NotImplementedError:
            msg = "WEB: %s does not implement the hypertext interface" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return -1
        except:
            msg = "WEB: Exception querying hypertext interface for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return -1

        return hypertext.getLinkIndex(offset)

    def getChildAtOffset(self, obj, offset):
        index = self.getChildIndex(obj, offset)
        if index == -1:
            return None

        try:
            child = obj[index]
        except:
            return None

        return child

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
            self._currentAttrs.pop(hash(obj))
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

    def doNotDescendForCaret(self, obj):
        if not obj or self.isZombie(obj):
            return True

        try:
            childCount = obj.childCount
        except:
            msg = "WEB: Exception getting childCount for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return True
        if not childCount or self.isParentOfNullChild(obj):
            return True

        if self.isHidden(obj) or self.isOffScreenLabel(obj):
            return True

        if self.isNonNavigableEmbeddedDocument(obj):
            return True

        role = obj.getRole()
        if role == pyatspi.ROLE_LINK \
           and (self.hasExplicitName(obj) or self.hasUselessCanvasDescendant(obj)):
            return True

        if self.isTextBlockElement(obj):
            return False

        if self.isImageMap(obj):
            return False

        doNotDescend = [pyatspi.ROLE_COMBO_BOX,
                        pyatspi.ROLE_IMAGE,
                        pyatspi.ROLE_LIST_BOX,
                        pyatspi.ROLE_MENU_BAR,
                        pyatspi.ROLE_MENU,
                        pyatspi.ROLE_MENU_ITEM,
                        pyatspi.ROLE_CHECK_BOX,
                        pyatspi.ROLE_RADIO_BUTTON,
                        pyatspi.ROLE_PUSH_BUTTON,
                        pyatspi.ROLE_TOGGLE_BUTTON,
                        pyatspi.ROLE_TOOL_BAR,
                        pyatspi.ROLE_TOOL_TIP,
                        pyatspi.ROLE_TREE,
                        pyatspi.ROLE_TREE_TABLE]

        if not self._script.browseModeIsSticky():
            doNotDescend.append(pyatspi.ROLE_EMBEDDED)

        return role in doNotDescend

    def searchForCaretContext(self, obj):
        contextObj, contextOffset = None, -1
        while obj:
            try:
                offset = obj.queryText().caretOffset
            except:
                obj = None
            else:
                contextObj, contextOffset = obj, offset
                childIndex = self.getChildIndex(obj, offset)
                if childIndex >= 0 and obj.childCount:
                    obj = obj[childIndex]
                else:
                    break

        if contextObj:
            return self.findNextCaretInOrder(contextObj, max(-1, contextOffset - 1))

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

    def getCaretContext(self, documentFrame=None, getZombieReplicant=False):
        if not documentFrame or self.isZombie(documentFrame):
            documentFrame = self.documentFrame()

        if not documentFrame:
            return self._getCaretContextViaLocusOfFocus()

        context = self._caretContexts.get(hash(documentFrame.parent))
        if not context:
            obj, offset = self.searchForCaretContext(documentFrame)
        elif not getZombieReplicant:
            return context
        elif self.isZombie(context[0]):
            obj, offset = self.findContextReplicant()
            if obj:
                caretObj, caretOffset = self.searchForCaretContext(obj.parent)
                if caretObj and not self.isZombie(caretObj):
                    obj, offset = caretObj, caretOffset
        else:
            obj, offset = context

        self.setCaretContext(obj, offset, documentFrame)

        return obj, offset

    def _getCaretContextPathRoleAndName(self, documentFrame=None):
        documentFrame = documentFrame or self.documentFrame()
        if not documentFrame:
            return [-1], None, None

        rv = self._contextPathsRolesAndNames.get(hash(documentFrame.parent))
        if not rv:
            return [-1], None, None

        return rv

    def getObjectFromPath(self, path):
        start = self._script.app
        rv = None
        for p in path:
            if p == -1:
                continue
            try:
                start = start[p]
            except:
                break
        else:
            rv = start

        return rv

    def clearCaretContext(self, documentFrame=None):
        self.clearContentCache()
        documentFrame = documentFrame or self.documentFrame()
        if not documentFrame:
            return

        parent = documentFrame.parent
        self._caretContexts.pop(hash(parent), None)
        self._priorContexts.pop(hash(parent), None)

    def findContextReplicant(self, documentFrame=None, matchRole=True, matchName=True):
        path, oldRole, oldName = self._getCaretContextPathRoleAndName(documentFrame)
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
        if not text:
            if self._advanceCaretInEmptyObject(obj) \
               and (self.isTextBlockElement(obj) or self.isEmptyAnchor(obj)):
                nextObj, nextOffset = self.nextContext(obj, offset)
                if nextObj:
                    msg = "WEB: First caret context for %s, %i is %s, %i" % (obj, offset, nextObj, nextOffset)
                    debug.println(debug.LEVEL_INFO, msg, True)
                    return nextObj, nextOffset

            msg = "WEB: First caret context for %s, %i is %s, %i" % (obj, offset, obj, 0)
            debug.println(debug.LEVEL_INFO, msg, True)
            return obj, 0

        if offset >= text.characterCount:
            if self.isLink(obj) and self.isContentEditableWithEmbeddedObjects(obj):
                nextObj, nextOffset = self.nextContext(obj, text.characterCount)
                if nextObj:
                    msg = "WEB: First caret context for %s, %i is %s, %i" % (obj, offset, nextObj, nextOffset)
                    debug.println(debug.LEVEL_INFO, msg, True)
                    return nextObj, nextOffset

            msg = "WEB: First caret context for %s, %i is %s, %i" % (obj, offset, obj, text.characterCount)
            debug.println(debug.LEVEL_INFO, msg, True)
            return obj, text.characterCount

        allText = text.getText(0, -1)
        offset = max (0, offset)
        if allText[offset] != self.EMBEDDED_OBJECT_CHARACTER or role == pyatspi.ROLE_ENTRY:
            msg = "WEB: First caret context for %s, %i is %s, %i" % (obj, offset, obj, offset)
            debug.println(debug.LEVEL_INFO, msg, True)
            return obj, offset

        child = self.getChildAtOffset(obj, offset)
        if not child:
            msg = "WEB: First caret context for %s, %i is %s, %i" % (obj, offset, None, -1)
            debug.println(debug.LEVEL_INFO, msg, True)
            return None, -1

        return self.findFirstCaretContext(child, 0)

    def findNextCaretInOrder(self, obj=None, offset=-1):
        if not obj:
            obj, offset = self.getCaretContext()

        if not obj or not self.inDocumentContent(obj):
            return None, -1

        if not (self.isHidden(obj) or self.isOffScreenLabel(obj) or self.isNonNavigablePopup(obj)):
            text = self.queryNonEmptyText(obj)
            if text:
                allText = text.getText(0, -1)
                for i in range(offset + 1, len(allText)):
                    child = self.getChildAtOffset(obj, i)
                    if child and not self.isZombie(child) and not self.isEmptyAnchor(child) \
                       and not self.isUselessImage(child):
                        return self.findNextCaretInOrder(child, -1)
                    if allText[i] != self.EMBEDDED_OBJECT_CHARACTER:
                        return obj, i
            elif not self.doNotDescendForCaret(obj) and obj.childCount:
                return self.findNextCaretInOrder(obj[0], -1)
            elif offset < 0 and not self.isTextBlockElement(obj) and not self.hasNoSize(obj) \
                 and not self.isUselessImage(obj) and not self.isParentOfNullChild(obj):
                return obj, 0

        # If we're here, start looking up the the tree, up to the document.
        documentFrame = self.documentFrame()
        if self.isSameObject(obj, documentFrame):
            return None, -1

        while obj and obj.parent:
            if self.isDetachedDocument(obj.parent):
                obj = self.iframeForDetachedDocument(obj.parent)
                continue

            parent = obj.parent
            if self.isZombie(parent):
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
                return self.findNextCaretInOrder(parent, start)

            index = obj.getIndexInParent() + 1
            try:
                parentChildCount = parent.childCount
            except:
                msg = "WEB: Exception getting childCount for %s" % parent
                debug.println(debug.LEVEL_INFO, msg, True)
            else:
                if 0 < index < parentChildCount:
                    return self.findNextCaretInOrder(parent[index], -1)
            obj = parent

        return None, -1

    def findPreviousCaretInOrder(self, obj=None, offset=-1):
        if not obj:
            obj, offset = self.getCaretContext()

        if not obj or not self.inDocumentContent(obj):
            return None, -1

        if not (self.isHidden(obj) or self.isOffScreenLabel(obj) or self.isNonNavigablePopup(obj)):
            text = self.queryNonEmptyText(obj)
            if text:
                allText = text.getText(0, -1)
                if offset == -1 or offset > len(allText):
                    offset = len(allText)
                for i in range(offset - 1, -1, -1):
                    child = self.getChildAtOffset(obj, i)
                    if child and not self.isZombie(child) and not self.isEmptyAnchor(child) \
                       and not self.isUselessImage(child):
                        return self.findPreviousCaretInOrder(child, -1)
                    if allText[i] != self.EMBEDDED_OBJECT_CHARACTER:
                        return obj, i
            elif not self.doNotDescendForCaret(obj) and obj.childCount:
                return self.findPreviousCaretInOrder(obj[obj.childCount - 1], -1)
            elif offset < 0 and not self.isTextBlockElement(obj) and not self.hasNoSize(obj) \
                 and not self.isUselessImage(obj) and not self.isParentOfNullChild(obj):
                return obj, 0

        # If we're here, start looking up the the tree, up to the document.
        documentFrame = self.documentFrame()
        if self.isSameObject(obj, documentFrame):
            return None, -1

        while obj and obj.parent:
            if self.isDetachedDocument(obj.parent):
                obj = self.iframeForDetachedDocument(obj.parent)
                continue

            parent = obj.parent
            if self.isZombie(parent):
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
                return self.findPreviousCaretInOrder(parent, start)

            index = obj.getIndexInParent() - 1
            try:
                parentChildCount = parent.childCount
            except:
                msg = "WEB: Exception getting childCount for %s" % parent
                debug.println(debug.LEVEL_INFO, msg, True)
            else:
                if 0 <= index < parentChildCount:
                    return self.findPreviousCaretInOrder(parent[index], -1)
            obj = parent

        return None, -1

    def handleAsLiveRegion(self, event):
        if not _settingsManager.getSetting('inferLiveRegions'):
            return False

        return self.isLiveRegion(event.source)

    def getPageObjectCount(self, obj):
        result = {'landmarks': 0,
                  'headings': 0,
                  'forms': 0,
                  'tables': 0,
                  'visitedLinks': 0,
                  'unvisitedLinks': 0}

        docframe = self.documentFrame(obj)
        col = docframe.queryCollection()
        stateset = pyatspi.StateSet()
        roles = [pyatspi.ROLE_HEADING,
                 pyatspi.ROLE_LINK,
                 pyatspi.ROLE_TABLE,
                 pyatspi.ROLE_FORM,
                 pyatspi.ROLE_SECTION, # We can nuke this when Firefox correcly maps landmarks
                 pyatspi.ROLE_LANDMARK]
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
