# Orca
#
# Copyright (C) 2010 Joanmarie Diggs
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
__copyright__ = "Copyright (c) 2010 Joanmarie Diggs" \
                "Copyright (c) 2011-2012 Igalia, S.L."
__license__   = "LGPL"

import pyatspi

import orca.keynames as keynames
import orca.object_properties as object_properties
import orca.settings as settings
import orca.settings_manager as settings_manager
import orca.speech_generator as speech_generator

_settingsManager = settings_manager.getManager()

########################################################################
#                                                                      #
# Custom SpeechGenerator                                               #
#                                                                      #
########################################################################

class SpeechGenerator(speech_generator.SpeechGenerator):
    """Provides a speech generator specific to WebKitGtk widgets."""

    def __init__(self, script):
        speech_generator.SpeechGenerator.__init__(self, script)

    def getVoiceForString(self, obj, string, **args):
        voice = settings.voices[settings.DEFAULT_VOICE]
        if string.isupper():
            voice = settings.voices[settings.UPPERCASE_VOICE]

        return voice

    def _generateLabel(self, obj, **args):
        result = super()._generateLabel(obj, **args)
        if result or not self._script.utilities.isWebKitGtk(obj):
            return result

        role = args.get('role', obj.getRole())
        inferRoles = [pyatspi.ROLE_CHECK_BOX,
                      pyatspi.ROLE_COMBO_BOX,
                      pyatspi.ROLE_ENTRY,
                      pyatspi.ROLE_LIST,
                      pyatspi.ROLE_PASSWORD_TEXT,
                      pyatspi.ROLE_RADIO_BUTTON]
        if not role in inferRoles:
            return result

        label, objects = self._script.labelInference.infer(obj)
        if label:
            result.append(label)
            result.extend(self.voice(speech_generator.DEFAULT))

        return result

    def __generateHeadingRole(self, obj):
        result = []
        role = pyatspi.ROLE_HEADING
        level = self._script.utilities.headingLevel(obj)
        if level:
            result.append(object_properties.ROLE_HEADING_LEVEL_SPEECH % {
                    'role': self.getLocalizedRoleName(obj, role),
                    'level': level})
        else:
            result.append(self.getLocalizedRoleName(obj, role))

        return result

    def _generateRoleName(self, obj, **args):
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        result = []
        acss = self.voice(speech_generator.SYSTEM)
        role = args.get('role', obj.getRole())
        force = args.get('force', False)

        doNotSpeak = [pyatspi.ROLE_UNKNOWN]
        if not force:
            doNotSpeak.extend([pyatspi.ROLE_FORM,
                               pyatspi.ROLE_LABEL,
                               pyatspi.ROLE_MENU_ITEM,
                               pyatspi.ROLE_LIST_ITEM,
                               pyatspi.ROLE_PARAGRAPH,
                               pyatspi.ROLE_SECTION,
                               pyatspi.ROLE_TABLE_CELL])

        if not (role in doNotSpeak):
            docRoles = [pyatspi.ROLE_DOCUMENT_FRAME, pyatspi.ROLE_DOCUMENT_WEB]
            if role == pyatspi.ROLE_IMAGE:
                link = self._script.utilities.ancestorWithRole(
                    obj, [pyatspi.ROLE_LINK], docRoles)
                if link:
                    result.append(self.getLocalizedRoleName(link))
            elif role == pyatspi.ROLE_HEADING:
                result.extend(self.__generateHeadingRole(obj))
            else:
                result.append(self.getLocalizedRoleName(obj, role))
                if obj.parent and obj.parent.getRole() == pyatspi.ROLE_HEADING:
                    result.extend(self.__generateHeadingRole(obj.parent))

            if result:
                result.extend(acss)

            if role == pyatspi.ROLE_LINK \
               and obj.childCount and obj[0].getRole() == pyatspi.ROLE_IMAGE:
                # If this is a link with a child which is an image, we
                # want to indicate that.
                #
                acss = self.voice(speech_generator.HYPERLINK)
                result.append(self.getLocalizedRoleName(obj[0]))
                result.extend(acss)

        return result

    def _generateAncestors(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the text of the ancestors for
        the object.  This is typically used to present the context for
        an object (e.g., the names of the window, the panels, etc.,
        that the object is contained in).  If the 'priorObj' attribute
        of the args dictionary is set, only the differences in
        ancestry between the 'priorObj' and the current obj will be
        computed.  The 'priorObj' is typically set by Orca to be the
        previous object with focus.
        """

        role = args.get('role', obj.getRole())
        if role == pyatspi.ROLE_LINK:
            return []

        args['stopAtRoles'] = [pyatspi.ROLE_DOCUMENT_FRAME,
                               pyatspi.ROLE_DOCUMENT_WEB,
                               pyatspi.ROLE_EMBEDDED,
                               pyatspi.ROLE_INTERNAL_FRAME,
                               pyatspi.ROLE_FORM,
                               pyatspi.ROLE_MENU_BAR,
                               pyatspi.ROLE_TOOL_BAR]
        args['skipRoles'] = [pyatspi.ROLE_PARAGRAPH,
                             pyatspi.ROLE_LIST_ITEM,
                             pyatspi.ROLE_TEXT]

        return speech_generator.SpeechGenerator._generateAncestors(
            self, obj, **args)

    def _generateMnemonic(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the mnemonic for the object, or
        an empty array if no mnemonic can be found.
        """

        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        if not (_settingsManager.getSetting('enableMnemonicSpeaking') \
                or args.get('forceMnemonic', False)):
            return []

        if not self._script.utilities.isWebKitGtk(obj):
            return speech_generator.SpeechGenerator._generateMnemonic(
                self, obj, **args)

        result = []
        acss = self.voice(speech_generator.SYSTEM)
        mnemonic, shortcut, accelerator = \
            self._script.utilities.mnemonicShortcutAccelerator(obj)
        if shortcut:
            if _settingsManager.getSetting('speechVerbosityLevel') == \
               settings.VERBOSITY_LEVEL_VERBOSE:
                shortcut = 'Alt Shift %s' % shortcut
            result = [keynames.localizeKeySequence(shortcut)]
            result.extend(acss)

        return result
