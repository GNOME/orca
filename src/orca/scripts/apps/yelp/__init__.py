# Orca
#
# Copyright 2011 The Orca Team.
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

""" Custom script for Yelp."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2011 The Orca Team."
__license__   = "LGPL"

import sys

import pyatspi
from orca.script_utilities import Utilities

def unloadYelpScript(version):
    if 'orca.scripts.apps.yelp.yelp_' + version in sys.modules:
        del(sys.modules['orca.scripts.apps.yelp.yelp_' + version])


def getScript(app):
    """Returns the correct version of the Yelp script based on toolkit."""
    docFrames = Utilities.descendantsWithRole(app, pyatspi.ROLE_DOCUMENT_FRAME)
    toolkit = ""
    if docFrames:
        attrs = dict([a.split(':', 1) for a in docFrames[0].getAttributes()])
        toolkit = attrs.get('toolkit', '')

    if toolkit == 'WebKitGtk':
        unloadYelpScript('v2')
        from yelp_v3 import script
        return script.Script(app)
    else:
        from yelp_v2 import script
        return script.Script(app)
