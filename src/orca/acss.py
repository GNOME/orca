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


class ACSS(dict):
    """Holds ACSS representation of a voice."""

    FAMILY = "family"
    RATE = "rate"
    GAIN = "gain"
    AVERAGE_PITCH = "average-pitch"
    PITCH_RANGE = "pitch-range"
    STRESS = "stress"
    RICHNESS = "richness"
    PUNCTUATIONS = "punctuations"

    settings = {
        FAMILY: None,  # None means use the engine's default value.
        RATE: 50,
        GAIN: 10,
        AVERAGE_PITCH: 5,
        PITCH_RANGE: 5,
        STRESS: 5,
        RICHNESS: 5,
        PUNCTUATIONS: "all",
    }

    def __init__(self, props: dict | None = None):
        """Create and initialize ACSS structure."""

        super().__init__()
        if not props:
            self["established"] = False
            return
        for key, value in props.items():
            if key == "established" or key in ACSS.settings:
                self[key] = dict(value) if key == ACSS.FAMILY else value

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

    def update(self, new_dict):
        family = new_dict.get(ACSS.FAMILY)
        if isinstance(family, dict) and family.get("name") is None:
            new_dict.pop(ACSS.FAMILY)

        return super().update(new_dict)
