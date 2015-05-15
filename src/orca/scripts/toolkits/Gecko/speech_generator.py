# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
# Copyright 2010 Orca Team.
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

"""Custom script for Gecko toolkit.
Please refer to the following URL for more information on the AT-SPI
implementation in Gecko:
http://developer.mozilla.org/en/docs/Accessibility/ATSPI_Support
"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2010 Orca Team."
__license__   = "LGPL"

import pyatspi

import orca.messages as messages
import orca.object_properties as object_properties
import orca.orca_state as orca_state
import orca.settings_manager as settings_manager
import orca.speech_generator as speech_generator

_settingsManager = settings_manager.getManager()

########################################################################
#                                                                      #
# Custom SpeechGenerator                                               #
#                                                                      #
########################################################################

class SpeechGenerator(speech_generator.SpeechGenerator):
    """Provides a speech generator specific to Gecko.
    """

    # pylint: disable-msg=W0142

    def __init__(self, script):
        speech_generator.SpeechGenerator.__init__(self, script)

    def _getACSS(self, obj, string):
        if obj.getRole() == pyatspi.ROLE_LINK:
            acss = self.voice(speech_generator.HYPERLINK)
        elif isinstance(string, str) \
            and string.isupper() \
            and string.strip().isalpha():
            acss = self.voice(speech_generator.UPPERCASE)
        else:
            acss = self.voice(speech_generator.DEFAULT)

        return acss

    def _generateName(self, obj, **args):
        result = []
        acss = self.voice(speech_generator.DEFAULT)
        role = args.get('role', obj.getRole())
        if role == pyatspi.ROLE_DOCUMENT_FRAME \
           and obj.getState().contains(pyatspi.STATE_EDITABLE):
            return []

        result.extend(speech_generator.SpeechGenerator._generateName(
                              self, obj, **args))
        if not result and role == pyatspi.ROLE_LIST_ITEM:
            result.append(self._script.utilities.expandEOCs(obj))
            result.extend(acss)

        acss = self.voice(speech_generator.HYPERLINK)
        link = None
        if role == pyatspi.ROLE_LINK:
            link = obj
        elif role == pyatspi.ROLE_IMAGE and not result:
            link = self._script.utilities.ancestorWithRole(
                obj, [pyatspi.ROLE_LINK], [pyatspi.ROLE_DOCUMENT_FRAME])
        if link and (not result or len(result[0].strip()) == 0):
            # If there's no text for the link, expose part of the
            # URI to the user.
            #
            basename = self._script.utilities.linkBasename(link)
            if basename:
                result.append(basename)
                result.extend(acss)

        return result

    def _generateDescription(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the description of the object,
        if that description is different from that of the name and
        label.
        """
        if not obj == orca_state.locusOfFocus:
            return []

        formatType = args.get('formatType')
        role = args.get('role', obj.getRole())
        if role == pyatspi.ROLE_TEXT and formatType != 'basicWhereAmI':
            return []

        return speech_generator.SpeechGenerator._generateDescription(
            self, obj, **args)

    def _generateLabel(self, obj, **args):
        start = args.get('startOffset')
        end = args.get('endOffset')
        if isinstance(start, int) and isinstance(end, int) \
           and not self._script.utilities.justEnteredObject(obj, start, end):
            return []

        acss = self.voice(speech_generator.DEFAULT)
        result = speech_generator.SpeechGenerator._generateLabel(self,
                                                                 obj,
                                                                 **args)

        if self._script.utilities.shouldInferLabelFor(obj):
            label, objects = self._script.labelInference.infer(obj, False)
            if label:
                result.append(label)
                result.extend(acss)

        # XUL combo boxes don't always have a label for/by
        # relationship.  But, they will make their names be
        # the string of the thing labelling them.
        #
        role = args.get('role', obj.getRole())
        if not len(result) \
           and role == pyatspi.ROLE_COMBO_BOX \
           and not self._script.inDocumentContent():
            result.append(obj.name)
            result.extend(acss)

        return result

    def _generateLabelOrName(self, obj, **args):
        if self._script.utilities.isTextBlockElement(obj):
            return []

        start = args.get('startOffset')
        end = args.get('endOffset')
        if isinstance(start, int) and isinstance(end, int) \
           and not self._script.utilities.justEnteredObject(obj, start, end):
            return []

        result = speech_generator.SpeechGenerator._generateLabelOrName(
            self, obj, **args)

        if not result and obj.parent.getRole() == pyatspi.ROLE_AUTOCOMPLETE:
            result = self._generateLabelOrName(obj.parent, **args)

        return result

    def _generateRoleName(self, obj, **args):
        """Prevents some roles from being spoken."""
        result = []
        acss = self.voice(speech_generator.SYSTEM)
        role = args.get('role', obj.getRole())
        force = args.get('force', False)
        start = args.get('startOffset')
        end = args.get('endOffset')
        if isinstance(start, int) and isinstance(end, int) \
           and not self._script.utilities.justEnteredObject(obj, start, end) \
           and not self._script.utilities.isTextBlockElement(obj) \
           and not self._script.utilities.isLink(obj):
            return []
        if role == pyatspi.ROLE_DOCUMENT_FRAME \
           and obj.getState().contains(pyatspi.STATE_EDITABLE):
            return []

        if not force:
            doNotSpeak = [pyatspi.ROLE_FORM,
                          pyatspi.ROLE_LABEL,
                          pyatspi.ROLE_MENU_ITEM,
                          pyatspi.ROLE_PARAGRAPH,
                          pyatspi.ROLE_SECTION,
                          pyatspi.ROLE_UNKNOWN]
        else:
            # We never ever want to speak 'unknown'
            #
            doNotSpeak = [pyatspi.ROLE_UNKNOWN]

        if not force and self._script.inDocumentContent(obj):
            doNotSpeak.append(pyatspi.ROLE_TABLE_CELL)
            doNotSpeak.append(pyatspi.ROLE_TEXT)
            if args.get('formatType', 'unfocused') != 'basicWhereAmI':
                doNotSpeak.append(pyatspi.ROLE_LIST_ITEM)
                doNotSpeak.append(pyatspi.ROLE_LIST)
            if args.get('startOffset') != None and args.get('endOffset') != None:
                doNotSpeak.append(pyatspi.ROLE_DOCUMENT_FRAME)
                doNotSpeak.append(pyatspi.ROLE_ALERT)

        if not (role in doNotSpeak):
            if role == pyatspi.ROLE_IMAGE:
                result.append(self.getLocalizedRoleName(obj, role))
                result.extend(acss)
                link = self._script.utilities.ancestorWithRole(
                    obj, [pyatspi.ROLE_LINK], [pyatspi.ROLE_DOCUMENT_FRAME])
                if link:
                    result.append(self.getLocalizedRoleName(link))
                    result.extend(acss)

            elif role == pyatspi.ROLE_HEADING:
                level = self._script.utilities.headingLevel(obj)
                if level:
                    result.append(object_properties.ROLE_HEADING_LEVEL_SPEECH % {
                        'role': self.getLocalizedRoleName(obj, role),
                        'level': level})
                    result.extend(acss)
                else:
                    result.append(self.getLocalizedRoleName(obj, role))
                    result.extend(acss)

            elif role == pyatspi.ROLE_LINK:
                if obj.parent.getRole() == pyatspi.ROLE_IMAGE:
                    result.append(messages.IMAGE_MAP_LINK)
                    result.extend(acss)
                else:
                    result.append(self.getLocalizedRoleName(obj, role))
                    result.extend(acss)
                    if obj.childCount and obj[0].getRole() == pyatspi.ROLE_IMAGE:
                        result.append(self.getLocalizedRoleName(obj[0]))
                        result.extend(acss)
            else:
                result.append(self.getLocalizedRoleName(obj, role))
                result.extend(acss)

        return result

    def _generateExpandedEOCs(self, obj, **args):
        """Returns the expanded embedded object characters for an object."""
        result = []

        startOffset = args.get('startOffset', 0)
        endOffset = args.get('endOffset', -1)
        text = self._script.utilities.expandEOCs(obj, startOffset, endOffset)
        if text:
            result.append(text)
        return result

    def _generateNumberOfChildren(self, obj, **args):
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        result = []
        acss = self.voice(speech_generator.SYSTEM)
        role = args.get('role', obj.getRole())
        if role in [pyatspi.ROLE_LIST, pyatspi.ROLE_LIST_BOX]:
            result.append(messages.listItemCount(obj.childCount))
            result.extend(acss)
        else:
            result.extend(
                speech_generator.SpeechGenerator._generateNumberOfChildren(
                    self, obj, **args))
        return result

    def _generateNewAncestors(self, obj, **args):
        # TODO - JD: This is not the right way to do this, but we can fix
        # that as part of the removal of formatting strings.
        start = args.get('startOffset')
        end = args.get('endOffset')
        if start != None or end != None:
            return []

        return speech_generator.SpeechGenerator._generateNewAncestors(
            self, obj, **args)

    def _generateAncestors(self, obj, **args):
        role = args.get('role', obj.getRole())
        if role == pyatspi.ROLE_LINK:
            return []

        args['stopAtRoles'] = [pyatspi.ROLE_DOCUMENT_FRAME,
                               pyatspi.ROLE_EMBEDDED,
                               pyatspi.ROLE_INTERNAL_FRAME,
                               pyatspi.ROLE_FORM,
                               pyatspi.ROLE_MENU_BAR,
                               pyatspi.ROLE_TOOL_BAR]
        args['skipRoles'] = [pyatspi.ROLE_PARAGRAPH,
                             pyatspi.ROLE_LIST_ITEM,
                             pyatspi.ROLE_TABLE_ROW,
                             pyatspi.ROLE_TEXT]

        return speech_generator.SpeechGenerator._generateAncestors(
            self, obj, **args)

    def _generateDefaultButton(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the default button in a dialog.
        This method should initially be called with a top-level window.
        """
        if self._script.inDocumentContent(obj):
            return []

        return speech_generator.SpeechGenerator.\
                     _generateDefaultButton(self, obj, **args)

    def _generateLiveRegionDescription(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the live region.
        """
        return self._script.liveMngr.\
                    generateLiveRegionDescription(obj, **args)

    def _generatePageSummary(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that summarize the objects found on the page
        containing obj.
        """
        result = []
        acss = self.voice(speech_generator.DEFAULT)
        headings, forms, tables, vlinks, uvlinks, percent = \
            self._script.getPageSummary(obj)
        if headings:
            result.append(messages.headingCount(headings))
        if forms:
            result.append(messages.formCount(forms))
        if tables:
            result.append(messages.tableCount(tables))
        if vlinks:
            result.append(messages.visitedLinkCount(vlinks))
        if uvlinks:
            result.append(messages.unvisitedLinkCount(uvlinks))
        if percent is not None:
            result.append(messages.percentRead(percent))

        if result:
            result.extend(acss)
        return result

    def generateSpeech(self, obj, **args):
        result = []
        # Detailed WhereAmI should always be a page summary if we
        # are in document content.
        #
        if args.get('formatType', 'unfocused') == 'detailedWhereAmI' \
           and self._script.inDocumentContent(obj):
            oldRole = self._overrideRole('default', args)
            result.extend(speech_generator.SpeechGenerator.\
                                           generateSpeech(self, obj, **args))
            self._restoreRole(oldRole, args)
        elif self._script.utilities.isLink(obj):
            oldRole = self._overrideRole(pyatspi.ROLE_LINK, args)
            result.extend(speech_generator.SpeechGenerator.\
                                           generateSpeech(self, obj, **args))
            self._restoreRole(oldRole, args)
        else:
            result.extend(speech_generator.SpeechGenerator.\
                                           generateSpeech(self, obj, **args))
        return result

    def getAttribute(self, obj, attributeName):
        attributes = obj.getAttributes()
        for attribute in attributes:
            if attribute.startswith(attributeName):
                return attribute.split(":")[1]

    def _generateNewNodeLevel(self, obj, **args):
        if self._script.utilities.isTextBlockElement(obj):
            return []

        return speech_generator.SpeechGenerator._generateNewNodeLevel(
            self, obj, **args)

    def _generatePositionInList(self, obj, **args):
        if _settingsManager.getSetting('onlySpeakDisplayedText') \
           or not (_settingsManager.getSetting('enablePositionSpeaking') \
                   or args.get('forceList', False)):
            return []

        if self._script.utilities.isTextBlockElement(obj):
            return []

        menuRoles = [pyatspi.ROLE_MENU_ITEM,
                     pyatspi.ROLE_CHECK_MENU_ITEM,
                     pyatspi.ROLE_RADIO_MENU_ITEM,
                     pyatspi.ROLE_MENU,
                     pyatspi.ROLE_COMBO_BOX]
        if obj.getRole() in menuRoles:
            return super()._generatePositionInList(obj, **args)

        position = self.getAttribute(obj, "posinset")
        total = self.getAttribute(obj, "setsize")
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

    def _generateNewRadioButtonGroup(self, obj, **args):
        # TODO - JD: Looking at the default speech generator's method, this
        # is all kinds of broken. Until that can be sorted out, try to filter
        # out some of the noise....
        return []

    def _generateAnyTextSelection(self, obj, **args):
        if not obj == orca_state.locusOfFocus:
            return []

        return speech_generator.SpeechGenerator._generateAnyTextSelection(
            self, obj, **args)

    def _generateAllTextSelection(self, obj, **args):
        if not obj == orca_state.locusOfFocus:
            return []

        return speech_generator.SpeechGenerator._generateAllTextSelection(
            self, obj, **args)

    def _generateSubstring(self, obj, **args):
        start = args.get('startOffset')
        end = args.get('endOffset')
        if start == None or end == None:
            return []

        string = self._script.utilities.substring(obj, start, end)
        string = self._script.utilities.adjustForRepeats(string)
        if not string:
            return []

        if not obj.getState().contains(pyatspi.STATE_EDITABLE):
            string = string.strip()

        result = [string]
        result.extend(self._getACSS(obj, string))
        return result

    # TODO - JD: While working on the Gecko rewrite, I found a metric crapton
    # of text generation methods (including, but not limited to, these below).
    # Are these really all needed? Seriously??
    def _generateCurrentLineText(self, obj, **args):
        result = self._generateSubstring(obj, **args)
        if result:
            return result

        return speech_generator.SpeechGenerator._generateCurrentLineText(
            self, obj, **args)

    def _generateDisplayedText(self, obj, **args):
        result = self._generateSubstring(obj, **args)
        if result:
            return result

        return speech_generator.SpeechGenerator._generateDisplayedText(
            self, obj, **args)

    def _generateTextContent(self, obj, **args):
        result = self._generateSubstring(obj, **args)
        if result:
            return result

        return speech_generator.SpeechGenerator._generateTextContent(
            self, obj, **args)
