# Orca
#
# Copyright 2005-2008 Google Inc.
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
#
"""Dectalk voice definitions using ACSS.

This module encapsulates Dectalk-specific voice definitions.  It
maps device-independent ACSS voice definitions into appropriate
Dectalk voice parameter settings.

"""

__id__ = "$Id$"
__author__ = "T. V. Raman"
__version__ = "$Revision$"
__date__ = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Google Inc."
__license__ = "LGPL"

import chnames

# Handling of special characters
#
# Emacspeak uses Tcl syntax to communicate with its speech servers.  It
# embraces text in curly braces, so that at least {, }, and \ must be quoted
# when sending text to speech server.  But individual speech engines have
# their own special characters in addition to those of Tcl.  Dectalk
# perceives speech parameters enclosed in square brackets, and Emacspeak
# exploits this to transmit speech settings to Dectalk.  Thus we must quote
# [ and ] too.

def makeSpecialCharMap():
    """Returns list of pairs mapping characters which are special for
    Dectalk speech server to their replacements.
    """
    chars = r'{\}[]'
    return [(ch, ' '+chnames.getCharacterName(ch)+' ') for ch in chars]


# Speech parameters

_defined_voices = {}

# Map from ACSS dimensions to Dectalk settings:

_table = {}
#family codes:

_table['family'] = {
    'male' : ' :np ',
    'paul' :  ':np',
    'man' :  ':nh',
    'harry' : ' :nh ',
    'dennis' :  ':nd',
    'frank' :  ':nf',
    'betty' :  ':nb',
    'female' : ' :nb ',
    'ursula' :  ':nu',
    'wendy' :  ':nw',
    'rita' :  ':nr',
    'kid' :  ':nk',
    'child' : ' :nk '
    }

# average-pitch :
# Average pitch for standard male voice is 122hz --this is mapped to
# a setting of 5.
# Average pitch varies inversely with speaker head size --a child
# has a small head and a higher pitched voice.
# We change parameter head-size in conjunction with average pitch to
# produce a more natural change on the Dectalk.

#male average pitch

def _update_map(table, key, format,  settings):
    """Internal function to update acss->synth mapping."""
    table[key] = {}
    for setting  in  settings:
        _table[key][setting[0]] = format % setting[1:]

_male_ap = [
    (0, 96, 115),
    (1, 101, 112),
    (2, 108, 109),
    (3, 112, 106),
    (4, 118, 103),
    (5, 122, 100),
    (6, 128, 98),
    (7, 134, 96),
    (8, 140, 94),
    (9, 147, 91)
    ]

_update_map(_table, ('male', 'average-pitch'),
            " ap %s hs %s ",  _male_ap)
_update_map(_table, ('paul', 'average-pitch'),
            " ap %s hs %s ",  _male_ap)

#Man  has a big head --and a lower pitch for the middle setting
_man_ap = [
    (0, 50, 125),
    (1, 59, 123),
    (2, 68, 121),
    (3, 77, 120),
    (4, 83, 118),
    (5, 89, 115),
    (6, 95, 112),
    (7, 110, 105),
    (8, 125, 100),
    (9, 140, 95)
    ]

_update_map(_table, ('man', 'average-pitch'),
            " ap %s hs %s ",_man_ap)
_update_map(_table, ('harry', 'average-pitch'),
            " ap %s hs %s ",_man_ap)

_female_ap = [
    (0, 160, 115),
    (1, 170, 112),
    (2, 181, 109),
    (3, 192, 106),
    (4, 200, 103),
    (5, 208, 100),
    (6, 219, 98),
    (7, 225, 96),
    (8, 240, 94),
    (9, 260, 91)
    ]

_update_map(_table, ('female', 'average-pitch'),
            " ap %s hs %s ",_female_ap)
_update_map(_table, ('betty', 'average-pitch'),
            " ap %s hs %s ",_female_ap)

# The default DECtalk values for the pitch of the other voices seem
# to be as follows:
# Frank = 155, Dennis = 110, Ursula = 240, Rita = 106, Wendy = 200
# Kit = Child = 306
# Therefore, follow TV Raman's lead:

