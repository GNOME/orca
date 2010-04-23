# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., Franklin Street, Fifth Floor,
# Boston MA  02110-1301 USA.

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi

import orca.settings as settings
import orca.speech_generator as speech_generator

########################################################################
#                                                                      #
# Speech Generator                                                     #
#                                                                      #
########################################################################

class SpeechGenerator(speech_generator.SpeechGenerator):

    # pylint: disable-msg=W0142

    def __init__(self, script):
        speech_generator.SpeechGenerator.__init__(self, script)

    def _generateAncestors(self, obj, **args):
        """The Swing toolkit has labelled panels that do not implement the
        AccessibleText interface, but getDisplayedText returns a
        meaningful string that needs to be used if getDisplayedLabel
        returns None.
        """
        args['requireText'] = False
        result = speech_generator.SpeechGenerator._generateAncestors(
            self, obj, **args)
        del args['requireText']
        return result

    def _generatePositionInList(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the relative position of an
        object in a list.
        """

        listObj = None
        if obj and obj.getRole() == pyatspi.ROLE_COMBO_BOX:
            allLists = self._script.findByRole(obj, pyatspi.ROLE_LIST, False)
            if len(allLists) == 1:
                listObj = allLists[0]

        if not listObj:
            return speech_generator.SpeechGenerator._generatePositionInList(
                self, obj, **args)

        result = []
        name = self._generateName(obj)
        position = -1
        index = total = 0

        for child in listObj:
            nextName = self._generateName(child)
            if not nextName or nextName[0] in ["", "Empty", "separator"] \
               or not child.getState().contains(pyatspi.STATE_VISIBLE):
                continue

            index += 1
            total += 1

            if nextName == name:
                position = index

        if (settings.enablePositionSpeaking or args.get('forceList', False)) \
           and position >= 0:
            result.append(self._script.formatting.getString(
                              mode='speech', stringType='groupindex') \
                              %  {"index" : position, "total" : total})

        return result
        
    def generateSpeech(self, obj, **args):
        result = []
        if args.get('formatType', 'unfocused') == 'basicWhereAmI' \
           and obj.getRole() == pyatspi.ROLE_TEXT:
            spinbox = self._script.getAncestor(obj,
                                               [pyatspi.ROLE_SPIN_BUTTON],
                                               None)
            if spinbox:
                obj = spinbox
        result.extend(speech_generator.SpeechGenerator.\
                                       generateSpeech(self, obj, **args))
        return result
