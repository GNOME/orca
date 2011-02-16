# Orca
#
# Copyright 2010 Consorcio Fernando de los Rios.
# Author: J. Ignacio Alvarez <jialvarez@emergya.es>
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

"""Import the appropriate module and return the desired window."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2010 Consorcio Fernando de los Rios."
__license__   = "LGPL"

import sys
import os
from orca import orca_platform
from orca import debug

OS = None

class Factory:
    def __init__(self, library='gtk2', window='main'):
        self.library = library
        self.window = window

    def loadModule(self):
        """Load specific module for present view to user"""

        try:
            gui = 'views.%s.orca_gui_%s_%s' % (self.library, self.window, self.library)
            self.guiModule = __import__(gui, 
                                        globals(), 
                                        locals(),
                                        [''])
            return self.guiModule
        except ImportError, e:
            debug.printException(debug.LEVEL_SEVERE)
            print "Exception raised when importing the module %s: %s" % (gui, str(e))

    def loadController(self):
        """Load specific controller for present view to user"""

        try:
            cnt = 'controllers.%s.orca_controller_%s_%s' % (self.library, self.window, self.library)
            self.cntModule = __import__(cnt,
                                        globals(), 
                                        locals(),
                                        [''])

            return self.cntModule
        except ImportError, e:
            debug.printException(debug.LEVEL_SEVERE)
            print "Exception raised when importing the controller %s: %s"  + (gui, str(e))


