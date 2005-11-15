"""ACSS --- Aural CSS.

Class ACSS defines a simple wrapper for holding ACSS voice
definitions.  Speech engines implement the code for converting
ACSS definitions into engine-specific markup codes.

"""

__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
__date__ = "$Date$"
__copyright__ = "Copyright (c) 2005 T. V. Raman"
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
            if k in ACSS.settings: self[k] = props[k]
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
