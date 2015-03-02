# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
# Copyright 2010 Joanmarie Diggs, Mesar Hameed
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

"""Holds state that is shared among many modules.
"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc." \
                "Copyright (c) 2010 Joanmarie Diggs, Mesar Hameed."
__license__   = "LGPL"

# NOTE: resist the temptation to do any imports here.  They can
# easily cause circular imports.
#

# The Accessible that has visual focus.
#
locusOfFocus = None

# The currently active window.
#
activeWindow = None

# The currently active script.
#
activeScript = None

# Used to capture keys to redefine key bindings by the user.
#
capturingKeys   = False

# The last non-modifier key event received.
#
lastNonModifierKeyEvent = None

# The InputEvent instance representing the last input event.  This is
# set each time a mouse, keyboard or braille event is received.
#
lastInputEvent = None

# Used to determine if the user wishes Orca to pass the next command
# along to the current application rather than consuming it.
#
bypassNextCommand = False

# The last searchQuery
#
searchQuery = None

# Assists with learn mode (what you enter when you press Insert+F1
# and exit when you press escape.
#
learnModeEnabled = False

# Handle to the Orca Preferences Glade GUI object.
#
orcaOS = None
