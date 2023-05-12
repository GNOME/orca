# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
# Copyright 2010 Joanmarie Diggs
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
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc., " \
                "Copyright (c) 2010 Joanmarie Diggs"
__license__   = "LGPL"

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

import orca.messages as messages
import orca.settings as settings
import orca.settings_manager as settings_manager
import orca.speech_generator as speech_generator
from orca.ax_object import AXObject

_settingsManager = settings_manager.getManager()

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
        AccessibleText interface, but displayedText returns a meaningful
        string that needs to be used if displayedLabel returns None.
        """
        args['requireText'] = False
        result = speech_generator.SpeechGenerator._generateAncestors(
            self, obj, **args)
        del args['requireText']
        return result

    def _generateNewAncestors(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the text of the ancestors for
        the object.  This is typically used to present the context for
        an object (e.g., the names of the window, the panels, etc.,
        that the object is contained in).  If the 'priorObj' attribute
        of the args dictionary is set, only the differences in
        ancestry between the 'priorObj' and the current obj will be
        computed.  Otherwise, no ancestry will be computed.  The
        'priorObj' is typically set by Orca to be the previous object
        with focus.
        """
        result = []
        if args.get('role', AXObject.get_role(obj)) == Atspi.Role.MENU:
            # We're way too chatty here -- at least with the Swing2
            # demo. Users entering a menu want to know they've gone
            # into a menu; not a huge ancestry.
            #
            return result
        result.extend(speech_generator.SpeechGenerator.\
                          _generateNewAncestors(self, obj, **args))
        return result

    def _generateNumberOfChildren(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represents the number of children the
        object has."""

        if _settingsManager.getSetting('onlySpeakDisplayedText') \
           or _settingsManager.getSetting('speechVerbosityLevel') == settings.VERBOSITY_LEVEL_BRIEF:
            return []

        result = []
        childCount = AXObject.get_child_count(obj)
        if obj and obj.getState().contains(Atspi.StateType.EXPANDED) \
           and AXObject.get_role(obj) == Atspi.Role.LABEL and childCount:
            result.append(messages.itemCount(childCount))
            result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))
        else:
            result.extend(speech_generator.SpeechGenerator.\
                          _generateNumberOfChildren(self, obj, **args))

        return result

    def _generatePositionInList(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the relative position of an
        object in a list.
        """

        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        listObj = None
        if obj and AXObject.get_role(obj) == Atspi.Role.COMBO_BOX:
            hasRole = lambda x: x and AXObject.get_role(x) == Atspi.Role.LIST
            allLists = self._script.utilities.findAllDescendants(obj, hasRole)
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
               or not child.getState().contains(Atspi.StateType.VISIBLE):
                continue

            index += 1
            total += 1

            if nextName == name:
                position = index

        if (_settingsManager.getSetting('enablePositionSpeaking') \
            or args.get('forceList', False)) \
           and position >= 0:
            result.append(self._script.formatting.getString(
                              mode='speech', stringType='groupindex') \
                              %  {"index" : position, "total" : total})
            result.extend(self.voice(speech_generator.SYSTEM, obj=obj, **args))
        return result
        
    def generateSpeech(self, obj, **args):
        result = []
        if AXObject.get_role(obj) == Atspi.Role.CHECK_BOX \
           and AXObject.get_role(obj.parent) == Atspi.Role.MENU:
            oldRole = self._overrideRole(Atspi.Role.CHECK_MENU_ITEM, args)
            result.extend(speech_generator.SpeechGenerator.\
                                           generateSpeech(self, obj, **args))
            self._restoreRole(oldRole, args)

        if args.get('formatType', 'unfocused') == 'basicWhereAmI' \
           and AXObject.get_role(obj) == Atspi.Role.TEXT:
            pred = lambda x: AXObject.get_role(x) == Atspi.Role.SPIN_BUTTON
            spinbox = AXObject.find_ancestor(obj, pred)
            if spinbox:
                obj = spinbox
        result.extend(speech_generator.SpeechGenerator.\
                                       generateSpeech(self, obj, **args))
        return result
