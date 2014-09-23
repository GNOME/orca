# Orca
#
# Copyright 2014 Orca Team.
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
__copyright__ = "Copyright (c) 2014 Orca Team."
__license__   = "LGPL"

import orca.tutorialgenerator as tutorial_generator

class TutorialGenerator(tutorial_generator.TutorialGenerator):
    def __init__(self, script):
        tutorial_generator.TutorialGenerator.__init__(self, script)

    def getTutorial(self, obj, alreadyFocused, forceTutorial=False):
        if self._script.utilities.isFocusModeWidget(obj) \
           and not self._script.useFocusMode(obj):
            return []

        return tutorial_generator.TutorialGenerator.getTutorial(
            self, obj, alreadyFocused, forceTutorial)
