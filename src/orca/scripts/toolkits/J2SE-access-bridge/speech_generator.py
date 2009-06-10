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
