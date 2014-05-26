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
    pulled out from default.py: __getDesktopBindings()
    with the goal of being more readable and less monolithic.
"""

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2010 Joanmarie Diggs, Mesar Hameed."
__license__   = "LGPL"

from . import keybindings

# Storing values 
defaultModifierMask = keybindings.defaultModifierMask
ORCA_MODIFIER_MASK = keybindings.ORCA_MODIFIER_MASK
NO_MODIFIER_MASK = keybindings.NO_MODIFIER_MASK
ORCA_SHIFT_MODIFIER_MASK = keybindings.ORCA_SHIFT_MODIFIER_MASK

keymap = (

    ("KP_Divide", defaultModifierMask, ORCA_MODIFIER_MASK, 
    "routePointerToItemHandler"),

    # We want the user to be able to combine modifiers with the
    # mouse click (e.g. to Shift+Click and select), therefore we
    # do not "care" about the modifiers -- unless it's the Orca
    # modifier.
    #
    ("KP_Divide", ORCA_MODIFIER_MASK, NO_MODIFIER_MASK,
    "leftClickReviewItemHandler"),

    ("KP_Multiply", ORCA_MODIFIER_MASK, NO_MODIFIER_MASK,
    "rightClickReviewItemHandler"),

    ("KP_Subtract", defaultModifierMask, NO_MODIFIER_MASK,
    "toggleFlatReviewModeHandler"),

    ("KP_Add", defaultModifierMask, NO_MODIFIER_MASK,
    "sayAllHandler"),

    ("KP_Enter", defaultModifierMask, NO_MODIFIER_MASK,
    "whereAmIBasicHandler", 1),

    ("KP_Enter", defaultModifierMask, NO_MODIFIER_MASK,
    "whereAmIDetailedHandler", 2),

    ("KP_Enter", defaultModifierMask, ORCA_MODIFIER_MASK,
    "getTitleHandler", 1),

    ("KP_Enter", defaultModifierMask, ORCA_MODIFIER_MASK,
    "getStatusBarHandler", 2),

    ("KP_Delete", defaultModifierMask, NO_MODIFIER_MASK,
    "findHandler"),

    ("KP_Delete", defaultModifierMask, ORCA_MODIFIER_MASK,
    "findNextHandler"),

    ("KP_Delete", defaultModifierMask, ORCA_SHIFT_MODIFIER_MASK,
    "findPreviousHandler"),

    ("KP_Home", defaultModifierMask, NO_MODIFIER_MASK,
    "reviewPreviousLineHandler"),

    ("KP_Home", defaultModifierMask, ORCA_MODIFIER_MASK, 
    "reviewHomeHandler"),

    ("KP_Up", defaultModifierMask, NO_MODIFIER_MASK,
    "reviewCurrentLineHandler", 1),

    ("KP_Up", defaultModifierMask, NO_MODIFIER_MASK,
    "reviewSpellCurrentLineHandler", 2),

    ("KP_Up", defaultModifierMask, NO_MODIFIER_MASK,
    "reviewPhoneticCurrentLineHandler", 3),

    ("KP_Page_Up", defaultModifierMask, NO_MODIFIER_MASK, 
    "reviewNextLineHandler"),

    ("KP_Page_Up", defaultModifierMask, ORCA_MODIFIER_MASK,
    "reviewEndHandler"),

    ("KP_Left", defaultModifierMask, NO_MODIFIER_MASK, 
    "reviewPreviousItemHandler"),

    ("KP_Left", defaultModifierMask, ORCA_MODIFIER_MASK,
    "reviewAboveHandler"),

    ("KP_Begin", defaultModifierMask, NO_MODIFIER_MASK,
    "reviewCurrentItemHandler", 1),

    ("KP_Begin", defaultModifierMask, NO_MODIFIER_MASK,
    "reviewSpellCurrentItemHandler", 2),

    ("KP_Begin", defaultModifierMask, NO_MODIFIER_MASK,
    "reviewPhoneticCurrentItemHandler", 3),

    ("KP_Begin", defaultModifierMask, ORCA_MODIFIER_MASK,
    "reviewCurrentAccessibleHandler"),

    ("KP_Right", defaultModifierMask, NO_MODIFIER_MASK,
    "reviewNextItemHandler"),

    ("KP_Right", defaultModifierMask, ORCA_MODIFIER_MASK,
    "reviewBelowHandler"),

    ("KP_End", defaultModifierMask, NO_MODIFIER_MASK,
    "reviewPreviousCharacterHandler"),

    ("KP_End", defaultModifierMask, ORCA_MODIFIER_MASK,
    "reviewEndOfLineHandler"),

    ("KP_Down", defaultModifierMask, NO_MODIFIER_MASK,
    "reviewCurrentCharacterHandler", 1),

    ("KP_Down", defaultModifierMask, NO_MODIFIER_MASK,
    "reviewSpellCurrentCharacterHandler", 2),

    ("KP_Down", defaultModifierMask, NO_MODIFIER_MASK,
    "reviewUnicodeCurrentCharacterHandler", 3),

    ("KP_Page_Down", defaultModifierMask, NO_MODIFIER_MASK,
    "reviewNextCharacterHandler"),

)

