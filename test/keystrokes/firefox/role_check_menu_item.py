#!/usr/bin/python

"""Test of menu checkbox output using Firefox.
"""

from macaroon.playback import *

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Open the "View" menu.
#
sequence.append(KeyComboAction("<Alt>v"))
sequence.append(WaitForFocus("Toolbars", acc_role=pyatspi.ROLE_MENU))

########################################################################
# When focus is on Toolbars, Up Arrow to the "Full Screen" check menu
# item. The following should be presented in speech and braille:
#
# BRAILLE LINE:  'Minefield Application Minefield Frame ToolBar Application MenuBar < > Full Screen CheckItem(F11)'
#      VISIBLE:  '< > Full Screen CheckItem(F11)', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Full Screen check item not checked F11'
#
sequence.append(KeyComboAction("Up"))
sequence.append(WaitForFocus("Full Screen", acc_role=pyatspi.ROLE_CHECK_MENU_ITEM))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech and braille:
#
# Note: Due to https://bugzilla.mozilla.org/show_bug.cgi?id=396799,
# We might not speak the item count.
#
# BRAILLE LINE:  'Minefield Application Minefield Frame ToolBar Application MenuBar < > Full Screen CheckItem(F11)'
#      VISIBLE:  '< > Full Screen CheckItem(F11)', cursor=1
# SPEECH OUTPUT: 'View menu'
# SPEECH OUTPUT: 'Full Screen'
# SPEECH OUTPUT: 'check item'
# SPEECH OUTPUT: 'not checked'
# SPEECH OUTPUT: 'F11'
# SPEECH OUTPUT: 'item 10 of 10'
# SPEECH OUTPUT: ''
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Dismiss the menu by pressing Escape and wait for the location bar
# to regain focus.
#
sequence.append(KeyComboAction("Escape"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.start()
