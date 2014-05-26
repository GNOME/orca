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
    pulled out from default.py: __getLaptopBindings()
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
ORCA_CTRL_MODIFIER_MASK = keybindings.ORCA_CTRL_MODIFIER_MASK

keymap = (
    
    ("9", defaultModifierMask, ORCA_MODIFIER_MASK,
    "routePointerToItemHandler"),

    # We want the user to be able to combine modifiers with the
    # mouse click (e.g. to Shift+Click and select), therefore we
    # do not "care" about the modifiers (other than the Orca
    # modifier).
    #

    ("7", ORCA_MODIFIER_MASK, ORCA_MODIFIER_MASK,
    "leftClickReviewItemHandler"),

    ("8", ORCA_MODIFIER_MASK, ORCA_MODIFIER_MASK,
    "rightClickReviewItemHandler"),

    ("p", defaultModifierMask, ORCA_MODIFIER_MASK,
    "toggleFlatReviewModeHandler"),

    ("semicolon", defaultModifierMask, ORCA_MODIFIER_MASK,
    "sayAllHandler"),

    ("Return", defaultModifierMask, ORCA_MODIFIER_MASK,
    "whereAmIBasicHandler", 1),

    ("Return", defaultModifierMask, ORCA_MODIFIER_MASK,
    "whereAmIDetailedHandler", 2),

    ("slash", defaultModifierMask, ORCA_MODIFIER_MASK,
    "getTitleHandler", 1),
    
    ("slash", defaultModifierMask, ORCA_MODIFIER_MASK,
    "getStatusBarHandler", 2),

    ("bracketleft", defaultModifierMask, ORCA_MODIFIER_MASK,
    "findHandler"),

    ("bracketright", defaultModifierMask, ORCA_MODIFIER_MASK,
    "findNextHandler"),

    ("bracketright", defaultModifierMask, ORCA_CTRL_MODIFIER_MASK,
    "findPreviousHandler"),

    ("u", defaultModifierMask, ORCA_MODIFIER_MASK,
    "reviewPreviousLineHandler"),

    ("u", defaultModifierMask, ORCA_CTRL_MODIFIER_MASK,
    "reviewHomeHandler"),

    ("i", defaultModifierMask, ORCA_MODIFIER_MASK,
    "reviewCurrentLineHandler", 1),

    ("i", defaultModifierMask, ORCA_MODIFIER_MASK,
    "reviewSpellCurrentLineHandler", 2),

    ("i", defaultModifierMask, ORCA_MODIFIER_MASK,
    "reviewPhoneticCurrentLineHandler", 3),

    ("o", defaultModifierMask, ORCA_MODIFIER_MASK,
    "reviewNextLineHandler"),

    ("o", defaultModifierMask, ORCA_CTRL_MODIFIER_MASK,
    "reviewEndHandler"),

    ("j", defaultModifierMask, ORCA_MODIFIER_MASK,
    "reviewPreviousItemHandler"),

    ("j", defaultModifierMask, ORCA_CTRL_MODIFIER_MASK,
    "reviewAboveHandler"), 

    ("k", defaultModifierMask, ORCA_MODIFIER_MASK,
    "reviewCurrentItemHandler", 1),

    ("k", defaultModifierMask, ORCA_MODIFIER_MASK,
    "reviewSpellCurrentItemHandler", 2),

    ("k", defaultModifierMask, ORCA_MODIFIER_MASK,
    "reviewPhoneticCurrentItemHandler", 3),

    ("k", defaultModifierMask, ORCA_CTRL_MODIFIER_MASK,
    "reviewCurrentAccessibleHandler"),

    ("l", defaultModifierMask, ORCA_MODIFIER_MASK,
    "reviewNextItemHandler"),

    ("l", defaultModifierMask, ORCA_CTRL_MODIFIER_MASK,
    "reviewBelowHandler"),

    ("m", defaultModifierMask, ORCA_MODIFIER_MASK,
    "reviewPreviousCharacterHandler"),

    ("m", defaultModifierMask, ORCA_CTRL_MODIFIER_MASK,
    "reviewEndOfLineHandler"),

    ("comma", defaultModifierMask, ORCA_MODIFIER_MASK,
    "reviewCurrentCharacterHandler", 1),

    ("comma", defaultModifierMask, ORCA_MODIFIER_MASK,
    "reviewSpellCurrentCharacterHandler", 2),

    ("comma", defaultModifierMask, ORCA_MODIFIER_MASK,
    "reviewUnicodeCurrentCharacterHandler", 3),

    ("period", defaultModifierMask, ORCA_MODIFIER_MASK,
    "reviewNextCharacterHandler"),

)
