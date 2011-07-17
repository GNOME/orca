# Orca
#
# Copyright (C) 2010 Joanmarie Diggs
#
# Author: Joanmarie Diggs <joanied@gnome.org>
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
__copyright__ = "Copyright (c) 2010 Joanmarie Diggs"
__license__   = "LGPL"

import pyatspi

import orca.keynames as keynames
import orca.orca as orca
import orca.rolenames as rolenames
import orca.settings as settings
import orca.speech_generator as speech_generator

from orca.orca_i18n import _

_settingsManager = getattr(orca, '_settingsManager')

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
        if string.decode("UTF-8").isupper():
            voice = settings.voices[settings.UPPERCASE_VOICE]

        return voice

    def _generateRoleName(self, obj, **args):
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
            if role == pyatspi.ROLE_IMAGE:
                link = self._script.utilities.ancestorWithRole(
                    obj, [pyatspi.ROLE_LINK], [pyatspi.ROLE_DOCUMENT_FRAME])
                if link:
                    result.append(rolenames.getSpeechForRoleName(link))

            if role == pyatspi.ROLE_HEADING:
                level = self._script.utilities.headingLevel(obj)
                if level:
                    # Translators: the %(level)d is in reference to a heading
                    # level in HTML (e.g., For <h3>, the level is 3)
                    # and the %(role)s is in reference to a previously
                    # translated rolename for the heading.
                    #
                    result.append(_("%(role)s level %(level)d") % {
                        'role': rolenames.getSpeechForRoleName(obj, role),
                        'level': level})
                else:
                    result.append(rolenames.getSpeechForRoleName(obj, role))
            else:
                result.append(rolenames.getSpeechForRoleName(obj, role))

            if result:
                result.extend(acss)

            if role == pyatspi.ROLE_LINK \
               and obj.childCount and obj[0].getRole() == pyatspi.ROLE_IMAGE:
                # If this is a link with a child which is an image, we
                # want to indicate that.
                #
                acss = self.voice(speech_generator.HYPERLINK)
                result.append(rolenames.getSpeechForRoleName(obj[0]))
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
