# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
# Copyright 2010-2011 Orca Team
# Copyright 2011-2015 Igalia, S.L.
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
                "Copyright (c) 2010-2011 Orca Team" \
                "Copyright (c) 2011-2015 Igalia, S.L."
__license__   = "LGPL"

import pyatspi
import urllib

from orca import debug
from orca import messages
from orca import object_properties
from orca import orca_state
from orca import settings
from orca import settings_manager
from orca import speech_generator

_settingsManager = settings_manager.getManager()


class SpeechGenerator(speech_generator.SpeechGenerator):

    def __init__(self, script):
        super().__init__(script)

    def _generateOldAncestors(self, obj, **args):
        if args.get('index', 0) > 0:
            return []

        priorObj = args.get('priorObj')
        if self._script.utilities.isInlineIframeDescendant(priorObj):
            return []

        return super()._generateOldAncestors(obj, **args)

    def _generateNewAncestors(self, obj, **args):
        if args.get('index', 0) > 0 \
           and not self._script.utilities.isListDescendant(obj):
            return []

        if self._script.utilities.isInlineIframeDescendant(obj):
            return []

        return super()._generateNewAncestors(obj, **args)

    def _generateAncestors(self, obj, **args):
        if not self._script.utilities.inDocumentContent(obj):
            return super()._generateAncestors(obj, **args)

        if self._script.inSayAll() and obj == orca_state.locusOfFocus:
            return []

        result = []
        priorObj = args.get('priorObj')
        if priorObj and self._script.utilities.inDocumentContent(priorObj):
            priorDoc = self._script.utilities.getDocumentForObject(priorObj)
            doc = self._script.utilities.getDocumentForObject(obj)
            if priorDoc != doc and not self._script.utilities.getDocumentForObject(doc):
                result = [super()._generateName(doc)]

        if self._script.utilities.isLink(obj) \
           or self._script.utilities.isLandmark(obj) \
           or self._script.utilities.isMath(obj):
            return result

        args['stopAtRoles'] = [pyatspi.ROLE_DOCUMENT_FRAME,
                               pyatspi.ROLE_DOCUMENT_WEB,
                               pyatspi.ROLE_EMBEDDED,
                               pyatspi.ROLE_INTERNAL_FRAME,
                               pyatspi.ROLE_MATH,
                               pyatspi.ROLE_MENU_BAR,
                               pyatspi.ROLE_TOOL_BAR]
        args['skipRoles'] = [pyatspi.ROLE_PARAGRAPH,
                             pyatspi.ROLE_HEADING,
                             pyatspi.ROLE_LABEL,
                             pyatspi.ROLE_LINK,
                             pyatspi.ROLE_LIST_ITEM,
                             pyatspi.ROLE_TEXT]

        if self._script.utilities.isEditableDescendantOfComboBox(obj):
            args['skipRoles'].append(pyatspi.ROLE_COMBO_BOX)

        result.extend(super()._generateAncestors(obj, **args))

        return result

    def _generateAllTextSelection(self, obj, **args):
        if self._script.utilities.isZombie(obj) \
           or obj != orca_state.locusOfFocus:
            return []

        # TODO - JD: These (and the default script's) need to
        # call utility methods rather than generate it.
        return super()._generateAllTextSelection(obj, **args)

    def _generateAnyTextSelection(self, obj, **args):
        if self._script.utilities.isZombie(obj) \
           or obj != orca_state.locusOfFocus:
            return []

        # TODO - JD: These (and the default script's) need to
        # call utility methods rather than generate it.
        return super()._generateAnyTextSelection(obj, **args)

    def _generateHasPopup(self, obj, **args):
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        if not self._script.utilities.inDocumentContent(obj):
            return []

        result = []
        popupType = self._script.utilities.popupType(obj)
        if popupType == 'dialog':
            result = [messages.HAS_POPUP_DIALOG]
        elif popupType == 'grid':
            result = [messages.HAS_POPUP_GRID]
        elif popupType == 'listbox':
            result = [messages.HAS_POPUP_LISTBOX]
        elif popupType in ('menu', 'true'):
            result = [messages.HAS_POPUP_MENU]
        elif popupType == 'tree':
            result = [messages.HAS_POPUP_TREE]

        if result:
            result.extend(self.voice(speech_generator.SYSTEM))

        return result

    def _generateClickable(self, obj, **args):
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        if not self._script.utilities.inDocumentContent(obj):
            return []

        if not args.get('mode', None):
            args['mode'] = self._mode

        args['stringType'] = 'clickable'
        if self._script.utilities.isClickableElement(obj):
            result = [self._script.formatting.getString(**args)]
            result.extend(self.voice(speech_generator.SYSTEM))
            return result

        return []

    def _generateDescription(self, obj, **args):
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        if not self._script.utilities.inDocumentContent(obj):
            return super()._generateDescription(obj, **args)

        if self._script.utilities.isZombie(obj):
            return []

        if self._script.utilities.preferDescriptionOverName(obj):
            return []

        role = args.get('role', obj.getRole())
        if obj != orca_state.locusOfFocus:
            if role in [pyatspi.ROLE_ALERT, pyatspi.ROLE_DIALOG]:
                return super()._generateDescription(obj, **args)
            if not args.get('inMouseReview'):
                return []

        formatType = args.get('formatType')
        if formatType == 'basicWhereAmI' and self._script.utilities.isLiveRegion(obj):
            return self._script.liveRegionManager.generateLiveRegionDescription(obj, **args)

        if role == pyatspi.ROLE_TEXT and formatType != 'basicWhereAmI':
            return []

        # TODO - JD: This is private.
        if role == pyatspi.ROLE_LINK and self._script._lastCommandWasCaretNav:
            return []

        return super()._generateDescription(obj, **args)

    def _generateHasLongDesc(self, obj, **args):
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        if not self._script.utilities.inDocumentContent(obj):
            return []

        if not args.get('mode', None):
            args['mode'] = self._mode

        args['stringType'] = 'haslongdesc'
        if self._script.utilities.hasLongDesc(obj):
            result = [self._script.formatting.getString(**args)]
            result.extend(self.voice(speech_generator.SYSTEM))
            return result

        return []

    def _generateHasDetails(self, obj, **args):
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        if not self._script.utilities.inDocumentContent(obj):
            return super()._generateHasDetails(obj, **args)

        objs = self._script.utilities.detailsIn(obj)
        if not objs:
            return []

        objString = lambda x: str.strip("%s %s" % (x.name, self.getLocalizedRoleName(x)))
        toPresent = ", ".join(set(map(objString, objs)))

        args['stringType'] = 'hasdetails'
        result = [self._script.formatting.getString(**args) % toPresent]
        result.extend(self.voice(speech_generator.SYSTEM))
        return result

    def _generateAllDetails(self, obj, **args):
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        objs = self._script.utilities.detailsIn(obj)
        if not objs:
            container = pyatspi.findAncestor(obj, self._script.utilities.hasDetails)
            objs = self._script.utilities.detailsIn(container)

        if not objs:
            return []

        args['stringType'] = 'hasdetails'
        result = [self._script.formatting.getString(**args) % ""]
        result.extend(self.voice(speech_generator.SYSTEM))

        result = []
        for o in objs:
            result.append(self.getLocalizedRoleName(o))
            result.extend(self.voice(speech_generator.SYSTEM))

            string = self._script.utilities.expandEOCs(o)
            if not string.strip():
                continue

            result.append(string)
            result.extend(self.voice(speech_generator.DEFAULT))
            result.extend(self._generatePause(o))

        return result

    def _generateDetailsFor(self, obj, **args):
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        if not self._script.utilities.inDocumentContent(obj):
            return super()._generateDetailsFor(obj, **args)

        objs = self._script.utilities.detailsFor(obj)
        if not objs:
            return []

        if args.get('leaving'):
            return []

        lastKey, mods = self._script.utilities.lastKeyAndModifiers()
        if (lastKey in ['Down', 'Right'] or self._script.inSayAll()) and args.get('startOffset'):
            return []
        if lastKey in ['Up', 'Left']:
            text = self._script.utilities.queryNonEmptyText(obj)
            if text and args.get('endOffset') not in [None, text.characterCount]:
                return []

        result = []
        objArgs = {'stringType': 'detailsfor', 'mode': args.get('mode')}
        for o in objs:
            string = self._script.utilities.displayedText(o) or self.getLocalizedRoleName(o)
            words = string.split()
            if len(words) > 5:
                words = words[0:5] + ['...']

            result.append(self._script.formatting.getString(**objArgs) % " ".join(words))
            result.extend(self.voice(speech_generator.SYSTEM))
            result.extend(self._generatePause(o, **objArgs))

        return result

    def _generateLabelOrName(self, obj, **args):
        if not self._script.utilities.inDocumentContent(obj):
            return super()._generateLabelOrName(obj, **args)

        if self._script.utilities.isTextBlockElement(obj) \
           and not self._script.utilities.isLandmark(obj) \
           and not self._script.utilities.isDPub(obj) \
           and not self._script.utilities.isContentSuggestion(obj):
            return []

        if obj.name:
            name = obj.name
            if not self._script.utilities.hasExplicitName(obj):
                name = name.strip()
            result = [name]
            result.extend(self.voice(speech_generator.DEFAULT))
            return result

        return super()._generateLabelOrName(obj, **args)

    def _generateName(self, obj, **args):
        if not self._script.utilities.inDocumentContent(obj):
            return super()._generateName(obj, **args)

        if self._script.utilities.isTextBlockElement(obj) \
           and not self._script.utilities.isLandmark(obj) \
           and not self._script.utilities.isDPub(obj):
            return []

        role = args.get('role', obj.getRole())
        alwaysPresent = [pyatspi.ROLE_PUSH_BUTTON,
                         pyatspi.ROLE_IMAGE]

        if obj.parent and obj.name and obj.name == obj.parent.name \
           and obj != orca_state.locusOfFocus and role not in alwaysPresent:
            return []

        # TODO - JD: Once the formatting strings are vastly cleaned up
        # or simply removed, hacks like this won't be needed.
        if role in [pyatspi.ROLE_COMBO_BOX, pyatspi.ROLE_SPIN_BUTTON]:
            return super()._generateName(obj, **args)

        if obj.name:
            if self._script.utilities.preferDescriptionOverName(obj):
                result = [obj.description]
            elif self._script.utilities.isLink(obj) \
                 and not self._script.utilities.hasExplicitName(obj):
                return []
            else:
                name = obj.name
                if not self._script.utilities.hasExplicitName(obj):
                    name = name.strip()
                result = [name]

            result.extend(self.voice(speech_generator.DEFAULT))
            return result

        return super()._generateName(obj, **args)

    def _generateLabel(self, obj, **args):
        if not self._script.utilities.inDocumentContent(obj):
            return super()._generateLabel(obj, **args)

        if self._script.utilities.isTextBlockElement(obj):
            return []

        label, objects = self._script.utilities.inferLabelFor(obj)
        if label:
            result = [label]
            result.extend(self.voice(speech_generator.DEFAULT))
            return result

        return super()._generateLabel(obj, **args)

    def _generateNewNodeLevel(self, obj, **args):
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        if self._script.utilities.isTextBlockElement(obj) \
           or self._script.utilities.isLink(obj):
            return []

        return super()._generateNewNodeLevel(obj, **args)

    def _generateLeaving(self, obj, **args):
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        if not args.get('leaving'):
            return []

        if self._script.utilities.inDocumentContent(obj) \
           and not self._script.utilities.inDocumentContent(orca_state.locusOfFocus):
            result = ['']
            result.extend(self.voice(speech_generator.SYSTEM))
            return result

        return super()._generateLeaving(obj, **args)

    def _generateNewRadioButtonGroup(self, obj, **args):
        # TODO - JD: Looking at the default speech generator's method, this
        # is all kinds of broken. Until that can be sorted out, try to filter
        # out some of the noise....
        return []

    def _generateNumberOfChildren(self, obj, **args):
        if _settingsManager.getSetting('onlySpeakDisplayedText') \
           or _settingsManager.getSetting('speechVerbosityLevel') == settings.VERBOSITY_LEVEL_BRIEF:
            return []

        # We handle things even for non-document content due to issues in
        # other toolkits (e.g. exposing list items to us that are not
        # exposed to sighted users)
        role = args.get('role', obj.getRole())
        if role not in [pyatspi.ROLE_LIST, pyatspi.ROLE_LIST_BOX]:
            return super()._generateNumberOfChildren(obj, **args)

        setsize = self._script.utilities.getSetSize(obj[0])
        if setsize is None:
            children = [x for x in obj if x.getRole() == pyatspi.ROLE_LIST_ITEM]
            setsize = len(children)

        if not setsize:
            return []

        result = [messages.listItemCount(setsize)]
        result.extend(self.voice(speech_generator.SYSTEM))
        return result

    # TODO - JD: Yet another dumb generator method we should kill.
    def _generateTextRole(self, obj, **args):
        return self._generateRoleName(obj, **args)

    def getLocalizedRoleName(self, obj, **args):
        if not self._script.utilities.inDocumentContent(obj):
            return super().getLocalizedRoleName(obj, **args)

        roledescription = self._script.utilities.getRoleDescription(obj)
        if roledescription:
            return roledescription

        return super().getLocalizedRoleName(obj, **args)

    def _generateRealActiveDescendantDisplayedText(self, obj, **args):
        if not self._script.utilities.inDocumentContent(obj):
            return super()._generateRealActiveDescendantDisplayedText(obj, **args)

        return self._generateDisplayedText(obj, **args)

    def _generateRoleName(self, obj, **args):
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        if not self._script.utilities.inDocumentContent(obj):
            return super()._generateRoleName(obj, **args)

        result = []
        acss = self.voice(speech_generator.SYSTEM)

        roledescription = self._script.utilities.getRoleDescription(obj)
        if roledescription:
            result = [roledescription]
            result.extend(acss)
            return result

        role = args.get('role', obj.getRole())
        enabled, disabled = self._getEnabledAndDisabledContextRoles()
        if role in disabled:
            return []

        force = args.get('force', False)
        start = args.get('startOffset')
        end = args.get('endOffset')
        index = args.get('index', 0)
        total = args.get('total', 1)

        if not force:
            doNotSpeak = [pyatspi.ROLE_FOOTER,
                          pyatspi.ROLE_FORM,
                          pyatspi.ROLE_LABEL,
                          pyatspi.ROLE_MENU_ITEM,
                          pyatspi.ROLE_PARAGRAPH,
                          pyatspi.ROLE_SECTION,
                          pyatspi.ROLE_REDUNDANT_OBJECT,
                          pyatspi.ROLE_UNKNOWN]
        else:
            doNotSpeak = [pyatspi.ROLE_UNKNOWN]

        if not force:
            doNotSpeak.append(pyatspi.ROLE_TABLE_CELL)
            doNotSpeak.append(pyatspi.ROLE_TEXT)
            doNotSpeak.append(pyatspi.ROLE_STATIC)
            if args.get('string'):
                doNotSpeak.append("ROLE_CONTENT_SUGGESTION")
            if args.get('formatType', 'unfocused') != 'basicWhereAmI':
                doNotSpeak.append(pyatspi.ROLE_LIST_ITEM)
                doNotSpeak.append(pyatspi.ROLE_LIST)
            if (start or end):
                doNotSpeak.append(pyatspi.ROLE_DOCUMENT_FRAME)
                doNotSpeak.append(pyatspi.ROLE_DOCUMENT_WEB)
                doNotSpeak.append(pyatspi.ROLE_ALERT)
            if self._script.utilities.isAnchor(obj):
                doNotSpeak.append(obj.getRole())
            if total > 1:
                doNotSpeak.append(pyatspi.ROLE_ROW_HEADER)
            if self._script.utilities.isMenuInCollapsedSelectElement(obj):
                doNotSpeak.append(pyatspi.ROLE_MENU)

        lastKey, mods = self._script.utilities.lastKeyAndModifiers()
        isEditable = obj.getState().contains(pyatspi.STATE_EDITABLE)

        if isEditable and not self._script.utilities.isContentEditableWithEmbeddedObjects(obj):
            if ((lastKey in ["Down", "Right"] and not mods) or self._script.inSayAll()) and start:
                return []
            if lastKey in ["Up", "Left"] and not mods:
                text = self._script.utilities.queryNonEmptyText(obj)
                if text and end not in [None, text.characterCount]:
                    return []
            if role not in doNotSpeak:
                result.append(self.getLocalizedRoleName(obj, **args))
                result.extend(acss)

        elif isEditable and self._script.utilities.isDocument(obj):
            if obj.parent and not obj.parent.getState().contains(pyatspi.STATE_EDITABLE) \
               and lastKey not in ["Home", "End", "Up", "Down", "Left", "Right", "Page_Up", "Page_Down"]:
                result.append(object_properties.ROLE_EDITABLE_CONTENT)
                result.extend(acss)

        elif role == pyatspi.ROLE_HEADING:
            if index == total - 1 or not self._script.utilities.isFocusableWithMathChild(obj):
                level = self._script.utilities.headingLevel(obj)
                if level:
                    result.append(object_properties.ROLE_HEADING_LEVEL_SPEECH % {
                        'role': self.getLocalizedRoleName(obj, **args),
                        'level': level})
                    result.extend(acss)
                else:
                    result.append(self.getLocalizedRoleName(obj, **args))
                    result.extend(acss)

        elif self._script.utilities.isLink(obj):
            if obj.parent.getRole() == pyatspi.ROLE_IMAGE:
                result.append(messages.IMAGE_MAP_LINK)
                result.extend(acss)
            else:
                if self._script.utilities.hasUselessCanvasDescendant(obj):
                    result.append(self.getLocalizedRoleName(obj, role=pyatspi.ROLE_IMAGE))
                    result.extend(acss)
                if index == total - 1 or not self._script.utilities.isFocusableWithMathChild(obj):
                    result.append(self.getLocalizedRoleName(obj, **args))
                    result.extend(acss)

        elif role not in doNotSpeak and args.get('priorObj') != obj:
            result.append(self.getLocalizedRoleName(obj, **args))
            result.extend(acss)

        if self._script.utilities.isMath(obj) and not self._script.utilities.isMathTopLevel(obj):
            return result

        ancestorRoles = [pyatspi.ROLE_HEADING, pyatspi.ROLE_LINK]
        speakRoles = lambda x: x and x.getRole() in ancestorRoles
        ancestor = pyatspi.findAncestor(obj, speakRoles)
        if ancestor and ancestor.getRole() != role and (index == total - 1 or obj.name == ancestor.name):
            result.extend(self._generateRoleName(ancestor))

        return result

    def _generatePageSummary(self, obj, **args):
        if not self._script.utilities.inDocumentContent(obj):
            return []

        onlyIfFound = args.get('formatType') != 'detailedWhereAmI'

        string = self._script.utilities.getPageSummary(obj, onlyIfFound)
        if not string:
            return []

        result = [string]
        result.extend(self.voice(speech_generator.SYSTEM))
        return result

    def _generateSiteDescription(self, obj, **args):
        if not self._script.utilities.inDocumentContent(obj):
            return []

        link_uri = self._script.utilities.uri(obj)
        if not link_uri:
            return []

        link_uri_info = urllib.parse.urlparse(link_uri)
        doc_uri = self._script.utilities.documentFrameURI()
        if not doc_uri:
            return []

        result = []
        doc_uri_info = urllib.parse.urlparse(doc_uri)
        if link_uri_info[1] == doc_uri_info[1]:
            if link_uri_info[2] == doc_uri_info[2]:
                result.append(messages.LINK_SAME_PAGE)
            else:
                result.append(messages.LINK_SAME_SITE)
        else:
            linkdomain = link_uri_info[1].split('.')
            docdomain = doc_uri_info[1].split('.')
            if len(linkdomain) > 1 and len(docdomain) > 1  \
               and linkdomain[-1] == docdomain[-1]  \
               and linkdomain[-2] == docdomain[-2]:
                result.append(messages.LINK_SAME_SITE)
            else:
                result.append(messages.LINK_DIFFERENT_SITE)

        if result:
            result.extend(self.voice(speech_generator.HYPERLINK))

        return result

    def _generateExpandedEOCs(self, obj, **args):
        if not self._script.utilities.inDocumentContent(obj):
            return super()._generateExpandedEOCs(obj, **args)

        result = []
        startOffset = args.get('startOffset', 0)
        endOffset = args.get('endOffset', -1)
        text = self._script.utilities.expandEOCs(obj, startOffset, endOffset)
        if text:
            result.append(text)
        return result

    def _generatePositionInList(self, obj, **args):
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        if not args.get('forceList', False) \
           and not _settingsManager.getSetting('enablePositionSpeaking'):
            return []

        if not self._script.utilities.inDocumentContent(obj):
            return super()._generatePositionInList(obj, **args)

        menuRoles = [pyatspi.ROLE_MENU_ITEM,
                     pyatspi.ROLE_TEAROFF_MENU_ITEM,
                     pyatspi.ROLE_CHECK_MENU_ITEM,
                     pyatspi.ROLE_RADIO_MENU_ITEM,
                     pyatspi.ROLE_MENU]
        if obj.getRole() in menuRoles:
            return super()._generatePositionInList(obj, **args)

        if self._script.utilities.isEditableComboBox(obj):
            return []

        position = self._script.utilities.getPositionInSet(obj)
        total = self._script.utilities.getSetSize(obj)
        if position is None or total is None:
            return super()._generatePositionInList(obj, **args)

        position = int(position)
        total = int(total)
        if position < 0 or total < 0:
            return []

        result = []
        result.append(self._script.formatting.getString(
            mode='speech',
            stringType='groupindex') \
            % {"index" : position,
               "total" : total})
        result.extend(self.voice(speech_generator.SYSTEM))
        return result

    def _generateRealTableCell(self, obj, **args):
        result = super()._generateRealTableCell(obj, **args)
        if not self._script.inFocusMode():
            return result

        if _settingsManager.getSetting('speakCellCoordinates'):
            label = self._script.utilities.labelForCellCoordinates(obj)
            if label:
                result.append(label)
                result.extend(self.voice(speech_generator.SYSTEM))
                return result

            row, col = self._script.utilities.coordinatesForCell(obj)
            if self._script.utilities.cellRowChanged(obj):
                result.append(messages.TABLE_ROW % (row + 1))
                result.extend(self.voice(speech_generator.SYSTEM))
            if self._script.utilities.cellColumnChanged(obj):
                result.append(messages.TABLE_COLUMN % (col + 1))
                result.extend(self.voice(speech_generator.SYSTEM))

        return result

    def _generateTableCellRow(self, obj, **args):
        if not self._script.utilities.inDocumentContent(obj):
            return super()._generateTableCellRow(obj, **args)

        if not self._script.utilities.shouldReadFullRow(obj):
            return self._generateRealTableCell(obj, **args)

        isRow = lambda x: x and x.getRole() == pyatspi.ROLE_TABLE_ROW
        row = pyatspi.findAncestor(obj, isRow)
        if row and row.name and not self._script.utilities.isLayoutOnly(row):
            return self.generate(row)

        return super()._generateTableCellRow(obj, **args)

    def _generateRowHeader(self, obj, **args):
        # TODO - JD: _lastCommandWasCaretNav is private.
        if self._script.utilities.lastInputEventWasLineNav() \
           and self._script._lastCommandWasCaretNav:
            return []

        return super()._generateRowHeader(obj)

    def generateSpeech(self, obj, **args):
        if not self._script.utilities.inDocumentContent(obj):
            msg = "WEB: %s is not in document content. Calling default speech generator." % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return super().generateSpeech(obj, **args)

        msg = "WEB: Generating speech for document object %s" % obj
        debug.println(debug.LEVEL_INFO, msg, True)

        result = []
        if args.get('formatType') == 'detailedWhereAmI':
            oldRole = self._overrideRole('default', args)
        elif self._script.utilities.isLink(obj):
            oldRole = self._overrideRole(pyatspi.ROLE_LINK, args)
        elif self._script.utilities.treatAsDiv(obj, offset=args.get('startOffset')):
            oldRole = self._overrideRole(pyatspi.ROLE_SECTION, args)
        else:
            oldRole = self._overrideRole(self._getAlternativeRole(obj, **args), args)

        if not 'priorObj' in args:
            args['priorObj'] = self._script.utilities.getPriorContext()[0]

        if self._script.utilities.isLabellingContents(obj):
            result = list(filter(lambda x: x, self.generateContext(obj, **args)))

        if not result:
            result = list(filter(lambda x: x, super().generateSpeech(obj, **args)))

        self._restoreRole(oldRole, args)
        msg = "WEB: Speech generation for document object %s complete:" % obj
        debug.println(debug.LEVEL_INFO, msg, True)
        for element in result:
            debug.println(debug.LEVEL_ALL, "%s%s" % (' ' * 18, element))

        return result

    def generateContents(self, contents, **args):
        if not len(contents):
            return []

        result = []
        contents = self._script.utilities.filterContentsForPresentation(contents, True)
        msg = "WEB: Generating speech contents (length: %i)" % len(contents)
        debug.println(debug.LEVEL_INFO, msg, True)
        for i, content in enumerate(contents):
            obj, start, end, string = content
            msg = "ITEM %i: %s, start: %i, end: %i, string: '%s'" \
                  % (i, obj, start, end, string)
            debug.println(debug.LEVEL_INFO, msg, True)
            utterance = self.generateSpeech(
                obj, startOffset=start, endOffset=end, string=string,
                index=i, total=len(contents), **args)
            if isinstance(utterance, list):
                isNotEmptyList = lambda x: not (isinstance(x, list) and not x)
                utterance = list(filter(isNotEmptyList, utterance))
            if utterance and utterance[0]:
                result.append(utterance)
                args['priorObj'] = obj

        if not result:
            if self._script.inSayAll():
                string = ""
            else:
                string = messages.BLANK
            result = [string, self.voice(speech_generator.DEFAULT)]

        return result
