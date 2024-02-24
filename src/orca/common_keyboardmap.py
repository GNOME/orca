# Orca
#
# Copyright 2010-2011 The Orca Team
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

""" A list of common keybindings and unbound keys
    pulled out from default.py: getKeyBindings()
    with the goal of being more readable and less monolithic.
"""

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2010-2011 The Orca Team"
__license__   = "LGPL"

from . import keybindings

defaultModifierMask = keybindings.defaultModifierMask
ORCA_MODIFIER_MASK = keybindings.ORCA_MODIFIER_MASK
NO_MODIFIER_MASK = keybindings.NO_MODIFIER_MASK
ORCA_CTRL_MODIFIER_MASK = keybindings.ORCA_CTRL_MODIFIER_MASK

keymap = (

    ("space", defaultModifierMask, ORCA_MODIFIER_MASK,
    "preferencesSettingsHandler"),

    ("space", defaultModifierMask, ORCA_CTRL_MODIFIER_MASK,
    "appPreferencesSettingsHandler"),

    #####################################################################
    #                                                                   #
    #  Unbound handlers                                                 #
    #                                                                   #
    #####################################################################

    ("", defaultModifierMask, NO_MODIFIER_MASK,
    "cycleSettingsProfileHandler"),

    ("", defaultModifierMask, NO_MODIFIER_MASK,
    "cycleDebugLevelHandler"),

    ("", defaultModifierMask, NO_MODIFIER_MASK,
    "panBrailleLeftHandler"),

    ("", defaultModifierMask, NO_MODIFIER_MASK,
    "panBrailleRightHandler"),

    ("", defaultModifierMask, NO_MODIFIER_MASK,
    "shutdownHandler"),
)
