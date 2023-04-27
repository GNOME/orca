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

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

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
        inferRoles = [Atspi.Role.CHECK_BOX,
                      Atspi.Role.COMBO_BOX,
                      Atspi.Role.ENTRY,
                      Atspi.Role.LIST,
                      Atspi.Role.PASSWORD_TEXT,
                      Atspi.Role.RADIO_BUTTON]
        if not role in inferRoles:
            return result

        label, objects = self._script.labelInference.infer(obj)
        if label:
            result.append(label)
            result.extend(self.voice(speech_generator.DEFAULT, obj=obj, **args))

        return result

    def __generateHeadingRole(self, obj):
        result = []
        role = Atspi.Role.HEADING
        level = self._script.utilities.headingLevel(obj)
        if level:
            result.append(object_properties.ROLE_HEADING_LEVEL_SPEECH % {
                    'role': self.getLocalizedRoleName(obj, role=role),
                    'level': level})
        else:
            result.append(self.getLocalizedRoleName(obj, role=role))

        return result

    def _generateRoleName(self, obj, **args):
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        result = []
        role = args.get('role', obj.getRole())
        force = args.get('force', False)

        doNotSpeak = [Atspi.Role.UNKNOWN]
        if not force:
            doNotSpeak.extend([Atspi.Role.FORM,
                               Atspi.Role.LABEL,
                               Atspi.Role.MENU_ITEM,
                               Atspi.Role.LIST_ITEM,
                               Atspi.Role.PARAGRAPH,
                               Atspi.Role.SECTION,
                               Atspi.Role.TABLE_CELL])

        if not (role in doNotSpeak):
            docRoles = [Atspi.Role.DOCUMENT_FRAME, Atspi.Role.DOCUMENT_WEB]
            if role == Atspi.Role.IMAGE:
                link = self._script.utilities.ancestorWithRole(
                    obj, [Atspi.Role.LINK], docRoles)
                if link:
                    result.append(self.getLocalizedRoleName(link))
            elif role == Atspi.Role.HEADING:
                result.extend(self.__generateHeadingRole(obj))
            else:
                result.append(self.getLocalizedRoleName(obj, role=role))
                if obj.parent and obj.parent.getRole() == Atspi.Role.HEADING:
                    result.extend(self.__generateHeadingRole(obj.parent))

            if result:
                result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))

            if role == Atspi.Role.LINK \
               and obj.childCount and obj[0].getRole() == Atspi.Role.IMAGE:
                # If this is a link with a child which is an image, we
                # want to indicate that.
                #
                result.append(self.getLocalizedRoleName(obj[0]))
                result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))

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
        if role == Atspi.Role.LINK:
            return []

        args['stopAtRoles'] = [Atspi.Role.DOCUMENT_FRAME,
                               Atspi.Role.DOCUMENT_WEB,
                               Atspi.Role.EMBEDDED,
                               Atspi.Role.INTERNAL_FRAME,
                               Atspi.Role.FORM,
                               Atspi.Role.MENU_BAR,
                               Atspi.Role.TOOL_BAR]
        args['skipRoles'] = [Atspi.Role.PARAGRAPH,
                             Atspi.Role.LIST_ITEM,
                             Atspi.Role.TEXT]

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
        mnemonic, shortcut, accelerator = \
            self._script.utilities.mnemonicShortcutAccelerator(obj)
        if shortcut:
            if _settingsManager.getSetting('speechVerbosityLevel') == \
               settings.VERBOSITY_LEVEL_VERBOSE:
                shortcut = 'Alt Shift %s' % shortcut
            result = [keynames.localizeKeySequence(shortcut)]
            result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))

        return result
