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


keymap = (
    ("9", keybindings.defaultModifierMask, keybindings.ORCA_MODIFIER_MASK,
    "routePointerToItemHandler"),

    # We want the user to be able to combine modifiers with the
    # mouse click (e.g. to Shift+Click and select), therefore we
    # do not "care" about the modifiers (other than the Orca
    # modifier).
    #
    ("7", keybindings.ORCA_MODIFIER_MASK, keybindings.ORCA_MODIFIER_MASK,
    "leftClickReviewItemHandler"),
    ("8", keybindings.ORCA_MODIFIER_MASK, keybindings.ORCA_MODIFIER_MASK,
    "rightClickReviewItemHandler"),

    ("semicolon", keybindings.defaultModifierMask, keybindings.ORCA_MODIFIER_MASK,
    "sayAllHandler", 1),
)