_frank_ap = [
    (0, 129, 115),
    (1, 134, 112),
    (2, 141, 109),
    (3, 145, 106),
    (4, 151, 103),
    (5, 155, 100),
    (6, 159, 98),
    (7, 165, 96),
    (8, 171, 94),
    (9, 178, 91)
    ]

_update_map(_table, ('frank', 'average-pitch'),
            " ap %s hs %s ",  _frank_ap)

_dennis_ap = [
    (0, 84, 115),
    (1, 89, 112),
    (2, 96, 109),
    (3, 100, 106),
    (4, 106, 103),
    (5, 110, 100),
    (6, 116, 98),
    (7, 122, 96),
    (8, 128, 94),
    (9, 135, 91)
    ]

_update_map(_table, ('dennis', 'average-pitch'),
            " ap %s hs %s ",  _dennis_ap)

_ursula_ap = [
    (0, 196, 115),
    (1, 206, 112),
    (2, 215, 109),
    (3, 224, 106),
    (4, 232, 103),
    (5, 240, 100),
    (6, 251, 98),
    (7, 265, 96),
    (8, 280, 94),
    (9, 300, 91)
    ]

_update_map(_table, ('ursula', 'average-pitch'),
            " ap %s hs %s ",  _ursula_ap)

_rita_ap = [
    (0, 62, 115),
    (1, 72, 112),
    (2, 81, 109),
    (3, 90, 106),
    (4, 98, 103),
    (5, 106, 100),
    (6, 117, 98),
    (7, 131, 96),
    (8, 146, 94),
    (9, 166, 91)
    ]

_update_map(_table, ('rita', 'average-pitch'),
            " ap %s hs %s ",  _rita_ap)

# For some reason, Wendy at a high pitch causes the
# synthesizer to click and eventually make a feedback sound!
# It doesn't seem to be the result of the pitch.
# Keeping head size constant for higher pitch seems to eliminate
# the problem.

_wendy_ap = [
    (0, 156, 115),
    (1, 166, 112),
    (2, 175, 109),
    (3, 184, 106),
    (4, 192, 103),
    (5, 200, 100),
    (6, 211, 100),
    (7, 225, 100),
    (8, 240, 100),
    (9, 260, 100)
    ]

_update_map(_table, ('wendy', 'average-pitch'),
            " ap %s hs %s ",  _wendy_ap)

# Kit/Child can't have the traditional adult head size
# Setting the largest head size is the smallest adult
# female head size.

_child_ap = [
    (0, 256, 91),
    (1, 266, 89),
    (2, 276, 87),
    (3, 286, 85),
    (4, 296, 83),
    (5, 306, 81),
    (6, 316, 79),
    (7, 326, 77),
    (8, 336, 75),
    (9, 346, 73)
    ]

_update_map(_table, ('child', 'average-pitch'),
            " ap %s hs %s ",  _child_ap)
_update_map(_table, ('kit', 'average-pitch'),
            " ap %s hs %s ",  _child_ap)

# pitch-range for male:

#  Standard pitch range is 100 and is  mapped to
# a setting of 5.
# A value of 0 produces a flat monotone voice --maximum value of 250
# produces a highly animated voice.
# Additionally, we also set the assertiveness of the voice so the
# voice is less assertive at lower pitch ranges.

_male_pr = [
    (0, 0, 0),
    (1, 20, 10),
    (2, 40, 20),
    (3, 60, 30),
    (4, 80, 40, ),
    (5, 100, 50, ),
    (6, 137, 60),
    (7, 174, 70),
    (8, 211, 80),
    (9, 250, 100),
    ]

_update_map(_table, ('male', 'pitch-range'),
            " pr %s as %s ", _male_pr)
_update_map(_table, ('paul', 'pitch-range'),
            " pr %s as %s ", _male_pr)

# For now, assume that standard pitch range is reasonably
# consistent for all male voices with the execption of harry

_update_map(_table, ('frank', 'pitch-range'),
            " pr %s as %s ", _male_pr)
_update_map(_table, ('dennis', 'pitch-range'),
            " pr %s as %s ", _male_pr)


_man_pr = [
    (0, 0, 0),
    (1, 16, 20),
    (2, 32, 40),
    (3, 48, 60),
    (4, 64, 80, ),
    (5, 80, 100, ),
    (6, 137, 100),
    (7, 174, 100),
    (8, 211, 100),
    (9, 250, 100)
    ]

