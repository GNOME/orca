# Orca
#
# Copyright 2005-2008 Google Inc.
# Portions Copyright 2007-2008, Sun Microsystems, Inc.
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
__copyright__ = "Copyright (c) 2005-2008 Google Inc."
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
        GAIN :          10,
        AVERAGE_PITCH : 5,
        PITCH_RANGE :   5,
        STRESS :        5,
        RICHNESS :      5,
        PUNCTUATIONS :  'all'
    }

    def __init__(self, props=None):
        """Create and initialize ACSS structure."""
        dict.__init__(self)
        props = props or {}
        if props:
            for k in props:
                if k == 'established' or k in ACSS.settings:
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
        else:
            self['established'] = False

    def __eq__(self, other):
        if not isinstance(other, ACSS):
            return False
        if self.get(ACSS.FAMILY) != other.get(ACSS.FAMILY):
            return False
        if self.get(ACSS.RATE) != other.get(ACSS.RATE):
            return False
        if self.get(ACSS.AVERAGE_PITCH) != other.get(ACSS.AVERAGE_PITCH):
            return False
        return True

    def __setitem__ (self, key, value):
        """Update name when we change values."""
        dict.__setitem__(self, key, value)

    def __delitem__(self, key):
        """Update name if we delete a key."""
        dict.__delitem__(self, key)

    def name(self):
        _name = 'acss-'
        names = list(self.keys())
        if names:
            names.sort()
            for  k in names:
                _name += f"{k}-{self[k]}:"
        _name = _name[:-1]
        return _name

    def getLocale(self):
        family = self.get(ACSS.FAMILY, {})
        return family.get('locale')

    def getDialect(self):
        family = self.get(ACSS.FAMILY, {})
        return family.get('dialect')

    def update(self, newDict):
        family = newDict.get(ACSS.FAMILY)
        if isinstance(family, dict) and family.get('name') is None:
            newDict.pop(ACSS.FAMILY)

        return super().update(newDict)
