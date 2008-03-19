# Orca
#
# Copyright 2006-2007 Sun Microsystems Inc.
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
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

"""Custom script for planner."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2006-2007 Sun Microsystems Inc."
__license__   = "LGPL"

import orca.default as default
import orca.braille as braille
import orca.settings as settings
import orca.speechgenerator as speechgenerator
import orca.braillegenerator as braillegenerator
import pyatspi

from orca.orca_i18n import _ # for gettext support

class BrailleGenerator(braillegenerator.BrailleGenerator):
    """We make this to appropiately present ribbon's toggle button in
    a toolbar used to display in a menu those options that doesn't
    fill in toolbar when the application is resized. Also for each one
    of the grphics buttons in the main window."""

    def __init__(self, script):
        braillegenerator.BrailleGenerator.__init__(self, script)

    def _getBrailleRegionsForToggleButton(self, obj):
        """Get the braille for a radio button.  If the button already had
        focus, then only the state is displayed.

        Arguments:
        - obj: the check box

        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """

        self._debugGenerator("_getBrailleRegionsForRadioButton", obj)

        text = ""
        text = self._script.appendString(text, 
                                         self._script.getDisplayedLabel(obj))
        text = self._script.appendString(text, 
                                         self._script.getDisplayedText(obj))

        # First special toggle button is the one in the toolbar and
        # that it has no name Application should implement an
        # accessible name in this component, but until this is made We
        # speech/braille "display more options" when the focus is in
        # one of these toggle buttons.
        #
        roleList = [pyatspi.ROLE_TOGGLE_BUTTON, pyatspi.ROLE_TOOL_BAR]

        if self._script.isDesiredFocusedItem(obj, roleList) and not obj.name:
            text += _("Display more options")

        text = self._script.appendString(text, self._getTextForRole(obj))

        if obj.getState().contains(pyatspi.STATE_CHECKED):
            brailleindicatorindex = 1
        else:
            brailleindicatorindex = 0

        regions = []
        indicator = \
            settings.brailleRadioButtonIndicators[brailleindicatorindex]
        componentRegion = braille.Component(obj, text, indicator=indicator)
        regions.append(componentRegion)

        return [regions, componentRegion]

class SpeechGenerator(speechgenerator.SpeechGenerator):

    def __init__(self, script):
        speechgenerator.SpeechGenerator.__init__(self, script)

    # We make this to appropiately present ribbon's toggle button in a
    # toolbar used to display in a menu those options that doesn fill
    # in toolbar when the application is resized.
    #
    # Also for each one of the grphics buttons in the main window
    #
    def _getSpeechForToggleButton(self, obj, already_focused):
        utterances = []
        tmp = []

        # Application should implement an accessible name in this
        # component, but until this is made We speech/braille "display
        # more options" when the focus is in one of these toggle
        # buttons.
        #

        roleList = [pyatspi.ROLE_TOGGLE_BUTTON, \
                    pyatspi.ROLE_TOOL_BAR]

        if self._script.isDesiredFocusedItem(obj, roleList) and not obj.name:
            if not already_focused:
                tmp.append(_("Display more options"))
                tmp.extend(self._getDefaultSpeech(obj, already_focused))

                if obj.getState().contains(pyatspi.STATE_CHECKED):
                    tmp.append(_("pressed"))
                else:
                    tmp.append(_("not pressed"))

                utterances.extend(tmp)
                utterances.extend(self._getSpeechForObjectAvailability(obj))
            else:
                if obj.getState().contains(pyatspi.STATE_CHECKED):
                    utterances.append(_("pressed"))
                else:
                    utterances.append(_("not pressed"))

            return utterances

        return self._getSpeechForLabel(obj, already_focused)

########################################################################
#                                                                      #
# The planner script class.                                            #
#                                                                      #
########################################################################

class Script(default.Script):

    def __init__(self, app):
        """Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """
        default.Script.__init__(self, app)

    # This method tries to detect and handle the following cases:
    # 1) Toolbar: the last toggle button to show 'more options'
    # 2) Main window: one of the four graphic toggle buttons.
    #
    def getBrailleGenerator(self):
        return BrailleGenerator(self)

    def getSpeechGenerator(self):
        return SpeechGenerator(self)
