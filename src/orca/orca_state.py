# Orca
#
# Copyright 2006-2008 Sun Microsystems Inc.
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

"""Holds state that is shared among many modules.
"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

# NOTE: resist the temptation to do any imports here.  They can
# easily cause circular imports.
#

# History of focused accessibles, helps caching.
#
focusHistory = []

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

# Used to capture keys to redefine key bindings by the user.
#
capturingKeys   = False
lastCapturedKey = None

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

# The last word examined for the misspelled indicator.
#
lastWordCheckedForSpelling = ""

# The last searchQuery
#
searchQuery = None

# Whether we should use the pronunciation dictionary to help speak 
# certain words. This will be True everywhere except when focus is 
# in the Pronunciation Dictionary in the Orca Preferences dialog.
#
usePronunciationDictionary = True

# Handle to the Orca Preferences Glade GUI object.
#
orcaOS = None

# Handle to the Orca application specific preferences Glade GUI object.
#
appOS = None

# Handle to the Glade warning dialog object that is displayed, if the 
# user has attempted to start a second instance of a preferences dialog.
#
orcaWD = None

# Handle to the Orca Preferences Glade file.
#
prefsGladeFile = None

# Handles to the magnification Advanced Settings Glade GUI object and dialog.
#
advancedMag = None
advancedMagDialog = None

# Whether magnification "color enhancements" are currently enabled.
#
colorEnhancementsEnabled = True

# Whether magnification "mouse enhancements" are currently enabled.
#
mouseEnhancementsEnabled = True

# The current zoomer type.
#
zoomerType = None