_update_map(_table, ('man', 'pitch-range'),
            " pr %s as %s ", _man_pr)
_update_map(_table, ('harry', 'pitch-range'),
            " pr %s as %s ", _man_pr)

_female_pr = [
    (0, 0, 0),
    (1, 50, 10),
    (2, 80, 20),
    (3, 100, 25),
    (4, 110, 30, ),
    (5, 140, 35),
    (6, 165, 57),
    (7, 190, 75),
    (8, 220, 87),
    (9, 250, 100)
    ]

_update_map(_table, ('female', 'pitch-range'),
            " pr %s as %s ", _female_pr)
_update_map(_table, ('betty', 'pitch-range'),
            " pr %s as %s ", _female_pr)

# For now, assume that standard pitch range is reasonably
# consistent for all female voices, including kit

_update_map(_table, ('ursula', 'pitch-range'),
            " pr %s as %s ", _female_pr)
_update_map(_table, ('rita', 'pitch-range'),
            " pr %s as %s ", _female_pr)
_update_map(_table, ('wendy', 'pitch-range'),
            " pr %s as %s ", _female_pr)
_update_map(_table, ('kit', 'pitch-range'),
            " pr %s as %s ", _female_pr)
_update_map(_table, ('child', 'pitch-range'),
            " pr %s as %s ", _female_pr)

# Stress:

# On the Dectalk we vary four parameters
# The hat rise which controls the overall shape of the F0 contour
# for sentence level intonation and stress,
# The stress rise that controls the level of stress on stressed
# syllables,
# the baseline fall for paragraph level intonation
# and the quickness --a parameter that controls whether the final
# frequency targets are completely achieved in the phonetic transitions.

_male_stress = [
    (0, 0, 0, 0, 0),
    (1, 3, 6, 20, 3),
    (2, 6, 12, 40, 6),
    (3, 9, 18, 60, 9, ),
    (4, 12, 24, 80, 14),
    (5, 18, 32, 100, 18),
    (6, 34, 50, 100, 20),
    (7, 48, 65, 100, 35),
    (8, 63, 82, 100, 60),
    (9, 80, 90, 100, 40)
]

_update_map(_table, ('male', 'stress'),
            " hr %s sr %s qu %s bf %s ", _male_stress)
_update_map(_table, ('paul', 'stress'),
            " hr %s sr %s qu %s bf %s ", _male_stress)

# For now, grabbing these values for all males but Harry

_update_map(_table, ('frank', 'stress'),
            " hr %s sr %s qu %s bf %s ", _male_stress)
_update_map(_table, ('dennis', 'stress'),
            " hr %s sr %s qu %s bf %s ", _male_stress)


_man_stress = [
    (0, 0, 0, 0, 0),
    (1, 4, 6, 2, 2),
    (2, 8, 12, 4, 4),
    (3, 12, 18, 6, 6),
    (4, 16, 24, 8, 8),
    (5, 20, 30, 10, 9),
    (6, 40, 48, 32, 16),
    (7, 60, 66, 54, 22),
    (8, 80, 78, 77, 34),
    (9, 100, 100, 100, 40)
    ]

_update_map(_table, ('man', 'stress'),
            " hr %s sr %s qu %s bf %s ", _man_stress)
_update_map(_table, ('harry', 'stress'),
            " hr %s sr %s qu %s bf %s ", _man_stress)

_female_stress = [
    (0, 1, 1, 0, 0),
    (1, 3, 4, 11, 0),
    (2, 5, 8, 22, 0),
    (3, 8, 12, 33, 0),
    (4, 11, 16, 44, 0),
    (5, 14, 20, 55, 0),
    (6, 35, 40, 65, 10),
    (7, 56, 80, 75, 20),
    (8, 77, 90, 85, 30),
    (9, 100, 100, 100, 40)
    ]

_update_map(_table, ('female', 'stress'),
            " hr %s sr %s qu %s bf %s ", _female_stress)
_update_map(_table, ('betty', 'stress'),
            " hr %s sr %s qu %s bf %s ", _female_stress)

# For now, grabbing these values for all females including kit

_update_map(_table, ('ursula', 'stress'),
            " hr %s sr %s qu %s bf %s ", _female_stress)
_update_map(_table, ('rita', 'stress'),
            " hr %s sr %s qu %s bf %s ", _female_stress)
