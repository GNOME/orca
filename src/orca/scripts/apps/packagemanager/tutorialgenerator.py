# Orca
#
# Copyright 2008-2009 Sun Microsystems Inc.
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
__copyright__ = "Copyright (c) 2008-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import orca.tutorialgenerator as tutorialgenerator

from orca.orca_i18n import _         # for gettext support

class TutorialGenerator(tutorialgenerator.TutorialGenerator):
    """Overridden here so that we can provide a custom message regarding
    how to move focus to the search results after a search has been
    executed. This is needed because focus remains in the Search entry,
    and an object in between the entry and the list of results clears
    the search automatically when given focus."""

    def __init__(self, script):
        tutorialgenerator.TutorialGenerator.__init__(self, script)

    def _getTutorialForText(self, obj, alreadyFocused, forceTutorial):
        """Get the tutorial string for a text object.

        Arguments:
        - obj: the text component
        - alreadyFocused: False if object just received focus
        - forceTutorial: used for when whereAmI really needs the tutorial
          string

        Returns a list of tutorial utterances to be spoken for the object.
        """

        utterances = tutorialgenerator.TutorialGenerator.\
            _getTutorialForText(self, obj, alreadyFocused, forceTutorial)
        if utterances and self._script.isSearchEntry(obj):
            # Translators: This is the tutorial string associated with a
            # specific search field in the Packagemanager application.
            # It is designed to inform the user how to move directly to
            # the search results after the search has been completed.
            #
            utterances.append(_("Use Ctrl+L to move focus to the results."))
        self._debugGenerator("_getTutorialForText",
                             obj,
                             alreadyFocused,
                             utterances)

        return utterances
