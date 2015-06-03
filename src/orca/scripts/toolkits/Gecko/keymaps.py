# Orca
#
# Copyright 2010 Joanmarie Diggs, Mesar Hameed.
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
    pulled out from script.py: __getLaptopBindings()
    with the goal of being more readable and less monolithic.
"""

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2010 Joanmarie Diggs, Mesar Hameed."
__license__   = "LGPL"

import orca.keybindings as keybindings

# Storing values 
defaultModifierMask = keybindings.defaultModifierMask
ORCA_MODIFIER_MASK = keybindings.ORCA_MODIFIER_MASK
NO_MODIFIER_MASK = keybindings.NO_MODIFIER_MASK
ORCA_SHIFT_MODIFIER_MASK = keybindings.ORCA_SHIFT_MODIFIER_MASK
ORCA_CTRL_MODIFIER_MASK = keybindings.ORCA_CTRL_MODIFIER_MASK
CTRL_MODIFIER_MASK = keybindings.CTRL_MODIFIER_MASK
ALT_MODIFIER_MASK = keybindings.ALT_MODIFIER_MASK
SHIFT_MODIFIER_MASK = keybindings.SHIFT_MODIFIER_MASK

# KeyBindings that use the arrow keys for navigating HTML content.
arrowKeymap = (
    ("Right", defaultModifierMask, NO_MODIFIER_MASK, "goNextCharacterHandler"),

    ("Left", defaultModifierMask, NO_MODIFIER_MASK, 
    "goPreviousCharacterHandler"),

    ("Right", defaultModifierMask, CTRL_MODIFIER_MASK, "goNextWordHandler"),
    ("Left", defaultModifierMask, CTRL_MODIFIER_MASK, "goPreviousWordHandler"),
    ("Up", defaultModifierMask, NO_MODIFIER_MASK, "goPreviousLineHandler"),
    ("Down", defaultModifierMask, NO_MODIFIER_MASK, "goNextLineHandler"),
    ("Home", defaultModifierMask, CTRL_MODIFIER_MASK, "goTopOfFileHandler"),
    ("End", defaultModifierMask, CTRL_MODIFIER_MASK, "goBottomOfFileHandler"),
    ("Home", defaultModifierMask, NO_MODIFIER_MASK, "goBeginningOfLineHandler"),
    ("End", defaultModifierMask, NO_MODIFIER_MASK, "goEndOfLineHandler"),
)

commonKeymap = (
    ("F12", defaultModifierMask, ORCA_MODIFIER_MASK,
    "toggleCaretNavigationHandler"),

    ("a", defaultModifierMask, ORCA_MODIFIER_MASK, "togglePresentationModeHandler"),
    ("a", defaultModifierMask, ORCA_MODIFIER_MASK, "enableStickyFocusModeHandler", 2),
)

desktopKeymap = (
    ("KP_Multiply", defaultModifierMask, ORCA_MODIFIER_MASK, 
    "moveToMouseOverHandler"),
)

laptopKeymap = (
    ("0", defaultModifierMask, ORCA_MODIFIER_MASK, "moveToMouseOverHandler"),
)