_update_map(_table, ('wendy', 'stress'),
            " hr %s sr %s qu %s bf %s ", _female_stress)
_update_map(_table, ('kit', 'stress'),
            " hr %s sr %s qu %s bf %s ", _female_stress)
_update_map(_table, ('child', 'stress'),
            " hr %s sr %s qu %s bf %s ", _female_stress)

#richness

# Smoothness and richness vary inversely.
# a  maximally smooth voice produces a quieter effect
# a rich voice is "bright" in contrast.

_male_richness = [
    (0, 0, 100),
    (1, 14, 80),
    (2, 28, 60),
    (3, 42, 40),
    (4, 56, 30),
    (5, 70, 28),
    (6, 60, 24 ),
    (7, 70, 16),
    (8, 80, 8),
    (9, 100, 0)
    ]

_update_map(_table, ('male', 'richness'),
            " ri %s sm %s " ,_male_richness)
_update_map(_table, ('paul', 'richness'),
            " ri %s sm %s " ,_male_richness)

# For now, grabbing these values for all males but Harry

_update_map(_table, ('frank', 'richness'),
            " ri %s sm %s " ,_male_richness)
_update_map(_table, ('dennis', 'richness'),
            " ri %s sm %s " ,_male_richness)

_man_richness = [
    (0, 100, 0),
    (1, 96, 3),
    (2, 93, 6),
    (3, 90, 9),
    (4, 88, 11),
    (5, 86, 12),
    (6, 60, 24, ),
    (7, 40, 44),
    (8, 20, 65),
    (9, 0, 70)
    ]

_update_map(_table, ('man', 'richness'),
            " ri %s sm %s " , _man_richness)
_update_map(_table, ('harry', 'richness'),
            " ri %s sm %s " , _man_richness)

_female_richness = [
    (0, 0, 100),
    (1, 8, 76),
    (2, 16, 52),
    (3, 24,28),
    (4, 32, 10),
    (5, 40, 4),
    (6, 50, 3),
    (7, 65, 3),
    (8, 80,  2),
    (9, 100, 0)
    ]

_update_map(_table, ('female', 'richness'),
            " ri %s sm %s ", _female_richness)
_update_map(_table, ('betty', 'richness'),
            " ri %s sm %s ", _female_richness)

# For now, grabbing these values for all females including kit

_update_map(_table, ('ursula', 'richness'),
            " ri %s sm %s ", _female_richness)
_update_map(_table, ('rita', 'richness'),
            " ri %s sm %s ", _female_richness)
_update_map(_table, ('wendy', 'richness'),
            " ri %s sm %s ", _female_richness)
_update_map(_table, ('kit', 'richness'),
            " ri %s sm %s ", _female_richness)
_update_map(_table, ('child', 'richness'),
            " ri %s sm %s ", _female_richness)


def getrate(r):
    return int(180 + 4*r)

def getvolume(v):
    return int(10*v)

def getvoicelist(): 
    return _table['family'].keys()

def getvoice(acss):
    """Memoized function that returns  synthesizer code for
    specified  ACSS setting.
    Synthesizer code is a tupple of the form (open,close)
    where open sets the voice, and close resets it."""
    name = acss.name()
    if name in _defined_voices:
        return _defined_voices[name]
    _defined_voices[name] = acss2voice(acss)
    return _defined_voices[name]

def acss2voice(acss):
    """Return synthesizer code."""
    code = ""
    familyName = 'male'
    if 'family' in acss:
        familyName = acss['family']['name']
        if familyName in _table['family']:
            code += _table['family'][familyName]
    if 'rate' in acss:
        code += " :ra %s" % getrate(acss['rate'])
    if 'punctuations' in acss:
        code += " :punc %s" % acss['punctuations']
    if 'gain' in acss:
        code += " :volume set %s" % getvolume(acss['gain'])
    voice = ""
    dv = ""
    for d in ['average-pitch', 'pitch-range',
              'richness', 'stress']:
        if d in acss:
            if (familyName, d) in _table:
                voice += _table[(familyName, d)][int(acss[d])]
    if voice:
        dv = " :dv %s" % voice
    if code or voice:
        code = "[%s  %s]" % (code, dv)
    return (code, " [:np] ")
