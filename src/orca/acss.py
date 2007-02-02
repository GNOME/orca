# Orca
#
# Copyright 2005-2006 Google Inc.
# Portions Copyright 2007, Sun Microsystems, Inc.
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
#
"""ACSS --- Aural CSS.

Class ACSS defines a simple wrapper for holding ACSS voice
definitions.  Speech engines implement the code for converting
ACSS definitions into engine-specific markup codes.

"""

__id__ = "$Id$"
__author__ = "T. V. Raman"
__version__ = "$Revision$"
__date__ = "$Date$"
__copyright__ = "Copyright (c) 2005 Google Inc."
__license__ = "LGPL"

class ACSS(dict):

    """Holds ACSS representation of a voice."""

    FAMILY        = 'family'
    RATE          = 'rate'
    GAIN          = 'gain'
    AVERAGE_PITCH = 'average-pitch'
    PITCH_RANGE   = 'pitch-range'
    STRESS        = 'stress'
    RICHNESS      = 'richness'
    PUNCTUATIONS  = 'punctuations'

    # A value of None means use the engine's default value.
    #
    settings = {
        FAMILY :        None,
        RATE :          50,
        GAIN :          5,
        AVERAGE_PITCH : 5,
        PITCH_RANGE :   5,
        STRESS :        5,
        RICHNESS :      5,
        PUNCTUATIONS :  'all'
    }

    def __init__(self,props={}):
        """Create and initialize ACSS structure."""
        for k in props:
            if k in ACSS.settings:
                # Do a 'deep copy' of the family.  Otherwise,
                # the new ACSS shares the actual data with the
                # props passed in.  This can cause unexpected
                # side effects.
                #
                if k == ACSS.FAMILY:
                    self[k] = {}
                    for j in props[k].keys():
                        self[k][j] = props[k][j]
                else:
                    self[k] = props[k]
        self.updateName()

    def __setitem__ (self, key, value):
        """Update name when we change values."""
        dict.__setitem__(self, key, value)
        self.updateName()

    def __delitem__(self, key):
        """Update name if we delete a key."""
        dict.__delitem__(self,key)
        self.updateName()

    def updateName(self):
        """Update name based on settings."""
        _name='acss-'
        names = self.keys()
        if names:
            names.sort()
            for  k in names:
                _name += "%s-%s:" % (k, self[k])
        self._name = _name[:-1]

    def name(self): return self._name
