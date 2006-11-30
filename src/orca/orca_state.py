# Orca
#
# Copyright 2006 Sun Microsystems Inc.
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
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

"""Holds state that is shared among many modules.
"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2006 Sun Microsystems Inc."
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

# The "click" count. Used to determine if the user has double or triple
# "clicked" a key.
#
clickCount = 0

# The InputEvent instance representing the last input event.  This is
# set each time a mouse, keyboard or braille event is received.
#
lastInputEvent = None

# The last timestamp from a device event. Used to set focus for the Orca
# configuration GUI.
#
lastInputEventTimestamp = 0

# Records the last time a key was echoed.
#
lastKeyEchoTime = None

# The time that the last "No focus" event occured.
#
noFocusTimestamp = 0.0

# The last word spoken.
#
lastWord = ""

# The last searchQuery
#
searchQuery = None

