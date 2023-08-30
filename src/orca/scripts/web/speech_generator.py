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

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi
import urllib

from orca import debug
from orca import messages
from orca import object_properties
from orca import orca_state
from orca import settings
from orca import settings_manager
from orca import speech_generator
from orca.ax_object import AXObject
from orca.ax_utilities import AXUtilities

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

        if not self._script.utilities.getTable(obj) \
           and (self._script.utilities.isLink(obj) \
                or self._script.utilities.isLandmark(obj) \
                or self._script.utilities.isMath(obj) \
                or AXUtilities.is_tool_tip(obj) \
                or AXUtilities.is_status_bar(obj)):
            return result

        if self._script.utilities.isItemForEditableComboBox(obj, priorObj):
            return result

        args['stopAtRoles'] = [Atspi.Role.DOCUMENT_WEB,
                               Atspi.Role.EMBEDDED,
                               Atspi.Role.INTERNAL_FRAME,
                               Atspi.Role.MATH,
                               Atspi.Role.MENU_BAR]
        args['skipRoles'] = [Atspi.Role.PARAGRAPH,
                             Atspi.Role.HEADING,
                             Atspi.Role.LABEL,
                             Atspi.Role.LINK,
                             Atspi.Role.LIST_ITEM,
                             Atspi.Role.TEXT]
        args['stopAfterRoles'] = [Atspi.Role.TOOL_BAR]

        if self._script.utilities.isEditableDescendantOfComboBox(obj):
            args['skipRoles'].append(Atspi.Role.COMBO_BOX)

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
            result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))

        return result

    def _generateClickable(self, obj, **args):
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        if not self._script.utilities.inDocumentContent(obj):
            return []

        if self._script.utilities.isFeedArticle(obj):
            return []

        if not args.get('mode', None):
            args['mode'] = self._mode

        args['stringType'] = 'clickable'
        if self._script.utilities.isClickableElement(obj):
            result = [self._script.formatting.getString(**args)]
            result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))
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

        role = args.get('role', AXObject.get_role(obj))
        if obj != orca_state.locusOfFocus:
            if role in [Atspi.Role.ALERT, Atspi.Role.DIALOG]:
                return super()._generateDescription(obj, **args)
            if not args.get('inMouseReview'):
                return []

        formatType = args.get('formatType')
        if formatType == 'basicWhereAmI' and self._script.utilities.isLiveRegion(obj):
            return self._script.liveRegionManager.generateLiveRegionDescription(obj, **args)

        if role == Atspi.Role.TEXT and formatType != 'basicWhereAmI':
            return []

        # TODO - JD: This is private.
        if role == Atspi.Role.LINK and self._script._lastCommandWasCaretNav:
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
            result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))
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

        def objString(x):
            return str.strip(f"{AXObject.get_name(x)} {self.getLocalizedRoleName(x)}")

        toPresent = ", ".join(set(map(objString, objs)))

        args['stringType'] = 'hasdetails'
        result = [self._script.formatting.getString(**args) % toPresent]
        result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))
        return result

    def _generateAllDetails(self, obj, **args):
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        objs = self._script.utilities.detailsIn(obj)
        if not objs:
            container = AXObject.find_ancestor(obj, self._script.utilities.hasDetails)
            objs = self._script.utilities.detailsIn(container)

        if not objs:
            return []

        args['stringType'] = 'hasdetails'
        result = [self._script.formatting.getString(**args) % ""]
        result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))

        result = []
        for o in objs:
            result.append(self.getLocalizedRoleName(o))
            result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))

            string = self._script.utilities.expandEOCs(o)
            if not string.strip():
                continue

            result.append(string)
            result.extend(self.voice(speech_generator.DEFAULT, obj=obj, **args))
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
            result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))
            result.extend(self._generatePause(o, **objArgs))

        return result

    def _generateLabelOrName(self, obj, **args):
        if not self._script.utilities.inDocumentContent(obj):
            return super()._generateLabelOrName(obj, **args)

        if self._script.utilities.isTextBlockElement(obj) \
           and not self._script.utilities.isLandmark(obj) \
           and not self._script.utilities.isDocument(obj) \
           and not self._script.utilities.isDPub(obj) \
           and not self._script.utilities.isContentSuggestion(obj):
            return []

        priorObj = args.get("priorObj")
        if obj == priorObj:
            return []

        if priorObj and priorObj in self._script.utilities.labelsForObject(obj):
            return []

        objName = AXObject.get_name(obj)
        descendant = args.get("ancestorOf")
        if descendant and priorObj and objName and objName == AXObject.get_name(priorObj):
            msg = "WEB: %s's ancestor %s has same name as priorObj %s. \
                   Not generating labelOrName." % (descendant, obj, priorObj)
            debug.println(debug.LEVEL_INFO, msg, True)
            return []

        role = args.get('role', AXObject.get_role(obj))
        if role == Atspi.Role.MENU and self._script.utilities.isPopupMenuForCurrentItem(obj):
            tokens = ["WEB:", obj, "is popup menu for current item."]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return []

        if self._script.utilities.isContentEditableWithEmbeddedObjects(obj) \
           or self._script.utilities.isDocument(obj):
            lastKey, mods = self._script.utilities.lastKeyAndModifiers()
            if lastKey in ["Home", "End", "Up", "Down", "Left", "Right", "Page_Up", "Page_Down"]:
                return []

        if AXUtilities.is_page_tab(priorObj) and AXObject.get_name(priorObj) == objName:
            return []

        if objName:
            name = objName
            if not self._script.utilities.hasExplicitName(obj):
                name = name.strip()

            if self._script.utilities.shouldVerbalizeAllPunctuation(obj):
                name = self._script.utilities.verbalizeAllPunctuation(name)

            result = [name]
            result.extend(self.voice(speech_generator.DEFAULT, obj=obj, **args))
            return result

        if AXUtilities.is_check_box(obj):
            gridCell = AXObject.find_ancestor(obj, self._script.utilities.isGridCell)
            if gridCell:
                return super()._generateLabelOrName(gridCell, **args)

        return super()._generateLabelOrName(obj, **args)

    def _generateName(self, obj, **args):
        if not self._script.utilities.inDocumentContent(obj):
            return super()._generateName(obj, **args)

        if self._script.utilities.isTextBlockElement(obj) \
           and not self._script.utilities.isLandmark(obj) \
           and not self._script.utilities.isDPub(obj) \
           and not args.get('inFlatReview'):
            return []

        if self._script.utilities.hasVisibleCaption(obj):
            return []

        if self._script.utilities.isFigure(obj) and args.get('ancestorOf'):
            caption = args.get('ancestorOf')
            if not AXUtilities.is_caption(caption):
                caption = AXObject.find_ancestor(caption, AXUtilities.is_caption)
            if caption and hash(obj) in self._script.utilities.labelTargets(caption):
                return []

        role = args.get('role', AXObject.get_role(obj))

        # TODO - JD: Once the formatting strings are vastly cleaned up
        # or simply removed, hacks like this won't be needed.
        if role in [Atspi.Role.COMBO_BOX, Atspi.Role.SPIN_BUTTON]:
            return super()._generateName(obj, **args)

        if AXObject.get_name(obj):
            if self._script.utilities.preferDescriptionOverName(obj):
                result = [AXObject.get_description(obj)]
            elif self._script.utilities.isLink(obj) \
                 and not self._script.utilities.hasExplicitName(obj):
                return []
            else:
                name = AXObject.get_name(obj)
                if not self._script.utilities.hasExplicitName(obj):
                    name = name.strip()
                result = [name]

            result.extend(self.voice(speech_generator.DEFAULT, obj=obj, **args))
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
            result.extend(self.voice(speech_generator.DEFAULT, obj=obj, **args))
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
            result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))
            return result

        return super()._generateLeaving(obj, **args)

    def _generateNewRadioButtonGroup(self, obj, **args):
        # TODO - JD: The default speech generator's method determines group membership
        # via the member-of relation. We cannot count on that here. Plus, radio buttons
        # on the web typically live in a group which is labelled. Thus the new-ancestor
        # presentation accomplishes the same thing. Unless this can be further sorted out,
        # try to filter out some of the noise....
        return []

    def _generateNumberOfChildren(self, obj, **args):
        if _settingsManager.getSetting('onlySpeakDisplayedText') \
           or _settingsManager.getSetting('speechVerbosityLevel') == settings.VERBOSITY_LEVEL_BRIEF:
            return []

        # We handle things even for non-document content due to issues in
        # other toolkits (e.g. exposing list items to us that are not
        # exposed to sighted users)
        roles = [Atspi.Role.DESCRIPTION_LIST,
                 Atspi.Role.LIST,
                 Atspi.Role.LIST_BOX,
                 'ROLE_FEED']
        role = args.get('role', AXObject.get_role(obj))
        if role not in roles:
            return super()._generateNumberOfChildren(obj, **args)

        setsize = self._script.utilities.getSetSize(AXObject.get_child(obj, 0))
        if setsize is None:
            if self._script.utilities.isDescriptionList(obj):
                children = self._script.utilities.descriptionListTerms(obj)
            elif role in [Atspi.Role.LIST, Atspi.Role.LIST_BOX]:
                children = [x for x in AXObject.iter_children(obj, AXUtilities.is_list_item)]
            setsize = len(children)

        if not setsize:
            return []

        if self._script.utilities.isDescriptionList(obj):
            result = [messages.descriptionListTermCount(setsize)]
        elif role == 'ROLE_FEED':
            result = [messages.feedArticleCount(setsize)]
        else:
            result = [messages.listItemCount(setsize)]
        result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))
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

        rad = self._script.utilities.realActiveDescendant(obj)
        return self._generateDisplayedText(rad, **args)

    def _generateRoleName(self, obj, **args):
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        if not self._script.utilities.inDocumentContent(obj):
            return super()._generateRoleName(obj, **args)

        if obj == args.get('priorObj'):
            return []

        result = []
        roledescription = self._script.utilities.getRoleDescription(obj)
        if roledescription:
            result = [roledescription]
            result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))
            return result

        role = args.get('role', AXObject.get_role(obj))
        enabled, disabled = self._getEnabledAndDisabledContextRoles()
        if role in disabled:
            return []

        force = args.get('force', False)
        start = args.get('startOffset')
        end = args.get('endOffset')
        index = args.get('index', 0)
        total = args.get('total', 1)

        if not force:
            doNotSpeak = [Atspi.Role.FOOTER,
                          Atspi.Role.FORM,
                          Atspi.Role.LABEL,
                          Atspi.Role.MENU_ITEM,
                          Atspi.Role.PARAGRAPH,
                          Atspi.Role.SECTION,
                          Atspi.Role.REDUNDANT_OBJECT,
                          Atspi.Role.UNKNOWN]
        else:
            doNotSpeak = [Atspi.Role.UNKNOWN]

        if not force:
            doNotSpeak.append(Atspi.Role.TABLE_CELL)
            doNotSpeak.append(Atspi.Role.TEXT)
            doNotSpeak.append(Atspi.Role.STATIC)
            if args.get('string'):
                doNotSpeak.append("ROLE_CONTENT_SUGGESTION")
            if args.get('formatType', 'unfocused') != 'basicWhereAmI':
                doNotSpeak.append(Atspi.Role.LIST_ITEM)
                doNotSpeak.append(Atspi.Role.LIST)
            if (start or end):
                doNotSpeak.append(Atspi.Role.DOCUMENT_FRAME)
                doNotSpeak.append(Atspi.Role.DOCUMENT_WEB)
                doNotSpeak.append(Atspi.Role.ALERT)
            if self._script.utilities.isAnchor(obj):
                doNotSpeak.append(AXObject.get_role(obj))
            if total > 1:
                doNotSpeak.append(Atspi.Role.ROW_HEADER)
            if self._script.utilities.isMenuInCollapsedSelectElement(obj):
                doNotSpeak.append(Atspi.Role.MENU)

        lastKey, mods = self._script.utilities.lastKeyAndModifiers()
        isEditable = AXUtilities.is_editable(obj)

        if isEditable and not self._script.utilities.isContentEditableWithEmbeddedObjects(obj):
            if ((lastKey in ["Down", "Right"] and not mods) or self._script.inSayAll()) and start:
                return []
            if lastKey in ["Up", "Left"] and not mods:
                text = self._script.utilities.queryNonEmptyText(obj)
                if text and end not in [None, text.characterCount]:
                    return []
            if role not in doNotSpeak:
                result.append(self.getLocalizedRoleName(obj, **args))
                result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))

        elif isEditable and self._script.utilities.isDocument(obj):
            parent = AXObject.get_parent(obj)
            if parent and not AXUtilities.is_editable(parent) \
               and lastKey not in \
                    ["Home", "End", "Up", "Down", "Left", "Right", "Page_Up", "Page_Down"]:
                result.append(object_properties.ROLE_EDITABLE_CONTENT)
                result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))

        elif role == Atspi.Role.HEADING:
            if index == total - 1 or not self._script.utilities.isFocusableWithMathChild(obj):
                level = self._script.utilities.headingLevel(obj)
                if level:
                    result.append(object_properties.ROLE_HEADING_LEVEL_SPEECH % {
                        'role': self.getLocalizedRoleName(obj, **args),
                        'level': level})
                    result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))
                else:
                    result.append(self.getLocalizedRoleName(obj, **args))
                    result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))

        elif self._script.utilities.isLink(obj):
            if AXUtilities.is_image(AXObject.get_parent(obj)):
                result.append(messages.IMAGE_MAP_LINK)
                result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))
            else:
                if self._script.utilities.hasUselessCanvasDescendant(obj):
                    result.append(self.getLocalizedRoleName(obj, role=Atspi.Role.IMAGE))
                    result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))
                if index == total - 1 or not self._script.utilities.isFocusableWithMathChild(obj):
                    result.append(self.getLocalizedRoleName(obj, **args))
                    result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))

        elif role not in doNotSpeak and args.get('priorObj') != obj:
            result.append(self.getLocalizedRoleName(obj, **args))
            result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))

        if self._script.utilities.isMath(obj) and not self._script.utilities.isMathTopLevel(obj):
            return result

        def speakRoles(x):
            return AXUtilities.is_heading(x) or AXUtilities.is_link(x)

        ancestor = AXObject.find_ancestor(obj, speakRoles)
        if ancestor and AXObject.get_role(ancestor) != role \
            and (index == total - 1 or AXObject.get_name(obj) == AXObject.get_name(ancestor)):
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
        result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))
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
            result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))

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
        if AXUtilities.is_list_item(obj):
            thisObjIndex = args.get('index', 0)
            objCount = args.get('total', 1)
            if thisObjIndex + 1 < objCount:
                return []

        if args.get('formatType') not in ['basicWhereAmI', 'detailedWhereAmI']:
            if args.get('priorObj') == obj:
                return []

        return super()._generatePositionInList(obj, **args)

    def _generateUnselectedCell(self, obj, **args):
        if not self._script.inFocusMode():
            return []

        return super()._generateUnselectedCell(obj, **args)

    def _generateRealTableCell(self, obj, **args):
        result = super()._generateRealTableCell(obj, **args)
        if not self._script.inFocusMode():
            return result

        if _settingsManager.getSetting('speakCellCoordinates'):
            label = self._script.utilities.labelForCellCoordinates(obj)
            if label:
                result.append(label)
                result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))
                return result

            row, col = self._script.utilities.coordinatesForCell(obj)
            if self._script.utilities.cellRowChanged(obj):
                result.append(messages.TABLE_ROW % (row + 1))
                result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))
            if self._script.utilities.cellColumnChanged(obj):
                result.append(messages.TABLE_COLUMN % (col + 1))
                result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))

        return result

    def _generateTableCellRow(self, obj, **args):
        if not self._script.utilities.inDocumentContent(obj):
            return super()._generateTableCellRow(obj, **args)

        if not self._script.utilities.shouldReadFullRow(obj):
            return self._generateRealTableCell(obj, **args)

        row = AXObject.find_ancestor(obj, AXUtilities.is_table_row)
        if row and AXObject.get_name(row) and not self._script.utilities.isLayoutOnly(row):
            return self.generate(row)

        return super()._generateTableCellRow(obj, **args)

    def _generateRowHeader(self, obj, **args):
        if self._script.utilities.lastInputEventWasLineNav():
            return []

        return super()._generateRowHeader(obj)

    def generateSpeech(self, obj, **args):
        if not self._script.utilities.inDocumentContent(obj):
            tokens = ["WEB:", obj, "is not in document content. Calling default speech generator."]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return super().generateSpeech(obj, **args)

        tokens = ["WEB: Generating speech for document object", obj]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        result = []
        if args.get('formatType') == 'detailedWhereAmI':
            oldRole = self._overrideRole('default', args)
        elif self._script.utilities.isLink(obj):
            oldRole = self._overrideRole(Atspi.Role.LINK, args)
        elif self._script.utilities.isCustomImage(obj):
            oldRole = self._overrideRole(Atspi.Role.IMAGE, args)
        elif self._script.utilities.treatAsDiv(obj, offset=args.get('startOffset')):
            oldRole = self._overrideRole(Atspi.Role.SECTION, args)
        else:
            oldRole = self._overrideRole(self._getAlternativeRole(obj, **args), args)

        if 'priorObj' not in args:
            document = self._script.utilities.getTopLevelDocumentForObject(obj)
            args['priorObj'] = self._script.utilities.getPriorContext(document)[0]

        start = args.get("startOffset", 0)
        end = args.get("endOffset", -1)
        args["language"], args["dialect"] = \
            self._script.utilities.getLanguageAndDialectForSubstring(obj, start, end)

        if not result:
            result = list(filter(lambda x: x, super().generateSpeech(obj, **args)))

        self._restoreRole(oldRole, args)
        tokens = ["WEB: Speech generation for document object", obj, "complete."]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        return result

    def generateContents(self, contents, **args):
        if not len(contents):
            return []

        result = []
        contents = self._script.utilities.filterContentsForPresentation(contents, True)
        tokens = ["WEB: Generating speech contents (length:", len(contents), ")"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)
        for i, content in enumerate(contents):
            obj, start, end, string = content
            msg = "ITEM %i: %s, start: %i, end: %i, string: '%s'" \
                  % (i, obj, start, end, string)
            debug.println(debug.LEVEL_INFO, msg, True)
            utterance = self.generateSpeech(
                obj, startOffset=start, endOffset=end, string=string,
                index=i, total=len(contents), **args)
            if isinstance(utterance, list):
                def isNotEmptyList(x):
                    return not (isinstance(x, list) and not x)

                utterance = list(filter(isNotEmptyList, utterance))
            if utterance and utterance[0]:
                result.append(utterance)
                args['priorObj'] = obj

        if not result:
            if self._script.inSayAll(treatInterruptedAsIn=False) \
               or not _settingsManager.getSetting('speakBlankLines') \
               or args.get('formatType') == 'ancestor':
                string = ""
            else:
                string = messages.BLANK
            result = [string, self.voice(speech_generator.DEFAULT, **args)]

        return result
